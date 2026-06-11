#!/usr/bin/env node
// AGENT_HANDOFF_HOOK:START
import fs from "node:fs";
import path from "node:path";

const MULTI_INDEX = ".agent-handoff/README.md";
const MULTI_FILES = [
  "snapshot.md",
  "workspace.md",
  "decisions.md",
  "work-log.md",
  "validation.md",
  "backlog.md",
  "risks.md",
  "archive.md"
];

const SINGLE_HEADINGS = [
  "## Handoff 快照",
  "## 当前工作日志",
  "## 验证历史",
  "## 任务积压"
];

const PROMPT_TRIGGERS = [
  "handoff",
  "agent_handoff",
  "continue",
  "resume",
  "closeout",
  "compact",
  "handover",
  "recover",
  "resume work",
  "session state",
  "restore context"
];

const DEFAULT_MAX_AGE_MINUTES = 120;
const MAX_READ_BYTES = 512 * 1024;
const INPUT_RETRY_LIMIT = 2;

function optionValue(name) {
  const flag = `--${name}`;
  const exact = process.argv.find((arg) => arg.startsWith(`${flag}=`));
  if (exact) return exact.slice(flag.length + 1);
  const index = process.argv.indexOf(flag);
  if (index !== -1 && index + 1 < process.argv.length) return process.argv[index + 1];
  return undefined;
}

