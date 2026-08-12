#!/usr/bin/env python3
"""检查、压缩并轮转仓库本地 Agent handoff 状态。"""

from __future__ import annotations

import argparse
import os
import re
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


SNAPSHOT_SOFT_BYTES = 16 * 1024
SNAPSHOT_SOFT_LINES = 240
SNAPSHOT_HARD_BYTES = 32 * 1024
SNAPSHOT_HARD_LINES = 400
WORK_LOG_MAX_BYTES = 64 * 1024
WORK_LOG_MAX_SECTIONS = 30
VALIDATION_MAX_BYTES = 64 * 1024
VALIDATION_MAX_ROWS = 200
CURRENT_STATE_MAX_BYTES = 32 * 1024
SINGLE_SOFT_BYTES = 32 * 1024
SINGLE_HARD_BYTES = 64 * 1024
ARCHIVE_CHUNK_BYTES = 128 * 1024

SNAPSHOT_LIST_LIMITS = {
    "立即下一步": 5,
    "活跃文件": 20,
    "待确认问题": 10,
}
SNAPSHOT_SCALAR_FIELDS = {
    "最后更新",
    "上一个 agent",
    "工作区根目录",
    "当前目标",
    "当前状态",
    "阻塞项",
}
# 原样保留、不参与确定性规范化的 snapshot 段落。
SNAPSHOT_PRESERVE_SECTIONS = ["当前执行方案"]


@dataclass
class MaintenanceResult:
    changed: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)

    def merge(self, other: "MaintenanceResult") -> None:
        self.changed.extend(other.changed)
        self.warnings.extend(other.warnings)
        self.unresolved.extend(other.unresolved)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def byte_count(text: str) -> int:
    return len(text.encode("utf-8"))


def line_count(text: str) -> int:
    return len(text.splitlines())


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            delete=False,
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
        ) as handle:
            handle.write(content)
            temp_path = Path(handle.name)
        os.replace(temp_path, path)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def unique_items(items: list[str], limit: int) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        cleaned = item.strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        result.append(cleaned)
        if len(result) == limit:
            break
    return result


def split_utf8(text: str, max_bytes: int) -> list[str]:
    if byte_count(text) <= max_bytes:
        return [text]

    chunks: list[str] = []
    current: list[str] = []
    current_bytes = 0
    for line in text.splitlines(keepends=True):
        encoded = line.encode("utf-8")
        if len(encoded) > max_bytes:
            if current:
                chunks.append("".join(current))
                current = []
                current_bytes = 0
            segment = ""
            for char in line:
                candidate = segment + char
                if byte_count(candidate) > max_bytes:
                    chunks.append(segment)
                    segment = char
                else:
                    segment = candidate
            current = [segment]
            current_bytes = byte_count(segment)
            continue
        if current_bytes + len(encoded) > max_bytes and current:
            chunks.append("".join(current))
            current = []
            current_bytes = 0
        current.append(line)
        current_bytes += len(encoded)
    if current:
        chunks.append("".join(current))
    return chunks


def append_archive_index(handoff_dir: Path, entries: list[tuple[Path, str]]) -> None:
    index_path = handoff_dir / "archive.md"
    content = read_text(index_path).rstrip()
    if not content:
        content = "# Handoff 归档\n\n此文件索引不参与常规恢复的压缩历史。"
    if "## 轮转记录" not in content:
        content += "\n\n## 轮转记录"
    for path, reason in entries:
        relative = path.relative_to(handoff_dir).as_posix()
        link = f"- [{path.name}]({relative}): {reason}"
        if link not in content:
            content += f"\n{link}"
    atomic_write(index_path, content.rstrip() + "\n")


def archive_content(handoff_dir: Path, kind: str, content: str, reason: str) -> list[Path]:
    archive_dir = handoff_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    payload_limit = ARCHIVE_CHUNK_BYTES - 2048
    payloads = split_utf8(content, payload_limit)
    created: list[Path] = []
    for index, payload in enumerate(payloads, start=1):
        suffix = f"-part{index}" if len(payloads) > 1 else ""
        path = archive_dir / f"{kind}-{timestamp}{suffix}.md"
        archived = (
            f"# 已归档 {kind}\n\n"
            f"- 归档时间: {datetime.now(timezone.utc).isoformat()}\n"
            f"- 归档原因: {reason}\n\n"
            "## 原始内容\n\n"
            f"{payload.rstrip()}\n"
        )
        atomic_write(path, archived)
        created.append(path)
    append_archive_index(handoff_dir, [(path, reason) for path in created])
    return created


