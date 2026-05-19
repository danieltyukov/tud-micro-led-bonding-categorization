#!/usr/bin/env python3
"""
Rewrite tud-microled-v2.kicad_pcb so the BOM shows only ACTUAL PARTS:

  - 4 × NTC (TDK NTCG104BH103HT1)
  - 1 × R  (Yageo RT0603BRD07100RL)
  - 2 × strips (Samtec TSW-140-07-G-S) — one consolidated 1×32 north, one 1×32 south
  - 26 × LEDs (Wurth WL-SFCC, DNP — customer bonds)

All bare-pad footprints (BondPad_DoE, Fiducial_1mm, Probe_1.27mm, TC_Pad_1mm,
TLM, VDP) are removed from the .kicad_pcb entirely — they were design-only
gold lands, not parts the fab handles.

The 64 individual single-pin Header_2.54mm footprints (H_N_1..32 + H_S_1..32)
collapse into 2 multi-pin footprints (H_N at Y=13.5 with 32 pads, H_S at Y=85)
with each pad's net preserved at the original pin's X position.
"""

from __future__ import annotations

import re
import uuid as _uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PCB = REPO / "new-pcb" / "tud-microled-v2.kicad_pcb"


FOOTPRINT_RE = re.compile(
    r'(\t\(footprint "([^"]+)"\n.*?\n\t\)\n)',
    re.DOTALL,
)


def extract_ref(block: str) -> str:
    m = re.search(r'\(property "Reference" "([^"]+)"', block)
    return m.group(1) if m else "?"


def extract_at(block: str) -> tuple[float, float, float]:
    """The first (at X Y [rot]) line of the footprint block — its origin."""
    m = re.search(r'\(at ([\-0-9.]+) ([\-0-9.]+)(?: ([\-0-9.]+))?\)', block)
    x, y, rot = float(m.group(1)), float(m.group(2)), float(m.group(3) or 0)
    return x, y, rot


def extract_pad_net(block: str) -> tuple[int, str]:
    """Return (net_number, net_name) of the FIRST pad in the footprint."""
    m = re.search(
        r'\(pad "1" thru_hole .*?\(net (\d+) "([^"]*)"\)',
        block,
        re.DOTALL,
    )
    if not m:
        return (0, "")
    return (int(m.group(1)), m.group(2))


PIN_BLOCK_TEMPLATE = (
    '\t\t(pad "{pin}" thru_hole circle\n'
    '\t\t\t(at {dx:.3f} 0)\n'
    '\t\t\t(size 1.7 1.7)\n'
    '\t\t\t(drill 1)\n'
    '\t\t\t(layers "*.Cu" "*.Mask")\n'
    '\t\t\t(remove_unused_layers no)\n'
    '\t\t\t(net {net_num} "{net_name}")\n'
    '\t\t\t(uuid "{uuid}")\n'
    '\t\t)\n'
)


def build_consolidated_header(
    ref: str, x0: float, y0: float, pins: list[tuple[float, int, str]]
) -> str:
    """Build a 1×N multi-pin footprint block. `pins` = [(x_abs, net_num, net_name), ...]."""
    fp_uuid = _uuid.uuid4()
    pad_blocks = []
    for i, (x_abs, net_num, net_name) in enumerate(pins, start=1):
        dx = x_abs - x0
        pad_blocks.append(PIN_BLOCK_TEMPLATE.format(
            pin=i, dx=dx, net_num=net_num, net_name=net_name,
            uuid=str(_uuid.uuid4()),
        ))

    block = (
        f'\t(footprint "Header_2.54mm"\n'
        f'\t\t(layer "F.Cu")\n'
        f'\t\t(uuid "{fp_uuid}")\n'
        f'\t\t(at {x0} {y0})\n'
        f'\t\t(property "Reference" "{ref}"\n'
        f'\t\t\t(at 0 -2 0)\n'
        f'\t\t\t(layer "F.Fab")\n'
        f'\t\t\t(hide yes)\n'
        f'\t\t\t(uuid "{_uuid.uuid4()}")\n'
        f'\t\t\t(effects (font (size 1 1) (thickness 0.15)))\n'
        f'\t\t)\n'
        f'\t\t(property "Value" "Samtec TSW-140-07-G-S"\n'
        f'\t\t\t(at 0 2 0)\n'
        f'\t\t\t(layer "F.Fab")\n'
        f'\t\t\t(hide yes)\n'
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
        + "".join(pad_blocks) +
        f'\t\t(embedded_fonts no)\n'
        f'\t)\n'
    )
    return block


