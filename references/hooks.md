# 可选 Claude Code Hook 强制提醒

仅当用户要求比书面项目规则更强的操作提醒时使用 hooks。Hooks 必须检查并提醒；不得生成 handoff 内容，因为收尾状态需要仓库上下文和 agent 判断。

此 hook 指南仅适用于 Claude Code。Codex 不使用 Claude hooks，默认 bootstrap 命令也不会安装 hooks，除非传入 `--install-hooks`。

## 安全契约

- 保持 hooks 轻量、本地、限定在项目范围内。
- 需要输出时始终输出有效 JSON。
- 始终以状态码 `0` 退出，包括错误路径。
- 返回 JSON 时始终返回 `continue: true`。
- 永远不要返回 `decision: "block"`、`continue: false` 或 `decision: "approve"`。
- 永远不要用 hook 失败来终止、阻塞或关闭 agent 会话。
- 永远不要从 hook 写入 handoff 文件。
- 永远不要调用网络、安装依赖、删除文件、启动服务或修改项目状态。
- 保留已有用户 hook 脚本，除非其中包含 Agent handoff hook 标记。

`statusMessage` 属于 `.claude/settings.json`，只是在 hook 命令运行时显示的 Claude Code UI 标签。hook 脚本不得依赖它。事件行为必须来自 Claude Code hook stdin JSON，尤其是 `hook_event_name`。

## 推荐安装

仅当用户明确要求 hooks 时使用 bootstrap 脚本：

```bash
python <skill-dir>/scripts/bootstrap_handoff.py --repo <repo-root> --install-hooks
```

此命令会：

- 如果缺失，创建 `.claude/hooks/handoff-watch.mjs`。
- 如果目标脚本已有 hook 标记，只替换带标记的 Agent handoff hook 块。
- 保留没有 Agent handoff 标记的现有 `.claude/hooks/handoff-watch.mjs`。
- 将缺失的 hook 条目合并到 `.claude/settings.json`。
- 避免重复运行时生成重复的 hook 命令。

修改已有项目时，先使用 `--dry-run`：

```bash
python <skill-dir>/scripts/bootstrap_handoff.py --repo <repo-root> --install-hooks --dry-run
```

## 模板文件

- `templates/claude-settings-hooks.json`: 可用于手动合并或脚本安装的事件感知 `.claude/settings.json` hook 片段。
- `templates/handoff-watch.mjs`: 完整的建议型 hook 脚本，用于检查 handoff 文件的新鲜度和结构。

手动安装 hooks 时，只将 `templates/claude-settings-hooks.json` 中的 `hooks` 对象合并到项目的 `.claude/settings.json`。不要覆盖无关设置。

## 安装目标文件

```text
.claude/
  settings.json
  hooks/
    handoff-watch.mjs
```

## 支持的事件

| Event | Behavior |
| --- | --- |
| `SessionStart` | 注入 handoff 健康状态和恢复读取指引作为附加上下文。 |
| `UserPromptSubmit` | 仅当 prompt 暗示 handoff、continue、resume、compact、closeout 或 recovery 工作，或 handoff 结构缺失时注入上下文。 |
| `PreCompact` | 如果任务状态已改变，提醒 agent 在压缩上下文前更新 handoff 文件。 |
| `Stop` | 如果仓库状态已改变，提醒 agent 在最终回复前更新相关 handoff 文件。 |
| `SubagentStop` | 与 `Stop` 相同的收尾提醒行为，并带有 stop-loop 抑制。 |
| `SessionEnd` | 输出安静的会话结束摘要。 |

##

通用检查：

- `.agent-handoff/README.md` 存在（多文档布局）或 `AGENT_HANDOFF.md` 存在（单文档布局）。
- 入口文件未超过配置的陈旧阈值。
- Claude Code hook stdin JSON 可被解析。

多文档布局检查：

- `.agent-handoff/` 存在。
- `.agent-handoff/README.md` 包含 `## 恢复阅读顺序`。
- `.agent-handoff/README.md` 包含 `## Handoff 布局`。
- 当 snapshot 文件存在时，`.agent-handoff/snapshot.md` 包含 `## 当前状态`。

单文档布局检查：

- `AGENT_HANDOFF.md` 包含 `## Handoff 快照`。
- `AGENT_HANDOFF.md` 包含 `## 当前工作日志`。
- `AGENT_HANDOFF.md` 包含 `## 验证历史`。
- `AGENT_HANDOFF.md` 包含 `## 任务积压`。

## 输出策略

此 hook 仅提供建议。它显式返回 `continue: true`，且永远不会发出阻塞决策。

它可以使用：

- `hookSpecificOutput.additionalContext` 用于启动和 prompt 上下文注入。
- `systemMessage` 用于收尾、压缩、手动操作或错误提醒。
- `suppressOutput: true` 用于安静的 no-op 路径，例如无关的 `UserPromptSubmit`、活动的 stop-loop 抑制和 `SessionEnd`。

Hook 应暴露有用提醒，但不应从 agent 手中夺走控制权。

## 重试策略

仅重试当前 hook 进程内可能是瞬态的窄范围失败：

- stdin 读取问题
- 不完整 hook 输入导致的 JSON 解析问题

仓库状态问题不重试，因为重试不会改变它们：

- 缺少 handoff 文件
- 缺少必需章节
- 陈旧时间戳
- 混合或不完整布局

直接向 agent 报告仓库状态问题。

## 参数和环境

| Name | Purpose |
| --- | --- |
| `--project-dir <path>` | 设置用于手动测试的项目根目录。 |
| `--event <name>` | 未提供 stdin 时设置 hook 事件。 |
| `--max-age-minutes <n>` | 设置 handoff 陈旧阈值。默认值为 `120`。 |
| `CLAUDE_PROJECT_DIR` | Claude Code 提供的项目根目录。优先于 stdin `cwd`。 |
| `HANDOFF_MAX_AGE_MINUTES=<n>` | 等同于 `--max-age-minutes <n>`。 |

手动测试：

```bash
node .claude/hooks/handoff-watch.mjs --project-dir <repo-root> --event Stop
```

如果需要更严格的强制执行，不要修改此模板让其默认阻塞。请先向用户确认期望行为并记录操作风险，因为阻塞型 hook 可能中断正常收尾或启动。
