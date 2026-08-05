#!/usr/bin/env python3
"""Close-up of the RETURN cluster and the two bottom rails."""
import math

OUT = ("/tmp/claude-1000/-home-danieltyukov-workspace-tud-tud-micro-led-bonding-"
       "categorization/27a8d42d-6fd7-4431-9aeb-8e458955a7fc/scratchpad/rig/")

P = 52.0                       # 2x the main drawing
C = dict(force="#d81e1e", ret="#f08c00", gnd="#242424", a0="#0e9c52", a1="#8e3fbe",
         a2="#c2185b", a3="#00acc1", dig="#2f6fd0", board="#f4f1e7", edge="#d2ccb9", hole="#333",
         txt="#181818", faint="#8f8a7c")
BAND = dict(blk="#171717", brn="#7a4a16", red="#cf2020", gld="#c9a227")

BX, BY = 130.0, 168.0
BW, BH = 730.0, 592.0
def cx(c): return 210.0 + (c - 2) * P
ROWY = {r: 232.0 + i * P for i, r in enumerate("EDCBA")}
Y_GND = ROWY["A"] + 2.8 * P
Y_FORCE = Y_GND + P

RAILCOLS = [c for c in range(3, 14) if (c - 3) % 6 < 5]
RAILX = [cx(c) for c in RAILCOLS]
def rx(c):
    assert c in RAILCOLS, f"column {c} is a gap in the rail"
    return cx(c)

o = []
def add(s): o.append(s)
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def T(x, y, s, size=15, fill=None, anchor="middle", weight="normal", halo=0, op=1.0):
    hl = (f' stroke="#fbfaf6" stroke-width="{halo}" paint-order="stroke" '
          f'stroke-linejoin="round"') if halo else ""
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" '
        f'fill="{fill or C["txt"]}" text-anchor="{anchor}" opacity="{op}"{hl}>{esc(s)}</text>')

def hole(x, y, s=17.0):
    add(f'<rect x="{x-s/2:.1f}" y="{y-s/2:.1f}" width="{s}" height="{s}" rx="3" '
        f'fill="{C["hole"]}"/><rect x="{x-s/2+3:.1f}" y="{y-s/2+3:.1f}" '
        f'width="{s-6}" height="{s-6}" rx="2" fill="#0c0c0c"/>')

def leg(x1, y1, x2, y2):
    add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#a3a3a3" '
        f'stroke-width="6" stroke-linecap="round"/>')

def resistor(x1, y1, x2, y2, bands):
    L = math.hypot(x2 - x1, y2 - y1)
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    body = min(132.0, max(84.0, L - 56))
    cxm, cym = (x1 + x2) / 2, (y1 + y2) / 2
    leg(x1, y1, x2, y2)
    add(f'<g transform="translate({cxm:.1f},{cym:.1f}) rotate({ang:.1f})">'
        f'<rect x="{-body/2:.1f}" y="-22" width="{body:.1f}" height="44" rx="15" '
        f'fill="#e7d3af" stroke="#ac9066" stroke-width="2.5"/>')
    step = body / 5.6
    for i, b in enumerate(bands):
        bx = -body / 2 + step * 0.8 + i * step if i < 3 else body / 2 - step * 0.75
        add(f'<rect x="{bx-6:.1f}" y="-22" width="12" height="44" fill="{BAND[b]}"/>')
    add('</g>')

def cap(x1, y1, x2, y2):
    cxm, cym = (x1 + x2) / 2, (y1 + y2) / 2
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    leg(x1, y1, x2, y2)
    add(f'<g transform="translate({cxm:.1f},{cym:.1f}) rotate({ang:.1f})">'
        f'<ellipse rx="34" ry="27" fill="#2f6fd0" stroke="#1c4a92" stroke-width="2.5"/>'
        f'<ellipse cx="-9" cy="-8" rx="13" ry="8" fill="#74a8ec" opacity="0.6"/></g>')

def plug(x, y, col):
    add(f'<rect x="{x-12:.1f}" y="{y-12:.1f}" width="24" height="24" rx="4.5" '
        f'fill="{col}" stroke="#00000077" stroke-width="2"/>')