def h2_sections(text: str, title: str) -> list[str]:
    matches = list(re.finditer(r"(?m)^## ([^\r\n]+)\r?$", text))
    sections: list[str] = []
    for index, match in enumerate(matches):
        if match.group(1).strip() != title:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append(text[start:end].strip())
    return sections


def h2_section_raw(text: str, title: str) -> str | None:
    """返回最后一个匹配 H2 段落的原文（含标题），用于原样保留。"""
    matches = list(re.finditer(r"(?m)^## ([^\r\n]+)\r?$", text))
    raw: str | None = None
    for index, match in enumerate(matches):
        if match.group(1).strip() != title:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        raw = text[match.start():end].strip()
    return raw


def parse_snapshot(text: str) -> tuple[dict[str, str], dict[str, list[str]], list[str]]:
    current_sections = h2_sections(text, "当前状态")
    if not current_sections:
        raise ValueError("snapshot 缺少 '## 当前状态'")

    scalars: dict[str, str] = {}
    lists = {key: [] for key in SNAPSHOT_LIST_LIMITS}
    active_list: str | None = None
    for line in current_sections[-1].splitlines():
        field_match = re.match(r"^- ([^:]+):\s*(.*)$", line)
        if field_match:
            key = field_match.group(1).strip()
            value = field_match.group(2).strip()
            if key in SNAPSHOT_LIST_LIMITS:
                active_list = key
                if value:
                    lists[key].append(value)
            elif key in SNAPSHOT_SCALAR_FIELDS:
                scalars[key] = value
                active_list = None
            else:
                active_list = None
            continue
        item_match = re.match(r"^\s{2,}-\s+(.+)$", line)
        if item_match and active_list:
            lists[active_list].append(item_match.group(1).strip())

    required = ["当前目标", "当前状态"]
    missing = [key for key in required if not scalars.get(key)]
    if missing or not lists["立即下一步"]:
        details = ", ".join(missing + (["立即下一步"] if not lists["立即下一步"] else []))
        raise ValueError(f"snapshot 缺少必需的当前状态字段: {details}")

    recovery_sections = h2_sections(text, "恢复摘要")
    recovery: list[str] = []
    if recovery_sections:
        for line in recovery_sections[-1].splitlines():
            match = re.match(r"^-\s+(.+)$", line)
            if match:
                recovery.append(match.group(1).strip())
    return scalars, lists, recovery


def truncate_utf8(value: str, max_bytes: int) -> str:
    marker = "... [已截断; 见归档]"
    if byte_count(value) <= max_bytes:
        return value
    budget = max_bytes - byte_count(marker)
    if budget <= 0:
        return marker[:max_bytes]
    result: list[str] = []
    used = 0
    for char in value:
        size = byte_count(char)
        if used + size > budget:
            break
        result.append(char)
        used += size
    return "".join(result).rstrip() + marker


