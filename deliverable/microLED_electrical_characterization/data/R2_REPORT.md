# Round 2 — Arduino I-V sweep: results and conclusions

Written by the analysis side. 89 channel sweeps across 5 boards / 8 samples,
plus 9 repeatability sweeps. Raw data in `../FINAL_MEASUREMENTS/data/R2_sweeps/`.

---

## The headline

**The eight bonding conditions cannot be distinguished by series resistance, and
the reason is now measured rather than assumed: the rig's own repeatability is
larger than the effect.**

    one-way ANOVA over the 7 samples with n>=3:  F(6,21) = 1.96   not significant
    between-sample sd 1.28 ohm    within-sample sd 0.92 ohm

**85 % of that within-sample "die-to-die" scatter is the female-male jumpers, not
the dice.** Three channels re-seated three times each:

| channel | seat 1 | seat 2 | seat 3 | sd |
|---|---|---|---|---|
| s7 D1 R | 10.323 | 12.365 | 10.329 | 1.177 |
| s7 D3 R | 10.424 | 11.130 | 11.769 | 0.673 |
| s8 D6 R | 10.984 | 11.939 | 11.900 | 0.541 |

Pooled seat-to-seat sd **0.843 ohm**, against a within-sample sd of 0.915. Every
channel's minimum is its cleanest seating, and contact resistance can only add, so
the true red R_s is near the **mean of the minima, 10.58 ohm**, with roughly
**0.85 ohm of wiring** sitting on top of every reported number.

Bond resistances are 10-100 mOhm. The instrument floor is 840 mOhm. The experiment
was never capable of resolving them.

### Root cause

`2_ARDUINO_IV.md` takes both sense taps from the breadboard (A1 on FORCE, A0 on
RETURN) rather than from the Tier-1 probe pads. That folds both female-male
jumpers and both header contacts into `v_die`. `ARDUINO_IV_RIG.md` section 4.2
specified the Kelvin arrangement precisely to keep them out. Dropping it is the
single most consequential decision in the round 2 design.

---

## What the data does support

**Yield separates the conditions clearly, and R_s does not.**

| sample | channels lost / 24 | failure modes |
|---|---|---|
| 1 | 2 | 1 detached die, 1 open |
| 2 | 7 | 2 detached dice, 4 opens |
| 3 | 9 of 12 | 5 shorts, 3 opens, 4 cross-lit, 1 shunted — solder contamination |
| 4 | 3 of 12 | 1 short, 1 open, 1 cross-lit |
| 5 | 0 | — |
| 6 | 3 | 1 detached die |
| 7 | 0 | — |
| 8 | 2 | 2 shorts |

Samples 5 and 7 lost nothing. Sample 3 lost 75 %. That is a far stronger
discriminator between processes than any R_s difference, and it does not depend on
the instrument at all.

---

## Findings about the measurement itself

**Round 1's DMM screening was completely reliable.** Six channels it called open
or shorted drew no current on the rig; every channel it passed swept normally.
Zero disagreements in 89 sweeps.

**The rig found one defect the DMM could not.** `s3 D1 R` fits to ideality 13.0 and
R_s = -27 ohm, which is impossible. Below 3 mA the junction sits at 1.21 V — under a
red LED's turn-on — while 0.42 mA flows, so the current is going around the die. A
~2.9 kOhm shunt, consistent with the solder smear round 1 noted. A DMM diode test at
1 mA reads 1.781 V and passes it. Only a current sweep resolves it. Round 1 flagged
it "suspect" without knowing why; that instinct was right.

**The ideality check is a defect detector.** Any channel fitting outside
n = 1.2 to 2.4 has something in parallel with the junction regardless of how normal
its curve looks at working current. It cost nothing and caught the one defect the
DMM missed. All 29 usable reds fit at n = 1.60 to 2.06.

**Green and blue R_s are not usable at 5 V.** Green fits at ideality 3.2 to 4.0,
which is unphysical; blue at 2.2 to 2.5 is borderline. With V_F near 2.8 V the bank
only spans 20x in current, so V0, n and R_s trade off against each other. Red gets
30x and fits cleanly. **Report red only.** More current range would fix this; more
current precision would not, so an SMU is not the answer for green.

---

## Rig defects found and fixed during the campaign

