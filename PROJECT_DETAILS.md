# TU Delft / ITEC — Micro-LED Bonding Categorization Project

Working notes that consolidate everything in this repository: project goal, the
existing KiCad PCB, the supporting papers and datasheet, and links to outside
designs that can serve as inspiration for a new board revision.

---

## 1. Project Goal

This project investigates how to attach small (≈1 mm²) semiconductor / LED dies
onto a PCB **without applying mounting pressure** (the "pick-and-release" / air
drop method) and to **characterize the resulting bonds** geometrically,
mechanically and electrically. It is a collaboration between
**TU Delft (ECTM / Microelectronics, M. Mastrangeli, H. van Zeijl, A. Abdelwahab)**
and **ITEC B.V. / Nexperia (R. van Hoorn, H. Kuipers)**, financed by ITEC B.V.
and co-financed by the Netherlands Enterprise Agency (RVO).

### Work-plan with Ahmed (`Work with Ahmed.md`)

1. **Design of the PCB** for LED characterization.
2. **Clean-room assembly**: solder-paste stencil printing → pick-and-place /
   pick-and-release of LED dies onto either the existing PCB or a newly
   shipped revision.
3. **Geometric characterization** of the LED dies: 3-D laser scans, **bond
   line thickness (BLT)** and **die tilt**. Post-bonding alignment is *not*
   expected to be corrected.
4. **Electrical measurement** and full characterization once assembly is
   complete.

---

## 2. Existing PCB — `Electrical test + LED-no solder.kicad_pcb`

KiCad 6 board (file format version `20221018`, `pcbnew` generator). 4,141
lines of S-expression source.

### Board outline

- **Size**: 58.75 mm × 61.51 mm (Edge.Cuts rectangle `47.85,15.77` →
  `106.6,77.28`).
- **Stack-up**: standard 1.6 mm two-layer FR-4 (`thickness 1.6`), F.Cu / B.Cu.
- **Surface finish (per paper)**: **ENIG** — chosen for solderability and the
  reliable electrical connectivity it gives to the test structures.
- **Silkscreen designer credit**: "Ahmed Abdelwahab" at `(84.1, 50.96)`.

### Footprint inventory

165 footprints total. None carry a populated `reference` or `value` — every
text field is empty / hidden, which is intentional for a research test
board (no part numbers; structures are identified by position only).

Pad-size histogram (count × `width × height` mm):

| Count | Size (mm)   | Likely role                                      |
|------:|-------------|--------------------------------------------------|
| 645   | 1.27 × 1.27 | Probe pads for VDP / TLM / DC structures         |
|  68   | 0.5  × 0.5  | Bond-pad geometry under test                     |
|  43   | 1.0  × 1.0  | "Reference" 1 mm² bond pad (matches die size)    |
|  32   | 0.4  × 0.4  | Bond-pad geometry under test (matches LED land)  |
|  16   | 0.64 × 0.64 | Bond-pad geometry under test                     |
|  16   | 0.48 × 0.48 | Bond-pad geometry under test                     |
|   9   | 0.25 × 4    | TLM-style elongated finger                       |
|   8   | 0.5  × 5    | TLM / current-injection finger                   |
|   8   | 0.3  × 5    | TLM / current-injection finger                   |
|   7   | 1.0  × 5    | Wide TLM finger                                  |
|   7   | 0.5  × 4    | TLM finger                                       |
|   4   | 0.25× 0.25  | Smallest bond-pad geometry under test            |
|   1   | 4 × 4 / 3 × 3 / 2 × 2 / 1.5 × 1.5 | Larger reference pads        |

Pads use both **rect** and **circle** primitives at varying rotations (0°,
90°, 180°, 270°). According to Fig. 12 of the ECTC paper the board also
features the **"+ four corner mini-pads" geometry** (0.5 mm pads added to
the four corners of the 1 mm² bond pads) that *almost eliminated die tilt*
in their experiments.