def wire(pts, col, w=13.0):
    d = f'M {pts[0][0]:.1f} {pts[0][1]:.1f}'
    i = 1
    while i < len(pts):
        if pts[i] == "C":
            a, b, c2 = pts[i+1], pts[i+2], pts[i+3]
            d += f' C {a[0]:.1f} {a[1]:.1f} {b[0]:.1f} {b[1]:.1f} {c2[0]:.1f} {c2[1]:.1f}'
            i += 4
        else:
            d += f' L {pts[i][0]:.1f} {pts[i][1]:.1f}'; i += 1
    add(f'<path d="{d}" fill="none" stroke="#00000055" stroke-width="{w+5}" '
        f'stroke-linecap="round" stroke-linejoin="round"/>')
    add(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" '
        f'stroke-linecap="round" stroke-linejoin="round"/>')

def tagbox(x, y, s, col, size=15, anchor="middle"):
    w = len(s) * size * 0.60 + 20
    x0 = x - w / 2 if anchor == "middle" else (x if anchor == "start" else x - w)
    add(f'<rect x="{x0:.1f}" y="{y-size*0.95:.1f}" width="{w:.1f}" '
        f'height="{size*1.75:.1f}" rx="7" fill="#ffffffee" stroke="{col}" stroke-width="2"/>')
    T(x0 + w / 2, y + size * 0.42, s, size, col, "middle", "bold")

# ===================================================================== canvas
W, H = 1520, 890
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}" font-family="DejaVu Sans, Helvetica, Arial, sans-serif">')
add(f'<rect width="{W}" height="{H}" fill="#fbfaf6"/>')
T(56, 52, "Close-up: the RETURN cluster and the two rails", 29, "#111", "start", "bold")
T(56, 82, "Columns 2 to 13 at twice the size. This is the part that was crowded.",
  16.5, "#5a5a5a", "start")

add(f'<rect x="{BX}" y="{BY}" width="{BW}" height="{BH}" rx="14" fill="{C["board"]}" '
    f'stroke="{C["edge"]}" stroke-width="3"/>')
for c in (4, 8):
    add(f'<rect x="{cx(c)-25:.1f}" y="{ROWY["E"]-32:.1f}" width="50" '
        f'height="{ROWY["A"]-ROWY["E"]+64:.1f}" rx="25" fill="{C["ret"]}" opacity="0.17"/>')
add(f'<rect x="{cx(4)-25:.1f}" y="{ROWY["E"]-17:.1f}" width="{cx(8)-cx(4)+50:.1f}" '
    f'height="34" rx="17" fill="{C["ret"]}" opacity="0.17"/>')
add(f'<rect x="{BX+16:.1f}" y="{Y_GND-25:.1f}" width="{BW-32:.1f}" height="50" rx="25" '
    f'fill="{C["gnd"]}" opacity="0.10"/>')
add(f'<rect x="{BX+16:.1f}" y="{Y_FORCE-25:.1f}" width="{BW-32:.1f}" height="50" rx="25" '
    f'fill="{C["force"]}" opacity="0.13"/>')
add(f'<line x1="{BX+22}" y1="{Y_FORCE+36:.1f}" x2="{BX+BW-22}" y2="{Y_FORCE+36:.1f}" '
    f'stroke="#d63b3b" stroke-width="4"/>')
add(f'<line x1="{BX+22}" y1="{Y_GND-36:.1f}" x2="{BX+BW-22}" y2="{Y_GND-36:.1f}" '
    f'stroke="#3a63c0" stroke-width="4"/>')
for c in range(2, 14):
    for r in "EDCBA":
        hole(cx(c), ROWY[r])
    T(cx(c), ROWY["E"] - 44, str(c), 15, C["faint"])
for x in RAILX:
    hole(x, Y_GND); hole(x, Y_FORCE)
for r in "EDCBA":
    T(BX + 32, ROWY[r] + 6, r, 16, C["faint"])
T(BX - 16, Y_GND + 6, "GND", 18, C["gnd"], "end", "bold")
T(BX - 16, Y_FORCE + 6, "FORCE", 18, C["force"], "end", "bold")

cap(cx(4), ROWY["A"], rx(5), Y_GND)
cap(cx(8), ROWY["A"], rx(9), Y_GND)
resistor(cx(8), ROWY["B"], rx(11), Y_GND, ["brn", "blk", "brn", "gld"])
cap(rx(11), Y_FORCE, rx(13), Y_GND)

wire([(cx(4), ROWY["E"]), (cx(8), ROWY["E"])], C["ret"])
plug(cx(4), ROWY["E"], C["ret"]); plug(cx(8), ROWY["E"], C["ret"])