| defect | effect | resolution |
|---|---|---|
| `SHIFT = 4` hardcoded in the original sketch | correct only at OVERSAMPLE 256; step 4 would have rescaled every voltage 4x and 1/4x | divide by `1024 * OVERSAMPLE` |
| Common ADC offset, 14.4 mV | cancels in `v_die`, not in current; 26 % current error at the bottom of the sweep | measured three independent ways, added back in firmware |
| `bandgapRaw()` truncated to integer | quantised the rail to 0.455 %, putting a 2-3 mV floor on `v_die` and costing ~13x in fit precision | return a float over 64 samples |
| Link jumper contact, 2.9 ohm | outside both measurement loops, but a canary | reseated to 0.4-0.7 ohm |

The differential-current fix (A3 to the GND rail) **did not work** and could not:
the GND rail sits at ~0 V, and a channel reading low cannot report a negative count,
so the offset is clipped there and subtracting it does nothing. A3 remains as a
monitor of the ground path.

Verification was bracketed with a 100 ohm dummy. Boards 1, 2 and 5/6 closed at
98.398 / 98.626 / 100.372 ohm with intercepts of -0.72 / -0.78 / -0.42 mV. Board 3/4's
verify failed on a worn dummy fixture, not on the rig: its die sweeps have fit
residuals of 1.29-1.54 mV, indistinguishable from the other boards' 1.55.

---

## Per-channel results, red

| sample | die | R_s (Ω) | n |
|---|---|---|---|
| 1 | D1 | 10.01 | 1.74 |
| 1 | D2 | 11.12 | 1.78 |
| 1 | D3 | 10.05 | 1.75 |
| 1 | D4 | 10.55 | 1.74 |
| 1 | D7 | 12.12 | 1.81 |
| 1 | D8 | 10.77 | 1.67 |
| 2 | D2 | 10.88 | 1.80 |
| 2 | D3 | 10.75 | 1.66 |
| 2 | D4 | 11.22 | 1.77 |
| 2 | D5 | 11.64 | 1.66 |
| 2 | D8 | 11.11 | 1.66 |
| 3 | D1 | -27.46 **excluded** | 12.98 |
| 3 | D4 | 10.92 | 1.65 |
| 4 | D5 | 12.13 | 1.81 |
| 4 | D6 | 13.43 | 1.69 |
| 4 | D8 | 12.81 | 1.78 |
| 5 | D1 | 10.43 | 1.70 |
| 5 | D2 | 12.79 | 1.82 |
| 5 | D3 | 11.24 | 1.81 |
| 5 | D4 | 10.67 | 1.92 |
| 6 | D5 | 10.69 | 1.69 |
| 6 | D6 | 12.37 | 1.67 |
| 6 | D7 | 13.01 | 1.80 |
| 7 | D1 | 10.32 | 1.79 |
| 7 | D2 | 12.03 | 1.87 |
| 7 | D3 | 10.42 | 1.76 |
| 7 | D4 | 13.05 | 1.77 |
| 8 | D5 | 12.66 | 2.06 |
| 8 | D6 | 10.98 | 1.93 |
| 8 | D7 | 11.18 | 1.75 |

| sample | n | mean R_s | sd |
|---|---|---|---|
| 1 | 6 | 10.770 | 0.785 |
| 2 | 5 | 11.120 | 0.344 |
| 3 | 1 | 10.918 | — |
| 4 | 3 | 12.788 | 0.650 |
| 5 | 4 | 11.283 | 1.062 |
| 6 | 3 | 12.023 | 1.201 |
| 7 | 4 | 11.456 | 1.319 |
| 8 | 3 | 11.606 | 0.916 |

Grand mean 11.426 ohm, sd 0.995, N = 29. Corrected for the wiring term, true red
R_s is approximately **10.6 ohm**.

---

## Not collected

- **NTC readings.** None, for any board. Ambient drift cannot be separated from
  self-heating at analysis time.
- **Step 6, reverse leakage.** Skipped by operator decision after the rig was
  assembled. It was the only remaining measurement insensitive to contact
  resistance, and the only one that would have quantified the s3 D1 R shunt.
  Rewire diagram kept at `../FINAL_MEASUREMENTS/arduino-rig/leakage_step6.pdf`.
- **Opening verifies** for boards 2 and 3/4.

---

## If this were repeated

1. **Sense at the Tier-1 probe pads, not the breadboard.** This is the whole
   result. Without it, R_s measures the jumpers.
2. **Report red only,** or raise the supply above 5 V so green and blue get a
   usable current range.
3. **Seat repeats from the start,** not at the end. Three seatings on one channel
   per board would have exposed the problem on day one.
4. **Keep the ideality check.** It is a free defect detector.
5. Self-heating is real but not limiting: R_s falls 1.49 ohm between a 5 ms and an
   80 ms pulse, and 64x oversampling (5 ms) is indistinguishable from 256x.
