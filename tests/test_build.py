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


class ProjectTests(unittest.TestCase):
    def test_three_cards(self):
        for p in load_data()["projects"]:
            s = build.build_project(p)
            ET.fromstring(s)
            self.assertTrue(p["title"] in s, p["title"])
            self.assertTrue(p["status"] in s, p["status"])
            for t in p["stack"]:
                self.assertTrue(t in s, t)
            self.assertIn("LIVE DEMO", s)
            self.assertTrue(no_external(s), p["id"])

    def test_wrap(self):
        self.assertEqual(
            build.wrap_text("Deteksi kematangan & manfaat buah berbasis AI. Antarmuka minimalis dan aksesibel.", 46),
            ["Deteksi kematangan & manfaat buah berbasis AI.", "Antarmuka minimalis dan aksesibel."],
        )
        self.assertEqual(build.wrap_text("satu dua tiga", 7), ["satu", "dua", "tiga"])


class ReadmeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = load_data()
        cls.md = build.build_readme(cls.d)

    def test_badge_escape(self):
        self.assertEqual(
            build.badge("ROLE", "BACKEND_DEV", "00e5ff"),
            "https://img.shields.io/badge/ROLE-BACKEND__DEV-00e5ff?style=for-the-badge&labelColor=0a0f24",
        )
        self.assertEqual(
            build.badge("", "Next.js", "0a0f24", logo="nextdotjs", logo_color="ffffff"),
            "https://img.shields.io/badge/Next.js-0a0f24?style=for-the-badge&labelColor=0a0f24&logo=nextdotjs&logoColor=ffffff",
        )
        self.assertIn("PERFORMA%20OPTIMA%20GROUP", build.badge("COMPANY", "PERFORMA OPTIMA GROUP", "2f6bff"))
        self.assertIn("REST--API", build.badge("", "REST-API", "0a0f24"))

    def test_sections_and_assets(self):
        for a in [
            "assets/hero.svg", "assets/h-01.svg", "assets/h-02.svg", "assets/h-03.svg", "assets/h-04.svg",
            "assets/h-05.svg", "assets/h-06.svg", "assets/skills.svg", "assets/proj-fruch.svg",
            "assets/proj-story.svg", "assets/proj-pos.svg", "assets/footer.svg",
            "readme-typing-svg.demolab.com", "github-readme-stats.vercel.app/api?username=RayNathans",
            "api/top-langs/?username=RayNathans", "streak-stats.demolab.com?user=RayNathans",
            "raw.githubusercontent.com/RayNathans/RayNathans/output/github-snake.svg",
            "komarev.com/ghpvc/?username=RayNathans",
        ]:
            self.assertTrue(a in self.md, f"hilang: {a}")

    def test_links(self):
        self.assertNotIn('href="#"', self.md)
        self.assertNotIn("](#)", self.md)
        for u in [
            "https://dicoding-milestone-fruch.vercel.app/", "https://nathdicodingstory.netlify.app/",
            "https://sipolubogo.cartera.my.id/", "https://www.linkedin.com/in/nikolaus-ray-nathan/",
            "https://nathporto.netlify.app/", "mailto:nikolausraynathan@gmail.com",
        ]:
            self.assertTrue(u in self.md, f"hilang: {u}")

    def test_certs(self):
        self.assertEqual(self.md.count("https://www.dicoding.com/certificates/"), 9)
        self.assertIn("Belajar Pengembangan Web Intermediate", self.md)
        certs_block = self.md.split("ACCESS CERTIFICATES")[1].split("</details>")[0]
        self.assertNotIn("React", certs_block)
        self.assertNotIn("Dasar AI", certs_block)

    def test_about_and_facts(self):
        self.assertIn('"sekarang": "Backend Dev @ Performa Optima Group"', self.md)
        self.assertIn('"kopi": true', self.md)
        self.assertIn("9 sertifikat Dicoding: Front-End, Back-End, Web Intermediate", self.md)
        self.assertIn("2025-08 → NOW · SURABAYA", self.md)

    def test_no_loc_uptime_no_coffee_no_fake_numbers(self):
        self.assertNotIn("UPTIME", self.md)
        self.assertNotIn("COFFEE", self.md.upper())
        self.assertNotIn("1,204", self.md)

    def test_images_have_alt(self):
        import re
        imgs = re.findall(r"<img[^>]*>", self.md)
        self.assertGreater(len(imgs), 10)
        for tag in imgs:
            self.assertIn("alt=", tag, tag[:80])

    def test_current_job_toggle_changes_five_places(self):
        d = dict(self.d, profile=dict(self.d["profile"], current_job=False))
        md = build.build_readme(d)
        self.assertIn("STATUS-OPEN%20TO%20WORK", md)
        self.assertIn("2025-08 → 2026-02 · SURABAYA", md)
        self.assertIn('"sekarang": "Open to work · Full Stack"', md)
        self.assertIn("(Ags 2025 – Feb 2026)", md)
        self.assertNotIn("COMPANY-PERFORMA%20OPTIMA%20GROUP", md)
        hero = build.build_hero(d)
        self.assertIn("[READY]", hero)
        self.assertNotIn("[RUNNING]", hero)


if __name__ == "__main__":
    unittest.main()
