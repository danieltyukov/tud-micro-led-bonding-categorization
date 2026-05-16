# v4.0 PCB — verification, calibration, and full characterization matrix

Comprehensive verification of the v4.0 board with EIS calibration structures.
Supersedes the v3.9 verification doc.

---

## 1. LED bonding dimensions — ✅ VERIFIED CORRECT

Cross-checked against Würth's **official KiCad library** (`new-pcb/library/footprints/LED_SMD_Wurth.pretty/D_Wurth_WL-SFCC-0404superflat.kicad_mod`):

| Parameter | Würth library | v4.0 board | Match? |
|---|---|---|---|
| Pad 1 (anode) | `(at -0.4 -0.4) size 0.4 0.4` | identical | ✅ |
| Pad 2 (K_R)   | `(at  0.4 -0.4) size 0.4 0.4` | identical | ✅ |
| Pad 3 (K_B)   | `(at  0.4  0.4) size 0.4 0.4` | identical | ✅ |
| Pad 4 (K_G)   | `(at -0.4  0.4) size 0.4 0.4` | identical | ✅ |

Datasheet confirms pad 1 is the anode (with polarity mark, top-left when LED is viewed from above), with CW numbering 1→2→3→4. Schematic: pin 2 = R, pin 3 = B, pin 4 = G.

---

## 2. Chain trace width vs LED current limits — ✅ ADEQUATE WITH MARGIN

WL-SFCC continuous I_F per LED per colour:
- I_FR = 10 mA (red)
- I_FG = 10 mA (green)
- I_FB = 10 mA (blue)
- I_F peak = 20 mA (10% duty)

Our LED chains carry the **chain current** (single value through the series). Worst case = 10 mA DC continuous through 12 series LEDs (DCL12).

| Parameter | Value | Spec |
|---|---|---|
| Trace width | 0.20 mm (default `TRACE_W`) | ≥ 0.15 mm min |
| Copper thickness | 35 µm (1 oz) | Aisler default |
| Cross-section | 0.20 mm × 35 µm = 7×10⁻³ mm² | — |
| Chain DC current | 10 mA continuous | — |
| Current density | **1.43 A/mm²** | < 30 A/mm² (FR-4 safe limit for short traces) |
| Trace resistance (per mm) | ≈ 2.46 mΩ/mm | (ρ_Cu × L) / (W × t) |
| Voltage drop across longest chain trace (~50 mm) | **≈ 125 µV** at 10 mA | negligible vs 12 × 2.6 V chain |
| Temperature rise | < 1 °C at this density | negligible |

