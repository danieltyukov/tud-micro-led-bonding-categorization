# Method references and notes on the draft

For "Contactless Die Attach Methods Via Solder Paste", electrical characterization only.
Prepared 12 August 2026 at A. Abdelwahab's request.

Five references, IEEE only. Each was found on IEEE Xplore through the TU Delft Library
proxy, the metadata was taken from the Xplore record, and the full text was downloaded and
read before being tied to a sentence. PDFs are in `references/`. BibTeX is in
`method_references.bib`.

Five rather than fourteen, because these are the ones that actually carry a claim we make.
Where no IEEE source genuinely supports a method, that is said below rather than papered
over with a citation that does not fit.

---

## 1. Reference list, IEEE style

```
[R1] A. Abdelwahab, H. van Zeijl, R. van Hoorn, H. Kuipers, and M. Mastrangeli,
     "Pick-and-Release: A Novel Contactless Bonding Method for Die Attachment," in
     2025 IEEE 75th Electronic Components and Technology Conference (ECTC),
     May 2025, pp. 2125-2132, doi: 10.1109/ECTC51687.2025.00363.

[R2] M. Zhanghu, Y. Liu, B.-R. Hyun, Y. Li, and Z. Liu, "Optimizing InGaN Micro-LED
     Efficiency: Investigating the Internal Quantum Efficiency and Ideality Factor
     Connection," IEEE Trans. Electron Devices, vol. 71, no. 10, pp. 6190-6197,
     Oct. 2024, doi: 10.1109/TED.2024.3449829.

[R3] E. Jung, J. K. Lee, M. S. Kim, and H. Kim, "Leakage Current Analysis of
     GaN-Based Light-Emitting Diodes Using a Parasitic Diode Model," IEEE Trans.
     Electron Devices, vol. 62, no. 10, pp. 3322-3325, Oct. 2015,
     doi: 10.1109/TED.2015.2468581.

[R4] N. Roccato et al., "Fast Characterization of Power LEDs: Circuit Design and
     Experimental Results," IEEE Trans. Electron Devices, vol. 71, no. 6,
     pp. 3753-3760, Jun. 2024, doi: 10.1109/TED.2024.3393448.

[R5] D. Gacio, J. M. Alonso, J. Garcia, M. S. Perdigao, E. Sousa Saraiva, and
     F. E. Bisogno, "Effects of the Junction Temperature on the Dynamic Resistance
     of White LEDs," IEEE Trans. Ind. Appl., vol. 49, no. 2, pp. 750-760,
     Mar./Apr. 2013, doi: 10.1109/TIA.2013.2243092.
```

---

## 2. Where each one goes, and what it actually says

### [R1] Abdelwahab et al., ECTC 2025

Cite at the daisy-chain sentence and at the sheet-resistance sentence.

This is the method source for both, not a background citation. Its Section E describes the
same structure the new figure measures: a daisy chain bridging six 1 mm x 1 mm dummy dies
on a PCB that also carries van der Pauw and TLM structures and RGB-LED footprints, read on
a Summit 11K/12K probe station, with sheet resistance taken on the CDE ResMap 178
multi-probe station. It reports chain resistances from 0.199 +/- 0.019 ohm (Ag, with
pressure) to 0.380 +/- 0.025 ohm (Au, pressure-less), the same order as the 0.22 to 0.61
ohm in the new eight-condition data.

The new eight-condition data was taken on that same v1 vehicle in a separate session, so
[R1] describes the actual hardware rather than an analogue of it. Because it is the same
board, the same structure and the same instruments, it removes the need to cite a generic
four-point-probe or daisy-chain standard for either sentence.

Worth keeping straight in the text: the daisy-chain data and the LED-coupon data are two
separate experiments on two different boards. Any statement that the two rankings agree is
a statement about assembly conditions, not about two structures measured on one coupon.

### [R2] Zhanghu et al., TED 2024

Cite where the ideality window of 1.2 to 2.4 is defined, and where the anomalous channel is
excluded.

