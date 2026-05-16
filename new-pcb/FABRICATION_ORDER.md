# Fabrication & Assembly Order — Aisler

**Project:** TUD micro-LED v4.0  ·  **Designer:** Daniel Tyukov · 5714699 · ET4277 / ET4391
**Board:** 93 × 93 mm · 2-layer · 1.6 mm FR-4 · ENIG finish · DRC clean (0 violations)
**Supplier:** [Aisler](https://aisler.net) (Aachen, DE / Eindhoven, NL — EU fab + assembly)

---

## TL;DR

1. Drag-drop `new-pcb/tud-microled-v2.kicad_pcb` onto Aisler "Start Project".
2. ENIG (Gold) finish, 2 layers, 1.55 mm thickness, 3 boards.
3. Add **Beagle assembly** with the BOM table below.
4. Mark **D1–D8 + DCL6_L1..6 + DCL12_L1..12 (26 LEDs)** as **Do Not Assemble** — you bond them in the cleanroom.
5. Everything else (NTCs, headers, load resistor) is pre-assembled by Aisler.

---

## Bare-PCB configuration

| Field | Value | Why |
|---|---|---|
| File format | KiCad PCB (`.kicad_pcb`) — drag-drop natively, no Gerber zip needed | Aisler reads KiCad directly; cleaner than re-exporting |
| Layers | 2 | matches design |
| Dimensions | **93 × 93 mm** (auto-detected from Edge.Cuts) | Fits the Tresky T-3000-PRO die-bonder envelope (≤ 95 × 95 mm) with 1 mm margin |
| Thickness | 1.55 mm (Aisler standard) | Effective FR-4 = 1.5 mm, matches design |
| Quantity | 3 boards (Aisler bundles in 3s) | 1 trial + 1 real + 1 spare per solder-paste variant |
| **Surface finish** | **ENIG (Gold)** — Ni 4 µm + Au 0.075 µm RoHS | Mandatory; every probe pad must be gold for reliable contact + bonding |
| Outer copper | 35 µm (1 oz) | default |
| Solder mask | Green (or matte black for ~€5 surcharge) | cosmetic |
| Silk | White | matches design |
| Min clearance | 0.15 mm | design rule (met) |
| Min track | 0.20 mm | design rule (met) |

---

## Bill of materials — pre-assembled by Aisler

**Total: 4 SMD + 64 THT + 1 SMD load = 69 placements per board.** All except the 26 LEDs are factory-soldered.

### Pre-assembled (Aisler Beagle)

| Designator(s) | Qty | Footprint | Recommended part | Notes |
|---|---:|---|---|---|
| **TH1, TH2, TH3, TH4** | 4 | 0402 SMD (NTC_0402 in board lib) | **Murata `NCP15XH103J03RC`** (10 kΩ ±5 %, B25/85 = 3380 K) — LCSC C5316 | For V_F-TSP thermal sensing — see `docs/datasheets/README.md` |
| **EIS_LOAD** (across PP_EIS_LOAD_A & PP_EIS_LOAD_B) | 1 | 0603 SMD thin-film | **Vishay Dale `TNPW0603100RBEEA`** (100 Ω, ±0.1 %, 25 ppm/°C, thin-film) — DigiKey 541-1830-1-ND | Reference resistor for LCR meter calibration |
| **H_N_1 .. H_N_32** | 32 | Pin header 2.54 mm, THT, vertical, single row | **Würth `61301021121`** (WR-PHD 1×40 male, cut to 32 pins) — LCSC C124378 | North header |
| **H_S_1 .. H_S_32** | 32 | Pin header 2.54 mm, THT, vertical, single row | Same as above (cut from second 1×40 strip) | South header |

### Do Not Assemble (DNP) — customer bonds in cleanroom

| Designator(s) | Qty | Footprint | Component |
|---|---:|---|---|
| **D1, D2, D3, D4, D5, D6, D7, D8** | 8 | WL-SFCC_0404 (4 SMD pads at corners) | Würth `150044M155220` WL-SFCC RGB LED |
| **DCL6_L1 .. DCL6_L6** | 6 | Same | Same |
| **DCL12_L1 .. DCL12_L12** | 12 | Same | Same |

**Total LEDs: 26 per board.** All are research-experiment subjects bonded in TU Delft cleanroom under controlled paste/reflow/bonder conditions (Tresky T-3000-PRO, paste varies per study, reflow profile per Würth datasheet §6 or paper §III-A).

### Bare gold lands (no component, intentional)

These are F.Cu probe pads with ENIG finish, not part of the BOM:

| Designator pattern | Qty | Purpose |
|---|---:|---|
| `BP_R*_C*` | 36 | DoE bond-pad array (6×6) — for future dummy-die bond studies |
| `PP_*` (probe pads on TLM/VDP/DC/LED) | ~70 | Tier-1 manual probe access |
| `TLM_*`, `VDP_*` | ~30 | TLM/VDP test structure fingers |
| `TC1..TC4` | 4 | Thermocouple-wire solder pads for in-situ reflow temp |
| `PP_GND1, PP_GND2` | 2 | GND access at corners |
| `PP_EIS_OPEN_A/B, PP_EIS_SHORT_A/B, PP_EIS_LOAD_A/B` | 6 | EIS calibration pads (LOAD has the 100 Ω resistor across A↔B) |
| `FID1..FID4` | 4 | Optical fiducials for Aisler P&P |

---

## DNP — Critical instruction for Aisler

Write in the Aisler order notes (Beagle UI free-text field):

> **DO NOT POPULATE THE LEDs.** The 26 WL-SFCC LED footprints (D1-D8, DCL6_L1..6, DCL12_L1..12, all using footprint `D_Wurth_WL-SFCC-0404superflat`) are the research subject and will be bonded by the customer in the TU Delft cleanroom under controlled conditions (paste, reflow profile, die-bonder). Please ONLY assemble: 4 × NTC at TH1-4, 1 × 100Ω 0.1% thin-film 0603 at EIS_LOAD, and 64 × pin header pins at H_N_* and H_S_*.

---

## Files to upload

All in `new-pcb/fab/`:

| File | Where in Aisler UI |
|---|---|
| `../tud-microled-v2.kicad_pcb` (the source file at `new-pcb/`) | "Start Project" — drag-drop |
| `tud-microled-v2-bom.csv` | Beagle assembly — BOM |
| `tud-microled-v2-pos.csv` | Beagle assembly — Pick-and-Place CSV |
| `tud-microled-v2-top.pdf` | Visual review |
| `tud-microled-v2-bot.pdf` | Visual review |
| `tud-microled-v2.step` | (optional) 3D model |

Files you can ignore:
- `tud-microled-v2-gerbers.zip` — Aisler reads KiCad natively; only needed if falling back to Eurocircuits.

---

## Cost estimate

| Item | Approx € |
|---|---:|
| 3 × bare PCB (93 × 93 mm, 2-layer, ENIG, white silk) | 50-60 |
| Beagle assembly setup fee | 30 |
| 4 × NTC (Murata C5316) | 4 |
| 1 × 100 Ω 0.1% (Vishay TNPW0603) | 1 |
| 64 × pin header pins | 5 |
| Per-placement cost (69 × ~€0.20) | 14 |
| Shipping (PostNL/DHL in EU) | 8 |
| **TOTAL** | **~€115-125 for 3 fully-assembled boards** |

Per-board cost ≈ €40. Boards arrive **ready for the cleanroom step** — just need to bond LEDs.

---

## When the boards arrive — sanity-check inspection

1. **Headers**: 32-pin male headers cleanly soldered north and south, no missing pins.
2. **NTCs**: 4 tiny black 0402 SMDs at TH1, TH2, TH3, TH4 (between LED pairs).
3. **Load resistor**: 1 small SMD between the labelled "100R LOAD" pads in the EIS CAL section.
4. **LED footprints**: 26 footprints (D1-D8 + 6 + 12 chain LEDs) are EMPTY — bare gold pads visible.
5. **Gold finish**: every probe pad / TC pad / fiducial is GOLD (not silver) — confirms ENIG.
6. **No solder paste residue** on the empty LED footprints.

If anything is wrong → contact Aisler immediately; they'll re-run before you ship to cleanroom.

---

## If Aisler doesn't work out

**Eurocircuits** (BE/DE — TU Delft's traditional fab):
- Upload `tud-microled-v2-gerbers.zip` + BOM + pos
- DEFINED pool service + ENIG finish
- Assembly via eC-stencil-mate (manual SMT) or full SMT line
- Slightly pricier (~€150 for 5 assembled boards) but 3-5 day lead time
