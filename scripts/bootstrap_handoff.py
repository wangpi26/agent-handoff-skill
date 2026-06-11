#!/usr/bin/env python3
"""引导创建 Agent handoff 文件。

此脚本刻意保持保守:
- 仅在 handoff 文件缺失时创建。
- 支持两种布局:
  - single: 旧版单文件 AGENT_HANDOFF.md
  - multi: 以 .agent-handoff/README.md 作为索引，并按需使用 .agent-handoff/*.md 状态文件
- 检测 System Harness，并将 handoff 写入外层 Harness 根目录。
- 在 Agent 规则入口中只创建或更新一条带标记的 handoff 引用。
- 不覆盖现有 handoff 状态。
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Iterable


START = "<!-- AGENT_HANDOFF_PROTOCOL:START -->"
END = "<!-- AGENT_HANDOFF_PROTOCOL:END -->"

READONLY_ALLOW = [
    "Read",
    "Grep",
    "Glob",
    "Bash(wc:*)",
    "Bash(sed -n:*)",
    "Bash(rg:*)",
    "Bash(grep:*)",
    "Bash(ls:*)",
    "Bash(pwd)",
    "Bash(git status:*)",
    "Bash(git diff:*)",
    "Bash(git log:*)",
    "Bash(git ls-files:*)",
]

HOOK_SCRIPT_START = "// AGENT_HANDOFF_HOOK:START"
HOOK_SCRIPT_END = "// AGENT_HANDOFF_HOOK:END"
HOOK_COMMAND = 'node "$CLAUDE_PROJECT_DIR/.claude/hooks/handoff-watch.mjs"'


def single_handoff_template(repo: Path) -> str:
    today = date.today().isoformat()
    root = str(repo)
    return f"""# Agent Handoff

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

- 最后更新: {today}
- 上一个 agent: Codex/Claude Code
- 工作区根目录: `{root}`
- 当前目标: 为此仓库建立持久化 Agent handoff 机制。
- 当前状态: initialized
- 立即下一步:
  - 检查仓库特定文件，并用已验证事实替换 `UNKNOWN` 条目。
- 活跃文件:
  - `AGENT_HANDOFF.md`
  - `AGENTS.md`
  - `.claude/CLAUDE.md`
- 阻塞项: 无
- 待确认问题:
  - 确认 handoff 文件应提交还是仅保留在本地。

## 工作区地图

- `.`: 仓库根目录。
- 主要入口:
  - `UNKNOWN`
- 测试入口:
  - `UNKNOWN`
- 文档/规格:
  - `UNKNOWN`

## 持久化项目上下文

- UNKNOWN: 填入从仓库文件或用户输入中验证过的长期项目事实。

## 后续 Agent 操作规则

- 每个会话开始时，如存在预加载项目规则则先依赖它们，然后显式读取此文件。
- 将此文件用作连续性记忆，而不是源代码阅读的替代品。
- 修改实现前，先从源文件验证行为。
- 将编辑范围限制在当前任务和现有项目约定内。
- 除非明确要求，不要修改生成的依赖目录或无关文件。
- 绝不回退无关的用户或 agent 变更。
- 最终回复前，使用状态、已变更文件、验证、风险和下一步更新此文件。

## 决策日志

| 日期 | 决策 | 原因 | 证据 |
| --- | --- | --- | --- |
| {today} | 使用 `AGENT_HANDOFF.md` 作为仓库本地持久化 agent 记忆。 | 保持跨会话和跨 agent 的连续性。 | 用户请求或引导创建动作。 |

## 当前工作日志

### {today}

- 目标: 建立持久化 Agent handoff 机制。
- 已变更文件:
  - `AGENT_HANDOFF.md`: 已创建初始持久化 handoff 状态。
  - `AGENTS.md`: 如已启用，已创建或更新 Codex 项目级 handoff 规则。
  - `.claude/CLAUDE.md`: 如已启用，已创建或更新 Claude Code 项目级 handoff 规则。
- 结果: 已搭建初始 handoff 机制。
- 剩余风险: 在检查源文件前，仓库特定上下文仍包含 `UNKNOWN`。

## 任务积压

- [ ] 用已验证仓库事实替换 `UNKNOWN` 条目。
- [ ] 确认 handoff 文件应提交还是加入 gitignore。

## 验证历史

