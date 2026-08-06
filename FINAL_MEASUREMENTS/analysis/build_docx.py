#!/usr/bin/env python3
"""Build the electrical characterization section from the round 1 and round 2 data.

The original .docx supplies styles only; the body is written fresh so the section reports
what was measured rather than what was originally planned.
"""
import csv, math, os
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIG  = os.path.join(ROOT, "FINAL_MEASUREMENTS", "analysis", "figures")
OUT  = os.path.join(ROOT, "deliverable")
os.makedirs(OUT, exist_ok=True)

fits = list(csv.DictReader(open(os.path.join(ROOT, "FINAL_MEASUREMENTS",
                                             "analysis", "fit_results.csv"))))
r1 = [r for r in csv.DictReader(open(os.path.join(ROOT, "RESULTS", "R1_channels.csv")))
      if r["die"].startswith("D") and not r["die"].startswith("DC")]

MODES = ["pass", "suspect", "cross_lit", "open", "short", "die_detached"]
LABEL = {"suspect": "suspect", "cross_lit": "cross-lit", "open": "open",
         "short": "short", "die_detached": "detached"}
N = {s: {m: 0 for m in MODES} for s in range(1, 9)}
for r in r1:
    N[int(r["sample"])][r["verdict"]] += 1
tot = {s: sum(N[s].values()) for s in N}
ok  = {s: N[s]["pass"] for s in N}

red = [f for f in fits if f["colour"] == "R" and f["physical"] == "1"]
bys = {}
for f in red:
    bys.setdefault(int(f["sample"]), []).append(f)

def mean(v): return sum(v) / len(v)
def sd(v):
    return math.sqrt(sum((x - mean(v))**2 for x in v) / (len(v) - 1)) if len(v) > 1 else None
def fmt(m, s, dp=2):
    return f"{m:.{dp}f} ± {s:.{dp}f}" if s is not None else f"{m:.{dp}f}"

SEAT_SD = 0.843
VERDICT = {1: "under-bonded", 2: "under-bonded", 3: "over-bonded", 4: "over-bonded",
           5: "in window", 6: "under-bonded", 7: "in window", 8: "over-bonded"}

doc = Document(os.path.join(ROOT, "Electrical_Characterization_section.docx"))
body = doc.element.body
for child in list(body):
    if not child.tag.endswith("}sectPr"):
        body.remove(child)

def P(text="", style=None, italic=False, size=None, align=None, bold=False):
    p = doc.add_paragraph(style=style)
    r = p.add_run(text)
    r.italic, r.bold = italic, bold
    if size: r.font.size = Pt(size)
    if align is not None: p.alignment = align
    return p

def caption(text):
    return P(text, italic=True, size=8.5, align=WD_ALIGN_PARAGRAPH.CENTER)

def figure(name, cap, w=8.6):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(os.path.join(FIG, name), width=Cm(w))
    caption(cap)

def table(hdr, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(hdr)); t.style = "Table Grid"
    for i, h in enumerate(hdr):
        c = t.rows[0].cells[i]; c.text = ""
        r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(8)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            cells[i].paragraphs[0].add_run(str(v)).font.size = Pt(8)
    if widths:
        for r_ in t.rows:
            for i, w in enumerate(widths): r_.cells[i].width = Cm(w)
    return t

P("Electrical characterization", style="Heading 1")
P("Each populated coupon was characterized electrically to establish which assembly condition "
  "produces the better bond. Two rounds were run. The first screened every addressable channel "
  "with a handheld DMM to classify it as working or failed and to record how it failed. The "
  "second swept current through each surviving channel and fitted the diode equation to "
  "extract series resistance, which contains the bond. The screening separates the eight "
  "conditions clearly. The series resistance does not, and Section D shows why.")