### Test structures present (from the paper, Fig. 23a)

The PCB integrates:

- **5 × 5 array of 1 mm² bond pads** — the main array on which dummy dies and
  LEDs are mounted (Cu, Ag, Au, ENIG finish variants on the *die* side).
- **Daisy-chain (DC)** structure — bridges six 1 mm × 1 mm dummy dies so a
  single current path runs through six bonds in series → catches detached
  dies and broken chains via X-ray follow-up.
- **Van der Pauw (VDP)** structure — measures **effective sheet resistivity
  of the ENIG-finished pads**: reported value 2.94 × 10⁻⁵ Ω·m.
- **Transmission Line Model (TLM)** structures — measure contact resistivity
  ρ_c via ρ_c = R_c · W · a (Eq. 2 of the paper). The 0.25/0.3/0.5/1 mm × 4–5 mm
  rectangular fingers in the pad table above are the TLM fingers.
- **RGB-LED footprints** matching the **Würth WL-SFCC 0404** (see §3) — used
  to verify that current actually flows through the bonded joints (Fig. 23b
  in the paper shows the LEDs lit up).

The file name **"…-no solder"** signals this is the version with **no solder-
paste apertures defined on the Paste layers**; the solder is screen-printed
through a separate 100 µm laser-cut stainless-steel **stencil with TS391LT
Sn42 / Bi57.6 / Ag0.4 paste**, applied with a manual Eurocircuits
**eC-stencil-mate**.

---

## 3. Supporting Documents in the Repo

### 3.1 `ECTC-2025-published Ahmed Abdelwahab.pdf`
A. Abdelwahab, H. van Zeijl, R. van Hoorn, H. Kuipers, M. Mastrangeli,
**"Pick-and-Release: A Novel Contactless Bonding Method for Die Attachment"**,
*2025 IEEE 75th ECTC*, pp. 2125–2132, **DOI: 10.1109/ECTC51687.2025.00363**.

The directly relevant publication for this PCB. Headline numbers:

- Dies: **1 mm × 1 mm × 525 µm** silicon with Cu / Au / Ag (200–300 nm)
  top finishes over the appropriate adhesion stack (Si₃N₄ or SiO₂ + Cr/Ti).
- Solder: **TS391LT Sn42Bi57.6Ag0.4**, T_melt = 138 °C; reflow peak 165 °C.
- Pick-and-release: free-fall drop from **100–250 µm**, terminal velocity
  ≈ **125 µm/ms** (boosted from gravitational 44–70 µm/ms by the release air
  pulse).
- Contact angle of solder on ENIG pad: **≈ 18°** (lowest of all surfaces
  tested — Si, Cu, Ag, Au all > 18°).
- **Bond Line Thickness (BLT)**: 50–75 µm depending on finish and pressure
  (lower & more reproducible with 1 MPa pick-and-place, irrespective of
  finish).
- **Die tilt**: 5.4°–8.1° "high-tilt" axis without optimization. With the
  **rounded-corner + four corner mini-pads** geometry tilt is reduced to
  **≈ 0.2°** (Ag die, with pressure, Fig. 12).
- **Die-shear strength**: 42.99 ± 4.76 MPa for Ag (best); 9–11 MPa for Cu
  (worst — Cu dies lack an adhesion layer between Cu and Si₃N₄ so failure is
  adhesive at the solder/die interface).
- **Voiding**: 1 MPa mounting pressure eliminates voids for Cu and Ag;
  negligible effect for Au.
- **Electrical**: DC chain resistance lowest for Ag-with-pressure (0.199 ±
  0.019 Ω); highest for Au-without-pressure (0.380 ± 0.025 Ω). Sheet
  resistance of the solder on ENIG: **4.404 × 10⁻⁸ Ω·m**.

