# Round 1 — do this

Read every value out to me. I write it into `../RESULTS/`. You write nothing.

Say `OL` when the meter says `OL`. Read digits exactly, trailing zeros included.
If you re-land and get a different number, give me both.

Pad locations: `board-probe-map.png`.
Background, if you ever want it: `../docs/datasheets/INSTRUMENTS.md`.

---

## Setup

- Black probe into `COM`.
- Red probe into the far right jack (`VΩHz`).
- Dial: from `OFF`, **4 clicks clockwise**. Land on the orange cluster at the top.
- Wrist strap on. Hold boards by the edges.

**Getting to a function (measured on your meter):**

Turning the dial one click away and back always lands on **resistance**. From there:

| Want | Presses of `SELECT` from resistance |
|---|---|
| resistance `Ω` | 0 |
| continuity (wifi icon) | 1 |
| diode | 2 |
| capacitance `nF` | 3 |

So whenever a step below says a function, first flick the dial off and back, then press
`SELECT` that many times.

Work through the boards in rotation, not one board at a time.

## Pin numbers (bottom black header)

| Die | A | K_G | K_B | K_R |
|---|---|---|---|---|
| D1 | 1 | 2 | 3 | 4 |
| D2 | 5 | 6 | 7 | 8 |
| D3 | 9 | 10 | 11 | 12 |
| D4 | 13 | 14 | 15 | 16 |
| D5 | 17 | 18 | 19 | 20 |
| D6 | 21 | 22 | 23 | 24 |
| D7 | 25 | 26 | 27 | 28 |
| D8 | 29 | 30 | 31 | 32 |

---

## Step 1 — meter check (once)

**1a**
- Touch the two probe tips together and hold.
- Press `RANGE` **once**.
- **Read out the number.**
- Press `REL Δ` **once**. Display goes to `0.0`.

**1b**
- Pull the tips apart, touch them together again. **Read out.**
- Do that **10 times**.

**1c**
- Touch the two ends of the small grey part marked `100R LOAD`. **Read out.**

**1d**
- Touch the two gold pads marked `SHORT`. **Read out.**

**1e**
- Press `REL Δ` **once**. REL indicator goes off.
- Hold `RANGE` for **2 seconds**. `AUTO` appears.
- Hold the probes apart in the air. Press `RANGE` **once**.
- Touch the two gold pads marked `OPEN`. **Read out.**

**1f**
- Flick the dial off and back. Press `SELECT` **twice** (diode).
- Touch the two ends of `100R LOAD`. **Read out.**

**1g** Every hour or so, and once at the very end, redo **1c** and **read out**.

---

## Step 2 — look at every die

No meter. Loupe or phone macro.

For every die on every board, **read out**:
- present: `y` or `n`
- alignment: `ok` / `shifted` / `rotated` / `tombstoned`
- solder: `ok` / `excess` / `starved` / `bridged`

Dice: D1 to D8 on all five boards. Plus on boards 1 and 2 only, the 6 dice in the left
chain and the 12 in the right chain, counting from the `IN` pad.

Photograph anything not `ok`. Save it in `../RESULTS/R1_photos/` and **read out the
filename**.

---

## Step 3 — temperature (once per board, and again after each break)

- Flick the dial off and back (lands on resistance).
- If REL is showing, press `REL Δ` once.
- Hold `RANGE` **2 seconds** until `AUTO` appears.
- Red probe on the gold square just left of `TH1`. Black probe on a small pad marked `GND`
  in a top corner.
- Press `RANGE` **once**.
- **Read out.**
- Move the red probe to `TH2`, then `TH3`, then `TH4`. **Read out each.**

---

## Step 4 — board check (each board)

- Flick the dial off and back. If REL is showing, press `REL Δ` once.
- Hold `RANGE` **2 seconds** until `AUTO`.
- Touch the tips together. Press `RANGE` **once**. Press `REL Δ` **once**.

**4a** Touch pin `4`, then D1's 4th gold pad. **Read out.**

- **Board 1 only:** repeat with pins `8, 12, 16, 20, 24, 28, 32` against D2 to D8's 4th
  gold pad. All eight.
