# Sample inventory: 8 bonded samples on 5 v2 PCBs

Photo: `photos/2026-08-03_samples-01-08_overview.jpg`

Supersedes the "two boards" assumption in `MEASUREMENT_PLAN.md`.

---

## 1. What is bonded

| Sample | PCB | Region | Individual LEDs | Daisy chains | NTCs | Sites |
|---|---|---|---|---|---|---|
| 1 | A | whole board | D1 - D8 | DC-A (N=6) **and** DC-B (N=12) | TH1 - TH4 | 26 |
| 2 | B | whole board | D1 - D8 | DC-A (N=6) **and** DC-B (N=12) | TH1 - TH4 | 26 |
| 3 | C | left half | D1 - D4 | none bonded | TH1, TH2 | 4 |
| 4 | C | right half | D5 - D8 | none bonded | TH3, TH4 | 4 |
| 5 | D | left half | D1 - D4 | none bonded | TH1, TH2 | 4 |
| 6 | D | right half | D5 - D8 | none bonded | TH3, TH4 | 4 |
| 7 | E | left half | D1 - D4 | none bonded | TH1, TH2 | 4 |
| 8 | E | right half | D5 - D8 | none bonded | TH3, TH4 | 4 |

In the overview photo, top row left to right = PCB A (tag 1), PCB B (tag 2), PCB C
(tags 3 and 4). Bottom row left to right = PCB D (tags 5 and 6), PCB E (tags 7 and 8).

The split on PCBs C, D and E is the handwritten purple vertical line at the board
centreline, **x ≈ 46.5 mm**, which falls between D4 (x = 38.5 - 44.5 mm) and D5
(x = 48.5 - 54.5 mm). Confirmed: odd sample = left half, even sample = right half.

**Totals:** 40 bonded dice (8 + 8 + 6 × 4), plus 36 chain dice on samples 1 and 2
(18 each). 76 bonded sites, 304 bonds, since each WL-SFCC die has 4 bonds
(A, K_R, K_G, K_B).

## 2. Out of scope

The following structures are present on every PCB as **bare ENIG with no solder and no
dice**, so there is nothing on them to measure. They are excluded from the whole
measurement campaign, not just from phase 1:

- 6 × 6 BOND-PAD DoE array (each pad is an isolated single-terminal net anyway)
- TLM ladders, 3 banks × 7 fingers
- Van der Pauw cloverleaves, 4 cloverleaves

The `EIS CAL` block (OPEN pair, SHORT pair, 100 Ω 0.1 % `R_EIS_LOAD`) is **not** in this
list. It stays in scope as the meter calibration artefact, see `EQUIPMENT_DMM.md`
section 4.

## 3. Consequence for the study design

**The individual LED row is the only structure common to all 8 samples.** Everything
that compares the eight bonding conditions must be built on it. Samples 1 and 2 also
carry chains, which makes them richer but not more comparable.

| Comparison | Basis | n per sample |
|---|---|---|
| All 8 conditions | individual LEDs | 4 dice (samples 3-8), 8 dice (samples 1, 2) |
| Samples 1 vs 2 only | chains DC-A and DC-B | 18 additional dice each |

### The n = 4 problem, and what to do about it

Samples 3 - 8 have **4 dice each**, so 12 channels and 16 bonds. That is a small sample,
and binary metrics degrade badly at that size:

- Observing 12 out of 12 channels good establishes the true channel yield is above only
  about **78 %** at 95 % confidence.
- Bonds within one die are **not independent**: a shifted or tombstoned die takes
  several of its bonds down together. The effective sample size is closer to the 4 dice
  than to the 12 channels, which drops that bound to about **47 %**.

So a per-sample yield number from samples 3 - 8 will separate a catastrophic process
from a working one, and nothing finer. Do not report yield differences between two
samples that both come back clean.

**Prefer the continuous metric.** The V_F distribution per colour per sample uses all
12 channels as measurements rather than as trials, and a mean plus spread from n = 12 is
genuinely informative even when a yield from n = 4 is not. Phase 1 should lead with V_F
statistics and treat yield as the defect census that accompanies them.

Samples 1 and 2, with 8 individual dice plus 36 chain dice, are the only ones where a
yield number carries weight. They are also the only ones where chain data exists at all.

## 4. Process metadata, held back deliberately

The measurement campaign is run **blind**. The operator records everything against the
paper tag number and does not know which bonding process each tag is, until every reading
is taken. See `FINAL_MEASUREMENTS/1_MULTIMETER_ONLY.md`.

This is the right call. Probing is a manual, judgement-laden measurement: how long you
hold a needle, whether you re-land after an ugly reading, whether you record a marginal
value as `OL`. Expectations leak into all of it and the operator cannot feel it happening.
Blinding removes that channel at zero cost, because the mapping is joined on afterwards
by sample number.

The mapping still has to exist, and it has to be **locked before measurement, not
reconstructed from memory after**. Otherwise this is not a blind study, it is just missing
data. One row per sample, kept separately:

```
sample_id, pcb_id, half, lab_label, paste_type, paste_lot, die_finish,
mounting_method, mounting_pressure_MPa, reflow_profile_id, bonding_date,
operator, notes
```

Hand it over only once the readings are in.

---

## 5. Board reference: where to put the probes

All coordinates from `new-pcb/tud-microled-v2.kicad_pcb`, board 93 × 93 mm, origin at
the top-left as the board reads (title block at the top, mm ruler at the bottom).

### 5.1 South header `H_S` (y = 89 mm), pre-wired to all 32 LED signals

Pin 1 sits at x = 7.13 mm, pitch 2.54 mm, numbering increases left to right.

