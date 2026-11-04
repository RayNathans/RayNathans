"""Bangun semua aset SVG dan README dari data/*.json.

    .venv/Scripts/python.exe tools/build.py
"""
from __future__ import annotations

import random
import sys
from html import escape as html_escape
from pathlib import Path
from urllib.parse import quote, quote_plus

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
            "timeline_when": f"{job['start']} – NOW · {job['city']}",
            "strip_label": "COMPANY",
            "strip_value": company_up,
            "term_status": "status: building PWA for field technicians [RUNNING]",
            "about_now": f"Backend Dev @ {job['company']}",
            "fact01": f"{job['title']} di {job['company']} ({_bulan_id(job['start'])} – sekarang)",
            "fact02": "Membangun aplikasi PWA untuk otomasi laporan teknisi",
            "role_badge": "BACKEND_DEV",
        }
    return {
        "timeline_when": f"{job['start']} – {job['end']} · {job['city']}",
        "strip_label": "STATUS",
        "strip_value": "OPEN TO WORK",
        "term_status": "status: open for new missions [READY]",
        "about_now": "Open to work · Full Stack",
        "fact01": f"{job['title']} di {job['company']} ({_bulan_id(job['start'])} – {_bulan_id(job['end'])})",
        "fact02": "Pernah membangun aplikasi PWA untuk otomasi laporan teknisi",
        "role_badge": "FULL_STACK_DEV",
    }


def orb_text(s: str) -> str:
    """Teks untuk elemen ber-class orb: Orbitron tidak punya '·', jadi pemisah itu
    dipindah ke tspan mono. Hasil sudah di-escape."""
    parts = esc(s).split("·")
    sep = f'<tspan class="mono" fill="{PALETTE["muted"]}">·</tspan>'
    return sep.join(parts)


def _finish(svg: str) -> str:
    """Validasi akhir setiap SVG: semua glyph harus ada di font yang di-embed."""
    svgkit.check_glyphs(svg)
    return svg


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
    p = data["profile"]
    js = job_strings(p)
    first, _, rest = p["name"].upper().partition(" ")
    return _finish(svgkit.render(
        "hero.svg",
        style=svgkit.base_style(),
        avatar=svgkit.avatar_data_uri(),
        name_first=esc(first),
        name_rest=esc(rest or first),
        name_full=esc(p["name"]),
        role_full=esc(p["role"]),
        stack_lower=esc(", ".join(s.lower() for s in p["stack"])),
        term_status=esc(js["term_status"]),
        buildings=_hero_buildings(),
        windows=_hero_windows(rng),
        rain=_hero_rain(rng),
    ))


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
    return _finish(svgkit.render(
        "header.svg",
        style=svgkit.base_style(),
        idx=esc(idx),
        title=esc(title),
        title_x="104",
    ))


def build_footer() -> str:
    return _finish(svgkit.render("footer.svg", style=svgkit.base_style()))


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
    return _finish(svgkit.render(
        "skills.svg",
        style=svgkit.base_style(),
        height=str(height),
        names=esc(", ".join(s["name"] for s in skills)),
        rows="\n".join(rows),
    ))


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
    return _finish(svgkit.render(
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
    ))


# ---------------------------------------------------------------- status strip
def build_strip(data: dict) -> str:
    js = job_strings(data["profile"])
    n_certs = len(data["certs"])
    followers = data.get("stats", {}).get("followers", 0)
    cells = [
        ("ROLE", js["role_badge"], PALETTE["c1"]),
        (js["strip_label"], js["strip_value"], PALETTE["ink"]),
        ("CERTS", f"{n_certs:02d} · DICODING", PALETTE["c3"]),
        ("FOLLOWERS", str(followers), PALETTE["ink"]),
    ]
    out = []
    for i, (label, value, color) in enumerate(cells):
        x = i * 300
        if i:
            out.append(f'<line x1="{x}" y1="14" x2="{x}" y2="62" stroke="{PALETTE["line"]}"/>')
        out.append(
            f'<circle class="dot" cx="{x + 24}" cy="30" r="3" fill="{PALETTE["c1"]}" style="animation-delay:-{i * 0.45:.2f}s"/>'
            f'<text x="{x + 36}" y="34" class="mono" font-size="11" fill="{PALETTE["muted"]}" letter-spacing="2">{esc(label)}</text>'
            f'<text class="val orb" x="{x + 36}" y="56" font-size="15" fill="{color}" letter-spacing="1" '
            f'style="animation-delay:{i * 0.15:.2f}s">{orb_text(value)}</text>'
        )
    aria = " · ".join(f"{l}: {v}" for l, v, _ in cells)
    return _finish(svgkit.render("strip.svg", style=svgkit.base_style(), cells="\n".join(out), aria=esc(aria)))


