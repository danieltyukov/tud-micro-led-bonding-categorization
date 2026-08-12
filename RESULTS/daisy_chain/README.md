# Daisy-chain resistance, dummy dies

Total daisy-chain resistance measured by A. Abdelwahab on the DC test structure: a chain of
six 1 x 1 mm2 Au-coated dummy dies, one chain per assembly condition, eight conditions.

Not my measurement, and not the same hardware as the LED coupons in the rest of `RESULTS/`.
It predates this campaign and is reproduced here because it is the one dataset that resolves
bond resistance directly.

| File | Contents |
|---|---|
| `Total daisy chain resistance (8 conditions).xlsx` | Source workbook as received, 12 August 2026 |
| `daisy_chain_resistance.csv` | Same numbers, machine readable, used by the MATLAB figure |

Columns: `condition` 1-8, `R_total_ohm` mean total chain resistance, `R_dev_ohm` the
deviation reported alongside it in the workbook.

## Why it matters here

The LED coupons could not resolve bond resistance. Re-seating two jumpers moved the fitted
series resistance by 0.84 ohm, against bond resistances of 10 to 100 mohm, so the one-way
ANOVA over conditions was never going to find anything (`../R2_REPORT.md`, and the
repeatability section of the characterization report).

This structure does resolve it. The spread across conditions is 0.39 ohm from the lowest
(condition 5, 0.22 ohm) to the highest (condition 4, 0.61 ohm), carried by 12 joints, so
roughly 30 mohm per joint. The reported deviation is 11 to 20 mohm, about 20 to 35 times
smaller than the between-condition spread.

The ranking agrees with the LED yield ranking:

| | lowest chain resistance | highest chain resistance |
|---|---|---|
| Chain | 5 (0.22), 7 (0.24) | 4 (0.61), 3 (0.56) |
| LED channel yield | 5 (100 %), 7 (100 %) | 3 (25 %), 4 (66.7 %) |

Two independent structures, one continuity screen and one resistance measurement, put the
same two conditions in the process window.

## Figure

`figures.m` in `../../FINAL_MEASUREMENTS/analysis/` reads `daisy_chain_resistance.csv` and
writes `fig9_daisy_chain` (markers, matching the style of figures 4 and 6) and
`fig9b_daisy_chain_bars` (bar variant).

## Caveats

- Chain totals include the board traces and the probe landing, which are common to all
  conditions but were not subtracted. The figures are comparative, not absolute per-joint
  resistances.
- Sample size behind each mean, and whether the deviation is a standard deviation or a
  range, are not recorded in the workbook. The figure calls it deviation for that reason.
- Dummy dies are Au-coated and unpatterned, so the chain measures the joint and the trace
  only. No junction is involved, unlike the LED channels.