def render_snapshot(
    scalars: dict[str, str],
    lists: dict[str, list[str]],
    recovery: list[str],
    preserved: list[str],
) -> str:
    scalar_limits = {
        "最后更新": 256,
        "上一个 agent": 256,
        "工作区根目录": 512,
        "当前目标": 768,
        "当前状态": 768,
        "阻塞项": 768,
    }
    lines = ["# Handoff 快照", "", "## 当前状态", ""]
    for key in ["最后更新", "上一个 agent", "工作区根目录", "当前目标", "当前状态"]:
        if key in scalars:
            lines.append(f"- {key}: {truncate_utf8(scalars[key], scalar_limits[key])}")

    for key in ["立即下一步", "活跃文件"]:
        lines.append(f"- {key}:")
        values = unique_items(lists[key], SNAPSHOT_LIST_LIMITS[key])
        lines.extend(f"  - {truncate_utf8(value, 256)}" for value in values)

    if "阻塞项" in scalars:
        lines.append(f"- 阻塞项: {truncate_utf8(scalars['阻塞项'], scalar_limits['阻塞项'])}")

    lines.append("- 待确认问题:")
    questions = unique_items(lists["待确认问题"], SNAPSHOT_LIST_LIMITS["待确认问题"])
    lines.extend(f"  - {truncate_utf8(value, 256)}" for value in questions)

    for section in preserved:
        lines.extend(["", section])

    recovery_items = unique_items(recovery, 5)
    if not recovery_items:
        recovery_items = ["从当前目标和立即下一步恢复。"]
    lines.extend(["", "## 恢复摘要", ""])
    lines.extend(f"- {truncate_utf8(item, 256)}" for item in recovery_items)
    return "\n".join(lines).rstrip() + "\n"


def exceeds_snapshot_soft_limit(text: str) -> bool:
    return byte_count(text) > SNAPSHOT_SOFT_BYTES or line_count(text) > SNAPSHOT_SOFT_LINES


def exceeds_snapshot_hard_limit(text: str) -> bool:
    return byte_count(text) > SNAPSHOT_HARD_BYTES or line_count(text) > SNAPSHOT_HARD_LINES


def maintain_snapshot(handoff_dir: Path) -> MaintenanceResult:
    result = MaintenanceResult()
    path = handoff_dir / "snapshot.md"
    if not path.exists():
        result.unresolved.append(".agent-handoff/snapshot.md 缺失。")
        return result

    original = read_text(path)
    if not exceeds_snapshot_soft_limit(original):
        return result

    severity = "硬限" if exceeds_snapshot_hard_limit(original) else "软限"
    try:
        scalars, lists, recovery = parse_snapshot(original)
    except ValueError as error:
        result.unresolved.append(
            f"snapshot 超过{severity}但无法安全解析，已保留原文: {error}。"
        )
        return result

    preserved = [
        raw
        for title in SNAPSHOT_PRESERVE_SECTIONS
        if (raw := h2_section_raw(original, title)) is not None
    ]
    compacted = render_snapshot(scalars, lists, recovery, preserved)
    if exceeds_snapshot_soft_limit(compacted):
        result.unresolved.append(
            "snapshot 规范化后仍超过 16 KiB / 240 行软限，已保留原文。"
        )
        return result

    reason = (
        f"snapshot 超过{severity}"
        f"（{byte_count(original)} 字节, {line_count(original)} 行）"
    )
    archive_content(handoff_dir, "snapshot", original, reason)
    atomic_write(path, compacted)
    result.changed.append(".agent-handoff/snapshot.md")
    result.changed.append(".agent-handoff/archive.md")
    result.warnings.append(f"已压缩并归档超限 snapshot: {reason}。")
    return result


def remove_spans(text: str, spans: list[tuple[int, int]]) -> str:
    if not spans:
        return text
    parts: list[str] = []
    cursor = 0
    for start, end in sorted(spans):
        parts.append(text[cursor:start])
        cursor = end
    parts.append(text[cursor:])
    return "".join(parts)


def dated_h2_sections(text: str) -> list[tuple[int, int, str]]:
    headings = list(re.finditer(r"(?m)^## [^\r\n]+\r?$", text))
    sections: list[tuple[int, int, str]] = []
    for index, heading in enumerate(headings):
        title = heading.group(0)[3:].strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}(?:\b|\s)", title):
            continue
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        sections.append((heading.start(), end, text[heading.start():end]))
    return sections


