"""Ambil statistik GitHub @RayNathans dari API publik + halaman kontribusi, tulis data/stats.json.

    .venv/Scripts/python.exe tools/fetch_stats.py [--user RayNathans]

Tanpa token pun jalan (rate limit lebih rendah). Di GitHub Actions, env GITHUB_TOKEN dipakai
sebagai Authorization untuk REST API. Bila pengambilan gagal, stats.json lama dibiarkan.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "stats.json"
API = "https://api.github.com"

# Warna linguist untuk bahasa yang umum dipakai Nathan; sisanya memakai palet neon bergilir.
LANG_COLORS = {
    "PHP": "#4F5D95", "Blade": "#f7523f", "TypeScript": "#3178c6", "JavaScript": "#f1e05a",
    "Python": "#3572A5", "HTML": "#e34c26", "CSS": "#663399", "SCSS": "#c6538c", "Vue": "#41b883",
    "Shell": "#89e051", "Dockerfile": "#384d54", "Go": "#00ADD8", "Java": "#b07219", "Kotlin": "#A97BFF",
}
FALLBACK_COLORS = ["#00e5ff", "#2f6bff", "#ff2bd6", "#7c3aed", "#22c55e", "#f59e0b"]


# ------------------------------------------------------------------ parsing murni
def parse_contributions(html: str) -> list[dict]:
    """Baca kalender kontribusi dari HTML github.com/users/<user>/contributions."""
    days = {}
    for m in re.finditer(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*?id="([^"]+)"', html):
        days[m.group(2)] = {"date": m.group(1), "count": 0}
    for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        cid, text = m.group(1), m.group(2).strip()
        if cid in days:
            n = re.match(r"(\d+|No) contribution", text)
            days[cid]["count"] = 0 if not n or n.group(1) == "No" else int(n.group(1))
    return sorted(days.values(), key=lambda d: d["date"])


def _rng(a: str, b: str) -> str:
    return f"{a} – {b}"


def compute_streaks(days: list[dict], today: dt.date | None = None) -> dict:
    """Total kontribusi, streak saat ini, dan streak terpanjang dari deret harian terurut."""
    today = today or dt.date.today()
    total = sum(d["count"] for d in days)
    longest = cur = 0
    longest_rng = cur_rng = None
    run_start = None
    for d in days:
        if d["count"] > 0:
            cur += 1
            run_start = run_start or d["date"]
            if cur > longest:
                longest, longest_rng = cur, (run_start, d["date"])
        else:
            cur, run_start = 0, None
    # streak saat ini: hitung mundur dari hari ini; hari ini boleh masih kosong
    current = 0
    current_rng = None
    idx = {d["date"]: d["count"] for d in days}
    day = today
    if idx.get(day.isoformat(), 0) == 0:
        day -= dt.timedelta(days=1)
    end = day
    while idx.get(day.isoformat(), 0) > 0:
        current += 1
        day -= dt.timedelta(days=1)
    if current:
        current_rng = ((day + dt.timedelta(days=1)).isoformat(), end.isoformat())
    return {
        "total": total,
        "current": current,
        "longest": longest,
        "current_range": _rng(*current_rng) if current_rng else "",
        "longest_range": _rng(*longest_rng) if longest_rng else "",
        "range": _rng(days[0]["date"], days[-1]["date"]) if days else "",
    }


def aggregate_languages(per_repo: dict[str, dict[str, int]], top: int = 6) -> list[dict]:
    """Gabungkan byte per bahasa dari semua repo; persen dibulatkan sehingga totalnya 100."""
    totals: dict[str, int] = {}
    for langs in per_repo.values():
        for name, b in langs.items():
            totals[name] = totals.get(name, 0) + b
    items = sorted(totals.items(), key=lambda kv: -kv[1])[:top]
    grand = sum(b for _, b in items) or 1
    raw = [b * 100 / grand for _, b in items]
    pcts = [int(x) for x in raw]
    for i in sorted(range(len(raw)), key=lambda i: raw[i] - pcts[i], reverse=True)[: 100 - sum(pcts)]:
        pcts[i] += 1
    out = []
    for i, ((name, b), pct) in enumerate(zip(items, pcts)):
        out.append({"name": name, "bytes": b, "pct": pct,
                    "color": LANG_COLORS.get(name, FALLBACK_COLORS[i % len(FALLBACK_COLORS)])})
    return out


# ------------------------------------------------------------------ pengambilan
def _get(url: str, token: str | None, accept: str = "application/vnd.github+json") -> bytes:
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "RayNathans-profile-build"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def _json(url: str, token: str | None) -> dict:
    return json.loads(_get(url, token))


def fetch_all(user: str, token: str | None = None) -> dict:
    u = _json(f"{API}/users/{user}", token)
    repos = _json(f"{API}/users/{user}/repos?per_page=100&type=owner", token)
    repos = [r for r in repos if not r.get("fork")]
    per_repo = {r["name"]: _json(r["languages_url"], token) for r in repos}
    commits = _json(f"{API}/search/commits?q=author:{user}&per_page=1", token).get("total_count", 0)
    prs = _json(f"{API}/search/issues?q=author:{user}+type:pr&per_page=1", token).get("total_count", 0)
    issues = _json(f"{API}/search/issues?q=author:{user}+type:issue&per_page=1", token).get("total_count", 0)
    html = _get(f"https://github.com/users/{user}/contributions", None, accept="text/html").decode("utf-8", "ignore")
    days = parse_contributions(html)
    streak = compute_streaks(days)
    return {
        "updated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "since": u.get("created_at", "")[:7],
        "followers": u.get("followers", 0),
        "public_repos": u.get("public_repos", 0),
        "stars": sum(r.get("stargazers_count", 0) for r in repos),
        "commits": commits,
        "prs": prs,
        "issues": issues,
        "contrib_year": streak["total"],
        "streak": streak,
        "languages": aggregate_languages(per_repo),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default="RayNathans")
    args = ap.parse_args()
    try:
        data = fetch_all(args.user, os.environ.get("GITHUB_TOKEN") or None)
    except Exception as e:  # noqa: BLE001
        print(f"fetch_stats gagal: {e}; stats.json lama dipertahankan", file=sys.stderr)
        return 0 if OUT.exists() else 1
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"stats.json diperbarui: {data['commits']} commits, {data['contrib_year']} kontribusi 12 bln, "
          f"{len(data['languages'])} bahasa")
    return 0


if __name__ == "__main__":
    sys.exit(main())
