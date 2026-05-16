# Fabrication & Assembly Order Sheet — Aisler

**Project:** TUD micro-LED v2  ·  **Designer:** Daniel Tyukov · 5714699 · ET4277 / ET4391
**Board:** 100 × 100 mm · 2-layer · 1.6 mm FR-4 · ENIG finish · DRC clean
**Supplier:** [Aisler](https://aisler.net) (Aachen, DE / Eindhoven, NL — EU fab + assembly)

---

## TL;DR — what you do

1. Go to https://aisler.net → "Start Project" → **drag-drop the file `new-pcb/tud-microled-v2.kicad_pcb`** (the raw KiCad file, NOT a Gerber zip — Aisler reads KiCad natively).
2. On the configuration page, set:
   - **Surface finish:** ENIG (Gold) — **critical**
   - **PCB thickness:** 1.55 mm (Aisler's standard, matches our 1.6 mm spec)
   - **Quantity:** 3 (Aisler bundles in 3s)
   - **Layers:** 2 (auto-detected)
   - **Outer copper:** 1 oz / 35 µm (default)
3. Add **"Aisler Beagle"** assembly service.
4. Upload `new-pcb/fab/tud-microled-v2-bom.csv` and `new-pcb/fab/tud-microled-v2-pos.csv` for Beagle to match parts.
5. In the part-review screen, **mark D1-D8 as "Do not assemble"** (the 8 Würth WL-SFCC LEDs — you bond these in the cleanroom).
6. Add NTCs and headers from Aisler's part library (table below).
7. Add to cart → checkout. Aisler ships from EU, no customs.

---

## Detailed fields

### Bare-PCB configuration

| Field | Value | Why |
|---|---|---|
| File format | KiCad PCB (`.kicad_pcb`) | Aisler renders directly from KiCad without Gerber re-export, fewer fab errors |
| Layers | 2 | matches design |
| Dimensions | 100 × 100 mm | auto-detected from Edge.Cuts layer |
| Thickness | 1.55 mm | Aisler's standard "Beagle-standard" stack-up; effective FR-4 = 1.5 mm |
| Quantity | 3 | Beagle pool minimum |
| **Surface finish** | **ENIG (Gold)** | Mandatory — every probe pad must be gold. Aisler's ENIG is 4 µm Ni + 0.075 µm Au RoHS |
| Outer copper | 35 µm (1 oz) | default |
| Solder mask | Green (or matte black for ~€5 surcharge) | cosmetic |
| Silk | White | matches design |
| Min clearance | 0.15 mm | design rule |
| Min track | 0.20 mm | design rule |
| Smallest drill | 0.30 mm | matches via spec |

### Aisler Beagle assembly

Beagle is Aisler's auto-quote SMT/THT assembly. It uses their own part library
("Aisler Library" — a curated subset of DigiKey + Mouser stock) and quotes
per-placement automatically. They source the parts; you pay for parts + a
single setup fee.

**Files to upload:**
- `new-pcb/fab/tud-microled-v2-bom.csv` → "Bill of Materials"
- `new-pcb/fab/tud-microled-v2-pos.csv` → "Pick-and-Place / Centroid"

**Parts to assemble (Aisler will ask you to match each line):**

| Designators | Footprint | Aisler library search term | Confirm spec |
|---|---|---|---|
| TH1, TH2, TH3, TH4 | NTC_0402 | "NTC 10k 0402 B3380" | Murata `NCP15XH103F03RC` or Vishay `NTCS0402E3103FXT` — 10 kΩ ±1%, B25/85 = 3380 K |
| H_N_1 … H_N_30 (30 pins) | Header_2.54mm | "Pin header 2.54mm single row male" | Würth `61301021121` (cut from 1×40 strip) or any single-row 2.54 mm |
| H_S_1 … H_S_32 (32 pins) | Header_2.54mm | "Pin header 2.54mm single row male" | same SKU as above |

Total: **4 SMD + 62 THT placements = 66 parts**.

### Parts to NOT assemble (DNP)

In the Aisler part-review UI, mark these as "Do not place / DNP":

| Designators | Why |
|---|---|
| **D1-D8** (Würth WL-SFCC 0404 RGB LED) | Research subject. You bond these in the TU Delft cleanroom with controlled paste / reflow / bonder. |
| All `BP_*`, `TLM_*`, `VDP_*`, `DC_*`, `PP_*`, `TC*`, `FID*` | Bare gold pads — no component to place |

Aisler usually flags bare-pad footprints automatically (they have no
matching `MPN`), but double-check the review screen.

---

## Aisler quirks to know

1. **They re-bundle the order in batches of 3 boards minimum.** You can't order just 1. Order 3 unless you need more.
2. **Lead time is ~5-8 working days from order to delivery.** No express option, but no shipping delay vs Chinese fabs.
3. **No customs.** Both NL and DE are inside the EU — boards ship via PostNL or DHL, no import paperwork.
4. **KiCad native upload** is more accurate than Gerber upload: Aisler's renderer sees layer names like `F.SilkS` and `Edge.Cuts` directly. If anything looks wrong in their preview, it's wrong in our KiCad file too — fix at the source.
5. **No DNP column in BOM CSV.** You set DNP per-line in the web UI after upload.
6. **Beagle availability:** their assembly service has variable lead time depending on parts in stock. If `C5316`-equivalent NTC isn't in their library, search the alternatives in the table above — any 10 kΩ 0402 NTC with B = 3380 K works for our temperature-monitoring use.

---

## Files to upload

All in `new-pcb/fab/`:

| File | Where |
|---|---|
| `new-pcb/tud-microled-v2.kicad_pcb` | Main upload — drop on Aisler "Start Project" |
| `tud-microled-v2-bom.csv` | Beagle assembly — BOM |
| `tud-microled-v2-pos.csv` | Beagle assembly — Pick-and-Place |
| `tud-microled-v2-top.pdf` / `-bot.pdf` | Visual review before checkout |
| `tud-microled-v2.step` | (optional) 3D model for mechanical-fit confirmation |

Files you can ignore for the Aisler order:
- `tud-microled-v2-gerbers.zip` — only needed if Aisler's KiCad parser ever fails (it won't)

---

## Cost estimate (Aisler)

| Item | Approx € |
|---|---|
| 3 × bare PCB (100×100 mm, 2-layer, ENIG) | 45-55 |
| Beagle setup fee | 30 |
| Component cost (4 NTC + 62 header pins) | 5-10 |
| Per-placement cost (66 × ~€0.20) | 13 |
| Shipping (PostNL/DHL inside EU) | 8 |
| **Total** | **~€100-115 for 3 fully-assembled boards** |

Final price depends on Aisler's current Beagle rates — get an instant quote in
the web UI after upload.

---

## DNP wording (paste into Aisler order notes if their UI asks for free text)

> Do NOT populate D1-D8 (Würth WL-SFCC 0404 RGB LED footprints). These 8 LEDs
> are the research subject and will be bonded by the customer in the TU Delft
> cleanroom under controlled conditions (solder paste type, reflow profile,
> die-bonder). Please only assemble: 4 × NTC (TH1-TH4) + 30+32 pin headers
> (H_N_*, H_S_*).

---

## When the boards arrive

1. **Inspect** — confirm:
   - 4 tiny black 0402 NTCs at TH1-TH4 (above the LED row)
   - 30-pin header populated north, 32-pin header populated south
   - Gold (not silver) on every probe / bond / test pad
   - No solder paste residue on the 8 empty LED footprints

2. **Cleanroom step** — stencil-print solder paste on the 8 LED positions,
   place 8 LEDs, reflow (165 °C peak per ECTC paper §III-A). Optionally
   solder fine TC wire onto TC1-TC4 before reflow for in-situ profile data.

3. **Electrical characterisation** — see `ELECTRICAL_CHARACTERIZATION.md`
   for the full test plan (V_F, I-V, pulsed-IV, EIS, V_F-TSP, aging).

---

## If Aisler doesn't work out

- **Eurocircuits** (Belgium/Germany — TU Delft's traditional fab): upload
  `tud-microled-v2-gerbers.zip` + BOM + pos to their PCB Visualizer; pick
  "DEFINED" pool + ENIG; assembly via eC-stencil-mate or full SMT line.
  Slightly pricier (~€150 for 5 assembled boards) but ~3-5 day lead time.
