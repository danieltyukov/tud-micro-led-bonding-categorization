# Phase 1: what to measure with the handheld DMM alone

Instrument: Thsinde 18B+, see `EQUIPMENT_DMM.md`.
Samples: 8 bonded conditions on 5 PCBs, see `SAMPLES.md`.
Successor session: `MEASUREMENT_PLAN.md`, which needs a bench PSU.

---

## Scope

**In scope:** the individual LED row D1 - D8 on all five PCBs.

**Daisy chains: excluded.** They are electrically dead by a board design fault (die rotation
leaves the chain wired cathode-to-cathode with the anode floating). See `SAMPLES.md`
section 2 and `DECISIONS.md` D3.

**Out of scope, permanently:** the DoE bond-pad array, the TLM ladders and the Van der
Pauw cloverleaves. They carry no solder and no dice on any of these boards. The only
passive structure still used is the `EIS CAL` block, as the meter calibration artefact.

| Sample | Dice measurable | Note |
|---|---|---|
| 1 | 7 | 1 detached |
| 2 | 6 | 2 detached |
| 3, 4 | 4 each | board contaminated, excluded from V_F stats |
| 5, 7, 8 | 4 each | |
| 6 | 3 | 1 detached |

## What this session is and is not

**Is:** a defect screen, a bond census, a V_F fingerprint at one fixed low current, and a
temperature baseline. None of those needs a source, a sweep, or 4-wire sensing.

**Is not:** bond resistance. A good joint is 10 - 100 mΩ; two-wire hand probing on ENIG
repeats to about ±0.2 - 0.5 Ω. The measurement is 5 to 50 times coarser than the effect.
Do not record a number and call it R_bond. See `EQUIPMENT_DMM.md` section 3.

**Lead with V_F, not with yield.** Samples 3 - 8 have only 4 dice each, so a binary
pass/fail rate from them carries almost no confidence (see `SAMPLES.md` section 3).
The V_F distribution uses those same 12 channels as measurements rather than as trials
and is the more informative product. Yield is the defect census that accompanies it.

---

## Sequencing with the Arduino rig

`ARDUINO_IV_RIG.md` replaces part of this session and depends on another part. Do not run
all of phase 1 and then build the rig: about 80 min of it would be duplicated work.

### What the Arduino rig replaces (do NOT do the full five-board pass first)

| Step | Why it is superseded |
|---|---|
| Step 4, diode V_F on D1 - D8 | The rig measures V_F at 63 currents per channel instead of one, and extracts R_s |
| Step 6, reverse leakage | The rig reaches ~100 nA; the DMM only distinguishes `OL` from not-`OL` |

Still do **step 4 on one board** before building the rig. It costs 20 min and gives you
ground truth: a channel the DMM says is dead is dead, so when the Arduino later reads
nothing you know it is your probe contact and not the bond. It is also the cross-check
that validates the rig's absolute V_F.

### What the Arduino rig does NOT replace

| Step | Why the DMM is still needed |
|---|---|
| Step 0, site map | Visual. Nothing electrical substitutes for it. |
| Step 2, wiring integrity | The rig's Kelvin sensing is meaningless until you know each header pin actually reaches its probe pad. |
| Step 3, NTC temperature | The DMM does this at 0.022 K in seconds. |
| Step 5, short and bridge screen | The rig cannot measure 60 MΩ. See the hard dependency below. |

### Hard prerequisites, in order (about 2 h)

Everything here must be done and logged **before** the first die sees Arduino current.

1. **Step 1**, meter self-characterization. Needed regardless.
2. **Step 0**, site map, all 40 individual-die sites. The rig cannot tell an empty site
   from an open bond.
3. **Step 2**, wiring integrity, all five PCBs. Specifically 2a: the rig forces current
   through the header pin and senses at the probe pad, so if that trace is open the force
   path is dead and you would chase a phantom bond failure.
4. **Step 5**, isolation screen, all five PCBs. **This is the one that will actually bite
   you.** A bridge between two cathodes of the same die, say `LEDn_KR` to `LEDn_KB`,
   splits the drive current between two junctions. The rig would happily sweep it and
   report a plausible but wrong R_s for the parallel combination, with nothing in the
   data to reveal it. The DMM at 60 MΩ finds it in seconds; the rig cannot find it at all.
5. **Step 3**, one NTC block per board, as the temperature baseline.
6. **Step 4 on one board only**, as ground truth and cross-check.

Plus three checks specific to the rig, done with the same meter:

7. **Probe-pad contact quality.** Land a needle on each `PP_Dn_A` and `PP_Dn_KR` you plan
   to use and confirm low ohms to its header pin. A pad that will not take a contact makes
   the Kelvin sense read a floating node through the 1 kΩ series resistor, which looks
   like data rather than like a failure.
