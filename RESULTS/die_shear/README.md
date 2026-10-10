# Die shear strength, 8 conditions

Die shear strength per assembly condition, measured by A. Abdelwahab and received on
9 October 2026. Not my measurement. He asked for it to be plotted in the same style as
the daisy chain resistance figure (`../daisy_chain/`).

| File | Contents |
|---|---|
| `die shear strength MPa.xlsx` | Source workbook as received (numbers stored as text, unit written "Mpa") |
| `die_shear_strength.csv` | Same numbers, machine readable |

Columns: `condition` 1-8, `shear_MPa` mean die shear strength, `shear_dev_MPa` the
deviation reported alongside it in the workbook.

## Figure

`../../deliverable/for_ahmed_2026-10-10/die_shear_figure.m` writes
`die_shear_strength_bars` (bars, matching the daisy chain bar figure he pasted back) and
`die_shear_strength` (markers). Same settings as `figures.m`: Helvetica 9 pt, 8.9 cm wide,
600 dpi PNG and vector PDF.

## Against the chain resistance

Conditions 5, 7 and 1 are the three strongest (44.2, 35.2, 32.1 MPa) and also the three
lowest chain resistances (0.22, 0.24, 0.40 ohm). Condition 4 breaks the pattern: mid-range
strength (25.1 MPa) but the highest chain resistance (0.61 ohm). Across all eight,
Spearman rho = -0.57, p = 0.14 (Pearson r = -0.73, p = 0.04). Against the LED channel
yield, rho = 0.59, p = 0.12. Eight points, so a trend at most.

## Caveats

- Number of dies sheared per condition, and whether the deviation is a standard deviation
  or a range, are not in the workbook. The figure calls it deviation, as for the chains.
- Which test vehicle and die type were sheared is not stated. Comparisons with the chain
  data or the LED coupons assume the condition numbering is shared, as before.
- Reported deviation is 6 to 13 % of the mean.
