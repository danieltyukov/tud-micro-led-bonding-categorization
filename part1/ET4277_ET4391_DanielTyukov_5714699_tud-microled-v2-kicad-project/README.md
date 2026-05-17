# tud-microled-v2 — KiCad project + Aisler order bundle

Daniel Tyukov · student no. 5714699 · ET4277 + ET4391 · Part 1

| Folder | Purpose |
|---|---|
| `kicad_project/` | Full KiCad 9.0.8 project — open `tud-microled-v2.kicad_pro` to inspect the schematic and PCB. Library contains Würth WL-SFCC + custom NTC / EIS-load / probe-pad / TLM / VDP / DoE footprints. Python generators in `tools/` rebuild the PCB and BOM from source. |
| `aisler_order/` | Everything Aisler needs, ready to drag-drop into the order form. See `FABRICATION_ORDER.md` for the step-by-step checklist and the DNP note for the 26 LEDs. |
| `datasheets/` | Verified datasheets for the four assembled component classes (Würth WL-SFCC LED, Murata NCP15 NTC, Vishay TNPW0603 resistor, Würth WR-PHD pin header). |
| `references/` | The five IEEE-Xplore papers cited in the report. |
