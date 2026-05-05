---
name: agent-handoff
description: Create, update, repair, or review a durable Agent handoff mechanism for a repository. Use when the user asks to bootstrap cross-session project memory, create or maintain AGENT_HANDOFF.md, add Claude Code handoff rules, create reusable session prompts, enforce handoff closeout, repair stale handoff state, or review handoff quality.
---

# Agent Handoff

## Overview

Use this skill to establish repository-local continuity memory so a future agent can recover objective, status, decisions, validation, risks, and next actions without relying on previous chat history.

The handoff mechanism is repository-local by default. Do not edit user-level `~/.claude/CLAUDE.md` unless the user explicitly asks for it.

## Workflow

1. Inspect the repository before writing files.
2. Identify existing agent guidance files: `AGENTS.md`, `CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/`, `.claude/settings.json`, README files, docs, source roots, test configuration, and obvious subprojects.
3. If bootstrapping a new mechanism, prefer running `scripts/bootstrap_handoff.py` from this skill to create safe scaffolding and idempotent Claude rule blocks.
4. If repairing or reviewing an existing mechanism, read `references/quality.md`, inspect the current files, then edit the repository files directly with factual updates.
5. Always keep the handoff content evidence-based. Use `UNKNOWN` for facts that cannot be verified from the repository or user request.
6. Re-read files you created or changed before reporting completion.

## Default Files

- `AGENT_HANDOFF.md`: Required durable handoff state at the repository root.
- `.claude/CLAUDE.md`: Recommended project-level Claude Code rules. Merge a marked handoff protocol block; do not overwrite unrelated rules.
- `AGENT_SESSION_PROMPTS.md`: Optional reusable prompts for new window startup, continuation, closeout, and quality review.
- `.gitignore`: Optionally add local handoff files when the project does not want to commit them.
- `.claude/settings.json`: Optionally merge safe read-only permission allow rules if the user asks for read/query operations to avoid repeated approval.

## Idempotency Rules

Use these markers for the project-level Claude handoff protocol:

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
python <skill-dir>/scripts/bootstrap_handoff.py --repo <repo-root> --session-prompts --gitignore
```

Useful flags:

- `--repo <path>`: Target repository root. Defaults to the current working directory.
- `--session-prompts`: Create `AGENT_SESSION_PROMPTS.md` if missing.
- `--gitignore`: Add local handoff files to `.gitignore` if missing.
- `--allow-readonly`: Merge safe read-only query permissions into `.claude/settings.json`.
- `--dry-run`: Show planned changes without writing files.

After running the script, inspect the generated files and replace placeholder or `UNKNOWN` content with repository-based facts where possible.

## References

Load only the references needed for the task:

- `references/templates.md`: Read when creating or manually repairing `AGENT_HANDOFF.md` or `AGENT_SESSION_PROMPTS.md`.
- `references/claude-rules.md`: Read when creating or updating `.claude/CLAUDE.md`.
- `references/hooks.md`: Read only when the user asks for hook-based enforcement.
- `references/quality.md`: Read when reviewing, compressing, repairing, or validating a handoff mechanism.

## Closeout

When this skill changes repository files, report:

- Files created or updated.
- Current handoff status.
- How the next agent should start.
- Any remaining `UNKNOWN` entries, risks, or user confirmations needed.