8. **`R_EIS_LOAD` = 100.0 Ω.** It becomes the rig's sense resistor, so confirm it is
   undamaged (step 1, S3). Its 0.1 % tolerance is the only traceable calibration in the
   whole Arduino chain.
9. **The UNO's 5 V rail.** DC V, 6 V range. This number goes into the `VCC` constant in
   the sketch and is a direct gain error on every R_s. Measure it again with the rig
   powered and drawing current, since it sags under load and differs between USB cables.

---

## Deliverables

| File | Content |
|---|---|
| `00_samples.csv` | one row per sample: process metadata. **Withheld until measurement is complete**, see `SAMPLES.md` section 4 |
| `01_site_map.csv` | one row per bonded site per sample: visual state |
| `02_data_log.csv` | one row per electrical reading |
| `03_temperature.csv` | one row per measurement block: the NTC resistances |
| `04_meter_cal.csv` | meter self-characterization, and every drift re-check |
| `photos/` | whole-board shots, chain close-ups, every anomaly |

Log directly into a spreadsheet as you go. Nothing on paper only.

### `02_data_log.csv` columns

```
timestamp, block_id, sample_id, pcb_id, device, channel, test,
range_locked, rel_zeroed, reading, unit, verdict, notes
```

- `device`: `D1`..`D8`, `CAL_LOAD`, `CAL_SHORT`, `CAL_OPEN`
- `channel`: `R`, `G`, `B`, or blank
- `test`: `diode`, `ohm`, `ohm_rev`, `cont`, `ntc`, `iso`
- `verdict`: `pass`, `open`, `short`, `leaky`, `OL`, `n/a`
- `reading`: the number as displayed. If the meter shows `OL`, write `OL`, not a number.

### `03_temperature.csv` columns

```
block_id, timestamp, sample_id, ntc1_ohm, ntc2_ohm, ntc3_ohm, ntc4_ohm, ambient_note
```

Start a new `block_id` on every board change, every break, and every 30 min. On split
boards, only the two NTCs of the half being measured need a value; leave the others
blank rather than guessing. Convert to °C in analysis, never in the lab:

```
   1        1        1        R
  ───  =  ───── + ─── · ln ( ─── )
   T       T₀       B         R₀
```

with T₀ = 298.15 K, R₀ = 10 kΩ, **B = 4100 K** for the TDK NTCG104BH103HT1 (datasheet
row: 4067 / 4092 / 4100 / 4110 K for B25/50, B25/80, B25/85, B25/100).

---

## Step 0. Microscope site map (before any probing)

Not a DMM step, but it gates the interpretation of every DMM reading. A site with no die
reads `OL`, which is indistinguishable from an open bond in the electrical data alone.

40 individual-die sites. Fill `01_site_map.csv`:

```
sample_id, site, present, alignment, solder, notes
```

- `site`: `D1`..`D8` for every sample. Chain dice are excluded, see Scope.
- `present`: y / n
- `alignment`: ok / shifted / rotated / tombstoned
- `solder`: ok / excess / starved / bridged

Photograph everything that is not `ok`.

---

## Step 1. Meter self-characterization (15 min, once)

Run `EQUIPMENT_DMM.md` section 4 in full: S1 through S7. Record in `04_meter_cal.csv`.

Three numbers gate the rest of the session:

| Number | Where it comes from | What it decides |
|---|---|---|
| `sigma_2wire` | S2, spread of 10 re-landings | Below this, no resistance difference is real |
| `I_test` | S4, V across the 100 Ω in diode mode | The current at which every V_F is quoted |
| `V_oc` | S5, diode mode across ~10 kΩ | Whether green and blue channels are testable at all |

**If `V_oc` < 3.0 V, green and blue channels will read `OL` on healthy parts.** In that
case restrict step 4 to the red channel, and say so in the write-up rather than
reporting a false 100 % G/B failure rate.

Any PCB will do for the CAL block; it is board copper, unaffected by the bonding
condition. Use the same board every time so the drift re-checks are comparable.

---

## Step 2. Board wiring integrity (10 min per PCB, 5 PCBs)

Verify the board before trusting anything measured through it. Ω mode, 600.0 Ω locked,
REL zeroed on the leads.

**2a. South header to probe pad.** For each LED, one check: header pin 4·(n−1)+4 to
`PP_Dn_KR`. Expect 0.1 - 0.5 Ω. This is the trace parasitic in series with every
header-side reading. Do all 8 on the first board, spot-check 2 per board after that.

**2b. Common-anode bus.** South pins 1, 5, 9, 13, 17, 21, 25, 29 are all `LED_VCC`.
Continuity beeper across all of them, then one resistance reading pin 1 to pin 29
(the full length of the B.Cu bus). Expect well under 1 Ω. If any A pin does not join
the bus, that PCB has a fabrication fault and its anode data is invalid.