| 日期 | 命令/检查 | 结果 | 备注 |
| --- | --- | --- | --- |
| {today} | 引导创建文件 | 通过 | 已生成初始 handoff 脚手架；仓库特定事实仍需复核。 |

## Handoff 更新模板

结束任务或会话可能中断时使用:

```markdown
## Handoff 快照

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
  - <none or question>
```

相关时，同时更新 `当前工作日志`、`决策日志`、`验证历史` 和 `任务积压`。
"""


def multi_index_template(repo: Path) -> str:
    today = date.today().isoformat()
    root = str(repo)
    return f"""# Agent Handoff 索引

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

- 最后更新: {today}
- 工作区根目录: `{root}`
- 当前状态文件: `.agent-handoff/snapshot.md`
- 主要下一步来源: `.agent-handoff/snapshot.md`
- 风险来源: `.agent-handoff/risks.md`
- 积压来源: `.agent-handoff/backlog.md`

## 收尾规则

对非平凡工作，在最终回复前更新相关文件:

- 始终更新 `.agent-handoff/snapshot.md`。
- 当文件或任务状态变化时，更新 `.agent-handoff/work-log.md`。
- 当运行检查或有意跳过检查时，更新 `.agent-handoff/validation.md`。
- 当作出持久化决策时，更新 `.agent-handoff/decisions.md`。
- 当后续事项、阻塞项、风险或未知项变化时，更新 `.agent-handoff/backlog.md` 和 `.agent-handoff/risks.md`。
"""


def multi_snapshot_template(repo: Path) -> str:
    today = date.today().isoformat()
    return f"""# Handoff 快照

## 当前状态

- 最后更新: {today}
- 上一个 agent: Codex/Claude Code
- 工作区根目录: `{repo}`
- 当前目标: 为此仓库建立持久化多文档 Agent handoff 机制。
- 当前状态: initialized
- 立即下一步:
  - 检查仓库特定文件，并用已验证事实替换 `UNKNOWN` 条目。
- 活跃文件:
  - `.agent-handoff/README.md`
  - `.agent-handoff/snapshot.md`
- 阻塞项: 无
- 待确认问题:
  - 确认 handoff 文件应提交还是仅保留在本地。

## 恢复摘要

- 使用 `.agent-handoff/README.md` 作为唯一入口。
- 从这里了解当前目标和下一步行动。
- 不要将此文件视为源代码检查的替代品。
"""


def multi_workspace_template() -> str:
    return """# 工作区地图

## 仓库结构

- `.`: 仓库根目录。
- `.agent-handoff/README.md`: handoff 唯一入口和恢复路径。
- `.agent-handoff/`: 持久化 handoff 状态文件。

## 主要入口

- `UNKNOWN`

## 测试入口

- `UNKNOWN`

## 文档与规格

- `UNKNOWN`

## 持久化项目上下文

- UNKNOWN: 填入从仓库文件或用户输入中验证过的长期事实。

## 项目约定

- UNKNOWN
"""


def multi_decisions_template() -> str:
    today = date.today().isoformat()
    return f"""# 决策日志

| 日期 | 决策 | 原因 | 证据 |
| --- | --- | --- | --- |
| {today} | 使用多文档 Agent handoff 记忆。 | 保持当前状态快速可读，同时在专用文件中保留决策、验证、积压和风险。 | 引导创建动作。 |

## 决策指南

- 只记录持久化决策。
- 包含原因和证据。
- 不要将猜测记录为决策。
- 如果缺少证据，标记为 `UNKNOWN`。
"""


def multi_work_log_template() -> str:
    today = date.today().isoformat()
    return f"""# 当前工作日志

## {today}

- 目标: 建立持久化多文档 Agent handoff 机制。
- 已变更文件:
  - `.agent-handoff/README.md`: 已创建 handoff 索引。
  - `.agent-handoff/`: 已创建结构化 handoff 状态文件。
  - Agent 规则入口: 如已启用，仅创建或更新 handoff 引用。
- 结果: 已搭建初始多文档 handoff 机制。
- 剩余风险: 在检查源文件前，仓库特定上下文仍包含 `UNKNOWN`。

## 工作日志指南

- 这里只保留近期且仍有操作价值的工作。
- 将过时或较长历史作为压缩摘要移至 `archive.md`。
- 优先记录文件路径和具体结果，而不是散文式摘要。
"""


def multi_validation_template() -> str:
    today = date.today().isoformat()
    return f"""# 验证历史

