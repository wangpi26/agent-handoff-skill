---
name: agent-handoff
description: 用于创建、更新、修复或审查持久化仓库接力机制的跨平台 Codex 和 Claude Code skill。支持单文档和多文档布局。检测 System Harness 时自动将 handoff 状态写入外层根目录，且只在 Agent 规则入口维护一条引用。适用于用户要求引导跨会话项目记忆、创建或维护 .agent-handoff 状态文件、在 AGENTS.md 或 .claude/CLAUDE.md 添加 handoff 引用、安装可选 Claude Code 提醒 hook、强制收尾、修复过期接力状态或审查接力质量。Codex 使用时安装到 ~/.codex/skills/agent-handoff；Claude Code 个人使用时安装到 ~/.claude/skills/agent-handoff；Claude Code 项目使用时安装到 repo/.claude/skills/agent-handoff。
---

# Agent Handoff

## 概述

在 Codex 或 Claude Code 中使用这个跨平台 skill，为仓库建立本地连续性记忆，让未来 Agent 不依赖旧聊天历史也能恢复目标、状态、决策、验证、风险和下一步动作。

接力机制默认只作用于仓库本地。除非用户明确要求，不要编辑用户级 `~/.claude/CLAUDE.md` 或其他用户级 Agent 配置。

## System Harness 检测

检测到 System Harness（外层目录同时存在 `AGENTS.md` 和 `harness/directory-contract.md`）时：

- handoff 状态只写入外层 Harness 根目录。
- 不向内层业务仓库复制 agent-handoff Skill。
- 内层 `AGENTS.md` 只承担仓库级导航，不需要理解 handoff 实现。
- 外层 Agent 规则入口只保留一条简洁 handoff 引用，不写入启动顺序、文件布局、维护协议或收口清单正文。
- 未检测到 Harness 时，继续支持普通单仓库 handoff。

## 平台安装

- Codex 个人 skill：将此目录安装到 `~/.codex/skills/agent-handoff`。
- Claude Code 个人 skill：将此目录安装到 `~/.claude/skills/agent-handoff`。
- Claude Code 项目 skill：将此目录安装到 `<repo>/.claude/skills/agent-handoff`。

同一份 `SKILL.md`、`references/` 和 `scripts/` 可跨平台共享。`agents/openai.yaml` 是 Codex UI 元数据，Claude Code 不需要它。

## 布局选择

- `multi` 布局是真实项目的默认选择。它以 `.agent-handoff/README.md` 作为唯一入口，并用 `.agent-handoff/*.md` 按需存储状态文件。
- `single` 布局是小项目使用的旧版紧凑模式。它把所有恢复状态保存在 `AGENT_HANDOFF.md` 中。
- 不要强制迁移已有 `AGENT_HANDOFF.md`。如果该文件已存在，应保留它，并基于仓库事实手动修复或迁移。

## 工作流程

1. 写入文件前先检查仓库。
2. 识别已有 Agent 指导文件：`AGENTS.md`、`CLAUDE.md`、`.claude/CLAUDE.md`、`.claude/rules/`、`.claude/settings.json`、README 文件、文档、源码根目录、测试配置和明显的子项目。
3. 检测 System Harness：如果当前目录或其父级同时存在 `AGENTS.md` 和 `harness/directory-contract.md`，则将 handoff 根目录切换到外层。
4. 如果要初始化新机制，优先运行此 skill 中的 `scripts/bootstrap_handoff.py`，用安全脚手架和幂等引用完成创建。
5. 如果要修复或审查已有机制，先读取 `references/quality.md`，检查当前文件，然后直接用事实更新仓库文件。
6. 始终保持接力内容有证据支撑。对无法从仓库或用户请求中验证的事实使用 `UNKNOWN`。
7. 报告完成前，重新读取已创建或修改的文件。

## 默认文件

- `.agent-handoff/README.md`：多文档布局下的唯一入口和恢复路径；单文档布局不创建此文件。
- `.agent-handoff/snapshot.md`：当前目标、状态、下一步、活跃文件、阻塞项和待确认问题。
- `.agent-handoff/workspace.md`：项目结构、入口、测试命令、文档和长期项目上下文。
- `.agent-handoff/decisions.md`：重要决策、原因和证据。
- `.agent-handoff/work-log.md`：近期仍有操作价值的工作日志。
- `.agent-handoff/validation.md`：验证命令/检查、结果、失败原因和未跑测试说明。
- `.agent-handoff/backlog.md`：待办和后续项。
- `.agent-handoff/risks.md`：风险、阻塞点、`UNKNOWN` 和需要确认的信息。
- `.agent-handoff/archive.md`：压缩后的旧历史，不参与默认恢复。
- `AGENTS.md`：推荐的 Codex 项目 instructions 文件。只合并一条带标记的 handoff 引用；不要覆盖无关项目指导。
- `.claude/CLAUDE.md`：推荐的项目级 Claude Code 规则，只合并一条带标记的 handoff 引用；不要覆盖无关规则。
- `AGENT_SESSION_PROMPTS.md`：可选的可复用提示文件。
- `.gitignore`：当项目不希望提交本地接力文件时，可选择加入忽略规则。
- `.claude/settings.json`：仅 Claude Code 使用。只有用户明确要求时，才可选择合并安全只读权限 allow 规则或提醒型接力 hook。
- `.claude/hooks/handoff-watch.mjs`：仅 Claude Code 使用。可选的事件感知提醒 hook 脚本，只在用户要求 hook 提醒时安装。

