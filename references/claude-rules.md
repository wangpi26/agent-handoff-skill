# Claude Code Handoff Rules

Merge a marked block into project-level `.claude/CLAUDE.md` for Claude Code. If the repository already has `.claude/CLAUDE.md`, preserve existing guidance and replace only the marked block when present. Do not edit user-level `~/.claude/CLAUDE.md` unless the user explicitly asks.

Prefer generating the block with `scripts/bootstrap_handoff.py` so it matches the chosen layout:

```bash
python <skill-dir>/scripts/bootstrap_handoff.py --repo <repo-root> --platform claude --layout multi
python <skill-dir>/scripts/bootstrap_handoff.py --repo <repo-root> --platform claude --layout single
```

If the markers already exist, replace only the marked block.

## Markers

```markdown
<!-- AGENT_HANDOFF_PROTOCOL:START -->
...
<!-- AGENT_HANDOFF_PROTOCOL:END -->
```

## Multi-Document Startup Rule

For `--layout multi`, the generated Claude Code rule instructs future agents to read:

1. `AGENT_HANDOFF.md`
2. `.agent-handoff/snapshot.md`
3. `.agent-handoff/risks.md`
4. `.agent-handoff/backlog.md`
5. Additional `.agent-handoff/` files only when needed
6. Task-relevant source files

`AGENT_HANDOFF.md` must remain an index. Current task state belongs in `.agent-handoff/snapshot.md`.

## Single-Document Startup Rule

For `--layout single`, the generated Claude Code rule instructs future agents to read:

1. `AGENT_HANDOFF.md`
2. Task-specific docs referenced by `AGENT_HANDOFF.md`
3. Task-relevant source files

All state stays in `AGENT_HANDOFF.md`.

## Closeout Requirement

For non-trivial tasks:

- Multi layout: update the smallest relevant `.agent-handoff/` files before final response.
- Single layout: update `AGENT_HANDOFF.md` before final response.

Do not paste secrets, credentials, long logs, full code blocks, or chat transcript dumps.

## Read-Only Permission Note

If the user asks for read-only query operations to avoid repeated approval, update project `.claude/settings.json` by merging allow rules for safe inspection only. Do not allow mutating commands under this rule.
