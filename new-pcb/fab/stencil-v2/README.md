# Stencil v2 — corrected solder-paste stencil (Eurocircuits)

Generated from `tud-microled-v2.kicad_pcb` (KiCad 9.0). This folder contains the
data to order a **new top-side solder-paste stencil** that fixes the previous one.

## What was wrong with the first stencil

The previous stencil had apertures on **only 10 pads** — `TH1–TH4` (thermistors)
and `R_EIS_LOAD` — because those were the only pads carrying an `F.Paste` layer.
Every bond/LED/test pad lacked a paste aperture, so the stencil came back
effectively "reversed": openings only where solder had already been hand-applied,
and nothing where paste actually needs to be printed.

## What this stencil does (two aperture types on `F.Paste`)

1. **Paste apertures** (1:1 with the copper pad) on **all 327 exposed conductive
   pads** so paste can be printed: DoE bond pads (`BP_*`), WL-SFCC LEDs
   (`D*`, `DCL6_*`, `DCL12_*`), probe pads (`PP_*`), TLM/VDP test structures,
   thermocouple pads (`TC*`), and fiducials (`FID*`).

2. **Clearance reliefs** (a window drawn *around the component body*, not a paste
   dot) so the foil lies flat over parts already on the board — **no bulges**:
   | Part | Relief window (mm) |
   |------|--------------------|
   | `H_N` header (top pin row) | 5.68,12.05 → 87.32,14.95 |
   | `H_S` header (bottom pin row) | 5.68,83.55 → 87.32,86.45 |
   | `TH1` | 16.6,76.15 → 18.8,77.45 |
   | `TH2` | 36.6,76.15 → 38.8,77.45 |
   | `TH3` | 56.6,76.15 → 58.8,77.45 |
   | `TH4` | 76.6,76.15 → 78.8,77.45 |
   | `R_EIS_LOAD` | 73.52,34.41 → 77.48,36.38 |

   The header pins/bodies and the soldered thermistors/resistor pass through these
   windows. **Note:** these are open windows in the paste layer — if you don't want
   paste falling through over the already-soldered parts, simply don't squeegee
   across those windows (or tape them off during print).

## Files

- `tud-microled-v2-F_Paste.gbr` — the stencil aperture layer (**this is the stencil**)
- `tud-microled-v2-Edge_Cuts.gbr` — board outline, for alignment/registration
- `tud-microled-v2-stencil-v2.zip` — both of the above, zipped for upload
- `paste_preview.svg` / `paste_preview.png` — visual check of the aperture pattern
- `drc_report.txt` — KiCad DRC result (0 violations)

## Ordering notes (Eurocircuits stencil service)

- Order **top stencil only** (no bottom-side components/paste).
- Suggested foil thickness **100–120 µm**. Reasoning: smallest bond apertures are
  0.4 mm (LED) and 0.5 mm (DoE) squares — fine at 100–150 µm. **But** the VDP
  (0.15 mm) and TLM (0.25 mm) test-structure apertures are at/below the reliable
  paste-release limit for thicker foils; at ≤100 µm they release better. Those are
  test pads, not bond sites, so partial transfer there is acceptable if you prefer
  a thicker foil for the bond pads.
- The foil can be larger than the 93 × 93 mm board and trimmed after, as discussed.
