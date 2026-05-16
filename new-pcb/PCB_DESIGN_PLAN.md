# Micro-LED Bonding Characterization PCB — v2 Design Plan

**Status:** Draft. Owner: Daniel (PCB) + Ahmed (process). Target tape-out: TBD.
**Predecessor:** `old-pcb/Electrical test + LED-no solder.kicad_pcb` (ECTC 2025).
**Companion docs:** `../PROJECT_DETAILS.md`, `docs/ECTC-2025-published Ahmed Abdelwahab.pdf`.

---

## 1. Goals

The v2 board must let us answer the questions that v1 raised but could not
fully close. In priority order:

1. **Reduce die tilt to < 0.5°** on **every** bond pad — by adopting the
   *"four-corner mini-pad"* geometry universally (it eliminated tilt on the
   limited subset where v1 used it).
2. **Quantify the geometry → tilt relationship** with a clean Design Of
   Experiments (DoE): pad shape (square / rounded-corner / circle / cross),
   corner radius (R = 0 / 50 / 100 / 200 µm), and mini-pad spacing.
3. **Measure contact resistivity ρ_c with a proper TLM ladder** — fixed
   finger width, **swept contact-spacing** (5/10/20/50/100/200 µm). The v1
   TLM had only a fixed spacing.
4. **Verify electrical performance on real RGB LEDs** using the Würth WL-SFCC
   super-flat 0404 (`150044M155220`) — the part we already have in the BOM
   and whose KiCad library is now vendored in `library/`.
5. **Be tooling-ready out of the box** — fiducials for the Tresky bonder and
   eC-stencil-mate, silkscreen IDs on every structure, separate paste-layer
   file so the stencil can be re-cut without re-tooling the PCB.

---

## 2. Lessons from v1 (`old-pcb/`)

| v1 behaviour                                  | v2 response                                                                                          |
|-----------------------------------------------|------------------------------------------------------------------------------------------------------|
| Die tilt 5°–8° on plain square pads           | Apply 4 corner mini-pads (0.5 × 0.5 mm at the corners of each 1 × 1 mm bond pad) everywhere          |
| Tilt only solved on one pad geometry          | Sweep geometry: square / rounded / circle / cross + radius sweep                                     |
| TLM fingers fixed                             | TLM ladder with 6 contact spacings (5/10/20/50/100/200 µm) per finger width                          |
| No structure labels on silkscreen             | Every structure carries an ID ("BP-Sq-R0-A1", "TLM-W0.5-S20", "DC-N6-1", "VDP-1", "LED-R1C1")        |
| 165 footprints with empty references          | Keep references *populated* but parked off-board on the F.Fab layer — no silkscreen text on bond/probe pads (keeps Keyence scans clean) |
| No fiducials                                  | 3 × 1 mm copper fiducials (top-left / top-right / bottom-right asymmetric) + 4 × 1 mm corner fiducials on the Eco1.User layer for the stencil printer |
| Solder paste off-board                        | Keep that. Generate F.Paste apertures procedurally and provide both "with stencil" (paste defined) and "no stencil" (current behaviour) variants |
| 165 manually-placed footprints, hand routed    | v2 footprints generated from a CSV table → KiCad scripting (see §11) so DoE expansion is just a CSV row |

---

## 3. Board outline & stack-up

- **Outline:** keep 58.75 × 61.51 mm (drop-in compatible with the bonder
  fixture and the stencil frame). Slightly chamfered top-left corner for
  unambiguous orientation.
- **Stack-up:** 2-layer FR-4, 1.6 mm finished thickness, 35 µm (1 oz) copper.
  Top side carries all bond pads and test structures; bottom side carries
  routing only.
- **Solder mask:** matte black or matte green, **opening = pad + 0.0 mm**
  (defined by the pad, NSMD where possible to reproduce v1 behaviour). The
  paper relied on the contact-angle of solder on ENIG (~18°) — keep the
  geometry identical.
- **Surface finish:** **ENIG** (Ni 4–5 µm / Au 0.05–0.12 µm) — paper §III-B,
  Fig. 4(b). Quote both lead-free and RoHS to the fab.
- **Silkscreen:** white, 0.15 mm line / 1.0 mm height; **none** on bond pads
  or probe pads — only in dedicated label rows between rows of structures.

---

## 4. Test-structure inventory (v2 target)

For every structure, give it an on-silkscreen ID matching the table below.
Coordinates are notional — final placement is done after the structure-by-
structure layout.

