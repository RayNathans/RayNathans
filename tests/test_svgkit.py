import glob
import io
import os
import sys
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

    def test_base_style_has_reduced_motion(self):
        css = svgkit.base_style()
        self.assertIn("prefers-reduced-motion", css)
        self.assertIn(".c1{fill:#00e5ff}", css)

    def test_render_rejects_missing_var(self):
        probe = svgkit.TEMPLATES / "_probe.svg"
        probe.write_text("<svg>{{a}} {{b}}</svg>", encoding="utf-8")
        try:
            with self.assertRaises(KeyError):
                svgkit.render("_probe.svg", a="1")
            self.assertEqual(svgkit.render("_probe.svg", a="1", b="2"), "<svg>1 2</svg>")
        finally:
            probe.unlink()

    def test_subset_covers_template_glyphs(self):
        from fontTools.ttLib import TTFont

        cmap = set()
        for f in ("Orbitron-subset.woff2", "ShareTechMono-subset.woff2"):
            cmap |= set(TTFont(ROOT / "fonts" / f).getBestCmap())
        missing = set()
        for path in glob.glob(str(svgkit.TEMPLATES / "*.svg")):
            text = Path(path).read_text(encoding="utf-8")
            missing |= {ch for ch in text if ord(ch) > 0x7E and ord(ch) not in cmap}
        self.assertEqual(missing, set(), f"glyph tanpa font: {sorted(missing)}")

    def test_load_data_keys(self):
        d = svgkit.load_data()
        self.assertEqual(set(d), {"profile", "skills", "projects", "certs"})
        self.assertEqual(len(d["skills"]), 12)
        self.assertEqual(len(d["certs"]), 9)
        self.assertEqual(len(d["projects"]), 3)
        self.assertTrue(d["profile"]["current_job"])


if __name__ == "__main__":
    unittest.main()