| 日期 | 命令/检查 | 结果 | 备注 |
| --- | --- | --- | --- |
| {today} | 引导创建文件 | 通过 | 已生成初始多文档 handoff 脚手架；仓库特定事实仍需复核。 |

## 验证指南

- 记录已运行的命令/检查。
- 记录失败检查的简要原因和下一步行动。
- 对有意未运行的检查记录为 `not run`，并说明原因。
- 不要粘贴长日志；需要时总结并引用文件。
"""


def multi_backlog_template() -> str:
    return """# 任务积压

- [ ] 用已验证仓库事实替换 `UNKNOWN` 条目。
- [ ] 确认 handoff 文件应提交还是加入 gitignore。

## 积压指南

- 保持任务可执行。
- 移除已完成或过时事项。
- 有用时，将事项关联到风险、决策或文件。
"""


def multi_risks_template() -> str:
    return """# 风险、阻塞项与未知项

## 当前阻塞项

- 无

## 当前风险

- 在检查源文件前，仓库特定事实仍为 `UNKNOWN`。

## 未知项 / 需要确认

- UNKNOWN: handoff 文件应提交还是仅保留在本地。

## 风险指南

- 保持风险具体。
- 将不确定内容标记为 `UNKNOWN`。
- 尽可能包含解决每个未知项所需的来源。
"""


def multi_archive_template() -> str:
    return """# Handoff 归档

此文件存放压缩后的旧历史，不应成为常规启动内容。

## 归档指南

- 不要使用此文件记录当前状态。
- 将过时但可能有用的历史作为简洁摘要移至此处。
- 保留指向相关决策、验证条目或源文件的指针。
"""


def common_rule_body(layout: str) -> str:
    if layout == "multi":
        startup = """制定计划或编辑文件前，读取:

1. `.agent-handoff/README.md`
2. `.agent-handoff/snapshot.md`
3. `.agent-handoff/risks.md`
4. `.agent-handoff/backlog.md`
5. 仅在当前任务需要时，根据 `.agent-handoff/README.md` 中的恢复阅读顺序读取其他 `.agent-handoff/` 文件
6. 与用户当前请求直接相关的源文件

将 handoff 文件作为连续性记忆，但在改变行为前从源文件验证实现细节。"""
        memory = """此仓库使用多文档持久化 handoff 记忆:

- `.agent-handoff/README.md`: 唯一入口和恢复路径
- `.agent-handoff/snapshot.md`: 当前目标、状态、下一步、活跃文件、阻塞项和待确认问题
- `.agent-handoff/workspace.md`: 仓库地图、入口点、命令和稳定上下文
- `.agent-handoff/decisions.md`: 包含原因和证据的持久化决策
- `.agent-handoff/work-log.md`: 近期操作工作
- `.agent-handoff/validation.md`: 验证命令/检查及结果
- `.agent-handoff/backlog.md`: 待办工作
- `.agent-handoff/risks.md`: 风险、阻塞项、未知项和确认项
- `.agent-handoff/archive.md`: 压缩旧历史

维护最小的相关文件。不要将所有状态放入 `.agent-handoff/README.md`; 它是入口索引。"""
        size = """- 保持 `.agent-handoff/README.md` 简短；它是入口索引。
- 保持 `.agent-handoff/snapshot.md` 简短、当前且面向行动。
- 在 `.agent-handoff/work-log.md` 中只保留近期且仍相关的工作。
- 优先更新现有条目，而不是追加重复或矛盾记录。
- 将过时长历史移至 `.agent-handoff/archive.md`。
- 在持续未中断的聊天中，仅在压缩、恢复、不确定或任务变化后重读相关 handoff 文件。"""
        closeout = """对非平凡任务，在任何最终回复前更新相关 handoff 文件，不要等待用户要求。

最低必需更新:

- 用当前目标、状态、下一步、活跃文件、阻塞项和待确认问题刷新 `.agent-handoff/snapshot.md`。
- 当文件或任务状态变化时，添加或更新 `.agent-handoff/work-log.md`。
- 为已运行或有意未运行的命令/检查添加 `.agent-handoff/validation.md` 条目。
- 在 `.agent-handoff/decisions.md` 中记录持久化决策。
- 当后续事项、阻塞项、风险或未知项变化时，更新 `.agent-handoff/backlog.md` 和 `.agent-handoff/risks.md`。
- 移除或重写会误导下一个 agent 的过时状态。

