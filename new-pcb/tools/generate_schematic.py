#!/usr/bin/env python3
"""
Generate tud-microled-v2.kicad_sch from scratch — a single-sheet A2-landscape
schematic linked to the existing PCB by footprint references and net names.

Strategy
--------
The PCB was originally PCB-only (no schematic). This generator emits a clean
schematic that documents the electrical intent and lets `Tools > Update PCB
from Schematic` round-trip in KiCad.

Layout (594 × 420 mm A2 landscape):
  Top    : Title block + design notes
  Left   : LED row D1-D8 (common anode + 24 cathodes)
  Middle : DCL6 + DCL12 daisy chains (R-cathode series)
  Right  : 4 NTCs (thermistor V_F-TSP) + EIS calibration block
  Bottom : H_N_1..32 north header + H_S_1..32 south header

Net labels replace long cross-sheet wires — any two pins sharing a label name
are electrically connected (standard KiCad practice).
"""

from __future__ import annotations
import uuid
from pathlib import Path
from textwrap import dedent

REPO = Path(__file__).resolve().parents[2]
OUT  = REPO / "new-pcb" / "tud-microled-v2.kicad_sch"

# KiCad uses mm; 1.27 mm = 50 mil = base grid.
GRID = 1.27
A2_W = 594.0
A2_H = 420.0

def U() -> str:
    return str(uuid.uuid4())

def snap(v: float) -> float:
    return round(v / GRID) * GRID

# ─────────────────────────────────────────────────────────────────────────
# Symbol library definitions (embedded — KiCad needs lib_symbols inline).
# ─────────────────────────────────────────────────────────────────────────

LIB_R = '''(symbol "Device:R" (pin_numbers hide) (pin_names (offset 0)) (in_bom yes) (on_board yes)
  (property "Reference" "R" (at 2.032 0 90) (effects (font (size 1.27 1.27))))
  (property "Value" "R" (at 0 0 90) (effects (font (size 1.27 1.27))))
  (property "Footprint" "" (at -1.778 0 90) (effects (font (size 1.27 1.27)) hide))
  (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
  (symbol "R_0_1"
    (rectangle (start -1.016 -2.54) (end 1.016 2.54)
      (stroke (width 0.254) (type default)) (fill (type none))))
  (symbol "R_1_1"
    (pin passive line (at 0 3.81 270) (length 1.27)
      (name "~" (effects (font (size 1.27 1.27))))
      (number "1" (effects (font (size 1.27 1.27)))))
    (pin passive line (at 0 -3.81 90) (length 1.27)
      (name "~" (effects (font (size 1.27 1.27))))
      (number "2" (effects (font (size 1.27 1.27)))))))'''

LIB_LED_RGB = '''(symbol "LED_RGB_4pad" (pin_numbers hide) (pin_names (offset 0.508) hide) (in_bom yes) (on_board yes)
  (property "Reference" "D" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
  (property "Value" "WL-SFCC" (at 0 -7.62 0) (effects (font (size 1.27 1.27))))
  (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
  (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
  (symbol "LED_RGB_4pad_0_1"
    (rectangle (start -3.81 3.81) (end 3.81 -3.81)
      (stroke (width 0.254) (type default)) (fill (type none)))
    (polyline (pts (xy -2.54 -2.54) (xy -1.27 -2.54) (xy -1.27 -1.27))
      (stroke (width 0.2) (type default)) (fill (type none)))
    (polyline (pts (xy -2.54 -1.27) (xy -1.27 -1.27) (xy -1.27 0))
      (stroke (width 0.2) (type default)) (fill (type none)))
    (polyline (pts (xy -2.54 0) (xy -1.27 0) (xy -1.27 1.27))
      (stroke (width 0.2) (type default)) (fill (type none)))
    (text "R" (at -3.0 -2.54 0) (effects (font (size 0.8 0.8))))
    (text "G" (at -3.0 -1.27 0) (effects (font (size 0.8 0.8))))
    (text "B" (at -3.0 0 0) (effects (font (size 0.8 0.8))))
    (text "A" (at -3.0 1.91 0) (effects (font (size 0.8 0.8)))))
  (symbol "LED_RGB_4pad_1_1"
    (pin passive line (at 5.08 2.54 180) (length 1.27)
      (name "A" (effects (font (size 1 1))))
      (number "1" (effects (font (size 0.9 0.9)))))
    (pin passive line (at 5.08 -2.54 180) (length 1.27)
      (name "KG" (effects (font (size 1 1))))
      (number "2" (effects (font (size 0.9 0.9)))))
    (pin passive line (at 5.08 -1.27 180) (length 1.27)
      (name "KB" (effects (font (size 1 1))))
      (number "3" (effects (font (size 0.9 0.9)))))
    (pin passive line (at 5.08 0 180) (length 1.27)
      (name "KR" (effects (font (size 1 1))))
      (number "4" (effects (font (size 0.9 0.9)))))))'''

