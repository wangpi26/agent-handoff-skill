# Handoff 质量指南

审查、修复、压缩或验证仓库 handoff 机制时使用此参考。

## 标准维护流程

1. 初始化：检查仓库结构，创建或更新 handoff 文件，将项目级 handoff 引用合并到 Codex `AGENTS.md` 和/或 Claude Code `.claude/CLAUDE.md`，可选创建 `AGENT_SESSION_PROMPTS.md`。
2. 会话启动，单文档布局：明确读取 `AGENT_HANDOFF.md`，判断当前活跃子项目，然后只检查与任务相关的源文件。
3. 会话启动，多文档布局：读取 `.agent-handoff/README.md`、`.agent-handoff/snapshot.md`、`.agent-handoff/risks.md` 和 `.agent-handoff/backlog.md`；仅在需要时读取其他 handoff 文件。
4. 工作期间：当目标/状态改变时更新 snapshot，记录决策及其原因和证据，出现阻塞和风险时记录它们。
5. 收尾：最终回复前更新工作日志、验证历史、后续步骤、风险、阻塞和陈旧状态。
6. 审查/修复：移除矛盾、陈旧备注、聊天记录内容、长日志、密钥和无法验证的声明。

## 优秀的多文档 Handoff

- `.agent-handoff/README.md` 只是入口索引、恢复路径和指针文件。
- `.agent-handoff/snapshot.md` 简短回答当前目标、状态、下一步动作、活跃文件、阻塞项和开放问题。
- `.agent-handoff/risks.md` 包含所有活跃阻塞、风险和未解决的 `UNKNOWN` 项。
- `.agent-handoff/backlog.md` 包含可执行的待办工作，不含已完成的陈旧任务。
- `.agent-handoff/validation.md` 记录已通过、失败和有意未运行的检查。
- `.agent-handoff/decisions.md` 包含带原因和证据的持久决策。
- `.agent-handoff/workspace.md` 包含稳定的仓库地图和命令，而不是易变的任务状态。
- 正常恢复不需要 `.agent-handoff/archive.md`。
- 必读启动集合足以恢复前一个 agent 正在做的工作。

## 优秀的 `AGENT_HANDOFF.md`（单文档布局）

- 新 agent 能在五分钟内理解当前目标和下一步即时动作。
- 所有路径都可从仓库根目录定位。
- 当前状态、阻塞项和 backlog 互不矛盾。
- 重要决策包含原因和证据。
- 验证历史说明运行了什么、是否通过或失败，以及任何注意事项。
- 未知项明确标记为 `UNKNOWN`。
- 文档减少无关阅读，但不替代源代码验证。
- Snapshot 简短且保持最新。
- 近期工作日志仍然相关；旧细节已压缩或归档。

## 多文档恢复测试

如果新 agent 只读取以下内容即可恢复上下文，则 handoff 通过恢复质量测试：

1. `.agent-handoff/README.md`
2. `.agent-handoff/snapshot.md`
3. `.agent-handoff/risks.md`
4. `.agent-handoff/backlog.md`
5. `.agent-handoff/validation.md`
6. 当决策影响任务时读取 `.agent-handoff/decisions.md`

并回答：

- 当前目标是什么？
- 当前状态是什么？
- 下一步具体动作是什么？
- 哪些文件处于活跃状态？
- 哪些决策约束这项工作？
- 哪些验证已通过、失败或未运行？
- 还剩哪些风险、阻塞或未知项？

## 常见问题

- 写成聊天摘要，而不是任务状态。
- 记录类似"优化代码"这类模糊结果，且没有文件路径或验证。
- 开始新任务前没有刷新当前目标。
- 记录决策但没有原因或证据。
- 让文件无限增长，积累陈旧或矛盾备注。
- 粘贴长命令输出、完整代码块或失败日志。
- 把猜测写成事实。
- 忘记记录未运行的测试。

## 修复检查清单

- 先刷新 `Handoff 快照` 或 `.agent-handoff/snapshot.md`。
- 根据仓库证据验证活跃文件。
- 替换陈旧目标和陈旧下一步动作。
- 如果旧日志不再具备操作价值，将其压缩为简洁摘要。
- 保留有用的决策和验证历史。
- 将未解决问题标记为 `UNKNOWN`，不要编造答案。
- 确认没有添加密钥、凭据、token 或私有日志。
- 报告完成前重新读取最终文档。
