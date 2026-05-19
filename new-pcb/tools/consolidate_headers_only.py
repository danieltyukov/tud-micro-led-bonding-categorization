#!/usr/bin/env python3
"""
Collapse 64 single-pin Header_2.54mm footprints into 2 multi-pin 1x32 strips
(one H_N at north edge, one H_S at south edge). DOES NOT touch any other
footprint — all bare-pad test structures (BondPad_DoE, TLM, VDP, Probe pads,
TC pads, Fiducials) stay on the board as bare ENIG gold lands, exactly as
designed. They're already flagged DNP in the .kicad_pcb so Aisler /
Eurocircuits ignore them as parts.
"""

from __future__ import annotations

import re
import uuid as _uuid
from pathlib import Path

PCB = Path(__file__).resolve().parents[2] / "new-pcb" / "tud-microled-v2.kicad_pcb"


FOOTPRINT_RE = re.compile(
    r'(\t\(footprint "([^"]+)"\n.*?\n\t\)\n)',
    re.DOTALL,
)


def extract_ref(block: str) -> str:
    m = re.search(r'\(property "Reference" "([^"]+)"', block)
    return m.group(1) if m else "?"


def extract_at(block: str) -> tuple[float, float]:
    m = re.search(r'\(at ([\-0-9.]+) ([\-0-9.]+)(?: [\-0-9.]+)?\)', block)
    return float(m.group(1)), float(m.group(2))


def extract_pad_net(block: str) -> tuple[int, str]:
    m = re.search(r'\(pad "1" thru_hole .*?\(net (\d+) "([^"]*)"\)', block, re.DOTALL)
    return (int(m.group(1)), m.group(2)) if m else (0, "")


PIN_TEMPLATE = (
    '\t\t(pad "{pin}" thru_hole circle\n'
    '\t\t\t(at {dx:.3f} 0)\n'
    '\t\t\t(size 1.7 1.7)\n'
    '\t\t\t(drill 1)\n'
    '\t\t\t(layers "*.Cu" "*.Mask")\n'
    '\t\t\t(remove_unused_layers no)\n'
    '\t\t\t(net {n} "{nm}")\n'
    '\t\t\t(uuid "{u}")\n'
    '\t\t)\n'
)


def build_strip(ref: str, x0: float, y0: float, pins: list[tuple[float, int, str]]) -> str:
    pad_blocks = "".join(
        PIN_TEMPLATE.format(pin=i, dx=(xa - x0), n=n, nm=nm, u=str(_uuid.uuid4()))
        for i, (xa, n, nm) in enumerate(pins, start=1)
    )
    return (
        f'\t(footprint "Header_2.54mm"\n'
        f'\t\t(layer "F.Cu")\n'
        f'\t\t(uuid "{_uuid.uuid4()}")\n'
        f'\t\t(at {x0} {y0})\n'
        f'\t\t(property "Reference" "{ref}" (at 0 -2 0) (layer "F.Fab") (hide yes)\n'
        f'\t\t\t(uuid "{_uuid.uuid4()}")\n'
        f'\t\t\t(effects (font (size 1 1) (thickness 0.15)))\n'
        f'\t\t)\n'
        f'\t\t(property "Value" "TSW-140-07-G-S" (at 0 2 0) (layer "F.Fab") (hide yes)\n'
        f'\t\t\t(uuid "{_uuid.uuid4()}")\n'
        f'\t\t\t(effects (font (size 1 1) (thickness 0.15)))\n'
        f'\t\t)\n'
        f'\t\t(property "Footprint" "" (at 0 0 0) (layer "F.Fab") (hide yes)\n'
        f'\t\t\t(uuid "{_uuid.uuid4()}")\n'
        f'\t\t\t(effects (font (size 1.27 1.27) (thickness 0.15)))\n'
        f'\t\t)\n'
        f'\t\t(property "Datasheet" "" (at 0 0 0) (layer "F.Fab") (hide yes)\n'
        f'\t\t\t(uuid "{_uuid.uuid4()}")\n'
        f'\t\t\t(effects (font (size 1.27 1.27) (thickness 0.15)))\n'
        f'\t\t)\n'
        f'\t\t(property "Description" "" (at 0 0 0) (layer "F.Fab") (hide yes)\n'
        f'\t\t\t(uuid "{_uuid.uuid4()}")\n'
        f'\t\t\t(effects (font (size 1.27 1.27) (thickness 0.15)))\n'
        f'\t\t)\n'
        f'\t\t(property "Manufacturer" "Samtec" (at 0 0 0) (unlocked yes) (layer "F.Fab") (hide yes)\n'
        f'\t\t\t(uuid "{_uuid.uuid4()}")\n'
        f'\t\t\t(effects (font (size 1.27 1.27) (thickness 0.15)))\n'
        f'\t\t)\n'
        f'\t\t(property "MPN" "TSW-140-07-G-S" (at 0 0 0) (unlocked yes) (layer "F.Fab") (hide yes)\n'
        f'\t\t\t(uuid "{_uuid.uuid4()}")\n'
        f'\t\t\t(effects (font (size 1.27 1.27) (thickness 0.15)))\n'
        f'\t\t)\n'
        f'\t\t(attr through_hole)\n'
        + pad_blocks +
        f'\t\t(embedded_fonts no)\n'
        f'\t)\n'
    )


def main() -> int:
    text = PCB.read_text()
    blocks = list(FOOTPRINT_RE.finditer(text))
    print(f"Found {len(blocks)} footprint blocks (keeping all bare-pad structures)")

    h_pins = {"H_N": [], "H_S": []}
    drop_set = set()

    for i, m in enumerate(blocks):
        block = m.group(1)
        if m.group(2) != "Header_2.54mm":
            continue
        ref = extract_ref(block)
        if not (ref.startswith("H_N_") or ref.startswith("H_S_")):
            continue
        side = "H_N" if ref.startswith("H_N_") else "H_S"
        x, y = extract_at(block)
        net_n, net_name = extract_pad_net(block)
        h_pins[side].append((int(ref.split("_")[-1]), x, y, net_n, net_name))
        drop_set.add(i)

    print(f"  Collapsing {len(h_pins['H_N'])} H_N pins → 1 strip")
    print(f"  Collapsing {len(h_pins['H_S'])} H_S pins → 1 strip")

    h_pins["H_N"].sort()
    h_pins["H_S"].sort()

    new_strips = []
    for side in ("H_N", "H_S"):
        if not h_pins[side]:
            continue
        x0 = min(p[1] for p in h_pins[side])
        y0 = h_pins[side][0][2]
        pins = [(x, n, nm) for _, x, _, n, nm in h_pins[side]]
        new_strips.append(build_strip(side, x0, y0, pins))

    out = []
    cursor = 0
    for i, m in enumerate(blocks):
        out.append(text[cursor:m.start()])
        if i not in drop_set:
            out.append(m.group(1))
        cursor = m.end()
    out.append("".join(new_strips))
    out.append(text[cursor:])
    PCB.write_text("".join(out))
    print(f"Wrote {PCB}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