It supplies the physical reading of the number: n = 1 corresponds to band-to-band radiative
recombination, n = 2 to Shockley-Read-Hall recombination through defect levels, and n > 2
to deep-level-assisted tunnelling. That is exactly the reasoning behind treating a fit
outside the window as evidence of an extra conduction path rather than a bad fit. It also
reports an inverse correlation between ideality factor and internal quantum efficiency
across its devices, and observes that leakage paths raise the apparent series resistance,
which is the same coupling we see on S3-D1.

### [R3] Jung et al., TED 2015

Cite where the parallel path across the junction is introduced, in the forward-sweep defect
section and again in the reverse-bias section.

It analyses LED leakage as a parasitic element shunting the main diode and separates the
two by their turn-on voltages, 2.64 V for the main diode against 0.94 V for the parasitic
one. That is the same separation we make when a channel conducts at 1.21 V, well below a
red LED's turn-on.

One caveat to respect in the wording: their shunt is intrinsic to the device, attributed to
hydrogen-related deep levels, while ours is external contamination from the assembly. Cite
it for the model and the diagnostic, not for the mechanism.

### [R4] Roccato et al., TED 2024

Cite at the 5 ms current-on time and in the self-heating section.

Its abstract states the point outright: LED characterization is often carried out with
pulses of 10 ms and longer, conditions in which self-heating can significantly affect the
measurement. Our own result, that nothing shifts between 5 and 20 ms but 80 ms moves the
extracted series resistance, sits exactly on that boundary, so this is corroboration rather
than background.

### [R5] Gacio et al., TIA 2013

Cite at the forward-voltage temperature coefficient and in the self-heating analysis.

It defines the relation we use, V_D = V_D(25 C) + λ(T_j - 25) with λ = ∂V_D/∂T_j, and
measures λ experimentally for four commercial LEDs. More usefully for us, it then measures
how junction temperature shifts the LED's dynamic resistance, which is the exact confound
behind our 80 ms result. It also picks its own pulse width as a trade-off between
signal-to-noise and negligible self-heating, the same argument we make for 5 ms.

---

## 3. What has no IEEE source, and what to do about it

Two things in the section cannot honestly be cited to IEEE.

**The statistics.** The Wilson score interval on the yield bars, the chi-square test of
independence across conditions, and the one-way ANOVA on series resistance are general
statistics with no IEEE home. Three options, in order of preference:

1. State them without citation. They are standard and named explicitly, which is normal
   practice for a packaging paper.
2. Cite the primary sources, which are not IEEE: E. B. Wilson, J. Amer. Statist. Assoc.,
   vol. 22, no. 158, pp. 209-212, 1927 for the interval, and a design-of-experiments text
   for the ANOVA and chi-square.
3. Drop the Wilson interval from the figure and show plain counts.

I would take option 1 for the tests and keep the Wilson interval named in the caption as it
already is.

**The diode-equation fit itself.** Fitting V = V₀ + n·V_T·ln(I) + I·R_s by nonlinear least
squares is textbook. [R2] extracts ideality factors from measured I-V curves and [R5] fits
forward-voltage data, so between them the practice is covered. Adding a separate extraction
paper would be padding.

---

## 4. One discrepancy the reading turned up

The draft says the effective resistivity of the Au surface finish was 10 x 10⁻⁸ Ω·m,
measured on the CDE ResMap 178.

[R1], from the same group and the same instrument, reports **2.86 x 10⁻⁸ Ω·m for Au**
(with 3.59 x 10⁻⁸ for Cu and 2.74 x 10⁻⁸ for Ag). Bulk gold is 2.44 x 10⁻⁸ Ω·m, so 2.86 is
a sensible thin-film value and 10 is four times bulk.

Either the new wafer genuinely differs from the one in the ECTC paper, in which case the
factor of 3.5 is worth a sentence, or the number has been mistyped. Worth checking against
the raw ResMap output before submission, since [R1] is cited two lines earlier and a reader
can put the two numbers side by side.

---

## 5. Three numbers in the draft worth fixing

Checked against the raw data. The conclusions do not change; the arithmetic does.

### 5.1 The shunt fraction: neither one third nor 61 %

Paragraph beginning "One numerical correction:". Two things.

