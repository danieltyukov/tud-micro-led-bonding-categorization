# Instrument reference: what is documented, and what is not

Extracted 2026-08-03 for the measurement campaign in `FINAL_MEASUREMENTS/`.

---

## 1. Thsinde 18B+ digital multimeter

### Documentation status

A paper manual ships in the box. An independent reviewer describes it as "poorly written
and contains obvious errors". Nothing usable exists online: the page claiming to be a
manual (`manuals.plus/thsinde/...`) is AI-generated SEO filler carrying the Amazon listing
spec table plus invented reviews and a price, with no operating instructions at all.

**The gap is filled by an independent bench review**, saved here as
`Thsinde-18B-plus-Independent-Review-N8FDY.pdf` (Tom, N8FDY, v1.0, 12 Jun 2023). The
reviewer measured this exact model against a recently calibrated Keithley DMM6500 6.5-digit
bench meter and confirmed it meets its stated accuracy across DC volts, AC volts, current,
resistance and capacitance. It is the only source for the numbers that actually matter
here.

The Fluke 15B+/17B+/18B+ manual is stored as a cross-reference **only**. It is a different
instrument: 4000 counts rather than 6000, no NCV, no REL, no MAX/MIN, and it has a
dedicated LED TEST dial position the Thsinde does not. The Thsinde borrowed the model
number and the styling. Do not quote its specs as if they were this meter's.

### Measured characteristics (N8FDY review, the numbers that decide the plan)

| Parameter | Measured | Consequence for this campaign |
|---|---|---|
| **Diode open-circuit voltage** | **3.245 V** | **Above the forward voltage of red, green and blue.** All three channels give a reading in round 1 step 6. This was the single largest risk in the plan and it is resolved. |
| **Diode short-circuit current** | **1.49 mA** | every V_F recorded is at this current |
| Resistance test voltage, low range | 1.02 V | below LED turn-on, so a healthy LED reads `OL` in resistance mode in **both** directions. This is why the isolation screens are shunt-path tests, not polarity tests. |
| Resistance test voltage, medium / high range | 0.93 V / 0.50 V | same, further below turn-on |
| DC volts input impedance | 11 MΩ | |
| mV range input impedance | 20 MΩ | twice the typical for this class, so it will not load anything on this board |
| Current shunt burden, 10 A jack | 0.028 Ω | |
| Current shunt burden, mA jack | 1.57 Ω | |
| Current shunt burden, µA jack | 101.45 Ω | |
| Backlight timeout | 14.5 s | it drops out constantly while working in the dark for step 6 |
| AC volts 3 dB cutoff at 1 V | 3 kHz | irrelevant here, DC only |

Reviewer's caveats worth carrying: current accuracy below 10 µA is poor, capacitance below
10 nF is unusable, and there is **no third-party safety certification** despite the CAT IV
600 V marking. None of that affects this campaign, which is DC, above 10 µA, and under 5 V.

The reviewer also notes the knob beeps on every click and the meter beeps on every button
press.

### What is documented (Amazon listing spec table, confirmed 2026-08-03)

| Item | Value |
|---|---|
| Display | **6000 counts** |
| Power | single 9 V battery |
| Safety | CAT IV 600 V, 1000 V DC / 750 V AC max |
| True RMS | yes |

**DC voltage**, 5 ranges: 600 mV, 6 V, 60 V, 600 V at ±(0.5 % + 3); 1000 V at ±(0.8 % + 10)

**Resistance**, 6 ranges: 600 Ω at ±(0.8 % + 5); 6 kΩ, 60 kΩ, 600 kΩ, 6 MΩ at
±(0.8 % + 3); 60 MΩ at ±(1 % + 25)

**Current**, 5 ranges: 600 µA, 6000 µA at ±(0.8 % + 10); 60 mA, 600 mA, 10 A at
±(2 % + 30). Listing quotes AC only; DC assumed the same ranges via `SELECT`.

**Capacitance**, 6 ranges: 60 nF, 600 nF, 6 µF, 60 µF at (3.5 % + 20); 600 µF, 6000 µF at
±(5.0 % + 10)

**Frequency**: 10 Hz, 100 Hz, 1 kHz, 10 kHz, 100 kHz, 1 MHz, 20 MHz at ±(0.1 % + 3)

### Resolution per range, derived from 6000 counts

| Function | Range | Resolution |
|---|---|---|
| Ω | 600.0 Ω | **0.1 Ω** |
| Ω | 6.000 kΩ | 1 Ω |
| Ω | 60.00 kΩ | **10 Ω** |
| Ω | 600.0 kΩ | 100 Ω |
| Ω | 6.000 MΩ | 1 kΩ |
| Ω | 60.00 MΩ | 10 kΩ |
| DC V | 600.0 mV | **0.1 mV** |
| DC V | 6.000 V | 1 mV |
| DC V | 60.00 V | 10 mV |
| DC mA | 60.00 mA | 10 µA |
| DC µA | 600.0 µA | 0.1 µA |

### Still not documented, so confirm at the bench

