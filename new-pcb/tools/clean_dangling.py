#!/usr/bin/env python3
"""
Remove the 3 dangling DRC items identified after consolidation:
  - track segment from (59.5, 35.39) to (62.5, 35.39) on F.Cu
  - via at (88, 16) on F.Cu/B.Cu
  - via at (4, 16) on F.Cu/B.Cu

These connected to footprints removed during consolidation (probe pads or
bare GND lands) and now have no useful endpoint. KiCad flags them as
'track_dangling' / 'via_dangling' warnings.
"""

import re
from pathlib import Path

PCB = Path(__file__).resolve().parents[2] / "new-pcb" / "tud-microled-v2.kicad_pcb"

# Patterns for the 3 known dangling items. Use re.DOTALL across the block.
PATTERNS = [
    re.compile(
        r'\t\(segment\s+\(start 59\.5 35\.39\)\s+\(end 62\.5 35\.39\).*?\n\t\)\n',
        re.DOTALL,
    ),
    re.compile(
        r'\t\(via\s+\(at 88 16\).*?\n\t\)\n',
        re.DOTALL,
    ),
    re.compile(
        r'\t\(via\s+\(at 4 16\).*?\n\t\)\n',
        re.DOTALL,
    ),
]

def main() -> int:
    text = PCB.read_text()
    removed = 0
    for p in PATTERNS:
        text, n = p.subn('', text)
        removed += n
        print(f"  pattern {p.pattern[:60]}... → removed {n}")
    if removed:
        PCB.write_text(text)
        print(f"\nRemoved {removed} dangling items, wrote {PCB}")
    else:
        print("No matches (already clean).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
