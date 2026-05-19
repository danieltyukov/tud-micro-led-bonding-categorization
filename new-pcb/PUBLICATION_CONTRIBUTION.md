# Publication Contribution Plan — building on Abdelwahab ECTC 2025

> **As-built note (May 2026):** The v2 board ordered through Eurocircuits is a simplified LED-bonding-only version. Sections of this plan that depended on TLM/VDP/DoE bare-pad test structures (now removed from the layout) are forward-looking for a future revision. The four-point V_F + NTC thermometry contribution is still supported by the as-built board.

What new science the v2 PCB enables vs what was already published in
[Abdelwahab 2025] *"Pick-and-Release: A Novel Contactless Bonding Method for
Die Attachment"* (ECTC 2025, pp. 2125–2132). Companion to
`ELECTRICAL_CHARACTERIZATION.md` (the how) and `V2_DESIGN_NOTES.md` (the what).

---

## 1. What the paper actually measured electrically (§V-E)

| Measurement | Quantity extracted | On what |
|---|---|---|
| DC chain resistance, N = 6 in series | Per-bond R, 0.20–0.38 Ω | **Dummy** Si dies (Ag/Au/Cu finish) |
| VDP sheet resistance | ENIG ρ_eff = 2.94 × 10⁻⁵ Ω·m | Bare PCB pads |
| TLM contact resistivity ρ_c | Slightly higher pressureless | **Dummy** Si dies |
| **RGB LEDs** | **"used to verify whether current flows"** ← qualitative go/no-go only | Real LEDs |

**Critical observation:** the paper does **zero quantitative electrical
characterization on the LEDs themselves**. They lit them up — that's it. They
tested **one** solder paste (TS391LT Sn42Bi57.6Ag0.4). They report **no**
reliability, **no** thermal, **no** AC, **no** pulsed data. Their own "future
work" calls out standardized commercial chips — exactly what your WL-SFCC
LEDs are.

That is the entire publication-contribution surface for v2.

---

## 2. Tier-1 contributions — direct extensions (fast paper, 3–6 months)

These follow the paper's methodology one-to-one but apply it to real LEDs.

| Measurement | What it adds | v2 hardware needed |
|---|---|---|
| **V_F at I_F = 10 mA, per LED, per colour** (R/G/B) | First quantitative LED-side metric. Joint R adds on top of intrinsic V_F (R ≈ 2.0 V, G/B ≈ 3.0 V). | 32 LED signals routed to south header (✓ present) |
| **Full I-V sweep 0–20 mA, extract R_s** | R_s = dV/dI in the linear regime above the knee is directly **bond + trace resistance** since LED's intrinsic R_s is fab-stable across a reel. | SMU + 2 header pins per LED colour (✓) |
| **Solder paste comparison matrix** | Paper tested **1** paste. Repeat with SAC305, Sn96.5Ag3Cu0.5, In-based, sintered Ag, conductive epoxy — fills the explicit "future work" gap. | Same board geometry, different cleanroom runs (✓) |
| **Reverse leakage at −5 V** | Non-destructive ESD-damage / shunt-path detector. Paper saw "Cu adhesion failure" only post-shear — leakage detects it without breaking the part. | SMU reverse-bias, µA range (✓ via header) |
| **8-LED daisy-chain go/no-go** | Faster QC: chain dark = at least 1 of 16 bonds failed. | External jumpers on south-header pins to wire 8 LEDs in series (✓ doable, but requires wiring outside PCB) |

**Tier-1 headline title:**
*"Functional micro-LED bond characterization across solder formulations and
die finishes — extending pick-and-release methodology to commercial RGB LEDs"*

---

## 3. Tier-2 contributions — novel beyond the paper (each = standalone publication)

| Measurement | Why it's new | What it produces |
|---|---|---|
| **V_F-TSP — Forward-Voltage Thermal Sensing Parameter** | LED's V_F drifts ≈ −2 mV/°C → the LED is its own thermometer. NTCs at TH1–TH4 give substrate T. **R_th-jc = (T_j − T_c) / P_diss.** Paper has no thermal data at all. | Bond thermal resistance per solder/finish — the single most reliability-relevant number for LEDs |
| **AC impedance spectroscopy (EIS), 10 Hz – 1 MHz** | Voided/cracked joints have a distinct Nyquist signature. Paper's X-ray was contrast-limited and they admitted it. EIS is the non-destructive electrical analogue. | Nyquist plot → equivalent-circuit fit (R_bond + C_void) |
| **Pulsed I-V (1–100 µs)** | Eliminates self-heating. (R_s_pulsed − R_s_DC) = thermal contribution to apparent bond R. Decomposes electrical vs thermal bond contributions. | Pulsed I-V curves, dynamic R extraction |
| **Long-term V_F drift under DC stress** | 100–1000 h at I_F = constant, track V_F → bond degradation kinetics (intermetallic growth, void coalescence). Paper has **zero reliability data**. | Aging curves per solder/finish |
| **Ideality factor n from low-current Shockley fit** | n > 1 indicates non-ideal recombination at the die boundary — sensitive to interface contamination from poor wetting. | Indirect probe of die-side bond quality |

