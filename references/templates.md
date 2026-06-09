# Agent Handoff 模板

创建或修复仓库本地 handoff 文件时使用这些模板。用仓库事实替换占位符。无法验证的事实使用 `UNKNOWN`。

对于项目级 agent 规则，Codex `AGENTS.md` 使用 `references/codex-rules.md`，Claude Code `.claude/CLAUDE.md` 使用 `references/claude-rules.md`。

## 布局

- `multi`: 真实项目的推荐默认布局。`AGENT_HANDOFF.md` 是简短索引，`.agent-handoff/*.md` 按类别存储状态。
- `single`: 适用于小项目的旧版紧凑布局。`AGENT_HANDOFF.md` 存储全部状态。

不要强制迁移已有的 `AGENT_HANDOFF.md`。保留它，并在需要时基于仓库事实手动迁移。

## 多文档布局

```text
AGENT_HANDOFF.md
.agent-handoff/
  snapshot.md
  workspace.md
  decisions.md
  work-log.md
  validation.md
  backlog.md
  risks.md
  archive.md
```

### AGENT_HANDOFF.md

```markdown
# Agent Handoff 索引

> 本仓库持久化 agent handoff 记忆的入口。
> 先读取此文件，然后按下方恢复阅读顺序继续。

## 维护契约

- 保持此文件简短。它是索引和恢复路径，不是工作日志。
- 将当前任务状态存放在 `.agent-handoff/snapshot.md`。
- 将持久化事实、决策、验证、积压、风险和归档存放在下列专用文件中。
- 保持所有内容基于事实和仓库证据。将不确定内容标记为 `UNKNOWN`。
- 不要包含密钥、凭据、长日志、完整代码块或聊天记录转储。
- 对任何非平凡任务，在最终回复前更新相关 `.agent-handoff/` 文件。

## Handoff 布局

- `.agent-handoff/snapshot.md`: 当前目标、状态、下一步、活跃文件、阻塞项和待确认问题。
- `.agent-handoff/workspace.md`: 仓库地图、入口点、测试命令、文档和稳定项目上下文。
- `.agent-handoff/decisions.md`: 包含原因和证据的重要决策。
- `.agent-handoff/work-log.md`: 近期操作工作日志。
- `.agent-handoff/validation.md`: 验证命令/检查、结果和注意事项。
- `.agent-handoff/backlog.md`: 待办工作和后续事项。
- `.agent-handoff/risks.md`: 风险、阻塞项、未知项和所需的用户/来源确认。
- `.agent-handoff/archive.md`: 压缩后的旧历史，不属于常规启动内容。

## 恢复阅读顺序

1. 读取此文件。
2. 读取 `.agent-handoff/snapshot.md`。
3. 读取 `.agent-handoff/risks.md`。
4. 读取 `.agent-handoff/backlog.md`。
5. 仅当验证状态对当前任务重要时，读取 `.agent-handoff/validation.md`。
6. 仅在变更架构、行为、依赖或既有决策时，读取 `.agent-handoff/decisions.md`。
7. 仅在需要定位、命令、入口点或子项目边界时，读取 `.agent-handoff/workspace.md`。
8. 仅在需要近期实现细节时，读取 `.agent-handoff/work-log.md`。
9. 仅在明确需要旧上下文时，读取 `.agent-handoff/archive.md`。

## 当前指针

- 最后更新: YYYY-MM-DD
- 工作区根目录: `<repo root>`
- 当前状态文件: `.agent-handoff/snapshot.md`
- 主要下一步来源: `.agent-handoff/snapshot.md`
- 风险来源: `.agent-handoff/risks.md`
- 积压来源: `.agent-handoff/backlog.md`
```

### .agent-handoff/snapshot.md

```markdown
# Handoff 快照

## 当前状态

- 最后更新: YYYY-MM-DD
- 上一个 agent: <agent/model/tool>
- 工作区根目录: `<repo root>`
- 当前目标: <one sentence>
- 当前状态: <not started | in progress | blocked | implemented | validated>
- 立即下一步:
  - <next concrete action>
- 活跃文件:
  - `<path>`
- 阻塞项: <none or concrete blocker>
- 待确认问题:
  - <none, UNKNOWN, or question needing user/source confirmation>

## 恢复摘要

- <one to three bullets with the most important context needed to resume>
```

### .agent-handoff/workspace.md

```markdown
# 工作区地图

## 仓库结构

- `<path>`: <purpose>

## 主要入口点

- `<path>`

## 测试入口点

- `<command or path>`

## 文档与规格

- `<path>`

## 持久化项目上下文

- <Long-lived project fact verified from repository files or user input.>

## 项目约定

- <Important convention>
```

### .agent-handoff/decisions.md

