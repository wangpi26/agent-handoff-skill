# Agent Handoff Templates

Use these templates when creating or repairing repository-local handoff files. Replace placeholders with repository facts. Use `UNKNOWN` when a fact cannot be verified.

For project-level agent rules, use `references/codex-rules.md` for Codex `AGENTS.md` and `references/claude-rules.md` for Claude Code `.claude/CLAUDE.md`.

## Layouts

- `multi`: recommended default for real projects. `AGENT_HANDOFF.md` is a short index and `.agent-handoff/*.md` stores state by category.
- `single`: legacy compact layout for small projects. `AGENT_HANDOFF.md` stores all state.

Do not force-migrate an existing `AGENT_HANDOFF.md`. Preserve it and migrate manually from repository facts when needed.

## Multi-Document Layout

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
# Agent Handoff Index

> Entry point for durable agent handoff memory in this repository.
> Read this file first, then follow the Recovery Reading Order below.

## Maintenance Contract

- Keep this file short. It is an index and recovery route, not a work log.
- Store current task state in `.agent-handoff/snapshot.md`.
- Store durable facts, decisions, validation, backlog, risks, and archives in the dedicated files listed below.
- Keep all content factual and repository-based. Mark uncertainty as `UNKNOWN`.
- Do not include secrets, credentials, long logs, full code blocks, or chat transcript dumps.
- Before final response for any non-trivial task, update the relevant `.agent-handoff/` files.

## Handoff Layout

- `.agent-handoff/snapshot.md`: Current objective, status, next actions, active files, blockers, and open questions.
- `.agent-handoff/workspace.md`: Repository map, entry points, test commands, docs, and stable project context.
- `.agent-handoff/decisions.md`: Important decisions with reasons and evidence.
- `.agent-handoff/work-log.md`: Recent operational work log.
- `.agent-handoff/validation.md`: Validation commands/checks, results, and caveats.
- `.agent-handoff/backlog.md`: Pending work and follow-ups.
- `.agent-handoff/risks.md`: Risks, blockers, unknowns, and user/source confirmations needed.
- `.agent-handoff/archive.md`: Compressed old history that is not part of normal startup.

## Recovery Reading Order

1. Read this file.
2. Read `.agent-handoff/snapshot.md`.
3. Read `.agent-handoff/risks.md`.
4. Read `.agent-handoff/backlog.md`.
5. Read `.agent-handoff/validation.md` only if validation state matters for the current task.
6. Read `.agent-handoff/decisions.md` only when changing architecture, behavior, dependencies, or prior decisions.
7. Read `.agent-handoff/workspace.md` only when orientation, commands, entry points, or subproject boundaries are needed.
8. Read `.agent-handoff/work-log.md` only when recent implementation details are needed.
9. Read `.agent-handoff/archive.md` only when explicitly needed for old context.

## Current Pointer

- Last updated: YYYY-MM-DD
- Workspace root: `<repo root>`
- Current state file: `.agent-handoff/snapshot.md`
- Primary next-action source: `.agent-handoff/snapshot.md`
- Risk source: `.agent-handoff/risks.md`
- Backlog source: `.agent-handoff/backlog.md`
```

### .agent-handoff/snapshot.md

```markdown
# Handoff Snapshot

## Current State

- Last updated: YYYY-MM-DD
- Last agent: <agent/model/tool>
- Workspace root: `<repo root>`
- Current objective: <one sentence>
- Current status: <not started | in progress | blocked | implemented | validated>
- Immediate next actions:
  - <next concrete action>
- Active files:
  - `<path>`
- Blockers: <none or concrete blocker>
- Open questions:
  - <none, UNKNOWN, or question needing user/source confirmation>

## Recovery Summary

- <one to three bullets with the most important context needed to resume>
```

### .agent-handoff/workspace.md

```markdown
# Workspace Map

## Repository Structure

- `<path>`: <purpose>

## Main Entry Points

- `<path>`

## Test Entry Points

- `<command or path>`

## Docs And Specs

- `<path>`

## Durable Project Context

- <Long-lived project fact verified from repository files or user input.>