def maintain_work_log(handoff_dir: Path) -> MaintenanceResult:
    result = MaintenanceResult()
    path = handoff_dir / "work-log.md"
    if not path.exists():
        result.unresolved.append(".agent-handoff/work-log.md 缺失。")
        return result

    original = read_text(path)
    sections = dated_h2_sections(original)
    if byte_count(original) <= WORK_LOG_MAX_BYTES and len(sections) <= WORK_LOG_MAX_SECTIONS:
        return result
    if len(sections) < 2:
        result.unresolved.append(
            "work-log.md 超限，但可轮转的完整日期段落不足两个。"
        )
        return result

    remove_count = max(0, len(sections) - WORK_LOG_MAX_SECTIONS)
    while remove_count < len(sections) - 1:
        candidate = remove_spans(original, [(start, end) for start, end, _ in sections[:remove_count]])
        if byte_count(candidate) <= WORK_LOG_MAX_BYTES:
            break
        remove_count += 1

    if remove_count == 0:
        remove_count = 1
    removed_sections = sections[:remove_count]
    compacted = remove_spans(original, [(start, end) for start, end, _ in removed_sections])
    if byte_count(compacted) > WORK_LOG_MAX_BYTES:
        result.unresolved.append(
            "work-log.md 在保留最新完整日期段落后仍超过 64 KiB。"
        )
        return result

    archived = "".join(section for _, _, section in removed_sections).strip() + "\n"
    reason = f"work log 超过 64 KiB 或 {WORK_LOG_MAX_SECTIONS} 个日期段落"
    archive_content(handoff_dir, "work-log", archived, reason)
    atomic_write(path, compacted.lstrip("\n"))
    result.changed.extend([".agent-handoff/work-log.md", ".agent-handoff/archive.md"])
    result.warnings.append(f"已轮转 {remove_count} 个旧 work-log 段落。")
    return result


def validation_table(text: str) -> tuple[list[str], int, int, list[str]] | None:
    lines = text.splitlines(keepends=True)
    separator_pattern = re.compile(r"^\s*\|(?:\s*:?-+:?\s*\|)+\s*$")
    for separator_index, line in enumerate(lines):
        if separator_index == 0 or not separator_pattern.match(line.rstrip("\r\n")):
            continue
        if not lines[separator_index - 1].lstrip().startswith("|"):
            continue
        data_start = separator_index + 1
        data_end = data_start
        while data_end < len(lines) and lines[data_end].lstrip().startswith("|"):
            data_end += 1
        return lines, data_start, data_end, lines[data_start:data_end]
    return None


def maintain_validation(handoff_dir: Path) -> MaintenanceResult:
    result = MaintenanceResult()
    path = handoff_dir / "validation.md"
    if not path.exists():
        result.unresolved.append(".agent-handoff/validation.md 缺失。")
        return result

    original = read_text(path)
    parsed = validation_table(original)
    row_count = len(parsed[3]) if parsed else 0
    if byte_count(original) <= VALIDATION_MAX_BYTES and row_count <= VALIDATION_MAX_ROWS:
        return result
    if parsed is None or row_count < 2:
        result.unresolved.append(
            "validation.md 超限，但没有可安全轮转的 Markdown 表格行。"
        )
        return result

    lines, data_start, data_end, rows = parsed
    remove_count = max(0, len(rows) - VALIDATION_MAX_ROWS)
    while remove_count < len(rows) - 1:
        candidate = "".join(lines[:data_start] + rows[remove_count:] + lines[data_end:])
        if byte_count(candidate) <= VALIDATION_MAX_BYTES:
            break
        remove_count += 1
    if remove_count == 0:
        remove_count = 1

    compacted = "".join(lines[:data_start] + rows[remove_count:] + lines[data_end:])
    if byte_count(compacted) > VALIDATION_MAX_BYTES:
        result.unresolved.append(
            "validation.md 在保留最新完整表格行后仍超过 64 KiB。"
        )
        return result

    table_header = "".join(lines[data_start - 2:data_start])
    archived = table_header + "".join(rows[:remove_count])
    reason = f"validation 历史超过 64 KiB 或 {VALIDATION_MAX_ROWS} 行"
    archive_content(handoff_dir, "validation", archived, reason)
    atomic_write(path, compacted)
    result.changed.extend([".agent-handoff/validation.md", ".agent-handoff/archive.md"])
    result.warnings.append(f"已轮转 {remove_count} 行旧 validation 记录。")
    return result