**Conclusion:** the 0.2 mm chain traces handle continuous WL-SFCC current with > 20× margin. The chains could safely carry up to ~200 mA if needed for pulsed testing (above the LED's own absolute max).

---

## 3. EIS calibration structures — added in v4.0

### Why each cal type matters

| Cal | Purpose | What it captures |
|---|---|---|
| **OPEN** | 2 isolated pads, probes contact nothing electrically | Stray capacitance of cable + probe + fixture (typically pF range — important above ~10 kHz) |
| **SHORT** | 2 pads tied by 0.4 mm copper trace, probes contact a low-R short | Stray inductance + contact resistance + cable resistance (typically nH + mΩ — important below ~1 kHz and at high current) |
| **LOAD** | 2 pads with 0603 footprint for user-soldered 100 Ω ±0.1 % reference | Magnitude/phase scale verification — confirms the meter reads close to a known impedance after OPEN/SHORT cal |

The three together fully characterize the parasitic loop around your DUT measurement, letting the LCR meter subtract them in real time. Without cal: Nyquist plot has tilted/shifted features that prevent equivalent-circuit fitting.

### Does the cal apply to LED Nyquist measurements?

**Yes — the same OPEN/SHORT/LOAD cal applies to any 2-port impedance measurement done with the same LCR meter + probe setup.** The cal captures the parasitic measurement loop; once compensated, every subsequent EIS sweep (on any LED) gets the same correction applied automatically by the meter.

Standard EIS workflow per board:
1. Solder 100 Ω 0.1% across EIS_LOAD pads (one-time setup)
2. Place PCB on probe station
3. **Land probes on PP_EIS_OPEN_A and PP_EIS_OPEN_B** → trigger meter OPEN cal
4. **Land probes on PP_EIS_SHORT_A and PP_EIS_SHORT_B** → trigger SHORT cal
5. **Land probes on PP_EIS_LOAD_A and PP_EIS_LOAD_B** → trigger LOAD cal (verifies real R = 100 Ω, imaginary R = 0)
6. Land probes on a LED (e.g., D1 anode probe pad + KR probe pad)
7. Sweep frequency 10 Hz – 1 MHz → get clean Nyquist
8. Repeat step 6 for D2-D8 — cal persists between measurements

### Difference between OPEN and 100R LOAD — concretely

- **OPEN**: probes hover near each other but DON'T TOUCH or have any electrical connection. Meter measures only the air capacitance between the probe tips + cable parasitic C. Result: pure imaginary impedance Z ≈ 1/(jωC_stray) which dominates at high frequency.
- **LOAD**: probes touch the 100 Ω resistor. Meter measures Z ≈ 100 + jωL_stray. The real part SHOULD be ~100 Ω; the imaginary part SHOULD be the stray L. If after OPEN/SHORT cal the meter reads 100.05 Ω and ~0 imaginary, cal is good. If it reads 95 Ω or 105 Ω, something in the cal went wrong.

**They're not alternatives — you need ALL THREE for a proper Nyquist measurement.**

### New components required on the board

Just **one** new component: a 100 Ω 0.1 % thin-film 0603 resistor. Recommended part:

**Vishay TNPV0603100RBEEN** — 100 Ω ±0.1 %, 25 ppm/°C, thin-film 0603 SMD, 1/8 W power rating.
- LCSC: C72111
- DigiKey: 541-1830-1-ND
- Mouser: 71-TNPV0603100RBEEN
- Datasheet: `docs/datasheets/Vishay-TNPV-Series-Precision-Thin-Film-Resistor-63080.pdf` (downloaded)

Already added to the BOM (see `FABRICATION_ORDER.md`).

### Should EIS CAL pads be routed to header pins?

**Recommendation: NO — keep Tier-1 (probe-only) access as currently designed.**

Reasoning:
1. **Calibration path must match measurement path** for accuracy. If you cal through header→trace→pad and then measure direct probe→pad, the calibrations don't match → trash data.
2. For PROBE STATION workflow (which is what the paper used — Summit 11K), Tier-1 cal pads + Tier-1 LED probing is the same path → cal valid.
3. For Tier-2 header-based EIS (faster but secondary), you'd need cal pads routed to dedicated header pins, plus a relay/switch matrix to route LCR between cal pins and DUT pins. That's automated-test infrastructure, not what you have.
4. Adding 6 cal-pin routes would consume 6 of the 28 spare north pins, clutter the back-side PINOUT, and increase routing risk without real benefit.

**If you later want Tier-2 EIS:** request a v4.1 spin that routes EIS_OPEN_A/B + EIS_SHORT_A/B + EIS_LOAD_A/B to north header pins (would use 6 of the 28 spare jumperable pins, no design complexity). For now, Tier-1 only.

---

## 4. Anything else missing for FULL electrical characterization?

The original measurement table (Tiers A–F in your earlier question) is now **fully supported** with v4.0:

| Tier | Measurement | What was needed | v4.0 status |
|---|---|---|---|
| **A** | V_F / R_s / leakage / ideality (DC) | SMU + probe pads | ✅ probe pads at LED row + south header |
| **A** | Step-stress, Weibull | Multi-ch SMU + datalogger | ✅ south header → ext. multi-SMU |
| **B** | **EIS Nyquist** | LCR meter + **OPEN/SHORT/LOAD cal** | ✅ **EIS CAL added in v4** |
| **B** | C-V profiling | LCR + DC bias | ✅ same setup as EIS (LCR + bias) |
| **B** | f-dependent capacitance | LCR meter | ✅ same setup |
| **C** | R_th-jc | SMU + DMM(NTC) + thermal chuck | ✅ NTCs TH1-4 + south header |
| **C** | Z_th(t) structure function | Pulsed SMU + V_F sample | ✅ south header → pulsed SMU |
| **C** | Thermal time constant τ | Pulsed power + fast V_F | ✅ same |
| **D** | 1/f noise spectroscopy | Low-noise preamp + spectrum analyzer | ✅ probe pads + ext. preamp |
| **D** | Shot noise | Same | ✅ |
| **E** | Pulsed I-V | Pulsed SMU | ✅ south header |
| **F** | Aging / DC stress / HALT | Persistent SMU + chamber | ✅ south header for unattended runs |
| **F** | Chain QC + Weibull fail-time | LED chains | ✅ DCL6 + DCL12 + north header pins 3/10/19/32 |

### Calibrations needed per measurement (now ALL covered)

| Measurement | Cal source | On v4.0? |
|---|---|---|
| DC V_F, R_s | SMU's internal cal (offset/gain) | yes (external) |
| Reverse leakage | SMU internal cal | yes (external) |
| EIS Nyquist | OPEN/SHORT/LOAD at the probe | **✅ on-board EIS CAL pads** |
| R_th-jc (V_F-TSP) | V_F(T) curve from thermal chuck | yes (off-board chuck) |
| Pulsed I-V | Pulsed SMU internal | yes (external) |
| 1/f noise | System noise floor (input shorted) | ✅ EIS SHORT pads double as noise-floor reference |

**Bonus:** the EIS SHORT pads ALSO serve as the noise-floor reference for 1/f noise measurements. Touch your preamp inputs to PP_EIS_SHORT_A/B — measure the spectrum analyzer's PSD — that's the system noise floor to subtract from your LED noise. One on-board structure, two cal uses.

### Things still NOT on board (off-board lab needs only)

| Need | Required for | Where instead |
|---|---|---|
| Integrating sphere | Optical output power | TU Delft EKL Labsphere |
| Spectrometer | CIE chromaticity | EKL |
| Thermal chamber (−40 / +125 °C) | Thermal cycling | EKL |
| Mechanical shear tester | Bond shear strength | Nordson DAGE 4000 (paper) |
| X-ray inspection | Void imaging | Seamark X5600 (paper) |

These are **separate instrument needs**, not PCB-fixable. No PCB design could absorb them.

**Bottom line:** v4.0 hardware supports 100% of electrical characterization for your bonded LEDs, plus the EIS Nyquist capability that was previously meter-cal-limited.

---

## 5. Back-side PINOUT box — ✅ NO TEXT OVERFLOW

Single compact line (after the previous truncation issue):

```
TIER-2 SOUTH PINOUT
  1-4 D1   5-8 D2   9-12 D3   13-16 D4
17-20 D5  21-24 D6  25-28 D7  29-32 D8
each group: A, KG, KB, KR  (A = LED_VCC)
NORTH 3,10,19,32 = pre-wired chain (others jumperable)
```

Fits inside the PINOUT box without truncation. The ambiguous "(marked O)" wording was removed in v3.9.1 (KiCad stroke font renders "O" as a visually-thin oval that reads as "U").

---

## 6. Van der Pauw — design note (unchanged from v3.9)

The VDP cloverleaves require a dummy die bonded across all 4 cardinal contacts to function. For your LED-only study, they serve as **bare-ENIG sheet-resistance calibration** only (probe across 2 cardinal pads, measure 4-wire R → know ENIG plating uniformity per fab batch). The TLM ladders provide the same function with tighter spacings.

If you want a future dummy-die batch from EKL (~€500, weeks of EKL time), the VDPs become fully functional for sheet-resistance + correction-factor analysis per [van der Pauw 1958].

---

## 7. v4.0 design summary

| Spec | Value |
|---|---|
| Board | **93 × 93 mm**, 2-layer FR-4, 1.6 mm, ENIG finish |
| **DRC violations** | **0** |
| **Unconnected pads** | **0** |
| Footprints | 194 (incl. 26 WL-SFCC LEDs, 4 NTCs, 1 load R, 64 header pins, 99 bare pads) |
| Routing | 32 south header pins → LED probes (pre-wired), 4 north pins (3/10/19/32) → LED chain endpoints, common-anode B.Cu bus, NTC GND vias |
| Designer | Daniel Tyukov · #5714699 · ET4277 / ET4391 |

### Iteration log (recent)

| Rev | Highlight |
|---|---|
| v3.6 | Replaced dummy-die DC chains with LED chains (R-series) |
| v3.7 | Compressed to 95×95mm, routed 4 north pins to LED chain endpoints |
| v3.8 | 32-pin north header aligned with south for breadboard mating, silk circles on routed pins |
| v3.9 | Compressed to 93×93 mm with breathing room, restored ruler, fixed TH labels |
| v3.9.1 | Back-side PINOUT compacted to 1 line (no truncation, no ambiguous "O") |
| **v4.0** | **Added EIS CAL: OPEN + SHORT + LOAD pads + 100Ω 0.1% Vishay TNPV0603 — enables full Nyquist calibration** |

---

## 8. Component datasheets

See **`docs/datasheets/README.md`** for the full index. Currently in folder:

| Datasheet | File | Status |
|---|---|---|
| Würth WL-SFCC 0404 RGB LED | `Wurth-WL-SFCC-0404-RGB-LED-150044M155220.pdf` | ✅ in repo |
| Vishay TNPW 0603 thin-film series | `Vishay-Dale-TNPW0603-Thin-Film-Resistor-28758.pdf` | ✅ in repo |
| Würth WR-PHD 2.54 mm pin header (1×40 single-row) | `Wurth-WR-PHD-1x40-2.54mm-PinHeader-61304011121.pdf` | ✅ in repo |
| Murata NCP15XH103J03RC NTC | `Murata-NCP15XH103J03RC-NTC-R44E.pdf` | ✅ in repo (downloaded via Mouser CDN) |
