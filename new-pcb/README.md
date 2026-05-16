# new-pcb — v2 Micro-LED Bonding Characterization PCB

The next-generation PCB. Spec lives in **`PCB_DESIGN_PLAN.md`** — start there.

## Layout of this folder

```
new-pcb/
├── PCB_DESIGN_PLAN.md   ← THE plan (read first)
├── README.md            ← you are here
└── library/             ← KiCad symbol/footprint/3D-model library
    ├── README.md        ← how to wire the library into KiCad
    ├── symbols/
    ├── footprints/
    └── 3dmodels/
```

KiCad project files (`*.kicad_pro / *.kicad_sch / *.kicad_pcb`) will land
here once the schematic + layout work begins (Phase 1–2 in §13 of the plan).

## Quick start once a KiCad project exists

1. Open `tud-microled-v2.kicad_pro` in KiCad 6 or newer.
2. Make sure `WE_3DMODEL_DIR` is set in **Preferences → Configure Paths**
   (see `library/README.md` for the value).
3. Run `bash tools/build.sh` to regenerate paste apertures, run DRC, and
   re-export Gerbers.
