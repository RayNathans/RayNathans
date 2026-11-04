import glob
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import build  # noqa: E402


class RepoTests(unittest.TestCase):
    def test_assets_match_build(self):
        """Hasil build yang di-commit identik dengan build segar."""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / "assets").mkdir()
            build.main(out=out)
            for path in sorted(glob.glob(str(out / "assets" / "*.svg"))) + [str(out / "README.md")]:
                rel = Path(path).relative_to(out)
                fresh = Path(path).read_text(encoding="utf-8")
                committed = (ROOT / rel).read_text(encoding="utf-8")
                self.assertEqual(fresh, committed, f"{rel} belum dibangun ulang: jalankan tools/build.py")

    def test_svgs_small_and_offline(self):
        svgs = glob.glob(str(ROOT / "assets" / "*.svg"))
        self.assertGreaterEqual(len(svgs), 12)
        for path in svgs:
            text = Path(path).read_text(encoding="utf-8")
            self.assertLess(len(text.encode("utf-8")), 400_000, path)
            self.assertNotIn("http", text.replace("http://www.w3.org", ""), path)
            self.assertIn("prefers-reduced-motion", text, path)
            self.assertNotIn("<script", text, path)

    def test_workflows_valid_yaml(self):
        import yaml

        snake_txt = (ROOT / ".github/workflows/snake.yml").read_text(encoding="utf-8")
        snake = yaml.safe_load(snake_txt)
        self.assertIn("workflow_dispatch", snake[True] if True in snake else snake["on"])
        self.assertIn("RayNathans", snake_txt)
        self.assertIn("output", snake_txt)
        bld = yaml.safe_load((ROOT / ".github/workflows/build.yml").read_text(encoding="utf-8"))
        self.assertIn("jobs", bld)

    def test_snake_colors_have_hash(self):
        """Platane/snk memakai nilai warna apa adanya; tanpa '#' hasilnya hitam."""
        import re

        txt = (ROOT / ".github/workflows/snake.yml").read_text(encoding="utf-8")
        outputs = re.search(r"dist/github-snake\.svg\?(\S+)", txt).group(1)
        for key in ("color_dots", "color_snake"):
            val = re.search(key + r"=([^&\s]+)", outputs).group(1)
            for color in val.split(","):
                self.assertTrue(color.startswith("#"), f"{key}: {color} tanpa #")

    def test_build_workflow_builds_before_testing(self):
        """CI harus membangun ulang aset dulu; test membandingkan aset dengan build segar."""
        import yaml

        bld = yaml.safe_load((ROOT / ".github/workflows/build.yml").read_text(encoding="utf-8"))
        names = [s.get("name", "") for s in bld["jobs"]["build"]["steps"]]
        i_build = next(i for i, n in enumerate(names) if n.startswith("Build"))
        i_test = next(i for i, n in enumerate(names) if n.startswith("Test"))
        i_commit = next(i for i, n in enumerate(names) if n.startswith("Commit"))
        self.assertLess(i_build, i_test)
        self.assertLess(i_test, i_commit)
        self.assertIn("concurrency", bld)

    def test_no_attribution_markers_in_history(self):
        log = subprocess.run(["git", "log", "--format=%B"], cwd=ROOT, capture_output=True, text=True).stdout
        self.assertNotIn("Co-Authored-By", log)
        self.assertNotIn("Generated with", log)

    def test_handoff_doc(self):
        doc = (ROOT / "docs/SERAH-TERIMA.md").read_text(encoding="utf-8")
        for s in ["RayNathans/RayNathans", "Public profile", "current_job", "nikolausraynathan@gmail.com", "OFL", "snake"]:
            self.assertIn(s, doc)


if __name__ == "__main__":
    unittest.main()
