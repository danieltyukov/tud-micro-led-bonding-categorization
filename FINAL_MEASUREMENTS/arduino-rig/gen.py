#!/usr/bin/env python3
"""Fritzing-style breadboard render + schematic for the Arduino I-V rig (round 2)."""
import math

OUT = ("/tmp/claude-1000/-home-danieltyukov-workspace-tud-tud-micro-led-bonding-"
       "categorization/27a8d42d-6fd7-4431-9aeb-8e458955a7fc/scratchpad/rig/")

P = 26.0
MM = P / 2.54
NCOL = 30
BB_X, BB_Y = 100.0, 470.0
PADX, PADY = 42.0, 30.0
RAILGAP = 2.8 * P
RAVINE = 2.0 * P

def hx(c): return BB_X + PADX + (c - 1) * P

RAILCOLS = [c for c in range(3, NCOL + 1) if (c - 3) % 6 < 5]
RAILX = [hx(c) for c in RAILCOLS]
def rx(c):
    assert c in RAILCOLS, f"column {c} is a gap in the rail"
    return hx(c)

_y = BB_Y + PADY
Y_TR_OUT = _y; _y += P
Y_TR_IN = _y; _y += RAILGAP
ROWY = {}
for i, r in enumerate("JIHGF"):
    ROWY[r] = _y + i * P
_y = ROWY["F"] + RAVINE
for i, r in enumerate("EDCBA"):
    ROWY[r] = _y + i * P
_y = ROWY["A"] + RAILGAP
Y_GND = _y; _y += P
Y_FORCE = _y
BB_W = PADX * 2 + (NCOL - 1) * P
BB_H = (Y_FORCE + PADY) - BB_Y
BB_BOT = BB_Y + BB_H
BB_R = BB_X + BB_W

UNO_X, UNO_Y = 180.0, 1120.0
UNO_W, UNO_H = 68.6 * MM, 53.4 * MM
UNO_TOP = UNO_Y + 2.6 * MM
UNO_BOT = UNO_Y + UNO_H - 2.6 * MM
DIG_R = {n: 62.0 - i * 2.54 for i, n in enumerate("01234567")}
DIG_L = {n: 40.16 - i * 2.54 for i, n in
         enumerate(["8", "9", "10", "11", "12", "13", "GND", "AREF", "SDA", "SCL"])}
ANA = {n: 62.0 - i * 2.54 for i, n in enumerate(["A5", "A4", "A3", "A2", "A1", "A0"])}
PWR = {n: 44.22 - i * 2.54 for i, n in
       enumerate(["VIN", "GNDb", "GNDa", "5V", "3V3", "RESET", "IOREF", "NC"])}
def ux(mm): return UNO_X + mm * MM

C = dict(force="#d81e1e", ret="#f08c00", gnd="#242424", a0="#0e9c52", a1="#8e3fbe",
         a2="#c2185b", a3="#00acc1", dig="#2f6fd0", board="#f4f1e7", edge="#d2ccb9", hole="#333",
         uno="#0b7c8c", unoE="#065b66", hdr="#131313", gold="#d9b83f",
         pcb="#14532d", pcbE="#0a3a1e", txt="#181818", faint="#8f8a7c")
BAND = dict(blk="#171717", brn="#7a4a16", red="#cf2020", org="#e8781c", yel="#e6c518",
            grn="#1f8f42", blu="#2050c8", gld="#c9a227")
RES = {"220": ["red", "red", "brn", "gld"], "330": ["org", "org", "brn", "gld"],
       "1k": ["brn", "blk", "red", "gld"], "2k": ["red", "blk", "red", "gld"],
       "5k1": ["grn", "brn", "red", "gld"], "10k": ["brn", "blk", "org", "gld"],
       "100": ["brn", "blk", "brn", "gld"]}

o = []
def add(s): o.append(s)
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def T(x, y, s, size=14, fill=None, anchor="middle", weight="normal", op=1.0, rot=None,
      halo=0):
    tr = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot is not None else ""
    hl = (f' stroke="#fbfaf6" stroke-width="{halo}" paint-order="stroke" '
          f'stroke-linejoin="round"') if halo else ""
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" '
        f'fill="{fill or C["txt"]}" text-anchor="{anchor}" opacity="{op}"{tr}{hl}>'
        f'{esc(s)}</text>')

