# Claude Code Handoff 规则

将带标记的引用合并到 Claude Code 的项目级 `.claude/CLAUDE.md`。如果仓库已有 `.claude/CLAUDE.md`，保留现有指引；存在标记块时只替换该标记块。除非用户明确要求，不要编辑用户级 `~/.claude/CLAUDE.md`。

优先使用 `scripts/bootstrap_handoff.py` 生成该引用，确保它与所选布局匹配：

```bash
python <skill-dir>/scripts/bootstrap_handoff.py --repo <repo-root> --platform claude --layout multi
python <skill-dir>/scripts/bootstrap_handoff.py --repo <repo-root> --platform claude --layout single
```

如果标记已存在，只替换标记块。

## 标记

```markdown
<!-- AGENT_HANDOFF_PROTOCOL:START -->
...
<!-- AGENT_HANDOFF_PROTOCOL:END -->
```

## 多文档启动规则

对于 `--layout multi`，生成的 Claude Code 引用仅指向唯一入口：

```markdown
<!-- AGENT_HANDOFF_PROTOCOL:START -->
跨会话恢复与阶段收口时，按需遵循 `.agent-handoff/README.md`。不要将 handoff 实现细节复制到本规则入口。
<!-- AGENT_HANDOFF_PROTOCOL:END -->
```

详细恢复顺序、文件布局和维护规则由 `.agent-handoff/README.md` 自身承载。

## 续接恢复保护

如果用户说 `continue`、`继续`、`Continue from where you left off.` 或任何等价的续接请求，应将其视为恢复任务的明确指令。不要回答 `No response requested.`，也不要静默停止。先说明最后已知目标和下一个具体动作，然后继续。如果上下文不足，先从 handoff 文件和任务相关源文件恢复上下文，再行动。

## 稳定文件读取协议

生成的 Claude Code 规则包含防御性的 Read 协议：

- 除非已知文件很小，否则 Read 范围不要超过 240 行。
- 将 Read `offset` 视为行号，而不是字符偏移。
- 如果某个文件在 Read 后出现意外空输出、offset 警告、陈旧片段、不一致的行号、`file is shorter than the provided offset`，或 Read 尝试后 API 终止，应停止对该文件继续分页读取。
- offset 失败后，任何后续读取前都要通过定向搜索重新锚定。
- 当 Read 变得不可靠时，使用小范围、带引用、只读的 shell 检查，例如 `wc -l`、`rg -n` 和 `sed -n '<start>,<end>p'`。
- 不要基于不确定的 offset 提议或编辑代码。

## 单文档启动规则

对于 `--layout single`，生成的 Claude Code 引用指向旧版入口：

```markdown
<!-- AGENT_HANDOFF_PROTOCOL:START -->
跨会话恢复与阶段收口时，按需遵循 `AGENT_HANDOFF.md`。不要将 handoff 实现细节复制到本规则入口。
<!-- AGENT_HANDOFF_PROTOCOL:END -->
```

所有状态都保留在 `AGENT_HANDOFF.md` 中。

## 收尾要求

对于非平凡任务：

- Multi layout: 最终回复前更新最小范围的相关 `.agent-handoff/` 文件。
- Single layout: 最终回复前更新 `AGENT_HANDOFF.md`。

不要粘贴密钥、凭据、长日志、完整代码块或聊天记录转储。

## 只读权限说明

如果用户要求允许只读查询操作以避免反复审批，请通过合并安全检查专用的 allow 规则来更新项目 `.claude/settings.json`。不要在此规则下允许会修改状态的命令。