### 4.1 Main bond-pad DoE array (centre of board, ~30 × 30 mm region)

A 10 × 10 grid (100 sites) at **2.0 mm pitch** centre-to-centre — fits in
20 × 20 mm. ID format: `BP-<shape>-<R>-<row><col>`.

| Site count | Shape          | Size (mm)        | Corner radius (µm) | Mini-pad corners?         |
|-----------:|----------------|------------------|--------------------|---------------------------|
| 16         | Square plain   | 1 × 1            | 0                  | No (control / reference)  |
| 16         | Square + minis | 1 × 1            | 0                  | **Yes** (4 × 0.5 × 0.5 mm)|
| 16         | Square rounded | 1 × 1            | 50                 | Yes                       |
| 16         | Square rounded | 1 × 1            | 100                | Yes                       |
| 16         | Square rounded | 1 × 1            | 200                | Yes                       |
| 8          | Circle         | Ø 1.0            | —                  | Yes (4 × 0.5 × 0.5 mm at ±45°) |
| 8          | Cross / "+"    | 1 × 1 (200 µm w) | —                  | No                        |
| 4          | Reference 2 mm | 2 × 2            | 0                  | No                        |

Each site is **electrically isolated** — they connect to two **1.27 × 1.27
mm probe pads** on the side of the board via 0.2 mm traces, so you can
do 4-wire die-shear-and-resistance after bonding.

### 4.2 Daisy chains (north edge of board)

- 3 chains: **N = 6 / 12 / 24** dies in series. v1 had only N = 6.
- Chain ID: `DC-N6-1`, `DC-N12-1`, `DC-N24-1`.
- Bond pad geometry: 1 × 1 mm + 4-corner-mini, **same** as the DoE control
  to make the resistance comparable.
- Each chain terminated by two 1.27 × 1.27 mm probe pads (4-wire access:
  two more probe pads tap the chain mid-point for split measurement).

### 4.3 Van der Pauw (VDP) (west edge)

- 4 VDP cloverleaf structures with 1.0 / 0.5 / 0.25 / 0.1 mm arm width to
  cross-check sheet-resistance scaling.
- ID: `VDP-W1`, `VDP-W0.5`, `VDP-W0.25`, `VDP-W0.1`.

### 4.4 TLM ladders (south edge)

- 3 ladder banks at finger width **W = 0.25 / 0.5 / 1.0 mm**.
- Each bank has 7 identical fingers with **contact spacings** 5 / 10 / 20 /
  50 / 100 / 200 µm (6 gaps between 7 fingers).
- Each finger terminates in a 1.27 × 1.27 mm probe pad.
- ID: `TLM-W0.5-S20` = bank W = 0.5 mm, spacing 20 µm.

### 4.5 RGB LED test row (east edge)

- 8 footprints of **D_Wurth_WL-SFCC-0404superflat** (`150044M155220`).
- 4 wired so all 8 share **anode + 3 individually accessible R/G/B cathodes**
  → smoke-test the assembly visually (just like Fig. 23b of the paper).
- 4 wired into a "small daisy chain" through the LED bodies (anode of LED N
  to common cathode of LED N+1) so a single bonded-joint failure breaks the
  light. Useful go/no-go.
- ID: `LED-R1C1` … `LED-R1C8`.

### 4.6 Calibration / metrology assists

- 4 × **1.0 mm copper fiducials** (filled circles, 2 mm solder-mask opening)
  near the corners — for the stencil printer and the bonder.
- 1 × asymmetric **L-shape fiducial** top-left so orientation is
  unambiguous even with the board rotated.
- A **graduated mm/µm ruler** along the south edge etched into copper for
  Keyence calibration.

---

## 5. Pad-geometry library (the heart of the DoE)

All bond pads are 1 × 1 mm reference area unless stated. Variations:

```
            Plain        Rounded R = X        +Corner-minis      Circle
            ┌─────┐      ╭─────╮              ┌─────┐ ◾◾         ┌─────╮
            │     │      │     │              │     │            │     │
            │     │      │     │              │     │            │     │
            └─────┘      ╰─────╯              └─────┘ ◾◾         ╰─────╯
```

- **Mini-pad** dimensions per paper: 0.5 × 0.5 mm, placed so their inner
  edge sits 100 µm outside the main pad edge at the corner. Connected to
  the same net as the main pad with a 0.15 mm trace under solder mask.
