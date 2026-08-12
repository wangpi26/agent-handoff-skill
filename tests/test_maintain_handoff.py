import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "maintain_handoff.py"
BOOTSTRAP = ROOT / "scripts" / "bootstrap_handoff.py"


class MaintainHandoffTest(unittest.TestCase):
    def setUp(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.repo = Path(temp_dir.name)
        subprocess.run(
            [
                sys.executable,
                str(BOOTSTRAP),
                "--repo",
                str(self.repo),
                "--platform",
                "both",
                "--layout",
                "multi",
                "--scope",
                "standalone",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    def run_maintain(self, *flags: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--repo", str(self.repo), *flags],
            capture_output=True,
            text=True,
        )

    def test_check_fresh_repo_is_clean(self) -> None:
        result = self.run_maintain("--check")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("unresolved=0", result.stdout)

    def test_compact_oversized_snapshot_preserves_plan_section(self) -> None:
        snapshot = self.repo / ".agent-handoff" / "snapshot.md"
        original = snapshot.read_text()
        plan_section = original[original.index("## 当前执行方案"):]
        padding = "- 待确认问题:\n" + "".join(f"  - 冗余项 {index}\n" for index in range(300))
        snapshot.write_text(original + padding)

        result = self.run_maintain("--compact-if-needed")
        self.assertIn("snapshot.md", result.stdout)
        compacted = snapshot.read_text()
        self.assertLess(len(compacted.encode("utf-8")), 16 * 1024)
        self.assertIn("## 当前执行方案", compacted)
        self.assertIn("- 状态: unknown", compacted)
        self.assertTrue((self.repo / ".agent-handoff" / "archive").is_dir())
        archived_index = (self.repo / ".agent-handoff" / "archive.md").read_text()
        self.assertIn("## 轮转记录", archived_index)
        self.assertIn(plan_section.splitlines()[0], archived_index + compacted)

    def test_unparseable_snapshot_is_preserved(self) -> None:
        snapshot = self.repo / ".agent-handoff" / "snapshot.md"
        broken = "# 损坏\n\n" + "x" * (17 * 1024)
        snapshot.write_text(broken)

        result = self.run_maintain("--compact-if-needed")
        self.assertEqual(result.returncode, 2)
        self.assertIn("UNRESOLVED", result.stdout)
        self.assertEqual(snapshot.read_text(), broken)

    def test_work_log_rotation(self) -> None:
        work_log = self.repo / ".agent-handoff" / "work-log.md"
        sections = ["# 当前工作日志\n"]
        for index in range(40):
            sections.append(f"\n## 2026-01-{index % 28 + 1:02d}\n\n- 目标: 任务 {index}\n")
        work_log.write_text("".join(sections))

        result = self.run_maintain("--rotate")
        self.assertIn("work-log.md", result.stdout)
        remaining = work_log.read_text()
        self.assertLessEqual(remaining.count("\n## 20"), 30)
        self.assertTrue(list((self.repo / ".agent-handoff" / "archive").glob("work-log-*.md")))

    def test_single_layout_size_warning(self) -> None:
        single_repo = self.repo / "single"
        single_repo.mkdir()
        handoff = single_repo / "AGENT_HANDOFF.md"
        handoff.write_text("# Agent Handoff\n\n" + "x" * (33 * 1024))

        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--repo", str(single_repo), "--check"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("软限", result.stdout)


if __name__ == "__main__":
    unittest.main()
