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
    return d
