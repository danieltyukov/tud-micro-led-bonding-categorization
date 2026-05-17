# v2 PCB — Design Notes (v3 iteration, delivered)

What's actually shipped in `tud-microled-v2.kicad_pcb`. Companion to
`PCB_DESIGN_PLAN.md` (spec) and `ELECTRICAL_CHARACTERIZATION.md` (test plan).

---

## Status: **fab-ready** ✅

| Check | Result |
|---|---|
| KiCad version | 9.0.8 (file format 20241229) |
| Board | **100 × 100 mm**, 2-layer FR-4, 1.6 mm |
| Surface finish | ENIG (Ni 4 µm / Au 0.075 µm) |
| Board size | **93 × 93 mm** (under Tresky T-3000-PRO envelope of 95 × 95 mm) |
| **DRC violations** | **0** |
| **Unconnected pads** | **0** |
| Footprints | 194 (incl. 26 WL-SFCC LEDs, 4 NTCs, 1 EIS load R, 64 header pins) |
| Headers | 32 + 32 = 64 pins, both rows aligned to same X grid for breadboard mating |
| Calibration | EIS CAL pads added in v4.0 (OPEN / SHORT / 100Ω LOAD) for full Nyquist calibration |
| Designer | **Daniel Tyukov · student no. 5714699 · ET4277 / ET4391** |

Generated procedurally by `tools/generate_pcb_text.py` (fully reproducible).
Re-run any time to regenerate from scratch.

---

## What's on the board

### Front side (F.Cu + F.SilkS)

| Section | Y range | Contents |
|---|---|---|
| Title block | 3 – 11 | 3 zones: TUDelft mark / project + version + size / Daniel Tyukov + student no. + course codes |
| TIER-2 NORTH header | 13.5 | 30 × 2.54 mm PTH pins, **user-jumperable** |
| DoE BOND-PAD array | 17 – 43 | 6 × 6 isolated test pads at 3.5 mm pitch; plain → +4 minis → rounded; LEGEND box on right |
| TLM LADDERS | 45 – 58 | 3 banks (W = 0.25 / 0.5 / 1.0 mm) × 7 fingers × spacings 5/10/20/50/100/200 µm |
| VAN DER PAUW | 59 – 67 | 4 cloverleaves (W = 1.0 / 0.5 / 0.25 / 0.1 mm) |
| LED DAISY CHAINS | 68 – 77.5 | N=6 + N=12 WL-SFCC LEDs in series via RED chain (A → K_R). 2N bonds tested per chain. K_G / K_B isolated per-LED (probe directly on pad). IN/OUT probe pads at each chain end. |
| WL-SFCC LEDs | 79.5 – 86.7 | 8 × Würth 0404 super-flat RGB; A bus on B.Cu |
| TIER-2 SOUTH header | 89 | **32 × 2.54 mm PTH pins, pre-wired to all 32 LED signals** |
| mm ruler | 93.5 | 0–80 mm with major + minor ticks |

### Back side (B.SilkS)

| Section | Y range | Contents |
|---|---|---|
| Title block | 3 – 12 | TUDelft mark + project name + date |
| FABRICATION | 16 – 36 | Stack-up, finish, mask, clearance/trace specs |
| ASSEMBLY | 38 – 58 | Paste, stencil, bonder, reflow, metrology toolchain |
| DESIGNER | 60 – 72 | Daniel Tyukov, student #, courses, ECTM + ITEC, prior work attribution |
| TIER-2 SOUTH PINOUT | 73.5 – 86 | Pin→LED mapping: `1-4 D1, 5-8 D2, ... 29-32 D8` (A, KG, KB, KR) |

---

## Routing summary

### South header — pre-wired (F.Cu)

**32 of 32 pins routed.** Each pin → its assigned LED probe pad through a 3-segment
Manhattan route:
- Vertical from pin pad → 4-lane horizontal jog → vertical to probe pad
- 4 horizontal lanes (Y = 87.7 / 87.3 / 86.9 / 86.5 mm) — one per role (A / KG / KB / KR)
- All on F.Cu, lanes sit in the 2 mm gap between header pad keepout (y > 88.15) and probe pad top (y < 86.135)

**Common-anode B.Cu bus** ties together all 8 LED A-probe pads via vias at each
A probe, with a horizontal trace on B.Cu at y = 85.5 mm.

### North header — user-jumperable

The 30 north pins are pre-assigned to specific VDP / DC / TLM nets in the
pin pad's NET field, but **no copper traces are routed** to those targets.
The user solders a 0.1" header into the holes and runs jumper wires from
the header pins to the Tier-1 probe pads of whichever structure they want
to access.

Why not pre-route? Several attempts to route 26 long B.Cu traces from
2.54 mm-pitch header pins to scattered VDP/DC/TLM contacts (some at sub-mm
spacing per VDP) introduced unavoidable clearance violations: pin pitch
(2.54 mm) is barely larger than via diameter + clearance, and the per-VDP
contact spacing means horizontal jogs collide with adjacent verticals.

