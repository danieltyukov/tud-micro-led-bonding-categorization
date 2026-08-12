# Method references and notes on the draft

For "Contactless Die Attach Methods Via Solder Paste", section on electrical
characterization. Prepared 12 August 2026 at A. Abdelwahab's request.

Fourteen references, one per method actually used in the measurements. Each was checked
against the publisher record, and each is tied below to the sentence in the draft it
supports. Numbered `[R1]`-`[R14]` so the numbering cannot collide with the citations
already in the article.

---

## 1. Reference list, IEEE style

```
[R1]  F. M. Smits, "Measurement of sheet resistivities with the four-point probe,"
      Bell Syst. Tech. J., vol. 37, no. 3, pp. 711-718, May 1958,
      doi: 10.1002/j.1538-7305.1958.tb03883.x.

[R2]  Test Method for Measuring Resistivity of Silicon Wafers with an In-Line
      Four-Point Probe, SEMI MF84, SEMI, Milpitas, CA, USA.

[R3]  D. K. Schroder, Semiconductor Material and Device Characterization, 3rd ed.
      Hoboken, NJ, USA: Wiley-IEEE Press, 2006, doi: 10.1002/0471749095.

[R4]  Performance Test Methods and Qualification Requirements for Surface Mount
      Solder Attachments, IPC-9701A, IPC, Bannockburn, IL, USA, Feb. 2006.

[R5]  E. F. Schubert, Light-Emitting Diodes, 2nd ed. Cambridge, U.K.: Cambridge
      Univ. Press, 2006, doi: 10.1017/CBO9780511790546.

[R6]  D. C. Montgomery, Design and Analysis of Experiments, 9th ed. Hoboken, NJ,
      USA: Wiley, 2017.

[R7]  E. B. Wilson, "Probable inference, the law of succession, and statistical
      inference," J. Amer. Statist. Assoc., vol. 22, no. 158, pp. 209-212,
      Jun. 1927, doi: 10.1080/01621459.1927.10502953.

[R8]  A. Agresti and B. A. Coull, "Approximate is better than 'exact' for interval
      estimation of binomial proportions," Amer. Statistician, vol. 52, no. 2,
      pp. 119-126, May 1998, doi: 10.1080/00031305.1998.10480550.

[R9]  Integrated Circuit Thermal Measurement Method - Electrical Test Method
      (Single Semiconductor Device), JESD51-1, JEDEC Solid State Technology
      Association, Arlington, VA, USA, Dec. 1995.

[R10] Implementation of the Electrical Test Method for the Measurement of Real
      Thermal Resistance and Impedance of Light-Emitting Diodes with Exposed
      Cooling Surface, JESD51-51, JEDEC Solid State Technology Association,
      Arlington, VA, USA, Apr. 2012.

[R11] S. K. Cheung and N. W. Cheung, "Extraction of Schottky diode parameters from
      forward current-voltage characteristics," Appl. Phys. Lett., vol. 49, no. 2,
      pp. 85-87, Jul. 1986, doi: 10.1063/1.97359.

[R12] J. H. Werner, "Schottky barrier and pn-junction I/V plots - small signal
      evaluation," Appl. Phys. A, vol. 47, no. 3, pp. 291-300, 1988,
      doi: 10.1007/BF00615935.

[R13] J. M. Shah, Y.-L. Li, Th. Gessmann, and E. F. Schubert, "Experimental
      analysis and theoretical model for anomalously high ideality factors
      (n >> 2.0) in AlGaN/GaN p-n junction diodes," J. Appl. Phys., vol. 94,
      no. 4, pp. 2627-2630, Aug. 2003, doi: 10.1063/1.1593218.

[R14] M. S. Wong et al., "Quantitative analysis of leakage current in III-nitride
      micro-light-emitting diodes," Appl. Phys. Lett., vol. 126, no. 4, 043506,
      Jan. 2025, doi: 10.1063/5.0250282.
```

BibTeX for all fourteen is in `method_references.bib` in this folder.

---

## 2. Where each one goes

| Sentence in the draft | Cite | Why |
|---|---|---|
| "The sheet resistance of the 4-inch Au-coated wafer was measured using a CDE ResMap 178 multiprobe station" | [R1], [R2], [R3] | [R1] is the source of the geometric correction factors any four-point probe applies; [R2] is the standardised procedure; [R3] Ch. 1 is the textbook treatment |
| "the DC test structure consisted of a daisy chain incorporating six 1x1 mm2 Au-coated dummy dies" | [R4], [R3] | [R4] is why a daisy chain is the accepted structure for judging surface-mount solder attachments; [R3] Ch. 3 covers the four-terminal measurement of the chain |
| "probed through the gold contact pads using the diode-test mode of a digital multimeter" | [R5] | Forward voltage of an LED and what a junction-voltage reading means |
| "A chi-square test applied to all 120 channels" | [R6] | Chi-square test of independence |
| "Error bars are 95 % Wilson intervals on the pass fraction" (Fig. 5 caption) | [R7], [R8] | [R7] is the interval itself; [R8] is why it is the right choice at n = 12 and at 100 % yield, where the normal approximation degenerates |
| "the current was pulsed for 5 ms followed by an off-time of 250 ms" | [R9], [R10] | The forward-voltage electrical test method and its pulsing requirements; [R10] is the LED-specific form |
| "extracted using a three-parameter nonlinear least-squares fit" | [R11], [R12], [R5] | Standard extraction of ideality and series resistance from a forward sweep |
| "V0, n and Rs were strongly correlated, making the fit poorly identifiable" | [R12] | Werner analyses exactly this degeneracy over a short current range |
| "physically plausible fits were defined by ideality factors between 1.2 and 2.4" | [R13], [R5] | [R13] is the standard reference for what an out-of-range ideality factor in a III-nitride junction indicates |
| "A one-way ANOVA comparing the eight assembly conditions" | [R6] | ANOVA |
| "the smallest difference in mean series resistance detectable by the present setup" | [R6] | Minimum detectable difference / power |
| "a forward-voltage temperature coefficient of approximately -2 mV/K" | [R5], [R10] | The coefficient and the thermal-characterisation framework it comes from |
| "characterized under reverse bias to identify possible conduction paths parallel to the LED junction" | [R14] | Reverse-bias I-V used to separate a parallel leakage path from the junction. Their leakage is intrinsic to the sidewall and ours is assembly-induced, so cite it for the measurement, not the mechanism |

