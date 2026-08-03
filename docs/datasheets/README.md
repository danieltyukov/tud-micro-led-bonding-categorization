# Component Datasheets — v2 PCB

Datasheets for every component ordered for the v2 PCB. All MPNs match the BOM in `new-pcb/fab/tud-microled-v2-fab-bom.csv` and are verified in stock on Mouser EU at order time.

**Components ship loose from Eurocircuits ("Place loose") and are hand-soldered at TU Delft EKL. The 26 LEDs are customer-supplied and bonded at EKL under the Tresky T-3000-PRO with a controlled paste profile.**

---

## Final BOM (3 distinct parts, 7 placements per board)

| Designator(s) | Qty / board | Manufacturer | MPN | Mouser PN | Datasheet file |
|---|---:|---|---|---|---|
| TH1, TH2, TH3, TH4 | 4 | TDK | `NTCG104BH103HT1` | 810-NTCG104BH103HT1 | `TDK-NTCG104BH103HT1-NTC.pdf` |
| R_EIS_LOAD | 1 | Yageo | `RT0603BRB07100RL` | 603-RT0603BRB07100RL | `Yageo-RT0603BRB07100RL-Resistor.pdf` |
| H_N, H_S | 2 | Samtec | `TSW-140-07-G-S` (cut to 1×32) | 200-TSW14007GS | `Samtec-TSW-Series-PinHeader.pdf` |
| D1-D8 + DCL6_L1..6 + DCL12_L1..12 | 26 | Würth | `150044M155220` | 710-150044M155220 | `Wurth-WL-SFCC-0404-RGB-LED-150044M155220.pdf` |

---

## Datasheets in this folder

| File | Pages | Component | Where on PCB |
|---|---:|---|---|
| `TDK-NTCG104BH103HT1-NTC.pdf` | 20 | TDK NTCG104 series — NTC 10 kΩ ±3% 0402, AEC-Q200 | TH1..TH4 |
| `Yageo-RT0603BRB07100RL-Resistor.pdf` | 10 | Yageo RT series — 100 Ω ±0.1% 0603 thin-film, 10 ppm/°C | R_EIS_LOAD |
| `Samtec-TSW-Series-PinHeader.pdf` | 6 | Samtec TSW series — product specification sheet (electrical, mechanical) | H_N + H_S |
| `Wurth-WL-SFCC-0404-RGB-LED-150044M155220.pdf` | 10 | Würth WL-SFCC RGB LED — full electrical/optical/mechanical/reflow | D1..D8, DCL6_L1..6, DCL12_L1..12 |

All downloaded from manufacturer / Mouser EU on **2026-05-19**.

---

## Test-equipment documentation (added 2026-08-03)

For the measurement campaign in `FINAL_MEASUREMENTS/`.

| File | Pages | What it is |
|---|---:|---|
| `INSTRUMENTS.md` | - | **Start here.** Extracted specs for the multimeter and the Arduino, with what is documented, what is not, and the numbers that must be measured at the bench instead. |
| `Arduino-UNO-R3-Datasheet.pdf` | 26 | Arduino UNO R3 board datasheet |
| `Microchip-ATmega328P-Datasheet.pdf` | 294 | Microchip 7810D-AVR-01/15. Source of the ADC specs and the absolute maximum ratings that constrain the current bank |
| `Thsinde-18B-plus-Independent-Review-N8FDY.pdf` | 8 | Independent bench review of this exact meter against a calibrated Keithley DMM6500. **The only source for its diode-test voltage and current.** |
| `Fluke-15B-17B-18B-plus-Users-Manual.pdf` | 23 | **A different instrument.** Cross-reference only, see below |

### On the Thsinde 18B+ multimeter

**No manufacturer manual exists.** The only page that claims to be one
(`manuals.plus/thsinde/...`) is AI-generated SEO filler carrying the Amazon listing spec
table plus invented reviews and a price. It contains no operating instructions, no button
behaviour, and no diode-test specification. It is not worth storing, so its usable content
is transcribed into `INSTRUMENTS.md` instead.

