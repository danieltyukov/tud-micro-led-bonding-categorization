# v2 PCB — design notes (delivered build)

What's actually shipped in this iteration of `tud-microled-v2.kicad_pcb`.
Companion to `PCB_DESIGN_PLAN.md` (the spec) and
`ELECTRICAL_CHARACTERIZATION.md` (the measurement plan).

---

## Status: **fab-ready** ✅

| Check | Result |
|---|---|
| KiCad version | 9.0.8 (file format 20241229) |
| Board dimensions | 100.0 × 80.0 mm, 2-layer FR-4, 1.6 mm |
| Surface finish | ENIG (recommended) |
| DRC violations | **0** |
| Unconnected pads | **0** |
| Footprint errors | **0** |
| Footprints placed | 153 |
| Nets defined | 139 |
| Net DRC | clean |

Generated procedurally by `tools/generate_pcb_text.py` — fully reproducible.
Re-run the script any time to regenerate. The script writes the .kicad_pcb
S-expression directly (bypassing the SWIG bindings, which had several bugs
during the build).

## What's on the board

### Top half
- **6 × 6 bond-pad DoE array** at 3.5 mm pitch, centered horizontally.
  - Rows 1–2: plain square 1×1 mm (control geometry)
  - Rows 3–4: plain square + 4-corner mini-pads
  - Rows 5–6: rounded-square (R=50/100/200 µm) + 4-corner mini-pads
  - Each site is on its own net (`BP_R<r>C<c>_P1`) — probe directly.

### Middle (top → bottom)
- **3 TLM ladders** (W=0.25, 0.5, 1.0 mm), each with 7 fingers swept
  through contact spacings 5/10/20/50/100/200 µm.
  - Local pad clearance override of 2 µm so DRC doesn't trip on the
    µm-scale spacings.
- **4 Van der Pauw cloverleaves** (arm widths 1.0, 0.5, 0.25, 0.1 mm),
  arm length scaled to leave > 0.3 mm corner-to-corner gap.

### Lower middle
- **2 daisy chains** (N=6, N=12). N=24 is deferred to v2.1 because
  50 × 1.8 mm = 90 mm width competes with the LED row footprint.
- 4-wire access via 2 probe pads per chain.

### South
- **8 × Würth WL-SFCC 0404 superflat RGB LEDs** (P/N 150044M155220),
  pitch 10 mm.
- 4 probe pads per LED (A / KG / KB / KR), spread ±3 mm. Probe order
  matches the side of the LED pad to avoid trace crossings.
- **Common anode bus** routed on B.Cu via vias at each anode probe.

### Periphery
- 4 × 1 mm fiducials at the corners
- Asymmetric "L" silkscreen at NW for orientation
- 2 × 30-pin 2.54 mm headers (Tier 2 — solder once, plug into bench fixture)
- mm ruler on south silkscreen (10 mm major ticks)
- Title block: "TUD micro-LED v2 / Ahmed Abdelwahab - ECTM + ITEC"

## Design rules

| Rule | Value |
|---|---|
| Clearance | 0.15 mm |
| Min track width | 0.15 mm |
| Default track width | 0.20 mm |
| Via | 0.6 mm diameter / 0.3 mm drill |
| Min via | 0.45 mm / 0.20 mm |
| Min hole | 0.20 mm |

These match standard Eurocircuits 4-class (and JLCPCB 1-2 oz) capability.

## What's intentionally not in v2.0

1. **DoE probe pads with routing** — direct probing of the 1×1 mm bond pads is
   used instead. Routing fan-out to a separate Tier-1 probe strip needs
   proper 2-layer escape and isn't worth the DRC churn for v2.0.
2. **N=24 daisy chain** — needs 90 mm width; deferred.
3. **Tier-3 edge connector** — Tier 2 + Tier 1 cover all immediate needs.
4. **Schematic** — research test boards traditionally ship PCB-only. The
   v1 board (`old-pcb/`) had no schematic either.
5. **Net classes** — single class with above defaults is fine for this design.

## Fabrication outputs (`fab/`)

| File | Purpose |
|---|---|
| `gerbers/` | Per-layer Gerber files (X2 format) |
| `gerbers/*.drl` | Excellon drill files (PTH + NPTH) |
| `tud-microled-v2-gerbers.zip` | Upload this single file to your fab |
| `tud-microled-v2.step` | 3D model (5.4 MB) for mechanical fit / review |
| `tud-microled-v2.pdf` | 1.9 MB PDF for design review |
| `tud-microled-v2-pos.csv` | Pick-and-place position file (mm units) |
| `tud-microled-v2-bom.csv` | BOM — populated parts only (8 × WL-SFCC) |
| `preview/board_top.png` | Top render (1600×1280) |
| `preview/board_bottom.png` | Bottom render (1600×1280) |

## How to fabricate

1. **Upload `fab/tud-microled-v2-gerbers.zip`** to Eurocircuits or JLCPCB.
2. Order with: 2-layer FR-4, 1.6 mm thick, ENIG finish, black or green mask,
   white silkscreen.
3. Order a matching **100 µm laser-cut SS stencil** via Eurocircuits
   `eC-stencil-mate` (same vendor recommendation as v1).
4. Total fab cost estimate: ~€40 for 5 boards (Eurocircuits standard).

## Iteration log

| Iter | DRC | Notes |
|---|---|---|
| v0 (pcbnew SWIG attempt) | 1802 | All pads stacked at (0,0); SetPosition() was absolute, not local |
| v1 (text format, broken) | n/a | `(plot_on_all_layers_selection 0x0)` invalid; KiCad refused to load |
| v2 (text format, all nets bad) | n/a | `(net N "name")` in segments invalid; KiCad refused to load |
| v3 | 269 | Pads correctly placed; routing collided with adjacent bond pads |
| v4 | 69 | Removed DoE probe pads; daisy chain layout re-jigged |
| v5 | 17 | Reordered LED probes by side; TLM probe routing dropped |
| v6 | 0 (with 23 unconnected) | TLM pads got local clearance override; silk text moved |
| **v7** | **0 / 0** | Mini-pads overlap main pad; common-anode bus on B.Cu via vias |