# Footprints to delete entirely (bare-pad design-only structures)
DELETE_FOOTPRINTS = {
    "BondPad_DoE",
    "Fiducial_1mm",
    "Probe_1.27mm",
    "TC_Pad_1mm",
    "TLM",
    "VDP",
}


def main() -> int:
    text = PCB.read_text()
    blocks = list(FOOTPRINT_RE.finditer(text))
    print(f"Found {len(blocks)} footprint blocks total")

    # First pass: collect H_N_* and H_S_* pin positions + nets
    h_pins = {"H_N": [], "H_S": []}   # list of (ref_num, x_abs, y_abs, net_num, net_name)
    keep_indices = []
    drop_indices = []

    for i, m in enumerate(blocks):
        block = m.group(1)
        fp = m.group(2)
        ref = extract_ref(block)

        if fp == "Header_2.54mm":
            x, y, _rot = extract_at(block)
            net_num, net_name = extract_pad_net(block)
            side = "H_N" if ref.startswith("H_N_") else "H_S"
            ref_num = int(ref.split("_")[-1])
            h_pins[side].append((ref_num, x, y, net_num, net_name))
            drop_indices.append(i)
        elif fp in DELETE_FOOTPRINTS:
            drop_indices.append(i)
        else:
            keep_indices.append(i)

    print(f"  H_N pins collected: {len(h_pins['H_N'])}")
    print(f"  H_S pins collected: {len(h_pins['H_S'])}")
    print(f"  Bare-pad footprints to delete: " +
          str(sum(1 for i in drop_indices if blocks[i].group(2) in DELETE_FOOTPRINTS)))
    print(f"  Keeping (NTC/R/LED + others): {len(keep_indices)}")

    # Sort pins by ref number
    h_pins["H_N"].sort()
    h_pins["H_S"].sort()

    # Validate Y consistency
    for side in ("H_N", "H_S"):
        ys = {p[2] for p in h_pins[side]}
        if len(ys) > 1:
            print(f"WARNING: {side} pins not on a single Y line: {ys}")
            # Continue anyway — multi-pin footprint will use rot=0 and we'll
            # place pads at absolute X without altering Y per pad. This means
            # if Y varies, the consolidation breaks routing — bail out.
            return 1

    # Build the two consolidated footprints
    new_blocks = []
    if h_pins["H_N"]:
        x0 = min(p[1] for p in h_pins["H_N"])
        y0 = h_pins["H_N"][0][2]
        pins = [(x_abs, n, nm) for _, x_abs, _, n, nm in h_pins["H_N"]]
        new_blocks.append(build_consolidated_header("H_N", x0, y0, pins))
        print(f"  Built H_N footprint at ({x0}, {y0}) with {len(pins)} pads")
    if h_pins["H_S"]:
        x0 = min(p[1] for p in h_pins["H_S"])
        y0 = h_pins["H_S"][0][2]
        pins = [(x_abs, n, nm) for _, x_abs, _, n, nm in h_pins["H_S"]]
        new_blocks.append(build_consolidated_header("H_S", x0, y0, pins))
        print(f"  Built H_S footprint at ({x0}, {y0}) with {len(pins)} pads")

    # Reconstruct file: keep non-dropped blocks, then append new consolidated headers
    out = []
    cursor = 0
    for i, m in enumerate(blocks):
        if i in keep_indices:
            out.append(text[cursor:m.end()])
        else:
            # Drop this block, but preserve any non-block text before it
            out.append(text[cursor:m.start()])
        cursor = m.end()

    # text[cursor:] is everything after the last footprint block (includes graphics,
    # board outline, vias, etc.). We need to inject new headers BEFORE this tail
    # but AFTER the last kept footprint. Easiest: append new headers right after
    # the last kept footprint's end. We've already done that via the out list.
    # So we splice the new_blocks just before text[cursor:] (which is tail content).
    out.append("".join(new_blocks))
    out.append(text[cursor:])

    new_text = "".join(out)

    backup = PCB.with_suffix(".kicad_pcb.pre-consolidate")
    if not backup.exists():
        backup.write_text(text)
    PCB.write_text(new_text)
    print(f"\nBackup: {backup}")
    print(f"Wrote:  {PCB}")
    print(f"Old size: {len(text):>9} bytes")
    print(f"New size: {len(new_text):>9} bytes  ({len(new_text)-len(text):+d})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
