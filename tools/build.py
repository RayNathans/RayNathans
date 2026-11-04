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


# ---------------------------------------------------------------- judul seksi & footer
SECTIONS: list[tuple[str, str]] = [
    ("01", "IDENTITY"),
    ("02", "SKILL MATRIX"),
    ("03", "MISSION LOGS"),
    ("04", "TELEMETRY"),
    ("05", "TIMELINE.LOG"),
    ("06", "ESTABLISH CONNECTION"),
]


def build_header(idx: str, title: str) -> str:
    return svgkit.render(
        "header.svg",
        style=svgkit.base_style(),
        idx=esc(idx),
        title=esc(title),
        title_x="104",
    )


def build_footer() -> str:
    return svgkit.render("footer.svg", style=svgkit.base_style())


# ---------------------------------------------------------------- skill matrix
_SK_ROW_H = 52
_SK_TOP = 40
_SK_COLS = (30, 610)  # x awal tiap kolom
_SK_SEG_W, _SK_SEG_GAP, _SK_SEGS = 16, 3, 20


def build_skills(skills: list[dict]) -> str:
    per_col = (len(skills) + 1) // 2
    height = _SK_TOP + per_col * _SK_ROW_H + 12
    rows = []
    for i, sk in enumerate(skills):
        col, row = divmod(i, per_col)
        x0 = _SK_COLS[col]
        y = _SK_TOP + row * _SK_ROW_H
        on = round(sk["pct"] / 5)
        bar_x = x0 + 120
        segs = []
        for s in range(_SK_SEGS):
            sx = bar_x + s * (_SK_SEG_W + _SK_SEG_GAP)
            if s < on:
                fill = PALETTE["c3"] if s >= 16 else PALETTE["c1"]
                segs.append(
                    f'<rect class="seg on" x="{sx}" y="{y + 14}" width="{_SK_SEG_W}" height="12" fill="{fill}" '
                    f'style="--d:{(i * 60 + s * 40) / 1000:.2f}s"/>'
                )
            else:
                segs.append(
                    f'<rect class="seg off" x="{sx}" y="{y + 14}" width="{_SK_SEG_W}" height="12" '
                    f'fill="{PALETTE["panel"]}" stroke="{PALETTE["line"]}"/>'
                )
        rows.append(
            f'<text x="{x0}" y="{y + 25}" class="mono" font-size="15" fill="{PALETTE["ink"]}">{esc(sk["name"])}</text>'
            + "".join(segs)
            + f'<text class="pct mono" x="{bar_x + _SK_SEGS * (_SK_SEG_W + _SK_SEG_GAP) + 8}" y="{y + 25}" '
            f'font-size="14" fill="{PALETTE["c1"]}" style="--d:{(i * 60 + on * 40) / 1000:.2f}s">{sk["pct"]}%</text>'
        )
    return svgkit.render(
        "skills.svg",
        style=svgkit.base_style(),
        height=str(height),
        names=esc(", ".join(s["name"] for s in skills)),
        rows="\n".join(rows),
    )


# ---------------------------------------------------------------- kartu proyek
def wrap_text(s: str, max_chars: int) -> list[str]:
    """Penggalan kata sederhana: tiap baris <= max_chars karakter."""
    lines: list[str] = []
    cur = ""
    for word in s.split():
        cand = f"{cur} {word}".strip()
        if cur and len(cand) > max_chars:
            lines.append(cur)
            cur = word
        else:
            cur = cand
    if cur:
        lines.append(cur)
    return lines


def _chips(stack: list[str], y: int) -> str:
    out = []
    x = 16
    for t in stack:
        w = 7 * len(t) + 14
        out.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="18" fill="none" stroke="{PALETTE["c2"]}" rx="2"/>'
            f'<text x="{x + w / 2:.0f}" y="{y + 13}" text-anchor="middle" class="mono" font-size="10" fill="{PALETTE["ink"]}">{esc(t)}</text>'
        )
        x += w + 6
    return "".join(out)


def build_project(p: dict) -> str:
    art = (svgkit.TEMPLATES / p["art"]).read_text(encoding="utf-8")
    desc_lines = wrap_text(p["desc"], 46)[:3]
    desc = "".join(
        f'<text x="16" y="{200 + i * 17}" class="mono" font-size="12" fill="{PALETTE["muted"]}">{esc(line)}</text>'
        for i, line in enumerate(desc_lines)
    )
    st_color = PALETTE["ok"] if p["status"] == "DEPLOYED" else PALETTE["c3"]
    st_w = 7 * len(p["status"]) + 18
    st_x = 400 - 12 - st_w
    return svgkit.render(
        "project.svg",
        style=svgkit.base_style(),
        art=art,
        title=esc(p["title"]),
        desc_plain=esc(p["desc"]),
        desc=desc,
        chips=_chips(p["stack"], 250),
        status=esc(p["status"]),
        st_color=st_color,
        st_w=str(st_w),
        st_x=str(st_x),
        st_tx=f"{st_x + st_w / 2:.0f}",
        id_label=esc(f"MISSION // {p['id'].upper()}"),
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
    for idx, title in SECTIONS:
        write(f"h-{idx}.svg", build_header(idx, title), out)
    write("footer.svg", build_footer(), out)
    write("skills.svg", build_skills(data["skills"]), out)
    for p in data["projects"]:
        write(f"proj-{p['id']}.svg", build_project(p), out)
    print("build selesai")


if __name__ == "__main__":
    main()
