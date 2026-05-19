#!/usr/bin/env python3
"""
Unify the (property "Value" "...") field on each footprint that shares an MPN
so Aisler's BOM Grouped view collapses them into a single row.

Before: TH1-TH4 each have Value = "TH1"/"TH2"/"TH3"/"TH4" → 4 rows in Aisler.
After:  TH1-TH4 all have Value = "NTCG104BH103HT1"          → 1 row, qty 4.
"""

from __future__ import annotations

import re
from pathlib import Path

PCB = Path(__file__).resolve().parents[2] / "new-pcb" / "tud-microled-v2.kicad_pcb"

# Map footprint-name → unified Value string (matches the MPN)
UNIFY = {
    "NTC_0402":      "NTCG104BH103HT1",
    "EIS_Load_0603": "RT0603BRD07100RL",
    "Header_2.54mm": "TSW-140-07-G-S",
    "WL-SFCC_0404":  "WL-SFCC RGB (DNP)",
}

FOOTPRINT_RE = re.compile(
    r'(\t\(footprint "([^"]+)"\n.*?\n\t\)\n)',
    re.DOTALL,
)


def patch(block: str, fp_name: str) -> tuple[str, bool]:
    if fp_name not in UNIFY:
        return block, False
    new_value = UNIFY[fp_name]
    # Replace the FIRST (property "Value" "...") in this footprint block
    new_block, n = re.subn(
        r'(\(property "Value" )"[^"]*"',
        rf'\1"{new_value}"',
        block,
        count=1,
    )
    return new_block, n > 0


def main() -> int:
    text = PCB.read_text()
    out: list[str] = []
    cursor = 0
    changes: dict[str, int] = {}
    for m in FOOTPRINT_RE.finditer(text):
        out.append(text[cursor:m.start()])
        block = m.group(1)
        fp = m.group(2)
        new_block, changed = patch(block, fp)
        out.append(new_block)
        if changed:
            changes[fp] = changes.get(fp, 0) + 1
        cursor = m.end()
    out.append(text[cursor:])
    new_text = "".join(out)

    if new_text == text:
        print("No changes.")
        return 0

    PCB.write_text(new_text)
    print(f"Wrote {PCB}")
    for fp, n in sorted(changes.items()):
        print(f"  {n:>3}× {fp} Value unified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
