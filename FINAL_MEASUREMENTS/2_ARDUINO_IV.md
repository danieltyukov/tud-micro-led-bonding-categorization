# Round 2: Arduino UNO current sweep

Hardware on the table: the 5 green PCBs, the Arduino **UNO** (not the Nano ESP32), a
breadboard, jumper wires, loose resistors and capacitors, and the multimeter for setup
only.

Do round 1 first. Its short-and-bridge screen catches a fault this rig cannot see: two
bridged cathodes split the drive current between two junctions, and the sweep comes back
looking perfectly normal.

Theory, error budget and the reasoning behind every choice: `../measurements/ARDUINO_IV_RIG.md`.

## What you end up with

A 63-point current-voltage curve for every channel, and from each curve a fitted series
resistance R_s to about ±10 mΩ. That turns "the bond works" into a number, so the 8
bonding conditions can be compared on a continuous scale instead of pass/fail.

---

## Parts to gather

| Part | Count | Use |
|---|---|---|
| 10 kΩ, 4.7 kΩ, 2.2 kΩ, 1 kΩ, 470 Ω, 220 Ω | 1 each | the current bank |
| 1 kΩ | 3 | series into the ADC pins |
| 100 nF | 3 | ADC pin to GND |
| 100 Ω metal film | 1 | the current sense resistor |
| 10 kΩ metal film | 1 | reverse leakage, step 7 |
| **Female-to-male** jumper wires | 4 or more | the board's headers are male pins, so the board end must be female |
| Male-to-male jumper wires | a handful | breadboard to UNO |

**Two fine probe needles or sharp grabber clips.** Optional for steps 1 - 6 (see "two
modes" below), but **required** for the 36 chain dice on boards 1 and 2. Those have no
header pins: the only way to reach one is to land on its own two solder edges. If you do
not have clips, sweep the 40 header-reachable dice and mark the chain dice as deferred.

---

## Two modes, one wire apart

**No-needle mode.** Everything through the header pins. The cathode trace and the pin
contact end up inside the measured resistance. Contact resistance is constant during a
sweep but changes each time you re-seat the jumper, which adds scatter between channels.
This is the default and it is fine for the bulk run.

**One-needle mode.** One ADC wire moves from the breadboard to a needle held on the die's
own gold probe pad in the LED row. That removes the cathode trace and pin contact
entirely. Use it on a handful of channels to measure how much no-needle mode costs you.

The wiring below is the same for both. Only the `A0` wire moves.

---

## Build

### The bank

Six resistors on the breadboard, one leg each into UNO pins **D2 - D7**, all other legs
into one common breadboard rail called **FORCE**.

```
  D2 ──[10k ]──┐
  D3 ──[4k7 ]──┤
  D4 ──[2k2 ]──┤
  D5 ──[1k  ]──┼── FORCE rail
  D6 ──[470 ]──┤
  D7 ──[220 ]──┘
```

### The loop

```
  FORCE rail ──F/M jumper──► south header, an A pin that is NOT the die under test
                             (use pin 1; use pin 5 when testing D1)

  south header, die's OWN A pin ──F/M jumper──► breadboard node ANODE_SENSE
  south header, die's K pin     ──F/M jumper──► breadboard node RETURN

  RETURN ──[100 Ω sense]── UNO GND

  ANODE_SENSE ──[1k]──► UNO A1      (+100 nF from A1 to GND)
  RETURN      ──[1k]──► UNO A2      (+100 nF from A2 to GND)
  RETURN      ──[1k]──► UNO A0      (+100 nF from A0 to GND)      <- no-needle mode
```

**One-needle mode:** move the `A0` wire off `RETURN` and onto a needle resting on that
die's own cathode probe pad, the gold square in the LED row (4th square in the die's group
for red). Nothing else changes.

**Why force and sense go to different A pins.** All eight A pins are one common copper bus.
Injecting at pin 1 and sensing at the die's own A pin leaves the bus voltage drop outside
the measurement. It is a free 4-wire connection on the anode side, no extra hardware.

UNO GND connects to the board **once**, through the sense resistor. Do not add a second
ground wire.

---

## Step 1. Calibrate the sense resistor against the board

The board carries a 100 Ω part with 0.1 % tolerance, marked **100R LOAD** in the EIS CAL
box. Use it to transfer accuracy onto your loose resistor, which removes the meter's own
gain error.

DMM to **Ω**, `600.0` locked, tips shorted, `REL Δ`.

1. Read the board's **100R LOAD**, call it `R_board`.
2. Read your loose 100 Ω, call it `R_ext`.
3. The true value is

```
                        100.0
   R_sense  =  R_ext × ─────────
                        R_board
```

Put `R_sense` into the sketch. Example: `R_board` = 100.2, `R_ext` = 99.4, so
`R_sense` = 99.4 × 100.0 / 100.2 = **99.20 Ω**.