如果任务只是对话且项目状态没有变化，则不需要更新文件。"""
        checklist = "最终回复前，用最终任务状态、已变更文件、已运行命令/检查及结果、剩余风险、阻塞项、待确认问题或下一步，更新相关 `.agent-handoff/` 文件。"
    else:
        startup = """制定计划或编辑文件前，读取:

1. `AGENT_HANDOFF.md`
2. `AGENT_HANDOFF.md` 引用的任何任务特定文档
3. 与用户当前请求直接相关的源文件

将 `AGENT_HANDOFF.md` 作为连续性记忆，但在改变行为前从源文件验证实现细节。"""
        memory = """`AGENT_HANDOFF.md` 是此仓库的跨会话持久化记忆。每个有意义的任务期间都要维护它。

当以下任一内容变化时更新它:

- 当前目标或状态
- 活跃文件
- 重要决策
- 已变更文件
- 验证命令和结果
- 阻塞项、风险、待确认问题或后续工作

保持更新简洁且基于证据。不要粘贴密钥、凭据、长日志、大段代码块或聊天记录转储。替换过时信息，不要添加矛盾记录。"""
        size = """- 保持 `Handoff 快照` 简短、当前且面向行动。
- 在 `当前工作日志` 中只保留近期且仍相关的工作。
- 优先更新现有条目，而不是追加重复或矛盾记录。
- 在持续未中断的聊天中，仅在压缩、恢复、不确定或任务变化后重读相关章节。"""
        closeout = """对非平凡任务，在任何最终回复前更新 `AGENT_HANDOFF.md`，不要等待用户要求。

最低必需更新:

- 用当前目标、状态、下一步、活跃文件和阻塞项刷新 `Handoff 快照`。
- 为该任务添加或更新 `当前工作日志`。
- 为已运行的命令或人工检查添加 `验证历史` 条目。
- 记录剩余风险、待确认问题或后续工作。
- 移除或重写会误导下一个 agent 的过时状态。

如果任务只是对话且项目状态没有变化，则不需要更新文件。"""
        checklist = "最终回复前，用最终任务状态、已变更文件、已运行命令/检查及结果、剩余风险、阻塞项、待确认问题或下一步更新 `AGENT_HANDOFF.md`。"

    return f"""## 必需启动流程

{startup}

## 默认实现标准

对非平凡开发工作，默认以生产级/商业级质量为目标，而不是最低可用实现。优先选择稳健、可维护的方案，并进行适当验证，考虑运行时和边界情况，清楚报告已测试和未测试内容。保持范围与用户请求一致；不要添加无关功能或投机性抽象。

## 稳定文件读取协议

为避免 Read 工具行号或 offset 漂移:

1. 普通文件查找、内容搜索和文件读取优先使用专用 search/read 工具。
2. 读取大型或易变文件前确认文件大小，必要时使用行数或定向搜索。
3. 先搜索精确目标，再读取目标周围的小范围精确内容。
4. 除非确认文件很小，否则 Read 范围不超过 240 行。
5. 如果 Read 返回意外空输出、offset 警告、过时片段、行号不一致、`file is shorter than the provided offset`，或 Read 尝试后 API 终止，立即停止对该文件继续分页 Read。
6. 将 Read `offset` 视为行号，而不是字符 offset。绝不重试同一个越界 offset，也不要通过补零或使用大致的大 offset 猜测。如果工具报告文件有 N 行，该文件后续所有 Read offset 必须在 `0..N` 内。
7. 从 Read offset 失败恢复时，使用针对章节/标题/符号的定向 `Grep` 重新锚定，或读取如 offset `0` 这样的已知有效小范围；然后再读取已确认行号周围的小范围。
8. 当 Read 变得不可靠时，使用带引号路径的 shell 验证命令，如 `wc -l`、`rg -n` 和 `sed -n '<start>,<end>p'`; 保持范围较小，并在相关时将该兜底方式记录到验证备注中。
9. 将只读 shell 检查命令（`wc`、`rg`、`grep`、`sed -n`、`ls`、`pwd`，以及不变更状态的 `git status`/`git diff`/`git log`/`git ls-files`）视为安全查询操作。应尽可能在项目 settings 中预批准它们，让源代码验证不需要反复人工批准。
10. 不要基于不确定 offset 提议或编辑代码；先用搜索结果重新锚定。