def hole(x, y, s=9.0, op=1.0):
    add(f'<g opacity="{op}"><rect x="{x-s/2:.1f}" y="{y-s/2:.1f}" width="{s}" height="{s}" '
        f'rx="1.6" fill="{C["hole"]}"/><rect x="{x-s/2+1.5:.1f}" y="{y-s/2+1.5:.1f}" '
        f'width="{s-3}" height="{s-3}" rx="1" fill="#0c0c0c"/></g>')

def leg(x1, y1, x2, y2):
    add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#a3a3a3" '
        f'stroke-width="3.6" stroke-linecap="round"/>')

def resistor(x1, y1, x2, y2, code):
    L = math.hypot(x2 - x1, y2 - y1)
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    body = min(68.0, max(40.0, L - 28))
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    leg(x1, y1, x2, y2)
    add(f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({ang:.1f})">'
        f'<rect x="{-body/2:.1f}" y="-11.5" width="{body:.1f}" height="23" rx="8" '
        f'fill="#e7d3af" stroke="#ac9066" stroke-width="1.5"/>')
    step = body / 5.6
    for i, b in enumerate(RES[code]):
        bx = -body / 2 + step * 0.8 + i * step if i < 3 else body / 2 - step * 0.75
        add(f'<rect x="{bx-3.2:.1f}" y="-11.5" width="6.4" height="23" fill="{BAND[b]}"/>')
    add('</g>')

def cap(x1, y1, x2, y2):
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    leg(x1, y1, x2, y2)
    add(f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({ang:.1f})">'
        f'<ellipse rx="18" ry="14.5" fill="#2f6fd0" stroke="#1c4a92" stroke-width="1.6"/>'
        f'<ellipse cx="-5" cy="-4" rx="7" ry="4.5" fill="#74a8ec" opacity="0.6"/></g>')

def plug(x, y, col):
    add(f'<rect x="{x-6.5:.1f}" y="{y-6.5:.1f}" width="13" height="13" rx="2.5" '
        f'fill="{col}" stroke="#00000077" stroke-width="1.3"/>')

def wire(pts, col, w=7.0):
    d = f'M {pts[0][0]:.1f} {pts[0][1]:.1f}'
    i = 1
    while i < len(pts):
        if pts[i] == "C":
            a, b, c2 = pts[i+1], pts[i+2], pts[i+3]
            d += f' C {a[0]:.1f} {a[1]:.1f} {b[0]:.1f} {b[1]:.1f} {c2[0]:.1f} {c2[1]:.1f}'
            i += 4
        else:
            d += f' L {pts[i][0]:.1f} {pts[i][1]:.1f}'; i += 1
    add(f'<path d="{d}" fill="none" stroke="#00000022" stroke-width="{w+6}" '
        f'stroke-linecap="round" stroke-linejoin="round" transform="translate(2.5,3.5)"/>')
    add(f'<path d="{d}" fill="none" stroke="#00000055" stroke-width="{w+3}" '
        f'stroke-linecap="round" stroke-linejoin="round"/>')
    add(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" '
        f'stroke-linecap="round" stroke-linejoin="round"/>')

def pill(x, y, s, col, size=13.5):
    w = len(s) * size * 0.60 + 16
    add(f'<rect x="{x-w/2:.1f}" y="{y-size*0.92:.1f}" width="{w:.1f}" '
        f'height="{size*1.7:.1f}" rx="6" fill="#ffffffe8" stroke="{col}" stroke-width="1.6"/>')
    T(x, y + size * 0.40, s, size, col, "middle", "bold")