- continuity beeper threshold (the Fluke 18B+ uses 70 Ω, for scale)
- auto power off delay
- the order in which `SELECT` cycles Ω / continuity / diode / capacitance
- whether `REL Δ` is exited by a second press or a long press

Each is answered in under a minute by pressing the button and watching the display, which
is why the bench doc tells you to read the icon rather than count presses. The diode
numbers, which used to be on this list and were the ones that mattered, are now measured
(see above) and re-confirmed in round 1 step 1f.

### Dial layout, read off the meter

`OFF` sits at the lower left. Turning clockwise, the pointer sweeps up the left side and
over the top. Ten positions:

`OFF` → `Hz ~V` → `▽` (DC V) → `mV` → **`Ω ·))) →⊢ ⊣⊢`** → `Hz%` → `A` → `mA` → `µA` → `NCV`

The resistance / continuity / diode / capacitance cluster is therefore **4 clicks clockwise
from OFF**, and it is the only position the round 1 procedure ever uses.

---

## 2. Arduino UNO R3 / ATmega328P

Real datasheets, both saved here:

- `Arduino-UNO-R3-Datasheet.pdf` (Arduino, 26 pp)
- `Microchip-ATmega328P-Datasheet.pdf` (Microchip 7810D-AVR-01/15, 294 pp)

### Absolute maximum ratings (ATmega328P, Absolute Maximum Ratings table)

| Limit | Value |
|---|---|
| DC current per I/O pin | **40.0 mA** |
| DC current VCC and GND pins | **200.0 mA** |
| **Maximum current per port** | **±30 mA** |
| Voltage on any pin except RESET | −0.5 V to VCC + 0.5 V |

**The ±30 mA per-port limit is the binding one for the current bank**, not the 40 mA
per-pin figure. Arduino pins D0 - D7 are all Port D, so a bank spread across D2 - D7 shares
one 30 mA budget. The bank specified in `ARDUINO_IV_RIG.md` draws about 13.7 mA total on a
red channel and 9.2 mA on blue, so it sits at under half the limit.

### ADC (ATmega328P section 23)

| Spec | Value |
|---|---|
| Resolution | 10-bit |
| Integral non-linearity | 0.5 LSB |
| Absolute accuracy | ±2 LSB |
| Conversion time | 65 - 260 µs |
| Max sample rate | 15 kSPS |
| Normal conversion | **13 ADC clock cycles** |
| First conversion after enabling ADC | **25 ADC clock cycles** |
| Sample-and-hold instant | 1.5 ADC clock cycles after conversion start |

Two quotes worth having exactly:

> "By default, the successive approximation circuitry requires an input clock frequency
> between 50kHz and 200kHz to get maximum resolution. If a lower resolution than 10 bits
> is needed, the input clock frequency to the ADC can be higher than 200kHz to get a
> higher sample rate."

> "The ADC is optimized for analog signals with an output impedance of approximately 10k
> or less."

The second is why the ADC input series resistors are 1 kΩ and not 100 kΩ.

### ADC prescaler, ADPS2:0 in ADCSRA

| ADPS2:0 | Divisor | ADC clock at 16 MHz | One conversion | 256 samples | Within 50-200 kHz? |
|---|---|---|---|---|---|
| 111 | 128 | 125 kHz | 104 µs | 26.6 ms | yes (Arduino default) |
| 110 | 64 | 250 kHz | 52 µs | 13.3 ms | marginally over |
| **101** | **32** | **500 kHz** | **26 µs** | **6.7 ms** | **no, reduced resolution** |
| 100 | 16 | 1 MHz | 13 µs | 3.3 ms | no |

Divisor table verbatim: 000 and 001 both give 2, 010 gives 4, 011 gives 8, 100 gives 16,
101 gives 32, 110 gives 64, 111 gives 128.

The rig runs at /32, deliberately outside the datasheet's maximum-resolution window. The
trade is explicit: raw per-sample resolution is degraded, but 256-sample oversampling
recovers more than that, and the shorter pulse matters more because self-heating is the
dominant error. The self-heating check in `2_ARDUINO_IV.md` step 4 is what validates the
trade for your dice.

### Bandgap reference

Electrical characteristics table: bandgap reference voltage at VCC = 5 V is **min 1.0 V,
typical 1.1 V, max 1.2 V**.

That is a ±10 % part-to-part spread, which is why the rig uses AVCC as the reference with
a DMM-measured value rather than the internal bandgap.

---

## Sources

- [Thsinde 18B+ listing page, manuals.plus](https://manuals.plus/thsinde/thsinde-18b-auto-ranging-digital-multimeter-user-manual)
- [Fluke 15B+/17B+/18B+ Users Manual](https://media.fluke.com/11f1df9e-b9f3-4e31-8144-b10800c110f6_original%20file.pdf)
- [Arduino UNO R3 datasheet](https://docs.arduino.cc/resources/datasheets/A000066-datasheet.pdf)
- [Microchip ATmega328P datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-7810-Automotive-Microcontrollers-ATmega328P_Datasheet.pdf)
