"""Bangun semua aset SVG dan README dari data/*.json.

    .venv/Scripts/python.exe tools/build.py
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import svgkit  # noqa: E402
from tools.svgkit import PALETTE, esc  # noqa: E402

_BULAN = {
    "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "Mei", "06": "Jun",
    "07": "Jul", "08": "Ags", "09": "Sep", "10": "Okt", "11": "Nov", "12": "Des",
}


def _bulan_id(ym: str) -> str:
    y, m = ym.split("-")
    return f"{_BULAN[m]} {y}"


def job_strings(profile: dict) -> dict:
    """Semua teks yang bergantung pada status pekerjaan, dari satu flag current_job."""
    job = profile["job"]
    company_up = job["company"].upper()
    if profile.get("current_job", True):
        return {
            "timeline_when": f"{job['start']} → NOW · {job['city']}",
            "strip_label": "COMPANY",
            "strip_value": company_up,
            "term_status": "status: building PWA for field technicians [RUNNING]",
            "about_now": f"Backend Dev @ {job['company']}",
            "fact01": f"{job['title']} di {job['company']} ({_bulan_id(job['start'])} – sekarang)",
        }
    return {
        "timeline_when": f"{job['start']} → {job['end']} · {job['city']}",
        "strip_label": "STATUS",
        "strip_value": "OPEN TO WORK",
        "term_status": "status: open for new missions [READY]",
        "about_now": "Open to work · Full Stack",
        "fact01": f"{job['title']} di {job['company']} ({_bulan_id(job['start'])} – {_bulan_id(job['end'])})",
    }


# ---------------------------------------------------------------- hero
_NEAR_BUILDINGS = [
    # x, y, w, h, gradient
    (20, 260, 110, 140, "bld"),
    (160, 220, 70, 180, "bld2"),
    (260, 280, 140, 120, "bld"),
    (430, 240, 60, 160, "bld2"),
    (520, 300, 120, 100, "bld"),
    (700, 290, 90, 110, "bld2"),
    (1000, 270, 90, 130, "bld2"),
    (1110, 230, 80, 170, "bld"),
]


def _hero_buildings() -> str:
    return "".join(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{g})"/>'
        for x, y, w, h, g in _NEAR_BUILDINGS
    )


def _hero_windows(rng: random.Random) -> str:
    out = []
    for x, y, w, h, _ in _NEAR_BUILDINGS:
        for wy in range(y + 14, y + h - 10, 24):
            for wx in range(x + 10, x + w - 12, 20):
                if rng.random() < 0.5:
                    continue
                col = PALETTE["c3"] if rng.random() < 0.15 else PALETTE["c1"]
                out.append(
                    f'<rect class="win" x="{wx}" y="{wy}" width="7" height="9" fill="{col}" '
                    f'style="animation-delay:-{rng.uniform(0, 2.6):.2f}s;animation-duration:{rng.uniform(2, 4.2):.2f}s"/>'
                )
    return "".join(out)


def _hero_rain(rng: random.Random, n: int = 40) -> str:
    out = []
    for _ in range(n):
        x = rng.randint(0, 1200)
        ln = rng.randint(14, 30)
        out.append(
            f'<line x1="{x}" y1="0" x2="{x - 2}" y2="{ln}" stroke-width="{rng.choice([1, 1, 1.5])}" '
            f'opacity="{rng.uniform(0.25, 0.5):.2f}" style="animation-delay:-{rng.uniform(0, 1.6):.2f}s;animation-duration:{rng.uniform(0.9, 1.6):.2f}s"/>'
        )
    return "\n".join(out)


def build_hero(data: dict) -> str:
    rng = random.Random(7)
    js = job_strings(data["profile"])
    return svgkit.render(
        "hero.svg",
        style=svgkit.base_style(),
        avatar=svgkit.avatar_data_uri(),
        term_status=esc(js["term_status"]),
        buildings=_hero_buildings(),
        windows=_hero_windows(rng),
        rain=_hero_rain(rng),
    )


# ---------------------------------------------------------------- output
def write(name: str, content: str, out: Path | None = None) -> Path:
    root = out or svgkit.ROOT
    path = root / "assets" / name if name.endswith(".svg") else root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return path


def main(out: Path | None = None) -> None:
    data = svgkit.load_data()
    write("hero.svg", build_hero(data), out)
    print("build selesai")


if __name__ == "__main__":
    main()
