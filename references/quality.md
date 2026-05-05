# Handoff Quality Guide

Use this reference when reviewing, repairing, compressing, or validating a repository handoff mechanism.

## Standard Maintenance Flow

1. Initialization: inspect repository structure, create or update `AGENT_HANDOFF.md`, merge project-level handoff rules into Codex `AGENTS.md` and/or Claude Code `.claude/CLAUDE.md`, optionally create `AGENT_SESSION_PROMPTS.md`.
2. Session start: explicitly read `AGENT_HANDOFF.md`, determine the active subproject, then inspect only task-relevant source files.
3. During work: update snapshot when objective/status changes, record decisions with reasons and evidence, record blockers and risks when they appear.
4. Closeout: update work log, validation history, next steps, risks, blockers, and stale state before final response.
5. Review/repair: remove contradictions, stale notes, chat transcript content, long logs, secrets, and unverifiable claims.

## Good `AGENT_HANDOFF.md`

- A new agent can understand the current objective and immediate next action within five minutes.
- All paths are locatable from the repository root.
- Current status, blockers, and backlog do not contradict each other.
- Important decisions include reasons and evidence.
- Validation history states what was run, whether it passed or failed, and any caveats.
- Unknowns are explicitly marked as `UNKNOWN`.
- The document reduces irrelevant reading, but does not replace source-code verification.
- The snapshot is short and current.
- Recent work log entries are still relevant; old details are compressed or archived.

## Common Problems

- Writing a chat summary instead of task state.
- Recording vague outcomes like "optimized code" without file paths or validation.
- Starting a new task without refreshing the current objective.
- Capturing decisions without reason or evidence.
- Letting the file grow indefinitely with stale or contradictory notes.
- Pasting long command output, full code blocks, or failure logs.
- Writing guesses as facts.
- Forgetting to record tests that were not run.

## Repair Checklist

- Refresh `Handoff Snapshot` first.
- Verify active files from repository evidence.
- Replace stale objectives and stale next actions.
- Collapse old logs into concise summaries if they are no longer operationally useful.
- Preserve useful decisions and validation history.
- Mark unresolved questions as `UNKNOWN` instead of inventing answers.
- Confirm no secrets, credentials, tokens, or private logs were added.
- Re-read the final document before reporting completion.
