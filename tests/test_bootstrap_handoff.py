import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "bootstrap_handoff.py"


class BootstrapHandoffTest(unittest.TestCase):
    def bootstrap(self, layout: str) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name)
        subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--repo",
                str(repo),
                "--platform",
                "both",
                "--layout",
                layout,
                "--scope",
                "standalone",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return repo

    def test_multi_layout_contains_current_plan_contract(self) -> None:
        repo = self.bootstrap("multi")
        index = (repo / ".agent-handoff" / "README.md").read_text()
        snapshot = (repo / ".agent-handoff" / "snapshot.md").read_text()

        self.assertIn("## 当前执行方案恢复契约", index)
        self.assertIn("## 当前执行方案", snapshot)
        self.assertIn("- 状态: unknown", snapshot)
        self.assertIn("- 主方案: UNKNOWN", snapshot)

    def test_single_layout_contains_current_plan_contract(self) -> None:
        repo = self.bootstrap("single")
        handoff = (repo / "AGENT_HANDOFF.md").read_text()

        self.assertIn("## 当前执行方案", handoff)
        self.assertIn("- 状态: unknown", handoff)
        self.assertIn("显式声明的安全硬边界", handoff)
        self.assertIn("关键操作前", handoff)


if __name__ == "__main__":
    unittest.main()