# ================================================================= breadboard
def breadboard():
    add(f'<rect x="{BB_X}" y="{BB_Y}" width="{BB_W}" height="{BB_H}" rx="12" '
        f'fill="{C["board"]}" stroke="{C["edge"]}" stroke-width="2.5"/>')
    rv = ROWY["F"] + P * 0.60
    add(f'<rect x="{BB_X+7}" y="{rv:.1f}" width="{BB_W-14}" height="{RAVINE-P*1.2:.1f}" '
        f'rx="5" fill="#e7e2d3"/>')
    for yo, yi, dim in ((Y_TR_OUT, Y_TR_IN, 0.28), (Y_FORCE, Y_GND, 1.0)):
        x1, x2 = BB_X + 16, BB_R - 16
        add(f'<line x1="{x1}" y1="{yo+P*0.62:.1f}" x2="{x2}" y2="{yo+P*0.62:.1f}" '
            f'stroke="#d63b3b" stroke-width="3" opacity="{dim}"/>')
        add(f'<line x1="{x1}" y1="{yi-P*0.62:.1f}" x2="{x2}" y2="{yi-P*0.62:.1f}" '
            f'stroke="#3a63c0" stroke-width="3" opacity="{dim}"/>')
    for c in range(1, NCOL + 1):
        for r in "JIHGFEDCBA":
            hole(hx(c), ROWY[r])

    for x in RAILX:
        for y, op in ((Y_TR_OUT, .28), (Y_TR_IN, .28), (Y_GND, 1), (Y_FORCE, 1)):
            hole(x, y, op=op)
    for r in "JIHGFEDCBA":
        T(BB_X + 26, ROWY[r] + 5, r, 13, C["faint"])
        T(BB_R - 26, ROWY[r] + 5, r, 13, C["faint"])
    for c in range(1, NCOL + 1):
        if c % 5 == 0 or c == 1:
            T(hx(c), rv + P * 0.52, str(c), 12.5, C["faint"])
    T(BB_R - 24, Y_TR_IN + RAILGAP * 0.40, "top half + both top rails: leave empty",
      15, C["faint"], "end")
    T(BB_R - 24, Y_TR_IN + RAILGAP * 0.74,
      "rail holes: first at col 3, then five, a one-hole gap, five, ...",
      15, C["faint"], "end")
    T(BB_X - 16, Y_FORCE + 5, "FORCE", 16, C["force"], "end", "bold")
    T(BB_X - 16, Y_GND + 5, "GND", 16, C["gnd"], "end", "bold")
    T(BB_R + 16, Y_FORCE + 5, "FORCE", 16, C["force"], "start", "bold")
    T(BB_R + 16, Y_GND + 5, "GND", 16, C["gnd"], "start", "bold")

# ==================================================================== arduino
def uno():
    add(f'<rect x="{UNO_X-24:.1f}" y="{UNO_Y+7*MM:.1f}" width="{24+13*MM:.1f}" '
        f'height="{12*MM:.1f}" rx="3" fill="#bcbfc3" stroke="#8d9196" stroke-width="1.5"/>')
    add(f'<rect x="{UNO_X-18:.1f}" y="{UNO_Y+UNO_H-19*MM:.1f}" width="{18+13*MM:.1f}" '
        f'height="{11*MM:.1f}" rx="5" fill="#1b1b1b"/>')
    add(f'<rect x="{UNO_X}" y="{UNO_Y}" width="{UNO_W:.1f}" height="{UNO_H:.1f}" rx="14" '
        f'fill="{C["uno"]}" stroke="{C["unoE"]}" stroke-width="3"/>')
    add(f'<rect x="{ux(26):.1f}" y="{UNO_Y+UNO_H*0.50:.1f}" width="{19*MM:.1f}" '
        f'height="{7.5*MM:.1f}" rx="2" fill="#151618"/>')
    T(ux(35.5), UNO_Y + UNO_H * 0.50 + 4.9 * MM, "ATmega328P", 12, "#c8ccd0")
    T(ux(50), UNO_Y + UNO_H * 0.33, "ARDUINO  UNO", 23, "#e9f7f9", weight="bold")
    def hdr(mms, y, labs, below):
        xs = [ux(m) for m in mms]
        add(f'<rect x="{min(xs)-0.55*P:.1f}" y="{y-0.58*P:.1f}" '
            f'width="{max(xs)-min(xs)+1.1*P:.1f}" height="{1.16*P:.1f}" rx="3" '
            f'fill="{C["hdr"]}"/>')
        for m, lb in zip(mms, labs):
            x = ux(m)
            add(f'<rect x="{x-6.5:.1f}" y="{y-6.5:.1f}" width="13" height="13" rx="1.5" '
                f'fill="{C["gold"]}"/><rect x="{x-3:.1f}" y="{y-3:.1f}" width="6" '
                f'height="6" fill="#111"/>')
            T(x, y + (1.34 * P if below else -0.95 * P), lb, 11.5, "#e9f7f9", weight="bold")
    hdr([DIG_L[n] for n in DIG_L], UNO_TOP,
        ["8", "9", "10", "11", "12", "13", "GND", "ARF", "SDA", "SCL"], True)
    hdr([DIG_R[n] for n in DIG_R], UNO_TOP, ["0", "1", "2", "3", "4", "5", "6", "7"], True)
    hdr([PWR[n] for n in PWR], UNO_BOT,
        ["VIN", "GND", "GND", "5V", "3V3", "RST", "IOR", "NC"], False)
    hdr([ANA[n] for n in ANA], UNO_BOT, ["A5", "A4", "A3", "A2", "A1", "A0"], False)
    T(ux(53), UNO_TOP + 2.6 * P, "DIGITAL", 13, "#bfe6ec", weight="bold")
    T(ux(55.5), UNO_BOT - 2.5 * P, "ANALOG IN", 13, "#bfe6ec", weight="bold")
    T(ux(35), UNO_BOT - 2.5 * P, "POWER", 13, "#bfe6ec", weight="bold")