# ---------------------------------------------------------------- identity
_ID_LINE_H = 24


def _json_line(indent: int, key: str | None, value: str, kind: str, comma: bool, i: int) -> str:
    """Satu baris about.json berwarna: key cyan, string ink, keyword magenta, komentar redup."""
    y = 60 + i * _ID_LINE_H
    parts = [f'<text class="ln" x="{20 + indent * 18}" y="{y}" style="animation-delay:{0.12 * i:.2f}s">']
    if key is not None:
        parts.append(f'<tspan fill="{PALETTE["c1"]}">"{esc(key)}"</tspan><tspan fill="{PALETTE["muted"]}">: </tspan>')
    color = {"str": PALETTE["ink"], "kw": PALETTE["c3"], "arr": PALETTE["ink"], "brace": PALETTE["muted"]}[kind]
    parts.append(f'<tspan fill="{color}">{value}</tspan>')
    if comma:
        parts.append(f'<tspan fill="{PALETTE["muted"]}">,</tspan>')
    parts.append("</text>")
    return "".join(parts)


def build_identity(data: dict) -> str:
    p = data["profile"]
    js = job_strings(p)
    n_certs = len(data["certs"])
    stack = ", ".join(f'<tspan fill="{PALETTE["ink"]}">"{esc(s)}"</tspan>' for s in p["stack"])
    rows = [
        (0, None, "{", "brace", False),
        (1, "nama", f'"{esc(p["name"])}"', "str", True),
        (1, "peran", f'"{esc(p["role"])}"', "str", True),
        (1, "sekarang", f'"{esc(js["about_now"])}"', "str", True),
        (1, "basis", f'"{esc(p["city"])}"', "str", True),
        (1, "stack", f"[{stack}]", "arr", True),
        (1, "sedang_belajar", f'"{esc(p["learning"])}"', "str", True),
        (1, "motto", f'"{esc(p["motto"])}"', "str", True),
        (1, "kopi", f'true<tspan fill="{PALETTE["muted"]}">  // selalu</tspan>', "kw", False),
        (0, None, '}<tspan class="cur" fill="#00e5ff">_</tspan>', "brace", False),
    ]
    lines = "\n".join(_json_line(ind, k, v, kind, comma, i) for i, (ind, k, v, kind, comma) in enumerate(rows))
    facts = [
        js["fact01"],
        js["fact02"],
        "Memimpin tim 3 developer di Litera Sumbu Pakarti",
        f"{n_certs} sertifikat Dicoding: Front-End, Back-End, Web Intermediate",
        "Sedang mendalami PostgreSQL & Python",
    ]
    fact_svg = []
    y = 62
    for i, f in enumerate(facts):
        fact_svg.append(f'<g class="fact" style="animation-delay:{0.25 + i * 0.18:.2f}s">')
        fact_svg.append(f'<text x="756" y="{y}" class="mono" font-size="12" fill="{PALETTE["c3"]}">[{i + 1:02d}]</text>')
        for j, line in enumerate(wrap_text(f, 44)[:2]):
            fact_svg.append(f'<text x="800" y="{y + j * 18}" class="mono" font-size="13" fill="{PALETTE["ink"]}">{esc(line)}</text>')
        fact_svg.append(f'<line class="pulse-line" x1="756" y1="{y + 26}" x2="1180" y2="{y + 26}" stroke="{PALETTE["line"]}"/></g>')
        y += 50
    panel_h = max(60 + len(rows) * _ID_LINE_H + 8, y - 10)
    height = panel_h + 1
    return _finish(svgkit.render(
        "identity.svg",
        style=svgkit.base_style(),
        name=esc(p["name"]),
        height=str(height),
        panel_h=str(panel_h),
        corner_y=str(panel_h - 11),
        lines=lines,
        facts="\n".join(fact_svg),
    ))


# ---------------------------------------------------------------- telemetry
_LANG_BAR_W = 352


