# Arduino I-V rig: a real current sweep without a bench PSU

Photo: `photos/2026-08-03_microcontrollers.jpg`

Sits between `PHASE1_DMM_ONLY.md` (screening only) and `MEASUREMENT_PLAN.md` (bench PSU).
Built from an Arduino UNO, six resistors, a breadboard and jumper wires.

---

## 1. Why this beats the 9 V battery, and what it actually buys

The battery gives one or two operating points. That is not enough, and the reason is
worth stating precisely. An LED's forward characteristic is

```
  V(I)  =  V₀ + n·V_T·ln(I / I_s)  +  I·R_s
```

The first term is the diode's exponential; the second is the series resistance, which is
where the bond lives. Between 1 mA and 10 mA the exponential term alone contributes
n·V_T·ln(10) ≈ 0.12 V for n = 2, while I·R_s contributes about 0.05 V for R_s = 5 Ω.
**A two-point slope mixes them and reports neither.** You need enough points to fit and
separate them, which is exactly what a microcontroller gives you and a battery does not.

The standard separation, once you have a sweep:

```
   dV        n·V_T                    dV
  ────  =  ─────── + R_s     →    I·────  =  n·V_T + I·R_s
   dI          I                     dI
```

Plot I·(dV/dI) against I: the slope is R_s and the intercept is n·V_T. Or fit V(I)
directly by nonlinear least squares over all points, which is better conditioned.

| | 9 V battery + R | Arduino UNO rig |
|---|---|---|
| Points per channel | 1 - 2, by hand | 63, automatic |
| R_s extraction | impossible | yes, by fit |
| Self-heating control | none | pulsed, fixed duty cycle |
| 4-wire Kelvin sensing | needs 2 DMMs and 4 hands | native, 2 ADC channels |
| Time for 120 channels | days | about 4 h |
| Repeats and statistics | no | free |

## 2. Which board

**Use the UNO.** ATmega328P at 16 MHz, 5 V rail, 10-bit ADC.

**Do not use the Nano ESP32 in the measurement path.** Two reasons:

1. 3.3 V logic. A green or blue channel is V_F ≈ 3.0 V at 10 mA. After the current-sense
   drop there is no headroom left to push current through anything. Even red is marginal.
2. The ESP32-S3 ADC has substantial integral nonlinearity and a per-chip calibration
   curve. It is fine for reading a potentiometer, poor for a 0.1 % DC measurement.

Keep the Nano ESP32 for logging or wireless if you want it, driven over serial by the
UNO. It contributes nothing to the analog front end.

## 3. Resolution: what a 10-bit ADC can actually do here

Raw, a 10-bit ADC on a 5 V reference is 4.88 mV per LSB. Useless. Two techniques fix it.

**Oversampling.** Averaging 4ⁿ samples and right-shifting by n adds n effective bits,
provided there is at least 1 LSB of noise to act as dither, which a real circuit always
has (AVR121). 256 samples, shift 4, gives **14 effective bits**:

```
  5.0 V / 16384  =  0.305 mV effective LSB
```

**Set the ADC clock properly.** Arduino's default prescaler is /128, giving 125 kHz and
104 µs per conversion. 256 samples then take 27 ms, too long for a short pulse. Prescaler
/32 gives 500 kHz and 26 µs, so 256 samples take 6.7 ms. That is outside the datasheet's
50 - 200 kHz "maximum resolution" window, but with oversampling on top it is the better
trade. Verify empirically: sweep once at each prescaler and check R_s agrees.

### What that resolution means for the science

With R_sense = 100 Ω:

| Quantity | Resolution |
|---|---|
| Current | 0.305 mV / 100 Ω = **3 µA** (0.03 % at 10 mA) |
| V across the die | 0.43 mV (two channels subtracted, noise adds in quadrature) |
| R_total from a single point at 10 mA | 43 mΩ |
| **R_s from a 63-point fit** | **about ±10 mΩ, 1σ** |

That last number is the headline. A fit over the full sweep beats a single point by
roughly √N, and ±10 mΩ is genuinely at the scale of a solder bond.

