# Measurement campaign decisions

Append-only. Newest first. One entry per decision that would otherwise get re-argued.

---

## D1. Do not book SMU time before the Arduino rig has run

**Date:** 2026-08-03
**Status:** accepted
**Scope:** the 8 bonded samples on the 5 v2 PCBs described in `SAMPLES.md`

### Decision

Build and run the Arduino UNO I-V rig (`ARDUINO_IV_RIG.md`) across all 120 channels
first. Do not book SMU or probe-station time for the main cross-sample comparison.

If SMU time is booked afterwards, book it **targeted**: the outliers the Arduino flags,
a golden reference subset for cross-validating the Arduino numbers, and the two chains
on samples 1 and 2. That is a half-day, not a week.

### Context

The available options were a handheld DMM (`EQUIPMENT_DMM.md`), an Arduino UNO rig built
from parts already on the bench, and a Keithley 2400-class SMU with the Summit 11K/12K
probe station recorded in `new-pcb/ELECTRICAL_CHARACTERIZATION.md:193`. Note that the
Summit is cited there as the instrument the ECTC 2025 paper used, not as confirmed TU
Delft access, so availability would have to be verified anyway.

### Rationale

**The SMU does not isolate the bond on these samples.** Every instrument measuring a
bonded LED sees

```
  R_s  =  R_die  +  R_bond_anode  +  R_bond_cathode  +  R_trace
```

R_die is of order ohms and varies die to die; the bonds are 10 - 100 mΩ. Nothing in a
Keithley removes R_die from that sum. Only a die-free structure does, and the TLM
ladders, Van der Pauw cloverleaves and DoE pads on these boards are bare ENIG with no
solder (`SAMPLES.md` section 2).

**Sample size, not resolution, is the binding constraint.** For a two-sample comparison
at α = 0.05 and 80 % power, the smallest detectable difference in mean R_s is
approximately 2.4·σ·√(2/n) at these small n. A change of Δ in mean bond resistance
appears as 2Δ in R_s, so:

| Sample | n dice | Smallest detectable bond difference |
|---|---|---|
| 3 - 8 | 4 | ≈ 1.2 × σ(R_s) |
| 1, 2 (8 individual + 18 chain) | 26 | ≈ 0.4 × σ(R_s) |

If σ(R_s) turns out to be 300 mΩ, a 50 mΩ bond difference is invisible at n = 4 with any
instrument. This is structural and no amount of instrument resolution fixes it.

**The instrument term is already far below the population term.** The Arduino rig
resolves R_s to about ±10 mΩ (1σ, from a 63-point fit). An SMU reaches about ±0.1 mΩ.
Both enter the comparison in quadrature with σ(R_s), which is expected to be hundreds of
mΩ. √(0.300² + 0.010²) = 0.3002 and √(0.300² + 0.0001²) = 0.3000. The upgrade moves
nothing.

**What the design does support well** is coarse categorization: a process that adds ohms,
produces opens, or leaves cracked joints is obvious at n = 4. That is a legitimate result
and is what "bonding categorization" reasonably means here.

### The rule that reverses this decision

After the first board's sweeps, compute the within-sample standard deviation of R_s
across its dice (`ARDUINO_IV_RIG.md` section 6.3):

- **σ ≫ 10 mΩ** (expected): the die population limits you. The SMU changes nothing for
  the comparison. Decision stands.
- **σ comparable to 10 mΩ**: the instrument limits you. Book the SMU.

This is measurable in about two hours and does not have to be guessed.

### What the SMU is still needed for

Four things, none of which is the main comparison:

1. **Pulsed measurement.** Self-heating is the dominant error and fakes roughly −1.2 Ω of
   series resistance (`ARDUINO_IV_RIG.md` section 7.1). The Arduino's shortest useful
   pulse is a few ms and can only hold the bias constant; a 2461 pulses to ~100 µs and
   removes it. This is the one genuine technical gap.
2. **The N=12 chain on samples 1 and 2**, which needs ~24 V compliance. The Arduino
   alternative is a 36 V battery stack with dividers and clamps, and a probe slip there
   destroys the ATmega.
3. **Reverse leakage below ~100 nA**, if bonding-induced die damage becomes a hypothesis.
4. **Publication credibility.** An ECTC-class reviewer expects a calibrated instrument.
   A documented Arduino rig with a 0.1 % reference-resistor check and a stated error
   budget is defensible, but it is a fight to be picked deliberately, not by default.
   The golden cross-validation subset exists to avoid having to pick it.

### Consequences

- Phase order becomes: DMM screen → Arduino sweeps → decide → targeted SMU if justified.
- The Arduino rig must produce a defensible error budget, since it may end up being the
  instrument of record. `ARDUINO_IV_RIG.md` section 7 is therefore not optional reading.
- The `R_EIS_LOAD` verification sweep at the start of every session is mandatory, since
  it is the only traceable calibration in the chain.

### Implication for a v3 board

The case for a full SMU campaign becomes strong again on a board where the bond can be
isolated from the die. Two changes would do it:

1. **Paste and reflow the TLM ladders and Van der Pauw cloverleaves**, so contact
   resistivity and sheet resistance are measurable at all.
2. **Restore dummy-die daisy chains alongside the LED chains.** Iteration 28 replaced the
   dummy-die chains with WL-SFCC LED chains (`new-pcb/V2_DESIGN_NOTES.md:154`). A metal
   dummy die has near-zero, low-variance resistance, so R_chain ≈ 2N·R_bond and the bond
   is the entire signal. With LEDs, R_die returns with all its variance and the advantage
   is lost. That swap bought optical go/no-go and cost the clean bond measurement.

3. **Put chains on every condition, and raise n per condition.** Samples 3 - 8 having only
   4 dice each is the single largest limitation of this campaign, and it is a layout and
   bonding-plan decision, not an instrument decision.