Also read each of the six bank resistors and record them. They do not need to be accurate,
but knowing them tells you which currents to expect.

## Step 2. Measure the UNO's 5 V rail

DMM to **DC V**, `6 V` range. Red probe on the UNO's **5V** pin, black on **GND**.

Take it twice: once with the UNO idle, once with the rig actually sweeping at its highest
current. **Use the loaded number in the sketch.** This is a direct gain error on every R_s
you will extract. Re-measure it if you change USB cable or port.

## Step 3. Flash and verify on a plain resistor, before any die

Sketch: `../measurements/ARDUINO_IV_RIG.md` section 5. Set `R_SENSE` and `VCC` from steps
1 and 2. Serial at 115200.

Wire a **loose 100 Ω where the LED would be**: FORCE rail to one leg, other leg to
`RETURN`. `A1` on the FORCE-side leg, `A0` and `A2` on `RETURN`.

Run one sweep. Fit a straight line through voltage against current. **The slope must come
out at 100 Ω.** If it does not, something is wrong in the wiring, the reference, or the
`VCC` constant, and no LED data would be trustworthy.

Repeat this verification sweep at the start of every session.

Capture serial straight to a file:

```
stty -F /dev/ttyACM0 115200 raw -echo
cat /dev/ttyACM0 | tee R2_sweeps/verify_2026-08-12.csv
```

## Step 4. Self-heating check, on one channel, before the bulk run

Pick one healthy red channel. Sweep it three times, changing only `OVERSAMPLE` in the
sketch: **64**, then **256**, then **1024**. Fit R_s from each.

If R_s changes between them, the die is heating during the pulse and that heating is being
counted as resistance. Drop to the shortest setting whose R_s still agrees with the one
below it, and use that setting for every channel afterwards.

This is the check that decides whether the whole round is valid. Do not skip it.

## Step 5. Sweep every channel

For each die, for each of R, G, B: move the two F/M jumpers (own A pin, and the K pin),
run one sweep, save the serial output to its own file.

Filename convention, so nothing gets lost:

```
R2_sweeps/s<sample>_<die>_<channel>_seat<n>.csv
R2_sweeps/s1_D1_R_seat1.csv
R2_sweeps/s3_D2_G_seat1.csv
R2_sweeps/s1_DCL6-L01_R_seat1.csv
```

`seat` is which time you seated the jumpers. Re-seat and re-sweep **one reference channel
per board** a second and third time. That repeat scatter is your real error bar and it
cannot be recovered later if you do not collect it.

Skip any channel round 1 marked `short` or `open`. Note the skip rather than leaving a gap.

**Chain dice, boards 1 and 2.** These have no header pins. Replace the two F/M jumpers
with grabber clips on the die's own solder edges: anode-side edge to `ANODE_SENSE`,
cathode-side edge to `RETURN`. Everything else in the wiring is unchanged. 36 dice, red
channel only, and the clips make this slower and less repeatable than the header route, so
take two seatings on every one.

Log the four NTC resistances with the DMM every time you pick up a different board, same
as round 1 step 3.

Green and blue have about 3.0 V forward drop, so the bank tops out near 10 mA on them
instead of 17 mA. That is expected, not a fault.

## Step 6. The spread check, then decide

After the **first board only**, fit R_s for its channels and compute the standard deviation
of R_s within that sample, **separately for R, G and B**, excluding anything round 1
flagged as defective.

| Result | Meaning |
|---|---|
| spread much bigger than 10 mΩ | the dice themselves dominate, the rig is good enough, carry on |
| spread near 10 mΩ | the rig is the limit, and an SMU session is worth booking |

Record both numbers before continuing. They set what the whole campaign can resolve, and
they belong in the write-up as a stated sensitivity limit. Background:
`../measurements/DECISIONS.md` entry D1.

## Step 7. Reverse leakage, properly this time

Round 1 step 8 only told you `OL` or not-`OL`, which is nearly no information. This gets
you to about **10 nA**.

The UNO is used here only as a clean, regulated 5 V source. **The DMM is the meter**, not
the ADC: on its 600.0 mV range the DMM resolves 0.1 mV, and through a 10 kΩ that is 10 nA.
The ADC route would only reach about 100 nA, so do not use it.

Unplug the current bank first. Then:

```
  UNO 5V pin ──[ 10 kΩ ]──┬── die's CATHODE  (K pin on the south header)
                          │
                        DMM across the 10 kΩ, DC mV range
                          │
  UNO GND ─────────────── die's ANODE  (any A pin)
```

Note the polarity: 5 V to the **cathode**, ground to the **anode**. That reverse-biases
the die. Wire it the other way and you forward-bias it through a 10 kΩ, which will not
damage anything but gives a meaningless reading.

