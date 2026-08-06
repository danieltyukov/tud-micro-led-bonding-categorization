# Micro-LED bonding: electrical characterization

Electrical characterization of eight micro-LED assembly conditions across five coupons.
Round 1 screened every channel with a DMM. Round 2 swept the current through each surviving
channel and fitted the diode equation.

## Result in one line

Channel yield and failure mode separate the eight conditions (chi-square, p = 2.2e-4) and
place conditions 5 and 7 ahead of the rest. Series resistance does not separate them, because
the measurement fixture repeats to only 0.84 ohm while bond resistances are 10 to 100 mohm.

| condition | yield | failure modes | assessment |
|---|---|---|---|
| 1 | 83.3 % | open 1, detached 3 | under-bonded |
| 2 | 58.3 % | open 4, detached 6 | under-bonded |
| 3 | 25.0 % | suspect 1, cross-lit 2, open 2, short 4 | over-bonded |
| 4 | 66.7 % | suspect 1, cross-lit 1, open 1, short 1 | over-bonded |
| 5 | 100 % | none | in window |
| 6 | 75.0 % | detached 3 | under-bonded |
| 7 | 100 % | none | in window |
| 8 | 83.3 % | short 2 | over-bonded |

## Contents

    report/     the section as .docx and .pdf, figures embedded
    figures/    all 8 figures, PNG at 600 dpi and vector PDF
    matlab/     analysis code, R2025b
    data/       raw measurements, both rounds
    firmware/   the Arduino sketch and the rig wiring diagram

## Reproducing the figures

Open MATLAB in `matlab/`, adjust nothing, and run:

    figures

It reads `../data/`, refits every sweep, writes the eight figures into `figures/`, and prints
every number quoted in the report. Requires the Statistics and Machine Learning Toolbox for
`anova1` and `chi2cdf`.

    readsweep.m   read one sweep CSV
    fitdiode.m    three-parameter fit of V = V0 + n*VT*ln(I) + I*Rs
    collect.m     fit every channel, one table row each
    figures.m     main script

## Data

`data/round1_dmm/` is the DMM screening: one row per channel with the diode voltage and a
verdict. `data/round2_sweeps/` is one CSV per sweep, 63 current levels each, with columns
`level, i_mA, v_die_V, v_anode_V, v_cath_V, v_sense_V, v_gnd_V, vcc_V`. Files ending `_OPEN`
are channels that drew no current, kept because they confirm the round 1 verdict. Files
`heat_os*` are the self-heating study, `verify_100R_*` the fixture verification against a
100 ohm reference, and `_seat2`/`_seat3` the re-seating repeatability runs.

`data/fit_results.csv` holds the fitted parameters for every channel.
`data/R2_REPORT.md` is the working log of the round 2 campaign, including the four
instrument defects found and fixed during it.

## Caveats worth reading before using the numbers

Series resistance is not usable for comparing bonds in this build. Both voltage taps sit on
the breadboard rather than on the Tier-1 probe pads, so the two female-male jumpers fall
inside the measured loop. Re-seating them on an unchanged channel moves R_s by 0.84 ohm,
which is 85 % of the apparent die-to-die spread. Sensing at the probe pads would fix it.

Green and blue fits are not physical. Their ideality factors come out at 3.2 to 4.0 because
the 5 V rail leaves only a 20-fold current range at V_F near 2.8 V. Red only.

Reverse leakage was not measured. TLM, van der Pauw and impedance spectroscopy need
instruments that were not available.

The DCL6 and DCL12 daisy chains read open on every coupon. The chain routes each die's
top-left pad to its top-right pad, and with the dice rotated 90 degrees those are the red and
blue cathodes, so every element is a pair of back-to-back diodes. Layout fault in this coupon
revision, not a bonding failure.