# ================================================================= DUT header
DUT_X, DUT_Y, DPP = 1010.0, 82.0, 19.0
def dpx(p): return DUT_X + 46 + (p - 1) * DPP
DUT_W = 92 + 31 * DPP
DUT_HY = DUT_Y + 130

def dut():
    add(f'<rect x="{DUT_X}" y="{DUT_Y}" width="{DUT_W:.1f}" height="222" rx="10" '
        f'fill="{C["pcb"]}" stroke="{C["pcbE"]}" stroke-width="2.5"/>')
    T(DUT_X + DUT_W / 2, DUT_Y + 32, "your PCB  -  SOUTH 32-pin header", 18, "#e2f5e9",
      weight="bold")
    T(DUT_X + DUT_W / 2, DUT_Y + 55, "pins 1-4 = D1,   5-8 = D2,   ...   29-32 = D8",
      13.5, "#9fd9b4")
    add(f'<rect x="{DUT_X+36:.1f}" y="{DUT_HY-17:.1f}" width="{32*DPP:.1f}" height="34" '
        f'rx="3" fill="#131313"/>')
    labs = ["KR", "A", "KG", "KB"]
    cols = {"KR": "#ff7a7a", "A": "#ffd166", "KG": "#7bd88f", "KB": "#8ec2ff"}
    for p in range(1, 33):
        x, k = dpx(p), (p - 1) % 4
        add(f'<rect x="{x-6.5:.1f}" y="{DUT_HY-6.5:.1f}" width="13" height="13" rx="1.5" '
            f'fill="{C["gold"]}"/><rect x="{x-3:.1f}" y="{DUT_HY-3:.1f}" width="6" '
            f'height="6" fill="#111"/>')
        T(x, DUT_HY + 30, labs[k], 10.5, cols[labs[k]], weight="bold")
        if p % 4 == 1 or p == 32:
            T(x, DUT_HY - 15, str(p), 10, "#cfe8d8")
    for d in range(8):
        x0, x1 = dpx(4 * d + 1) - 9, dpx(4 * d + 4) + 9
        add(f'<rect x="{x0:.1f}" y="{DUT_HY+40:.1f}" width="{x1-x0:.1f}" height="21" '
            f'rx="4" fill="none" stroke="#5fae7e" stroke-width="1.4"/>')
        T((x0 + x1) / 2, DUT_HY + 55, f"D{d+1}", 12, "#cfe8d8", weight="bold")
    T(DUT_X + DUT_W / 2, DUT_Y + 208,
      "die Dn:   anode = pin 4n-2      red K = 4n-3      green K = 4n-1      blue K = 4n",
      14, "#e2f5e9", weight="bold")

