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
       "100": ["brn", "blk", "brn", "gld"],
       "100k": ["brn", "blk", "yel", "gld"]}

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
W, H = 1780, 1780
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}" font-family="DejaVu Sans, Helvetica, Arial, sans-serif">')
add(f'<rect width="{W}" height="{H}" fill="#fbfaf6"/>')
T(60, 58, "Step 6  -  reverse leakage.  Rewire from the sweep rig.", 31, "#111", "start", "bold")
T(60, 88, "Different circuit. The bank comes off, the die is driven BACKWARDS, and the DMM "
          "reads across a 100 k resistor.", 16, "#5a5a5a", "start")

DUT_X, DUT_Y, DPP = 1010.0, 82.0, 19.0
def dpx(p): return DUT_X + 46 + (p - 1) * DPP
DUT_W = 92 + 31 * DPP
DUT_HY = DUT_Y + 130
breadboard(); uno(); dut()

# ---------------------------------------------------------------- what stays
BANK = [("7", 14, "220"), ("6", 16, "330"), ("5", 18, "1k"),
        ("4", 20, "2k"), ("3", 22, "5k1"), ("2", 24, "10k")]
add('<g opacity="0.20">')
for pin, c, code in BANK:
    resistor(hx(c), ROWY["A"], rx(c + 1), Y_FORCE, code)
cap(hx(4), ROWY["A"], rx(5), Y_GND)
cap(hx(8), ROWY["A"], rx(9), Y_GND)
resistor(hx(8), ROWY["B"], rx(11), Y_GND, "100")
cap(rx(11), Y_FORCE, rx(13), Y_GND)
wire([(hx(4), ROWY["E"]), (hx(8), ROWY["E"])], C["ret"], 6.5)
for pin, tx, ty, col in (("A0", hx(4), ROWY["D"], C["a0"]), ("A1", rx(6), Y_FORCE, C["a1"]),
                         ("A2", hx(8), ROWY["D"], C["a2"]), ("A3", rx(10), Y_GND, C["a3"])):
    x0, y0 = ux(ANA[pin]), UNO_BOT
    wire([(x0, y0), "C", (x0 - 160, y0 - 120), (tx + 200, ty + 320), (tx, ty)], col, 6.5)
add('</g>')

# ------------------------------------------------------- REMOVE: the 6 jumpers
for pin, c, code in BANK:
    x0, y0 = ux(DIG_R[pin]), UNO_TOP
    x1, y1 = hx(c), ROWY["E"]
    add(f'<path d="M {x0:.1f} {y0:.1f} C {x0:.1f} {y0-170:.1f} {x1:.1f} {y1+215:.1f} '
        f'{x1:.1f} {y1:.1f}" fill="none" stroke="#d81e1e" stroke-width="4" '
        f'stroke-dasharray="9 8" opacity="0.5"/>')
pill(hx(20), BB_BOT + 44, "REMOVE these six D2-D7 jumpers - that kills the bank", "#d81e1e", 15)
T(hx(20), ROWY["C"], "everything faded stays on the board, it is simply not used",
  14.5, "#9a9a9a")

# ---------------------------------------------------------------- KEEP: GND
gx, gy = ux(PWR["GNDa"]), UNO_BOT
wire([(gx, gy), "C", (gx - 160, gy - 120), (rx(3) + 200, Y_GND + 320), (rx(3), Y_GND)],
     C["gnd"], 6.5)
plug(gx, gy, C["gnd"]); plug(rx(3), Y_GND, C["gnd"])

# ---------------------------------------------------------------- ADD: 5V leg
vx, vy = ux(PWR["5V"]), UNO_BOT
wire([(vx, vy), "C", (vx - 250, vy - 200), (hx(10) + 60, ROWY["G"] + 420),
      (hx(10), ROWY["G"])], "#b8002e", 6.5)
plug(vx, vy, "#b8002e"); plug(hx(10), ROWY["G"], "#b8002e")

# ---------------------------------------------------------------- ADD: 100 k
resistor(hx(10), ROWY["F"], hx(14), ROWY["F"], "100k")
T(hx(14) + 30, ROWY["F"] + 6, "100 k, measured 98.0 k", 15, "#7a5a10",
  "start", "bold", halo=5)

# --------------------------------------------------- ADD: F/M to cathode/anode
wire([(hx(14), ROWY["G"]), "C", (hx(14) + 260, ROWY["G"] + 10), (BB_R + 60, ROWY["G"] - 200),
      (BB_R + 66, BB_Y - 40), "C", (BB_R + 70, DUT_Y + 300),
      (dpx(1) - 120, DUT_HY + 150), (dpx(1), DUT_HY)], C["ret"], 6.5)
plug(hx(14), ROWY["G"], C["ret"])
wire([(rx(28), Y_GND), "C", (rx(28) + 150, Y_GND - 40), (BB_R + 130, Y_GND - 260),
      (BB_R + 134, BB_Y - 90), "C", (BB_R + 140, DUT_Y + 250),
      (dpx(2) - 90, DUT_HY + 190), (dpx(2), DUT_HY)], C["gnd"], 6.5)
plug(rx(28), Y_GND, C["gnd"])
T(rx(28) - 20, Y_GND - 28, "GND rail col 28", 12.5, C["gnd"], "end", halo=5)