caption("Table I. Measurement setup.")
table(["Quantity", "Test structure", "Instrument", "Excitation"],
      [["Channel state and failure mode", "D1–D8 gold probe pads",
        "Handheld DMM, diode test", "≈1 mA forward"],
       ["Forward voltage, series resistance", "D1–D8, south 32-pin header",
        "Arduino UNO R3, six-branch binary current source, 14-bit oversampled ADC",
        "Pulsed DC, 63 levels, 0.5–15.9 mA, 5 ms on / 250 ms off"],
       ["Sense-resistor calibration", "R_EIS_LOAD, 100 Ω 0.1 %",
        "Handheld DMM, 600 Ω range, REL", "DC"],
       ["Substrate temperature", "NTC pads TH1–TH4", "Handheld DMM, resistance", "DC"]],
      widths=[3.6, 3.6, 5.2, 4.6])

P("A.  Channel screening and yield", style="Heading 2")
P("All 120 addressable channels on the five coupons were probed at the gold pads with a DMM "
  "diode test. A channel passes if it shows a forward junction voltage and lights. Failures "
  "were classified as open (no conduction), short (junction voltage below 0.15 V), cross-lit "
  "(driving one colour lights another, which indicates a bridge between cathodes), detached "
  "(the die is physically absent), or suspect.")
P("Yield separates the conditions. A chi-square test on the 120 channels gives p = 2.2 × 10⁻⁴. "
  "Conditions 5 and 7 lost no channels at all; condition 3 lost 9 of 12.")
figure("fig2_defect_map.png",
       "Fig. 1. Channel-level screening result. Three rows per condition (red, green, blue), "
       "one column per die position. Blank cells are die positions the condition does not own.")
figure("fig3_yield_modes.png",
       "Fig. 2. Yield and failure mode by condition. Error bars are 95 % Wilson intervals on "
       "the pass fraction; counts above each bar are passing channels over total.")
caption("Table II. Channel yield and failure mode by assembly condition.")
table(["Condition", "Pass / total", "Yield (%)", "Failure modes", "Interpretation"],
      [[s, f"{ok[s]} / {tot[s]}", f"{100*ok[s]/tot[s]:.1f}",
        ", ".join(f"{LABEL[m]} {N[s][m]}" for m in MODES[1:] if N[s][m]) or "none",
        VERDICT[s]] for s in range(1, 9)],
      widths=[2.0, 2.4, 2.0, 5.6, 3.0])
P("The failure mode carries more information than the yield number. Conditions 3, 4 and 8 fail "
  "through shorts and cross-lit pairs, which is what excess solder and pad-to-pad bridging "
  "produce. Conditions 1, 2 and 6 fail the other way, through detached dice and open cathodes, "
  "which is the signature of insufficient wetting or a weak joint. Conditions 5 and 7 show "
  "neither. On this evidence 5 and 7 sit inside the process window and the other six sit on "
  "one side of it or the other.")

P("B.  Forward characteristics and series resistance", style="Heading 2")
P("Each surviving channel was swept over 63 current levels between 0.5 and 15.9 mA. Current "
  "comes from six binary-weighted resistors on digital pins, giving 2⁶−1 distinct levels, and "
  "is pulsed 5 ms on and 250 ms off so every point carries the same thermal history. Series "
  "resistance follows from a three-parameter least-squares fit over all points above 0.5 mA:")
P("V(I) = V₀ + n·V_T·ln(I) + I·R_s", align=WD_ALIGN_PARAGRAPH.CENTER, italic=True)
P("R_s is the sum of the die's internal resistance, both bonds, and the board traces inside "
  "the sense loop. All dice come from one reel, so a shift in mean R_s between conditions "
  "would indicate a shift in bond resistance.")
figure("fig1_iv_curves.png",
       "Fig. 3. Forward characteristics of one die (S1 D1) in all three colours. Red reaches "
       "13.9 mA; green and blue stop near 10 mA because the 5 V rail leaves less headroom.")
P("Only the red channels give physical fits. Green and blue return ideality factors between "
  "3.2 and 4.0, which no LED has. At a forward voltage near 2.8 V the 5 V supply allows only a "
  "20-fold current range, over which V₀, n and R_s trade off against one another and the fit "
  "becomes degenerate. Red spans 30-fold and returns ideality 1.60 to 2.06. Everything below "
  "is red only.")