# ==================================================================== canvas
W, H = 1780, 2010
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}" font-family="DejaVu Sans, Helvetica, Arial, sans-serif">')
add(f'<rect width="{W}" height="{H}" fill="#fbfaf6"/>')
T(60, 58, "Arduino I-V rig  -  build this", 32, "#111", "start", "bold")
T(60, 88, "Top view, drawn hole for hole. Only the bottom half of the breadboard is used.",
  16, "#5a5a5a", "start")

breadboard(); uno(); dut()

BANK = [("7", 14, "220", "220 R"), ("6", 16, "330", "330 R"),
        ("5", 18, "1k", "1 k"), ("4", 20, "2k", "2 k"),
        ("3", 22, "5k1", "5.1 k"), ("2", 24, "10k", "10 k")]

# ------------------------------------------------------------- wires (first)
for pin, c, code, lab in BANK:
    x0, y0, x1, y1 = ux(DIG_R[pin]), UNO_TOP, hx(c), ROWY["E"]
    wire([(x0, y0), "C", (x0, y0 - 170), (x1, y1 + 215), (x1, y1)], C["dig"], 6.5)
wire([(hx(4), ROWY["E"]), (hx(8), ROWY["E"])], C["ret"], 6.5)
for pin, tx, ty, col in (("GNDa", rx(3), Y_GND, C["gnd"]),
                         ("A0", hx(4), ROWY["D"], C["a0"]),
                         ("A1", rx(6), Y_FORCE, C["a1"]),
                         ("A2", hx(8), ROWY["D"], C["a2"]),
                         ("A3", rx(10), Y_GND, C["a3"])):
    src = PWR if pin.startswith("GND") else ANA
    x0, y0 = ux(src[pin]), UNO_BOT
    wire([(x0, y0), "C", (x0 - 160, y0 - 120), (tx + 200, ty + 320), (tx, ty)], col, 6.5)
wire([(rx(29), Y_FORCE), "C", (rx(29) + 110, Y_FORCE + 4), (BB_R + 46, Y_FORCE - 130),
      (BB_R + 48, Y_FORCE - 340), "C", (BB_R + 52, BB_Y - 90), (dpx(2) - 120, DUT_HY + 150),
      (dpx(2), DUT_HY)], C["force"], 6.5)
wire([(hx(4), ROWY["C"]), "C", (hx(4), ROWY["C"] - 300), (hx(4) - 20, BB_Y - 46),
      (hx(4) + 130, BB_Y - 74), "C", (hx(4) + 560, BB_Y - 128), (dpx(1) - 250, DUT_HY + 130),
      (dpx(1), DUT_HY)], C["ret"], 6.5)
add(f'<path d="M {rx(7):.1f} {Y_FORCE:.1f} L {rx(9):.1f} {Y_FORCE:.1f}" '
    f'stroke="#9a9a9a" stroke-width="7" stroke-linecap="round" stroke-dasharray="7 6"/>')

# ------------------------------------------------------- components (on top)
for pin, c, code, lab in BANK:
    resistor(hx(c), ROWY["A"], rx(c + 1), Y_FORCE, code)
cap(hx(4), ROWY["A"], rx(5), Y_GND)
cap(hx(8), ROWY["A"], rx(9), Y_GND)
resistor(hx(8), ROWY["B"], rx(11), Y_GND, "100")
cap(rx(11), Y_FORCE, rx(13), Y_GND)

# --------------------------------------------------------------------- plugs
for pin, c, code, lab in BANK:
    plug(ux(DIG_R[pin]), UNO_TOP, C["dig"]); plug(hx(c), ROWY["E"], C["dig"])
plug(hx(4), ROWY["E"], C["ret"]); plug(hx(8), ROWY["E"], C["ret"])
for pin, tx, ty, col in (("GNDa", rx(3), Y_GND, C["gnd"]), ("A0", hx(4), ROWY["D"], C["a0"]),
                         ("A1", rx(6), Y_FORCE, C["a1"]), ("A2", hx(8), ROWY["D"], C["a2"]),
                         ("A3", rx(10), Y_GND, C["a3"])):
    src = PWR if pin.startswith("GND") else ANA
    plug(ux(src[pin]), UNO_BOT, col); plug(tx, ty, col)
