# Fabrication Order — Eurocircuits "Place loose"

**Project:** TUD micro-LED v4 · **Designer:** Daniel Tyukov · 5714699 · ET4277 / ET4391
**Board:** 93 × 93 mm · 2-layer FR-4 · 1.55 mm · ENIG · DRC clean (0 violations, 0 unconnected, 0 schematic-parity)

Order path: **Eurocircuits PCB-proto + PCBA-proto with every line set to "Place loose"** — Eurocircuits sources every component through their European distributor network and ships them bagged-and-labelled alongside the bare PCBs. Nothing is soldered. The 26 LEDs stay off the PCB entirely (bonded later at TU Delft EKL under the Tresky T-3000-PRO with a controlled paste profile). The 5 SMT placements + 64 header pins are hand-soldered at EKL with solder wire and flux during the same cleanroom session.

The PCB has **no solder-paste apertures anywhere** (F.Paste and B.Paste gerbers are empty) — that's deliberate so that no fab ever pre-tins the LED bond pads.

---

## TL;DR

1. Bare PCB: 10 × 93 mm × 93 mm, 2-layer FR-4 1.55 mm, **ENIG**, white silk, green soldermask.
2. PCBA service: upload BOM + pos, set every line to **"Place loose"**, no stencil.
3. Components sourced and shipped loose by Eurocircuits: 4 × TDK NTC + 1 × Yageo R + 20 × Samtec headers (2 strips per board × 10 boards).
4. 26 LED footprints are marked DNP (`exclude_from_bom` + `exclude_from_pos_files` in the .kicad_pcb) — Eurocircuits ignores them entirely.

---

## Spec

| Field | Value |
|---|---|
| Layers | 2 |
| Dimensions | **93 × 93 mm** (fits Tresky T-3000-PRO die-bonder with 1 mm margin to its 95 × 95 mm envelope) |
| Thickness | 1.55 mm |
| Quantity | **10 boards** |
| Surface finish | **ENIG (Gold)** — Ni 4 µm + Au 0.075 µm RoHS — mandatory for LED bonding and probe-pad ohmic contact |
| Outer copper | 35 µm (1 oz) |
| Solder mask | Green |
| Silk | White |
| Min clearance / track | 0.30 / 0.20 mm (design); clears Eurocircuits Class 4 (0.15 mm minimum) with 2× headroom |
| Min drill / annular ring | 0.30 / 0.15 mm |
| Solder paste | **none** — F.Paste and B.Paste gerbers are intentionally empty |

---

## Bill of materials — 3 distinct parts, 7 placements per board

All parts ship loose; you hand-solder at EKL.

| Ref(s) | Footprint | Manufacturer | MPN | Mouser part # | Qty per board | Qty for 10 boards |
|---|---|---|---|---|---:|---:|
| **R_EIS_LOAD** | 0603 thin-film | Yageo | `RT0603BRB07100RL` | 603-RT0603BRB07100RL | 1 | 10 |
| **H_N** + **H_S** | 1×32 THT (cut from 1×40) | Samtec | `TSW-140-07-G-S` | 200-TSW14007GS | 2 strips | 20 strips |
| **TH1, TH2, TH3, TH4** | 0402 NTC | TDK | `NTCG104BH103HT1` | 810-NTCG104BH103HT1 | 4 | 40 |

Total assembled placements per board: **7** (1 × R + 2 × header strips + 4 × NTC).

### Do-Not-Populate (LEDs — customer bonds at EKL)

| Ref pattern | Qty | Component |
|---|---:|---|
| `D1..D8` | 8 | Würth WL-SFCC RGB LED (`150044M155220`) |
| `DCL6_L1..L6` | 6 | same |
| `DCL12_L1..L12` | 12 | same |

**Total: 26 LEDs per board, customer-supplied, customer-bonded.** The `.kicad_pcb` flags each WL-SFCC_0404 footprint with `exclude_from_bom` + `exclude_from_pos_files` so Eurocircuits' tooling treats them as bare gold lands.

---

## Files to upload

| File | Where in Eurocircuits |
|---|---|
| `fab/tud-microled-v2-gerbers.zip` | PCB visualiser (auto-extracts gerbers + drill) |
| `fab/tud-microled-v2-fab-bom.csv` (or the slim `-assembly-only.csv` variant) | eC-stencil-mate → BOM |
| `fab/tud-microled-v2-pos.csv` | eC-stencil-mate → Pick-and-Place |
| `fab/tud-microled-v2-top.pdf` / `-bot.pdf` | Visual review |
| `fab/tud-microled-v2.step` | Optional 3D verification |

---

## Step-by-step at eurocircuits.com

1. **Create a PCB-proto order** — upload `tud-microled-v2-gerbers.zip`. Configure: 2-layer, 1.55 mm FR-4, ENIG, white silk, green mask, 10 boards.
2. **Add PCBA service** to the same order — upload `tud-microled-v2-fab-bom.csv` and `tud-microled-v2-pos.csv`.
3. In the eC-stencil-mate BOM editor, **set every line's placement mode to "Place loose"**. There are exactly 3 lines (Yageo R, Samtec strip, TDK NTC), all marked DNP=No.
4. The 26 LED rows do not appear because `exclude_from_bom` filters them out at the .kicad_pcb layer.
5. Eurocircuits' supplier scanner will resolve the 3 MPNs through Mouser/Farnell. They may show "NI" (No Info) for ~1 working day while an engineer confirms European pricing — normal.
6. Pay; lead time ~5-7 working days. Both PCBs and the loose-parts bag arrive in one shipment.

---

## When the boards arrive — sanity-check inspection

1. **All 10 boards have gold pads everywhere** — 26 LED footprints, 4 NTC pads, 1 R pad, every probe annular ring, every test-pad land. No tin, no HASL.
2. **No solder paste residue** anywhere. If there's any paste film on the LED footprints, reject the boards.
3. **64 header holes (32 north + 32 south)** are clean, plated, and unobstructed.
4. **The parts bag contains:** 40 × TDK NTC (taped strip ok), 10 × Yageo R, 20 × Samtec 1×40 strip (you'll cut each to 32 pins on the bench).
5. **Cross-check MPNs printed on the parts packaging** against the BOM CSV.

If anything is wrong, contact Eurocircuits within their 1-week claim window — they re-fab without quibble.
