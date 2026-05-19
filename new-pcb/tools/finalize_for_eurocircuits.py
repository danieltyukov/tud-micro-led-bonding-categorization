#!/usr/bin/env python3
"""
Finalize the .kicad_pcb for the Eurocircuits "Place loose" order:

1. Swap the Yageo resistor MPN from RT0603BRD07100RL (out of stock on Mouser EU)
   to RT0603BRB07100RL (15,867 in stock, 10 ppm/°C TC — better than the original
   25 ppm/°C).
2. Inject (model ...) references into every footprint so the KiCad 3D viewer
   actually displays component bodies. Uses KiCad's standard ${KICAD9_3DMODEL_DIR}
   library plus the local Würth WL-SFCC STEP files we already vendored.

After running:
   - 0603 resistor → R_0603_1608Metric.step
   - 0402 NTC      → R_0402_1005Metric.step  (NTC body is identical to 0402 R)
   - 1×32 header   → PinHeader_1x32_P2.54mm_Vertical.step (per strip)
   - WL-SFCC LED   → ${WE_3DMODEL_DIR}/LED_SMD_Wurth.3dshapes/D_Wurth_WL-SFCC-0404superflat.step
   - bare-pad footprints get no 3D model (they're flat lands)
"""

from __future__ import annotations

import re
import uuid as _uuid
from pathlib import Path

PCB = Path(__file__).resolve().parents[2] / "new-pcb" / "tud-microled-v2.kicad_pcb"


# Footprint name → 3D model spec (path, scale-rotate-offset)
MODELS = {
    "EIS_Load_0603": (
        "${KICAD9_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0603_1608Metric.step",
        # Resistor body sits over the footprint origin
    ),
    "NTC_0402": (
        "${KICAD9_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step",
    ),
    "Header_2.54mm": (
        "${KICAD9_3DMODEL_DIR}/Connector_PinHeader_2.54mm.3dshapes/PinHeader_1x32_P2.54mm_Vertical.step",
    ),
    "WL-SFCC_0404": (
        "${WE_3DMODEL_DIR}/LED_SMD_Wurth.3dshapes/D_Wurth_WL-SFCC-0404superflat.step",
    ),
}


MODEL_BLOCK = (
    '\t\t(model "{path}"\n'
    '\t\t\t(offset (xyz 0 0 0))\n'
    '\t\t\t(scale (xyz 1 1 1))\n'
    '\t\t\t(rotate (xyz 0 0 0))\n'
    '\t\t)\n'
)


FOOTPRINT_RE = re.compile(
    r'(\t\(footprint "([^"]+)"\n.*?\n\t\)\n)',
    re.DOTALL,
)


def patch(block: str, fp_name: str) -> tuple[str, str]:
    # Step 1 — Yageo MPN swap on EIS_Load_0603 only
    if fp_name == "EIS_Load_0603":
        block = block.replace('"RT0603BRD07100RL"', '"RT0603BRB07100RL"')

    # Step 2 — insert (model ...) just before the closing paren of this footprint,
    # unless one already exists or the footprint type has no model assigned.
    if fp_name not in MODELS:
        return block, "no-model"

    if '(model "' in block:
        return block, "already-has-model"

    model_path = MODELS[fp_name][0]
    new_model = MODEL_BLOCK.format(path=model_path)

    # Insert before the last `\t)\n` of the footprint block.
    # The block ends with `\t\t(embedded_fonts no)\n\t)\n` or just `\n\t)\n`.
    closing = "\t)\n"
    idx = block.rfind(closing)
    if idx < 0:
        return block, "no-anchor"
    patched = block[:idx] + new_model + block[idx:]
    return patched, "+model"


def main() -> int:
    text = PCB.read_text()
    out = []
    cursor = 0
    stats: dict[str, int] = {}

    for m in FOOTPRINT_RE.finditer(text):
        out.append(text[cursor:m.start()])
        block = m.group(1)
        fp_name = m.group(2)
        new_block, action = patch(block, fp_name)
        out.append(new_block)
        key = f"{action} ({fp_name})" if action != "no-model" else "no-model (bare-pad)"
        stats[key] = stats.get(key, 0) + 1
        cursor = m.end()
    out.append(text[cursor:])
    new_text = "".join(out)

    if new_text == text:
        print("No changes.")
        return 0

    PCB.write_text(new_text)
    print(f"Wrote {PCB}")
    for k, v in sorted(stats.items()):
        print(f"  {v:>4}  {k}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
