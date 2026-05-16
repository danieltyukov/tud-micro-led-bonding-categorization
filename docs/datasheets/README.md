# Component Datasheets — v4.0 PCB

All 4 components on the TUD micro-LED v4.0 PCB, with manufacturer datasheets
verified by inspecting file content (not just file name).

**LEDs are bonded by the customer in cleanroom; all other components are
pre-assembled by the fab house (Aisler / Eurocircuits).**

---

## Datasheets in this folder — VERIFIED

| File | Component | Where on PCB | Qty | Verified content |
|---|---|---|---|---|
| `Wurth-WL-SFCC-0404-RGB-LED-150044M155220.pdf` | Würth WL-SFCC 0404 superflat RGB LED, P/N 150044M155220 — **SMD 4-pad, 0.95×0.95 mm** | D1-D8 + DCL6_L1..6 + DCL12_L1..12 | **26** (DNP — bonded in cleanroom) | ✅ "WL-SFCC SMT Full-color Chip LED compact" — matches |
| `Murata-NCP15XH103J03RC-NTC-R44E.pdf` | Murata NCP15 series NTC thermistor — **SMD 0402**, 10 kΩ ±5 %, B25/85 = 3380 K | TH1, TH2, TH3, TH4 | **4** (pre-assembled) | ✅ "NTC Thermistors" — R44E catalog covering NCP15 series |
| `Vishay-Dale-TNPW0603-Thin-Film-Resistor-28758.pdf` | Vishay Dale TNPW0603 thin-film 0.1% precision resistor — use `TNPW0603100RBEEA` (100 Ω, ±0.1 %) — **SMD 0603** | EIS_LOAD (between PP_EIS_LOAD_A and PP_EIS_LOAD_B) | **1** (pre-assembled) | ✅ "TNPW e3 - High Stability Thin Film Flat Chip Resistors" — matches |
| `Wurth-WR-PHD-1x40-2.54mm-PinHeader-61304011121.pdf` | Würth WR-PHD 1×40 male pin header, 2.54 mm pitch, vertical THT, single row, P/N 61304011121 | H_N_1..32 + H_S_1..32 | **64** total (= 2 strips × 32 pins each, cut from 1×40 strips, pre-assembled) | ✅ single-row matches PCB; recommended drill 1.10±0.15 mm (PCB uses 1.0 mm — at low edge of range, standard for 0.1" THT) |

---

## Final BOM (pre-assembled by fab)

| Designator(s) | Qty | Manufacturer P/N | Distributor codes |
|---|---:|---|---|
| TH1–TH4 | 4 | Murata `NCP15XH103J03RC` | Mouser 81-NCP15XH103J03RC · LCSC C5316 · DigiKey 490-2436-1-ND |
| EIS_LOAD | 1 | Vishay Dale `TNPW0603100RBEEA` | DigiKey 541-100ARTR-ND · Mouser 71-TNPW0603100RBEEA |
| H_N_1..32 + H_S_1..32 | 64 | Würth `61304011121` (1×40 single-row, cut to 1×32 each) | LCSC C124378 · Newark 20X1009 · RS 828-1642 |
| D1..D8 + DCL6_L1..6 + DCL12_L1..12 | 26 | Würth `150044M155220` | **DNP — bonded in cleanroom by customer** |

---

## Component summary

### Würth WL-SFCC 0404 RGB LED — SMD
- 0.95 × 0.95 × 0.25 mm body, 4 contact pads at corners
- Common anode (pin 1) + 3 cathodes (R/G/B = pins 2/3/4)
- V_F red ≈ 2.05 V, green/blue ≈ 3.05 V (at 10 mA)
- Datasheet pp 1-10, fully covers electrical / optical / mechanical / reflow

### Murata NCP15XH103J03RC NTC thermistor — SMD 0402
- 1.0 × 0.5 mm body, 2 SMD pads at ±0.5 mm pitch
- R(25°C) = 10 kΩ ±5 %, B25/85 = 3380 K ±1 %
- Operating range −40 °C to +125 °C
- ±0.3 °C accuracy with B-curve calibration (0–70 °C range)
- Recommended sense current ≤ 100 µA (self-heating < 0.01 °C)
- Datasheet is the full R44E catalog (25 pages, covers NCP15 series + larger)

### Vishay TNPW0603100RBEEA precision resistor — SMD 0603
- 1.6 × 0.8 mm body, thin-film
- 100 Ω, ±0.1 % tolerance, 25 ppm/°C TCR
- AEC-Q200 qualified, PFAS-free
- |ΔR/R| < 0.1 % under 85 °C / 85 % RH / 1000 h moisture
- TNPW series datasheet covers all values; the BEEA suffix specifies 100 Ω, ±0.1 %, BEE size code

### Würth WR-PHD pin header — through-hole, 2.54 mm pitch, single row
- **MPN: 61304011121** (1×40 single-row male, vertical THT, unshrouded)
- Pin cross-section: 0.64 ± 0.15 mm square
- Pin length above PCB: 6.0 ± 0.20 mm
- Insulator height above PCB: 11.54 ± 0.2 mm
- Datasheet recommended drill: 1.10 ± 0.15 mm (range 0.95-1.25)
- PCB drill: 1.0 mm (within recommended range, at low edge — standard for 0.1" THT)
- PCB pad: 1.7 mm Ø → annular ring 0.35 mm (well above Aisler 0.15 min)
- 1×40 strip (101.6 mm length) — order 2 strips, fab cuts to 32 pins per row

---

## NTC R-T equation (for V_F-TSP calibration)

  T(K) = 1 / [ (1/T₀) + (1/B) · ln(R / R₀) ]

with T₀ = 298.15 K, R₀ = 10 000 Ω, B = 3380 K. See `VERIFICATION_v4.md` §6.2 for the full thermal-resistance test procedure.

---

## Alternative SMD parts (in case of stock issues)

All drop-in compatible with the existing v4 footprints:

| Slot | Original | Alternative |
|---|---|---|
| NTC 0402 | Murata NCP15XH103J03RC | TDK NTCG104EH103HT1 · TE/Panasonic ERTJ1VR103J |
| Load R 0603 | Vishay TNPW0603100RBEEA | Yageo RT0603BRD07100RL · Susumu RR0816P-101-D · Bourns CRT0603-BY-1000ELF |
| Header 2.54mm | Würth 61301021121 | Any single-row male 2.54 mm THT strip (CNC Tech, TE, Molex, etc.) |
| RGB LED 0404 | Würth 150044M155220 | **Do not substitute** — your study is specifically on this device |
