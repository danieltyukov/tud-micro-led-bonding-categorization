# Electrical Characterization Plan — v2 PCB

How the v2 board enables electrical characterization of LED bonds made with
different bonding materials. Companion to `PCB_DESIGN_PLAN.md`.

---

## 1. The measurement problem

When you put a current through an LED bonded to the PCB, the voltage you
read at the probe tips is

  V_measured = V_F(LED) + V_joint_anode + V_joint_cathode + V_traces + V_probes

To compare bonding materials we need **V_joint** alone. That means:

1. **Strip V_probes and V_traces** → use **4-wire (Kelvin)** sensing.
2. **Strip V_F(LED)** → measure structures **without an LED in the loop**
   (TLM, Van der Pauw, dummy-die daisy chain) on the *same board*, *same
   fab lot*, *same paste / die finish*, so the only delta is the bond
   material/process being studied.
3. **Strip thermal drift** → ramp current slow, hold steady, average; use
   the SMU's built-in NPLC ≥ 10 averaging.

Everything below derives from this. The board is a vehicle that exposes
each contribution **separately**.

---

## 2. What we can measure

### 2.1 On the LED row (real RGB LEDs)

| Metric                        | What it tells you                                          | How                                                  |
|------------------------------|-------------------------------------------------------------|------------------------------------------------------|
| **V_F at I_F = 10 mA**        | Joint quality (poor bond → extra V drop)                    | Source 10 mA, measure V; 4-wire on golden samples    |
| **I_F at fixed V_F**          | Same info inverted; sometimes more sensitive                | Source V, measure I                                  |
| **I-V curve (0 → 20 mA)**     | Series resistance R_s = dV/dI in the linear regime          | Sweep I, fit linear region above knee                |
| **R_s extraction**            | **Directly the joint resistance** (LED's intrinsic R_s is fab-stable across a reel) | From I-V fit |
| **Reverse leakage at -5 V**   | ESD damage screen / shunt path through cracked die          | Apply −5 V, measure µA                               |
| **V_F drift under stress**   | Bond reliability under thermal / current cycling            | Hold I = I_F for hours; track V; or thermal cycle    |
| **Forward-current "diode go/no-go"** | Crude check that all 4 bonds are intact              | Light up R, G, B individually with 10 mA; eye check  |

Each LED has its **R = 2.0 V**, **G = 3.0 V**, **B = 3.0 V** nominal V_F at
10 mA, so the joint contribution is on top of those baselines.

### 2.2 On the LED daisy-chain row (4 LEDs in series via their bond joints)

Light goes off if any one of the 8 bonds in the chain fails → fastest
visual go/no-go for an assembly run. Quantitatively, the total V at
fixed I includes 8 × V_joint, so the average joint V drop per bond is

  V_joint_avg = (V_chain_measured − 4 × V_F_LED_reference) / 8

with the LED reference taken from the parallel LED row.

### 2.3 On the dummy-die structures (no LED in loop)

These are the **clean** measurements — no LED I-V to subtract.

| Structure       | Quantity extracted                              | Equation                                                  |
|-----------------|--------------------------------------------------|-----------------------------------------------------------|
| **Daisy chain N=6/12/24** | Mean per-bond resistance R_b           | R_b = (V/I − R_traces) / (2 × N)  (×2 because each die has top + bottom contact) |
| **Van der Pauw**          | Sheet resistance R_sh of the PCB pad metal | π/ln 2 · V/I, four-symmetric reads                       |
| **TLM ladder**            | **Contact resistivity ρ_c** of the joint  | Slope-intercept of R_total vs. contact spacing; ρ_c = R_c · W · a (paper Eq. 2) |
| **DoE bond-pad sites**    | Single-bond resistance per (shape, R, finish) | 4-wire 2-pad measurement, n ≥ 5 per cell                |

The DoE per-site measurements are what build the **bonding-material
comparison matrix**: identical board, only the paste / die finish /
process changes between fab runs, and the same 100 sites get re-measured.

### 2.4 Mechanical (not electrical, but pairs with it)

- **Die-shear strength** (Nordson DAGE 4000) at the *same* sites after
  electrical → correlate R_b with shear strength.
- The paper found Ag dies have the highest shear (42.99 MPa) **and** the
  lowest chain resistance — strong correlation.

---

## 3. Comparing bonding materials

For a meaningful comparison **everything except the bond material must be
identical**:

| Variable                       | Strategy                                                          |
|--------------------------------|-------------------------------------------------------------------|
| PCB fab lot                    | Order all boards in **one Eurocircuits lot**; record batch ID     |
| ENIG plating thickness         | Same as above (the Ni / Au thicknesses dominate ρ_c)              |
| Stencil aperture geometry      | Same stencil for every variant in a comparison                    |
| Paste type / lot               | **The thing being varied** — log lot, expiry, viscosity at print  |
| Die finish (Cu / Au / Ag / …)  | **The other thing being varied** — log wafer ID                   |
| Reflow profile                 | Same profile, recorded with a thermocouple in the chamber         |
| Pressure (P&P) vs. pressureless (P&R) | Both, on every condition, on separate board halves         |
| Operator / day                 | Random-assign sites to boards; track date/time per site           |

What you get out is a CSV with one row per bonded site:

```csv
site_id, shape, R_um, mini_pads, die_finish, paste_type, paste_lot,
mounting_method, mounting_pressure_MPa, reflow_profile_id,
R_bond_ohm, V_F_at_10mA_V, R_s_LED_ohm, BLT_um, tilt_high_deg,
tilt_low_deg, shear_MPa, void_pct, fail_mode
```

Then ANOVA / mixed-effects model on (R_bond_ohm) ~ (paste × finish × method
+ shape + mini_pads + ...). The board hands you data; the statistics
package extracts the bond-material effect.

---

## 4. Ports / connectors on the board

The board has **three** electrical access tiers — pick whichever suits the
measurement at hand. All three live on the *same* board so one design
serves manual exploration and automated bench testing.

### 4.1 Tier 1 — Manual probe pads (always present)

- **1.27 × 1.27 mm gold (ENIG) probe pads** around the perimeter of each
  structure, spaced **2.54 mm centre-to-centre**.
- Compatible with manual tungsten / BeCu probes on the **Summit 11K/12K
  probe station** (which the paper already uses).
- 4 wires per structure where it matters: **Force-High / Sense-High /
  Sense-Low / Force-Low** clearly silkscreened "FH / SH / SL / FL".
- Cheapest, most flexible, **slowest**. Used for ad-hoc / characterization
  / failure analysis.

### 4.2 Tier 2 — Soldered pin-header rows (optional, populate as needed)

- Two **2.54 mm pitch** through-hole rows along the north and south edges
  of the board, **40 pins** each.
- A user can solder a standard 0.1" header and plug the board into a
  benchtop fixture (ribbon cable to a breakout box, or directly into a
  Keithley 2602B's Mini-DIN inputs).
- Pin mapping:
  - 1–8: Force-High of the 8 LEDs.
  - 9–16: Sense-High of the 8 LEDs.
  - 17–24: Cathode-R / G / B per-LED.
  - 25–28: Common anodes (×4 for redundancy).
  - 29–34: Daisy chains 4-wire (FH / SH / SL / FL × 3 chains).
  - 35–40: TLM ladders' end fingers.
- This makes **repeated I-V sweeps and lifetime tests** practical (no
  re-landing 8 probes for every measurement).

### 4.3 Tier 3 — Edge connector (optional, only if Tier 2 isn't enough)

- A 30-pin **0.5 mm pitch FFC / FPC** card-edge or 2-row **2 mm pitch
  Molex Pico-Lock** on the east edge, exposing the **8 LED Force/Sense
  lines** and the **3 daisy chains' 4-wire ports**.
- Pairs with a fixture board carrying the SMU connectors so the test PCB
  can be hot-swapped without re-cabling each time.
- **Only populated** on the "characterization-rig" board variant —
  metrology / clean-room boards skip this to keep the assembly side flat.

### 4.4 What gets which tier

| Structure                              | Tier 1 | Tier 2 | Tier 3 |
|----------------------------------------|:------:|:------:|:------:|
| 100-site DoE bond-pad array            |  ✓     |        |        |
| 3 daisy chains (N=6/12/24)             |  ✓     |  ✓     |  ✓     |
| 4 Van der Pauw structures              |  ✓     |        |        |
| 3 TLM ladders (W=0.25/0.5/1.0 mm)      |  ✓     |  partial (end fingers only) | |
| 8 LEDs + 4 LED daisy chain             |  ✓     |  ✓     |  ✓     |
| Fiducials / mm-µm ruler                |   —    |   —    |   —    |

Rationale: the 100-site DoE array is by far the most pads, and only
needs manual measurement because each site is one-shot (you measure
once, then it gets shear-tested). The LEDs and daisy chains, on the
other hand, get measured **repeatedly** during lifetime studies — they
get all three tiers.

### 4.5 Pin / pad layout summary (target counts)

| Tier  | Element                                | Count                      |
|-------|----------------------------------------|----------------------------|
| 1     | 1.27 mm ENIG probe pads                | ~280 (=4 × 70 structures)  |
| 2     | 2.54 mm through-hole header positions  | 80 (2 rows × 40)           |
| 3     | Edge / FFC connector signals           | 30 (1 connector)           |
| —     | Fiducials                              | 5 (4 corner + 1 L-shape)   |

---

## 5. Lab tooling — what you need (TU Delft EKL has most of it)

### 5.1 Must-have, day one

| Tool                              | Why you need it                                   | TU Delft / paper equivalent                 |
|-----------------------------------|---------------------------------------------------|---------------------------------------------|
| **SMU (Source-Measure Unit)**     | 4-wire I-V sweep, single-channel                  | Keithley 2400 / 2450 / 2461                 |
| **Probe station**                 | Land 4 probes on 1.27 mm pads                     | Summit 11K/12K (paper §V-E)                 |
| **Tungsten / BeCu probe needles** | 5–25 µm tip for the LED's 0.275 mm pads           | PicoProbe / Microprobes — stock-available   |
| **Stereo microscope (10×–30×)**   | Land probes; visually inspect joints              | EKL standard equipment                      |
| **Bench DMM**                     | Spot R measurements, continuity                   | Keithley DMM6500 / Fluke 8846A              |
| **Digital camera + ring light**   | Capture LED colour / intensity                    | DSLR + macro lens; or USB microscope cam    |

This kit alone gets you: V_F, I_F, R_s, simple chain resistance, VDP, TLM
slope, leakage, **all the headline metrics in §2**.

### 5.2 Nice-to-have (better statistics, faster, automation)

| Tool                                   | What it unlocks                                            |
|----------------------------------------|------------------------------------------------------------|
| **Multi-channel SMU** (Keithley 2602B) | Sweep 8 LEDs in parallel, lifetime studies                 |
| **Switch matrix** (Keithley 707B / 3706A) | Auto-route one SMU to many channels — replaces re-probing  |
| **LCR meter** (Hioki IM3536)           | AC impedance / capacitance — picks up cracked-joint shunts |
| **Curve tracer** (Keithley 4200A-SCS)  | Fast I-V over many decades of current                      |
| **Thermal chuck / thermal chamber**    | T-cycle accelerated lifetime; V_F vs. T                     |
| **Integrating sphere + power meter**   | Optical efficiency, ties electrical to optical perf        |
| **Phantom V711 high-speed cam**        | Already on Tresky; documents the bonding event             |

### 5.3 Already in the paper's flow (don't re-buy)

- **Tresky T-3000-PRO** die bonder (assembly).
- **Keyence VK-X250** 3D laser microscope (BLT, tilt, contact angle).
- **Seamark X5600 Off-line X-Ray** (voiding).
- **Nordson DAGE 4000 Bondtester** (die shear).
- **CDE ResMap 178** (sheet R on die wafers).
- **SEM + EDS** (failure analysis).

---

## 6. End-to-end characterization workflow

The board is the deliverable; here's how a single comparison run uses it.

```
┌────────────────────────────────────────────────────────────────────────────┐
│ INPUT: 4 boards × {paste A, paste B} × {Ag-finish die, Cu-finish die}      │
│        = 16 boards total                                                   │
└────────────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        ▼                                           ▼
┌───────────────────┐                    ┌───────────────────────────┐
│ Paste-print step  │                    │ Pre-bond electrical: VDP, │
│ (eC-stencil-mate) │                    │ TLM open-circuit baseline │
└────────┬──────────┘                    └────────────┬──────────────┘
         ▼                                            ▼
┌──────────────────────┐               ┌────────────────────────────────┐
│ Die bonding (Tresky) │               │ Geometric pre-check: stencil   │
│ Pressureless P&R     │               │ paste volume (Keyence VK-X250) │
│ + Pressure P&P refs  │               └────────────────────────────────┘
└────────┬─────────────┘
         ▼
┌────────────────────────┐
│ Reflow on hot-plate    │
│ (paper §III-A profile) │
└────────┬───────────────┘
         ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ Post-bond electrical (the meat):                                          │
│                                                                            │
│ 1. SMU + probe station → 4-wire V_F at 10 mA on every LED                  │
│ 2. SMU sweep 0…20 mA → I-V curves, extract R_s per LED                     │
│ 3. SMU + manual probe → chain resistance on DC-6 / DC-12 / DC-24           │
│ 4. SMU + manual probe → R_total per TLM finger spacing → slope = R_sh,     │
│    intercept × W = R_c → ρ_c = R_c·W·a (paper Eq. 2)                       │
│ 5. SMU + manual probe → VDP 4-symmetric → R_sh of PCB ENIG (cross-check)   │
│ 6. SMU at each DoE site (one I/V point at 1 mA) → R_bond per geometry      │
└─────────────────────────────┬────────────────────────────────────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ Geometric metrology (Keyence VK-X250):                                    │
│  BLT, tilt-X, tilt-Y, joint volume per site                               │
└─────────────────────────────┬────────────────────────────────────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ X-ray inspection (Seamark X5600): void percentage per site                │
└─────────────────────────────┬────────────────────────────────────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ Mechanical (Nordson DAGE 4000): die-shear strength per site               │
│   (destructive — comes last)                                              │
└─────────────────────────────┬────────────────────────────────────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ SEM + EDS on the failed shear surfaces: failure mode per condition       │
└─────────────────────────────┬────────────────────────────────────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ Master CSV: 16 boards × 100 sites = 1600 rows; one analysis notebook     │
└──────────────────────────────────────────────────────────────────────────┘
```

This is identical to the v1 paper's workflow except that the board is
**designed** to make each step easier and the connectors make the
post-bond electrical measurements *fast enough* that you can afford to
run 16 boards instead of 4.

---

## 7. What ports on the board for what measurement (cheat-sheet)

| You want to measure …                         | Use these pads / connectors                                       |
|-----------------------------------------------|-------------------------------------------------------------------|
| One LED's V_F at 10 mA (Kelvin)               | Tier-1 FH/SH/SL/FL on the LED row, **or** Tier-2 header pins 1/9/17/25 |
| All 8 LEDs' V_F in parallel                   | Tier-2 header → ribbon cable → multi-channel SMU                  |
| LED daisy chain go/no-go                      | Tier-1 or Tier-2 FH/FL on `LED-CHAIN` net                         |
| Daisy chain N=6/12/24 resistance              | Tier-1 4 pads at chain ends, **or** Tier-2 pins 29–34              |
| TLM contact resistivity                       | Tier-1 only (one ladder = 7 fingers × 2 sense-points = 14 probes) |
| Van der Pauw sheet resistance                 | Tier-1 only (4 contacts per cloverleaf)                           |
| Single bond-pad resistance (DoE)              | Tier-1 only, 4 pads per site                                       |
| Lifetime stress on the LED row                | Tier-2 ribbon → fixture → multi-SMU                                |
| Hot-swap board into a fixture                 | Tier-3 edge connector                                              |

---

## 8. Failure modes the board can detect electrically

A "bad bond" looks different to the multimeter depending on how it
failed. The board separates these:

| Failure                          | Symptom                                                                  | Caught by                          |
|----------------------------------|---------------------------------------------------------------------------|------------------------------------|
| **Open** (no contact)            | Infinite R, LED dark                                                      | Continuity, daisy chain open       |
| **Cold joint** (high R)          | Extra Ω in series, V_F up, R_s up                                         | I-V slope, TLM intercept           |
| **Cracked die / shunt**           | Reverse leakage µA, I at low V_F                                          | Reverse-bias leak test             |
| **Tilted die, partial contact**   | R_s asymmetric across the 4 pads, V_F slightly elevated                   | 4-wire per-pin on the LED row      |
| **Void-rich joint**               | Borderline pass electrically, fails first under thermal cycle             | Pre/post thermal-cycle delta on V_F|
| **Solder bridging**               | Short between adjacent cathodes                                           | Continuity test cathode-cathode    |
| **No wetting on substrate**       | Detached die at first touch                                               | Chain open + X-ray                 |
| **No wetting on die**             | Die in place but high R                                                   | Chain resistance vs. shear         |

---

## 9. Summary: how the board enables this research

Three things make v2 a "research instrument" rather than a hobby substrate:

1. **Co-located reference structures.** The TLM, VDP, and dummy daisy
   chains live on the *same* board as the LEDs and DoE sites. They share
   ENIG plating, paste, reflow — so when you compare two bonding
   materials, the LED measurement and the dumb-resistor measurement
   change for the *same* reason. You can extract a clean ρ_c that maps
   onto LED V_F shift.
2. **4-wire everywhere it matters.** Force/sense pad pairs on every LED
   pin, every daisy chain, every TLM finger. Probe and trace resistance
   never enter the result.
3. **Three connector tiers** so the same board handles ad-hoc manual
   characterization, repeated bench testing, and hot-swap fixture use
   without redesigning the layout.

What it does **not** do: optical / radiometric metrology — that needs an
integrating sphere off-board. Photometric measurements complement the
electrical ones but aren't on this PCB.