plug(rx(29), Y_FORCE, C["force"]); plug(hx(4), ROWY["C"], C["ret"])

# -------------------------------------------------------------------- labels
for pin, c, code, lab in BANK:
    T(hx(c) + 6, ROWY["F"] - 10, f"D{pin}   {lab}", 15, C["dig"], "start", "bold",
      rot=-90, halo=5)
pill(hx(28), ROWY["I"], "resistor bank", C["dig"], 15)
pill(hx(10), ROWY["I"], "RETURN", C["ret"], 15)
pill(hx(10), ROWY["I"] + 24, "cols 4 + 8", C["ret"], 12)
T(rx(5), Y_GND + 30, "C2", 14, "#1c4a92", "middle", "bold", halo=5)
T(rx(9) + 4, Y_GND - 26, "C3", 14, "#1c4a92", "middle", "bold", halo=5)
T(rx(11) - 22, Y_GND + 18, "C1", 14, "#1c4a92", "end", "bold", halo=5)
T(rx(11) + 30, ROWY["B"] - 10, "100 R sense", 14, "#7a5a10", "middle", "bold", halo=5)


# ============================================================== build order
OX, OY, OW = 60.0, 112.0, 540.0
add(f'<rect x="{OX}" y="{OY}" width="{OW}" height="262" rx="12" fill="#fff" '
    f'stroke="#e2ded2" stroke-width="2"/>')
T(OX + 22, OY + 34, "build it in this order", 19, "#111", "start", "bold")
STEPS = [
  "six bank resistors: row A col 14..24, other leg FORCE one col right",
  "jumper D2..D7 into row E of its own bank column",
  "link E4 to E8 - all ten of those holes are now RETURN",
  "100 R from B8 down to the GND rail",
  "C2 from A4, C3 from A8 to GND rail; C1 across the rails (68 nF)",
  "jumper UNO GND to the GND rail col 3 - the only ground wire",
  "jumper A0 to D4, A2 to D8, A1 to FORCE col 6, A3 to GND col 10",
  "two F/M jumpers out to the die you are testing",
]
for i, st in enumerate(STEPS):
    y = OY + 62 + i * 25
    add(f'<circle cx="{OX+32}" cy="{y-4:.1f}" r="9" fill="#eef4fb" stroke="#2f6fd0" '
        f'stroke-width="1.4"/>')
    T(OX + 32, y, str(i + 1), 12, "#2f6fd0", "middle", "bold")
    T(OX + 50, y, st, 14, "#333", "start")

# ================================================================== legend
LX, LY, LW = 1010.0, 470.0, DUT_W
add(f'<rect x="{LX}" y="{LY}" width="{LW:.1f}" height="392" rx="12" fill="#fff" '
    f'stroke="#e2ded2" stroke-width="2"/>')
T(LX + 24, LY + 36, "every wire, by colour", 19, "#111", "start", "bold")
LEG = [(C["dig"], "6 x   UNO D2..D7   ->  row E, cols 24 22 20 18 16 14"),
       (C["gnd"], "1 x   UNO GND      ->  GND rail, col 3"),
       (C["a0"], "1 x   UNO A0       ->  RETURN, hole D4"),
       (C["a1"], "1 x   UNO A1       ->  FORCE rail, col 6"),
       (C["a2"], "1 x   UNO A2       ->  RETURN, hole D8"),
       (C["a3"], "1 x   UNO A3       ->  GND rail, col 10   NEW"),
       (C["ret"], "1 x   link E4 - E8   (RETURN becomes one node)"),
       (C["force"], "F/M   FORCE col 29 ->  die anode, pin 4n-2"),
       (C["ret"], "F/M   RETURN, C4   ->  die cathode you are testing")]