Per channel: wait about 5 s for the reading to settle, then record the millivolts.

```
  leakage current  =  reading in mV  /  10.0     gives microamps
```

1.0 mV means 100 nA. A healthy die should sit at a few tenths of a mV or less. Anything
above about 10 mV (1 µA) is a finding.

Do the red channel on every die, and G and B on any die round 1 flagged as suspect. Never
exceed 5 V reverse; the UNO rail is exactly at that limit, which is why no battery is used
here.

### Record: `R2_reverse.csv`

```
when,board_tag,sample,die,channel,r_bias_ohm,reading_mV,dmm_range,note
```

```
2026-08-12T15:02,1,1,D1,R,9970,0.2,600mV,
2026-08-12T15:04,1,1,D2,R,9970,14.6,600mV,about 1.5 uA, well above the rest
```

Send `reading_mV` and `r_bias_ohm` raw. Do not convert to current yourself.

---

## What to record

### `R2_rig.csv`

```
when,item,value,unit,how,note
```

`item` values: `r_board_100R`, `r_ext_100R`, `r_sense_computed`, `bank_10k`, `bank_4k7`,
`bank_2k2`, `bank_1k`, `bank_470`, `bank_220`, `vcc_idle`, `vcc_loaded`,
`verify_sweep_slope`

```
2026-08-12T10:00,r_board_100R,100.2,ohm,DMM 600R REL,EIS CAL box board tag 1
2026-08-12T10:02,r_ext_100R,99.4,ohm,DMM 600R REL,
2026-08-12T10:03,r_sense_computed,99.20,ohm,99.4*100.0/100.2,goes in the sketch
2026-08-12T10:10,vcc_loaded,4.981,V,DMM 6V on UNO 5V pin,rig sweeping at max current
2026-08-12T10:30,verify_sweep_slope,100.4,ohm,fit of loose 100R sweep,rig proven
```

### `R2_index.csv` — one row per sweep file

```
when,board_tag,sample,die,channel,mode,seat,file,oversample,cool_ms,vcc_used,r_sense_used,th1_ohm,th2_ohm,th3_ohm,th4_ohm,status,note
```

- `mode`: `no_needle` / `one_needle`
- `status`: `ok` / `skipped_short` / `skipped_open` / `bad_contact` / `redo`

```
2026-08-12T11:02,1,1,D1,R,no_needle,1,R2_sweeps/s1_D1_R_seat1.csv,256,250,4.981,99.20,10240,10190,10210,10230,ok,
2026-08-12T11:06,1,1,D1,R,no_needle,2,R2_sweeps/s1_D1_R_seat2.csv,256,250,4.981,99.20,10240,10190,10210,10230,ok,repeat for scatter
2026-08-12T11:20,3,3,D2,R,no_needle,1,,256,250,4.981,99.20,10180,10150,10160,10170,skipped_short,round 1 found KB-KR bridge
```

### `R2_selfheat.csv`

```
when,board_tag,sample,die,channel,oversample,file,note
```

```
2026-08-12T10:40,1,1,D1,R,64,R2_sweeps/heat_D1_R_os64.csv,
2026-08-12T10:45,1,1,D1,R,256,R2_sweeps/heat_D1_R_os256.csv,
2026-08-12T10:50,1,1,D1,R,1024,R2_sweeps/heat_D1_R_os1024.csv,
```

Do not fit these yourself. Send the three files and I will fit them.

### `R2_sweeps/*.csv`

Raw serial output, unedited. The sketch already writes the header line:

```
level,i_mA,v_die_V,v_anode_V,v_cath_V,v_sense_V
```

Keep the `#` comment lines. Do not delete points that look odd.

---

## Hand-off

| File | Content |
|---|---|
| `R2_rig.csv` | about 12 rows, plus one verify-sweep row per session |
| `R2_index.csv` | one row per sweep file, roughly 130 header-reachable plus up to 72 chain-die rows |
| `R2_selfheat.csv` | 3 rows |
| `R2_reverse.csv` | 40 rows, plus any G/B follow-ups |
| `R2_sweeps/` | the raw serial files |

Send it raw. No fitting, no averaging, no cleaning. The odd-looking points are often the
finding.

---

## Safety

- Wrist strap. Connect GND first, disconnect GND last.
- Current off before moving any jumper or probe. The sketch turns the bank off between
  points and after each sweep; do not defeat that.
- Never exceed 20 mA forward, never exceed 5 V reverse.
- Nothing above 5 V may reach an ADC pin. In this build nothing can, because the whole rig
  runs off the UNO's own rail. That stops being true the moment you add batteries for the
  daisy chains, which is a separate build with clamps
  (`../measurements/ARDUINO_IV_RIG.md` section 9).
