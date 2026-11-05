import copy
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests import fixtures  # noqa: E402
from tools import build, svgkit  # noqa: E402

load_data = svgkit.load_data
SVG_NS = "{http://www.w3.org/2000/svg}"


def no_external(svg: str) -> bool:
    return "http" not in svg.replace("http://www.w3.org", "")


def glyph_violations(svg: str, cmaps: dict) -> set:
    """Karakter non-ASCII pada <text>/<tspan> yang tidak ada di font kelasnya.

    Font ditentukan dari class: 'orb' → Orbitron, selain itu → Share Tech Mono.
    Elemen anak mewarisi class induknya bila tidak punya sendiri."""
    bad = set()

    def walk(el, family):
        cls = el.get("class", "")
        if "orb" in cls.split():
            family = "Orbitron"
        elif "mono" in cls.split():
            family = "Share Tech Mono"
        if el.tag in (SVG_NS + "text", SVG_NS + "tspan", SVG_NS + "g"):
            for chunk in (el.text or "",) + tuple(c.tail or "" for c in el):
                for ch in chunk:
                    if ord(ch) > 0x7E and not ch.isspace() and ord(ch) not in cmaps[family]:
                        bad.add((family, ch))
        for c in el:
            walk(c, family)

    walk(ET.fromstring(svg), "Share Tech Mono")
    return bad


class HeroTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.svg = build.build_hero(fixtures.data(True))

    def test_is_xml_and_no_external(self):
        ET.fromstring(self.svg)
        self.assertTrue(no_external(self.svg))

    def test_texts(self):
        for s in [
            "SYS.ONLINE", "NIKOLAUS", "RAY NATHAN", "FULL STACK DEVELOPER",
            "LARAVEL", "NEXT.JS", "SBY-07 // SECTOR 2026", "ID: RAY_NATHANS",
            "[OK]", "building PWA for field technicians [RUNNING]",
            "loading stack: laravel, next.js, typescript, postgresql",
        ]:
            self.assertTrue(s in self.svg, f"teks hilang: {s}")

    def test_name_comes_from_profile(self):
        d = fixtures.data(True)
        d["profile"]["name"] = "Budi Santoso Wijaya"
        svg = build.build_hero(d)
        self.assertIn(">BUDI<", svg)
        self.assertIn(">SANTOSO WIJAYA<", svg)
        self.assertIn('aria-label="Budi Santoso Wijaya', svg)
        self.assertNotIn("NIKOLAUS", svg)

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
        off = build.job_strings(fixtures.data(False)["profile"])
        self.assertEqual(off["strip_value"], "OPEN TO WORK")
        self.assertEqual(off["strip_label"], "STATUS")
        self.assertEqual(off["timeline_when"], "2025-08 – 2026-02 · SURABAYA")
        self.assertIn("[READY]", off["term_status"])
        self.assertEqual(off["about_now"], "Open to work · Full Stack")
        self.assertEqual(off["fact01"], "Backend Developer di Performa Optima Group (Ags 2025 – Feb 2026)")
        self.assertEqual(off["role_badge"], "FULL_STACK_DEV")
        self.assertTrue(off["fact02"].startswith("Pernah membangun"))
        on = build.job_strings(fixtures.data(True)["profile"])
        self.assertEqual(on["timeline_when"], "2025-08 – NOW · SURABAYA")
        self.assertEqual(on["strip_value"], "PERFORMA OPTIMA GROUP")
        self.assertEqual(on["about_now"], "Backend Dev @ Performa Optima Group")
        self.assertEqual(on["role_badge"], "BACKEND_DEV")
        self.assertTrue(on["fact02"].startswith("Membangun"))

    def test_hero_term_status_toggle(self):
        hero = build.build_hero(fixtures.data(False))
        self.assertIn("[READY]", hero)
        self.assertNotIn("[RUNNING]", hero)


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
        skills = [
            {"name": "PHP", "pct": 98, "badge": {"logo": "php", "color": "777BB4", "url": "https://www.php.net/"}},
            {"name": "Supabase", "pct": 75, "badge": {"logo": "supabase", "color": "3FCF8E", "url": "https://supabase.com/"}},
            {"name": "Python", "pct": 70, "badge": {"logo": "python", "color": "3776AB", "url": "https://www.python.org/"}},
        ]
        s = build.build_skills(skills)
        ET.fromstring(s)
        on = sum(round(x["pct"] / 5) for x in skills)
        self.assertEqual(s.count('class="seg on"'), on)
        self.assertEqual(s.count('class="seg off"'), 20 * len(skills) - on)
        for name in ("PHP", "98%", "Supabase", "75%", "SELF-ASSESSMENT"):
            self.assertTrue(name in s, f"teks hilang: {name}")
        self.assertTrue(no_external(s))