**Tier-2 paper titles (any one of these is publishable solo):**
- *"Junction-to-case thermal resistance of micro-LED bonds: a forward-voltage thermometry study"* ← highest-impact
- *"Non-destructive bond quality assessment of micro-LEDs via AC impedance spectroscopy"*
- *"Long-term reliability of pick-and-release bonded micro-LEDs under DC and thermal-cycle stress"*

---

## 4. Tier-3 contribution — methodology paper (highest novelty, needs dummy dies)

The unanswered question in [Abdelwahab 2025]: **does ρ_c measured on dummy-die
TLM ladders actually predict R_s of functional bonded LEDs?**

v2 has both structures on the same board, same fab lot, same paste, same
reflow → plot ρ_c(TLM) vs R_s(LED) per condition:

- **If they correlate** → validates the paper's methodology, strengthens its
  citation impact across the field.
- **If they don't** → reveals where dummy-die testing fails for real devices,
  carves out a "functional-device-required" methodology niche.

Either outcome is publishable. **Blocker:** you don't currently have dummy
Si dies — the test structures are present on v2 but unfunded for this study.
Tier-3 only unlocks if EKL fabricates a wafer of Ag / Au / Cu dummy dies
later (sub-€500, weeks of EKL time).

**Tier-3 paper title:**
*"Validity of dummy-die bond characterization for predicting functional
micro-LED performance"*

---

## 5. What the v2 PCB does NOT enable (off-board needs)

| Measurement | Why not on PCB | Where instead |
|---|---|---|
| Optical output power | Needs integrating sphere | Off-board Labsphere / Gigahertz-Optik |
| Spectral power distribution | Spectrometer setup | Off-board (CIE colourimetry) |
| Thermal cycling (ΔT = -40 → 125 °C) | Needs environmental chamber | Off-board (TU Delft EKL thermal chamber) |
| Mechanical die-shear strength | Destructive | Off-board Nordson DAGE 4000 (already in paper flow) |
| X-ray void inspection | External imaging | Off-board Seamark X5600 (already in paper flow) |
| Cross-sectional microscopy (SEM/EDS) | Destructive grinding+polishing | Off-board EKL (already in paper flow) |

These are **complements** to electrical measurements, not substitutes.

---

## 6. Hardware enablement per measurement (concise)

| Measurement | v2 hardware path | Status |
|---|---|---|
| V_F per LED/colour | South header pins → 4-wire via probe-pad + header-pin combination | ✅ enabled |
| I-V sweep + R_s extraction | Same as above | ✅ enabled |
| Solder-paste comparison | Geometry-agnostic, multi-board runs | ✅ enabled |
| Reverse leakage | South header → SMU reverse-bias | ✅ enabled |
| 8-LED series daisy-chain QC | Jumpers between adjacent south-header cathodes | ✅ enabled (external wiring) |
| V_F-TSP thermal resistance | NTCs TH1–TH4 + LED V_F probe | ✅ enabled (needs off-board thermal-chuck calibration) |
| AC impedance spectroscopy (EIS) | South header → LCR meter | ✅ enabled (needs LCR meter, e.g. Hioki IM3536) |
| Pulsed I-V | South header → pulsed SMU | ✅ enabled (needs pulsed-capable SMU, e.g. Keithley 2461) |
| Long-term V_F drift / aging | South header → persistent fixture | ✅ enabled |
| Ideality factor n | I-V sub-mA Shockley fit | ✅ enabled |
| Cross-validate vs dummy-die | TLM/VDP/DC structures present on v2 | ⚠ enabled but blocked: no dummy dies available |

---

## 7. Recommended headline contribution

If you have ~6–9 months and TU Delft EKL kit access, the strongest single
paper combines:

1. **Tier-1 R_s extraction across 3–4 paste formulations** (foundation)
2. **Tier-2 R_th-jc via V_F-TSP** (novelty)
3. **Short reliability section** — 1000 h × 2 paste conditions (impact)

Suggested title: *"Thermal and electrical characterization of pick-and-release
bonded micro-LEDs across solder formulations"*

Target venue: **ECTC 2026** (continues the same conference lineage) or
**IEEE T-CPMT** (journal extension with longer reliability section).
Cites [Abdelwahab 2025] as foundational; positions your work as the natural
extension from *"we proved current flows"* to *"here is how the bond actually
performs over time and under heat."*

---

## 8. Bench tooling required per tier

| Tier | Must-have | Already at TU Delft EKL? |
|---|---|---|
| 1 | SMU (Keithley 2400/2450/2461) + probe station + headers | ✓ (Summit 11K/12K used in paper) |
| 2 — V_F-TSP | + thermal chuck or hot-plate with feedback for V_F(T) calibration | ✓ EKL standard |
| 2 — EIS | + LCR / impedance analyser (Hioki IM3536, Keysight E4990A) | usually ✓; confirm with ECTM group |
| 2 — Pulsed I-V | + pulsed-capable SMU (Keithley 2461) | possibly; confirm |
| 2 — Aging | + multi-channel SMU or relay matrix for unattended 1000 h soak | ✓ Keithley 2602B / 707B |
| 3 — Methodology | + dummy-die wafer (Ag/Au/Cu) | ✗ requires EKL fab run |