The Fluke 15B+/17B+/18B+ manual is stored as a cross-reference **only**. It is a different
instrument: 4000 counts rather than 6000, no NCV, no REL, no MAX/MIN, and it has a
dedicated LED TEST dial position that the Thsinde does not. The Thsinde borrowed the model
number and the styling. Do not quote its specifications as if they were the Thsinde's.

The gap is filled by the N8FDY independent review, which measured the meter against a
calibrated Keithley DMM6500. Its key result for this project: **diode test open-circuit
voltage 3.245 V, short-circuit current 1.49 mA.** 3.245 V clears the forward voltage of
red, green and blue, so all three channels are testable in round 1 step 6. That had been
the largest open risk in the measurement plan. It is still re-confirmed on the board's own
100 Ω 0.1 % reference at the start of each session.

---

## Component summary

### TDK NTCG104BH103HT1 — SMD 0402 NTC
- 1.0 × 0.5 mm body, 2 SMD pads
- R(25 °C) = 10 kΩ ±3 %, **B25/85 = 4100 K** (datasheet row for this MPN: 4067 / 4092 / 4100 / 4110 K for B25/50, B25/80, B25/85, B25/100)
- **Correction 2026-08-03:** this file previously said 3380 K. That is the B25/50 figure for the *NTCG10xJF/JH* family, a different B-constant grade. The ordered part is the `BH` grade, which is the 4067-4110 K row.
- AEC-Q200 qualified, −55 °C to +125 °C operating range
- Sense current ≤ 100 µA to keep self-heating < 0.01 °C
- For V_F-TSP thermometry calibration: see `new-pcb/VERIFICATION_v4.md` §6.2
- Mouser EU stock: 12,207 (verified 2026-05-19)

### Yageo RT0603BRB07100RL — SMD 0603 thin-film
- 1.6 × 0.8 mm body
- 100 Ω, ±0.1 %, **10 ppm/°C** TCR, 100 mW (1/10 W)
- −55 °C to +155 °C operating range, 75 V max
- Used as the EIS reference load for LCR-meter calibration before Nyquist sweeps
- Mouser EU stock: 15,867 (verified 2026-05-19)
- Note: chosen over the original RT0603BRD07100RL because BRD was out of stock (backorder to Sep 2026); BRB is a strict upgrade (10 ppm/°C vs 25 ppm/°C TCR) at the same form factor

### Samtec TSW-140-07-G-S — THT 1×40 single-row male pin header
- 2.54 mm pitch, gold-plated contacts (Ni underplate + Au flash)
- Pin cross-section: 0.64 mm square
- Pin length above board: 5.84 mm
- Insulator height: 2.54 mm
- Each board uses 2 strips (one trimmed to 32 pins for the north row, one for the south row)
- Drill 1.0 mm, pad 1.7 mm Ø → annular ring 0.35 mm
- Mouser EU stock: 338 (verified 2026-05-19) — sufficient for 20 strips needed by 10 boards

### Würth WL-SFCC 0404 RGB LED — SMD (customer-bonded)
- 0.95 × 0.95 × 0.25 mm body, 4 contact pads at corners (one anode + R/G/B cathodes)
- V_F red ≈ 2.05 V, green/blue ≈ 3.05 V at 10 mA
- Reflow recommended per Würth profile §6 of the datasheet — *not used here* because we bond at EKL with the Tresky's controlled profile
- Bond pads ship as bare ENIG gold (F.Paste gerber is empty — fab applies no paste)

---

## NTC R-T equation (for V_F-TSP calibration)

T(K) = 1 / [ (1/T₀) + (1/B) · ln(R / R₀) ]

with T₀ = 298.15 K, R₀ = 10 000 Ω, **B = 4100 K**. See `new-pcb/VERIFICATION_v4.md` §6.2 for the full thermal-resistance test procedure.