class ProjectTests(unittest.TestCase):
    def test_three_cards(self):
        for p in fixtures.data()["projects"]:
            s = build.build_project(p)
            ET.fromstring(s)
            self.assertTrue(p["title"] in s, p["title"])
            self.assertTrue(p["status"] in s, p["status"])
            for t in p["stack"]:
                self.assertTrue(t in s, t)
            self.assertIn("LIVE DEMO", s)
            self.assertTrue(no_external(s), p["id"])

    def test_xml_specials_in_data(self):
        p = dict(fixtures.data()["projects"][0], title='Tom & "Jerry" <Co>', desc="A & B < C", stack=['C++ & "Go"'])
        s = build.build_project(p)
        ET.fromstring(s)
        self.assertIn("Tom &amp; &quot;Jerry&quot; &lt;Co&gt;", s)

    def test_wrap(self):
        self.assertEqual(
            build.wrap_text("Deteksi kematangan & manfaat buah berbasis AI. Antarmuka minimalis dan aksesibel.", 46),
            ["Deteksi kematangan & manfaat buah berbasis AI.", "Antarmuka minimalis dan aksesibel."],
        )
        self.assertEqual(build.wrap_text("satu dua tiga", 7), ["satu", "dua", "tiga"])


class StripTests(unittest.TestCase):
    def test_cells(self):
        s = build.build_strip(fixtures.data(True))
        ET.fromstring(s)
        for t in ("ROLE", "BACKEND_DEV", "COMPANY", "PERFORMA OPTIMA GROUP", "CERTS", "09 · DICODING", "FOLLOWERS", ">7<"):
            self.assertTrue(t in s, f"teks hilang: {t}")
        self.assertTrue(no_external(s))

    def test_toggle(self):
        s = build.build_strip(fixtures.data(False))
        self.assertIn("STATUS", s)
        self.assertIn("OPEN TO WORK", s)
        self.assertIn("FULL_STACK_DEV", s)
        self.assertNotIn("PERFORMA", s)


class IdentityTests(unittest.TestCase):
    def test_about_and_facts(self):
        s = build.build_identity(fixtures.data(True))
        ET.fromstring(s)
        for t in ('"nama"', "Nikolaus Ray Nathan", '"sekarang"', "Backend Dev @ Performa Optima Group",
                  '"stack"', "PostgreSQL", '"kopi"', "// selalu", "[01]", "[05]",
                  "Backend Developer di Performa Optima", "(Ags 2025 – sekarang)",
                  "9 sertifikat Dicoding", "about.json"):
            self.assertTrue(t in s, f"teks hilang: {t}")
        self.assertTrue(no_external(s))

    def test_toggle_and_escape(self):
        d = fixtures.data(False)
        d["profile"]["learning"] = 'PWA & "arsitektur" <backend>'
        s = build.build_identity(d)
        ET.fromstring(s)
        self.assertIn("Open to work · Full Stack", s)
        self.assertIn("Pernah membangun", s)
        self.assertIn("PWA &amp; &quot;arsitektur&quot; &lt;backend&gt;", s)


class TelemetryTests(unittest.TestCase):
    def test_numbers_from_stats(self):
        d = fixtures.data(True)
        s = build.build_telemetry(d)
        ET.fromstring(s)
        for t in ("GITHUB STATS", "STREAK", "TOP LANGUAGES", ">64<", ">67<", ">7<", ">5<", ">9<",
                  "TypeScript", "49%", "Blade", "CSS", "2026-11-04 10:00 UTC", "2025-11-02 – 2026-11-04"):
            self.assertTrue(t in s, f"teks hilang: {t}")
        self.assertTrue(no_external(s))
        self.assertNotIn("1,204", s)

    def test_language_bar_widths_sum(self):
        d = fixtures.data(True)
        s = build.build_telemetry(d)
        widths = [float(w) for w in re.findall(r'class="lang-seg"[^>]*width="([\d.]+)"', s)]
        self.assertEqual(len(widths), 5)
        self.assertAlmostEqual(sum(widths), build._LANG_BAR_W, delta=0.5)


