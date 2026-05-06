// AGENT_HANDOFF_HOOK:START
import fs from "node:fs";
import path from "node:path";

const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const handoffPath = path.join(projectDir, "AGENT_HANDOFF.md");
const handoffDir = path.join(projectDir, ".agent-handoff");

function approve(reason) {
  process.stdout.write(JSON.stringify({
    decision: "approve",
    reason
  }));
  process.exit(0);
}

try {
  if (!fs.existsSync(handoffPath)) {
    approve("AGENT_HANDOFF.md is missing. If this is a meaningful project task, create it before closeout.");
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

  approve(reminders.length
    ? reminders.join(" ") + " Update the handoff before final response if repository state changed."
    : "Handoff files exist and have the expected core structure.");
} catch (error) {
  approve(`Handoff hook check failed softly: ${error.message}. Manually verify AGENT_HANDOFF.md before closeout.`);
}
// AGENT_HANDOFF_HOOK:END
