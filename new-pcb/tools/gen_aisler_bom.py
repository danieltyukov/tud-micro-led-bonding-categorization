#!/usr/bin/env python3
"""
Generate an Aisler-Beagle-ready BOM from the KiCad position file.

Reads new-pcb/fab/tud-microled-v2-pos.csv, classifies every component as
either ASSEMBLED (with MPN) or DNP (do not place), and writes:

    new-pcb/fab/tud-microled-v2-aisler-bom.csv

Columns: Reference, Value, Footprint, Quantity, Manufacturer, MPN,
Distributor, DPN, DNP

Aisler's Beagle parses this format; the Manufacturer + MPN columns drive
their auto-sourcing.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
POS = REPO / "new-pcb" / "fab" / "tud-microled-v2-pos.csv"
BOM = REPO / "new-pcb" / "fab" / "tud-microled-v2-aisler-bom.csv"


# Map footprint name → (Value, Manufacturer, MPN, Distributor, DPN, DNP)
# DNP = "Yes" means do-not-populate (customer-bonded LEDs, bare pads)
# DNP = "No"  means Aisler must assemble this part
FOOTPRINT_TO_PART = {
    # ───── ASSEMBLE these (DNP=No) ─────
    "NTC_0402": (
        "NTC 10k 0402 B=3380K",
        "Murata",
        "NCP15XH103J03RC",
        "LCSC",
        "C5316",
        "No",
    ),
    "EIS_Load_0603": (
        "100R 0.1% 0603 thin-film",
        "Vishay Dale",
        "TNPW0603100RBEEA",
        "DigiKey",
        "541-100ARTR-ND",
        "No",
    ),
    "Header_2.54mm": (
        "Pin 2.54mm THT",
        "Wurth",
        "61301021121",
        "LCSC",
        "C124378",
        "No",
    ),
    # ───── DNP (customer bonds these in cleanroom) ─────
    "D_Wurth_WL-SFCC-0404superflat": (
        "WL-SFCC RGB",
        "Wurth",
        "150044M155220",
        "LCSC",
        "C2890605",
        "Yes  (customer bonds in cleanroom)",
    ),
    # ───── DNP (bare-pad test structures, no component) ─────
    "Probe_1.27mm":  ("Gold probe pad",  "-", "-", "-", "-", "Yes  (bare ENIG land)"),
    "BondPad_DoE":   ("DoE bond pad",    "-", "-", "-", "-", "Yes  (bare ENIG land)"),
    "TLM":           ("TLM finger",      "-", "-", "-", "-", "Yes  (bare ENIG land)"),
    "VDP":           ("VDP contact",     "-", "-", "-", "-", "Yes  (bare ENIG land)"),
    "DaisyChain":    ("DC bond pad",     "-", "-", "-", "-", "Yes  (bare ENIG land)"),
    "TC_Pad_1mm":    ("TC solder pad",   "-", "-", "-", "-", "Yes  (bare ENIG land)"),
    "Fiducial_1mm":  ("Optical fiducial","-", "-", "-", "-", "Yes  (no component)"),
    "WL-SFCC_0404":  ("WL-SFCC RGB",     "Wurth", "150044M155220", "LCSC", "C2890605",
                     "Yes  (customer bonds in cleanroom)"),
}


def read_pos():
    """Yield (ref, val, footprint, pos_x, pos_y, rot, side) per component."""
    with open(POS) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 7:
                continue
            # KiCad pos format: Ref Val Package PosX PosY Rot Side
            yield (parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6])


def main() -> int:
    if not POS.exists():
        print(f"ERROR: pos file {POS} not found — run kicad-cli pcb export pos first")
        return 1

    # Group by footprint → list of refs
    grouped: dict[str, list[str]] = defaultdict(list)
    unknown_footprints: set[str] = set()
    for ref, val, fp, *_ in read_pos():
        if fp not in FOOTPRINT_TO_PART:
            unknown_footprints.add(fp)
            continue
        grouped[fp].append(ref)

    if unknown_footprints:
        print(f"⚠ WARNING: unknown footprints (won't appear in BOM): {sorted(unknown_footprints)}")

    rows = []
    for fp, refs in sorted(grouped.items()):
        val, mfr, mpn, dist, dpn, dnp = FOOTPRINT_TO_PART[fp]
        rows.append({
            "Reference":  ",".join(sorted(refs, key=_natural_key)),
            "Value":      val,
            "Footprint":  fp,
            "Quantity":   len(refs),
            "Manufacturer": mfr,
            "MPN":        mpn,
            "Distributor": dist,
            "DPN":        dpn,
            "DNP":        dnp,
        })

    # Sort: assembled parts first (DNP=No), then DNP parts
    rows.sort(key=lambda r: (r["DNP"].startswith("Yes"), r["Footprint"]))

    with open(BOM, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "Reference", "Value", "Footprint", "Quantity",
            "Manufacturer", "MPN", "Distributor", "DPN", "DNP",
        ])
        w.writeheader()
        w.writerows(rows)

    # Print summary
    print(f"Wrote {BOM}")
    print(f"\n{'='*72}")
    print(f"{'BOM SUMMARY':^72}")
    print(f"{'='*72}\n")

    assembled = [r for r in rows if r["DNP"] == "No"]
    dnp = [r for r in rows if r["DNP"] != "No"]

    print(f"ASSEMBLED by fab ({sum(int(r['Quantity']) for r in assembled)} parts total):")
    for r in assembled:
        print(f"  {r['Quantity']:>3}× {r['Manufacturer']:<12} {r['MPN']:<22} ({r['Value']})")
        print(f"      → {r['Reference']}")
    print(f"\nDNP — customer bonds / bare pads ({sum(int(r['Quantity']) for r in dnp)} entries):")
    for r in dnp:
        first_refs = r["Reference"].split(",")[:3]
        print(f"  {r['Quantity']:>3}× {r['Footprint']:<33} → {','.join(first_refs)}{'...' if int(r['Quantity'])>3 else ''}")

    return 0


def _natural_key(ref: str):
    """Sort H_N_2 before H_N_10 numerically."""
    import re
    parts = re.split(r'(\d+)', ref)
    return [int(p) if p.isdigit() else p for p in parts]


if __name__ == "__main__":
    raise SystemExit(main())