## 继续恢复保护

如果用户说 `continue`、`继续`、`Continue from where you left off.` 或任何等效的继续请求，将其视为恢复任务的明确指令。不要回答 `No response requested.`，也不要静默停止。先说明最后已知目标和下一项具体行动，然后继续。如果上下文不足，先从 handoff 文件和任务相关源文件恢复，再行动。

## 持久化 Handoff 记忆

{memory}

## Handoff 大小纪律

{size}

## 强制收尾协议

{closeout}

## 工作纪律

- 不要假设哪个子项目处于活跃状态。根据用户请求、handoff 文件和仓库证据推断。
- 优先采用现有项目约定，而不是新抽象。
- 编辑文件前先读取。
- 将编辑范围限制在任务内。
- 除非明确要求，不要修改生成的依赖目录。
- 绝不回退无关的用户或 agent 变更。
- 诚实记录验证。如果测试或检查未运行，在 handoff 文件和最终回复中说明。

## 会话收尾清单

{checklist}"""


def rule_block(platform: str, layout: str) -> str:
    del platform
    entry = ".agent-handoff/README.md" if layout == "multi" else "AGENT_HANDOFF.md"
    return f"""{START}
跨会话恢复与阶段收口时，按需遵循 `{entry}`。不要将 handoff 实现细节复制到本规则入口。
{END}
"""


def session_prompts(layout: str) -> str:
    if layout == "multi":
        return """# Agent 会话提示

## 新窗口启动

```text
确认项目规则已加载，然后读取 AGENT_HANDOFF.md 并遵循其中的恢复阅读顺序。规划前至少读取 .agent-handoff/snapshot.md、.agent-handoff/risks.md 和 .agent-handoff/backlog.md。

恢复当前目标、状态、立即下一步、活跃文件、阻塞项、验证注意事项以及需要检查的源文件。之后只读取与任务相关的文件。任务期间，每当目标、决策、已变更文件、验证、风险、阻塞项或下一步变化时，更新最小相关的 .agent-handoff 文件。最终回复前完成 handoff 收尾。
```

## 继续特定任务

```text
继续此任务: <specific task>。

将其视为继续执行的明确请求。不要回答 "No response requested." 先说明你认为上一步是什么，识别下一项具体行动，然后继续。如果上下文不足，行动前先从 AGENT_HANDOFF.md 和必需的 .agent-handoff 文件恢复。

先读取 AGENT_HANDOFF.md，然后读取 .agent-handoff/snapshot.md、.agent-handoff/risks.md 和 .agent-handoff/backlog.md。检查任务相关源文件。维护多文档 handoff: 开始时更新 snapshot，作出持久化选择时更新 decisions，文件变化时更新 work-log，运行或跳过检查时更新 validation，后续事项或未知项变化时更新 risks/backlog。
```

## 收尾

```text
结束本轮前，更新多文档 handoff: 刷新 .agent-handoff/snapshot.md，更新 .agent-handoff/work-log.md，记录 .agent-handoff/validation.md，更新 .agent-handoff/backlog.md 和 .agent-handoff/risks.md，并移除或重写过时状态。然后报告变更内容、验证内容和剩余事项。
```

## Handoff 质量审查

```text
审查并直接修复多文档 handoff，让新的 agent 可以接手。检查 AGENT_HANDOFF.md 是否仅作为索引，snapshot 是否当前且简短，下一步是否具体，路径是否可定位，决策是否有原因和证据，验证是否已记录，以及过时、矛盾、推测性或聊天记录内容是否已移除。
```
"""
    return """# Agent 会话提示

## 新窗口启动

```text
确认项目规则已加载，然后显式读取 AGENT_HANDOFF.md。将其视为持久化项目状态，而不是聊天历史。

恢复当前目标、状态、立即下一步、活跃文件、阻塞项以及需要检查的源文件。之后只读取任务相关文件。任务期间，每当目标、决策、已变更文件、验证、风险、阻塞项或下一步变化时，更新 AGENT_HANDOFF.md。最终回复前完成 handoff 收尾。
```

## 继续特定任务

