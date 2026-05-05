#!/usr/bin/env python3
"""Bootstrap repository-local Agent handoff files.

This script is intentionally conservative:
- It creates AGENT_HANDOFF.md only when missing.
- It creates or updates a marked handoff protocol block in .claude/CLAUDE.md.
- It creates optional support files only when requested.
- It does not overwrite existing handoff state.
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


def handoff_template(repo: Path) -> str:
    today = date.today().isoformat()
    root = str(repo)
    return f"""# Agent Handoff

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

- Last updated: {today}
- Last agent: Codex
- Workspace root: `{root}`
- Current objective: Establish durable Agent handoff mechanism for this repository.
- Current status: initialized
- Immediate next actions:
  - Inspect repository-specific files and replace `UNKNOWN` entries with verified facts.
- Active files:
  - `AGENT_HANDOFF.md`
  - `.claude/CLAUDE.md`
- Blockers: none
- Open questions:
  - Confirm whether handoff files should be committed or remain local-only.

## Workspace Map

- `.`: repository root.
- Main entry points:
  - `UNKNOWN`
- Test entry points:
  - `UNKNOWN`
- Docs/specs:
  - `UNKNOWN`

## Durable Project Context

- UNKNOWN: Populate with long-lived project facts verified from repository files or user input.

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
| {today} | Use `AGENT_HANDOFF.md` as repository-local durable agent memory. | Preserve continuity across sessions and agents. | User request or bootstrap action. |

## Current Work Log

### {today}

- Objective: Establish durable Agent handoff mechanism.
- Changed files:
  - `AGENT_HANDOFF.md`: Created initial durable handoff state.
  - `.claude/CLAUDE.md`: Created or updated project-level handoff rules if enabled.
- Result: Initial handoff mechanism scaffolded.
- Remaining risks: Repository-specific context still contains `UNKNOWN` until source files are inspected.

## Task Backlog

- [ ] Replace `UNKNOWN` entries with verified repository facts.
- [ ] Confirm whether handoff files should be committed or gitignored.

## Validation History

| Date | Command/Check | Result | Notes |
| --- | --- | --- | --- |
| {today} | Bootstrap file creation | passed | Generated initial handoff scaffold; repository-specific facts still need review. |

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
"""


CLAUDE_BLOCK = f"""{START}
# Agent Handoff Protocol

## Required Startup Routine

Before making a plan or editing files, read:

1. `AGENT_HANDOFF.md`
2. Any task-specific docs referenced by `AGENT_HANDOFF.md`
3. The source files directly relevant to the user's current request

Use `AGENT_HANDOFF.md` as continuity memory, but verify implementation details from source files before changing behavior.

## Default Implementation Standard

For non-trivial development work, target production/commercial-grade quality by default rather than minimum viable implementation. Prefer robust, maintainable solutions with appropriate validation, runtime and edge-case consideration, and clear reporting of what was and was not tested. Keep scope aligned with the user's request; do not add unrelated features or speculative abstractions.

## Stable File Reading Protocol

To avoid stale snippets, line-number drift, or large unnecessary reads:

1. Prefer dedicated search/read tools for ordinary file lookup, content search, and file reads.
2. Confirm file size before reading large or volatile files, using line counts or targeted searches when needed.
3. Search for exact targets first, then read small exact ranges around those targets.
4. Keep read ranges small unless the file is known to be short.
5. If a read method becomes unreliable, use shell verification commands such as `wc -l`, `rg -n`, and `sed -n '<start>,<end>p'` with quoted paths.
6. Do not propose or edit code based on uncertain offsets; re-anchor with search results first.

## Durable Handoff Memory

`AGENT_HANDOFF.md` is the durable cross-session memory for this repository. Maintain it during every meaningful task.

Update it whenever any of these change:

- Current objective or status
- Active files
- Important decisions
- Files changed
- Validation commands and results
- Blockers, risks, open questions, or follow-up work

Keep updates concise and evidence-based. Do not paste secrets, credentials, long logs, large code blocks, or chat transcript dumps. Replace stale information instead of adding contradictory notes.

## Handoff Size Discipline

- Keep `Handoff Snapshot` short, current, and action-oriented.
- Keep only recent, still-relevant work in `Current Work Log`.
- Prefer updating existing bullets over appending duplicate or contradictory notes.
- In an ongoing uninterrupted chat, reread only relevant sections after compaction, resume, uncertainty, or task changes.

## Mandatory Closeout Protocol

Before any final response for a non-trivial task, update `AGENT_HANDOFF.md` without waiting for the user to ask.

Minimum required updates:

- Refresh `Handoff Snapshot` with current objective, status, next actions, active files, and blockers.
- Add or update `Current Work Log` for the task.
- Add `Validation History` entries for commands or manual checks that were run.
- Record remaining risks, open questions, or follow-up work.
- Remove or rewrite stale state that would mislead the next agent.

If the task was purely conversational and no project state changed, no file update is required.

## Work Discipline

- Do not assume which subproject is active. Infer it from the user request, `AGENT_HANDOFF.md`, and repository evidence.
- Prefer existing project conventions over new abstractions.
- Read files before editing them.
- Keep edits scoped to the task.
- Do not modify generated dependency folders unless explicitly asked.
- Never revert unrelated user or agent changes.
- Record validation honestly. If tests or checks were not run, say so in `AGENT_HANDOFF.md` and in the final response.

## Session Closeout Checklist

Before final response, update `AGENT_HANDOFF.md` with final task status, files changed, commands/checks run and outcomes, and remaining risks, blockers, open questions, or next steps.
{END}
"""


SESSION_PROMPTS = """# Agent Session Prompts

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
"""


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_text(path: Path, content: str, dry_run: bool, changed: list[str]) -> None:
    old = read_text(path)
    if old == content:
        return
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    changed.append(str(path))


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


def add_gitignore_entries(repo: Path, entries: Iterable[str], dry_run: bool, changed: list[str]) -> None:
    path = repo / ".gitignore"
    lines = read_text(path).splitlines()
    existing = {line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#")}
    missing = [entry for entry in entries if entry not in existing]
    if not missing:
        return
    additions = ["", "# Agent handoff local memory", *missing]
    content = "\n".join(lines + additions).lstrip("\n").rstrip() + "\n"
    write_text(path, content, dry_run, changed)


def merge_readonly_permissions(repo: Path, dry_run: bool, changed: list[str]) -> None:
    path = repo / ".claude" / "settings.json"
    if path.exists():
        try:
            data = json.loads(read_text(path))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Cannot merge permissions into invalid JSON: {path}: {exc}") from exc
    else:
        data = {}

    permissions = data.setdefault("permissions", {})
    allow = permissions.setdefault("allow", [])
    if not isinstance(allow, list):
        raise SystemExit(f"Cannot merge permissions: permissions.allow is not a list in {path}")

    for item in READONLY_ALLOW:
        if item not in allow:
            allow.append(item)

    content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    write_text(path, content, dry_run, changed)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap Agent handoff files for a repository.")
    parser.add_argument("--repo", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--session-prompts", action="store_true", help="Create AGENT_SESSION_PROMPTS.md if missing.")
    parser.add_argument("--gitignore", action="store_true", help="Add local handoff files to .gitignore if missing.")
    parser.add_argument("--allow-readonly", action="store_true", help="Merge safe read-only query permissions into .claude/settings.json.")
    parser.add_argument("--skip-claude-rules", action="store_true", help="Do not create or update .claude/CLAUDE.md.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned changes without writing files.")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    if not repo.exists() or not repo.is_dir():
        raise SystemExit(f"Repository path is not a directory: {repo}")

    changed: list[str] = []
    notes: list[str] = []

    handoff = repo / "AGENT_HANDOFF.md"
    if handoff.exists():
        notes.append(f"Preserved existing {handoff}; inspect and repair manually if needed.")
    else:
        write_text(handoff, handoff_template(repo), args.dry_run, changed)

    if not args.skip_claude_rules:
        claude_path = repo / ".claude" / "CLAUDE.md"
        updated = replace_marked_block(read_text(claude_path), CLAUDE_BLOCK)
        write_text(claude_path, updated, args.dry_run, changed)

    if args.session_prompts:
        prompts = repo / "AGENT_SESSION_PROMPTS.md"
        if prompts.exists():
            notes.append(f"Preserved existing {prompts}.")
        else:
            write_text(prompts, SESSION_PROMPTS, args.dry_run, changed)

    if args.gitignore:
        add_gitignore_entries(repo, ["AGENT_HANDOFF.md", "AGENT_SESSION_PROMPTS.md"], args.dry_run, changed)

    if args.allow_readonly:
        merge_readonly_permissions(repo, args.dry_run, changed)

    mode = "DRY RUN" if args.dry_run else "UPDATED"
    print(f"{mode}: {repo}")
    if changed:
        print("Changed files:")
        for item in changed:
            print(f"- {item}")
    else:
        print("Changed files: none")
    if notes:
        print("Notes:")
        for note in notes:
            print(f"- {note}")
    print("Next: inspect generated files and replace UNKNOWN placeholders with repository facts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
