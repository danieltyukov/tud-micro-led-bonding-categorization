# v3.9 PCB — verification & test procedures

Answers to the 6 verification points raised against the 93×93 board.

---

## 1. LED bonding dimensions — ✅ VERIFIED CORRECT

Cross-checked against Würth's **official KiCad library** for part `150044M155220`
(file: `new-pcb/library/footprints/LED_SMD_Wurth.pretty/D_Wurth_WL-SFCC-0404superflat.kicad_mod`):

| Parameter | Würth library | Our code | Match? |
|---|---|---|---|
| Pad 1 (anode) | `(at -0.4 -0.4)` size 0.4×0.4 | `(at -0.4 -0.4)` size 0.4×0.4 | ✅ |
| Pad 2 (K_R) | `(at  0.4 -0.4)` size 0.4×0.4 | `(at  0.4 -0.4)` size 0.4×0.4 | ✅ |
| Pad 3 (K_B) | `(at  0.4  0.4)` size 0.4×0.4 | `(at  0.4  0.4)` size 0.4×0.4 | ✅ |
| Pad 4 (K_G) | `(at -0.4  0.4)` size 0.4×0.4 | `(at -0.4  0.4)` size 0.4×0.4 | ✅ |

Datasheet specs all met:
- Pad size 0.4 × 0.4 mm (IPC ≈ 0.275 mm device pad + 0.125 mm fillet allowance)
- Pitch 0.8 mm centre-to-centre (=0.4 + 0.4 mm gap, per datasheet "Recommended Land Pattern")
- Polarity mark / pin 1 at top-left ✅
- CW numbering 1→2→3→4 from top-left ✅
- Schematic: pin 2 = R, pin 3 = B, pin 4 = G ✅

**Conclusion:** the bonding land pattern is dimensionally exact to Würth's recommendation.
Reflow profile (datasheet §6): peak 260 °C for ≤10 s, 60–120 s preheat 150–200 °C.

---

## 2. Routing — ✅ COMPLETE & VERIFIED

| Route group | Trace count | Status |
|---|---|---|
| South header → LED probe pads (32 pins, 4 lanes A/KG/KB/KR) | 96 segments | ✅ DRC clean |
| North header → LED-chain endpoints (4 pins: 3, 10, 19, 32) | 12 segments | ✅ DRC clean |
| LED chain R-series traces (N=6 + N=12) | 16 segments | ✅ DRC clean |
| Common-anode B.Cu bus (LED row) | 7 traces + 8 vias | ✅ DRC clean |
| NTC GND vias (4× to B.Cu pour) | 4 vias | ✅ DRC clean |
| GND probes to B.Cu pour | 2 vias | ✅ DRC clean |
| **Total DRC violations** | | **0** |
| **Total unconnected pads** | | **0** |

The south pre-wiring at 4 lanes (y = 82.4, 82.8, 83.2, 83.6) fits cleanly in the 2.5 mm gap between LED probe top (81.635) and south header bottom (84.15).

The 4 north routes (pins 3/10/19/32) take 3-segment Manhattan paths through clear F.Cu bands, avoiding all DoE / TLM / VDP / chain-LED obstacles.

---

## 3. Van der Pauw structures — ⚠ DESIGN NOTE

**The VDP "cloverleaves" on v3 are functional ONLY if a dummy die is bonded across the 4 contacts.** The footprint provides 4 isolated SMD lands at the cardinal positions:

| VDP | arm_len | Contact-to-contact diagonal | Needs a die of size ≥ |
|---|---|---|---|
| W=1.0 mm | 1.4 mm | 2.8 mm | 3 × 3 mm |
| W=0.5 mm | 0.9 mm | 1.8 mm | 2 × 2 mm |
| W=0.25 mm | 0.8 mm | 1.6 mm | 1.7 × 1.7 mm |
| W=0.1 mm | 0.8 mm | 1.6 mm | 1.7 × 1.7 mm |

**For your study** (only WL-SFCC LEDs, no dummy Si dies):
- LED die is only 0.95 × 0.95 mm — too small to span any of the 4 VDP structures
- VDP measurements are therefore **not directly executable** with v3 hardware as built
- VDP structures remain as **calibration/QC references**: they let you measure bare-ENIG pad sheet resistance from each fab batch (4-probe between any two contacts), confirming fab consistency lot-to-lot. The TLM ladders serve the same role with even tighter spacings.

This is a known limitation inherited from the v1 paper's design. Not a v3 regression.

---

## 4. Back-side TIER-2 SOUTH PINOUT text — ✅ UPDATED