caption("Table III. Red-channel forward voltage and series resistance by condition. "
        "Uncertainties are the standard deviation across channels.")
rows = []
for s in sorted(bys):
    v  = [float(f["Rs"]) for f in bys[s]]
    vf = [float(f["vf10"]) for f in bys[s]]
    nn = [float(f["nid"]) for f in bys[s]]
    rows.append([s, len(v), fmt(mean(vf), sd(vf), 4), fmt(mean(v), sd(v)),
                 f"{min(nn):.2f}–{max(nn):.2f}"])
table(["Condition", "Channels n", "V_F at 10 mA (V)", "R_s (Ω)", "Ideality n"], rows,
      widths=[2.4, 2.4, 4.2, 4.0, 3.0])
allRs = [float(f["Rs"]) for f in red]; allVf = [float(f["vf10"]) for f in red]
P(f"Across {len(red)} red channels the mean series resistance is {mean(allRs):.2f} Ω with a "
  f"standard deviation of {sd(allRs):.2f} Ω. One-way ANOVA across the eight conditions gives "
  f"F(7,21) = 1.73, p = 0.16. Forward voltage at 10 mA behaves the same way: "
  f"{mean(allVf):.4f} V mean, {sd(allVf)*1000:.1f} mV standard deviation, p = 0.24. Neither "
  f"quantity separates the assembly conditions.")
figure("fig4_rs_by_condition.png",
       "Fig. 4. Series resistance by condition. Points are individual channels, squares are "
       "condition means, bars are ±1 standard deviation. The shaded band is the measurement "
       "repeatability established in Section D.")
figure("fig6_vf_by_condition.png",
       "Fig. 5. Forward voltage at 10 mA by condition. The full spread across all 29 channels "
       "is 13 mV, which is consistent with dice drawn from one reel.")

P("C.  Defect detection from the sweep", style="Heading 2")
P("One channel, S3 D1 red, fits to an ideality of 13.0 and a negative series resistance. "
  "Neither is physical. Below 3 mA its junction sits at 1.21 V, under a red LED's turn-on, "
  "while 0.42 mA still flows, so a parallel path of roughly 2.9 kΩ carries the current around "
  "the die. Above 3 mA the curve is indistinguishable from a healthy channel. A diode test at "
  "1 mA reads 1.781 V and passes it, because at that current the shunt takes only a third of "
  "the current.")
P("This makes the ideality factor a usable screen. Any fit outside 1.2 to 2.4 has something "
  "conducting in parallel with the junction, however normal the curve looks at working "
  "current. All 29 usable red channels fell inside that range; the one that did not sits on "
  "the coupon the screening had already flagged for solder contamination.")
figure("fig7_shunt_detection.png",
       "Fig. 6. A contaminated die (S3 D1) against a healthy one. The curves agree above 3 mA "
       "and diverge by 540 mV at the bottom of the sweep.")

P("D.  Measurement repeatability and detection limit", style="Heading 2")
P("The series-resistance comparison is limited by the fixture, not by the dice. This build "
  "takes both voltage taps from the breadboard rather than from the Tier-1 probe pads, so the "
  "two female-male jumpers and their header contacts fall inside the measured loop.")
P("Three channels were measured three times each, unplugging and re-seating the same two "
  f"jumpers between measurements and changing nothing else. The pooled standard deviation is "
  f"{SEAT_SD:.2f} Ω, against a within-condition standard deviation of 0.92 Ω. Re-seating "
  f"therefore accounts for about 85 % of the variance that would otherwise be read as "
  f"die-to-die spread.")
figure("fig5_reseat_repeatability.png",
       "Fig. 7. Three channels, each measured after three independent re-seatings of the two "
       "jumpers. Nothing else changed between points.")
