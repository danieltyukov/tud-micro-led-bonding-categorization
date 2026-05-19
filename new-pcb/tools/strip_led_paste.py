#!/usr/bin/env python3
"""
Remove F.Paste from every WL-SFCC_0404 footprint pad so the solder-paste
stencil (whether from Aisler's stencil add-on or Amazing Assembly's SMT
line) does NOT deposit paste on the 26 LED bond pads.

The LEDs are bonded by the customer in the TU Delft cleanroom with a
controlled paste profile under the Tresky die-bonder — any pre-deposited
paste from the fab would contaminate the bond surface.

After this patch:
  - Pad layers go from `(layers "F.Cu" "F.Mask" "F.Paste")` → `(layers "F.Cu" "F.Mask")`
  - Mask aperture (gold pad still exposed for bonding) is preserved
  - Copper land is preserved
"""

from __future__ import annotations

import re
from pathlib import Path

PCB = Path(__file__).resolve().parents[2] / "new-pcb" / "tud-microled-v2.kicad_pcb"

FOOTPRINT_RE = re.compile(
    r'(\t\(footprint "([^"]+)"\n.*?\n\t\)\n)',
    re.DOTALL,
)


def strip_paste(block: str) -> tuple[str, int]:
    """Remove F.Paste / B.Paste from every pad's (layers ...) list in this footprint."""
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
    total_pads = 0
    led_footprints = 0
    for m in FOOTPRINT_RE.finditer(text):
        out.append(text[cursor:m.start()])
        block = m.group(1)
        if m.group(2) == "WL-SFCC_0404":
            new_block, n = strip_paste(block)
            out.append(new_block)
            total_pads += n
            led_footprints += 1
        else:
            out.append(block)
        cursor = m.end()
    out.append(text[cursor:])
    new_text = "".join(out)

    if new_text == text:
        print("No changes (LED pads already have no F.Paste).")
        return 0

    PCB.write_text(new_text)
    print(f"Patched {led_footprints} LED footprints, removed F.Paste from {total_pads} pads")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
