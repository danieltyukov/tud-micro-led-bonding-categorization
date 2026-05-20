#!/usr/bin/env python3
"""
Restore F.Paste on NTC_0402 and EIS_Load_0603 pads ONLY.

Decision history:
  - Earlier we planned "Place loose" → all paste apertures stripped (no SMT).
  - Now Eurocircuits will reflow the 4 NTCs + 1 resistor at the SMT line, so
    those 5 SMDs need paste apertures (10 pads total) to print through the
    stencil.
  - LEDs (WL-SFCC_0404) stay paste-less — bonded by us at EKL under the Tresky.
  - Headers (Header_2.54mm) are THT, never use paste regardless of process.
  - Every other footprint type is a bare-pad test structure with no parts.

After running, F.Paste gerber should contain exactly 10 D03 flashes.
"""

from __future__ import annotations

import re
from pathlib import Path

PCB = Path(__file__).resolve().parents[2] / "new-pcb" / "tud-microled-v2.kicad_pcb"

# Footprints that need F.Paste restored on every pad
RESTORE_PASTE = {"NTC_0402", "EIS_Load_0603"}

FOOTPRINT_RE = re.compile(
    r'(\t\(footprint "([^"]+)"\n.*?\n\t\)\n)',
    re.DOTALL,
)


def add_paste(block: str) -> tuple[str, int]:
    """Add 'F.Paste' to every pad's (layers ...) list in this block (if absent)."""
    pad_layer_re = re.compile(r'(\(layers\s+)([^)]+)(\))')
    n = [0]

    def fix(m: re.Match) -> str:
        prefix, layers_text, suffix = m.group(1), m.group(2), m.group(3)
        layers = re.findall(r'"[^"]+"', layers_text)
        if '"F.Paste"' in layers:
            return m.group(0)
        # Only add F.Paste if F.Cu is in the layer list (otherwise it's a
        # back-side or non-copper pad we shouldn't touch).
        if '"F.Cu"' not in layers:
            return m.group(0)
        layers.append('"F.Paste"')
        n[0] += 1
        return prefix + " ".join(layers) + suffix

    return pad_layer_re.sub(fix, block), n[0]


def main() -> int:
    text = PCB.read_text()
    out: list[str] = []
    cursor = 0
    pad_count = 0
    fp_count: dict[str, int] = {}
    for m in FOOTPRINT_RE.finditer(text):
        out.append(text[cursor:m.start()])
        block = m.group(1)
        fp_name = m.group(2)
        if fp_name in RESTORE_PASTE:
            new_block, n = add_paste(block)
            pad_count += n
            if n:
                fp_count[fp_name] = fp_count.get(fp_name, 0) + n
            out.append(new_block)
        else:
            out.append(block)
        cursor = m.end()
    out.append(text[cursor:])
    new_text = "".join(out)

    if new_text == text:
        print("No changes — paste already present on the target footprints.")
        return 0

    PCB.write_text(new_text)
    print(f"Restored F.Paste on {pad_count} pads:")
    for fp, n in sorted(fp_count.items()):
        print(f"  {n:>3}  {fp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
