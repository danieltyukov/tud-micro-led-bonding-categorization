#!/usr/bin/env python3
"""Extract H_N_* and H_S_* footprint positions + nets from the .kicad_pcb."""

import re
from pathlib import Path

PCB = Path(__file__).resolve().parents[2] / "new-pcb" / "tud-microled-v2.kicad_pcb"

text = PCB.read_text()

# Match a Header_2.54mm footprint block with its position and net
fp_re = re.compile(
    r'\(footprint "Header_2\.54mm".*?'
    r'\(at ([\-0-9.]+) ([\-0-9.]+)(?: ([\-0-9.]+))?\).*?'
    r'\(property "Reference" "(H_[NS]_\d+)".*?'
    r'\(pad "1" thru_hole .*?'
    r'\(net (\d+) "([^"]+)"\)',
    re.DOTALL,
)

rows = []
for m in fp_re.finditer(text):
    x, y, rot, ref, net_n, net_name = m.groups()
    rows.append((ref, float(x), float(y), float(rot or 0), int(net_n), net_name))

rows.sort(key=lambda r: (r[0].startswith("H_S"), int(r[0].split("_")[-1])))

print(f"Found {len(rows)} Header_2.54mm footprints\n")
print(f"{'Ref':<8} {'X':>8} {'Y':>8} {'Rot':>6} {'Net#':>5}  Net name")
for ref, x, y, rot, net_n, net_name in rows:
    print(f"{ref:<8} {x:>8.2f} {y:>8.2f} {rot:>6.0f} {net_n:>5}  {net_name}")

# Show clustering by Y (north should share one Y, south another)
ys_n = sorted({r[2] for r in rows if r[0].startswith("H_N")})
ys_s = sorted({r[2] for r in rows if r[0].startswith("H_S")})
xs_n_step = sorted({r[1] for r in rows if r[0].startswith("H_N")})
xs_s_step = sorted({r[1] for r in rows if r[0].startswith("H_S")})

print(f"\nH_N rows: Y unique = {ys_n}")
print(f"H_S rows: Y unique = {ys_s}")
if len(xs_n_step) > 1:
    print(f"H_N X step: {xs_n_step[1] - xs_n_step[0]:.3f} mm (first two)")
if len(xs_s_step) > 1:
    print(f"H_S X step: {xs_s_step[1] - xs_s_step[0]:.3f} mm (first two)")
