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

## Component summary

### TDK NTCG104BH103HT1 — SMD 0402 NTC
- 1.0 × 0.5 mm body, 2 SMD pads
- R(25 °C) = 10 kΩ ±3 %, B25/85 ≈ 3380 K
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

with T₀ = 298.15 K, R₀ = 10 000 Ω, B = 3380 K. See `new-pcb/VERIFICATION_v4.md` §6.2 for the full thermal-resistance test procedure.
