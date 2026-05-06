---
name: agent-handoff
description: Cross-platform Codex and Claude Code skill for creating, updating, repairing, or reviewing durable repository handoff mechanisms. Supports single-document and multi-document layouts. Use when the user asks to bootstrap cross-session project memory, create or maintain AGENT_HANDOFF.md and .agent-handoff state files, add Codex AGENTS.md rules, add Claude Code .claude/CLAUDE.md rules, create reusable session prompts, install optional Claude Code advisory hooks, enforce closeout, repair stale handoff state, or review handoff quality. Install under ~/.codex/skills/agent-handoff for Codex, ~/.claude/skills/agent-handoff for Claude Code personal use, or repo/.claude/skills/agent-handoff for Claude Code project use.
---

# Agent Handoff

## Overview

Use this cross-platform skill in Codex or Claude Code to establish repository-local continuity memory so a future agent can recover objective, status, decisions, validation, risks, and next actions without relying on previous chat history.

The handoff mechanism is repository-local by default. Do not edit user-level `~/.claude/CLAUDE.md` or other user-level agent configuration unless the user explicitly asks for it.

## Platform Installation

- Codex personal skill: install this folder at `~/.codex/skills/agent-handoff`.
- Claude Code personal skill: install this folder at `~/.claude/skills/agent-handoff`.
- Claude Code project skill: install this folder at `<repo>/.claude/skills/agent-handoff`.

The same `SKILL.md`, `references/`, and `scripts/` are shared across platforms. `agents/openai.yaml` is Codex UI metadata and is not required by Claude Code.

## Layout Choice

- `multi` layout is the default for real projects. It creates `AGENT_HANDOFF.md` as a short index and `.agent-handoff/*.md` for state files.
- `single` layout is the legacy compact mode for small projects. It keeps all recovery state in `AGENT_HANDOFF.md`.
- Do not force-migrate an existing `AGENT_HANDOFF.md`. If it exists, preserve it and repair or migrate manually from repository facts.

## Workflow

1. Inspect the repository before writing files.
2. Identify existing agent guidance files: `AGENTS.md`, `CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/`, `.claude/settings.json`, README files, docs, source roots, test configuration, and obvious subprojects.
3. If bootstrapping a new mechanism, prefer running `scripts/bootstrap_handoff.py` from this skill to create safe scaffolding and idempotent project handoff rule blocks.
4. If repairing or reviewing an existing mechanism, read `references/quality.md`, inspect the current files, then edit the repository files directly with factual updates.
5. Always keep the handoff content evidence-based. Use `UNKNOWN` for facts that cannot be verified from the repository or user request.
6. Re-read files you created or changed before reporting completion.

## Default Files

- `AGENT_HANDOFF.md`: Required durable handoff state at the repository root.
- `.agent-handoff/`: Multi-document layout directory for snapshot, workspace, decisions, work log, validation, backlog, risks, and archive.
- `AGENTS.md`: Recommended Codex project instructions file. Merge a marked handoff protocol block; do not overwrite unrelated project guidance.
- `.claude/CLAUDE.md`: Recommended project-level Claude Code rules generated for repositories that use Claude Code. Merge a marked handoff protocol block; do not overwrite unrelated rules.
- `AGENT_SESSION_PROMPTS.md`: Optional reusable prompts for new window startup, continuation, closeout, and quality review.
- `.gitignore`: Optionally add local handoff files when the project does not want to commit them.
- `.claude/settings.json`: Claude Code only. Optionally merge safe read-only permission allow rules or advisory handoff hooks if the user explicitly asks.
- `.claude/hooks/handoff-watch.mjs`: Claude Code only. Optional advisory hook script installed only when the user asks for hook reminders.

## Idempotency Rules

Use these markers for both Codex `AGENTS.md` and Claude Code `.claude/CLAUDE.md` project-level handoff rules:

```markdown
<!-- AGENT_HANDOFF_PROTOCOL:START -->
...
<!-- AGENT_HANDOFF_PROTOCOL:END -->
```

If both markers already exist, replace only the content between them. If the target file exists without markers, append the marked block after the existing content. Never duplicate the protocol block.

Do not overwrite an existing `AGENT_HANDOFF.md` with a template. Existing handoff state must be repaired by reading repository facts and editing stale or missing sections.

## Bootstrap Script

Use the script for deterministic setup:

```bash
python <skill-dir>/scripts/bootstrap_handoff.py --repo <repo-root> --platform both --layout multi --session-prompts --gitignore
```

Useful flags:

- `--repo <path>`: Target repository root. Defaults to the current working directory.
- `--platform codex|claude|both`: Project rule target. `codex` updates `AGENTS.md`; `claude` updates `.claude/CLAUDE.md`; `both` updates both.
- `--layout single|multi`: Handoff structure. `multi` is default; `single` preserves the legacy single-file layout.
- `--session-prompts`: Create `AGENT_SESSION_PROMPTS.md` if missing.
- `--gitignore`: Add local handoff files to `.gitignore` if missing.
- `--allow-readonly`: Claude Code only. Merge safe read-only query permissions into `.claude/settings.json`.
- `--install-hooks`: Claude Code only. Install advisory handoff hook script and merge missing hook entries into `.claude/settings.json`. Hooks always approve and exit `0`.
- `--skip-codex-rules`: Do not create or update `AGENTS.md`.
- `--skip-claude-rules`: Do not create or update `.claude/CLAUDE.md`.
- `--dry-run`: Show planned changes without writing files.

After running the script, inspect the generated files and replace placeholder or `UNKNOWN` content with repository-based facts where possible.

## Multi-Document Recovery Contract

In `multi` layout, a new agent must recover in this order:

1. `AGENT_HANDOFF.md`
2. `.agent-handoff/snapshot.md`
3. `.agent-handoff/risks.md`
4. `.agent-handoff/backlog.md`
5. `.agent-handoff/validation.md` when validation state matters
6. `.agent-handoff/decisions.md` when changing durable behavior or architecture
7. `.agent-handoff/workspace.md` when orientation or commands are needed
8. `.agent-handoff/work-log.md` when recent implementation details are needed
9. `.agent-handoff/archive.md` only for old context

`snapshot.md` must stay short and action-oriented. Use the dedicated files for decisions, validation, backlog, risks, and history.

## References

Load only the references needed for the task:

- `references/templates.md`: Read when creating or manually repairing `AGENT_HANDOFF.md` or `AGENT_SESSION_PROMPTS.md`.
- `references/codex-rules.md`: Read when creating or updating Codex `AGENTS.md`.
- `references/claude-rules.md`: Read when creating or updating Claude Code `.claude/CLAUDE.md`.
- `references/hooks.md`: Read only when the user asks for hook-based enforcement.
- `references/quality.md`: Read when reviewing, compressing, repairing, or validating a handoff mechanism.
- `templates/claude-settings-hooks.json`: Claude Code hook settings snippet for manual review or installation.
- `templates/handoff-watch.mjs`: Claude Code advisory hook script template.

## Closeout

When this skill changes repository files, report:

- Files created or updated.
- Current handoff status.
- How the next agent should start.
- Any remaining `UNKNOWN` entries, risks, or user confirmations needed.
