# tud-micro-led-bonding-categorization

Characterization of micro-LED / 1 mm² die bonding on PCB substrates.
Joint work: **TU Delft** (ECTM, M. Mastrangeli, H. van Zeijl, A. Abdelwahab)
and **ITEC B.V. / Nexperia** (R. van Hoorn, H. Kuipers). Financed by ITEC
B.V. and co-financed by the Netherlands Enterprise Agency (RVO).

## What's in here

```
.
├── README.md                  ← you are here
├── PROJECT_DETAILS.md         ← deep dive: project context, the v1 board, the papers
├── docs/                      ← reference PDFs + the Ahmed work-plan note
│   ├── ECTC-2025-published Ahmed Abdelwahab.pdf
│   ├── Stabilization of the tilt motion during capillary self-alignment of.pdf
│   ├── s41586-023-06167-5 (1).pdf
│   ├── patent-published-2024-2026.pdf
│   ├── 150044M155220-RGB LEDs.pdf
│   └── Work with Ahmed.md
├── old-pcb/                   ← v1 board (ECTC-2025 paper), read-only reference
│   ├── README.md
│   └── Electrical test + LED-no solder.kicad_*
└── new-pcb/                   ← v2 board, in development
    ├── README.md
    ├── PCB_DESIGN_PLAN.md          ← the detailed plan (geometry / fab / BOM)
    ├── ELECTRICAL_CHARACTERIZATION.md  ← measurements, ports, lab tools, workflow
    └── library/                    ← vendored Würth WL-SFCC symbol/footprint/3D
```

## Where to start, by role

- **PCB designer** → `new-pcb/PCB_DESIGN_PLAN.md`
- **Process / clean-room** → `new-pcb/PCB_DESIGN_PLAN.md` §7 and §9
- **Electrical characterization / lab planning** → `new-pcb/ELECTRICAL_CHARACTERIZATION.md`
- **Catching up on the project** → `PROJECT_DETAILS.md` then
  `docs/ECTC-2025-published Ahmed Abdelwahab.pdf`
- **Recreating the original results** → `old-pcb/` + `PROJECT_DETAILS.md` §2

## Status

| Component                      | Status         |
|--------------------------------|----------------|
| v1 board (ECTC 2025)           | shipped        |
| Project context document       | done           |
| v2 design plan                 | drafted, review pending |
| v2 KiCad project               | not started    |
| v2 schematic                   | not started    |
| v2 layout                      | not started    |
| v2 fabrication                 | not started    |
| v2 assembly + characterization | not started    |