On PCBs C, D and E this bus crosses the centreline and is shared by both samples on the
board. That is board copper, not a bond, so it does not corrupt either condition, but
note it: an anode-side short on one half is visible from the other.

**2c. North header (samples 1 and 2 only, for the chains).** Pins 3 / 10 / 19 / 32 to
`PP_DCL6_IN` / `PP_DCL6_OUT` / `PP_DCL12_IN` / `PP_DCL12_OUT`. Expect low ohms. On all
five PCBs, pins 5 / 13 / 21 / 29 to `PP_NTC1..4` for the temperature path. Only these 8
north pins are routed; the other 24 are jumper posts with no copper.

**2d. Header isolation.** Adjacent south pins that must never be connected: pin 2 to
pin 3 (`LED1_KG` to `LED1_KB`), pin 3 to pin 4, pin 4 to pin 5 (`LED1_KR` to `LED2_A`).
Expect `OL`. A finite reading is a solder bridge on the header itself, not a bond
defect. Catch it now, before it looks like a process result.

---

## Step 3. Temperature (2 min, at every block boundary)

Ω mode, **60.00 kΩ range locked** (10 Ω resolution ≈ 0.022 K), REL off.

`PP_NTCn` to `PP_GND1`. Expect about 10 kΩ at 25 °C, falling roughly 460 Ω per K of
warming. Log raw resistances into `03_temperature.csv`; do not convert in the lab.

Why this matters: dV_F/dT ≈ −2 mV/K. Holding a board for a few minutes shifts V_F by
several mV, the same size as the differences between bonding conditions. The NTC log is
what lets you separate the two later. It is also the one measurement on this board that
the DMM does genuinely well, at about 0.022 K resolution.

---

## Step 4. Diode-mode V_F on D1 - D8 (20 min per PCB) — the primary dataset

This is the measurement to protect if the session runs short. Do it across all five PCBs
before deepening anywhere.

Diode mode. Probe the south header: A pin to the channel's K pin. Settle 2 s, then read.

Per PCB: 8 dice × 3 channels = 24 readings. Across five PCBs: 120 readings covering all
40 individual dice. Record every reading, including `OL`.

Expected at `I_test` ≈ 1 mA: red 1.7 - 1.9 V, green and blue 2.6 - 2.8 V, subject to
`V_oc` from step 1.

**Free extra: work in a darkened corner.** At ~1 mA a healthy die visibly glows. That
confirms in one glance that the channel conducts, that the die is the colour you think,
and that the light comes from the site you are probing. Note `lit` / `dark` in the notes
column. A channel with a plausible V_F that does not light is a finding.

### Fault classification

| R | G | B | Diagnosis |
|---|---|---|---|
| pass | pass | pass | all four bonds intact at this current |
| `OL` | pass | pass | K_R bond open, or red die failed |
| pass | `OL` | pass | K_G bond open |
| pass | pass | `OL` | K_B bond open |
| `OL` | `OL` | `OL` | anode bond open, or die missing, or die destroyed |
| ≈ 0 V | any | any | shorted joint or bridge |
| pass | `OL` | `OL` | **check `V_oc` first.** If `V_oc` < 3 V this is the expected healthy result, not a fault |

Because all eight anodes are one net, an open anode bond cannot be localized from the
header. **Confirm it by probing the die directly:** land on that die's own anode-side
solder wing and its K_R wing. If the channel now conducts, the fault is in the header
path or the trace, not in the bond. If it still reads `OL`, the anode bond is open.
This two-step is what turns a header reading into a bond conclusion.

### What to extract

Per sample, per colour: **mean V_F, standard deviation, min, max, n**. This is the
headline comparison across the eight bonding conditions.

Alongside it, the defect census: how many channels failed and how, broken down as
anode-open / cathode-open / short. Report it as counts, not as a percentage, given
n = 4 dice on samples 3 - 8.

**Interpretation limit, state it in the write-up:** at 1 mA a 1 Ω series bond resistance
adds only 1 mV to V_F. This dataset separates *intact from failed* and detects grossly
resistive joints of order tens of ohms, but it cannot rank two healthy bonds against
each other. That ranking needs the current source in phase 2.

---

## Step 5. Short and bridge screen (10 min per PCB)

Ω mode, 6 MΩ or 60 MΩ range locked. Everything here should read `OL`.

Per die on the south header:

| Pair | Nets | Detects |
|---|---|---|
| K_G to K_B | `LEDn_KG` - `LEDn_KB` | cathode bridge under the die |
| K_B to K_R | `LEDn_KB` - `LEDn_KR` | cathode bridge |
| K_G to K_R | `LEDn_KG` - `LEDn_KR` | cathode bridge |
| A to each K, both polarities | `LED_VCC` - `LEDn_K*` | shorted joint across the die |

