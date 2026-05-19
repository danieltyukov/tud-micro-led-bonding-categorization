#!/usr/bin/env python3
"""
Generate a fab-neutral BOM from the KiCad position file.

Reads new-pcb/fab/tud-microled-v2-pos.csv, classifies every component as
either ASSEMBLED (with MPN) or DNP (do not place), and writes:

    new-pcb/fab/tud-microled-v2-fab-bom.csv

Columns: Reference, Value, Footprint, Quantity, Manufacturer, MPN,
Distributor, DPN, DNP

The MPN-based format is parsed identically by Aisler Beagle and
Eurocircuits assembly. Both auto-source parts from the Manufacturer +
MPN columns.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
POS = REPO / "new-pcb" / "fab" / "tud-microled-v2-pos.csv"
BOM = REPO / "new-pcb" / "fab" / "tud-microled-v2-fab-bom.csv"
# Slim BOM with only assembled parts (no DNP rows). Use this with
# Eurocircuits if their parser ever fails to honor the DNP column.
BOM_ASM = REPO / "new-pcb" / "fab" / "tud-microled-v2-fab-bom-assembly-only.csv"


# Map footprint name → (Value, Manufacturer, MPN, Distributor, DPN, DNP)
# DNP = "Yes" means do-not-populate (customer-bonded LEDs, bare pads)
# DNP = "No"  means the fab assembles this part
FOOTPRINT_TO_PART = {
    # ───── ASSEMBLE these (DNP=No) — verified in Aisler database May 2026 ─────
    "NTC_0402": (
        "NTC 10k 0402 3% AEC-Q200",
        "TDK",
        "NTCG104BH103HT1",
        "Mouser",
        "810-NTCG104BH103HT1",
        "No",
    ),
    "EIS_Load_0603": (
        "100R 0.1% 0603 thin-film 25ppm",
        "Yageo",
        "RT0603BRD07100RL",
        "Mouser",
        "603-RT0603BRD07100RL",
        "No",
    ),
    "Header_2.54mm": (
        "Pin 2.54mm THT 1x40 single-row male gold",
        "Samtec",
        "TSW-140-07-G-S",
        "Mouser",
        "200-TSW14007GS",
        "No",
    ),
    # ───── DNP (customer bonds these in cleanroom) ─────
    # DNP column kept as a plain "Yes" — Eurocircuits' BOM parser only
    # honors the strict string "Yes" and ignores descriptive parentheticals,
    # which previously caused the LEDs to be counted as parts to assemble.
    # Aisler Beagle accepts plain "Yes" as well.
    "D_Wurth_WL-SFCC-0404superflat": (
        "WL-SFCC RGB (DNP — customer bonds in cleanroom)",
        "Wurth",
        "150044M155220",
        "LCSC",
        "C2890605",
        "Yes",
    ),
    # ───── DNP (bare-pad test structures, no component) ─────
    "Probe_1.27mm":  ("Gold probe pad (bare ENIG land, DNP)",  "-", "-", "-", "-", "Yes"),
    "BondPad_DoE":   ("DoE bond pad (bare ENIG land, DNP)",    "-", "-", "-", "-", "Yes"),
    "TLM":           ("TLM finger (bare ENIG land, DNP)",      "-", "-", "-", "-", "Yes"),
    "VDP":           ("VDP contact (bare ENIG land, DNP)",     "-", "-", "-", "-", "Yes"),
    "DaisyChain":    ("DC bond pad (bare ENIG land, DNP)",     "-", "-", "-", "-", "Yes"),
    "TC_Pad_1mm":    ("TC solder pad (bare ENIG land, DNP)",   "-", "-", "-", "-", "Yes"),
    "Fiducial_1mm":  ("Optical fiducial (no component, DNP)",  "-", "-", "-", "-", "Yes"),
    "WL-SFCC_0404":  ("WL-SFCC RGB (DNP — customer bonds in cleanroom)",
                     "Wurth", "150044M155220", "LCSC", "C2890605", "Yes"),
}


def read_pos():
    """Yield (ref, val, footprint, pos_x, pos_y, rot, side) per component."""
    with open(POS) as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield (row["Ref"], row["Val"], row["Package"],
                   row["PosX"], row["PosY"], row["Rot"], row["Side"])


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

    fieldnames = [
        "Reference", "Value", "Footprint", "Quantity",
        "Manufacturer", "MPN", "Distributor", "DPN", "DNP",
    ]

    with open(BOM, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    # Slim BOM — only the assembled rows. Some fab BOM parsers (e.g.
    # Eurocircuits' eC-stencil-mate) misclassify DNP rows even when the
    # DNP column reads "Yes", so a strict assembly-only BOM is the safest
    # upload if assembly cost is coming out wrong.
    asm_rows = [r for r in rows if r["DNP"] == "No"]
    with open(BOM_ASM, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(asm_rows)

    # Print summary
    print(f"Wrote {BOM}")
    print(f"Wrote {BOM_ASM}  (slim, assembled parts only)")
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
