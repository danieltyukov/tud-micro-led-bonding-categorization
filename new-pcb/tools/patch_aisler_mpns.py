#!/usr/bin/env python3
"""
Patch tud-microled-v2.kicad_pcb so Aisler auto-assigns parts on upload.

For each assembled footprint type, inject "Manufacturer" + "MPN" properties
matching parts actually stocked in Aisler's database (verified via In-Depth
Search in the BOM editor, May 2026).

For each DNP / bare-pad footprint type, add exclude_from_bom +
exclude_from_pos_files modifiers to the (attr ...) line so Aisler doesn't
list them as components needing assignment.
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PCB = REPO / "new-pcb" / "tud-microled-v2.kicad_pcb"


# Footprint → (Manufacturer, MPN) — assembled parts that Aisler stocks
ASSEMBLY_MPNS = {
    "NTC_0402":      ("TDK",    "NTCG104BH103HT1"),    # 10 kΩ NTC 0402, AEC-Q200
    "EIS_Load_0603": ("Yageo",  "RT0603BRD07100RL"),   # 100 Ω 0.1% thin-film 0603
    "Header_2.54mm": ("Samtec", "TSW-140-07-G-S"),     # 1×40 2.54 mm gold THT
}

# Footprints that should be DNP / excluded from Aisler's parts list
DNP_FOOTPRINTS = {
    "WL-SFCC_0404",   # 26 LEDs — customer bonds in cleanroom
    "BondPad_DoE",    # 36 bare gold pads
    "Fiducial_1mm",   # 4 optical fiducials
    "Probe_1.27mm",   # 46 probe pads
    "TC_Pad_1mm",     # 4 thermocouple pads
    "TLM",            # 3 TLM structures
    "VDP",            # 4 VDP contacts
}


PROPERTY_TEMPLATE = '''\t\t(property "{name}" "{value}"
\t\t\t(at 0 0 0)
\t\t\t(unlocked yes)
\t\t\t(layer "F.Fab")
\t\t\t(hide yes)
\t\t\t(uuid "{uuid}")
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t(thickness 0.15)
\t\t\t\t)
\t\t\t)
\t\t)
'''


def make_property(name: str, value: str) -> str:
    return PROPERTY_TEMPLATE.format(
        name=name, value=value, uuid=str(uuid.uuid4())
    )


# Match a full footprint block.
# A footprint starts with `\t(footprint "..."` at indent 1 and ends at the
# matching closing paren at indent 1 (i.e. `\t)`).
FOOTPRINT_RE = re.compile(
    r'(\t\(footprint "([^"]+)"\n.*?\n\t\)\n)',
    re.DOTALL,
)


def patch_footprint(block: str, fp_name: str) -> tuple[str, str]:
    """Return (patched_block, action_label)."""
    if fp_name in ASSEMBLY_MPNS:
        mfr, mpn = ASSEMBLY_MPNS[fp_name]
        # Skip if Manufacturer property already exists
        if '(property "Manufacturer"' in block:
            return block, "already-tagged"

        # Inject Manufacturer + MPN after the last existing top-level property
        # (immediately before `(attr ...)` or first `(pad ...)` / `(fp_*)` line)
        insertion = make_property("Manufacturer", mfr) + make_property("MPN", mpn)

        # Find a good insertion point: after the "Description" property's closing paren
        # OR before the (attr ...) line, whichever comes first
        m = re.search(r'(\t\t\(property "Description".*?\n\t\t\)\n)', block, re.DOTALL)
        if m:
            new = block[:m.end()] + insertion + block[m.end():]
            return new, f"+MPN ({mfr} {mpn})"
        # Fallback: insert before (attr
        m = re.search(r'(\t\t\(attr )', block)
        if m:
            new = block[:m.start()] + insertion + block[m.start():]
            return new, f"+MPN ({mfr} {mpn})"
        return block, "skip-no-anchor"

    if fp_name in DNP_FOOTPRINTS:
        # Add exclude_from_bom + exclude_from_pos_files to (attr ...) if not present
        def repl(m: re.Match) -> str:
            inner = m.group(1)
            needed = []
            if "exclude_from_bom" not in inner:
                needed.append("exclude_from_bom")
            if "exclude_from_pos_files" not in inner:
                needed.append("exclude_from_pos_files")
            if not needed:
                return m.group(0)
            return f"(attr {inner.strip()} " + " ".join(needed) + ")"

        new = re.sub(r'\(attr ([^)]+)\)', repl, block)
        if new == block:
            return block, "already-dnp"
        return new, "+DNP"

    return block, "unchanged"


def main() -> int:
    if not PCB.exists():
        print(f"ERROR: {PCB} not found")
        return 1

    text = PCB.read_text()
    blocks = list(FOOTPRINT_RE.finditer(text))
    print(f"Found {len(blocks)} footprint blocks")

    stats: dict[str, int] = {}
    new_parts: list[str] = []
    cursor = 0
    out: list[str] = []

    for m in blocks:
        start, end = m.span()
        out.append(text[cursor:start])
        block = m.group(1)
        fp_name = m.group(2)
        patched, action = patch_footprint(block, fp_name)
        out.append(patched)
        stats[action] = stats.get(action, 0) + 1
        cursor = end

    out.append(text[cursor:])
    new_text = "".join(out)

    if new_text == text:
        print("No changes needed.")
        return 0

    backup = PCB.with_suffix(".kicad_pcb.pre-aisler-patch")
    backup.write_text(text)
    PCB.write_text(new_text)

    print(f"\nBackup written: {backup}")
    print(f"Patched file:   {PCB}")
    print("\nActions taken:")
    for action, count in sorted(stats.items()):
        print(f"  {count:>4}  {action}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