for i, (col, lab) in enumerate(LEG):
    y = LY + 72 + i * 34
    add(f'<rect x="{LX+26}" y="{y-7}" width="52" height="13" rx="6.5" fill="{col}" '
        f'stroke="#00000055"/>')
    T(LX + 92, y + 6, lab, 14.5, "#222", "start")

NX, NY = LX, LY + 412
add(f'<rect x="{NX}" y="{NY}" width="{LW:.1f}" height="470" rx="12" fill="#fff9ec" '
    f'stroke="#ecdcae" stroke-width="2"/>')
T(NX + 24, NY + 36, "check before you power up", 19, "#111", "start", "bold")
NOTES = ["12 male-male jumpers: 6 bank + A0 A1 A2 A3 + GND + 1 link",
         "2 female-male jumpers - the only wires leaving the board",
         "7 resistors: six in the bank, one 100 R RETURN to GND rail",
         "3 caps, 68 nF each: C1 rail to rail, C2 + C3 on RETURN",
         "nothing in series between an ADC pin and the node it reads",
         "UNO GND touches the breadboard exactly once",
         "A0 and A2 land on the same node - that is intended",
         "A3 reads the GND rail: it cancels the ADC offset",
         "rail holes line up with the columns, starting at col 3",
         "each rail is one strip, so any hole on it is the same node",
         "the grey dash is only for boards with split rails"]
for i, n in enumerate(NOTES):
    T(NX + 26, NY + 74 + i * 34, "•", 16, "#b08a2a", "start", "bold")
    T(NX + 46, NY + 74 + i * 34, n, 14.5, "#3a3a3a", "start")
T(NX + 26, NY + 442, "To change channel: move only the two female-male jumpers.",
  15, "#8a5a00", "start", "bold")

# ================================================================ schematic
SX, SY, SW, SH = 1010.0, NY + 492, DUT_W, 560.0
add(f'<rect x="{SX}" y="{SY}" width="{SW:.1f}" height="{SH}" rx="12" fill="#fff" '
    f'stroke="#e2ded2" stroke-width="2"/>')
T(SX + 24, SY + 36, "the same thing as a circuit", 19, "#111", "start", "bold")

def sline(pts, col="#222", w=2.4):
    d = f'M {pts[0][0]:.1f} {pts[0][1]:.1f}' + "".join(
        f' L {p[0]:.1f} {p[1]:.1f}' for p in pts[1:])
    add(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" '
        f'stroke-linecap="round" stroke-linejoin="round"/>')

def dot(x, y, col="#222"):
    add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.2" fill="{col}"/>')

def zig(x, y, L, vert=False, w=8):
    n, seg = 6, L / 6.0
    pts = [(0, 0)]
    for i in range(n):
        pts.append(((i + 0.5) * seg, w if i % 2 == 0 else -w))
    pts.append((L, 0))
    pts = [(x + b, y + a) if vert else (x + a, y + b) for a, b in pts]
    sline(pts)

def gndsym(x, y, col="#222"):
    for i, hw in enumerate((11, 7, 3.5)):
        add(f'<line x1="{x-hw:.1f}" y1="{y+i*4.5:.1f}" x2="{x+hw:.1f}" y2="{y+i*4.5:.1f}" '
            f'stroke="{col}" stroke-width="2.4" stroke-linecap="round"/>')

def scap(x, y):
    sline([(x, y), (x, y + 10)]); sline([(x, y + 22), (x, y + 32)])
    for yy in (y + 10, y + 22):
        add(f'<line x1="{x-13:.1f}" y1="{yy:.1f}" x2="{x+13:.1f}" y2="{yy:.1f}" '
            f'stroke="#222" stroke-width="2.8"/>')

BUS = SX + 232
y0 = SY + 108
STEP = 27
for i, (pin, c, code, lab) in enumerate(BANK[::-1]):
    y = y0 + i * STEP
    T(SX + 26, y + 5, f"D{pin}", 14, C["dig"], "start", "bold")
    sline([(SX + 70, y), (SX + 80, y)])
    zig(SX + 80, y, 64, w=7)
    sline([(SX + 144, y), (BUS, y)])
    T(SX + 152, y - 7, lab, 12, "#555", "start")
    dot(BUS, y, C["force"])
