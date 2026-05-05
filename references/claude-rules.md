# Claude Code Handoff Rules

Merge this marked block into the project-level `.claude/CLAUDE.md` by default. If the repository uses root `CLAUDE.md` or another explicit project memory file, follow the user's requested location. Do not edit user-level `~/.claude/CLAUDE.md` unless the user explicitly asks.

If the markers already exist, replace only the marked block.

````markdown
<!-- AGENT_HANDOFF_PROTOCOL:START -->
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
5. If a read returns unexpected empty output, offset warnings, stale snippets, or inconsistent line numbers, stop paging that file with the unreliable method.
6. When a read method becomes unreliable, use shell verification commands such as `wc -l`, `rg -n`, and `sed -n '<start>,<end>p'` with quoted paths; keep ranges small and record that fallback in validation notes when relevant.
7. Treat built-in local inspection tools and read-only shell inspection commands (`wc`, `rg`, `grep`, `sed -n`, `ls`, `pwd`, and non-mutating `git status`, `git diff`, `git log`, `git ls-files`) as safe query operations. They should be pre-approved in project settings only when the user wants repeated query operations to avoid manual approval.
8. Do not propose or edit code based on uncertain offsets; re-anchor with search results first.

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

Keep `AGENT_HANDOFF.md` optimized for fast new-session recovery:

- Keep `Handoff Snapshot` short, current, and action-oriented.
- Keep only recent, still-relevant work in `Current Work Log`; replace stale entries with compact summaries.
- Move old long history to an archive only when necessary, and leave a short pointer in `AGENT_HANDOFF.md`.
- Prefer updating existing bullets over appending duplicate or contradictory notes.
- A new agent should first read Snapshot, Active files, Backlog, Blockers, and Validation History, then inspect only task-relevant details.
- In an ongoing uninterrupted chat, do not reread the whole handoff file every turn; rely on current chat context and reread only the snapshot or relevant sections after compaction, resume, uncertainty, or task changes.

## Mandatory Closeout Protocol

Before any final response for a non-trivial task, update `AGENT_HANDOFF.md` without waiting for the user to ask.

Minimum required updates:

- Refresh `Handoff Snapshot` with current objective, status, next actions, active files, and blockers.
- Add or update `Current Work Log` for the task.
- Add `Validation History` entries for commands or manual checks that were run.
- Record remaining risks, open questions, or follow-up work.
- Remove or rewrite stale state that would mislead the next agent.

If the task was purely conversational and no project state changed, no file update is required. In that case, say briefly that no handoff update was needed.

## Work Discipline

- Do not assume which subproject is active. Infer it from the user request, `AGENT_HANDOFF.md`, and repository evidence.
- Prefer existing project conventions over new abstractions.
- Read files before editing them.
- Keep edits scoped to the task.
- Do not modify generated dependency folders unless explicitly asked.
- Never revert unrelated user or agent changes.
- Record validation honestly. If tests or checks were not run, say so in `AGENT_HANDOFF.md` and in the final response.
- If the user asks for read-only query operations to avoid repeated approval, update project `.claude/settings.json` by merging allow rules for safe inspection only. Do not allow mutating commands under this rule.

## Session Closeout Checklist

Before final response, update `AGENT_HANDOFF.md` with:

- Final task status
- Files changed
- Commands/checks run and outcomes
- Remaining risks, blockers, open questions, or next steps

Then summarize the result to the user in plain language.
<!-- AGENT_HANDOFF_PROTOCOL:END -->
````
