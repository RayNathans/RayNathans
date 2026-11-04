import datetime as dt
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import fetch_stats  # noqa: E402

HTML = """
<td data-date="2026-11-02" id="contribution-day-component-0-0" data-level="0" class="ContributionCalendar-day"></td>
<td data-date="2026-11-03" id="contribution-day-component-1-0" data-level="2" class="ContributionCalendar-day"></td>
<td data-date="2026-11-04" id="contribution-day-component-2-0" data-level="1" class="ContributionCalendar-day"></td>
<tool-tip for="contribution-day-component-0-0" class="sr-only">No contributions on November 2nd.</tool-tip>
<tool-tip for="contribution-day-component-1-0" class="sr-only">12 contributions on November 3rd.</tool-tip>
<tool-tip for="contribution-day-component-2-0" class="sr-only">1 contribution on November 4th.</tool-tip>
"""


class ParseTests(unittest.TestCase):
    def test_parse_contributions(self):
        days = fetch_stats.parse_contributions(HTML)
        self.assertEqual(
            days,
            [{"date": "2026-11-02", "count": 0}, {"date": "2026-11-03", "count": 12}, {"date": "2026-11-04", "count": 1}],
        )

    def test_compute_streaks(self):
        days = [
            {"date": "2026-10-28", "count": 2}, {"date": "2026-10-29", "count": 0}, {"date": "2026-10-30", "count": 1},
            {"date": "2026-10-31", "count": 3}, {"date": "2026-11-01", "count": 1}, {"date": "2026-11-02", "count": 0},
            {"date": "2026-11-03", "count": 12}, {"date": "2026-11-04", "count": 1},
        ]
        s = fetch_stats.compute_streaks(days, today=dt.date(2026, 11, 4))
        self.assertEqual(s["total"], 20)
        self.assertEqual(s["current"], 2)
        self.assertEqual(s["longest"], 3)
        self.assertEqual(s["current_range"], "2026-11-03 – 2026-11-04")
        self.assertEqual(s["longest_range"], "2026-10-30 – 2026-11-01")

    def test_current_streak_allows_today_empty(self):
        days = [{"date": "2026-11-02", "count": 1}, {"date": "2026-11-03", "count": 1}, {"date": "2026-11-04", "count": 0}]
        s = fetch_stats.compute_streaks(days, today=dt.date(2026, 11, 4))
        self.assertEqual(s["current"], 2)

    def test_aggregate_languages(self):
        per_repo = {"a": {"PHP": 7000, "Blade": 2000}, "b": {"TypeScript": 1000}}
        langs = fetch_stats.aggregate_languages(per_repo, top=6)
        self.assertEqual([x["name"] for x in langs], ["PHP", "Blade", "TypeScript"])
        self.assertEqual(sum(x["pct"] for x in langs), 100)
        self.assertEqual(langs[0]["pct"], 70)
        self.assertTrue(all(x["color"].startswith("#") for x in langs))

    def test_stats_json_shape(self):
        import json

        d = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
        for k in ("updated", "followers", "public_repos", "stars", "commits", "prs", "issues", "contrib_year", "streak", "languages"):
            self.assertIn(k, d)
        self.assertTrue({"total", "current", "longest"} <= set(d["streak"]))


if __name__ == "__main__":
    unittest.main()
