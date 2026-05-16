# Old PCB — v1 ("Electrical test + LED-no solder")

The original characterization PCB designed by **Ahmed Abdelwahab** and used
for the **2025 IEEE ECTC paper** "Pick-and-Release: A Novel Contactless
Bonding Method for Die Attachment" (DOI: 10.1109/ECTC51687.2025.00363).

## Files

| File                                            | Description                              |
|------------------------------------------------|------------------------------------------|
| `Electrical test + LED-no solder.kicad_pcb`     | KiCad 6 PCB (version 20221018), 4141 lines |
| `Electrical test + LED-no solder.kicad_pro`     | KiCad project metadata                   |
| `Electrical test + LED-no solder.kicad_prl`     | KiCad project local state (per-user)     |
| `~...kicad_pcb.lck`                             | KiCad session lockfile — delete if KiCad isn't currently running |

## Key facts (see ../PROJECT_DETAILS.md §2 for the full breakdown)

- Board outline: **58.75 × 61.51 mm**, 2-layer FR-4, 1.6 mm thick, ENIG finish.
- **165 footprints**, all unlabelled — a deliberate choice for clean optical
  metrology (Keyence 3D laser scans).
- File name suffix "**-no solder**" = solder-paste apertures are NOT defined
  on the F.Paste / B.Paste layers. Solder paste was screen-printed through a
  separate **100 µm laser-cut stainless steel stencil** (Eurocircuits
  `eC-stencil-mate`) with **TS391LT Sn42 / Bi57.6 / Ag0.4 paste**.
- On-board structures: 5 × 5 array of 1 mm² bond pads, Daisy-Chain (DC), Van
  der Pauw (VDP), Transmission-Line-Model (TLM) ladders, RGB-LED footprints
  matching the Würth WL-SFCC 0404.

## Why this is "old"

The v1 board has known limitations called out in the ECTC paper and the new
design plan (`../new-pcb/PCB_DESIGN_PLAN.md`):

1. Die tilt 5–8° on the 1 mm × 1 mm pads. The "+ four-corner-mini-pads"
   geometry on a small subset of pads brought tilt down to **~0.2°**, so the
   v2 board should apply that geometry **everywhere**.
2. No silkscreen structure IDs — every structure has to be located by its
   coordinates on the board, which slows characterization.
3. TLM finger pattern is geometrically fixed; we want a proper ladder with
   contact-spacing sweep (5/10/20/50/100/200 µm).
4. No fiducial markers for the Tresky T-3000-PRO die bonder.

## Don't edit this folder

This is a historical reference snapshot. New work goes in `../new-pcb/`.