def build_telemetry(data: dict) -> str:
    st = data["stats"]
    sk = st["streak"]
    stat_rows = [
        ("COMMITS (PUBLIC)", st["commits"]),
        ("CONTRIBUTIONS · 12 BLN", st["contrib_year"]),
        ("REPOSITORIES", st["public_repos"]),
        ("STARS", st["stars"]),
        ("PULL REQUESTS", st["prs"]),
        ("FOLLOWERS", st["followers"]),
    ]
    rows_svg = []
    for i, (label, val) in enumerate(stat_rows):
        y = 66 + i * 38
        rows_svg.append(
            f'<g class="row" style="animation-delay:{0.1 * i:.2f}s">'
            f'<text x="18" y="{y}" class="mono" font-size="11" fill="{PALETTE["muted"]}" letter-spacing="1">{esc(label)}</text>'
            f'<text x="250" y="{y + 1}" text-anchor="end" class="orb" font-size="18" fill="{PALETTE["c1"] if i % 2 == 0 else PALETTE["ink"]}">{val}</text>'
            f'<line x1="18" y1="{y + 12}" x2="250" y2="{y + 12}" stroke="{PALETTE["line"]}"/></g>'
        )
    ring_len = 2 * 3.14159 * 42
    years = max(1, dt_years(st.get("since", "")))
    ring_off = ring_len * (1 - min(1.0, years / 5))
    ring2_len = 2 * 3.14159 * 54
    frac = (sk["current"] / sk["longest"]) if sk.get("longest") else 0
    ring2_off = ring2_len * (1 - min(1.0, max(frac, 0.03)))
    x = 830
    bar, legend = [], []
    for i, lang in enumerate(st["languages"][:6]):
        w = _LANG_BAR_W * lang["pct"] / 100
        bar.append(f'<rect class="lang-seg" x="{x:.2f}" y="52" width="{w:.2f}" height="10" fill="{lang["color"]}" style="animation-delay:{0.15 * i:.2f}s"/>')
        x += w
        ly = 92 + i * 30
        legend.append(
            f'<g class="row" style="animation-delay:{0.2 + 0.1 * i:.2f}s">'
            f'<rect x="830" y="{ly - 9}" width="10" height="10" fill="{lang["color"]}"/>'
            f'<text x="850" y="{ly}" class="mono" font-size="13" fill="{PALETTE["ink"]}">{esc(lang["name"])}</text>'
            f'<text x="1182" y="{ly}" text-anchor="end" class="mono" font-size="13" fill="{PALETTE["c1"]}">{lang["pct"]}%</text></g>'
        )
    aria = (f"GitHub stats: {st['commits']} commits, {st['contrib_year']} kontribusi 12 bulan, "
            f"streak {sk['current']} hari, bahasa utama {', '.join(l['name'] for l in st['languages'][:3])}")
    return _finish(svgkit.render(
        "telemetry.svg",
        style=svgkit.base_style(),
        aria=esc(aria),
        stat_rows="\n".join(rows_svg),
        ring_len=f"{ring_len:.1f}", ring_off=f"{ring_off:.1f}",
        ring2_len=f"{ring2_len:.1f}", ring2_off=f"{ring2_off:.1f}",
        since_year=esc(st.get("since", "")[:4]),
        s_total=str(sk["total"]), s_current=str(sk["current"]), s_longest=str(sk["longest"]),
        s_range=esc(sk.get("range", "")), s_current_range=esc(sk.get("current_range", "") or "belum ada"),
        s_longest_range=esc(sk.get("longest_range", "") or "belum ada"),
        bar_w=str(_LANG_BAR_W), lang_bar="\n".join(bar), lang_rows="\n".join(legend),
        updated=esc(st.get("updated", "")),
    ))


def dt_years(since: str) -> int:
    """Umur akun dalam tahun penuh dari 'YYYY-MM'."""
    import datetime as _dt

    try:
        y, m = int(since[:4]), int(since[5:7])
    except ValueError:
        return 1
    today = _dt.date.today()
    return max(1, today.year - y - (1 if (today.month, 1) < (m, 1) else 0))