Any reading below about 1 MΩ is a finding. A reading near 0 Ω between A and a K is a
hard short: that die is bridged or cracked. Exclude it from the step 4 V_F statistics
and flag it in the site map.

Note on polarity: in Ω mode the meter's test voltage is well below LED turn-on, so a
healthy LED reads `OL` in **both** directions. This is a shunt-path screen, not a
polarity test. Read nothing into the symmetry.

---

## Step 6. Reverse leakage screen (5 min per PCB)

Ω mode, 60 MΩ locked, reversed polarity across each `LEDn_A` to `LEDn_K*` pair.

Expect `OL`. A finite reading indicates a shunt path: a cracked die, ESD damage, or
contamination bridging the joint. The meter's test voltage is low, so treat a non-`OL`
reading as a definite finding and an `OL` reading as no information. Quantitative
reverse leakage needs a bias source and is a phase-2 item.

---

## Step 7. Daisy chains (samples 1 and 2 only)

### 7a. End-to-end screen (5 min per board)

Ω mode at 60 MΩ, and diode mode, across `PP_DCL6_IN` to `PP_DCL6_OUT`, then
`PP_DCL12_IN` to `PP_DCL12_OUT`. Also reachable at north pins 3/10 and 19/32.

**The healthy result is `OL`, in both modes, in both directions.** Six dice in series
need about 11 - 12 V to conduct and twelve need about 22 - 24 V; the meter sources a
fraction of that. This carries no information about bond quality.

What it does catch: a reading below roughly 1 kΩ means a solder bridge is shorting out
one or more dice. Log it, then localize it in 7b.

### 7b. Per-site diode V_F (30 - 45 min per board)

The only way to get per-site data out of the chains with a DMM, and it covers 18 of the
26 sites on each of samples 1 and 2.

For each chain die, probe its anode-side solder wing to its K_R-side wing. Record as
`DCL6-L03` style rows. Optionally also K_G and K_B, which are isolated per die on this
board even though the chain runs through red only.

Fine-probe work: needles, light pressure, microscope. Take two readings per site with a
lift-and-reland in between. If they disagree by more than a few mV, take a third and log
all of them.

Priority if time is short: all 6 sites of DC-A on both samples, then DC-B.

### 7c. What is out of reach

Chain forward I-V is the single most valuable measurement on this board and it is
completely inaccessible without a source. Four 9 V batteries in series and a 1 kΩ
resistor would unlock DC-A for a few euro; see `EQUIPMENT_DMM.md` section 7.

---

## Step 8. Close-out

- [ ] Re-measure the 100 Ω `R_EIS_LOAD` and log it as the final drift point
- [ ] Re-measure D1 red on the first board probed, and compare with the opening reading.
      That difference is your reproducibility and belongs in the write-up as an error bar
- [ ] Final NTC block logged
- [ ] Every `OL` and every anomaly has a photo
- [ ] `01_site_map.csv` complete for all 40 individual-die sites
- [ ] Photos backed up, boards in ESD bags, labelled

---

## Suggested order and time budget

### If the Arduino rig is being built (recommended)

About 3 h at the bench, then build the rig. Everything here is either a prerequisite or
not replaced by it.

| Order | Step | Scope | Time |
|---|---|---|---|
| 1 | Step 1 | once, plus the UNO 5 V rail and `R_EIS_LOAD` | 20 min |
| 2 | Step 0 | 76 sites, all samples | 45 - 60 min |
| 3 | Step 2 + probe-pad contact check | all 5 PCBs | 60 min |
| 4 | **Step 5** | **all 5 PCBs. The cathode-bridge case is invisible to the rig** | **50 min** |
| 5 | Step 3 | one block per board | 10 min |
| 6 | Step 4 | **one board only**, as ground truth | 20 min |
| 7 | Step 7a | samples 1 and 2 | 10 min |

Then build the rig. Steps 4 (remaining boards), 6 and 7b are superseded by it.

### If the rig is not being built, or as a fallback

Roughly 5 - 6 h for the full standalone session. The order degrades gracefully: stopping
after any numbered block still leaves a complete, comparable dataset.

| Order | Step | Scope | Time |
|---|---|---|---|
| 1 | Step 1 | once | 15 min |
| 2 | Step 0 | 76 sites, all samples | 45 - 60 min |
| 3 | Step 2 + 3 | per PCB | 60 min total |
| 4 | **Step 4** | **all 5 PCBs, red first, then G/B** | **100 min** |
| 5 | Step 5 | per PCB | 50 min |
| 6 | Step 6 | per PCB | 25 min |
| 7 | Step 7 | samples 1 and 2 only | 70 - 100 min |
| 8 | Step 8 | once | 15 min |

Do step 4 across **all** boards before starting step 7 on either of them. A complete
shallow pass over eight samples is a comparison; a deep pass over two samples is an
anecdote.
