"""Data uji: struktur sama dengan data/*.json, tetapi nilainya dikunci di sini
sehingga test tidak ikut berubah saat Nathan mengedit datanya."""
import copy

from tools import svgkit


def data(current_job: bool = True) -> dict:
    d = copy.deepcopy(svgkit.load_data())
    d["profile"]["name"] = "Nikolaus Ray Nathan"
    d["profile"]["current_job"] = current_job
    d["profile"]["job"].update(
        {"title": "Backend Developer", "company": "Performa Optima Group",
         "city": "SURABAYA", "start": "2025-08", "end": "2026-02"}
    )
    d["profile"]["stack"] = ["Laravel", "Next.js", "TypeScript", "PostgreSQL"]
    d["profile"]["links"]["email"] = "nikolausraynathan@gmail.com"
    d["stats"] = {
        "updated": "2026-11-04 10:00 UTC",
        "since": "2024-02",
        "followers": 7,
        "public_repos": 4,
        "stars": 3,
        "commits": 64,
        "prs": 2,
        "issues": 1,
        "contrib_year": 67,
        "streak": {"total": 67, "current": 5, "longest": 9,
                   "current_range": "2026-10-31 – 2026-11-04", "longest_range": "2026-02-01 – 2026-02-09",
                   "range": "2025-11-02 – 2026-11-04"},
        "languages": [
            {"name": "TypeScript", "bytes": 700000, "pct": 49, "color": "#3178c6"},
            {"name": "Blade", "bytes": 400000, "pct": 28, "color": "#f7523f"},
            {"name": "PHP", "bytes": 300000, "pct": 21, "color": "#4F5D95"},
            {"name": "JavaScript", "bytes": 14000, "pct": 1, "color": "#f1e05a"},
            {"name": "CSS", "bytes": 9000, "pct": 1, "color": "#663399"},
        ],
    }
    d["timeline"] = [
        {"when": "2025-02 – 2025-08 · YOGYAKARTA", "title": "Frontend Developer (Volunteer) · Litera Sumbu Pakarti",
         "desc": "Sistem manajemen buku Yayasan Litera: peminjaman, donasi, inventaris. Memimpin tim 3 developer. Laravel/PHP."},
        {"when": "2025-02 – 2025-05", "title": "Dicoding Indonesia",
         "desc": "Menyelesaikan {n_certs} kelas: dasar pemrograman sampai Back-End dan Web Intermediate."},
    ]
    return d