# ---------------------------------------------------------------- DMM probes
for col, lab, cc in ((10, "red", "#d81e1e"), (14, "black", "#222")):
    x = hx(col)
    add(f'<line x1="{x:.1f}" y1="{ROWY["J"]:.1f}" x2="{x:.1f}" y2="{BB_Y-56:.1f}" '
        f'stroke="{cc}" stroke-width="5" stroke-linecap="round"/>')
    add(f'<circle cx="{x:.1f}" cy="{ROWY["J"]:.1f}" r="7" fill="{cc}"/>')
    T(x, BB_Y - 66, lab, 13.5, cc, weight="bold")
T((hx(10) + hx(14)) / 2, BB_Y - 96, "DMM probes in J10 and J14", 16, "#111", weight="bold")

# =================================================================== panels
LX, LY, LW = 1010.0, 380.0, DUT_W
add(f'<rect x="{LX}" y="{LY}" width="{LW:.1f}" height="300" rx="12" fill="#fff" '
    f'stroke="#e2ded2" stroke-width="2"/>')
T(LX + 24, LY + 38, "the rewire, in five moves", 19, "#111", "start", "bold")
STEPS = [("#d81e1e", "PULL the six jumpers off UNO D2-D7. Bank is dead."),
         ("#b8002e", "ADD a jumper: UNO 5V  ->  G10."),
         ("#7a5a10", "ADD the 100 k across the top half: F10 to F14."),
         (C["ret"],  "MOVE F/M #1 to G14, out to the die CATHODE."),
         (C["gnd"],  "MOVE F/M #2 to GND rail col 28, out to the ANODE.")]
for i, (col, s2) in enumerate(STEPS):
    y = LY + 78 + i * 40
    add(f'<circle cx="{LX+38}" cy="{y-5}" r="11" fill="{col}"/>')
    T(LX + 38, y, str(i + 1), 13, "#fff", "middle", "bold")
    T(LX + 60, y, s2, 14.5, "#222", "start")

NX, NY = LX, LY + 320
add(f'<rect x="{NX}" y="{NY}" width="{LW:.1f}" height="250" rx="12" fill="#fff9ec" '
    f'stroke="#ecdcae" stroke-width="2"/>')
T(NX + 24, NY + 38, "reading it", 19, "#111", "start", "bold")
NOTES = ["DMM: 2 clicks clockwise from OFF (DC volts), then RANGE",
         "down to mV. Red probe on the 5V side of the 100 k.",
         "Wait 5 seconds to settle, then read the millivolts.",
         "",
         "i_leak = V_mV / 98.0 k   ->   1 uA reads 98 mV",
         "",
         "Red on every die. Green and blue only where round 1",
         "flagged something."]
for i, n in enumerate(NOTES):
    T(NX + 26, NY + 74 + i * 22, n, 14.5, "#3a3a3a", "start")

SX, SY = 1010.0, NY + 270
add(f'<rect x="{SX}" y="{SY}" width="{LW:.1f}" height="300" rx="12" fill="#fff" '
    f'stroke="#e2ded2" stroke-width="2"/>')
T(SX + 24, SY + 36, "the circuit", 19, "#111", "start", "bold")
def sl(pts, col="#222", w=2.6):
    d = f'M {pts[0][0]:.1f} {pts[0][1]:.1f}' + "".join(f' L {p[0]:.1f} {p[1]:.1f}' for p in pts[1:])
    add(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>')
ay = SY + 130
T(SX + 34, ay + 5, "UNO 5V", 15, "#b8002e", "start", "bold")
sl([(SX + 116, ay), (SX + 178, ay)], "#b8002e", 3)
seg = 70 / 6
pts = [(SX + 178, ay)]
for i in range(6):
    pts.append((SX + 178 + (i + 0.5) * seg, ay + (9 if i % 2 == 0 else -9)))
pts.append((SX + 248, ay)); sl(pts)
T(SX + 213, ay + 32, "100 k", 14, "#7a5a10", weight="bold")
sl([(SX + 248, ay), (SX + 350, ay)], "#b8002e", 3)
add(f'<path d="M {SX+350:.1f} {ay-16:.1f} L {SX+350:.1f} {ay+16:.1f} L {SX+382:.1f} {ay:.1f} Z" '
    f'fill="#ffd166" stroke="#222" stroke-width="2"/>')
sl([(SX + 350, ay - 18), (SX + 350, ay + 18)], "#222", 3.4)
T(SX + 366, ay + 46, "die, REVERSED", 13.5, "#333", weight="bold")
T(SX + 366, ay + 64, "cathode on the left, bar side", 12.5, "#666")
sl([(SX + 382, ay), (SX + 480, ay)], C["gnd"], 3)
sl([(SX + 480, ay), (SX + 480, ay + 20)], C["gnd"], 3)
for i, hw in enumerate((13, 8, 4)):
    sl([(SX + 480 - hw, ay + 20 + i * 6), (SX + 480 + hw, ay + 20 + i * 6)], "#222", 2.6)
T(SX + 502, ay + 26, "UNO GND", 14, C["gnd"], "start", "bold")
sl([(SX + 178, ay - 50), (SX + 178, ay - 10)], "#888", 2)
sl([(SX + 248, ay - 50), (SX + 248, ay - 10)], "#888", 2)
sl([(SX + 178, ay - 50), (SX + 248, ay - 50)], "#888", 2)
T(SX + 213, ay - 58, "DMM, mV", 13.5, "#111", weight="bold")
T(SX + 24, SY + 250, "5 V reverse across the die. Never exceed that.", 14.5, "#8a5a00",
  "start", "bold")
T(SX + 24, SY + 274, "Contact resistance is irrelevant here: nanoamps through 98 k.",
  13.5, "#666", "start")

add('</svg>')
open(OUT + "leakage.svg", "w").write("\n".join(o))
print("ok")