```text
继续此任务: <specific task>。

将其视为继续执行的明确请求。不要回答 "No response requested." 先说明你认为上一步是什么，识别下一项具体行动，然后继续。如果上下文不足，行动前先从 AGENT_HANDOFF.md 恢复。

先确认项目规则已加载并读取 AGENT_HANDOFF.md，然后检查任务相关源文件。任务期间维护 AGENT_HANDOFF.md: 开始时更新目标和活跃文件，记录带原因的决策，记录已变更文件，记录验证命令和结果，并在结束前更新最终状态、风险、阻塞项和下一步。
```

## 收尾

```text
结束本轮前，更新 AGENT_HANDOFF.md: 刷新 Handoff 快照，更新当前工作日志，记录验证历史，更新任务积压，并移除或重写过时状态。然后报告变更内容、验证内容和剩余事项。
```

## Handoff 质量审查

```text
审查并直接修复 AGENT_HANDOFF.md，让新的 agent 可以接手。检查目标是否当前，下一步是否具体，路径是否可定位，决策是否有原因和证据，验证是否已记录，以及过时、矛盾、推测性或聊天记录内容是否已移除。
```
"""


def skill_template_text(relative_path: str) -> str:
    path = Path(__file__).resolve().parent.parent / relative_path
    if not path.exists():
        raise SystemExit(f"缺少 skill 模板: {path}")
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def hook_script_template() -> str:
    return skill_template_text("templates/handoff-watch.mjs")


def hook_settings_template() -> dict:
    data = json.loads(skill_template_text("templates/claude-settings-hooks.json"))
    if not isinstance(data, dict) or not isinstance(data.get("hooks"), dict):
        raise SystemExit("无效 hook settings 模板: templates/claude-settings-hooks.json")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_text(path: Path, content: str, dry_run: bool, changed: list[str]) -> None:
    old = read_text(path)
    if old == content:
        return
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    item = str(path)
    if item not in changed:
        changed.append(item)


def create_if_missing(path: Path, content: str, dry_run: bool, changed: list[str], notes: list[str]) -> None:
    if path.exists():
        notes.append(f"已保留现有 {path}; 如有需要请手动检查并修复。")
        return
    write_text(path, content, dry_run, changed)


def replace_marked_block(original: str, block: str) -> str:
    start = original.find(START)
    end = original.find(END)
    if start != -1 and end != -1 and end > start:
        end += len(END)
        prefix = original[:start].rstrip()
        suffix = original[end:].lstrip()
        parts = [part for part in [prefix, block.strip(), suffix] if part]
        return "\n\n".join(parts) + "\n"
    if not original.strip():
        return block.strip() + "\n"
    return original.rstrip() + "\n\n" + block.strip() + "\n"


def replace_marked_script(original: str, block: str) -> str:
    start = original.find(HOOK_SCRIPT_START)
    end = original.find(HOOK_SCRIPT_END)
    if start != -1 and end != -1 and end > start:
        end += len(HOOK_SCRIPT_END)
        prefix = original[:start].rstrip()
        replacement = block.strip()
        suffix = original[end:].lstrip()

        if replacement.startswith("#!") and prefix:
            if prefix.startswith("#!") and len(prefix.splitlines()) == 1:
                prefix = ""
            else:
                replacement = "\n".join(replacement.splitlines()[1:])

        parts = [part for part in [prefix, replacement, suffix] if part]
        return "\n".join(parts) + "\n"
    return original


def add_gitignore_entries(repo: Path, entries: Iterable[str], dry_run: bool, changed: list[str]) -> None:
    path = repo / ".gitignore"
    lines = read_text(path).splitlines()
    existing = {line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#")}
    missing = [entry for entry in entries if entry not in existing]
    if not missing:
        return
    additions = ["", "# Agent handoff 本地记忆", *missing]
    content = "\n".join(lines + additions).lstrip("\n").rstrip() + "\n"
    write_text(path, content, dry_run, changed)


def merge_readonly_permissions(repo: Path, dry_run: bool, changed: list[str]) -> None:
    path = repo / ".claude" / "settings.json"
    if path.exists():
        try:
            data = json.loads(read_text(path))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"无法将 permissions 合并到无效 JSON: {path}: {exc}") from exc
    else:
        data = {}

    permissions = data.setdefault("permissions", {})
    allow = permissions.setdefault("allow", [])
    if not isinstance(allow, list):
        raise SystemExit(f"无法合并 permissions: {path} 中的 permissions.allow 不是列表")

    for item in READONLY_ALLOW:
        if item not in allow:
            allow.append(item)

    content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    write_text(path, content, dry_run, changed)


def load_settings_json(path: Path) -> dict:
    if path.exists():
        try:
            data = json.loads(read_text(path))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"无法更新无效 JSON: {path}: {exc}") from exc
    else:
        data = {}
    if not isinstance(data, dict):
        raise SystemExit(f"无法更新 settings: {path} 中的根 JSON 值不是对象")
    return data


def merge_hook_settings(repo: Path, dry_run: bool, changed: list[str]) -> None:
    path = repo / ".claude" / "settings.json"
    data = load_settings_json(path)
    template = hook_settings_template()

    hooks = data.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise SystemExit(f"无法合并 hooks: {path} 中的 hooks 不是对象")

    for event, groups in template["hooks"].items():
        existing_groups = hooks.setdefault(event, [])
        if not isinstance(existing_groups, list):
            raise SystemExit(f"无法合并 hooks: {path} 中的 hooks.{event} 不是列表")

        found = False
        for group in existing_groups:
            if not isinstance(group, dict):
                continue
            commands = group.get("hooks", [])
            if not isinstance(commands, list):
                continue
            for command in commands:
                if isinstance(command, dict) and command.get("type") == "command" and command.get("command") == HOOK_COMMAND:
                    found = True
                    break
            if found:
                break

        if not found:
            existing_groups.extend(groups)

    content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    write_text(path, content, dry_run, changed)


def install_hooks(repo: Path, dry_run: bool, changed: list[str], notes: list[str]) -> None:
    script_path = repo / ".claude" / "hooks" / "handoff-watch.mjs"
    script = hook_script_template()
    script_ready = True
    if script_path.exists():
        existing = read_text(script_path)
        if existing == script:
            pass
        elif HOOK_SCRIPT_START in existing and HOOK_SCRIPT_END in existing:
            write_text(script_path, replace_marked_script(existing, script), dry_run, changed)
        else:
            notes.append(f"已保留现有 {script_path}; 其中没有 Agent handoff 标记，因此未覆盖 hook 脚本。")
            notes.append("已跳过 hook settings 合并，以避免接入未经验证的现有 hook 脚本。")
            script_ready = False
    else:
        write_text(script_path, script, dry_run, changed)

    if script_ready:
        merge_hook_settings(repo, dry_run, changed)


def create_single_layout(repo: Path, dry_run: bool, changed: list[str], notes: list[str]) -> None:
    create_if_missing(repo / "AGENT_HANDOFF.md", single_handoff_template(repo), dry_run, changed, notes)


def create_multi_layout(repo: Path, dry_run: bool, changed: list[str], notes: list[str]) -> None:
    handoff_dir = repo / ".agent-handoff"
    create_if_missing(handoff_dir / "README.md", multi_index_template(repo), dry_run, changed, notes)
    create_if_missing(handoff_dir / "snapshot.md", multi_snapshot_template(repo), dry_run, changed, notes)
    create_if_missing(handoff_dir / "workspace.md", multi_workspace_template(), dry_run, changed, notes)
    create_if_missing(handoff_dir / "decisions.md", multi_decisions_template(), dry_run, changed, notes)
    create_if_missing(handoff_dir / "work-log.md", multi_work_log_template(), dry_run, changed, notes)
    create_if_missing(handoff_dir / "validation.md", multi_validation_template(), dry_run, changed, notes)
    create_if_missing(handoff_dir / "backlog.md", multi_backlog_template(), dry_run, changed, notes)
    create_if_missing(handoff_dir / "risks.md", multi_risks_template(), dry_run, changed, notes)
    create_if_missing(handoff_dir / "archive.md", multi_archive_template(), dry_run, changed, notes)


def is_harness_root(path: Path) -> bool:
    return (path / "AGENTS.md").is_file() and (path / "harness" / "directory-contract.md").is_file()


def find_harness_root(path: Path) -> Path | None:
    current = path.resolve()
    for candidate in (current, *current.parents):
        if is_harness_root(candidate):
            return candidate
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="为普通仓库或 System Harness 引导创建 Agent handoff 文件。")
    parser.add_argument("--repo", default=".", help="仓库根目录。默认为当前目录。")
    parser.add_argument(
        "--platform",
        choices=["codex", "claude", "both"],
        default="both",
        help="项目规则目标: codex 更新 AGENTS.md, claude 更新 .claude/CLAUDE.md, both 同时更新两者。",
    )
    parser.add_argument(
        "--layout",
        choices=["single", "multi"],
        default="multi",
        help="Handoff 布局: single 创建旧版 AGENT_HANDOFF.md, multi 创建 .agent-handoff/README.md 以及状态文件。",
    )
    parser.add_argument(
        "--scope",
        choices=["auto", "standalone", "harness"],
        default="auto",
        help="目标范围: auto 自动使用已检测到的外层 Harness, standalone 使用 --repo, harness 要求检测到 Harness。",
    )
    parser.add_argument("--session-prompts", action="store_true", help="缺少 AGENT_SESSION_PROMPTS.md 时创建该文件。")
    parser.add_argument("--gitignore", action="store_true", help="缺少条目时，将本地 handoff 文件加入 .gitignore。")
    parser.add_argument("--allow-readonly", action="store_true", help="仅 Claude Code: 将安全的只读查询权限合并到 .claude/settings.json。")
    parser.add_argument("--install-hooks", action="store_true", help="仅 Claude Code: 将提示型 handoff hooks 安装到 .claude/hooks 并合并 .claude/settings.json。")
    parser.add_argument("--skip-codex-rules", action="store_true", help="不要创建或更新 AGENTS.md。")
    parser.add_argument("--skip-claude-rules", action="store_true", help="不要创建或更新 .claude/CLAUDE.md。")
    parser.add_argument("--dry-run", action="store_true", help="打印计划变更，但不写入文件。")
    args = parser.parse_args()

    requested_root = Path(args.repo).expanduser().resolve()
    if not requested_root.exists() or not requested_root.is_dir():
        raise SystemExit(f"目标路径不是目录: {requested_root}")
    harness_root = find_harness_root(requested_root)
    if args.scope == "harness" and harness_root is None:
        raise SystemExit(f"未从目标路径检测到 System Harness: {requested_root}")
    repo = harness_root if args.scope != "standalone" and harness_root else requested_root

    changed: list[str] = []
    notes: list[str] = []

    if args.layout == "multi":
        create_multi_layout(repo, args.dry_run, changed, notes)
    else:
        create_single_layout(repo, args.dry_run, changed, notes)

    write_codex = args.platform in ("codex", "both") and not args.skip_codex_rules
    write_claude = args.platform in ("claude", "both") and not args.skip_claude_rules

    if write_codex:
        codex_path = repo / "AGENTS.md"
        updated = replace_marked_block(read_text(codex_path), rule_block("codex", args.layout))
        write_text(codex_path, updated, args.dry_run, changed)

    if write_claude:
        claude_path = repo / ".claude" / "CLAUDE.md"
        updated = replace_marked_block(read_text(claude_path), rule_block("claude", args.layout))
        write_text(claude_path, updated, args.dry_run, changed)

    if args.session_prompts:
        prompts = repo / "AGENT_SESSION_PROMPTS.md"
        create_if_missing(prompts, session_prompts(args.layout), args.dry_run, changed, notes)

    if args.gitignore:
        entries = ["AGENT_SESSION_PROMPTS.md"]
        if args.layout == "multi":
            entries.append(".agent-handoff/")
        else:
            entries.append("AGENT_HANDOFF.md")
        add_gitignore_entries(repo, entries, args.dry_run, changed)

    if args.allow_readonly:
        merge_readonly_permissions(repo, args.dry_run, changed)

    if args.install_hooks:
        install_hooks(repo, args.dry_run, changed, notes)

    mode = "DRY RUN" if args.dry_run else "UPDATED"
    print(f"{mode}: {repo}")
    print(f"请求路径: {requested_root}")
    print(f"范围: {'harness' if harness_root and repo == harness_root else 'standalone'}")
    print(f"布局: {args.layout}")
    print(f"平台规则: {args.platform}")
    if changed:
        print("已变更文件:")
        for item in changed:
            print(f"- {item}")
    else:
        print("已变更文件: 无")
    if notes:
        print("注意事项:")
        for note in notes:
            print(f"- {note}")
    print("下一步: 检查生成的文件，并用仓库事实替换 UNKNOWN 占位符。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
