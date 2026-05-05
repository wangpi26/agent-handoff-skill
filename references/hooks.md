# Optional Hook Enforcement

Use hooks only when the user asks for stronger enforcement than written project rules. Hooks should check and remind; they should not auto-generate complex handoff content because that risks writing false state. The example supports both single-document and multi-document handoff layouts.

## Principles

- Keep hooks lightweight, local, and project-scoped.
- Prefer soft reminders over blocking the workflow.
- Always emit valid JSON from hook scripts.
- Do not use hooks to write speculative task status.
- Put scripts under `.claude/hooks/` and reference them from `.claude/settings.json`.

## Minimal `.claude/settings.json` Hook Snippet

Merge this into an existing settings file instead of overwriting unrelated settings.

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node \"$CLAUDE_PROJECT_DIR/.claude/hooks/handoff-watch.mjs\"",
            "timeout": 20,
            "statusMessage": "Checking AGENT_HANDOFF on session start"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node \"$CLAUDE_PROJECT_DIR/.claude/hooks/handoff-watch.mjs\"",
            "timeout": 10,
            "statusMessage": "Checking AGENT_HANDOFF closeout"
          }
        ]
      }
    ],
    "SubagentStop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node \"$CLAUDE_PROJECT_DIR/.claude/hooks/handoff-watch.mjs\"",
            "timeout": 10,
            "statusMessage": "Checking subagent handoff closeout"
          }
        ]
      }
    ]
  }
}
```

## Minimal `handoff-watch.mjs`

```javascript
import fs from "node:fs";
import path from "node:path";

const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const handoffPath = path.join(projectDir, "AGENT_HANDOFF.md");
const handoffDir = path.join(projectDir, ".agent-handoff");

function json(message) {
  process.stdout.write(JSON.stringify(message));
}

try {
  if (!fs.existsSync(handoffPath)) {
    json({
      decision: "approve",
      reason: "AGENT_HANDOFF.md is missing. If this is a meaningful project task, create it before closeout."
    });
    process.exit(0);
  }

  const stat = fs.statSync(handoffPath);
  const ageMinutes = Math.round((Date.now() - stat.mtimeMs) / 60000);
  const content = fs.readFileSync(handoffPath, "utf8");
  const missing = [];

  if (fs.existsSync(handoffDir)) {
    for (const rel of [
      "snapshot.md",
      "workspace.md",
      "decisions.md",
      "work-log.md",
      "validation.md",
      "backlog.md",
      "risks.md",
      "archive.md"
    ]) {
      if (!fs.existsSync(path.join(handoffDir, rel))) missing.push(`.agent-handoff/${rel}`);
    }
    if (!content.includes("## Recovery Reading Order")) missing.push("AGENT_HANDOFF.md Recovery Reading Order");
  } else {
    for (const heading of [
      "## Handoff Snapshot",
      "## Current Work Log",
      "## Validation History",
      "## Task Backlog"
    ]) {
      if (!content.includes(heading)) missing.push(heading);
    }
  }

  const reminders = [];
  if (ageMinutes > 120) reminders.push(`AGENT_HANDOFF.md was last modified about ${ageMinutes} minutes ago.`);
  if (missing.length) reminders.push(`Missing expected sections: ${missing.join(", ")}.`);

  json({
    decision: "approve",
    reason: reminders.length
      ? reminders.join(" ") + " Update the handoff before final response if repository state changed."
      : "Handoff files exist and have the expected core structure."
  });
} catch (error) {
  json({
    decision: "approve",
    reason: `Handoff hook check failed softly: ${error.message}. Manually verify AGENT_HANDOFF.md before closeout.`
  });
}
```