The previous "NORTH row: user-jumperable" line was stale (didn't reflect the 4 new chain routes). Updated to three lines:

```
NORTH pins (marked O):  3=DC6_IN  10=DC6_OUT
                       19=DC12_IN  32=DC12_OUT
other NORTH pins: user-jumperable
```

Box height 9.5 mm (key_y0=73.5, key_y1=83.0) accommodates all 5 content lines (2 LED-group lines + 1 group-format line + 2 NORTH-mapping lines) with size 0.8 silk text. No overflow.

---

## 5. Electrical characterization completeness — answer to "could we have done more?"

Looking at the published paper's electrical section (§V-E) and the broader literature on micro-LED bond characterisation, here is the full landscape:

### What v3.9 hardware DIRECTLY enables (on-board)

| Measurement | Mechanism | Hardware element |
|---|---|---|
| **V_F per LED per colour** (R/G/B) | 4-wire Kelvin via probe pad + south header pin | LED row + 32-pin south header (✅) |
| **I-V sweep + R_s extraction** | SMU sweep, slope = R_s_LED + R_bond | South header → ext. SMU (✅) |
| **Reverse leakage** (at -5V) | Detects cracked die / shunt path | South header → ext. SMU (✅) |
| **Chain go/no-go QC** (N=6 + N=12) | Series LED chain — dark = ≥1 bond open | North header pins 3, 10, 19, 32 (✅) |
| **Substrate temperature** | NTC voltage divider | 4× NTC pads TH1-TH4 (✅) |
| **V_F-TSP junction thermometry** | LED V_F = -2 mV/°C drift → T_j | LED row + NTC for reference (✅ — see §6) |
| **Pulsed I-V** | Pulsed SMU through south header | South header (✅) |
| **EIS (AC impedance)** | LCR meter through south header | South header (✅) |
| **Long-term aging / DC stress** | Persistent SMU drive via header | South header + GND pour (✅) |
| **Ideality factor n** | Low-current I-V Shockley fit | South header → ext. SMU (✅) |
| **Reflow profile in-situ** | TC wire soldered to TC pads → DAQ | 4× TC pads (✅) |

### What is NOT possible on this board (genuine hardware gaps)

| Measurement | Why blocked | Workaround |
|---|---|---|
| **Optical power output** | Needs integrating sphere / spectrometer | Off-board (Labsphere, Gigahertz-Optik, EKL facility) |
| **CIE chromaticity** | Same as above | Off-board spectrometer |
| **Thermal cycling −40 / +125 °C** | Needs environmental chamber | Off-board TU Delft EKL chamber |
| **Mechanical die-shear strength** | Destructive | Off-board Nordson DAGE (in paper flow) |
| **X-ray void inspection** | Needs imaging system | Off-board Seamark X5600 (in paper flow) |
| **VDP / TLM with own bond material** | Requires dummy dies to span structures | Use VDP/TLM as bare-ENIG calibration only |

### What could have been added but wasn't (judgment calls)

| Could-have | Why not added |
|---|---|
| On-board analog multiplexer (e.g., ADG1408) for 1-SMU automated 8-LED testing | Adds parts + complexity; SMU + manual probe re-landing is acceptable for a research-throughput volume of measurements |
| Precision current-sense shunts | Modern SMUs (Keithley 2400 / 2461) handle current measurement with sufficient precision; on-board shunt would only matter for sub-µA work |
| On-board pulse generator for EIS | LCR meter is preferred for EIS — on-board source would be redundant |
| Strain gauges to measure die curl during reflow | Out of scope (mechanical, not electrical) |
| PT100/PT1000 instead of NTCs | NTC at 10 kΩ / B=3380 K gives ±0.1 °C resolution near room temperature, plenty for V_F-TSP. PT100 would be more accurate at high T but adds parts cost. |
| 4-wire dedicated probe pads PER LED pin (8 force + 8 sense) | Doubles pad count; using probe pad + header pin already gives Kelvin separation |

### Bottom line

**Every electrical measurement reported in [Abdelwahab 2025] is reproducible on v3.9 hardware**, plus all the Tier-2 measurements I listed in `PUBLICATION_CONTRIBUTION.md` (V_F-TSP thermal R, EIS, pulsed I-V, aging, ideality). The remaining gaps are off-board lab needs (optics, thermal cycling, X-ray, shear), not PCB-fixable.

Hardware is **comprehensive for purely electrical characterisation**. No additional on-board features would expand the measurement space beyond what an external SMU + LCR + thermal chuck can already do.

---

## 6. NTC component recommendation & V_F-TSP test procedure

### 6.1 Recommended NTC for TH1–TH4

| Spec | Value |
|---|---|
| Part number | **Murata NCP15XH103J03RC** |
| Package | 0402 SMD (1.0 × 0.5 mm, matches our footprint) |
| Nominal resistance @ 25 °C | 10 kΩ ±5 % |
| B25/85 constant | 3380 K ±1 % |
| Operating range | −40 °C to +125 °C |
| Tolerance over range | ±1 % (XH = high-precision grade) |
| LCSC part | C5316 |
| DigiKey | 490-2436-1-ND |
| Mouser | 81-NCP15XH103J03RC |
| Datasheet | Murata "R44E" catalog, NTC for Temperature Sensor series |

**Datasheet download (manual, auto-download blocked by Cloudflare):**
- Mouser product page: https://www.mouser.com/ProductDetail/81-NCP15XH103J03RC
  → click "Datasheet" link
- LCSC product page: https://www.lcsc.com/product-detail/_C5316.html
  → click "Datasheet" tab
- Save the PDF as `docs/Murata-NCP15XH103-NTC.pdf` so it lives alongside the WL-SFCC datasheet

**Alternative parts** (if Murata is out of stock):
- Vishay `NTCS0402E3103FXT` — 10 kΩ ±1 %, B=3380 K, 0402
- TDK `B57441V2103H062` — 10 kΩ ±1 %, B=3380 K, 0402

All three are interchangeable for V_F-TSP — calibration curve is built per-device anyway.

### 6.2 V_F-TSP test procedure (NTC + LED for bond thermal resistance)

The **Forward-Voltage Thermal Sensing Parameter** method uses the LED's V_F as a built-in junction thermometer, while the NTC reads the substrate temperature beneath the bond. The temperature delta divided by dissipated power gives **bond thermal resistance R_th-jc** — the single most reliability-relevant number for an LED bond.

#### Setup (one-time)

1. Bond LED D1 to PCB in the cleanroom (Tresky T-3000-PRO, reflow profile from paper §III-A — peak 165 °C).
2. NTC TH1 is already pre-soldered between D1 and D2 (4 mm from D1, on the same FR-4 island).
3. Wire the south header pin 1 (LED_VCC) and pin 4 (LED1_KR) to your SMU. Wire the NTC probe pad PP_NTC1 to a DMM in 4-wire R mode.

#### Step 1 — V_F calibration (build the V_F(T_j) curve)

Goal: find the slope of V_F vs T_junction for THIS LED.

1. Place PCB on a temperature-controlled hotplate / Peltier chuck.
2. Wait for thermal equilibrium at 25 °C (≥5 min, no current to LED).
3. Apply a small **sense current** I_sense = 1 mA to D1 (red die: V_F ≈ 2.05 V).
4. Read V_F_sense from SMU (e.g., 2.052 V).
5. Read NTC resistance R_NTC; convert to T using the B-parameter formula:
     T(K) = 1 / [ (1/T₀) + (1/B) · ln(R_NTC / R₀) ]
   with T₀ = 298.15 K, R₀ = 10 000 Ω, B = 3380 K
6. Repeat for chuck setpoints 40, 60, 80 °C. Plot V_F_sense vs T.
7. Linear fit → slope ≈ **−2.0 mV/°C** for red, ≈ −2.5 mV/°C for green/blue.
   Save the slope as **K_LED** (the "TSP coefficient" for this device).

#### Step 2 — Bond thermal resistance measurement

Goal: measure R_th-jc = (T_junction − T_substrate) / P_dissipated under operating current.

1. PCB at room temperature. Read NTC → call this T_amb (e.g., 22.5 °C).
2. Apply **heating current** I_heat = 20 mA to D1 (well above sense).
   Wait for thermal steady state (typically 30–60 s; long enough that NTC stops drifting).
3. **Switch-and-measure** sequence (must be fast, ≤1 ms):
   a. Drop current from I_heat → I_sense (1 mA) for 100 µs.
   b. Sample V_F_op during the sense pulse.
   c. Return to I_heat.
4. Compute T_junction:
     T_j = T_amb + (V_F_sense_calibrated_at_T_amb − V_F_op) / K_LED
5. Read NTC → T_substrate (substrate temperature under heating).
6. Compute dissipated power:
     P_diss = I_heat × V_F (at I_heat, measured separately or read during heating)
7. **Bond thermal resistance:**
     **R_th-jc = (T_j − T_substrate) / P_diss**       [units: °C/W]

#### Expected results & paper relevance

| Bond quality | Typical R_th-jc (for 1 × 1 mm LED, SAC305 / ENIG) |
|---|---|
| Good bond (no voids, full wetting) | 30–60 °C/W |
| Voided bond | 70–150 °C/W |
| Cold joint / partial detach | > 200 °C/W |

Across solder pastes / die finishes / processes (paper's variables), **R_th-jc differences are the single clearest electrical signature of bond quality** — beats V_F drift, beats series resistance, beats EIS. It's also directly tied to LED lifetime (Arrhenius: every +10 °C halves lifetime).

For the paper: report mean ± stdev R_th-jc per condition (n ≥ 5 LEDs), ANOVA on (paste × finish × pressure). Pair with X-ray void % and shear strength for the multi-modal correlation that makes a strong ECTC / IEEE T-CPMT submission.

---

## Summary

| Item | Status |
|---|---|
| LED dimensions | ✅ Match Würth official footprint exactly |
| Routing | ✅ DRC clean, all targets connected |
| VDP | ⚠ Functional only with dummy die; serves as calibration reference for LED-only studies |
| Back-side text | ✅ Updated to reflect 4 routed north pins, no overflow |
| Electrical char completeness | ✅ All paper measurements reproducible; +5 Tier-2 novel measurements (R_th, EIS, pulsed, aging, n) |
| TH1-4 component | Murata NCP15XH103J03RC (LCSC C5316). Datasheet: download manually from Mouser/LCSC |
| V_F-TSP procedure | Documented above — pairs NTC + LED for bond thermal resistance |