# ---------------------------------------------------------------- timeline
def build_timeline(data: dict) -> str:
    p = data["profile"]
    js = job_strings(p)
    n_certs = len(data["certs"])
    entries = [{"when": js["timeline_when"], "title": f"{p['job']['title']} · {p['job']['company']}",
                "desc": p["job"]["desc"], "now": p.get("current_job", True)}]
    entries += [dict(e, desc=e["desc"].replace("{n_certs}", str(n_certs)), now=False) for e in data["timeline"]]
    out = []
    y = 44
    for i, e in enumerate(entries):
        desc_lines = wrap_text(e["desc"], 100)[:2]
        color = PALETTE["c3"] if e["now"] else PALETTE["c1"]
        node = (f'<circle class="now" cx="61" cy="{y}" r="9" fill="{PALETTE["c3"]}" opacity=".5"/>' if e["now"] else "")
        out.append(
            f'<g class="ent" style="animation-delay:{0.2 * i:.2f}s">{node}'
            f'<circle class="node" cx="61" cy="{y}" r="5" fill="{color}" filter="url(#neonf)" style="animation-delay:-{0.5 * i:.1f}s"/>'
            f'<text x="92" y="{y - 10}" class="mono" font-size="12" fill="{PALETTE["c1"]}" letter-spacing="1">{esc(e["when"])}</text>'
            f'<text x="92" y="{y + 10}" class="orb" font-size="15" fill="{PALETTE["ink"]}">{orb_text(e["title"])}</text>'
            + "".join(f'<text x="92" y="{y + 30 + j * 17}" class="mono" font-size="12" fill="{PALETTE["muted"]}">{esc(l)}</text>'
                      for j, l in enumerate(desc_lines))
            + "</g>"
        )
        y += 50 + 17 * len(desc_lines) + 18
    height = y - 20
    return _finish(svgkit.render(
        "timeline.svg",
        style=svgkit.base_style(),
        aria=esc("; ".join(f"{e['when']}: {e['title']}" for e in entries)),
        height=str(height),
        line_h=str(height - 40),
        entries="\n".join(out),
    ))


# ---------------------------------------------------------------- connect
_CONNECT_TEXT = "Terbuka untuk kolaborasi proyek web, open source, atau tukar ide soal Laravel dan Next.js."


def build_button(label: str, sub: str, fill: str, stroke: str, color: str) -> str:
    return _finish(svgkit.render(
        "button.svg", style=svgkit.base_style(),
        label=esc(label), sub=esc(sub), fill=fill, stroke=stroke, color=color,
    ))


def build_connect(data: dict) -> dict[str, str]:
    links = data["profile"]["links"]
    short = lambda u: u.replace("https://", "").replace("www.", "").rstrip("/")  # noqa: E731
    return {
        "connect.svg": _finish(svgkit.render("connect.svg", style=svgkit.base_style(), text=esc(_CONNECT_TEXT))),
        "btn-linkedin.svg": build_button("LINKEDIN", short(links["linkedin"]), PALETTE["c2"], PALETTE["c1"], "#ffffff"),
        "btn-portfolio.svg": build_button("PORTFOLIO", short(links["portfolio"]), PALETTE["panel"], PALETTE["c1"], PALETTE["c1"]),
        "btn-email.svg": build_button("EMAIL", links["email"], PALETTE["panel"], PALETTE["c3"], PALETTE["c3"]),
    }


# ---------------------------------------------------------------- README
_SHIELDS = "https://img.shields.io/badge/"
_USER = "RayNathans"


def _shield_text(s: str) -> str:
    return quote(s.replace("-", "--").replace("_", "__"), safe="-_.~")


def badge(label: str, value: str, color: str, logo: str | None = None, logo_color: str = "white") -> str:
    path = (_shield_text(label) + "-" if label else "") + _shield_text(value) + "-" + color
    url = f"{_SHIELDS}{path}?style=for-the-badge&labelColor={PALETTE['panel'][1:]}"
    if logo:
        url += f"&logo={logo}&logoColor={logo_color}"
    return url


def typing_url() -> str:
    lines = ["nathan@github:~$ whoami", "nathan@github:~$ cat about.json",
             "nathan@github:~$ ./deploy --prod", "nathan@github:~$ git push origin main"]
    return (
        "https://readme-typing-svg.demolab.com?font=Share+Tech+Mono&size=18&duration=2600&pause=800"
        "&color=00E5FF&background=00000000&center=true&vCenter=true&width=700&height=40&lines="
        + ";".join(quote_plus(l) for l in lines)
    )