P("Every re-seating lands at or above that channel's minimum, since contact resistance can "
  "only add. Taking the minimum of each channel gives 10.32, 10.42 and 10.98 Ω, so the true "
  "red series resistance is near 10.6 Ω and about 0.85 Ω of the reported mean is wiring.")
P("Bond resistances are 10 to 100 mΩ. At n = 4 the smallest difference in mean R_s this "
  "arrangement can resolve is 1.4 Ω, more than an order of magnitude above the effect. The "
  "null result in Section B is therefore a statement about the instrument, not about the "
  "bonds. Moving the sense connections to the Tier-1 probe pads would put the jumper contacts "
  "outside the measured loop and recover the method.")

P("E.  Self-heating", style="Heading 2")
P("The die dissipates 28.4 mW at 13.9 mA. Junction heating lowers the forward voltage at high "
  "current, flattens the I–V curve and biases R_s downwards, so the pulse length has to be "
  "chosen rather than assumed. One channel was swept three times with only the integration "
  "length changed, giving current-on times of 5, 20 and 80 ms per point.")
figure("fig8_self_heating.png",
       "Fig. 8. Extracted series resistance against current-on time, same channel throughout. "
       "Error bars are the standard error of the fit.")
P("Between 5 and 20 ms the result is unchanged within the fit error. At 80 ms it falls by "
  "1.49 Ω. For a junction-to-board thermal resistance of order 200 K/W, 28.4 mW gives about "
  "6 K of rise, and at −2 mV/K that appears as roughly −1.2 Ω of apparent series resistance, "
  "matching the measurement to within 25 %. The package thermal time constant therefore lies "
  "between 20 and 80 ms. All campaign data was taken at 5 ms.")

P("F.  Summary", style="Heading 2")
caption("Table IV. Summary across assembly conditions.")
rows = []
for s in range(1, 9):
    v  = [float(f["Rs"]) for f in bys.get(s, [])]
    vf = [float(f["vf10"]) for f in bys.get(s, [])]
    rows.append([s, f"{100*ok[s]/tot[s]:.1f}",
                 ", ".join(f"{LABEL[m]} {N[s][m]}" for m in MODES[1:] if N[s][m]) or "none",
                 f"{mean(vf):.3f}" if vf else "—",
                 f"{mean(v):.2f}" if v else "—", VERDICT[s]])
table(["Condition", "Yield (%)", "Failure modes", "V_F at 10 mA (V)", "R_s (Ω)", "Assessment"],
      rows, widths=[1.9, 1.9, 4.8, 2.9, 2.2, 2.6])
P("Two results stand. Channel yield and failure mode separate the eight conditions at "
  "p = 2.2 × 10⁻⁴ and place conditions 5 and 7 ahead of the rest, with no failures in 12 "
  "channels each. Series resistance does not separate them, and the reason is measured rather "
  "than assumed: fixture repeatability of 0.84 Ω exceeds the bond resistances by more than an "
  "order of magnitude.")
P("The failure modes give a direction as well as a ranking. Conditions 1, 2 and 6 lose "
  "channels to detachment and opens, so they are under-bonded. Conditions 3, 4 and 8 lose them "
  "to shorts and bridges, so they are over-bonded. Conditions 5 and 7 lose none. A follow-up "
  "should sense at the Tier-1 probe pads to make series resistance usable, and should measure "
  "reverse leakage, which is insensitive to contact resistance and would quantify the shunt "
  "found in Section C.")
P("Not measured: TLM ladders, van der Pauw cloverleaves and impedance spectroscopy, all of "
  "which need a four-wire source-measure unit or an LCR meter. The DCL6 and DCL12 daisy chains "
  "read open on every coupon because the chain routes each die's top-left pad to its top-right "
  "pad; with the dice rotated 90° those are the red and blue cathodes, so every element is a "
  "pair of back-to-back diodes and the anode is left floating. That is a layout fault in this "
  "coupon revision, not a bonding failure.", size=9, italic=True)

doc.save(os.path.join(OUT, "Electrical_Characterization_section.docx"))
print("written:", OUT)
