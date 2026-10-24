"""Per-day comparison on the six SYNTHETIC test days -> docs/fixture_findings.md.

Plans use the leakage-safe forecast proxy; numbers are scored on the day's observed values.
Run: python eval/fixture_table.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.config import load_config  # noqa: E402
from app.planning import FIXTURES, PLAN_NAMES, _read_list, plan_for  # noqa: E402

OUT = ROOT / "docs" / "fixture_findings.md"
COLS = [("hours_ge_80f", "h >=80F"), ("hours_ge_95f", "h >=95F"), ("hours_aqi_ge_101", "h AQI>=101"),
        ("hours_aqi_ge_151", "h AQI>=151"), ("dual_hazard_hours", "dual h"), ("paid_hours", "paid h")]


def build() -> tuple[str, list[str]]:
    s = load_config()["shift"]
    args = (s["default_paid_hours"], s["default_earliest_start"], s["default_latest_end"], False)
    lines = ["SYNTHETIC ILLUSTRATIONS, NOT EVIDENCE", "",
             "# Fixture findings",
             "",
             f"Plans built on the forecast proxy (no ORACLE), scored on observed values. "
             f"Paid hours {args[0]}, window {args[1]}-{args[2]}. Weighted cost uses config.yaml weights.",
             ""]
    smoke_wins = []
    for day in _read_list(FIXTURES / "days.json"):
        r = plan_for(day.id, *args)
        lines += [f"## {day.id} ({day.provenance})", "", day.label, "",
                  "| plan | " + " | ".join(c[1] for c in COLS) + " | cost (observed) | blocks |",
                  "|---" * (len(COLS) + 3) + "|"]
        for name in PLAN_NAMES:
            m, p = r["metrics"][name]["observed"], r["plans"][name]
            blocks = ", ".join(f"{b['start']}-{b['end']}" for b in p["blocks"])
            lines.append(f"| {name} | " + " | ".join(f"{m[k]:g}" for k, _ in COLS)
                         + f" | {p['observed_cost']:g} | {blocks} |")
        lines.append("")
        obs = r["metrics"]
        opt = obs["optimizer"]["observed"]["hours_aqi_ge_101"]
        if all(opt < obs[b]["observed"]["hours_aqi_ge_101"] for b in ("b3_early", "b3_late")):
            smoke_wins.append(day.id)
    lines += ["## Summary", "",
              "Days where the optimizer has fewer observed AQI>=101 hours than BOTH B3 variants: "
              + (", ".join(smoke_wins) if smoke_wins else "none") + ".", ""]
    return "\n".join(lines), smoke_wins


def main() -> None:
    text, wins = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT}; optimizer beats both B3 variants on AQI>=101 hours: {wins or 'none'}")


if __name__ == "__main__":
    main()