- **Cross / "+"** uses arm width 0.2 mm; envelope still 1 × 1 mm.
- **Circle** Ø = 1.0 mm (same area envelope, ~78 % of pad copper area).

Document each entry as its own KiCad footprint so the DoE layout is just
placing footprints from the project library.

---

## 6. Schematics & nets

Every structure is its own self-contained sub-schematic. Net naming:

- Bond-pad DoE: `BP_<ID>_P1`, `BP_<ID>_P2` (probe-side high / low).
- Daisy chain: `DC<N>_IN`, `DC<N>_OUT`, `DC<N>_MID`.
- VDP: `VDP_<W>_A` … `VDP_<W>_D` for the four cloverleaf contacts.
- TLM: `TLM_<W>_F1` … `TLM_<W>_F7` for the seven fingers.
- LED row: `LED_<col>_A` (anode), `LED_<col>_KR/KG/KB` (cathodes).

Probe-pad pitch: **2.54 mm** centre-to-centre on a regular grid along the
left/right edges so a Pogo-pin fixture can be used in addition to the
manual probe station.

---

## 7. Solder-paste / stencil strategy

Keep v1's "**-no solder**" convention: the master `.kicad_pcb` does **NOT**
define paste apertures, and the stencil is cut from a separate Gerber set.

- Primary stencil: **100 µm laser-cut SS**, aperture = pad area × 0.9
  (10 % reduction is paper §III-A's working value, ratio matches TS391LT
  Type 4 mesh).
- Secondary stencil: **50 µm**, aperture = pad area × 1.0 (for the smallest
  test pads where 100 µm starves the joint).
- The Gerber set ships with **two** F.Paste layers for each variant
  (`*.gtp`) — produced by a Python script in `tools/gen-paste.py` (see
  §11) so the master never gets two paste layers in conflict.

---

## 8. Bill of Materials (PCB-side)

The board itself only has the LEDs as active parts; everything else is
empty pads.

| Designator   | Part                                              | Qty | Source          | Notes                              |
|--------------|---------------------------------------------------|----:|-----------------|------------------------------------|
| D1 … D8      | Würth WL-SFCC 150044M155220 (super-flat RGB)      |   8 | DigiKey / Würth | Use vendored footprint in `library/` |
| —            | TS391LT Sn42/Bi57.6/Ag0.4 solder paste T4 (jar)   |   1 | Chip Quik       | Same as paper                      |
| —            | 100 µm SS stencil (eC-stencil-mate frame)         |   1 | Eurocircuits    | Order with the PCB                 |
| —            | 50 µm SS stencil (secondary)                      |   1 | Eurocircuits    | Optional, for smallest pads only   |
| —            | 1 mm² test dies (Cu / Au / Ag finish on Si)       |  ~60 | EKL clean-room   | Wafer-diced 1 × 1 × 0.525 mm       |

The dies are fabricated, not bought; spec is in paper §III-B.

---

## 9. Fab & assembly flow

1. **PCB fab** (Eurocircuits, lead-time 5 d): 2-layer FR-4, 1.6 mm, ENIG,
   black mask, **white silk except on metrology areas**, edge-rail tabs
   (3 × 1 mm) for the bonder fixture.
2. **Stencil fab** (Eurocircuits, same lot): 100 µm SS stencil, eC-stencil-
   mate compatible frame.
3. **Paste print** (clean-room, ISO 7): manual print on the eC-stencil-
   mate, inspect 100 % with the **Keyence VK-X250** (3D paste volume + footprint).
4. **Die prep** (EKL): wafer-dice the test dies, verify surface finish
   thickness with ellipsometry.
5. **Die bonding** (Tresky T-3000-PRO):
   - Pick-and-release on the DoE pads (the main experiment).
   - Pick-and-place at 1 MPa on a control row (so we have within-board
     reference).
   - 8 LEDs placed by the same Tresky on the LED row.
6. **Reflow** (hot-plate on the die bonder, paper §III-A reflow profile):
   RT → 90 °C @ 0.72 °C/s → 130 °C @ 0.44 °C/s → 138 °C @ 0.27 °C/s →
   165 °C @ 0.9 °C/s → unforced cooldown.
7. **Geometric metrology** (Keyence VK-X250): 3D scan every site for BLT
   and tilt (paper §IV).
8. **Electrical** (Summit 11K/12K probe station + Keithley): DC chain,
   VDP, TLM, light-on the LED row.
9. **Mechanical** (Nordson DAGE 4000 Bondtester): die-shear at 500 µm/s on
   each DoE site → strength vs. geometry plot.
