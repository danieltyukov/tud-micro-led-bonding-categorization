# new-pcb — v2 Micro-LED Bonding Characterization PCB

**Status: fab-ready (v4.0.7).** DRC clean (0 violations, 0 unconnected items),
gerbers + assembly outputs verified for both Aisler (Beagle assembly) and
Eurocircuits (eC-stencil-mate or SMT line).

## Quick links

- **Order from Aisler or Eurocircuits** → `FABRICATION_ORDER.md`
- **As-built design notes** → `V2_DESIGN_NOTES.md`
- **Original spec** → `PCB_DESIGN_PLAN.md`
- **Electrical characterization workflow** → `ELECTRICAL_CHARACTERIZATION.md`
- **What this v2 contributes vs ECTC 2025** → `PUBLICATION_CONTRIBUTION.md`

## Layout of this folder

```
new-pcb/
├── tud-microled-v2.kicad_pro     ← KiCad 9.0.8 project
├── tud-microled-v2.kicad_pcb     ← PCB layout (192 footprints, DRC clean)
├── tud-microled-v2.kicad_sch     ← single-sheet A2 schematic (linked to PCB)
├── PCB_DESIGN_PLAN.md            ← original design spec
├── V2_DESIGN_NOTES.md            ← as-built notes (the source of truth for v4.0.7)
├── VERIFICATION_v4.md            ← electrical-characterization verification
├── ELECTRICAL_CHARACTERIZATION.md ← measurement plan + lab tools
├── FABRICATION_ORDER.md          ← Aisler / Eurocircuits side-by-side order checklist + DNP instructions
├── PUBLICATION_CONTRIBUTION.md   ← v2 publication contributions
├── README.md                     ← you are here
├── library/                      ← KiCad symbol/footprint/3D library
│   ├── README.md                 ← how to wire the library into KiCad
│   ├── symbols/                  ← Würth WL-SFCC custom symbol
│   ├── footprints/               ← WL-SFCC, NTC, header, EIS, TLM, VDP, etc.
│   └── 3dmodels/                 ← STEP models for renders
├── tools/                        ← procedural generators
│   ├── generate_pcb_text.py      ← emits the .kicad_pcb (S-expression generator)
│   ├── generate_schematic.py     ← emits the .kicad_sch (used early; superseded by MCP)
│   └── gen_fab_bom.py            ← emits the fab-neutral BOM CSV (Aisler Beagle / Eurocircuits compatible)
└── fab/                          ← fabrication outputs (ready to upload to Aisler or Eurocircuits)
    ├── tud-microled-v2-fab-bom.csv      ← MPN-based BOM (parses identically at both fabs)
    ├── tud-microled-v2-pos.csv          ← Pick-and-place position file
    ├── tud-microled-v2-top.pdf          ← top visual review (F.Cu+F.Mask+F.SilkS+Edge.Cuts)
    ├── tud-microled-v2-bot.pdf          ← bottom visual review (mirrored)
    ├── tud-microled-v2-schematic.pdf    ← schematic PDF for documentation
    ├── tud-microled-v2.step             ← 3D mechanical model
    ├── tud-microled-v2-gerbers.zip      ← gerber bundle (Eurocircuits fallback)
    ├── gerbers/                          ← per-layer gerbers + drill .drl
    └── preview/                          ← 3D renders + schematic PNG
```

## Design summary

| | |
|---|---|
| Board | 93 × 93 mm, 2-layer FR-4, 1.55 mm |
| Finish | ENIG (Ni 4 µm / Au 0.075 µm) |
| Min track / clearance | 0.20 / 0.30 mm (≥ 2× the 0.15 mm minimum for Aisler standard pool / Eurocircuits Class 4) |
| Min drill / annular ring | 0.30 / 0.15 mm (matches both fabs' spec) |
| Components on board | 192 footprints (69 assembled + 123 bare/DNP) |
| Routed nets | 164 named nets, 0 unconnected |
| Footprints assembled by fab | 4 NTC + 1 R + 64 header pins = 69 placements |
| Footprints bonded by customer | 26 WL-SFCC RGB LEDs (cleanroom, marked DNP for the fab) |

## Quick start

1. Open `tud-microled-v2.kicad_pro` in KiCad 9.0 or newer.
2. Verify `WE_3DMODEL_DIR` is set in **Preferences → Configure Paths**
   (see `library/README.md` for the value).
3. Run `kicad-cli pcb drc new-pcb/tud-microled-v2.kicad_pcb` to confirm 0 violations.
4. Regenerate fab outputs after any PCB edit:
   - `python3 tools/generate_pcb_text.py` to regenerate the PCB from source (⚠ destroys the GND copper pour — see `V2_DESIGN_NOTES.md`)
   - `kicad-cli pcb export gerbers/drill/pdf/pos/step` for fab artifacts
   - `python3 tools/gen_fab_bom.py` for the fab-neutral BOM CSV (works for both Aisler and Eurocircuits)
