import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import build, svgkit  # noqa: E402

load_data = svgkit.load_data


def no_external(svg: str) -> bool:
    return "http" not in svg.replace("http://www.w3.org", "")


class HeroTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.svg = build.build_hero(load_data())

    def test_is_xml_and_no_external(self):
        ET.fromstring(self.svg)
        self.assertTrue(no_external(self.svg))

    def test_texts(self):
        for s in [
            "SYS.ONLINE", "NIKOLAUS", "RAY NATHAN", "FULL STACK DEVELOPER",
            "LARAVEL", "NEXT.JS", "SBY-07 // SECTOR 2026", "ID: RAY_NATHANS",
            "[OK]", "building PWA for field technicians [RUNNING]",
        ]:
            self.assertTrue(s in self.svg, f"teks hilang: {s}")

    def test_no_loc_uptime(self):
        self.assertNotIn("LOC:", self.svg)
        self.assertNotIn("UPTIME", self.svg)

    def test_embeds(self):
        self.assertEqual(self.svg.count("data:font/woff2;base64,"), 2)
        self.assertIn("data:image/jpeg;base64,", self.svg)
        self.assertNotIn("<script", self.svg)

    def test_size(self):
        self.assertLess(len(self.svg.encode("utf-8")), 400_000)

    def test_job_strings_toggle(self):
        p = dict(load_data()["profile"], current_job=False)
        js = build.job_strings(p)
        self.assertEqual(js["strip_value"], "OPEN TO WORK")
        self.assertEqual(js["strip_label"], "STATUS")
        self.assertEqual(js["timeline_when"], "2025-08 → 2026-02 · SURABAYA")
        self.assertIn("[READY]", js["term_status"])
        self.assertEqual(js["about_now"], "Open to work · Full Stack")
        self.assertEqual(js["fact01"], "Backend Developer di Performa Optima Group (Ags 2025 – Feb 2026)")
        on = build.job_strings(load_data()["profile"])
        self.assertEqual(on["timeline_when"], "2025-08 → NOW · SURABAYA")
        self.assertEqual(on["strip_value"], "PERFORMA OPTIMA GROUP")
        self.assertEqual(on["about_now"], "Backend Dev @ Performa Optima Group")


class HeaderFooterTests(unittest.TestCase):
    def test_header_content(self):
        s = build.build_header("02", "SKILL MATRIX")
        ET.fromstring(s)
        self.assertIn("02 //", s)
        self.assertIn("SKILL MATRIX", s)
        self.assertIn("sweep", s)
        self.assertTrue(no_external(s))

    def test_six_sections(self):
        self.assertEqual(
            [t for _, t in build.SECTIONS],
            ["IDENTITY", "SKILL MATRIX", "MISSION LOGS", "TELEMETRY", "TIMELINE.LOG", "ESTABLISH CONNECTION"],
        )
        self.assertEqual([i for i, _ in build.SECTIONS], ["01", "02", "03", "04", "05", "06"])

    def test_footer(self):
        s = build.build_footer()
        ET.fromstring(s)
        self.assertIn("END OF TRANSMISSION", s)
        self.assertIn("ship clean code", s)
        self.assertTrue(no_external(s))


class SkillsTests(unittest.TestCase):
    def test_rows_and_segments(self):
        skills = load_data()["skills"]
        s = build.build_skills(skills)
        ET.fromstring(s)
        self.assertEqual(s.count('class="seg on"'), sum(round(x["pct"] / 5) for x in skills))
        self.assertEqual(s.count('class="seg off"'), 20 * len(skills) - sum(round(x["pct"] / 5) for x in skills))
        for name in ("PHP", "98%", "Supabase", "75%", "SELF-ASSESSMENT"):
            self.assertTrue(name in s, f"teks hilang: {name}")
        self.assertTrue(no_external(s))


if __name__ == "__main__":
    unittest.main()