LIB_NTC = '''(symbol "Device:Thermistor_NTC" (pin_numbers hide) (pin_names (offset 0.254)) (in_bom yes) (on_board yes)
  (property "Reference" "TH" (at 0 6.35 0) (effects (font (size 1.27 1.27))))
  (property "Value" "Thermistor_NTC" (at 0 4.064 0) (effects (font (size 1.27 1.27))))
  (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
  (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
  (symbol "Thermistor_NTC_0_1"
    (rectangle (start -1.016 -2.54) (end 1.016 2.54)
      (stroke (width 0.254) (type default)) (fill (type none)))
    (polyline (pts (xy -2.286 -2.794) (xy -1.778 -2.794) (xy 1.778 2.794) (xy 1.778 2.286))
      (stroke (width 0.254) (type default)) (fill (type none)))
    (text "t°" (at 2.4 0 0) (effects (font (size 1 1)))))
  (symbol "Thermistor_NTC_1_1"
    (pin passive line (at 0 3.81 270) (length 1.27)
      (name "~" (effects (font (size 1.27 1.27))))
      (number "1" (effects (font (size 1.27 1.27)))))
    (pin passive line (at 0 -3.81 90) (length 1.27)
      (name "~" (effects (font (size 1.27 1.27))))
      (number "2" (effects (font (size 1.27 1.27)))))))'''

LIB_CONN_32 = '''(symbol "Connector_Generic:Conn_01x32" (pin_names (offset 1.016) hide) (in_bom yes) (on_board yes)
  (property "Reference" "J" (at 0 43.18 0) (effects (font (size 1.27 1.27))))
  (property "Value" "Conn_01x32" (at 0 -43.18 0) (effects (font (size 1.27 1.27))))
  (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
  (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
  (symbol "Conn_01x32_1_1"
    (rectangle (start -1.27 41.91) (end 1.27 -41.91)
      (stroke (width 0.254) (type default)) (fill (type background)))''' + '\n' + '\n'.join(
    f'''    (pin passive line (at -5.08 {39.37 - (i)*2.54:.2f} 0) (length 3.81)
      (name "Pin_{i+1}" (effects (font (size 1.27 1.27))))
      (number "{i+1}" (effects (font (size 1.27 1.27)))))'''
    for i in range(32)
) + '))'

LIB_TP = '''(symbol "Connector:TestPoint" (pin_names (offset 1.016) hide) (in_bom yes) (on_board yes)
  (property "Reference" "TP" (at 0 5.842 0) (effects (font (size 1.27 1.27))))
  (property "Value" "TestPoint" (at 0 3.302 0) (effects (font (size 1.27 1.27))))
  (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
  (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
  (symbol "TestPoint_0_1"
    (circle (center 0 2.032) (radius 0.508)
      (stroke (width 0)) (fill (type none))))
  (symbol "TestPoint_1_1"
    (pin passive line (at 0 0 90) (length 2.54)
      (name "1" (effects (font (size 1.27 1.27))))
      (number "1" (effects (font (size 1.27 1.27)))))))'''