function sleep(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

function exists(filePath) {
  try {
    return fs.existsSync(filePath);
  } catch {
    return false;
  }
}

function isDirectory(filePath) {
  try {
    return fs.statSync(filePath).isDirectory();
  } catch {
    return false;
  }
}

function readSmallText(filePath) {
  try {
    const stat = fs.statSync(filePath);
    if (stat.size > MAX_READ_BYTES) {
      const handle = fs.openSync(filePath, "r");
      try {
        const buffer = Buffer.alloc(MAX_READ_BYTES);
        const bytesRead = fs.readSync(handle, buffer, 0, MAX_READ_BYTES, 0);
        return buffer.subarray(0, bytesRead).toString("utf8");
      } finally {
        fs.closeSync(handle);
      }
    }
    return fs.readFileSync(filePath, "utf8");
  } catch {
    return "";
  }
}

function readHookInputWithRetry() {
  if (process.stdin.isTTY) return { input: {}, parseWarning: null };

  let lastWarning = null;
  for (let attempt = 0; attempt <= INPUT_RETRY_LIMIT; attempt += 1) {
    try {
      const raw = fs.readFileSync(0, "utf8").trim();
      if (!raw) return { input: {}, parseWarning: lastWarning };
      return { input: JSON.parse(raw), parseWarning: null };
    } catch (error) {
      const retryable = error instanceof SyntaxError || error.code === "EAGAIN";
      lastWarning = retryable
        ? `Hook stdin 在第 ${attempt + 1} 次尝试后读取/解析异常: ${error.message}`
        : `无法读取 hook stdin: ${error.message}`;
      if (!retryable || attempt === INPUT_RETRY_LIMIT) {
        return { input: {}, parseWarning: lastWarning };
      }
      sleep(20 * (attempt + 1));
    }
  }

  return { input: {}, parseWarning: lastWarning };
}

function ageMinutes(filePath) {
  try {
    const stat = fs.statSync(filePath);
    return Math.max(0, Math.round((Date.now() - stat.mtimeMs) / 60000));
  } catch {
    return null;
  }
}

function containsAny(text, terms) {
  const lower = text.toLowerCase();
  return terms.some((term) => lower.includes(term.toLowerCase()));
}

function buildHealth(projectDir, maxAgeMinutes, parseWarning) {
  const singlePath = path.join(projectDir, "AGENT_HANDOFF.md");
  const multiIndexPath = path.join(projectDir, MULTI_INDEX);
  const handoffDir = path.join(projectDir, ".agent-handoff");
  const singleExists = exists(singlePath);
  const multiIndexExists = exists(multiIndexPath);
  const content = multiIndexExists
    ? readSmallText(multiIndexPath)
    : singleExists
      ? readSmallText(singlePath)
      : "";
  const health = {
    projectDir,
    layout: "missing",
    handoffPath: multiIndexExists ? multiIndexPath : singlePath,
    handoffDir,
    ageMinutes: null,
    critical: [],
    warnings: [],
    missing: []
  };

  if (parseWarning) health.warnings.push(parseWarning);

  if (!singleExists && !multiIndexExists) {
    health.critical.push("缺少 .agent-handoff 和 AGENT_HANDOFF.md。");
    return health;
  }

  const activePath = multiIndexExists ? multiIndexPath : singlePath;
  health.ageMinutes = ageMinutes(activePath);

  if (isDirectory(handoffDir) && multiIndexExists) {
    health.layout = "multi";

    for (const rel of MULTI_FILES) {
      if (!exists(path.join(handoffDir, rel))) {
        health.missing.push(`.agent-handoff/${rel}`);
      }
    }

    if (!content.includes("## 恢复阅读顺序")) {
      health.critical.push(
        "多文档布局已存在，但 .agent-handoff/README.md 不包含 '## 恢复阅读顺序'。"
      );
    }

    if (!content.includes("## Handoff 布局")) {
      health.warnings.push(".agent-handoff/README.md 不包含 '## Handoff 布局'。");
    }

    const snapshot = readSmallText(path.join(handoffDir, "snapshot.md"));
    if (snapshot && !snapshot.includes("## 当前状态")) {
      health.warnings.push(".agent-handoff/snapshot.md 不包含 '## 当前状态'。");
    }
  } else {
    health.layout = "single";

    for (const heading of SINGLE_HEADINGS) {
      if (!content.includes(heading)) {
        health.missing.push(heading);
      }
    }
  }

  if (health.missing.length > 0) {
    health.critical.push(`缺少预期的 handoff 结构: ${health.missing.join(", ")}。`);
  }

  if (health.ageMinutes !== null && health.ageMinutes > maxAgeMinutes) {
    health.warnings.push(
      `AGENT_HANDOFF.md 约 ${health.ageMinutes} 分钟前最后修改。`
    );
  }

  return health;
}

function recoveryHint(health) {
  if (health.layout === "multi") {
    return [
      "先读取 .agent-handoff/README.md。",
      "然后读取 .agent-handoff/snapshot.md、.agent-handoff/risks.md 和 .agent-handoff/backlog.md。",
      "仅在与任务相关时读取 validation、decisions、workspace、work-log 和 archive。"
    ].join(" ");
  }

  if (health.layout === "single") {
    return "先读取 AGENT_HANDOFF.md，然后只检查与任务相关的源文件。";
  }

  return "依赖仓库 handoff 记忆前，先创建或修复 .agent-handoff/README.md 或 AGENT_HANDOFF.md。";
}

function healthSummary(health) {
  const parts = [
    `Agent handoff 健康状态: layout=${health.layout}`,
    health.ageMinutes === null ? "age=未知" : `age=${health.ageMinutes}m`
  ];

  if (health.critical.length) parts.push(`critical=${health.critical.join(" ")}`);
  if (health.warnings.length) parts.push(`warnings=${health.warnings.join(" ")}`);
  parts.push(recoveryHint(health));
  return parts.join(" ");
}

function writeJson(output) {
  process.stdout.write(`${JSON.stringify(output, null, 2)}\n`);
}

function contextOutput(eventName, context, suppressOutput = false) {
  return {
    continue: true,
    suppressOutput,
    hookSpecificOutput: {
      hookEventName: eventName,
      additionalContext: context
    }
  };
}

function systemOutput(message, suppressOutput = false) {
  return {
    continue: true,
    suppressOutput,
    systemMessage: message
  };
}

const { input, parseWarning } = readHookInputWithRetry();
const eventName = input.hook_event_name || optionValue("event") || "Manual";
const maxAgeMinutes = Number.parseInt(
  process.env.HANDOFF_MAX_AGE_MINUTES || optionValue("max-age-minutes") || `${DEFAULT_MAX_AGE_MINUTES}`,
  10
);
const projectDir = path.resolve(
  optionValue("project-dir") ||
    process.env.CLAUDE_PROJECT_DIR ||
    input.cwd ||
    process.cwd()
);
const health = buildHealth(
  projectDir,
  Number.isFinite(maxAgeMinutes) ? maxAgeMinutes : DEFAULT_MAX_AGE_MINUTES,
  parseWarning
);
const summary = healthSummary(health);

try {
  switch (eventName) {
    case "SessionStart": {
      writeJson(contextOutput("SessionStart", summary, false));
      break;
    }

    case "UserPromptSubmit": {
      const prompt = String(input.prompt || "");
      if (health.critical.length > 0 || containsAny(prompt, PROMPT_TRIGGERS)) {
        writeJson(contextOutput("UserPromptSubmit", summary, false));
      } else {
        writeJson({ continue: true, suppressOutput: true });
      }
      break;
    }

    case "PreCompact": {
      writeJson(
        systemOutput(
          `${summary} 压缩前，如果当前任务状态已变化，请更新 handoff 文件。`,
          false
        )
      );
      break;
    }

    case "Stop":
    case "SubagentStop": {
      if (input.stop_hook_active) {
        writeJson({ continue: true, suppressOutput: true });
        break;
      }

      writeJson(
        systemOutput(
          `${summary} 如果仓库状态已变化，请在最终回复前更新相关 handoff 文件。`,
          false
        )
      );
      break;
    }

    case "SessionEnd": {
      writeJson(systemOutput(`会话即将结束。${summary}`, true));
      break;
    }

    default: {
      writeJson(systemOutput(summary, false));
      break;
    }
  }
} catch (error) {
  writeJson(
    systemOutput(
      `Handoff hook 软失败: ${error.message}。收尾前请手动验证 AGENT_HANDOFF.md。`,
      false
    )
  );
}
// AGENT_HANDOFF_HOOK:END
