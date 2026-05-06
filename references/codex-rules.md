# Codex Handoff Rules

Merge a marked block into project-level `AGENTS.md` for Codex. If the repository already has an `AGENTS.md`, preserve existing guidance and replace only the marked block when present. Do not edit user-level `~/.codex/AGENTS.md` unless the user explicitly asks.

Codex uses `AGENTS.md` as repository instructions. This file is the Codex-side counterpart to Claude Code's `.claude/CLAUDE.md`.

Prefer generating the block with `scripts/bootstrap_handoff.py` so it matches the chosen layout:

```bash
python <skill-dir>/scripts/bootstrap_handoff.py --repo <repo-root> --platform codex --layout multi
python <skill-dir>/scripts/bootstrap_handoff.py --repo <repo-root> --platform codex --layout single
```

If the markers already exist, replace only the marked block.

## Markers

```markdown
<!-- AGENT_HANDOFF_PROTOCOL:START -->
...
<!-- AGENT_HANDOFF_PROTOCOL:END -->
```

## Multi-Document Startup Rule

For `--layout multi`, the generated Codex rule instructs future agents to read:

1. `AGENT_HANDOFF.md`
2. `.agent-handoff/snapshot.md`
3. `.agent-handoff/risks.md`
4. `.agent-handoff/backlog.md`
5. Additional `.agent-handoff/` files only when needed
6. Task-relevant source files

`AGENT_HANDOFF.md` must remain an index. Current task state belongs in `.agent-handoff/snapshot.md`.

## Continuation Recovery Guard

If the user says `continue`, `继续`, `Continue from where you left off.`, or any equivalent continuation request, treat it as an explicit instruction to resume the task. Do not answer `No response requested.` and do not stop silently. First state the last known objective and next concrete action, then continue. If context is insufficient, recover from the handoff files and task-relevant source files before acting.

## Single-Document Startup Rule

For `--layout single`, the generated Codex rule instructs future agents to read:

1. `AGENT_HANDOFF.md`
2. Task-specific docs referenced by `AGENT_HANDOFF.md`
3. Task-relevant source files

All state stays in `AGENT_HANDOFF.md`.

## Closeout Requirement

For non-trivial tasks:

- Multi layout: update the smallest relevant `.agent-handoff/` files before final response.
- Single layout: update `AGENT_HANDOFF.md` before final response.

Do not paste secrets, credentials, long logs, full code blocks, or chat transcript dumps.
