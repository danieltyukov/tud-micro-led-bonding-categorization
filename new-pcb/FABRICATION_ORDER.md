# Fabrication Order — Eurocircuits PCB + Assembly

**Project:** TUD micro-LED v4 · **Designer:** Daniel Tyukov · 5714699 · ET4277 / ET4391
**Board:** 93 × 93 mm · 2-layer FR-4 · 1.55 mm · ENIG · DRC clean (0 violations, 0 unconnected, 0 schematic-parity)

Order path: **Eurocircuits PCB-proto + PCBA-proto, all 3 BOM lines set to "Place on board"** (Eurocircuits sources the parts through their European distributor network, reflows the 5 SMD placements on the SMT line, and hand-solders the 2 THT header strips). The 26 LEDs stay off the PCB entirely (DNP — bonded later at TU Delft EKL under the Tresky T-3000-PRO with a controlled paste profile). The boards arrive fully assembled except for the LEDs.

The PCB's F.Paste gerber has **exactly 10 apertures** — only the 4 NTCs (8 pads) and 1 resistor (2 pads). The 26 LED footprints have no paste apertures so the SMT stencil never deposits paste on the bond pads.

---

## TL;DR

1. Bare PCB: 10 × 93 mm × 93 mm, 2-layer FR-4 1.55 mm, **ENIG**, white silk, green soldermask.
2. PCBA service: upload BOM + pos, all 3 BOM lines set to **"Place on board"**, no stencil add-on needed.
3. Components sourced and assembled by Eurocircuits: 4 × TDK NTC + 1 × Yageo R + 2 × Samtec headers per board × 10 boards.
4. 26 LED footprints are marked DNP (`exclude_from_bom` + `exclude_from_pos_files` in the .kicad_pcb) — Eurocircuits ignores them entirely and the LED pads ship as bare ENIG gold.

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
| Solder paste | F.Paste 10 apertures (4 NTC + 1 R) · B.Paste empty · 26 LED pads paste-free |

---

## Bill of materials — 3 distinct parts, 7 placements per board

All 7 placements are soldered on the Eurocircuits SMT/THT line. Only the 26 LEDs ship as bare ENIG gold lands for EKL bonding.

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

1. **Create a PCB-proto order** — upload `tud-microled-v2-gerbers.zip`. Configure: 2-layer, 1.55 mm FR-4, **ENIG** (chemical Ni/Au), white silk, green mask, 10 boards.
2. **Add PCBA service** to the same order — upload `tud-microled-v2-fab-bom.csv` and `tud-microled-v2-pos.csv`.
3. In the eC-stencil-mate BOM editor, leave every line in the default **"Place on board"** mode. There are exactly 3 lines (Yageo R, Samtec strip, TDK NTC), all marked DNP=No.
4. The 26 LED rows do not appear because `exclude_from_bom` filters them out at the .kicad_pcb layer.
5. Eurocircuits' supplier scanner will resolve the 3 MPNs through Mouser/Farnell. They may show "NI" (No Info) for ~1 working day while an engineer confirms European pricing — normal.
6. Pay; lead time ~7 WD PCB + 5 WD PCBA. Fully-assembled boards (minus the 26 LEDs) arrive in one shipment.

---

## When the boards arrive — sanity-check inspection

1. **26 LED footprints are bare ENIG gold** — no solder, no tin, no paste residue. If there is ANY paste film on the LED bond pads, reject the boards (the bonding step at EKL will fail).
2. **4 NTCs and 1 resistor are reflowed cleanly** — no tombstoning, no bridging, no solder balls.
3. **2 Samtec header strips are soldered into the 64 THT holes** (32 north + 32 south), pins vertical, no missing pins, no cold joints.
4. **Probe pads, TLM/VDP, DoE bond pads, TC pads, fiducials** all bare gold — no tin, no HASL.
5. **Cross-check labels** on the parts against the BOM CSV: TDK NTCG104BH103HT1, Yageo RT0603BRB07100RL, Samtec TSW-140-07-G-S.

If anything is wrong, contact Eurocircuits within their 1-week claim window — they re-fab without quibble.