### 3.2 `Stabilization of the tilt motion during capillary self-alignment of.pdf`
J. Berthier, K. A. Brakke, S. Mermoz, C. Frétigny, L. Di Cioccio,
**"Stabilization of the tilt motion during capillary self-alignment of
rectangular chips"**, *Sensors and Actuators A*, **234** (2015) 180–187,
DOI: 10.1016/j.sna.2015.09.008.

Foundational reference for the *tilt problem*: among the four self-alignment
modes (shift, twist, lift, tilt), only **tilt is non-restoring** for square /
rectangular chips. Their remedy — **lyophilic / wetting bands patterned on
the substrate** — is conceptually the same trick as the four mini-corner
pads added in §3.1.

### 3.3 `s41586-023-06167-5 (1).pdf`
Lee *et al.*, **"Fluidic self-assembly for MicroLED displays by controlled
viscosity"**, *Nature* **619**, 755 (2023), DOI: 10.1038/s41586-023-06167-5.

State of the art for **massively-parallel** microLED assembly: 19 000 disk-
shaped 45 µm × 5 µm GaN chiplets self-assembled at **99.88 % yield** in 60 s
by adding poloxamer to thicken the carrier liquid. Different regime
(thousands of LEDs, liquid-phase agitation) but the same surface-tension
physics drives the placement.

### 3.4 `patent-published-2024-2026.pdf`
B. V. Nexperia, **"A method for mounting an electronics component at a
particular placement location on a carrier as well as a pick-and-place
apparatus for mounting an electronics component at a particular placement
location on a carrier"**, *PCT Patent Application PCT/EP2024/070643*, 2024.

The patent covers the **pick-and-release / air-drop** method itself (gripper
120, die 11, substrate 50, solder droplet 60 in Fig. 1; controller 140
issues a release pulse at height Δh). Reference [9] of the ECTC paper.

### 3.5 `150044M155220-RGB LEDs.pdf`
Würth Elektronik **WL-SFCC 150044M155220** SMT Full-color (RGB) Chip LED,
0404 package. Key dimensions for the PCB:

- Body: **0.95 mm × 0.95 mm × 0.25 mm**.
- Four pads, **0.275 mm × 0.275 mm**, on a 0.4 mm pitch grid (recommended
  land pattern: **0.4 × 0.4 mm pads, 0.4 mm gap**).
- V_F ≈ 2.0 V (R) / 3.0 V (G,B); I_F = 10 mA nominal, 20 mA peak.
- Peak λ: 630 nm (R) / 520 nm (G) / 460 nm (B).
- Polarity mark on pad 1; common anode (pin 1) per the schematic.
- Operating range −30 °C … +85 °C; ESD HBM 1 kV; MSL 3.

---

## 4. KiCad / PCB Inspiration Found Online

No public open-source KiCad project exactly matches this purpose
(micro-LED-die capillary-bonding characterization with VDP / TLM / DC test
structures on a single board). The relevant building blocks live in
separate repos / datasheets:

### 4.1 RGB-LED footprint for the 0404 Würth WL-SFCC
- **SnapEDA** — `150044M155220` footprint & symbol downloadable as KiCad:
  https://www.snapeda.com/parts/150044M155220/Wurth%20Elektronik/view-part/
- **Ultra Librarian** — companion 150044M155260 part (same family) with
  KiCad export and STEP model:
  https://app.ultralibrarian.com/details/fd6816a2-515d-11ea-a124-0ad2c9526b44/Wurth-Electronics/150044M155260
- **Würth official datasheet** (recommended land pattern, top of §3.5):
  https://www.we-online.com/components/products/datasheet/150044M155220.pdf

Use any of the above and *verify* against the 0.4 × 0.4 mm pads / 0.4 mm
pitch land pattern before committing.

### 4.2 LED sample / reference card boards
- **Kaouthia/LED-Sample-Board** (GPL-3.0): a small KiCad / Gerber project
  whose only purpose is to expose SMT LEDs on solderable pads, useful as a
  layout reference for densely-packed LED footprints —
  https://github.com/Kaouthia/LED-Sample-Board

