# Round 2 — do this

Do round 1 first.

For single readings, read the value out to me. For sweeps, save the serial output to a file
and send me the file. I write everything into `../RESULTS/`. You write nothing.

Background if you ever want it: `../measurements/ARDUINO_IV_RIG.md`.

---

## Parts

| Part | Count |
|---|---|
| 10 kΩ, 4.7 kΩ, 2.2 kΩ, 1 kΩ, 470 Ω, 220 Ω | 1 each |
| 1 kΩ | 3 |
| 100 nF | 3 |
| 100 Ω metal film | 1 |
| 10 kΩ metal film | 1 |
| Female-to-male jumper wires | 4+ |
| Male-to-male jumper wires | a handful |

Arduino **UNO**, not the Nano ESP32.

## Pads and pins

Left to right under each die:

| Pad | Is | Header pin, die Dn |
|---|---|---|
| 1 | red cathode, **common to all 8 dice** | 4n−3 |
| 2 | anode | 4n−2 |
| 3 | green cathode | 4n−1 |
| 4 | blue cathode | 4n |

So D1 is pins 1,2,3,4 and D2 is 5,6,7,8, up to D8 at 29,30,31,32.

---

## Build

Six resistors, one leg each into UNO **D2-D7**, other legs all into one breadboard rail
called **FORCE**:

```
  D2 ──[10k ]──┐
  D3 ──[4k7 ]──┤
  D4 ──[2k2 ]──┤
  D5 ──[1k  ]──┼── FORCE
  D6 ──[470 ]──┤
  D7 ──[220 ]──┘
```

Then:

```
  FORCE ────F/M jumper────► die's ANODE pin (4n−2)

  die's CATHODE pin ────F/M jumper────► breadboard node RETURN
        red   = pin 4n−3
        green = pin 4n−1
        blue  = pin 4n

  RETURN ──[100 Ω]── UNO GND

  FORCE  ──[1k]──► UNO A1     (+100 nF A1 to GND)
  RETURN ──[1k]──► UNO A0     (+100 nF A0 to GND)
  RETURN ──[1k]──► UNO A2     (+100 nF A2 to GND)
```

UNO GND touches the board once, through the 100 Ω. No second ground wire.

---

## Step 1 — calibrate the sense resistor

DMM: dial 4 clicks clockwise from OFF, tips together, `RANGE` once, `REL Δ` once.

- Touch the two ends of `100R LOAD` on the board. **Read out.**
- Touch the two ends of your loose 100 Ω. **Read out.**
- Touch each of the six bank resistors. **Read out each.**

## Step 2 — measure the 5 V rail

DMM: dial **2 clicks** clockwise from OFF (DC volts). Leave on `AUTO`.

- Red probe on the UNO's `5V` pin, black on `GND`, USB plugged in. **Read out.**
- Repeat later with the rig sweeping at full current. **Read out.**

## Step 3 — verify the rig on a plain resistor

No LED in the loop yet.

- Put your loose 100 Ω where the die would be: `FORCE` to one leg, other leg to `RETURN`.
- Flash the sketch from `../measurements/ARDUINO_IV_RIG.md` section 5, with `R_SENSE` and
  `VCC` from steps 1 and 2.
- Capture the serial output:

```
stty -F /dev/ttyACM0 115200 raw -echo
cat /dev/ttyACM0 | tee verify.csv
```

- **Send me `verify.csv`.**

Do this at the start of every session.

## Step 4 — self-heating check

Pick one healthy red channel.

- Sweep it three times, changing only `OVERSAMPLE` in the sketch: **64**, then **256**,
  then **1024**.
- Save each to its own file: `heat_os64.csv`, `heat_os256.csv`, `heat_os1024.csv`.
- **Send me all three.**

Wait for my answer before step 5. It sets the `OVERSAMPLE` value you use for everything.

## Step 5 — sweep every channel

For each die, for each of red, green, blue:

- Move the two jumpers: `FORCE` to the anode pin, `RETURN` to that channel's cathode pin.
- Run one sweep.
- Save as `s<sample>_<die>_<channel>_seat1.csv`, e.g. `s1_D1_R_seat1.csv`.

Skip the four detached dice: board 1 D5, board 2 D1, board 2 D7, board 5/6 D8.

Re-seat and re-sweep **one channel per board** a second and third time, saving as
`_seat2` and `_seat3`.

Log the four NTC resistances with the DMM each time you pick up a different board, same as
round 1 step 3. **Read those out.**

Work through the boards in rotation, not one board at a time.

**Send me the files.**

## Step 6 — reverse leakage

Unplug the bank from `FORCE` first.

```
  UNO 5V ──[10 kΩ]──► die's CATHODE pin
  UNO GND ──────────► die's ANODE pin (4n−2)
```

DMM: dial 2 clicks clockwise from OFF (DC volts), `RANGE` until it shows `mV`.

- Probes across the 10 kΩ.
- Wait 5 seconds, then **read out the millivolts.**
- Red channel on every die. Green and blue only where round 1 flagged something.

---

## Done

Tell me when every step is finished. Only then, tell me which bonding process each tag was.