```markdown
# 决策日志

| 日期 | 决策 | 原因 | 证据 |
| --- | --- | --- | --- |
| YYYY-MM-DD | <decision> | <why> | <file/user request/test/source> |
```

### .agent-handoff/work-log.md

```markdown
# 当前工作日志

## YYYY-MM-DD

- 目标: <task>
- 已变更文件:
  - `<path>`: <summary>
- 结果: <what is done>
- 剩余风险: <none or concrete risk>
```

### .agent-handoff/validation.md

```markdown
# 验证历史

| 日期 | 命令/检查 | 结果 | 备注 |
| --- | --- | --- | --- |
| YYYY-MM-DD | `<command or manual check>` | <passed | failed | not run> | <brief note> |
```

### .agent-handoff/backlog.md

```markdown
# 任务积压

- [ ] <task or follow-up>
```

### .agent-handoff/risks.md

```markdown
# 风险、阻塞项和未知项

## 当前阻塞项

- <none or concrete blocker>

## 当前风险

- <none or concrete risk>

## 未知项/待确认项

- UNKNOWN: <specific uncertainty and how to resolve it>
```

### .agent-handoff/archive.md

```markdown
# Handoff 归档

此文件保存压缩后的旧历史，不属于常规启动内容。
```

## 单文档布局

仅用于小项目，或用户明确要求旧版单文件结构时使用。

````markdown
# Agent Handoff

> 此文件是本仓库中 agent 工作的持久化记忆。
> 新的 agent 应能读取此文件，只检查当前任务所需文件，并在不依赖先前聊天历史的情况下继续工作。

## 维护契约

- 规划或编辑前先读取此文件。
- 当任务状态、决策、已触及文件、验证结果、阻塞项、风险或下一步行动变化时，更新此文件。
- 保持内容事实化且紧凑。优先记录文件路径、命令和具体结果。
- 不要包含密钥、凭据、长命令日志、大段代码块或聊天记录转储。
- 替换过时记录，不要累积相互矛盾的历史。
- 将不确定内容标记为 `UNKNOWN`，并在需要时根据仓库证据解决。

## Handoff 快照

- 最后更新: YYYY-MM-DD
- 上一个 agent: <agent/model/tool>
- 工作区根目录: `<repo root>`
- 当前目标: <one sentence describing the current task>
- 当前状态: <not started | in progress | blocked | implemented | validated>
- 立即下一步:
  - <next concrete action>
- 活跃文件:
  - `<path>`
- 阻塞项: <none or concrete blocker>
- 待确认问题:
  - <none, UNKNOWN, or question needing user/source confirmation>

## 工作区地图

- `<path>`: <purpose>
- 主要入口点:
  - `<path>`
- 测试入口点:
  - `<command or path>`
- 文档/规格:
  - `<path>`

## 持久化项目上下文

- <Long-lived project fact that future agents need.>

## 后续 Agent 操作规则

- 每个会话开始时，如存在预加载项目规则则先依赖它们，然后显式读取此文件。
- 将此文件用作连续性记忆，而不是源代码阅读的替代品。
- 修改实现前，先从源文件验证行为。
- 将编辑范围限制在当前任务和现有项目约定内。
- 绝不回退无关的用户或 agent 变更。
- 最终回复前，使用状态、已变更文件、验证、风险和下一步更新此文件。

## 决策日志

| 日期 | 决策 | 原因 | 证据 |
| --- | --- | --- | --- |
| YYYY-MM-DD | <decision> | <why> | <file/user request/test/source> |

## 当前工作日志

### YYYY-MM-DD

- 目标: <task>
- 已变更文件:
  - `<path>`: <summary>
- 结果: <what is done>
- 剩余风险: <none or concrete risk>

## 任务积压

- [ ] <task or follow-up>

## 验证历史

| 日期 | 命令/检查 | 结果 | 备注 |
| --- | --- | --- | --- |
| YYYY-MM-DD | `<command or manual check>` | <passed | failed | not run> | <brief note> |
````

## AGENT_SESSION_PROMPTS.md

使用与所选布局匹配的 prompt。对于多文档布局，将 `AGENT_HANDOFF.md` 以及 `.agent-handoff/snapshot.md`、`.agent-handoff/risks.md`、`.agent-handoff/backlog.md` 说明为必读启动集合。

对于续接 prompt，加入明确的 anti-noop guard，避免 agent 将 `continue` 当作无需回复的请求：

```text
将此视为继续执行的明确请求。不要回答 "No response requested."。先说明你认为上一轮做到哪里，识别下一项具体行动，然后继续。如果上下文不足，请先从 AGENT_HANDOFF.md 和必需的 handoff 文件恢复，再行动。
```