- **Every other board:** just pin `4` and pin `32`. Two readings.

4b, 4c and 4d are done on **every** board.

**4b** Touch pin `1` and pin `29`. **Read out.**

**4c**
- Press `SELECT` **once** (continuity, wifi icon).
- Touch pin `1` to each of `5, 9, 13, 17, 21, 25, 29`. **Read out: beeps or not**, for each.
- Flick the dial off and back to return to resistance.

**4d**
- Hold `RANGE` **2 seconds**. Hold the probes apart in the air. Press `RANGE` **once**.
- Touch pin `2` and `3`. **Read out.**
- Touch pin `3` and `4`. **Read out.**
- Touch pin `4` and `5`. **Read out.**

---

## Step 5 — shorts (each board, each die)

Nothing to change on the meter. Still resistance, still locked on 60.00 MΩ from 4d.

**Three readings per die.** For D1, touch:

| Touch | and |
|---|---|
| pin 2 | pin 3 |
| pin 3 | pin 4 |
| pin 2 | pin 4 |

**For the next die, add 4 to every number.**

| Die | Pairs |
|---|---|
| D1 | **2-4 only** (2-3 and 3-4 already done in 4d) |
| D2 | 6-7, 7-8, 6-8 |
| D3 | 10-11, 11-12, 10-12 |
| D4 | 14-15, 15-16, 14-16 |
| D5 | 18-19, 19-20, 18-20 |
| D6 | 22-23, 23-24, 22-24 |
| D7 | 26-27, 27-28, 26-28 |
| D8 | 30-31, 31-32, 30-32 |

Every one should read `OL`. **Read out anything that shows a number** and tell me which pair.

Fastest way to report: work a whole board, then say "board 1 all OL", and call out only the
pairs that show a number.

Skip the three dice that are not there: board 1 D5, board 2 D7, board 5/6 D6.

---

## Step 6 — light up every channel (each board, each die)

- Flick the dial off the position and back. Press `SELECT` **twice** (diode).
- Turn the lights down so you can see the die glow.
- Backlight quits after 15 seconds. Long-press `HOLD` to bring it back.

**Use the four gold pads under each die, not the header pins.**

### First, find the anode. Once per board.

The silkscreen and netlist cannot be trusted for this. **Board 1's dice sit rotated 90°
from what the board says. Whether the other boards do too is unknown.**

On the first die of each board:

- Red probe on **pad 2**, black probe on each of pads 1, 3, 4 in turn.
- If all three light, pad 2 is the anode. That board matches board 1.
- If not, try red probe on **pad 1** instead, black on 2, 3, 4.
- Whichever pad lights all three is the anode. **Tell me which pad it was.**

Then note which colour appears on which pad, by watching the light.

Board 1 came out as: **pad 1 = red cathode, pad 2 = anode, pad 3 = green, pad 4 = blue.**

### Then, every die on that board

- **Red probe stays on the anode pad.**
- Black probe on each of the other three in turn.
- **Read out the number and `lit` or `dark`** for each, and say which colour lit.

Expect roughly 1.8-1.9 V on red, 2.6-2.8 V on green and blue.

Report like: `board 1 D1: 1.78 lit, 2.263 lit, 2.522 lit` for red, green, blue in that order.

If all three read `OL`: put both probes on that die's own two solder edges instead of the
pads, and **read out** what you get.

Skip board 1 D5, board 2 D7, board 5/6 D6.

---

## Step 7 — chains (boards 1 and 2 only)

**7a**
- Flick the dial off and back. Hold `RANGE` **2 seconds**. Hold the probes apart in the air.
  Press `RANGE` **once**.
- Touch the gold pad marked `IN` and the one marked `OUT` on the **left** chain.
  **Read out.** Swap the probes over. **Read out.**
- Same on the **right** chain. **Read out** both ways.

**7b**
- Press `SELECT` **twice** (diode).
- Put both probes on the two solder edges of the first chain die. **Read out.**
- Lift both probes, land them again. **Read out.**
- Do that for all 6 dice in the left chain and all 12 in the right chain, on both boards.

---

## Done

Tell me when every step is finished. Only then, tell me which bonding process each tag was.