class TimelineTests(unittest.TestCase):
    def test_entries(self):
        d = fixtures.data(True)
        s = build.build_timeline(d)
        ET.fromstring(s)
        for t in ("2025-08 – NOW · SURABAYA", "Backend Developer · Performa Optima Group",
                  "Litera Sumbu Pakarti", "Dicoding Indonesia", "Menyelesaikan 9 kelas"):
            self.assertTrue(t in s, f"teks hilang: {t}")
        self.assertNotIn("→", s)
        self.assertNotIn("{n_certs}", s)
        self.assertTrue(no_external(s))

    def test_toggle(self):
        s = build.build_timeline(fixtures.data(False))
        self.assertIn("2025-08 – 2026-02 · SURABAYA", s)
        self.assertNotIn("NOW", s)


class ConnectTests(unittest.TestCase):
    def test_files(self):
        files = build.build_connect(fixtures.data(True))
        self.assertEqual(set(files), {"connect.svg", "btn-linkedin.svg", "btn-portfolio.svg", "btn-email.svg"})
        for name, s in files.items():
            ET.fromstring(s)
            self.assertTrue(no_external(s), name)
        self.assertIn("Terbuka untuk kolaborasi", files["connect.svg"])
        self.assertIn("LINKEDIN", files["btn-linkedin.svg"])
        self.assertIn("PORTFOLIO", files["btn-portfolio.svg"])
        self.assertIn("EMAIL", files["btn-email.svg"])
        self.assertIn("nikolausraynathan@gmail.com", files["btn-email.svg"])