### 4.3 Flip-chip / die-attach templates
- **jaylogue/dec-flip-chip-templates** (CC-BY-4.0): KiCad templates for
  retro DEC flip-chip modules; uses ENIG / hard-gold finish at 1.4–1.6 mm
  thickness — same fab constraints as ours. Useful as a *pad-on-edge*
  reference even though the application is unrelated —
  https://github.com/jaylogue/dec-flip-chip-templates
- Hackaday writeup: https://hackaday.com/2021/11/07/flip-chip-kicad-templates/

### 4.4 KiCad standard footprint libraries (always check first)
- LED_SMD library: https://kicad.github.io/footprints/LED_SMD
- Würth connector library (community): https://github.com/savenlid/kicad/tree/master/footprints/Wurth-Elektronik

### 4.5 Test-structure references (not KiCad, but design-side)
- TLM theory and contact-resistance extraction:
  https://en.wikipedia.org/wiki/Transfer_length_method and
  https://cleanroom.byu.edu/contact_resistance
- Practical Components BGA daisy-chain test kit — commercial reference
  showing pad/via patterns that connect die-side and PCB-side halves of a
  daisy chain: https://www.practicalcomponents.com/Evaluation-PCB-Boards/product.cfm?PCB012-BGA-Global-Daisy-Chain-Test-Kit-2A48C44A4ECF7022=

### 4.6 Underlying research literature on substrate / pad design
- M. Mastrangeli, **"Capillary self-alignment of microchips on soft
  substrates"** (open-access via PMC):
  https://pmc.ncbi.nlm.nih.gov/articles/PMC6190098/
- M. Mastrangeli profile (links to the full surface-tension-driven
  self-assembly publication list):
  https://microelectronics.tudelft.nl/People/bio.php?id=514

---

## 5. Suggested next steps for a board revision

Driven by the paper's own conclusions:

1. **Always include the four-corner mini-pads** on every 1 mm² bond pad
   variant — die tilt drops from ~6° to ~0.2°.
2. Add a **rounded-corner** variant of the 1 mm² pads explicitly; the paper
   only references it qualitatively. A radius sweep (R = 50 / 100 / 200 µm)
   would close that gap.
3. **Increase TLM finger length range**: current 4–5 mm fingers; a
   conventional TLM ladder uses contact spacings of e.g. 5/10/20/50/100/200 µm
   between identical fingers. Verify the pattern is a true TLM ladder, not
   a single width-varied finger set.
4. **Bring the Würth WL-SFCC 0404 land pattern** in as official Würth
   footprint (SnapEDA / Ultra Librarian) rather than a hand-drawn copy —
   future-proofs against tolerance creep.
5. **Add fiducials** for the Tresky T-3000-PRO bonder and stencil-mate
   alignment.
6. **Annotate** the silkscreen with structure IDs ("DC1", "VDP1", "TLM-W0.5",
   etc.). The current board carries no on-board labels at all.

---

## 6. Quick filesystem map

```
.
├── Electrical test + LED-no solder.kicad_pcb   # KiCad 6 board, 165 footprints, 58.75 × 61.51 mm
├── Work with Ahmed.md                          # 4-step work-plan with Ahmed Abdelwahab
├── ECTC-2025-published Ahmed Abdelwahab.pdf    # The published paper this PCB was used for
├── Stabilization of the tilt motion ...pdf     # Berthier 2015, tilt-instability theory
├── s41586-023-06167-5 (1).pdf                  # Nature 2023, FSA microLED at 99.88 % yield
├── patent-published-2024-2026.pdf              # PCT/EP2024/070643, pick-and-release patent
└── 150044M155220-RGB LEDs.pdf                  # Würth WL-SFCC 0404 RGB LED datasheet
```