FBOT = SY + 300
sline([(BUS, SY + 68), (BUS, FBOT)], C["force"], 3.2)
T(BUS - 10, SY + 80, "FORCE", 15, C["force"], "end", "bold")

# --- A1 tap off FORCE
sline([(BUS, SY + 68), (SX + 590, SY + 68)], C["force"], 3.2)
T(SX + 598, SY + 73, "A1", 16, C["a1"], "start", "bold")
scap(SX + 500, SY + 68); gndsym(SX + 500, SY + 102)
T(SX + 516, SY + 92, "C1", 12.5, "#1c4a92", "start")

# --- LED branch
LEDX = SX + 340
sline([(BUS, FBOT), (LEDX, FBOT), (LEDX, FBOT + 26)], C["force"], 3.2)
add(f'<path d="M {LEDX-16:.1f} {FBOT+26:.1f} L {LEDX+16:.1f} {FBOT+26:.1f} '
    f'L {LEDX:.1f} {FBOT+58:.1f} Z" fill="#ffd166" stroke="#222" stroke-width="2"/>')
add(f'<line x1="{LEDX-16:.1f}" y1="{FBOT+58:.1f}" x2="{LEDX+16:.1f}" y2="{FBOT+58:.1f}" '
    f'stroke="#222" stroke-width="3"/>')
T(LEDX + 30, FBOT + 36, "one die, one colour", 13, "#333", "start", "bold")
T(LEDX + 30, FBOT + 54, "on your PCB", 13, "#333", "start")
T(LEDX - 26, FBOT + 20, "F/M jumper  ->  pin 4n-2", 12, C["force"], "end")
T(LEDX - 26, FBOT + 74, "F/M jumper  ->  cathode pin", 12, C["ret"], "end")

# --- RETURN
RY = FBOT + 92
sline([(LEDX, FBOT + 58), (LEDX, RY)], C["ret"], 3.2)
sline([(SX + 250, RY), (SX + 452, RY)], C["ret"], 3.2)
dot(LEDX, RY, C["ret"])
T(SX + 244, RY + 5, "RETURN", 15, C["ret"], "end", "bold")
sline([(SX + 250, RY), (SX + 250, RY + 18)], C["ret"], 3.2)
zig(SX + 250, RY + 18, 58, vert=True, w=8)
sline([(SX + 250, RY + 76), (SX + 250, RY + 92)])
gndsym(SX + 250, RY + 92)
T(SX + 268, RY + 44, "100 R sense", 13, "#7a5a10", "start", "bold")
sline([(SX + 250, RY + 76), (SX + 120, RY + 76)], C["a3"], 3.2)
dot(SX + 250, RY + 76, C["a3"])
T(SX + 112, RY + 81, "A3", 16, C["a3"], "end", "bold")
T(SX + 268, RY + 106, "UNO GND", 14, C["gnd"], "start", "bold")

sline([(SX + 452, RY), (SX + 590, RY)], C["ret"], 3.2)
T(SX + 598, RY + 5, "A0", 16, C["a0"], "start", "bold")
sline([(SX + 400, RY), (SX + 400, RY + 74), (SX + 590, RY + 74)], C["ret"], 3.2)
dot(SX + 400, RY, C["ret"])
T(SX + 598, RY + 79, "A2", 16, C["a2"], "start", "bold")
scap(SX + 500, RY); gndsym(SX + 500, RY + 34)
T(SX + 516, RY + 24, "C2", 12.5, "#1c4a92", "start")
scap(SX + 540, RY + 74); gndsym(SX + 540, RY + 108)
T(SX + 556, RY + 98, "C3", 12.5, "#1c4a92", "start")
T(SX + 24, SY + SH - 40,
  "A0 and A2 sit on the same node, so they read the same voltage.",
  13.5, "#666", "start")
T(SX + 24, SY + SH - 18,
  "i = (A2 - A3) / R_SENSE. The difference cancels the ADC offset.",
  13.5, C["a3"], "start", "bold")

add('</svg>')
open(OUT + "breadboard.svg", "w").write("\n".join(o))
print("ok")