Freerouting got 24 of 26 in one run but was inconsistent across runs.
Manual routing with per-zone fanout reached down to ~46 violations
(crossings between adjacent pin verticals and horizontals) but never to
zero. Deferring to v3.1 (4-layer board with B.Cu fanout bus zone).

---

## Design rules

| Rule | Value |
|---|---|
| Clearance | 0.15 mm |
| Min track width | 0.15 mm |
| Default track width | 0.20 mm |
| Via | 0.6 mm Ø / 0.3 mm drill |
| Min via | 0.45 / 0.20 mm |
| Min hole | 0.20 mm |

Matches Aisler standard pool and Eurocircuits class-4 capability.

---

## Fab outputs (in `fab/`)

| File | Purpose |
|---|---|
| `gerbers/` | Per-layer Gerber files (X2 format) + drill `.drl` + `.gbrjob` |
| `tud-microled-v2-gerbers.zip` | Gerber bundle — Aisler accepts the native `.kicad_pcb` so this is only needed if falling back to Eurocircuits |
| `tud-microled-v2.step` | 3D model for mechanical fit |
| `tud-microled-v2-top.pdf` | Top-side review PDF (F.Cu + F.Mask + F.SilkS + Edge.Cuts) |
| `tud-microled-v2-bot.pdf` | Bottom-side review PDF (mirrored, B.Cu + B.Mask + B.SilkS + Edge.Cuts) |
| `tud-microled-v2-pos.csv` | Pick-and-place position file (mm, both sides) |
| `tud-microled-v2-bom.csv` | BOM (LEDs + optional headers) |
| `preview/board_top.png` | 1800×1800 top 3D render |
| `preview/board_bottom.png` | 1800×1800 bottom 3D render |

---

## How to use the south header

1. Solder a 32-pin 0.1" male header strip into the south through-holes (5 min).
2. Plug a 32-pin ribbon cable.
3. The other end maps as follows:

| Cable wire | Pin | Signal |
|---:|---:|---|
| 1 | 1 | `LED_VCC` (D1 A) |
| 2 | 2 | `LED1_KG` |
| 3 | 3 | `LED1_KB` |
| 4 | 4 | `LED1_KR` |
| 5 | 5 | `LED_VCC` (D2 A — redundant) |
| 6 | 6 | `LED2_KG` |
| ⋮ | ⋮ | (pattern repeats for D1…D8) |
| 32 | 32 | `LED8_KR` |

Every 4-pin block = 1 LED. Pin 1 of each block is anode (= common LED_VCC).

---

## Iteration log

| Iter | DRC | Highlight |
|---|---:|---|
| 8 (first routing attempt) | 1802 | Pad SetPosition() bug — all pads stacked at (0,0) |
| ... | ... | (geometric layout convergence) |
| 16 (south routing v2) | 0 | South pre-wired D1–D7, north user-jumperable |
| 19 (silkscreen polish) | 0 | TIER-2 SOUTH PINOUT box on back, all 8 LEDs documented |
| 22-25 (north routing attempts) | 46–293 | Tried manual + freerouting; both hit fundamental geometric limits |
| 27 | 0 | South to D1-D8 (32 pins), north user-jumperable, silkscreen polished |
| 28 (v3.6) | 1 cosmetic | Dummy-die DC replaced with WL-SFCC LED chains (N=6 + N=12, R-series) |
| 29 (v3.7) | 0 | Compressed to 95×95 mm, 4 north pins (1/10/22/30) routed to chain endpoints |
| 30 (v3.8) | 0 | 32-pin north header aligned with south, silk circles on routed pins (pins 3/10/19/32) |
| 31 (v3.9) | 0 | Compressed to 93×93 mm with breathing room, ruler restored, TH1-4 labels relocated |
| 32 (v3.9.1) | 0 | Back-side PINOUT compacted to single line (no truncation, no ambiguous O→U) |
| **33 (v4.0 — delivered)** | **0** | **EIS CAL section added (OPEN/SHORT/100Ω LOAD) — full Nyquist calibration capability for impedance spectroscopy of bonded LEDs** |

---

## What's NOT in this build

- North header pre-routed traces — see "Routing summary" above
~~- Schematic — research test boards traditionally ship PCB-only; can be
  added in a future iteration by reverse-engineering the placement script~~

**Update (v4.0.7):** Single-sheet A2 schematic added — see
`tud-microled-v2.kicad_sch` and `fab/tud-microled-v2-schematic.pdf`.
Generated via KiCad MCP tools, linked to the PCB by matching component
references and footprint paths. 36 components placed (26 LEDs + 4 NTCs +
1 resistor + 3 test points + 2 × 32-pin connectors), 129 net labels
snap-connected to pin endpoints, 24 NC markers on user-jumperable north
pins. ERC residual: 21 expected "single-pin net" warnings on EIS probe
test points and LEDn_{KG,KB} south-header labels (by design — these nets
go to PCB probe pads only, not other components).