class GlyphTests(unittest.TestCase):
    """Fokus review #1: setiap karakter non-ASCII di SVG hasil build harus ada di font kelasnya."""

    @classmethod
    def setUpClass(cls):
        from fontTools.ttLib import TTFont

        cls.cmaps = {
            "Orbitron": set(TTFont(ROOT / "fonts" / "Orbitron-subset.woff2").getBestCmap()),
            "Share Tech Mono": set(TTFont(ROOT / "fonts" / "ShareTechMono-subset.woff2").getBestCmap()),
        }

    def test_checker_detects_missing_glyph(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg"><text class="orb">A · B</text><text class="mono">C → D</text></svg>'
        self.assertEqual(glyph_violations(svg, self.cmaps), {("Orbitron", "·"), ("Share Tech Mono", "→")})

    def test_all_built_svgs(self):
        d = fixtures.data(True)
        svgs = [build.build_hero(d), build.build_footer(), build.build_skills(d["skills"])]
        svgs += [build.build_header(i, t) for i, t in build.SECTIONS]
        svgs += [build.build_project(p) for p in d["projects"]]
        svgs += [build.build_strip(d), build.build_identity(d), build.build_telemetry(d), build.build_timeline(d)]
        svgs += list(build.build_connect(d).values())
        off = fixtures.data(False)
        svgs += [build.build_hero(off), build.build_strip(off), build.build_identity(off), build.build_timeline(off)]
        for svg in svgs:
            self.assertEqual(glyph_violations(svg, self.cmaps), set())

    def test_build_fails_on_unsupported_glyph_in_data(self):
        d = fixtures.data(True)
        d["projects"][0]["title"] = "FRUCH → AI"
        with self.assertRaises(ValueError):
            build.build_project(d["projects"][0])


class ReadmeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = fixtures.data(True)
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
            "assets/hero.svg", "assets/strip.svg", "assets/h-01.svg", "assets/identity.svg", "assets/h-02.svg",
            "assets/skills.svg", "assets/h-03.svg", "assets/proj-fruch.svg", "assets/proj-story.svg",
            "assets/proj-pos.svg", "assets/h-04.svg", "assets/telemetry.svg", "assets/h-05.svg",
            "assets/timeline.svg", "assets/h-06.svg", "assets/connect.svg", "assets/btn-linkedin.svg",
            "assets/btn-portfolio.svg", "assets/btn-email.svg", "assets/footer.svg",
            "readme-typing-svg.demolab.com",
            "raw.githubusercontent.com/RayNathans/RayNathans/output/github-snake.svg",
        ]:
            self.assertTrue(a in self.md, f"hilang: {a}")
        # urutan seksi mengikuti mockup
        pos = [self.md.index(a) for a in ("assets/hero.svg", "assets/strip.svg", "assets/identity.svg",
                                           "assets/skills.svg", "assets/proj-fruch.svg", "assets/telemetry.svg",
                                           "assets/timeline.svg", "assets/connect.svg", "assets/footer.svg")]
        self.assertEqual(pos, sorted(pos))

    def test_no_third_party_cards(self):
        for s in ("github-readme-stats", "streak-stats", "komarev", "img.shields.io/badge/ROLE",
                  "img.shields.io/badge/COMPANY", "img.shields.io/badge/STATUS", "img.shields.io/badge/CERTS",
                  "img.shields.io/badge/LINKEDIN", "```"):
            self.assertFalse(s in self.md, f"masih ada: {s}")

    def test_buttons_wrapped_in_links(self):
        for btn, href in (("btn-linkedin", "https://www.linkedin.com/in/nikolaus-ray-nathan/"),
                          ("btn-portfolio", "https://nathporto.netlify.app/"),
                          ("btn-email", "mailto:nikolausraynathan@gmail.com")):
            m = re.search(rf'<a href="([^"]+)"><img src="assets/{btn}\.svg"', self.md)
            self.assertIsNotNone(m, btn)
            self.assertEqual(m.group(1), href)

    def test_links(self):
        self.assertNotIn('href="#"', self.md)
        self.assertNotIn("](#)", self.md)
        for u in [
            "https://dicoding-milestone-fruch.vercel.app/", "https://nathdicodingstory.netlify.app/",
            "https://sipolubogo.cartera.my.id/", "https://www.linkedin.com/in/nikolaus-ray-nathan/",
            "https://nathporto.netlify.app/", "mailto:nikolausraynathan@gmail.com",
        ]:
            self.assertTrue(u in self.md, f"hilang: {u}")

    def test_certs_count_follows_data(self):
        self.assertEqual(self.md.count("https://www.dicoding.com/certificates/"), 9)
        self.assertTrue("Belajar Pengembangan Web Intermediate" in self.md)
        self.assertTrue("ACCESS CERTIFICATES [09]" in self.md)
        self.assertTrue("9 sertifikat Dicoding" in self.md)
        d = copy.deepcopy(self.d)
        d["certs"].append({"id": "ZZZZ", "title": "Kelas Baru", "date": "2026-01-01"})
        md = build.build_readme(d)
        self.assertTrue("ACCESS CERTIFICATES [10]" in md)
        self.assertTrue("10 sertifikat Dicoding" in md)
        self.assertEqual(md.count("https://www.dicoding.com/certificates/"), 10)
        self.assertTrue("10 · DICODING" in build.build_strip(d))

    def test_alt_texts_carry_content(self):
        for s in ("Backend Dev @ Performa Optima Group", "(Ags 2025 – sekarang)", "2025-08 – NOW · SURABAYA",
                  "role BACKEND_DEV", "COMPANY PERFORMA OPTIMA GROUP"):
            self.assertTrue(s in self.md, f"hilang: {s}")

    def test_no_loc_uptime_no_coffee_no_fake_numbers(self):
        self.assertNotIn("UPTIME", self.md)
        self.assertNotIn("COFFEE", self.md.upper())
        self.assertNotIn("1,204", self.md)

    def test_images_have_alt(self):
        imgs = re.findall(r"<img[^>]*>", self.md)
        self.assertGreater(len(imgs), 10)
        for tag in imgs:
            self.assertIn("alt=", tag, tag[:80])

    def test_current_job_toggle_changes_all_places(self):
        md = build.build_readme(fixtures.data(False))
        for s in ("STATUS OPEN TO WORK", "2025-08 – 2026-02 · SURABAYA", "Open to work · Full Stack",
                  "(Ags 2025 – Feb 2026)", "role FULL_STACK_DEV", "Pernah membangun"):
            self.assertTrue(s in md, f"hilang: {s}")
        for s in ("PERFORMA OPTIMA GROUP", "BACKEND_DEV", "NOW"):
            self.assertFalse(s in md, f"masih ada: {s}")


if __name__ == "__main__":
    unittest.main()