def completed_backlog_spans(text: str) -> list[tuple[int, int, str]]:
    lines = text.splitlines(keepends=True)
    offsets: list[int] = []
    cursor = 0
    for line in lines:
        offsets.append(cursor)
        cursor += len(line)

    spans: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        if not re.match(r"^- \[[xX]\] .+", line):
            continue
        end_index = index + 1
        while end_index < len(lines):
            candidate = lines[end_index]
            if not candidate.strip() or candidate.startswith((" ", "\t")):
                end_index += 1
                continue
            break
        start = offsets[index]
        end = offsets[end_index] if end_index < len(lines) else len(text)
        spans.append((start, end, text[start:end]))
    return spans


def maintain_backlog(handoff_dir: Path) -> MaintenanceResult:
    result = MaintenanceResult()
    path = handoff_dir / "backlog.md"
    if not path.exists():
        result.unresolved.append(".agent-handoff/backlog.md 缺失。")
        return result

    original = read_text(path)
    if byte_count(original) <= CURRENT_STATE_MAX_BYTES:
        return result
    completed = completed_backlog_spans(original)
    if not completed:
        result.unresolved.append(
            "backlog.md 超过 32 KiB，且没有可机械归档的已完成勾选项。"
        )
        return result

    remove_count = 0
    compacted = original
    while byte_count(compacted) > CURRENT_STATE_MAX_BYTES and remove_count < len(completed):
        remove_count += 1
        compacted = remove_spans(
            original,
            [(start, end) for start, end, _ in completed[:remove_count]],
        )
    if byte_count(compacted) > CURRENT_STATE_MAX_BYTES:
        result.unresolved.append(
            "backlog.md 在归档全部已完成勾选项后仍超过 32 KiB，已保留原文。"
        )
        return result

    archived = "".join(item for _, _, item in completed[:remove_count]).strip() + "\n"
    archive_content(
        handoff_dir,
        "backlog-completed",
        archived,
        "backlog 超过 32 KiB；已归档已完成勾选项",
    )
    atomic_write(path, compacted)
    result.changed.extend([".agent-handoff/backlog.md", ".agent-handoff/archive.md"])
    result.warnings.append(f"已归档 {remove_count} 条已完成 backlog 项。")
    return result


def inspect_repository(repo: Path) -> MaintenanceResult:
    result = MaintenanceResult()
    single_path = repo / "AGENT_HANDOFF.md"
    handoff_dir = repo / ".agent-handoff"

    if handoff_dir.is_dir():
        if not (handoff_dir / "README.md").exists():
            result.unresolved.append(".agent-handoff/README.md 入口缺失。")

        for name in [
            "workspace.md",
            "decisions.md",
            "work-log.md",
            "validation.md",
            "backlog.md",
            "risks.md",
            "archive.md",
        ]:
            if not (handoff_dir / name).exists():
                result.unresolved.append(f".agent-handoff/{name} 缺失。")

        snapshot_path = handoff_dir / "snapshot.md"
        if snapshot_path.exists():
            snapshot = read_text(snapshot_path)
            metrics = f"{byte_count(snapshot)} 字节, {line_count(snapshot)} 行"
            if exceeds_snapshot_hard_limit(snapshot):
                result.unresolved.append(
                    f"snapshot.md 超过 32 KiB / 400 行硬限（{metrics}）。"
                )
            elif exceeds_snapshot_soft_limit(snapshot):
                result.warnings.append(
                    f"snapshot.md 超过 16 KiB / 240 行软限（{metrics}）。"
                )
        else:
            result.unresolved.append(".agent-handoff/snapshot.md 缺失。")

        work_log_path = handoff_dir / "work-log.md"
        if work_log_path.exists():
            work_log = read_text(work_log_path)
            sections = len(dated_h2_sections(work_log))
            if byte_count(work_log) > WORK_LOG_MAX_BYTES or sections > WORK_LOG_MAX_SECTIONS:
                result.warnings.append(
                    f"work-log.md 超过 64 KiB 或 {WORK_LOG_MAX_SECTIONS} 个日期段落（{byte_count(work_log)} 字节, {sections} 段）。"
                )

        validation_path = handoff_dir / "validation.md"
        if validation_path.exists():
            validation = read_text(validation_path)
            parsed = validation_table(validation)
            rows = len(parsed[3]) if parsed else 0
            if byte_count(validation) > VALIDATION_MAX_BYTES or rows > VALIDATION_MAX_ROWS:
                result.warnings.append(
                    f"validation.md 超过 64 KiB 或 {VALIDATION_MAX_ROWS} 行（{byte_count(validation)} 字节, {rows} 行）。"
                )

        for name in ["backlog.md", "risks.md"]:
            path = handoff_dir / name
            if path.exists() and path.stat().st_size > CURRENT_STATE_MAX_BYTES:
                result.unresolved.append(
                    f"{name} 超过 32 KiB 当前状态上限（{path.stat().st_size} 字节），需要语义化清理。"
                )

        archive_dir = handoff_dir / "archive"
        if archive_dir.is_dir():
            for path in archive_dir.glob("*.md"):
                if path.stat().st_size > ARCHIVE_CHUNK_BYTES:
                    result.unresolved.append(
                        f"归档块 {path.name} 超过 128 KiB 上限（{path.stat().st_size} 字节）。"
                    )
        return result

    if not single_path.exists():
        result.unresolved.append("未找到 handoff 入口：.agent-handoff/ 目录和 AGENT_HANDOFF.md 均缺失。")
        return result

    content = read_text(single_path)
    if byte_count(content) > SINGLE_HARD_BYTES:
        result.unresolved.append(
            f"单文档 AGENT_HANDOFF.md 超过 64 KiB 硬限（{byte_count(content)} 字节），请迁移到 multi 布局。"
        )
    elif byte_count(content) > SINGLE_SOFT_BYTES:
        result.warnings.append(
            f"单文档 AGENT_HANDOFF.md 超过 32 KiB 软限（{byte_count(content)} 字节）。"
        )
    return result