## 幂等引用

对 Codex `AGENTS.md` 和 Claude Code `.claude/CLAUDE.md` 的项目级接力引用都使用这些 marker：

```markdown
<!-- AGENT_HANDOFF_PROTOCOL:START -->
...
<!-- AGENT_HANDOFF_PROTOCOL:END -->
```

如果两个 marker 都已存在，只替换它们之间的内容。如果目标文件存在但没有 marker，在既有内容后追加带 marker 的引用。不要重复写入引用块。

不要用模板覆盖已有 `.agent-handoff/README.md`。已有接力状态必须通过读取仓库事实并编辑过期或缺失章节来修复。

## Bootstrap 脚本

使用脚本进行确定性初始化：

```bash
python <skill-dir>/scripts/bootstrap_handoff.py --repo <repo-root> --platform both --layout multi --session-prompts --gitignore
```

常用参数：

- `--repo <path>`：目标仓库根目录。默认当前工作目录。
- `--platform codex|claude|both`：项目规则目标。`codex` 更新 `AGENTS.md`；`claude` 更新 `.claude/CLAUDE.md`；`both` 同时更新两者。
- `--layout single|multi`：接力结构。`multi` 是默认值；`single` 保留旧版单文件布局。
- `--scope auto|standalone|harness`：目标范围。`auto` 自动检测并使用外层 Harness；`standalone` 始终使用 `--repo`；`harness` 要求检测到 Harness 否则报错。
- `--session-prompts`：如果缺失则创建 `AGENT_SESSION_PROMPTS.md`。
- `--gitignore`：如果缺失，则把本地接力文件加入 `.gitignore`。
- `--allow-readonly`：仅 Claude Code 使用。把安全的只读查询权限合并到 `.claude/settings.json`。
- `--install-hooks`：仅 Claude Code 使用。安装事件感知提醒型接力 hook 脚本，并把缺失 hook 条目合并到 `.claude/settings.json`。
- `--skip-codex-rules`：不创建或更新 `AGENTS.md`。
- `--skip-claude-rules`：不创建或更新 `.claude/CLAUDE.md`。
- `--dry-run`：只显示计划变更，不写入文件。

运行脚本后，检查生成的文件，并尽可能用仓库事实替换占位符或 `UNKNOWN` 内容。

## 多文档恢复契约

在 `multi` 布局中，新 Agent 必须按以下顺序恢复：

1. `.agent-handoff/README.md`
2. `.agent-handoff/snapshot.md`
3. `.agent-handoff/risks.md`
4. `.agent-handoff/backlog.md`
5. 验证状态重要时读取 `.agent-handoff/validation.md`
6. 修改持久行为或架构时读取 `.agent-handoff/decisions.md`
7. 需要定位项目或命令时读取 `.agent-handoff/workspace.md`
8. 需要近期实现细节时读取 `.agent-handoff/work-log.md`
9. 仅为旧上下文读取 `.agent-handoff/archive.md`

`snapshot.md` 必须保持简短、面向行动。决策、验证、backlog、风险和历史应放入对应专用文件。

## 引用资料

只加载当前任务需要的引用资料：

- `references/templates.md`：创建或手动修复 `.agent-handoff/README.md` 或 `AGENT_SESSION_PROMPTS.md` 时读取。
- `references/codex-rules.md`：创建或更新 Codex `AGENTS.md` 时读取。
- `references/claude-rules.md`：创建或更新 Claude Code `.claude/CLAUDE.md` 时读取。
- `references/hooks.md`：仅当用户要求基于 hook 的强制或提醒时读取。
- `references/quality.md`：审查、压缩、修复或验证接力机制时读取。
- `templates/claude-settings-hooks.json`：Claude Code hook settings 片段，用于手动审查或安装。
- `templates/handoff-watch.mjs`：Claude Code 事件感知提醒 hook 脚本模板。

## 收尾

当此 skill 修改仓库文件时，报告：

- 创建或更新的文件。
- 当前接力状态。
- 下一位 Agent 应该如何开始。
- 任何剩余 `UNKNOWN` 条目、风险或需要用户确认的事项。
