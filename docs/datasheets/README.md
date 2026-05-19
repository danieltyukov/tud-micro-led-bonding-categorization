# Component Datasheets — v2 PCB

All 3 distinct components ordered for the v2 PCB, plus the LED that gets bonded at EKL.

**Components ship loose from Eurocircuits ("Place loose") and are hand-soldered at TU Delft EKL. The 26 LEDs are customer-supplied and bonded at EKL under the Tresky T-3000-PRO with a controlled paste profile.**

---

## Final BOM (3 distinct parts, 7 placements per board)

| Designator(s) | Qty / board | Manufacturer | MPN | Mouser PN |
|---|---:|---|---|---|
| TH1, TH2, TH3, TH4 | 4 | TDK | `NTCG104BH103HT1` | 810-NTCG104BH103HT1 |
| R_EIS_LOAD | 1 | Yageo | `RT0603BRD07100RL` | 603-RT0603BRD07100RL |
| H_N, H_S | 2 | Samtec | `TSW-140-07-G-S` (1×40 strip, cut to 1×32) | 200-TSW14007GS |
| D1-D8 + DCL6_L1..6 + DCL12_L1..12 | 26 | Würth | `150044M155220` | **DNP — bonded at EKL by customer** |

---

## Datasheets in this folder

| File | Component | Where on PCB | Qty/board | Status |
|---|---|---|---:|---|
| `Wurth-WL-SFCC-0404-RGB-LED-150044M155220.pdf` | Würth WL-SFCC 0404 superflat RGB LED — 0.95 × 0.95 × 0.25 mm, 4 corner pads | D1-D8 + DCL6_L1..6 + DCL12_L1..12 | 26 (DNP) | ✅ — **actual ordered part** |
| `Murata-NCP15XH103J03RC-NTC-R44E.pdf` | NTC 10 kΩ 0402, B25/85 = 3380 K | TH1..TH4 | 4 | electrical reference — **ordered part is TDK NTCG104BH103HT1** (equivalent) |
| `Vishay-Dale-TNPW0603-Thin-Film-Resistor-28758.pdf` | 100 Ω ±0.1% 0603 thin-film | R_EIS_LOAD | 1 | electrical reference — **ordered part is Yageo RT0603BRD07100RL** (equivalent) |
| `Wurth-WR-PHD-1x40-2.54mm-PinHeader-61304011121.pdf` | 1×40 male pin header, 2.54 mm pitch, vertical THT | H_N + H_S | 2 strips | mechanical reference — **ordered part is Samtec TSW-140-07-G-S** (equivalent) |

The non-LED datasheets remain as electrical/mechanical references because Aisler did not stock the original Murata/Vishay/Würth MPNs. The ordered TDK/Yageo/Samtec equivalents match every spec that matters for this design.

Optional: pull the actual ordered-part datasheets from Mouser (links below) and add them to this folder for completeness:

- TDK NTCG104BH103HT1 — https://www.mouser.com/datasheet/2/400/ntcg-1936252.pdf
- Yageo RT0603BRD07100RL — https://www.mouser.com/datasheet/2/447/PYu_RT_1_to_0_01_RoHS_L_12-3313554.pdf
- Samtec TSW-140-07-G-S — https://suddendocs.samtec.com/catalog_english/tsw_th.pdf

---

## Component summary (per the ordered parts)

### Würth WL-SFCC 0404 RGB LED — SMD
- 0.95 × 0.95 × 0.25 mm body, 4 contact pads at corners (one anode + R/G/B cathodes)
- V_F red ≈ 2.05 V, green/blue ≈ 3.05 V at 10 mA
- Reflow recommended per Würth profile §6 of the datasheet — *not used here* because we bond at EKL with the Tresky's controlled profile
- Bond pads ship as bare ENIG gold (F.Paste gerber is empty — fab applies no paste)

### TDK NTCG104BH103HT1 — SMD 0402
- 1.0 × 0.5 mm body, 2 SMD pads
- R(25 °C) = 10 kΩ ±3 %, B25/85 ≈ 3380 K
- AEC-Q200 qualified, −55 °C to +125 °C operating range
- Sense current ≤ 100 µA to keep self-heating < 0.01 °C
- For V_F-TSP thermometry calibration: see `new-pcb/VERIFICATION_v4.md` §6.2

### Yageo RT0603BRD07100RL — SMD 0603 thin-film
- 1.6 × 0.8 mm body
- 100 Ω, ±0.1 %, 25 ppm/°C TCR, 1/10 W
- Used as the EIS reference load for LCR-meter calibration before Nyquist sweeps

### Samtec TSW-140-07-G-S — THT 1×40 single-row male pin header
- 2.54 mm pitch, gold-plated contacts (Ni underplate + Au flash)
- Pin cross-section: 0.64 mm square
- Pin length above board: 5.84 mm
- Insulator height: 2.54 mm
- Each board uses 2 strips (one trimmed to 32 pins for the north row, one for the south row)
- Drill 1.0 mm, pad 1.7 mm Ø → annular ring 0.35 mm

---

## NTC R-T equation (for V_F-TSP calibration)

T(K) = 1 / [ (1/T₀) + (1/B) · ln(R / R₀) ]

with T₀ = 298.15 K, R₀ = 10 000 Ω, B = 3380 K. See `new-pcb/VERIFICATION_v4.md` §6.2 for the full thermal-resistance test procedure.
