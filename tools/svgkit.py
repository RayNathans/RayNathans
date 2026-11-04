"""Perkakas bersama untuk membangun aset SVG profil: palet, escape, embed font/avatar, render template."""
from __future__ import annotations

import base64
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "tools" / "templates"
FONTS = ROOT / "fonts"
DATA = ROOT / "data"
ASSETS = ROOT / "assets"

PALETTE: dict[str, str] = {
    "bg": "#03040d",
    "panel": "#0a0f24",
    "line": "#15214a",
    "ink": "#dbe7ff",
    "muted": "#7f93c4",
    "c1": "#00e5ff",
    "c2": "#2f6bff",
    "c3": "#ff2bd6",
    "c4": "#7c3aed",
    "ok": "#22c55e",
}

_FONT_FILES = (
    ("Orbitron", "Orbitron-subset.woff2", "400 900"),
    ("Share Tech Mono", "ShareTechMono-subset.woff2", "400"),
)

_PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")


def esc(s: str) -> str:
    """Escape teks untuk atribut/isi XML."""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def font_face_css() -> str:
    rules = []
    for family, fname, weight in _FONT_FILES:
        data = _b64(FONTS / fname)
        rules.append(
            f"@font-face{{font-family:'{family}';font-weight:{weight};font-style:normal;"
            f"src:url(data:font/woff2;base64,{data}) format('woff2')}}"
        )
    return "\n".join(rules)


def avatar_data_uri() -> str:
    return "data:image/jpeg;base64," + _b64(ASSETS / "avatar.jpg")


def base_style() -> str:
    colors = "".join(
        f".{k}{{fill:{v}}}.s-{k}{{stroke:{v}}}" for k, v in PALETTE.items()
    )
    return (
        font_face_css()
        + "\n"
        + colors
        + "\n.mono{font-family:'Share Tech Mono',monospace}"
        + ".orb{font-family:Orbitron,sans-serif;font-weight:900}"
        + "\n@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
    )


def render(template_name: str, **vars: str) -> str:
    """Isi {{key}} pada template; KeyError bila ada placeholder yang tidak diisi."""
    text = (TEMPLATES / template_name).read_text(encoding="utf-8")
    for k, v in vars.items():
        text = text.replace("{{" + k + "}}", str(v))
    left = _PLACEHOLDER.search(text)
    if left:
        raise KeyError(f"placeholder {left.group(0)} tidak diisi di {template_name}")
    return text


def load_data() -> dict:
    return {
        name: json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))
        for name in ("profile", "skills", "projects", "certs")
    }
