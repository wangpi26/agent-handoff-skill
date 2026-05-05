---
name: agent-handoff
description: Cross-platform Codex and Claude Code skill for creating, updating, repairing, or reviewing durable repository handoff mechanisms. Use when the user asks to bootstrap cross-session project memory, create or maintain AGENT_HANDOFF.md, add Codex AGENTS.md rules, add Claude Code .claude/CLAUDE.md rules, create reusable session prompts, enforce closeout, repair stale handoff state, or review handoff quality. Install under ~/.codex/skills/agent-handoff for Codex, ~/.claude/skills/agent-handoff for Claude Code personal use, or repo/.claude/skills/agent-handoff for Claude Code project use.
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

## Workflow

1. Inspect the repository before writing files.
2. Identify existing agent guidance files: `AGENTS.md`, `CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/`, `.claude/settings.json`, README files, docs, source roots, test configuration, and obvious subprojects.
3. If bootstrapping a new mechanism, prefer running `scripts/bootstrap_handoff.py` from this skill to create safe scaffolding and idempotent project handoff rule blocks.
4. If repairing or reviewing an existing mechanism, read `references/quality.md`, inspect the current files, then edit the repository files directly with factual updates.
5. Always keep the handoff content evidence-based. Use `UNKNOWN` for facts that cannot be verified from the repository or user request.
6. Re-read files you created or changed before reporting completion.

## Default Files

- `AGENT_HANDOFF.md`: Required durable handoff state at the repository root.
- `AGENTS.md`: Recommended Codex project instructions file. Merge a marked handoff protocol block; do not overwrite unrelated project guidance.
- `.claude/CLAUDE.md`: Recommended project-level Claude Code rules generated for repositories that use Claude Code. Merge a marked handoff protocol block; do not overwrite unrelated rules.
- `AGENT_SESSION_PROMPTS.md`: Optional reusable prompts for new window startup, continuation, closeout, and quality review.
- `.gitignore`: Optionally add local handoff files when the project does not want to commit them.
- `.claude/settings.json`: Claude Code only. Optionally merge safe read-only permission allow rules if the user asks for read/query operations to avoid repeated approval.

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
python <skill-dir>/scripts/bootstrap_handoff.py --repo <repo-root> --platform both --session-prompts --gitignore
```

Useful flags:

- `--repo <path>`: Target repository root. Defaults to the current working directory.
- `--platform codex|claude|both`: Project rule target. `codex` updates `AGENTS.md`; `claude` updates `.claude/CLAUDE.md`; `both` updates both.
- `--session-prompts`: Create `AGENT_SESSION_PROMPTS.md` if missing.
- `--gitignore`: Add local handoff files to `.gitignore` if missing.
- `--allow-readonly`: Claude Code only. Merge safe read-only query permissions into `.claude/settings.json`.
- `--skip-codex-rules`: Do not create or update `AGENTS.md`.
- `--skip-claude-rules`: Do not create or update `.claude/CLAUDE.md`.
- `--dry-run`: Show planned changes without writing files.

After running the script, inspect the generated files and replace placeholder or `UNKNOWN` content with repository-based facts where possible.

## References

Load only the references needed for the task:

- `references/templates.md`: Read when creating or manually repairing `AGENT_HANDOFF.md` or `AGENT_SESSION_PROMPTS.md`.
- `references/codex-rules.md`: Read when creating or updating Codex `AGENTS.md`.
- `references/claude-rules.md`: Read when creating or updating Claude Code `.claude/CLAUDE.md`.
- `references/hooks.md`: Read only when the user asks for hook-based enforcement.
- `references/quality.md`: Read when reviewing, compressing, repairing, or validating a handoff mechanism.

## Closeout

When this skill changes repository files, report:

- Files created or updated.
- Current handoff status.
- How the next agent should start.
- Any remaining `UNKNOWN` entries, risks, or user confirmations needed.