```
pin = 4·(n − 1) + k     for LED Dn, with k = 1:A, 2:K_G, 3:K_B, 4:K_R
```

| LED | A | K_G | K_B | K_R | Belongs to |
|---|---|---|---|---|---|
| D1 | 1 | 2 | 3 | 4 | left half (odd sample) |
| D2 | 5 | 6 | 7 | 8 | left half |
| D3 | 9 | 10 | 11 | 12 | left half |
| D4 | 13 | 14 | 15 | 16 | left half |
| D5 | 17 | 18 | 19 | 20 | right half (even sample) |
| D6 | 21 | 22 | 23 | 24 | right half |
| D7 | 25 | 26 | 27 | 28 | right half |
| D8 | 29 | 30 | 31 | 32 | right half |

On samples 1 and 2 the whole board is one condition, so all 8 belong to that sample.

All eight A pins are the **same net** `LED_VCC`, tied by a B.Cu bus at y = 85.5 mm.
Pins 1, 5, 9, 13, 17, 21, 25 and 29 are electrically one node. That is a feature (one
anode connection for everything) and a trap (you cannot isolate one anode bond from the
header alone; for that, probe the die's own anode pad wing).

**Note for the split boards:** the common anode bus runs across the centreline, so the
left and right halves of PCBs C, D and E share their anode connection even though they
are different bonding conditions. This does not corrupt anything, since the bus is
board copper rather than a bond, but it does mean an anode-side short on one half shows
up when probing the other.

### 5.2 North header `H_N` (y = 13.5 mm), 8 of 32 pins routed

Pin 1 at x = 7.13 mm, same pitch and direction. Routed pins carry silk circles.

| Pin | Net | Goes to | Relevant for |
|---|---|---|---|
| 3 | `DCL6_IN` | `PP_DCL6_IN` at (13.35, 72) | samples 1, 2 |
| 5 | `NTC1` | `PP_NTC1` at (15.2, 76.8), via B.Cu | all |
| 10 | `DCL6_OUT` | `PP_DCL6_OUT` at (30.65, 72) | samples 1, 2 |
| 13 | `NTC2` | `PP_NTC2` at (35.2, 76.8) | all |
| 19 | `DCL12_IN` | `PP_DCL12_IN` at (53.85, 72) | samples 1, 2 |
| 21 | `NTC3` | `PP_NTC3` at (55.2, 76.8) | all |
| 29 | `NTC4` | `PP_NTC4` at (75.2, 76.8) | all |
| 32 | `DCL12_OUT` | `PP_DCL12_OUT` at (86.15, 72) | samples 1, 2 |

The other 24 north pins have net names assigned in the pad but **no copper routed** to
them. They are jumper posts, not connections. Do not expect continuity from them.

### 5.3 Tier-1 probe pads (1.27 mm ENIG squares)

| Group | Location | Nets |
|---|---|---|
| LED anodes | y = 81, x = 8.5 + 10·(n−1) | `LED_VCC` (all common) |
| LED K_G | y = 81, x = 10.5 + 10·(n−1) | `LEDn_KG` |
| LED K_B | y = 81, x = 12.5 + 10·(n−1) | `LEDn_KB` |
| LED K_R | y = 81, x = 14.5 + 10·(n−1) | `LEDn_KR` |
| Chain ends | y = 72 | `DCL6_IN`/`OUT`, `DCL12_IN`/`OUT` |
| NTC | y = 76.8, x = 15.2 / 35.2 / 55.2 / 75.2 | `NTC1..4` |
| GND return | `PP_GND1` (4, 16), `PP_GND2` (88, 16) | `GND`, a B.Cu pour |
| EIS CAL | y = 35.39 | `EIS_OPEN_A/B` (44.5 / 47.5), `EIS_SHORT_A/B` (59.5 / 62.5), `R_EIS_LOAD` (75.5) |

### 5.4 Daisy chains (samples 1 and 2 only)

| Chain | Dice | Span | End probe pads | North pins |
|---|---|---|---|---|
| DC-A | 6 (`DCL6-L01` .. `L06`) | x = 13.35 to 30.65, y = 72 | `PP_DCL6_IN` / `PP_DCL6_OUT` | 3 / 10 |
| DC-B | 12 (`DCL12-L01` .. `L12`) | x = 53.85 to 86.15, y = 72 | `PP_DCL12_IN` / `PP_DCL12_OUT` | 19 / 32 |

Chains run through the RED channel only, anode to K_R, so DC-A puts 12 bonds in the
series path and DC-B puts 24. Chain LEDs are numbered from the IN pad side; L1 is
nearest IN.

`DCL6_J1..J5` and `DCL12_J1..J11` are the inter-die junctions. They are short traces
between adjacent LED pads with **no probe pads**. To reach a single chain site you must
land on that die's own exposed solder wings: the anode-side wing and the K_R-side wing.

Each chain die's K_G and K_B are isolated per LED (`DCL6_Ln_KG`, `DCL6_Ln_KB`, and the
DCL12 equivalents), so the green and blue bonds of a chain die can be probed directly
even though the chain itself only uses red.

### 5.5 NTC thermistors

TDK `NTCG104BH103HT1`, 10 kΩ ±3 % at 25 °C, **B(25/85) = 4100 K**. One terminal on `NTCn`, the other on
the `GND` B.Cu pour, which surfaces at `PP_GND1` and `PP_GND2`.

| NTC | x (mm) | Half |
|---|---|---|
| TH1 | 17.7 | left |
| TH2 | 37.7 | left |
| TH3 | 57.7 | right |
| TH4 | 77.7 | right |

On the split boards, log the two NTCs of the half you are measuring. On samples 1 and 2
log all four, which also gives the lateral thermal gradient across 93 mm.