def deduplicate_result(result: MaintenanceResult) -> MaintenanceResult:
    result.changed = list(dict.fromkeys(result.changed))
    result.warnings = list(dict.fromkeys(result.warnings))
    result.unresolved = list(dict.fromkeys(result.unresolved))
    return result


def maintain_repository(
    repo: Path, include_snapshot: bool = True, include_logs: bool = True
) -> MaintenanceResult:
    repo = repo.expanduser().resolve()
    handoff_dir = repo / ".agent-handoff"
    result = MaintenanceResult()
    if not handoff_dir.is_dir():
        return inspect_repository(repo)

    if include_snapshot:
        result.merge(maintain_snapshot(handoff_dir))
    if include_logs:
        result.merge(maintain_work_log(handoff_dir))
        result.merge(maintain_validation(handoff_dir))
        result.merge(maintain_backlog(handoff_dir))
    result.merge(inspect_repository(repo))
    return deduplicate_result(result)


def print_result(result: MaintenanceResult) -> None:
    print(
        "Handoff 维护: "
        f"changed={len(result.changed)} warnings={len(result.warnings)} unresolved={len(result.unresolved)}"
    )
    for path in result.changed:
        print(f"CHANGED: {path}")
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for unresolved in result.unresolved:
        print(f"UNRESOLVED: {unresolved}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="检查、压缩并轮转仓库本地 Agent handoff 状态。"
    )
    parser.add_argument("--repo", default=".", help="仓库根目录，默认当前目录。")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--check", action="store_true", help="只读检查容量限制，不写文件（默认）。")
    actions.add_argument(
        "--compact-if-needed",
        action="store_true",
        help="安全地压缩超限 snapshot 并轮转超限历史记录。",
    )
    actions.add_argument(
        "--rotate",
        action="store_true",
        help="只轮转超限的 work-log、validation 和已完成 backlog 记录。",
    )
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        parser.error(f"仓库路径不是目录: {repo}")

    if args.compact_if_needed:
        result = maintain_repository(repo, include_snapshot=True, include_logs=True)
    elif args.rotate:
        result = maintain_repository(repo, include_snapshot=False, include_logs=True)
    else:
        result = inspect_repository(repo)
    print_result(result)
    return 2 if result.unresolved else 0


if __name__ == "__main__":
    raise SystemExit(main())