def stats_urls() -> dict:
    c = {k: v[1:] for k, v in PALETTE.items()}
    return {
        "stats_url": (
            f"https://github-readme-stats.vercel.app/api?username={_USER}&show_icons=true&hide_border=false"
            f"&bg_color={c['bg']}&border_color={c['line']}&title_color={c['c1']}&text_color={c['ink']}"
            f"&icon_color={c['c3']}&ring_color={c['c2']}&rank_icon=percentile&include_all_commits=true&cache_seconds=86400"
        ),
        "streak_url": (
            f"https://streak-stats.demolab.com?user={_USER}&background={c['bg']}&border={c['line']}&stroke={c['line']}"
            f"&ring={c['c2']}&fire={c['c3']}&currStreakNum={c['c1']}&sideNums={c['ink']}&currStreakLabel={c['c1']}"
            f"&sideLabels={c['muted']}&dates={c['muted']}"
        ),
        "langs_url": (
            f"https://github-readme-stats.vercel.app/api/top-langs/?username={_USER}&layout=compact&langs_count=6"
            f"&bg_color={c['bg']}&border_color={c['line']}&title_color={c['c1']}&text_color={c['ink']}"
        ),
        "snake_url": f"https://raw.githubusercontent.com/{_USER}/{_USER}/output/github-snake.svg",
        "komarev": f"https://komarev.com/ghpvc/?username={_USER}&style=for-the-badge&color={c['c1']}&label=PROFILE+VIEWS",
    }


def build_readme(data: dict) -> str:
    p = data["profile"]
    js = job_strings(p)
    h = html_escape
    skill_badges = "\n".join(
        f'  <a href="{s["badge"]["url"]}"><img src="{badge("", s["name"], PALETTE["panel"][1:], s["badge"]["logo"], s["badge"]["color"])}" alt="{h(s["name"])}"></a>'
        for s in data["skills"]
    )
    project_cells = "\n".join(
        f'<td width="33%" valign="top">\n'
        f'<a href="{pr["live"]}"><img src="assets/proj-{pr["id"]}.svg" width="100%" alt="{h(pr["title"])}: {h(pr["desc"])}"></a>\n'
        f'<p align="center"><a href="{pr["live"]}">▸ LIVE DEMO</a></p>\n</td>'
        for pr in data["projects"]
    )
    cert_list = "\n".join(
        f'<li><a href="https://www.dicoding.com/certificates/{c["id"]}">{h(c["title"])}</a> · <code>{c["date"]}</code></li>'
        for c in data["certs"]
    )
    cert_list = "<ul>\n" + cert_list + "\n</ul>"
    n_certs = len(data["certs"])
    vals = dict(
        typing_url=typing_url(),
        b_role=badge("ROLE", js["role_badge"], PALETTE["c1"][1:]),
        b_strip=badge(js["strip_label"], js["strip_value"], PALETTE["c2"][1:]),
        b_certs=badge("CERTS", f"{n_certs:02d} · DICODING", PALETTE["c3"][1:]),
        cert_count=str(n_certs),
        cert_count2=f"{n_certs:02d}",
        fact02=js["fact02"],
        role_badge=js["role_badge"],
        strip_label=js["strip_label"],
        strip_value=js["strip_value"],
        name=p["name"],
        role=p["role"],
        about_now=js["about_now"],
        city=p["city"],
        stack_json=", ".join(f'"{s}"' for s in p["stack"]),
        learning=p["learning"],
        motto=p["motto"],
        fact01=js["fact01"],
        skill_names=h(", ".join(s["name"] for s in data["skills"])),
        skill_badges=skill_badges,
        project_cells=project_cells,
        timeline_when=js["timeline_when"],
        job_title=p["job"]["title"],
        company=p["job"]["company"],
        job_desc=p["job"]["desc"],
        cert_list=cert_list,
        linkedin=p["links"]["linkedin"],
        portfolio=p["links"]["portfolio"],
        email=p["links"]["email"],
        b_linkedin=badge("", "LINKEDIN", "0a66c2", "linkedin", "white"),
        b_portfolio=badge("", "PORTFOLIO", PALETTE["c1"][1:], "netlify", "03040d"),
        b_email=badge("", "EMAIL", PALETTE["c3"][1:], "gmail", "white"),
        **stats_urls(),
    )
    return svgkit.render("README.md.tpl", **vals)


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
    write("strip.svg", build_strip(data), out)
    write("identity.svg", build_identity(data), out)
    write("telemetry.svg", build_telemetry(data), out)
    write("timeline.svg", build_timeline(data), out)
    for name, svg in build_connect(data).items():
        write(name, svg, out)
    write("README.md", build_readme(data), out)
    print("build selesai")


if __name__ == "__main__":
    main()
