# Optional Hook Enforcement

Use hooks only when the user asks for stronger enforcement than written project rules. Hooks should check and remind; they should not auto-generate complex handoff content because that risks writing false state. The provided templates support both single-document and multi-document handoff layouts.

This hook guidance is optional and Claude Code specific. Codex does not use this hook snippet, and the default bootstrap command does not install hooks unless `--install-hooks` is passed.

## Principles

- Keep hooks lightweight, local, and project-scoped.
- Prefer soft reminders over blocking the workflow.
- Always emit valid JSON from hook scripts.
- Always exit with status code `0`, including error paths.
- Never return `decision: "block"` or `continue: false`.
- Do not return `decision: "approve"`; for non-blocking events, omit `decision` and use `systemMessage` only when a reminder is needed.
- Never use hook failures to terminate, block, or close an agent session.
- Do not use hooks to write speculative task status.
- Put scripts under `.claude/hooks/` and reference them from `.claude/settings.json`.
- Preserve existing user hook scripts unless they contain the Agent handoff hook markers.

## Recommended Install

Use the bootstrap script when the user explicitly asks for hooks:

```bash
python <skill-dir>/scripts/bootstrap_handoff.py --repo <repo-root> --install-hooks
```

This command:

- Creates `.claude/hooks/handoff-watch.mjs` if missing.
- Replaces only the marked Agent handoff block in `.claude/hooks/handoff-watch.mjs` if the markers already exist.
- Preserves an existing `.claude/hooks/handoff-watch.mjs` with no Agent handoff markers.
- Merges missing hook entries into `.claude/settings.json`.
- Avoids duplicating hook commands on repeated runs.

Use `--dry-run` first when changing an existing project:

```bash
python <skill-dir>/scripts/bootstrap_handoff.py --repo <repo-root> --install-hooks --dry-run
```

## Template Files

- `templates/claude-settings-hooks.json`: Minimal `.claude/settings.json` hook snippet.
- `templates/handoff-watch.mjs`: Advisory hook script that checks handoff file freshness and expected structure.

When manually installing hooks, merge the `hooks` object from `templates/claude-settings-hooks.json` into the project's `.claude/settings.json` instead of overwriting unrelated settings.

## Expected Target Files

```text
.claude/
  settings.json
  hooks/
    handoff-watch.mjs
```

## Safety Contract

The hook is an advisory reminder, not an enforcement gate. It must allow the session to continue even when:

- `AGENT_HANDOFF.md` is missing.
- `.agent-handoff/` files are incomplete.
- The script encounters an unexpected runtime error.

For a clean handoff state, the hook exits `0` with no stdout. For reminders, it exits `0` with JSON like:

```json
{
  "continue": true,
  "systemMessage": "Update the handoff before final response if repository state changed."
}
```

If stricter enforcement is desired, do not change this template to block by default. First confirm the desired behavior with the user and document the operational risk, because a blocking hook can interrupt normal agent closeout or session startup.