First, that paragraph is an editorial note written in the first person and it is sitting in
the body of the article. It needs to come out.

Second, the number. The correct figure is **about 44 %**, and the reason both earlier
figures missed it is the test current. This meter is not a 1 mA source. Its diode-mode test
current was measured directly during the round 1 setup as 0.142 V across a 100 Ω 0.1 %
reference, so **1.42 mA**, cross-checked against a 1.49 mA short-circuit figure.

At the 1.781 V reading a 2.87 kΩ shunt carries 0.62 mA. Against 1.42 mA that is 44 %, and
the junction takes the remaining 0.80 mA.

That split is confirmed independently. A healthy die on the same coupon sits at 1.749 V at
0.349 mA; carrying it to 0.80 mA through its own fitted ideality gives 1.783 to 1.793 V,
against the 1.781 V actually read. The alternative reading, that the meter is a Thevenin
source of 3.245 V behind about 2.2 kΩ, would put only 0.05 mA through the junction and
predict a reading roughly 150 mV low, so the data rules it out.

Suggested replacement: *"At the 1.781 V reading, the shunt carries 0.62 mA of the meter's
1.42 mA diode-test current, so the junction sees only 0.80 mA and the channel still reads
as a normal red LED."*

### 5.2 The variance share is 85 %, not 83 %

The re-seating paragraph currently reads "approximately 83 %, or about 85 %". One number,
and it is 85 %.

The pooled within-condition standard deviation over the 29 physical red-channel fits is
0.9147 Ω and the re-seating pooled standard deviation is 0.843 Ω, so the variance ratio is
0.843² / 0.9147² = 84.9 %. The 83 % comes from rounding 0.84 before squaring.

### 5.3 The self-heating estimate does not reproduce 1.2 Ω

The stated inputs are 200 K/W, 28.4 mW and -2 mV/K. Because dissipated power is very nearly
proportional to current over this range, the thermal perturbation is linear in current and
folds entirely into the fitted series resistance:

```
  ΔR_s ≈ λ · R_th · V_F = (2 mV/K)(200 K/W)(2.01 V) = 0.80 Ω
```

not 1.2 Ω. Against the measured 1.49 Ω that is a factor of 1.9, so agreement "to within
25 %" does not hold as written.

Cleanest fix is to invert it: the measured 1.49 Ω implies R_th ≈ 370 K/W, ordinary for a
0404 package on two-layer FR-4 with no heat-spreading copper. [R5] supports doing it this
way round, since it measures the temperature dependence of LED dynamic resistance directly.
The conclusion is unaffected: heating sets in between 20 and 80 ms, so 5 ms is safe.

---

## 6. Smaller editorial points

- The equation symbols dropped out of the paraphrase in two places: "where  is the terminal
  voltage,  is the voltage offset,  is the ideality factor" and "Over this limited range ,
  , and  were strongly correlated".
- "a statistically significant association between assembly condition and channel
  p = 2.2 x 10⁻⁴" is missing a word after "channel".
- Two cross-references still point at Section D.
- The sheet-resistance sentence gives resistivity but not the sheet resistance in Ω/sq or
  the Au thickness. Since ρ = R_sheet · t, giving two of the three lets a reader check it.
  See section 4 above.

---

## Downloaded PDFs

| File | Article |
|---|---|
| `references/ECTC2025_Abdelwahab_pick_and_release.pdf` | [R1], 8 pp |
| `references/TED2024_Zhanghu_ideality_factor_IQE_microLED.pdf` | [R2], 8 pp |
| `references/TED2015_Jung_leakage_parasitic_diode_model.pdf` | [R3], 4 pp |
| `references/TED2024_Roccato_fast_characterization_power_LEDs.pdf` | [R4], 8 pp |
| `references/TIA2013_Gacio_junction_temperature_dynamic_resistance.pdf` | [R5], 11 pp |

Note on [R1]: the title in our older `report/refs.bib` was wrong. The Xplore record gives
"Pick-and-Release: A Novel Contactless Bonding Method for Die Attachment", not "Electrical
Characterization of Capillary Self-Assembled Micro-LEDs on PCB Substrates". The DOI was
right.
