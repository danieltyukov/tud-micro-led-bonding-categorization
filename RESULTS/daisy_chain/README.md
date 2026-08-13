# Daisy-chain resistance, dummy dies, v1 board

Total daisy-chain resistance measured by A. Abdelwahab on the DC test structure of the
**v1 PCB**: a chain of six 1 x 1 mm2 Au-coated dummy dies, one chain per assembly
condition, eight conditions.

**This is a separate experiment.** Not my measurement, not my board, not the same session.
It was run on its own on the v1 board, which is the vehicle described in the ECTC 2025
paper (`../../docs/article/references/ECTC2025_Abdelwahab_pick_and_release.pdf`, Section E,
where the same DC structure and the same CDE ResMap 178 and Summit 11K/12K probe station
are described). The LED coupons in the rest of `RESULTS/` are a different test vehicle
measured in a different campaign.

Reproduced here because it is the one dataset that resolves bond resistance directly.

The v2 board carries daisy chains too, but **no daisy-chain measurements were taken from
it**. A layout fault left each chain die's anode floating, so those chains were diagnosed
as dead and excluded rather than characterized (`../README.md`, and
`../../measurements/DECISIONS.md` D3). The only daisy-chain data anywhere in this
repository is the v1 set on this page.

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
| Chain, v1 board | 5 (0.22), 7 (0.24) | 4 (0.61), 3 (0.56) |
| LED channel yield, my coupons | 5 (100 %), 7 (100 %) | 3 (25 %), 4 (66.7 %) |

Spearman rho = -0.92, p = 0.003 across the eight conditions.

**Read that as agreement between assembly conditions, not between two structures on one
coupon.** The two datasets share condition numbering, nothing else: different board,
different session, different operator, no shared hardware. So it is an independent
replication of the process ranking rather than a within-sample cross-check, and it carries
whatever session-to-session drift sits between the two campaigns.

It also rests on the assumption that conditions 1 to 8 mean the same eight recipes in both
datasets. That mapping came with the workbook and has not been independently confirmed. If
it is wrong the correlation is meaningless, so confirm it before the number goes in a paper.

## Figure

`figures.m` in `../../FINAL_MEASUREMENTS/analysis/` reads `daisy_chain_resistance.csv` and
writes `fig9_daisy_chain` (markers, matching the style of figures 4 and 6) and
`fig9b_daisy_chain_bars` (bar variant).

## Caveats

- Chain totals include the v1 board traces and the probe landing, which are common to all
  conditions but were not subtracted. The figures are comparative, not absolute per-joint
  resistances.
- Sample size behind each mean, and whether the deviation is a standard deviation or a
  range, are not recorded in the workbook. The figure calls it deviation for that reason.
- Dummy dies are Au-coated and unpatterned, so the chain measures the joint and the trace
  only. No junction is involved, unlike the LED channels.