**Read that as precision, not accuracy.** It is the statistical scatter of the fit.
Systematic errors are larger and are covered in section 7. For comparing eight samples
that is the right figure of merit, because systematics that are common to all samples
cancel in the comparison.

## 4. Circuit

### 4.1 Current source: a binary-weighted resistor bank on six pins

No op-amp, no transistor, no DAC. Six digital pins, each through a resistor, into the
common anode. A pin set to `OUTPUT`+`HIGH` sources current; set to `INPUT` it is
high-impedance and contributes nothing. 2⁶ − 1 = **63 distinct current levels**.

| Pin | Resistor | Approx. current (red, V_F ≈ 2.0 V) |
|---|---|---|
| D2 | 10 kΩ | 0.20 mA |
| D3 | 4.7 kΩ | 0.43 mA |
| D4 | 2.2 kΩ | 0.91 mA |
| D5 | 1 kΩ | 2.0 mA |
| D6 | 470 Ω | 4.3 mA |
| D7 | 220 Ω | 9.1 mA |

Currents assume 5 V minus V_F minus the 100 Ω sense drop. They do not need to be
accurate: **every point measures its own current.** The resistors only have to give a
spread of levels, so any E12 values you have will do.

Green and blue at V_F ≈ 3.0 V leave less headroom, so the same bank tops out around
10 mA instead of 17 mA. That is fine, 10 mA is the target anyway.

Pin loading: keep each pin under about 15 mA and the total under about 60 mA. The
ATmega328P absolute maximum is 40 mA per pin and 200 mA total, so this is comfortable.
The pin's own output impedance (roughly 25 Ω) sits in series with each resistor and
shifts the levels slightly, which does not matter since the current is measured.

*Upgrade, if you have one NPN transistor:* PWM on a timer at 62.5 kHz into an RC filter,
into the base of an emitter follower with an emitter resistor, gives a smoothly
programmable current sink with 8-bit control. More elegant, and it removes the headroom
tangle. The resistor bank needs no active parts and is the safer starting point.

### 4.2 Sensing: 4-wire Kelvin, using the board's own probe pads

This is the part that makes the measurement worth doing, and the v2 board was laid out
for it. Force current through the **south header pins**, sense voltage at the **Tier-1
probe pads** on the same nets. The 0.1 - 0.5 Ω of header trace, jumper wire and contact
resistance then sits outside the sense loop and disappears from the result. The ADC draws
essentially no current, so the sense wires carry no drop.

Three ADC channels:

| Channel | Connect to | Reads |
|---|---|---|
| `A1` | `PP_Dn_A` probe pad (y = 81, x = 8.5 + 10·(n−1)) | anode-side potential |
| `A0` | `PP_Dn_Kc` probe pad (K_R at x = 14.5 + 10·(n−1)) | cathode-side potential |
| `A2` | breadboard node at the top of R_sense | current |

```
  V_die  =  V(A1) − V(A0)                 (Kelvin, trace and contact excluded)
  I      =  V(A2) / R_sense
```

**A2 is separate from A0 on purpose.** A0 sits at the probe pad, upstream of the header
pin, the jumper wire and the contact. A2 sits directly across R_sense. Using A0 for the
current would fold all of those resistances back into the measurement and undo the
Kelvin arrangement.

### 4.3 R_sense: use the board's own 100 Ω

`R_EIS_LOAD` is a Yageo RT0603BRB07100RL, **100 Ω at 0.1 % tolerance**, already on the
board with probe access at (75.5, 35.39), nets `EIS_LOAD_A` / `EIS_LOAD_B`. It is on the
board precisely to be a calibration artefact. Wiring it into the return path makes the
current measurement traceable to 0.1 % with no calibration step of your own.

If you would rather keep the board's resistor out of the loop, use an external 1 % metal
film 100 Ω and measure it against `R_EIS_LOAD` with the DMM (REL-zeroed, both on the
600 Ω range, take the ratio). Do not trust a 2-wire DMM reading of a 100 Ω resistor to
better than about 0.5 % on its own.

### 4.4 Full wiring for one channel

