"""Copy the limitations list from docs/PITCH_filled.md (section "(d) Limitations", filled from the result files)
into static/limitations.json, so the offline UI's About sheet can show it without hardcoding anything. Non-logic.

Run after `python -m analysis.fill_pitch`:  python -m analysis.export_limitations
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "docs" / "PITCH_filled.md", ROOT / "static" / "limitations.json"


def limitations(text: str) -> list[str]:
    section = re.split(r"^## \(d\) Limitations\s*$", text, flags=re.M)[1]
    section = re.split(r"^## ", section, flags=re.M)[0]
    items, cur = [], None
    for line in section.splitlines():
        if line.startswith("- "):
            cur = line[2:].strip()
            items.append(cur)
        elif line.startswith("  ") and items:
            items[-1] = f"{items[-1]} {line.strip()}"
    return items


def main() -> None:
    items = limitations(SRC.read_text(encoding="utf-8"))
    OUT.write_text(json.dumps({"source": "docs/PITCH_filled.md (d) Limitations", "limitations": items}, indent=1),
                   encoding="utf-8")
    print(f"wrote {OUT} ({len(items)} items)")


if __name__ == "__main__":
    main()