# ---- female-male jumper leaves the top
wire([(cx(4), ROWY["C"]), "C", (cx(4) - 70, ROWY["C"] - 20), (BX + 60, 300), (150, 126)],
     C["ret"])
plug(cx(4), ROWY["C"], C["ret"])
tagbox(214, 108, "F/M out to the die cathode", C["ret"], 15)

# ---- four wires leave the bottom, bowed clear of their own column's holes
BOT = 812.0
LANES = (
    (rx(3), Y_GND,      (232, 700), (176, 756), 148.0, C["gnd"], "UNO GND"),
    (cx(4), ROWY["D"],  (275, 350), (280, 620), 288.0, C["a0"],  "A0"),
    (rx(6), Y_FORCE,    (416, 720), (404, 772), 400.0, C["a1"],  "A1"),
    (cx(8), ROWY["D"],  (480, 400), (516, 580), 522.0, C["a2"],  "A2"),
    (rx(10), Y_GND,     (700, 700), (660, 760), 640.0, C["a3"],  "A3"),
)
for x0, y0, c1, c2, ex, col, lab in LANES:
    wire([(x0, y0), "C", c1, c2, (ex, BOT)], col)
    plug(x0, y0, col)
    tagbox(ex, 848, lab, col, 15)
T(720, 853, "all five run down to the UNO", 16, "#5a5a5a", "start")

for c, r, s2 in ((4, "C", "C4"), (4, "D", "D4"), (4, "E", "E4"), (4, "A", "A4"),
                 (8, "D", "D8"), (8, "E", "E8"), (8, "A", "A8"), (8, "B", "B8")):
    T(cx(c) - 30, ROWY[r] + 6, s2, 15, "#5a5a5a", "end", "bold", halo=5)
add(f'<path d="M {cx(8)+40:.1f} {ROWY["E"]+4:.1f} L {cx(9)+30:.1f} '
    f'{ROWY["D"]-8:.1f}" stroke="{C["ret"]}" stroke-width="2.5" fill="none"/>')
T(cx(9) + 36, ROWY["D"] + 6, "the link jumper", 16, C["ret"], "start", "bold", halo=6)
T(cx(4) + 54, (ROWY["A"] + Y_GND) / 2 + 20, "C2", 16, "#1c4a92", "start", "bold", halo=6)
T(cx(8) + 60, (ROWY["A"] + Y_GND) / 2 + 20, "C3", 16, "#1c4a92", "start", "bold", halo=6)
T(rx(11) - 40, Y_GND + 48, "C1", 16, "#1c4a92", "middle", "bold", halo=6)
T(rx(11) + 46, ROWY["B"] - 20, "100 R sense", 16, "#7a5a10", "middle", "bold", halo=6)

# =================================================================== notes
NXX = 980.0
def note(y, col, head, body_lines):
    add(f'<rect x="{NXX}" y="{y}" width="480" height="4" rx="2" fill="{col}"/>')
    T(NXX, y + 34, head, 17, "#111", "start", "bold")
    for i, line in enumerate(body_lines):
        T(NXX, y + 62 + i * 25, line, 15.5, "#3a3a3a", "start")

note(150, C["ret"], "The orange shading is one single node",
     ["Holes A-E of one column are already joined inside",
      "the board. The link jumper joins column 4 to column",
      "8, so all ten of those holes are RETURN. Anything",
      "you plug into any of them is on the same node."])
note(320, C["ret"], "Three things there, three different jobs",
     ["C4  -  female-male jumper, leaves the board for the",
      "cathode pin of the channel under test",
      "E4 to E8  -  the link, lies flat on the board",
      "D8  -  goes to UNO A2, drawn pink so it cannot be",
      "confused with the two orange ones"])
note(510, C["gnd"], "How the rail holes are laid out",
     ["First rail hole is under column 3, then five in a row,",
      "a one-hole gap, five more, and so on. They line up",
      "with the numbered columns. The whole strip is one",
      "node, so the exact hole never changes the circuit."])
note(680, C["force"], "What ends up on each rail",
     ["A3 taps the GND rail in the SAME five-hole group as the",
      "100 R, so i = (A2 - A3) / R_SENSE is a true difference",
      "GND rail  -  UNO GND, A3, C1, C2, C3, the 100 R",
      "FORCE rail  -  UNO A1, C1, the six bank resistors,",
      "and the female-male jumper to the die anode"])

add('</svg>')
open(OUT + "closeup.svg", "w").write("\n".join(o))
print("ok")