```
  UNO D2 ──[10k ]──┐
  UNO D3 ──[4k7 ]──┤
  UNO D4 ──[2k2 ]──┤
  UNO D5 ──[1k  ]──┼──── H_S pin 4(n−1)+1     (anode, common LED_VCC net)
  UNO D6 ──[470 ]──┤
  UNO D7 ──[220 ]──┘

                        PP_Dn_A  ──[1k]──► A1      (+100 nF to GND)
                            │
                       [ die Dn, channel c ]
                            │
                        PP_Dn_Kc ──[1k]──► A0      (+100 nF to GND)
                            │
  H_S pin 4(n−1)+1+k ───────┴──┬──[ R_sense 100 Ω ]── UNO GND
                               │
                               └──[1k]──► A2       (+100 nF to GND)
```

The 1 kΩ series resistors and 100 nF caps on the ADC inputs are an anti-alias filter and
a little probe protection. 1 kΩ stays well inside the ATmega's 10 kΩ recommended source
impedance, so the sample-and-hold still settles. Allow ~1 ms after switching current
before reading, since 1 kΩ × 100 nF is a 100 µs time constant.

Connect the UNO GND to the board **once**. Do not create a second ground path.

### 4.5 Working through 24 channels per board

The anode is a common net, so the force side never moves. Plug a ribbon from the south
header to a breadboard; then for each channel you move **one jumper** (the cathode into
R_sense) and **two sense needles** (to that die's probe pads). 24 channels per PCB, about
2 min each including the sweep, so roughly 50 min per PCB and 4 h for all five.

## 5. Sketch

```cpp
// micro-LED bond characterization: I-V sweep rig
// Arduino UNO R3 (ATmega328P @ 16 MHz), 5 V AVCC reference
//
// Force : six binary-weighted resistors on D2..D7 -> common LED anode (H_S pin 4(n-1)+1)
// Sense : A1 = PP_Dn_A   (Kelvin, anode side)
//         A0 = PP_Dn_Kc  (Kelvin, cathode side)
//         A2 = top of R_sense on the breadboard  -> current
// Return: R_sense (100 ohm, 0.1 %) to UNO GND
//
// Output: CSV on serial at 115200. One block per channel, terminated by a blank line.

const uint8_t SRC_PIN[6] = {2, 3, 4, 5, 6, 7};   // 10k, 4k7, 2k2, 1k, 470, 220
const float   R_SENSE    = 100.00;               // ohm, from R_EIS_LOAD (0.1 %)
const float   VCC        = 5.000;                // MEASURE THIS WITH THE DMM AND EDIT IT
const uint16_t OVERSAMPLE = 256;                 // 4^4 -> +4 bits -> 14-bit effective
const uint8_t  SHIFT      = 4;
const uint16_t SETTLE_MS  = 2;                   // after switching current, before reading
const uint16_t COOL_MS    = 250;                 // current OFF between points, fixed

void setLevel(uint8_t mask) {
  for (uint8_t i = 0; i < 6; i++) {
    if (mask & (1 << i)) { pinMode(SRC_PIN[i], OUTPUT); digitalWrite(SRC_PIN[i], HIGH); }
    else                 { pinMode(SRC_PIN[i], INPUT); }   // high-Z, contributes nothing
  }
}

uint16_t adcOversampled(uint8_t ch) {
  uint32_t acc = 0;
  analogRead(ch);                                 // discard one, let the mux settle
  for (uint16_t i = 0; i < OVERSAMPLE; i++) acc += analogRead(ch);
  return (uint16_t)(acc >> SHIFT);                // 0..16368, 14-bit
}

float volts(uint16_t raw14) { return raw14 * (VCC / 16384.0f); }

void setup() {
  Serial.begin(115200);
  ADCSRA = (ADCSRA & ~0x07) | 0x05;               // ADC prescaler /32 -> 500 kHz
  setLevel(0);
  Serial.println(F("# set VCC in the sketch to the DMM-measured 5V rail before trusting V"));
}

void loop() {
  Serial.println(F("level,i_mA,v_die_V,v_anode_V,v_cath_V,v_sense_V"));

  for (uint8_t m = 1; m < 64; m++) {
    setLevel(m);
    delay(SETTLE_MS);
    uint16_t a = adcOversampled(A1);              // anode side
    uint16_t k = adcOversampled(A0);              // cathode side
    uint16_t s = adcOversampled(A2);              // current sense
    setLevel(0);                                  // current OFF immediately

    float vs = volts(s);
    float i  = vs / R_SENSE;
    float va = volts(a), vk = volts(k);

    Serial.print(m);              Serial.print(',');
    Serial.print(i * 1000.0, 4);  Serial.print(',');
    Serial.print(va - vk, 5);     Serial.print(',');
    Serial.print(va, 5);          Serial.print(',');
    Serial.print(vk, 5);          Serial.print(',');
    Serial.println(vs, 5);

    delay(COOL_MS);                               // fixed duty cycle, see section 7
  }

  setLevel(0);
  Serial.println();
  Serial.println(F("# sweep done - move to the next channel, then send any line"));
  while (!Serial.available()) { }
  while (Serial.available()) Serial.read();
}
```

Capture the serial output straight to a file, one per channel:

```
stty -F /dev/ttyACM0 115200 raw -echo
cat /dev/ttyACM0 | tee sweep_s3_D1_R.csv
```

## 6. What to do with the sweeps

### 6.1 Extract R_s

Per channel, fit over all 63 points:

```
  V(I)  =  V₀ + n·V_T·ln(I)  +  I·R_s
```

three free parameters (V₀, n, R_s), V_T = 25.85 mV at 27 °C. Report R_s with its standard
error. Cross-check with the linearized form: plot I·(dV/dI) against I, take the slope.
If the two disagree, the sweep has a problem, usually self-heating.

Then, per sample, the distribution of R_s across its channels. That distribution is the
comparison between the eight bonding conditions.

### 6.2 What R_s is and is not

It is

```
  R_s  =  R_die  +  R_bond_anode  +  R_bond_cathode  +  R_trace(sense loop)
```

`R_trace` is the copper between each probe pad and the die pad, about 25 mΩ total, a
fixed board constant identical on every sample, so it cancels in comparisons. `R_die` is
the LED's own internal series resistance, of order ohms, and it varies die to die. The
bonds are 10 - 100 mΩ.

So R_die dominates and this rig does **not** isolate a single bond. The argument that
makes the comparison valid is the one already in `new-pcb/ELECTRICAL_CHARACTERIZATION.md`:
all dice come from one reel, so R_die is a population with the same distribution on every
sample, and a shift in the *mean* R_s between samples is a shift in bond resistance.
That argument needs decent n per sample, which is the n = 4 problem from `SAMPLES.md`
section 3 all over again. It is strongest on samples 1 and 2.

### 6.3 The spread check: run this after the first board, before anything else

**Do this the moment the first board's 24 sweeps are fitted.** It decides whether an SMU
would change your results, and it takes minutes. It is the reversal condition for
decision D1 in `DECISIONS.md`.

Compute the **within-sample standard deviation of R_s** across that sample's channels,
per colour, excluding any channel already flagged as a defect in the phase-1 site map.

```
  sigma_within  =  stdev( R_s over the channels of one sample, one colour )
```

Compare it with the rig's own fit precision of about 10 mΩ:

| Result | Meaning | Action |
|---|---|---|
| `sigma_within` ≫ 10 mΩ (expect 10 - 100×) | The die population dominates. The instrument contributes nothing to the total, since the two add in quadrature: √(0.300² + 0.010²) = 0.3002 Ω. | **No SMU.** Decision D1 stands. Proceed with the Arduino for all 120 channels. |
| `sigma_within` comparable to 10 mΩ | The instrument is limiting. | **Book the SMU.** Its ±0.1 mΩ would genuinely buy resolution. |

Then compute what you can actually detect. At α = 0.05 and 80 % power the smallest
detectable difference in mean R_s is roughly 2.4·σ·√(2/n), and a bond change of Δ shows
up as 2Δ in R_s, so the smallest resolvable **bond** difference is about

```
  Δ_bond  ≈  1.2 · sigma_within        for n = 4   (samples 3 - 8)
  Δ_bond  ≈  0.4 · sigma_within        for n = 26  (samples 1 and 2)
```

Write these two numbers into the log before collecting the rest of the data. They tell
you in advance which comparisons the campaign can support, and they belong in the
write-up as a stated sensitivity limit rather than being discovered at analysis time.

Two caveats on interpreting `sigma_within`:

- It conflates die-to-die spread, bond-to-bond spread and measurement noise. You cannot
  separate them on a bonded LED. **If one sample's `sigma_within` is much larger than the
  others', that is itself a finding**: an inconsistent bonding process, which matters as
  much as a shifted mean.
- Compute it per colour. Red, green and blue are separate junctions in the same package
  with different V_F and different R_die, so pooling them inflates the spread for no
  reason.

Also verify self-heating here, not later: re-fit one channel from a 64× and a 1024×
oversampling sweep (section 7.1). If R_s moves between them, `sigma_within` is
contaminated and the whole check is invalid until the pulse length is fixed.

## 7. The error budget, honestly

Ordered by size. The first one is bigger than the effect you are chasing, so read it.

**7.1 Self-heating. This is the dominant error and it biases R_s directly.**

At 10 mA and 3 V the die dissipates 30 mW. For a 0404 package on a PCB pad, junction-to-
board thermal resistance is of order 200 K/W, so 30 mW is roughly 6 K of rise. With
dV_F/dT ≈ −2 mV/K that is −12 mV, over a current range of 10 mA, which looks exactly like
**−1.2 Ω of series resistance**. That is ten to a hundred times the bond you are trying
to measure, and it is not random: it scales with current, so it lands squarely on R_s.

Mitigations, in order of preference:

1. **Pulse, and keep the duty cycle identical for every measurement.** Current on only
   while reading, off for a fixed 250 ms after. The sketch does this. The bias does not
   vanish but becomes a common offset that cancels between samples.
2. **Keep the on-time short.** With prescaler /32 and 256× oversampling, three channels
   take about 20 ms. If R_s comes out suspiciously large, drop to 64× oversampling
   (5 ms total, one effective bit less) and see whether R_s falls. If it does, you were
   measuring heating.
3. **Cap the current at 10 mA.** Do not chase 20 mA points; they cost more in heating
   than they buy in fit leverage.
4. **For a golden subset, extrapolate to t = 0.** Take a series of readings during a
   longer pulse and extrapolate V back to the start of the pulse. This is the standard
   pulsed-V_F method and it removes the bias rather than balancing it.
5. **Log the NTCs** (`PP_NTC1..4`) before and after each board so ambient drift is
   separable from self-heating.

**Verification you must actually run:** sweep one channel at 64×, 256× and 1024×
oversampling. If the extracted R_s moves, heating is in your data and you have to fix it
before trusting anything.

**7.2 AVCC as the ADC reference.** The UNO's 5 V comes from USB or the onboard regulator:
typically ±1 to 5 % absolute, and it moves with load and with which cable you use. This is
a pure **gain error** on every voltage, hence on R_s.

- Measure AVCC with the DMM (DC V, 6 V range, 1 mV resolution) and put the number in the
  sketch. That pins it to the DMM's ~0.5 % absolute accuracy.
- Re-measure it whenever you change power source, and at the start of each session.
- Because it is a gain error common to all samples, it barely affects the comparison.
  It affects the absolute R_s you quote.
- The `readVcc()` bandgap trick can track AVCC in software, but the ATmega's 1.1 V
  bandgap is specified only to 1.0 - 1.2 V, so it needs its own one-time calibration
  against the DMM before it helps.

**7.3 Contact resistance drift at the sense needles.** Kelvin sensing removes contact
resistance from the *voltage*, but a bad contact raises the source impedance seen by the
ADC. Keep it well under 10 kΩ, which any metal-on-ENIG contact does. Not a real problem
here, unlike in the DMM-only phase where it dominated.

**7.4 R_sense tolerance.** 0.1 % if you use `R_EIS_LOAD`. Negligible.

**7.5 ADC nonlinearity.** ATmega328P INL is specified at ±0.5 LSB at 10 bits, i.e.
±2.4 mV. Oversampling averages noise, not INL. This is a smooth systematic across the
range, and it is identical for every sample, so it cancels in comparisons. It does put a
floor of a few mV on absolute V accuracy.

**7.6 Die-to-die spread of R_die.** Not an instrument error, but it is the statistical
floor on the science and it is larger than the instrument error. See section 6.

## 8. Reverse leakage, for free

Reverse the channel (drive the cathode, return the anode through R_sense) and use a
100 kΩ sense resistor instead of 100 Ω. Then 1 µA gives 100 mV, and the 0.305 mV
effective LSB corresponds to about 3 nA.

In practice the floor is the ATmega's ADC input leakage, so expect a usable resolution of
around **100 nA at 5 V reverse bias**. The bench-PSU plan targets 10 nA, so this gets you
within a decade of it for the price of one resistor. Note that 100 kΩ exceeds the
recommended 10 kΩ source impedance, so drop the 1 kΩ series resistor on that input and
allow a much longer settle (10 ms) before reading.

Never exceed 5 V reverse on these dice.

## 9. Daisy chains: a second build, samples 1 and 2 only

DC-A (N=6) needs about 12 V forward and DC-B (N=12) about 24 V. The 5 V rail cannot do
it, so the chains need an external rail: four 9 V batteries in series gives 36 V, which
covers both.

Changes from the single-LED rig:

- The resistor bank cannot switch 36 V from 5 V pins. Either switch by hand, or add a
  high-side MOSFET. Hand switching is fine, the sweep is slow anyway.
- **The anode-side sense node will sit at up to 30 V. It must go through a divider before
  the ADC.** A 10:1 divider (e.g. 90 kΩ / 10 kΩ) brings 30 V to 3 V. Use 0.1 % resistors
  or measure the ratio, since the divider ratio becomes a gain error.
- 90 kΩ source impedance is far outside the ADC's 10 kΩ recommendation. Buffer it, or
  scale the divider down (9 kΩ / 1 kΩ, which draws 3 mA, acceptable from a battery) and
  allow a long settle.
- The current-sense node stays near ground, so A2 needs no divider.
- **A probe slip that puts 36 V on an ADC pin destroys the ATmega.** Add a 10 kΩ series
  resistor and a 5.1 V Zener or a Schottky clamp to the 5 V rail on every divided input,
  and check the wiring twice before energising.

Do the individual LEDs first, get that dataset complete, and only then build this.

## 10. Handling

Everything in `EQUIPMENT_DMM.md` section 6 still applies, plus:

- **ESD.** You are now connecting ESD-sensitive dice to a USB-powered board. Wrist strap,
  connect GND first, disconnect GND last.
- **Current off while moving probes.** `setLevel(0)` before touching anything. The sketch
  leaves the current off between points and after each sweep, but a probe slip with the
  current on can inject a spike into a die.
- **Never exceed 20 mA forward or 5 V reverse.**
- Verify the rig on `R_EIS_LOAD` alone (no LED in the loop) before the first die sees
  current. Sweep it, fit a straight line, and check the slope comes out at 100 Ω. That
  proves force path, both sense paths, the ADC scaling and the VCC constant in one shot.
  Do this at the start of every session and log it, exactly as `04_meter_cal.csv` does for
  the DMM.

## 11. What this still cannot do

| Blocked | Why | Needs |
|---|---|---|
| Single-bond resistance in mΩ, isolated from R_die | R_die is ohms and dominates R_s | 4-wire on a die-free structure, or an SMU |
| Absolute R_s better than about 1 % | AVCC gain error, ADC INL | a precision voltage reference, or a calibrated SMU |
| Reverse leakage below ~100 nA | ADC input leakage | a bench PSU and the mV-across-10 kΩ method |
| V_F-TSP thermal characterization | no temperature control | a thermal chamber or hotplate |

None of that changes the conclusion: this rig turns "the bond is intact" into "R_s is
X ± 10 mΩ", across all 120 channels, in an afternoon. That is the step that makes the
eight bonding conditions comparable on a continuous scale.
