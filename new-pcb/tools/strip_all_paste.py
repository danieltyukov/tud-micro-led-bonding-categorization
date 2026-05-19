#!/usr/bin/env python3
"""
Strip F.Paste / B.Paste from EVERY footprint pad in the PCB.

Workflow context: parts are ordered loose from Eurocircuits ('Place loose')
and hand-soldered at TU Delft EKL with solder wire + flux — no solder paste
or stencil is ever used. So the design must have an empty F.Paste gerber.
"""

from __future__ import annotations

import re
from pathlib import Path

PCB = Path(__file__).resolve().parents[2] / "new-pcb" / "tud-microled-v2.kicad_pcb"

FOOTPRINT_RE = re.compile(
    r'(\t\(footprint "([^"]+)"\n.*?\n\t\)\n)',
    re.DOTALL,
)


def strip_paste_from_block(block: str) -> tuple[str, int]:
    """Remove F.Paste / B.Paste from every (layers ...) list in this footprint."""
    pad_layer_re = re.compile(r'(\(layers\s+)([^)]+)(\))')
    n = [0]

    def fix(m: re.Match) -> str:
        prefix, layers_text, suffix = m.group(1), m.group(2), m.group(3)
        layers = re.findall(r'"[^"]+"', layers_text)
        kept = [L for L in layers if L not in ('"F.Paste"', '"B.Paste"')]
        if len(kept) != len(layers):
            n[0] += 1
        return prefix + " ".join(kept) + suffix

    new = pad_layer_re.sub(fix, block)
    return new, n[0]


def main() -> int:
    text = PCB.read_text()
    out: list[str] = []
    cursor = 0
    pad_count = 0
    fp_stats: dict[str, int] = {}

    for m in FOOTPRINT_RE.finditer(text):
        out.append(text[cursor:m.start()])
        block = m.group(1)
        fp_name = m.group(2)
        new_block, n = strip_paste_from_block(block)
        out.append(new_block)
        if n:
            fp_stats[fp_name] = fp_stats.get(fp_name, 0) + n
            pad_count += n
        cursor = m.end()
    out.append(text[cursor:])
    new_text = "".join(out)

    if new_text == text:
        print("No changes (no F.Paste / B.Paste left anywhere).")
        return 0

    PCB.write_text(new_text)
    print(f"Stripped F.Paste / B.Paste from {pad_count} pads across the design:")
    for fp, n in sorted(fp_stats.items()):
        print(f"  {n:>4}  {fp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
