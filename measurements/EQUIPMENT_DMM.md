# Equipment: handheld DMM (phase 1)

Photo: `photos/2026-08-03_dmm-thsinde-18B-plus.jpg`

Meter: **Thsinde 18B+**, a rebadge of the widely cloned ANENG/BSIDE 18B+ platform.
This is the only instrument available for the first measurement session, so this file
records exactly what it can and cannot resolve on the v2 micro-LED bond board.

---

## 1. What is on the meter (read off the photo)

### Rotary switch, clockwise from OFF

| Position | Function | SELECT toggles |
|---|---|---|
| `Hz ~V` | AC voltage, true RMS | V / Hz |
| `V⎓` | DC voltage | - |
| `mV` | millivolt range | DC mV / AC mV |
| `Ω ·))) ·→⊢· ·⊣⊢` | resistance / continuity beeper / diode test / capacitance | cycles the four |
| `Hz %` | frequency and duty cycle | - |
| `A` | current, 10 A jack | DC / AC |
| `mA` | current, mA jack | DC / AC |
| `µA` | current, µA jack | DC / AC |
| `NCV` | non-contact voltage detect | - |

### Buttons

| Button | Use in this work |
|---|---|
| `SELECT` | cycle Ω → continuity → diode → capacitance. **Used constantly.** |
| `RANGE` | lock a manual range. **Use it.** Autorange hunts and costs repeatability. |
| `REL Δ` | subtract the present reading as an offset. **The single most important button here** (lead and probe compensation). |
| `HOLD` | freeze reading; long-press is the backlight |
| `MAX/MIN` | not used in phase 1 |
| `Hz %` | not used in phase 1 |

### Input jacks

| Jack | Rating |
|---|---|
| `10A` | 10 s max, fused |
| `mAµA` | 600 mA max, fused |
| `COM` | common |
| `VΩHz →⊢ ⊣⊢` | 1000 V DC / 750 V AC, CAT IV 600 V |

True RMS, auto power off.

---

## 2. Resolution (verify, do not assume)

The 18B+ platform is a 6000-count meter. **Confirm this before the session**: set the
Ω range manually and check whether the display tops out at `599.9` (6000 counts) or
`599` (600 counts). Everything below assumes 6000 counts.

| Function | Range to lock | Resolution | Relevance here |
|---|---|---|---|
| Ω | 600.0 Ω | **0.1 Ω** | continuity, trace R, bridge screen |
| Ω | 6.000 kΩ | 1 Ω | - |
| Ω | 60.00 kΩ | **10 Ω** | NTC thermistors (10 kΩ nominal) |
| Ω | 6 MΩ / 60 MΩ | 1 kΩ / 10 kΩ | reverse-leakage screen (expect OL) |
| DC mV | 600.0 mV | 0.1 mV | only with an external source |
| DC V | 6.000 V | 1 mV | only with an external source |
| Diode | fixed | 1 mV | **V_F fingerprint, the workhorse** |
| µA DC | 600.0 µA | 0.1 µA | only with an external source |
| mA DC | 60.00 mA | 10 µA | only with an external source |
| Capacitance | 6.000 nF and up | 1 pF | no useful role (see section 5) |

Published accuracy for this platform is roughly ±(0.5 % + 3) on DC V and
±(0.8 % + 5) on Ω. **Treat those as unverified.** Section 4 replaces them with numbers
you measure on this board.

---

## 3. The hard limit, stated plainly

A reflowed micro-LED solder joint has a resistance of order **10 mΩ to 100 mΩ**.

The measurement chain in front of it:

```
  meter floor (600 Ω range)             0.1 Ω
  test-lead resistance                  0.1 - 0.5 Ω   (removable with REL Δ)
  needle-on-ENIG contact resistance     0.05 - 0.5 Ω, varies shot to shot
  ---------------------------------------------------
  realistic 2-wire repeatability        ±0.2 to ±0.5 Ω
```

That is **5 to 50 times larger than the thing being measured.** REL Δ removes the fixed
lead offset but not the contact-resistance scatter, which is the dominant term and is
random per landing.

Consequences, all of them:

| Target quantity | Verdict with this meter |
|---|---|
| Single bond resistance R_b | **Not measurable.** Needs 4-wire Kelvin at mΩ resolution. |
| LED series resistance R_s from dV/dI | **Not measurable.** No current source, no sweep. |
| Chain I-V (N=6 needs ~12 V, N=12 needs ~24 V) | **Not measurable.** Diode mode cannot reach the turn-on voltage. |
| Reverse leakage in nA | **Not measurable.** Needs a bias source. |
| Bond **open** | **Measurable, definitive.** |
| Bond/pad **short or bridge** | **Measurable, definitive.** |
| Per-channel V_F at the meter's own test current | **Measurable, repeatable, comparable across all 8 samples. The primary dataset.** |
| Defect census per sample | **Measurable**, but see the n = 4 caveat in `SAMPLES.md` section 3 before turning it into a yield percentage. |
| Board temperature via the 4 on-board NTCs | **Measurable to about 0.02 K resolution.** |

So phase 1 is a **screening, V_F fingerprint and baseline** campaign. It is not a
bond-resistance campaign. Written up that way it is honest and useful; written up as
bond resistance it would be noise.

The DoE bond-pad array, TLM ladders and Van der Pauw cloverleaves on these boards carry
no solder and no dice, so they are out of scope for the whole campaign, not just for
this meter. See `SAMPLES.md` section 2.

---

## 4. Meter self-characterization (do once, about 15 min)

The board carries its own calibration artefacts, so the meter's unknown specs can be
turned into measured facts. Do this before touching any LED and record every number.

Structures used (all on the v2 board, `EIS CAL` block, y ≈ 35 mm):

| Structure | Nets | Expected |
|---|---|---|
| `R_EIS_LOAD` (Yageo RT0603BRB07100RL) | `EIS_LOAD_A` / `EIS_LOAD_B` | 100 Ω, 0.1 % tolerance |
| `PP_EIS_SHORT_A` / `PP_EIS_SHORT_B` | both on net `EIS_SHORT` | short trace, near 0 Ω |
| `PP_EIS_OPEN_A` / `PP_EIS_OPEN_B` | separate nets, no copper | true open, OL |

**S1. Lead zero.** Ω mode, RANGE locked to 600.0 Ω. Short the probe tips firmly.
Record the raw reading (`R_leads`). Press `REL Δ`. Display goes to 0.0.

**S2. Repeatability of the zero.** Lift and re-touch the probe tips 10 times, recording
each reading after REL. The spread of those 10 numbers **is your measurement uncertainty
for every resistance in the session.** Record it as `sigma_2wire`. Expect 0.1 - 0.3 Ω.

**S3. Reference resistor.** Still REL-zeroed, probe the two solder fillets of
`R_EIS_LOAD`. Expect 100.0 Ω ± 0.5 Ω. Record. Any larger deviation means the meter's
gain error is worse than assumed and the whole session is scaled by it.

**S4. Diode-mode test current.** This is the number that gives every later V_F reading
its meaning. Switch to diode mode. Probe across the same 100.0 Ω resistor. The display
shows the voltage across it, so

```
              V_display
  I_test  =  ───────────
               100.0 Ω
```

A reading of 0.100 V means I_test = 1.00 mA. Expect 0.5 - 1.5 mA.
**Record `I_test`. Every V_F in this campaign is "V_F at I_test", not "V_F at 10 mA".**

**S5. Diode-mode compliance voltage.** Probe a resistor of about 10 kΩ (any loose part)
in diode mode. Because the meter sources roughly a fixed current, it will hit its
open-circuit ceiling and display that ceiling, `V_oc`. If it shows `OL` instead, `V_oc`
is above the display maximum.

This single reading decides whether green and blue channels are testable at all:

| `V_oc` measured | Consequence |
|---|---|
| ≥ 3.2 V | red, green and blue channels all testable in diode mode |
| 2.0 - 3.2 V | red testable; green/blue marginal, many will read OL |
| < 2.0 V | red only, and even red may read OL |

Würth WL-SFCC nominal V_F at 10 mA: red ≈ 2.0 V, green ≈ 3.0 V, blue ≈ 3.0 V.
At 1 mA these drop by roughly 0.2 - 0.3 V, so expect red ≈ 1.7 - 1.9 V and
green/blue ≈ 2.6 - 2.8 V.

