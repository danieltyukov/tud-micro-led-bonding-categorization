# new-pcb — v2 Micro-LED Bonding Characterization PCB

**Status: fab-ready.** DRC clean (0 violations, 0 unconnected, 0 schematic-parity). Workflow: *Eurocircuits PCB + PCBA-proto*, all 3 BOM lines set to "Place on board" so the 4 NTC + 1 R + 2 header strips are reflowed / soldered by Eurocircuits. F.Paste has 10 apertures (NTC + R only); the 26 LED footprints stay paste-free and ship as bare ENIG gold for cleanroom bonding at TU Delft EKL.

## Quick links

- **Order from Eurocircuits** → `FABRICATION_ORDER.md`
- **As-built design notes** → `V2_DESIGN_NOTES.md`
- **Original spec** → `PCB_DESIGN_PLAN.md`
- **Electrical characterization workflow** → `ELECTRICAL_CHARACTERIZATION.md`
- **What this v2 contributes vs ECTC 2025** → `PUBLICATION_CONTRIBUTION.md`

## Folder layout

```
new-pcb/
├── tud-microled-v2.kicad_pro     KiCad 9.0.8 project
├── tud-microled-v2.kicad_pcb     PCB layout (130 footprints, DRC clean)
├── tud-microled-v2.kicad_sch     single-sheet A2 schematic
├── PCB_DESIGN_PLAN.md            original design spec
├── V2_DESIGN_NOTES.md            as-built notes
├── VERIFICATION_v4.md            electrical-characterization verification
├── ELECTRICAL_CHARACTERIZATION.md measurement plan + lab tools
├── FABRICATION_ORDER.md          Eurocircuits "Place loose" order checklist
├── PUBLICATION_CONTRIBUTION.md   v2 contributions vs ECTC 2025
├── library/                      Würth WL-SFCC LED symbol/footprint/3D
├── tools/                        Python helpers (PCB patcher, BOM generator)
└── fab/                          gerbers, BOM, pos, PDFs, STEP, top.png
    ├── tud-microled-v2-fab-bom.csv          BOM with TDK + Yageo + Samtec MPNs (Mouser PNs included)
    ├── tud-microled-v2-fab-bom-assembly-only.csv  slim BOM (the 3 assembled rows only)
    ├── tud-microled-v2-pos.csv               7 placements
    ├── tud-microled-v2-top.pdf / -bot.pdf    visual review
    ├── tud-microled-v2-gerbers.zip           26-file gerber + drill bundle
    ├── tud-microled-v2.step                  3D model
    └── preview/top.png                       1600×1600 raytraced render
```

## Design summary

| | |
|---|---|
| Board | 93 × 93 mm, 2-layer FR-4, 1.55 mm |
| Finish | ENIG (Ni 4 µm / Au 0.075 µm) |
| Min track / clearance | 0.20 / 0.30 mm (Eurocircuits Class 4 minimum is 0.15 mm) |
| Min drill / annular ring | 0.30 / 0.15 mm |
| Footprints on board | **130** (1 R + 4 NTC + 2 multi-pin headers + 26 LEDs DNP) |
| Distinct components | **3** (Yageo R, TDK NTC, Samtec header) |
| Placements per board (assembled) | **7** (1 R + 4 NTC + 2 header strips) |
| LED bonding | 26 × Würth WL-SFCC RGB at customer cleanroom (Tresky T-3000-PRO) |
| Solder-paste apertures | **10** on F.Paste (4 NTC × 2 + 1 R × 2). B.Paste empty. 26 LED footprints intentionally paste-free. |

## Bill of materials

3 distinct part numbers — all stocked at Mouser EU (1-day NL delivery) and resolvable through Eurocircuits' supplier scanner:

| Ref(s) | Manufacturer | MPN | Mouser PN |
|---|---|---|---|
| R_EIS_LOAD | Yageo | RT0603BRB07100RL | 603-RT0603BRB07100RL |
| H_N + H_S | Samtec | TSW-140-07-G-S | 200-TSW14007GS |
| TH1..TH4 | TDK | NTCG104BH103HT1 | 810-NTCG104BH103HT1 |

## Quick start

1. Open `tud-microled-v2.kicad_pro` in KiCad 9.0 or newer.
2. Confirm `WE_3DMODEL_DIR` is set in **Preferences → Configure Paths** (see `library/README.md`).
3. Run checks: `kicad-cli pcb drc tud-microled-v2.kicad_pcb` and `kicad-cli sch erc tud-microled-v2.kicad_sch` — both should report 0 violations.
4. Regenerate fab outputs after any PCB edit:
   - `kicad-cli pcb export gerbers --output fab/gerbers/ tud-microled-v2.kicad_pcb`
   - `kicad-cli pcb export drill --output fab/gerbers/ tud-microled-v2.kicad_pcb`
   - `kicad-cli pcb export pos --format csv --units mm --use-drill-file-origin --output fab/tud-microled-v2-pos.csv tud-microled-v2.kicad_pcb`
   - `kicad-cli pcb export pdf --layers F.Cu,F.Silkscreen,F.Mask,Edge.Cuts -o fab/tud-microled-v2-top.pdf tud-microled-v2.kicad_pcb`
   - `kicad-cli pcb render --side top --width 1600 --height 1600 --quality high --output fab/preview/top.png tud-microled-v2.kicad_pcb`
   - `python3 tools/gen_fab_bom.py` to refresh the BOM CSV
   - `(cd fab/gerbers && zip -q ../tud-microled-v2-gerbers.zip *)` to rebundle for Eurocircuits

## tools/ scripts

| Script | Purpose |
|---|---|
| `gen_fab_bom.py` | Reads `fab/tud-microled-v2-pos.csv`, emits `tud-microled-v2-fab-bom.csv` + slim variant |
| `patch_aisler_mpns.py` | Adds Manufacturer + MPN custom fields to each footprint so any fab auto-detects them |
| `consolidate_pcb.py` | One-time refactor that collapsed 64 single-pin headers into 2 multi-pin strips and deleted the 123 bare-pad design-only footprints |
| `strip_all_paste.py` | Removes F.Paste / B.Paste from every pad in the design (used for the loose-components workflow) |
| `clean_dangling.py` | Removes orphan tracks/vias left over by `consolidate_pcb.py` |
| `unify_values.py` | Sets the `Value` field of every footprint to its MPN so Aisler/EC Grouped views collapse them properly |
| `inspect_headers.py` | Read-only debug helper |
