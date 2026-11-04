"""Unduh font OFL dari repo resmi Google Fonts lalu buat subset woff2.

Dijalankan sekali (atau saat ingin memperbarui font):
    .venv/Scripts/python.exe tools/fetch_fonts.py
"""
from __future__ import annotations

import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / "scratch" / "fonts"
FONTS = ROOT / "fonts"
BASE = "https://raw.githubusercontent.com/google/fonts/main/ofl/"

SOURCES = {
    "Orbitron": ("orbitron/Orbitron%5Bwght%5D.ttf", "orbitron/OFL.txt"),
    "ShareTechMono": ("sharetechmono/ShareTechMono-Regular.ttf", "sharetechmono/OFL.txt"),
}

# ASCII + karakter non-ASCII yang dipakai template: · – → ✔ ▸ ● •
UNICODES = "U+0020-007E,U+00B7,U+2013,U+2192,U+2714,U+25B8,U+25CF,U+2022"


def fetch(rel: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(BASE + rel, timeout=60) as r:
        dest.write_bytes(r.read())
    print(f"unduh {rel} -> {dest} ({dest.stat().st_size} B)")


def subset(src: Path, dest: Path) -> None:
    cmd = [
        sys.executable, "-m", "fontTools.subset", str(src),
        f"--unicodes={UNICODES}", "--flavor=woff2", "--layout-features=*",
        f"--output-file={dest}", "--no-hinting",
    ]
    subprocess.run(cmd, check=True)
    print(f"subset {dest} ({dest.stat().st_size} B)")


def main() -> None:
    FONTS.mkdir(exist_ok=True)
    for name, (ttf_rel, ofl_rel) in SOURCES.items():
        ttf = SCRATCH / Path(ttf_rel).name.replace("%5B", "[").replace("%5D", "]")
        if not ttf.exists():
            fetch(ttf_rel, ttf)
        fetch(ofl_rel, FONTS / f"OFL-{name}.txt")
        subset(ttf, FONTS / f"{name}-subset.woff2")


if __name__ == "__main__":
    main()
