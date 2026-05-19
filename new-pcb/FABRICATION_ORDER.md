# Fabrication & Assembly Order — Aisler or Eurocircuits

**Project:** TUD micro-LED v4.0  ·  **Designer:** Daniel Tyukov · 5714699 · ET4277 / ET4391
**Board:** 93 × 93 mm · 2-layer · 1.6 mm FR-4 · ENIG finish · DRC clean (0 violations)

The PCB clears the standard pool at both EU fabs. Pick whichever fits the
schedule / budget on the day. The Gerbers, drill file, BOM CSV, and
pick-and-place CSV in `new-pcb/fab/` are identical inputs for both; only
the order form and a couple of file conventions differ.

| Fab | Location | Native input | Assembly service | Typical cost (3 boards) | Typical lead time |
|---|---|---|---|---:|---|
| **[Aisler](https://aisler.net)** | Aachen, DE / Eindhoven, NL | `.kicad_pcb` (drag-and-drop) or Gerbers | **Beagle** (turnkey, sources parts) | €115–125 | 5-8 working days |
| **[Eurocircuits](https://www.eurocircuits.com)** | Mechelen, BE / Aachen, DE / Eger, HU | Gerber X2 ZIP + drill (`.kicad_pcb` not accepted directly) | **eC-stencil-mate** (manual) or full SMT line | €130–160 | 3-5 working days |

For express shipping, both offer 1-3 day options at extra cost (Aisler
"Express", Eurocircuits "On Demand").

---

## TL;DR — both fabs

1. ENIG (Gold) finish, 2 layers, 1.55 mm FR-4 thickness, 3 boards.
2. Upload the right file bundle (see per-fab sections below).
3. Add assembly with the BOM and pick-and-place CSV from `new-pcb/fab/`.
4. Mark **D1–D8 + DCL6_L1..6 + DCL12_L1..12 (26 LEDs)** as **Do Not Assemble** — those are bonded in the cleanroom.
5. Everything else (NTCs, headers, load resistor) is pre-assembled by the fab.

---

## Bare-PCB configuration (identical for both fabs)

| Field | Value | Note |
|---|---|---|
| Layers | 2 | matches design |
| Dimensions | **93 × 93 mm** (auto-detected from Edge.Cuts) | Fits the Tresky T-3000-PRO die-bonder envelope (≤ 95 × 95 mm) with 1 mm margin |
| Thickness | 1.55 mm | standard at both fabs |
| Quantity | 3 boards | 1 trial + 1 real + 1 spare per solder-paste variant |
| **Surface finish** | **ENIG (Gold)** — Ni 4 µm + Au 0.075 µm RoHS | Mandatory; every probe pad must be gold for reliable contact + bonding |
| Outer copper | 35 µm (1 oz) | default |
| Solder mask | Green (matte black ~ €5 extra) | cosmetic |
| Silk | White | matches design |
| Min clearance | 0.30 mm (design) | clears Aisler 0.15 mm and Eurocircuits Class 4 (0.15 mm); deep in the cheap pool at both |
| Min track | 0.20 mm (design) | same — well above either fab's std-pool minimum |

---

## Bill of materials — pre-assembled by the fab

**69 placements per board (4 SMD + 64 THT + 1 SMD load).** All except the 26 LEDs are factory-soldered.

### Pre-assembled by Aisler Beagle or Eurocircuits SMT

| Designator(s) | Qty | Footprint | Recommended part | Notes |
|---|---:|---|---|---|
| **TH1, TH2, TH3, TH4** | 4 | 0402 SMD (NTC_0402 in board lib) | **Murata `NCP15XH103J03RC`** (10 kΩ ±5 %, B25/85 = 3380 K) — LCSC C5316 · Mouser 81-NCP15XH103J03RC | For V_F-TSP thermal sensing |
| **EIS_LOAD** (across PP_EIS_LOAD_A & PP_EIS_LOAD_B) | 1 | 0603 SMD thin-film | **Vishay Dale `TNPW0603100RBEEA`** (100 Ω, ±0.1 %, 25 ppm/°C, thin-film) — DigiKey 541-1830-1-ND | Reference resistor for LCR meter calibration |
| **H_N_1 .. H_N_32** | 32 | Pin header 2.54 mm, THT, vertical, single row | **Würth `61304011121`** (WR-PHD 1×40 single-row male, cut to 32 pins) — LCSC C124378 · Newark 20X1009 | North header |
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
| `FID1..FID4` | 4 | Optical fiducials for fab P&P |

---

## DNP — critical instruction for either fab

Paste this verbatim into the order notes (Aisler Beagle free-text field, or Eurocircuits "Special Requirements"):

> **DO NOT POPULATE THE LEDs.** The 26 WL-SFCC LED footprints (D1-D8, DCL6_L1..6, DCL12_L1..12, all using footprint `D_Wurth_WL-SFCC-0404superflat`) are the research subject and will be bonded by the customer in the TU Delft cleanroom under controlled conditions (paste, reflow profile, die-bonder). Please ONLY assemble: 4 × NTC at TH1-4, 1 × 100Ω 0.1% thin-film 0603 at EIS_LOAD, and 64 × pin header pins at H_N_* and H_S_*.

---

## What to upload — per fab

### Option A — Aisler (recommended for cost + speed)

| File (from `new-pcb/fab/`) | Where in Aisler UI |
|---|---|
| `../tud-microled-v2.kicad_pcb` (source at `new-pcb/`) | "Start Project" — drag-drop (Aisler reads KiCad natively) |
| `tud-microled-v2-fab-bom.csv` | Beagle assembly — BOM (MPN + DNP columns) |
| `tud-microled-v2-pos.csv` | Beagle assembly — Pick-and-Place CSV |
| `tud-microled-v2-top.pdf` / `-bot.pdf` | Visual review |
| `tud-microled-v2.step` | (optional) 3D model |

Files you can ignore for Aisler: `tud-microled-v2-gerbers.zip` (only needed for Eurocircuits).

### Option B — Eurocircuits (TU Delft's traditional fab)

| File (from `new-pcb/fab/`) | Where in Eurocircuits UI |
|---|---|
| `tud-microled-v2-gerbers.zip` | "Upload your design" → PCB visualiser (auto-extracts Gerbers + drill) |
| **`tud-microled-v2-fab-bom-assembly-only.csv`** | Assembly → BOM (**use this for Eurocircuits, not the full BOM**) |
| `tud-microled-v2-pos.csv` | Assembly → Pick-and-Place |
| `tud-microled-v2-top.pdf` / `-bot.pdf` | Visual review |

**Why the slim BOM for Eurocircuits?** Eurocircuits' BOM editor (eC-stencil-mate) lists every row in the CSV as a line item, regardless of the DNP column. A previous upload of the full BOM produced a quote with €659.60 of phantom assembly cost and six red "Unidentified" warnings — caused by two separate issues:

1. **DNP parsing.** Eurocircuits requires the DNP column to read literally `Yes` or `No`; anything else (e.g. `"Yes (customer bonds in cleanroom)"`) is silently treated as `No`. That made the 26 WL-SFCC LEDs count toward the assembly placement total. The current BOMs use strict `Yes`/`No`, so this specific bug is gone.
2. **Bare-pad rows.** The seven DNP rows (BP_*, FID*, PP_*, TC*, TLM_*, VDP_*, and the LEDs) carry `MPN="-"` because they are intentional gold lands, not parts. Even with DNP correctly flagged, Eurocircuits' editor still displays each of these as a row marked "Unidentified", which doesn't add to cost but does produce six red warnings and the orange "Incomplete" banner.

The slim BOM (`tud-microled-v2-fab-bom-assembly-only.csv`) sidesteps both issues by omitting every DNP row entirely. The CSV contains only the three rows Eurocircuits actually needs:

| Qty | Manufacturer | MPN | Distributor cross-ref |
|---:|---|---|---|
| 4 | Murata | `NCP15XH103J03RC` | LCSC C5316 |
| 1 | Vishay Dale | `TNPW0603100RBEEA` | DigiKey 541-100ARTR-ND |
| 64 | Würth | `61304011121` | LCSC C124378 · Newark 20X1009 |

69 placements total, zero ambiguity, no "Unidentified" line items. Eurocircuits' supplier scanner may still flag the parts as "NI" (No Info) for a working day while their engineers manually look up European-distributor pricing, but the quote will progress to a complete state instead of staying "Incomplete".

### Aisler keeps using the full BOM

For Aisler the full `tud-microled-v2-fab-bom.csv` is still the right file — Beagle uses the DNP rows to cross-check its sanity pass and tolerates `MPN="-"` on intentional DNP entries. Strict `Yes`/`No` in the DNP column works for both fabs, so the same file is safe at Aisler.

---

## Cost & lead-time comparison

| Item | Aisler | Eurocircuits |
|---|---:|---:|
| 3 × bare PCB (93 × 93 mm, 2-layer, ENIG, white silk) | 50-60 | 65-80 |
| Assembly setup fee | 30 | 35 |
| 4 × NTC (Murata C5316) | 4 | 4 |
| 1 × 100 Ω 0.1% (Vishay TNPW0603) | 1 | 1 |
| 64 × pin header pins | 5 | 5 |
| Per-placement cost (69 × ~€0.20) | 14 | 17 |
| Shipping (PostNL/DHL standard, EU) | 8 | 10 |
| **TOTAL (standard shipping)** | **~€115-125** | **~€135-160** |
| Express shipping surcharge | +€20-40 | +€25-50 |

Per-board cost: ~€40 (Aisler) or ~€50 (Eurocircuits) standard, ~€55 / ~€65 with express. Boards arrive ready for the cleanroom step — just need to bond the LEDs.

---

## When the boards arrive — sanity-check inspection

1. **Headers**: 32-pin male headers cleanly soldered north and south, no missing pins.
2. **NTCs**: 4 tiny black 0402 SMDs at TH1, TH2, TH3, TH4 (between LED pairs).
3. **Load resistor**: 1 small SMD between the labelled "100R LOAD" pads in the EIS CAL section.
4. **LED footprints**: 26 footprints (D1-D8 + 6 + 12 chain LEDs) are EMPTY — bare gold pads visible.
5. **Gold finish**: every probe pad / TC pad / fiducial is GOLD (not silver) — confirms ENIG.
6. **No solder paste residue** on the empty LED footprints.

If anything is wrong → contact the fab immediately; both Aisler and Eurocircuits will re-run before you ship to the cleanroom.