## Project Conventions

- <Important convention>
```

### .agent-handoff/decisions.md

```markdown
# Decision Log

| Date | Decision | Reason | Evidence |
| --- | --- | --- | --- |
| YYYY-MM-DD | <decision> | <why> | <file/user request/test/source> |
```

### .agent-handoff/work-log.md

```markdown
# Current Work Log

## YYYY-MM-DD

- Objective: <task>
- Changed files:
  - `<path>`: <summary>
- Result: <what is done>
- Remaining risks: <none or concrete risk>
```

### .agent-handoff/validation.md

```markdown
# Validation History

| Date | Command/Check | Result | Notes |
| --- | --- | --- | --- |
| YYYY-MM-DD | `<command or manual check>` | <passed | failed | not run> | <brief note> |
```

### .agent-handoff/backlog.md

```markdown
# Task Backlog

- [ ] <task or follow-up>
```

### .agent-handoff/risks.md

```markdown
# Risks, Blockers, And Unknowns

## Current Blockers

- <none or concrete blocker>

## Current Risks

- <none or concrete risk>

## Unknowns / Confirmations Needed

- UNKNOWN: <specific uncertainty and how to resolve it>
```

### .agent-handoff/archive.md

```markdown
# Handoff Archive

This file stores compressed old history that should not be part of normal startup.
```

## Single-Document Layout

Use only for small projects or when the user explicitly wants the legacy one-file structure.

````markdown
# Agent Handoff

> This file is the durable memory for agents working in this repository.
> A new agent should be able to read this file, inspect only the files needed for the current task, and continue without relying on previous chat history.

## Maintenance Contract

- Read this file before planning or editing.
- Update this file whenever task state, decisions, touched files, validation results, blockers, risks, or next actions change.
- Keep it factual and compact. Prefer file paths, commands, and concrete outcomes.
- Do not include secrets, credentials, long command logs, large code blocks, or chat transcript dumps.
- Replace stale notes instead of accumulating contradictory history.
- Mark uncertainty as `UNKNOWN` and resolve it from repository evidence when needed.

## Handoff Snapshot

- Last updated: YYYY-MM-DD
- Last agent: <agent/model/tool>
- Workspace root: `<repo root>`
- Current objective: <one sentence describing the current task>
- Current status: <not started | in progress | blocked | implemented | validated>
- Immediate next actions:
  - <next concrete action>
- Active files:
  - `<path>`
- Blockers: <none or concrete blocker>
- Open questions:
  - <none, UNKNOWN, or question needing user/source confirmation>

## Workspace Map

- `<path>`: <purpose>
- Main entry points:
  - `<path>`
- Test entry points:
  - `<command or path>`
- Docs/specs:
  - `<path>`

## Durable Project Context

- <Long-lived project fact that future agents need.>

## Operating Rules For Future Agents

- Start each session by relying on preloaded project rules if present, then reading this file explicitly.
- Use this file as continuity memory, not as a replacement for reading source code.
- Verify behavior from source files before changing implementation.
- Keep edits scoped to the current task and existing project conventions.
- Never revert unrelated user or agent changes.
- Before final response, update this file with status, changed files, validation, risks, and next steps.

## Decision Log

| Date | Decision | Reason | Evidence |
| --- | --- | --- | --- |
| YYYY-MM-DD | <decision> | <why> | <file/user request/test/source> |

## Current Work Log

### YYYY-MM-DD

- Objective: <task>
- Changed files:
  - `<path>`: <summary>
- Result: <what is done>
- Remaining risks: <none or concrete risk>

## Task Backlog

- [ ] <task or follow-up>

## Validation History

| Date | Command/Check | Result | Notes |
| --- | --- | --- | --- |
| YYYY-MM-DD | `<command or manual check>` | <passed | failed | not run> | <brief note> |
````

## AGENT_SESSION_PROMPTS.md

Use prompts that match the chosen layout. For multi-document layout, mention `AGENT_HANDOFF.md` plus `.agent-handoff/snapshot.md`, `.agent-handoff/risks.md`, and `.agent-handoff/backlog.md` as the required startup set.