LIB_GND = '''(symbol "power:GND" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes)
  (property "Reference" "#PWR" (at 0 -6.35 0) (effects (font (size 1.27 1.27)) hide))
  (property "Value" "GND" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
  (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
  (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
  (symbol "GND_0_1"
    (polyline (pts (xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27))
      (stroke (width 0)) (fill (type none))))
  (symbol "GND_1_1"
    (pin power_in line (at 0 0 270) (length 0) hide
      (name "GND" (effects (font (size 1.27 1.27))))
      (number "1" (effects (font (size 1.27 1.27)))))))'''

LIB_VCC = '''(symbol "power:VCC" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes)
  (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))
  (property "Value" "VCC" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
  (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
  (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
  (symbol "VCC_0_1"
    (polyline (pts (xy -0.762 1.27) (xy 0 2.54) (xy 0.762 1.27))
      (stroke (width 0)) (fill (type none)))
    (circle (center 0 1.27) (radius 0.762)
      (stroke (width 0.254)) (fill (type none))))
  (symbol "VCC_1_1"
    (pin power_in line (at 0 0 90) (length 1.27) hide
      (name "VCC" (effects (font (size 1.27 1.27))))
      (number "1" (effects (font (size 1.27 1.27)))))))'''

# ─────────────────────────────────────────────────────────────────────────
# Emit helpers
# ─────────────────────────────────────────────────────────────────────────

def emit_symbol(lib_id, ref, value, footprint, x, y, rot=0, mirror=None, dnp=False):
    """Place an instance of a library symbol at (x, y)."""
    inst_uuid = U()
    mirror_str = f"(mirror {mirror}) " if mirror else ""
    dnp_str = " (dnp yes)" if dnp else ""
    return f'''  (symbol (lib_id "{lib_id}") (at {x} {y} {rot}) {mirror_str}(unit 1)
    (in_bom yes) (on_board yes){dnp_str}
    (uuid {inst_uuid})
    (property "Reference" "{ref}" (at {x} {y - 7} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{value}" (at {x} {y + 7} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "{footprint}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "~" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))
    (instances (project "tud-microled-v2"
      (path "/" (reference "{ref}") (unit 1)))))'''

def emit_wire(x1, y1, x2, y2):
    return f'''  (wire (pts (xy {x1} {y1}) (xy {x2} {y2}))
    (stroke (width 0) (type default)) (uuid {U()}))'''

def emit_label(name, x, y, rot=0):
    return f'''  (label "{name}" (at {x} {y} {rot})
    (effects (font (size 1.27 1.27)) (justify left bottom))
    (uuid {U()}))'''

def emit_global_label(name, x, y, rot=0, shape="input"):
    return f'''  (global_label "{name}" (shape {shape}) (at {x} {y} {rot})
    (effects (font (size 1.27 1.27)) (justify left))
    (uuid {U()})
    (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide)))'''

def emit_junction(x, y):
    return f'''  (junction (at {x} {y}) (diameter 0) (color 0 0 0 0)
    (uuid {U()}))'''

def emit_no_connect(x, y):
    return f'  (no_connect (at {x} {y}) (uuid {U()}))'

def emit_text(text, x, y, size=1.5, rot=0, bold=False):
    bold_str = " bold" if bold else ""
    return f'''  (text "{text}" (at {x} {y} {rot})
    (effects (font (size {size} {size}){bold_str}) (justify left bottom))
    (uuid {U()}))'''

# ─────────────────────────────────────────────────────────────────────────
# Generate the schematic content
# ─────────────────────────────────────────────────────────────────────────

