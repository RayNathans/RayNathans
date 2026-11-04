import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import svgkit  # noqa: E402


class SvgkitTests(unittest.TestCase):
    def test_palette_values(self):
        self.assertEqual(svgkit.PALETTE["c1"], "#00e5ff")
        self.assertEqual(svgkit.PALETTE["bg"], "#03040d")
        self.assertEqual(
            set(svgkit.PALETTE),
            {"bg", "panel", "line", "ink", "muted", "c1", "c2", "c3", "c4", "ok"},
        )

    def test_esc(self):
        self.assertEqual(
            svgkit.esc('PWA & <b> "x"'), "PWA &amp; &lt;b&gt; &quot;x&quot;"
        )

    def test_font_face_has_two_data_uris(self):
        css = svgkit.font_face_css()
        self.assertEqual(css.count("data:font/woff2;base64,"), 2)
        self.assertIn("Orbitron", css)
        self.assertIn("Share Tech Mono", css)

    def test_avatar_uri(self):
        self.assertTrue(svgkit.avatar_data_uri().startswith("data:image/jpeg;base64,"))

    def test_base_style_reduced_motion_keeps_content_visible(self):
        css = svgkit.base_style()
        self.assertIn(".c1{fill:#00e5ff}", css)
        block = css.split("@media (prefers-reduced-motion: reduce)")[1]
        self.assertIn("animation:none!important", block)
        # elemen yang awalnya tersembunyi harus dipaksa tampil saat animasi dimatikan
        self.assertIn("opacity:1!important", block)
        self.assertIn("clip-path:none!important", block)
        for cls in (".seg.on", ".pct", ".out1", ".out2", ".typed"):
            self.assertIn(cls, block, cls)

    def test_render_rejects_missing_var(self):
        orig = svgkit.TEMPLATES
        with tempfile.TemporaryDirectory() as tmp:
            svgkit.TEMPLATES = Path(tmp)
            (Path(tmp) / "_probe.svg").write_text("<svg>{{a}} {{b}}</svg>", encoding="utf-8")
            try:
                with self.assertRaises(KeyError):
                    svgkit.render("_probe.svg", a="1")
                self.assertEqual(svgkit.render("_probe.svg", a="1", b="2"), "<svg>1 2</svg>")
            finally:
                svgkit.TEMPLATES = orig

    def test_glyph_check(self):
        self.assertEqual(svgkit.unsupported_glyphs("A · B", "Share Tech Mono"), set())
        self.assertEqual(svgkit.unsupported_glyphs("A · B", "Orbitron"), {"·"})
        self.assertEqual(svgkit.unsupported_glyphs("A → B", "Share Tech Mono"), {"→"})

    def test_load_data_structure(self):
        d = svgkit.load_data()
        self.assertEqual(set(d), {"profile", "skills", "projects", "certs"})
        self.assertIsInstance(d["profile"]["current_job"], bool)
        for k in ("name", "handle", "role", "job", "stack", "links", "city", "learning", "motto"):
            self.assertIn(k, d["profile"])
        self.assertGreaterEqual(len(d["skills"]), 1)
        for s in d["skills"]:
            self.assertTrue(0 <= s["pct"] <= 100, s)
            self.assertTrue({"logo", "color", "url"} <= set(s["badge"]), s)
        for p in d["projects"]:
            self.assertTrue({"id", "title", "status", "desc", "stack", "live", "art"} <= set(p), p)
            self.assertTrue((svgkit.TEMPLATES / p["art"]).exists(), p["art"])
        for c in d["certs"]:
            self.assertTrue({"id", "title", "date"} <= set(c), c)


if __name__ == "__main__":
    unittest.main()