**S6. Board short/open references.** REL-zeroed Ω mode across `PP_EIS_SHORT_A/B`:
record the residual (probe + trace). Ω mode across `PP_EIS_OPEN_A/B`: must read OL.
A finite reading on the OPEN pair means contamination or paste bridging, which
invalidates isolation assumptions everywhere else on that board.

**S7. Drift check.** Repeat S3 (the 100 Ω) at the start of the session, every ~30 min,
and at the end. Log all of them. Divergence over the session is your drift term.

---

## 5. Functions with no role here, and why

Recording this so the session is not spent exploring dead ends.

| Function | Why not |
|---|---|
| Capacitance | LED junction capacitance at zero bias is a few pF, below the meter floor and swamped by lead capacitance. It cannot see a bond. |
| `A` / `mA` / `µA` | These measure current from an external source. With no source in phase 1 there is nothing to measure. Also: putting the meter in a current range across a powered LED is a near-short. |
| `Hz` / `%` / AC V | No AC excitation in this work. |
| `NCV` | Mains proximity detector. Irrelevant. |
| `MAX/MIN` | Useful only for logging a varying signal. Nothing varies in phase 1. |

---

## 6. Handling rules

- **ESD wrist strap the whole session.** The WL-SFCC dice are ESD sensitive and an ESD
  kill is indistinguishable from a bad bond in the data. This is the single largest risk
  of corrupting the result set.
- Diode mode sources about 1 mA and ohms mode less. Both are safe for the dice.
- Land probes on the **ENIG pads and the exposed solder fillets**, never on the die body.
- Use light pressure with fine needles. Gouging the ENIG changes the pad for every later
  measurement and for the die-shear work.
- Hold the board by the edges. A hand on the board warms it by several K, and
  dV_F/dT ≈ −2 mV/K, which is the same order as the effects being looked for. Log the
  NTCs at every block.
- Take each diode-mode reading after a consistent settle time (about 2 s). The reading
  creeps as the junction self-heats.

---

## 7. What each additional instrument would unlock

Ordered by cost, so the next session can be planned.

| Add | Cost | Unlocks |
|---|---|---|
| **Arduino UNO + 6 resistors** (already owned) | **zero** | **A full 63-point I-V sweep per channel, 4-wire Kelvin, pulsed against self-heating. Extracts R_s to about ±10 mΩ, 1σ. This is the real upgrade: see `ARDUINO_IV_RIG.md`.** |
| 9 V battery + 1 kΩ resistor + breadboard | near zero | One or two I-V points per channel. Superseded by the Arduino rig, which does the same job better. A two-point slope cannot separate the diode's exponential term from R_s, so it does not actually yield a bond number. |
| 4 × 9 V in series (36 V) + dividers | near zero | The chains on samples 1 and 2 forward-biased, which is otherwise completely inaccessible. See `ARDUINO_IV_RIG.md` section 9. |
| Bench PSU 0-30 V + 1 kΩ + 10 kΩ | lab loan | Full `MEASUREMENT_PLAN.md`: chain I-V sweeps on both chains, per-site V_F at 1 and 10 mA, reverse leakage down to ~10 nA. |
| Second DMM | lab loan | Halves the session time. Removes the "set, read V_R, move probe, read V_F, re-read V_R" dance. |
| SMU (Keithley 2400 class) + Summit 11K/12K probe station | lab booking | True pulsed I-V, 24 V compliance for the N=12 chain, pA reverse leakage. **Does not isolate per-bond R_b on these samples** (R_die is still in the sum) and does not improve the cross-sample comparison, which is limited by n and die spread rather than by resolution. Read `DECISIONS.md` D1 before booking. |

The Arduino rig costs nothing beyond parts already on the bench and is the cheapest way
to get a number that discriminates between two *healthy* bonds rather than only between
working and failed. Build it as soon as the phase-1 screen is done, and skip the battery
route entirely.

Do not use the Arduino Nano ESP32 for this: 3.3 V logic cannot forward-bias a 3.0 V blue
channel with any headroom for current sensing, and the ESP32-S3 ADC is markedly more
nonlinear than the ATmega's.