def main():
    out = []

    # ── Header / paper / title ─────────────────────────────────────────
    out.append(f'''(kicad_sch (version 20250114) (generator "tud-microled-v2-sch-gen") (generator_version "1.0")
  (uuid {U()})
  (paper "A2")
  (title_block
    (title "TUD Micro-LED Bond Characterization — v4.0 PCB")
    (date "2026-05-17")
    (rev "v4.0.7")
    (company "TU Delft · ECTM + ITEC")
    (comment 1 "Daniel Tyukov · student no. 5714699 · ET4277 + ET4391")
    (comment 2 "Single-sheet schematic — linked to tud-microled-v2.kicad_pcb")
    (comment 3 "Bare-pad test structures (TLM/VDP/DoE/probe pads) are PCB-only and not shown here")
    (comment 4 "Generated procedurally by tools/generate_schematic.py — see V2_DESIGN_NOTES.md")
  )''')

    # ── lib_symbols cache ───────────────────────────────────────────────
    out.append("  (lib_symbols")
    for lib in [LIB_R, LIB_LED_RGB, LIB_NTC, LIB_CONN_32, LIB_TP, LIB_GND, LIB_VCC]:
        out.append("    " + lib.replace("\n", "\n    "))
    out.append("  )")

    # ── BLOCK 1: 8× WL-SFCC LEDs (D1-D8) common anode + 24 cathodes ────
    out.append('\n  ; ══ BLOCK 1: LED MATRIX D1-D8 (common anode, 24 cathode signals) ══')
    out.append(emit_text("BLOCK 1 — LED MATRIX D1-D8 (common-anode WL-SFCC RGB)",
                         15, 25, size=2.5, bold=True))
    out.append(emit_text("All anodes tied to LED_VCC. Cathodes go to south header H_S_1..32.",
                         15, 30, size=1.5))
    # Two rows of 4
    led_x0 = 20
    led_y0 = 50
    led_dx = 25  # horizontal spacing
    led_dy = 35  # vertical spacing
    for n in range(1, 9):
        col = (n - 1) % 4
        row = (n - 1) // 4
        x = led_x0 + col * led_dx
        y = led_y0 + row * led_dy
        out.append(emit_symbol("LED_RGB_4pad", f"D{n}", "WL-SFCC RGB",
                               "LED_SMD_Wurth:D_Wurth_WL-SFCC-0404superflat",
                               x, y))
        # Pin endpoints relative to symbol origin:
        # A  at +5.08, +2.54  → connect to LED_VCC label
        # KG at +5.08, -2.54  → label LEDn_KG
        # KB at +5.08, -1.27  → label LEDn_KB
        # KR at +5.08,  0.00  → label LEDn_KR
        out.append(emit_wire(x + 5.08, y + 2.54, x + 7.62, y + 2.54))
        out.append(emit_label("LED_VCC", x + 7.62, y + 2.54))
        for dy, role in [(-2.54, "KG"), (-1.27, "KB"), (0, "KR")]:
            out.append(emit_wire(x + 5.08, y + dy, x + 7.62, y + dy))
            out.append(emit_label(f"LED{n}_{role}", x + 7.62, y + dy))

    # ── BLOCK 2: DCL6 daisy chain (6 LEDs in series via K_R) ───────────
    out.append('\n  ; ══ BLOCK 2: DCL6 daisy chain — 6 LEDs in series via K_R bonds ══')
    out.append(emit_text("BLOCK 2 — DCL6 (6 LEDs in series, R-cathode chain)",
                         15, 130, size=2.5, bold=True))
    out.append(emit_text("A→K_R chain tests 2N=12 bonds. K_G/K_B per LED isolated (probe directly).",
                         15, 135, size=1.5))
    out.append(emit_text("Chain endpoints DCL6_IN (H_N_3) and DCL6_OUT (H_N_10) routed on PCB.",
                         15, 139, size=1.3))
    chain6_x0 = 20
    chain6_y = 160
    chain6_dx = 22  # horizontal spacing per LED
    chain_nets_6 = ["DCL6_IN"] + [f"DCL6_J{i}" for i in range(1, 6)] + ["DCL6_OUT"]
    for n in range(1, 7):
        x = chain6_x0 + (n - 1) * chain6_dx
        y = chain6_y
        ref = f"DCL6_L{n}"
        out.append(emit_symbol("LED_RGB_4pad", ref, "WL-SFCC RGB",
                               "LED_SMD_Wurth:D_Wurth_WL-SFCC-0404superflat",
                               x, y, dnp=True))
        # Anode goes to chain_nets_6[n-1]; K_R goes to chain_nets_6[n]
        a_label = chain_nets_6[n - 1]
        kr_label = chain_nets_6[n]
        out.append(emit_wire(x + 5.08, y + 2.54, x + 8.89, y + 2.54))
        out.append(emit_label(a_label, x + 8.89, y + 2.54))
        out.append(emit_wire(x + 5.08, y, x + 8.89, y))
        out.append(emit_label(kr_label, x + 8.89, y))
        # K_G and K_B → per-LED labels (isolated, used for probing K_G/K_B individually)
        out.append(emit_wire(x + 5.08, y - 1.27, x + 8.89, y - 1.27))
        out.append(emit_label(f"DCL6_L{n}_KB", x + 8.89, y - 1.27))
        out.append(emit_wire(x + 5.08, y - 2.54, x + 8.89, y - 2.54))
        out.append(emit_label(f"DCL6_L{n}_KG", x + 8.89, y - 2.54))

    # ── BLOCK 3: DCL12 daisy chain (12 LEDs) ─────────────────────────────
    out.append('\n  ; ══ BLOCK 3: DCL12 daisy chain — 12 LEDs in series via K_R ══')
    out.append(emit_text("BLOCK 3 — DCL12 (12 LEDs in series, R-cathode chain) — tests 2N=24 bonds",
                         15, 200, size=2.5, bold=True))
    out.append(emit_text("Endpoints DCL12_IN (H_N_19) and DCL12_OUT (H_N_32) routed on PCB.",
                         15, 205, size=1.3))
    chain12_x0 = 20
    chain12_y = 230
    chain12_dx = 22
    chain_nets_12 = ["DCL12_IN"] + [f"DCL12_J{i}" for i in range(1, 12)] + ["DCL12_OUT"]
    # Two rows of 6 to fit horizontally
    for n in range(1, 13):
        col = (n - 1) % 6
        row = (n - 1) // 6
        x = chain12_x0 + col * chain12_dx
        y = chain12_y + row * 35
        ref = f"DCL12_L{n}"
        out.append(emit_symbol("LED_RGB_4pad", ref, "WL-SFCC RGB",
                               "LED_SMD_Wurth:D_Wurth_WL-SFCC-0404superflat",
                               x, y, dnp=True))
        a_label = chain_nets_12[n - 1]
        kr_label = chain_nets_12[n]
        out.append(emit_wire(x + 5.08, y + 2.54, x + 8.89, y + 2.54))
        out.append(emit_label(a_label, x + 8.89, y + 2.54))
        out.append(emit_wire(x + 5.08, y, x + 8.89, y))
        out.append(emit_label(kr_label, x + 8.89, y))
        out.append(emit_wire(x + 5.08, y - 1.27, x + 8.89, y - 1.27))
        out.append(emit_label(f"DCL12_L{n}_KB", x + 8.89, y - 1.27))
        out.append(emit_wire(x + 5.08, y - 2.54, x + 8.89, y - 2.54))
        out.append(emit_label(f"DCL12_L{n}_KG", x + 8.89, y - 2.54))

    # ── BLOCK 4: NTCs (4 thermistors for V_F-TSP thermometry) ───────────
    out.append('\n  ; ══ BLOCK 4: NTC thermistors TH1-TH4 for V_F-TSP thermal sensing ══')
    out.append(emit_text("BLOCK 4 — NTC thermistors (TH1-TH4)",
                         350, 25, size=2.5, bold=True))
    out.append(emit_text("Murata NCP15XH103J03RC · 10 kΩ ±5 % · B25/85 = 3380 K",
                         350, 30, size=1.5))
    out.append(emit_text("Probe NTCn via north header; common GND return.",
                         350, 34, size=1.3))
    ntc_x0 = 360
    ntc_y0 = 50
    ntc_dx = 25
    for n in range(1, 5):
        x = ntc_x0 + (n - 1) * ntc_dx
        y = ntc_y0
        ref = f"TH{n}"
        out.append(emit_symbol("Device:Thermistor_NTC", ref, "10k NCP15XH103J03RC",
                               "TUD-microLED:NTC_0402", x, y))
        # Pin 1 = top (signal), Pin 2 = bottom (GND)
        out.append(emit_wire(x, y - 3.81, x, y - 7))
        out.append(emit_label(f"NTC{n}", x, y - 7))
        out.append(emit_wire(x, y + 3.81, x, y + 7.62))
        # GND symbol
        out.append(emit_symbol("power:GND", f"#PWR_NTC{n}", "GND", "", x, y + 7.62))

    # ── BLOCK 5: EIS calibration (LOAD 100Ω + OPEN + SHORT pads) ────────
    out.append('\n  ; ══ BLOCK 5: EIS calibration block (Nyquist OPEN/SHORT/LOAD) ══')
    out.append(emit_text("BLOCK 5 — EIS calibration set",
                         350, 90, size=2.5, bold=True))
    out.append(emit_text("LCR-meter Nyquist plot calibration: 100 Ω LOAD + OPEN (∞) + SHORT (0 Ω) refs.",
                         350, 95, size=1.5))
    # Load resistor R_EIS_LOAD
    eis_x = 365
    eis_y = 115
    out.append(emit_symbol("Device:R", "R_EIS_LOAD", "100R 0.1% TNPW0603",
                           "TUD-microLED:EIS_Load_0603", eis_x, eis_y))
    out.append(emit_wire(eis_x, eis_y - 3.81, eis_x, eis_y - 7.62))
    out.append(emit_label("EIS_LOAD_A", eis_x, eis_y - 7.62))
    out.append(emit_wire(eis_x, eis_y + 3.81, eis_x, eis_y + 7.62))
    out.append(emit_label("EIS_LOAD_B", eis_x, eis_y + 7.62))
    # OPEN test points (2 separate pads)
    open_x = 400
    open_y = 110
    out.append(emit_symbol("Connector:TestPoint", "TP_EIS_OPEN_A", "EIS_OPEN_A",
                           "TUD-microLED:Probe_1.27mm", open_x, open_y))
    out.append(emit_label("EIS_OPEN_A", open_x, open_y - 5))
    out.append(emit_symbol("Connector:TestPoint", "TP_EIS_OPEN_B", "EIS_OPEN_B",
                           "TUD-microLED:Probe_1.27mm", open_x + 10, open_y))
    out.append(emit_label("EIS_OPEN_B", open_x + 10, open_y - 5))
    # SHORT test point (single net = jumpered pair)
    out.append(emit_symbol("Connector:TestPoint", "TP_EIS_SHORT", "EIS_SHORT",
                           "TUD-microLED:Probe_1.27mm", open_x + 25, open_y))
    out.append(emit_label("EIS_SHORT", open_x + 25, open_y - 5))

    # ── BLOCK 6: Headers (1×32 each) ────────────────────────────────────
    out.append('\n  ; ══ BLOCK 6: 32-pin headers (north + south breadboard interface) ══')
    out.append(emit_text("BLOCK 6 — Headers (single-row 1×32, 2.54 mm pitch)",
                         15, 320, size=2.5, bold=True))
    out.append(emit_text("Würth WR-PHD 61304011121 (cut to 32 from 1×40). North = jumperable, south = pre-wired.",
                         15, 325, size=1.5))

    # SOUTH HEADER — 32 pins, all routed to LED signals
    # Pattern: pin (4k+1) = LED_VCC, (4k+2) = KG, (4k+3) = KB, (4k+4) = KR  for k=0..7
    h_s_x = 60
    h_s_y = 360
    out.append(emit_symbol("Connector_Generic:Conn_01x32", "J_SOUTH", "H_S 1×32",
                           "TUD-microLED:Header_2.54mm", h_s_x, h_s_y))
    # Connect each pin to its net label
    for i in range(32):
        pin_n = i + 1
        # Pin Y in symbol coords: top pin (pin 1) at y - 39.37, last (pin 32) at y + 39.37
        py = h_s_y - 39.37 + i * 2.54
        # Label to the left of the pin
        out.append(emit_wire(h_s_x - 5.08, py, h_s_x - 10, py))
        # Determine net
        role = ["A", "KG", "KB", "KR"][(pin_n - 1) % 4]
        led_n = (pin_n - 1) // 4 + 1
        net = "LED_VCC" if role == "A" else f"LED{led_n}_{role}"
        out.append(emit_label(f"{net}  (H_S_{pin_n})", h_s_x - 10, py, rot=180))

    # NORTH HEADER — 32 pins, only 8 routed
    h_n_x = 250
    h_n_y = 360
    out.append(emit_symbol("Connector_Generic:Conn_01x32", "J_NORTH", "H_N 1×32",
                           "TUD-microLED:Header_2.54mm", h_n_x, h_n_y))
    north_routed = {
        3:  "DCL6_IN",
        5:  "NTC1",
        10: "DCL6_OUT",
        13: "NTC2",
        19: "DCL12_IN",
        21: "NTC3",
        29: "NTC4",
        32: "DCL12_OUT",
    }
    for i in range(32):
        pin_n = i + 1
        py = h_n_y - 39.37 + i * 2.54
        out.append(emit_wire(h_n_x - 5.08, py, h_n_x - 10, py))
        if pin_n in north_routed:
            out.append(emit_label(f"{north_routed[pin_n]}  (H_N_{pin_n})", h_n_x - 10, py, rot=180))
        else:
            # User-jumperable — leave a no-connect marker plus annotation
            out.append(emit_no_connect(h_n_x - 5.08, py))
            out.append(emit_text(f"H_N_{pin_n}  (NC — user jumper)", h_n_x - 9, py - 0.5, size=0.9))

    # ── BLOCK 7: Design notes (bare-pad test structures, etc.) ──────────
    out.append('\n  ; ══ BLOCK 7: Design notes ══')
    out.append(emit_text("BLOCK 7 — DESIGN NOTES (test structures NOT on schematic)",
                         440, 230, size=2.0, bold=True))
    notes = [
        "Bare-gold test structures (123 placements, no nets to header):",
        "  • DoE bond-pad array: 36 × isolated 1 mm pads + 4 minis (3.5 mm pitch)",
        "  • TLM ladders W=0.25/0.5/1.0 mm × 7 fingers, gaps 200/300/500/1000/2000/4000 µm",
        "  • Van der Pauw cloverleaves W=1.0/0.5/0.25/0.15 mm × 4 contacts each",
        "  • Probe pads PP_* (46): manual 4-wire probe access to bonded LEDs",
        "  • TC pads (4): thermocouple-wire solder lands for in-situ reflow temp",
        "  • Fiducials FID1-4: optical alignment marks for P&P",
        "",
        "All 123 bare pads are documented on PCB silk + V2_DESIGN_NOTES.md.",
        "No electrical wiring → not shown on schematic.",
        "",
        "Net naming convention:",
        "  • LED_VCC          — 8-LED common anode bus (B.Cu pour)",
        "  • LEDn_K{R,G,B}    — individual color cathode of D1..D8",
        "  • DCL{6,12}_IN/OUT — chain endpoints (R-series)",
        "  • DCL{6,12}_Jk     — internal junction k of chain",
        "  • DCLn_Lk_K{G,B}   — isolated G/B cathode of chain LED k",
        "  • NTCn             — thermistor sense line (n=1..4)",
        "  • EIS_LOAD_A/B     — 100 Ω calibration resistor pads",
        "  • EIS_OPEN_A/B     — open-circuit cal probes",
        "  • EIS_SHORT        — short-circuit cal pad (jumpered pair)",
        "  • GND              — common return (NTC pin 2, B.Cu pour)",
    ]
    for i, line in enumerate(notes):
        out.append(emit_text(line, 440, 240 + i * 4, size=1.2))

    out.append("\n  (sheet_instances\n    (path \"/\" (page \"1\"))\n  )")
    out.append(")")

    text = "\n".join(out)
    OUT.write_text(text)
    print(f"Wrote {OUT}")
    print(f"  Lines: {text.count(chr(10)) + 1}")
    print(f"  Symbol placements: {text.count('(lib_id ')}")

if __name__ == "__main__":
    main()