---

## 3. Three numbers in the draft worth fixing

Checked against the raw data in this repository. The conclusions do not change; the
arithmetic does.

### 3.1 The shunt fraction at the diode test: neither one third nor 61 %

Paragraph beginning "One numerical correction:". Two things here.

First, that paragraph is an editorial note written in the first person and it is sitting in
the body of the article. It needs to come out.

Second, the number. The correct figure is **about 44 %**, and the reason both earlier
figures missed it is the test current. This meter is not a 1 mA source. Its diode-mode test
current was measured directly during the round 1 setup: 0.142 V across a 100 Ω 0.1 %
reference resistor, so **1.42 mA** (`RESULTS/R1_meter.csv`, step 1f, cross-checked against
the 1.49 mA short-circuit figure in the instrument review).

At the 1.781 V reading, a 2.87 kΩ shunt carries 0.62 mA. Against 1.42 mA that is 44 %, and
the junction takes the remaining 0.80 mA.

That split is confirmed independently. A healthy die on the same coupon sits at 1.749 V at
0.349 mA. Carrying it up to 0.80 mA through its own fitted ideality gives 1.783 to 1.793 V,
against the 1.781 V actually read. The alternative reading, that the meter is a Thevenin
source of 3.245 V behind about 2.2 kΩ, would put only 0.05 mA through the junction and
predict a reading roughly 150 mV low, so the data rules it out.

Suggested replacement: *"At the 1.781 V reading, the shunt carries 0.62 mA of the meter's
1.42 mA diode-test current, so the junction sees only 0.80 mA and the channel still reads
as a normal red LED."*

### 3.2 The variance share is 85 %, not 83 %

Paragraph on re-seating repeatability, which currently reads "approximately 83 %, or about
85 %". One number, and it is 85 %.

The pooled within-condition standard deviation over the 29 physical red-channel fits is
0.9147 Ω, and the re-seating pooled standard deviation is 0.843 Ω. The variance ratio is
0.843² / 0.9147² = **84.9 %**. The 83 % comes from rounding the re-seating figure to 0.84
before squaring. Rounding both to two decimals in the text is fine, but the quoted
percentage should be computed from the unrounded values.

### 3.3 The self-heating estimate does not reproduce 1.2 Ω

Paragraph on self-heating. The stated inputs are 200 K/W, 28.4 mW and -2 mV/K. Because the
dissipated power is very nearly proportional to current over this range, the thermal
perturbation is linear in current and folds entirely into the fitted series resistance:

```
  ΔR_s ≈ α · R_th · V_F = (2 mV/K)(200 K/W)(2.01 V) = 0.80 Ω
```

not 1.2 Ω. Against the measured 1.49 Ω that is a factor of 1.9, so the claim of agreement
"to within 25 %" does not hold as written.

Two honest ways out, both leaving the conclusion untouched:

- **Invert it.** The measured 1.49 Ω implies R_th ≈ 370 K/W, which is an ordinary value for
  a 0404 package on two-layer FR-4 with no heat-spreading copper. This is the stronger
  version: the measurement yields a thermal resistance rather than being checked against an
  assumed one.
- **Keep the forward estimate** but state R_th ≈ 300 K/W, which gives 1.21 Ω and does agree
  with the measurement to within 20 %.

Either way the finding stands: heating becomes significant between 20 and 80 ms, and every
campaign measurement was taken at 5 ms.

---

## 4. Smaller editorial points

- The equation variables did not survive the paraphrase. "where  is the terminal voltage,
  is the voltage offset,  is the ideality factor" and "Over this limited range , , and
  were strongly correlated" have lost their symbols.
- "a statistically significant association between assembly condition and channel
  p = 2.2 x 10⁻⁴" is missing a word, probably "channel outcome".
- Two cross-references point to "Section D" (in "discussed in Section D" and in the
  failure-mode paragraph). After the renumbering, the repeatability material looks like
  Section E.
- The sheet-resistance sentence gives the effective resistivity, 10 x 10⁻⁸ Ω·m, but not the
  sheet resistance in Ω/sq or the Au thickness. Since ρ = R_sheet · t, giving two of the
  three would let a reader check it. Bulk gold is 2.44 x 10⁻⁸ Ω·m, so the film is about
  four times bulk, which is worth stating explicitly rather than leaving the reader to
  notice it.
