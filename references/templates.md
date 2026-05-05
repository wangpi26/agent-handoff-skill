# Agent Handoff Templates

Use these templates when creating or repairing repository-local handoff files. Replace placeholders with repository facts. Use `UNKNOWN` when a fact cannot be verified.

## AGENT_HANDOFF.md

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
- `<path>`: <purpose>
- Main entry points:
  - `<path>`
- Test entry points:
  - `<command or path>`
- Docs/specs:
  - `<path>`

## Durable Project Context

- <Long-lived project fact that future agents need.>
- <Architecture, product, domain, deployment, or workflow fact.>
- <Important constraints or conventions.>

## Operating Rules For Future Agents

- Start each session by relying on preloaded project rules if present, then reading this file explicitly.
- Use this file as continuity memory, not as a replacement for reading source code.
- Verify behavior from source files before changing implementation.
- Keep edits scoped to the current task and existing project conventions.
- Do not modify generated dependency folders or unrelated files unless explicitly asked.
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

## Handoff Update Template

Use this when ending a task or when the session may be interrupted:

```markdown
## Handoff Snapshot

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
  - <none or question>
```

Also update `Current Work Log`, `Decision Log`, `Validation History`, and `Task Backlog` when relevant.
````

## AGENT_SESSION_PROMPTS.md

````markdown
# Agent Session Prompts

## New Window Startup

```text
Confirm project rules are loaded, then explicitly read AGENT_HANDOFF.md. Treat it as durable project state, not as chat history.

Recover the current objective, status, immediate next action, active files, blockers, and source files that need inspection. Read only task-relevant files after that. During the task, update AGENT_HANDOFF.md whenever objective, decisions, changed files, validation, risks, blockers, or next steps change. Complete handoff closeout before the final response.
```

## Continue Specific Task

```text
Continue this task: <specific task>.

Start by confirming project rules are loaded and reading AGENT_HANDOFF.md, then inspect task-relevant source files. Maintain AGENT_HANDOFF.md during the task: update objective and active files at the start, record decisions with reasons, record changed files, record validation commands and results, and update final status, risks, blockers, and next steps before closing.
```

## Closeout

```text
Before ending this turn, update AGENT_HANDOFF.md: refresh Handoff Snapshot, update Current Work Log, record Validation History, update Task Backlog, and remove or rewrite stale state. Then report what changed, what was validated, and what remains.
```

## Handoff Quality Review

```text
Review and directly repair AGENT_HANDOFF.md so a new agent can take over. Check that the objective is current, next actions are concrete, paths are locatable, decisions have reasons and evidence, validation is recorded, and stale, contradictory, speculative, or chat-transcript content is removed.
```
````