10. **Failure analysis** (Keyence VK + SEM/EDS) on failed bonds.

---

## 10. Test & data plan

Output of the experiment is a CSV with one row per bonded site:

```
site_id, shape, R_um, mini_pads, die_finish, mounting_pressure_MPa,
BLT_um, tilt_high_deg, tilt_low_deg, shear_MPa, R_chain_ohm, R_contact_ohm
```

Sample sizes per cell of the DoE matrix:

- **n ≥ 5** per (shape, R, die_finish, pressure) combination → tolerable
  variance on tilt (paper reported ±0.93°–±3.02° per cell at n ≈ 5).
- Two replicate boards per condition → 2× the n above.

The CSV feeds a Jupyter notebook (`tools/analysis.ipynb`) that re-makes
the paper's Fig. 10 / 12 / 13 with the new geometry sweep.

---

## 11. Tooling

- `tools/gen-pads.py` — read a CSV of (id, shape, R, mini_pads, x, y,
  rotation) and emit a `.kicad_mod` per geometry plus a `.kicad_sch` /
  `.kicad_pcb` patch placing them. Idempotent.
- `tools/gen-paste.py` — read the master `.kicad_pcb` and the stencil
  shrink % and emit a F.Paste Gerber. Generated, never edited by hand.
- `tools/check-drc.sh` — run `kicad-cli pcb drc` and fail CI if violations.
- `tools/build.sh` — full pipeline: gen-pads → gen-paste → DRC → Gerber
  export → zip for Eurocircuits.

---

## 12. Risks & open questions

| Risk                                                       | Mitigation                                                                |
|------------------------------------------------------------|----------------------------------------------------------------------------|
| ENIG-finish lot variation skews TLM ρ_c readings           | Order all boards in **one fab lot**; record fab batch ID on silkscreen.    |
| 50 µm stencil aperture under-prints below process window   | Keep 100 µm as primary; 50 µm is an experimental side study.               |
| 4 mini-pads on circle / cross is geometrically ambiguous   | Specify mini-pad placement at ±45° (circle) or aligned to arms (cross).    |
| Pogo fixture vs. manual probe — pad pitch trade-off        | Probe pads at 2.54 mm pitch, manual probe still fits because pad = 1.27 mm.|
| Patent: any IP exposure in publishing this PCB?            | Cross-check `docs/patent-published-2024-2026.pdf` before open-sourcing the .kicad_pcb (the pick-and-release **method** is patented; the **PCB test substrate** isn't).|
| ECTC paper used a 5 × 5 LED matrix, v2 uses 1 × 8          | Keep one row of v1-style 5 × 5 on a future v2.1 if Ahmed prefers parity.   |

---

## 13. Schedule (placeholder)

| Phase                                  | Calendar weeks |
|----------------------------------------|---------------:|
| Schematic + custom footprint library   | 2              |
| Layout + DRC                           | 2              |
| Review with Ahmed / Massimo            | 1              |
| Fab + stencil order                    | 1              |
| Receive + incoming inspection          | 1              |
| Assembly + metrology + electrical      | 3              |
| Write-up                               | 2              |
| **Total**                              | **12 weeks**   |

---

## 14. Deliverables

When this plan is executed, the `new-pcb/` folder should contain:

```
new-pcb/
├── PCB_DESIGN_PLAN.md                    ← this file
├── README.md                             ← getting started
├── library/                              ← vendored Würth + custom DoE footprints
│   ├── symbols/LED_Wurth_WL-SFCC.kicad_sym
│   ├── footprints/LED_SMD_Wurth.pretty/...
│   ├── footprints/BondPads_DoE.pretty/   ← custom (generated)
│   └── 3dmodels/...
├── tud-microled-v2.kicad_pro             ← KiCad project
├── tud-microled-v2.kicad_sch             ← top-level schematic
├── tud-microled-v2.kicad_pcb             ← layout
├── tools/
│   ├── gen-pads.py
│   ├── gen-paste.py
│   ├── check-drc.sh
│   └── build.sh
├── fab/                                  ← Gerbers + drill + paste, zipped per variant
│   ├── tud-microled-v2-PCB.zip
│   ├── tud-microled-v2-stencil-100um.zip
│   └── tud-microled-v2-stencil-50um.zip
└── data/
    ├── doe-matrix.csv                    ← drives gen-pads.py
    ├── results.csv                       ← post-experiment dataset
    └── analysis.ipynb
```
