# Micro-LED Bonding Categorization

Course project (ET4277 + ET4391) and research contribution at TU Delft ECTM, investigating how ~1 mm² LED dies bond to a PCB without mounting pressure (pick-and-release / air-drop), and how to characterize the resulting bonds geometrically, mechanically, and electrically. Joint work with M. Mastrangeli, H. van Zeijl, and A. Abdelwahab (TU Delft) and ITEC B.V. / Nexperia (R. van Hoorn, H. Kuipers), financed by ITEC B.V. and co-financed by RVO. Builds on a v1 board published at ECTC 2025.

The work splits into two reports (both in `part1/` and `part2/`): part 1 designs the test board and its electrical characterization; part 2 documents the bonding process and the capillary self-alignment physics.

## The test board (v2/v4)

A single 93 × 93 mm 2-layer FR-4 board (ENIG, all pads gold) packing every structure needed to characterize bonds on one substrate: a 6 × 6 bond-pad design of experiments (three pad geometries × three fillet radii at 3.5 mm pitch), TLM ladders and Van der Pauw crosses for sheet and contact resistance, 6- and 12-LED daisy chains, eight standalone RGB LEDs with four NTC thermometers for junction-temperature sensing, and an LCR calibration set (open / short / 100 Ω).

![Annotated fab render of the micro-LED bond characterization board](new-pcb/fab/preview/top.png)

The board is designed in KiCad and exported fab-ready for Eurocircuits: the five SMT parts (resistor, headers, NTCs) are reflowed by the fab, while the 26 LED bond pads ship as bare gold and are bonded at the TU Delft EKL cleanroom under a Tresky T-3000-PRO die bonder. Board sources, generators, and fab outputs (gerbers, BOM, position, STEP, PDFs) are under `new-pcb/`; the KiCad project itself is DRC-clean with full schematic parity.

## Part 1: electrical characterization

Design of the measurement methodology: TLM/Van der Pauw extraction of contact and sheet resistance on ENIG, daisy-chain continuity, and V_F-based temperature sensing (V_F-TSP) using the on-board NTCs as reference. Report and KiCad project archive in `part1/`.

## Part 2: bonding and capillary self-alignment

Cleanroom process work: solder-paste stencil printing, die-bonder placement of the micro-LEDs, and analysis of capillary self-alignment and residual die tilt (bond-line thickness and tilt are measured, not corrected). Photographed throughout in `part2/photos-during-lab2/`.

![Solder-paste printed bond-pad array before die placement](part2/report/figures/printed_array.jpg)

The report (`part2/report/report.pdf`) ties the observed self-alignment and tilt back to the fluid-joint physics from the cited literature (`part2/downloaded_references/`, capillary self-alignment and fluidic self-assembly papers).

## Repository layout

| Path | Contents |
| --- | --- |
| `part1/` | Electrical characterization report, board project archive, fab quote |
| `part2/` | Bonding process report, lab photos, self-alignment references |
| `new-pcb/` | v2/v4 KiCad project, generation tools, and Eurocircuits fab package |
| `old-pcb/` | v1 board (ECTC 2025), kept for reference |
| `report/` | Consolidated part 1 report source and reference papers |
| `docs/` | Datasheets, published papers, patent, collaboration notes |
| `PROJECT_DETAILS.md` | Full project context and design rationale |

Fabrication logistics (Eurocircuits order steps, stencil handling, "place loose" LED rows) are detailed in `new-pcb/FABRICATION_ORDER.md` and `new-pcb/README.md`.

Tools: KiCad 9, Python fab/BOM generators, Eurocircuits PCB + PCBA, Tresky die bonder, LCR/TLM measurement bench.
