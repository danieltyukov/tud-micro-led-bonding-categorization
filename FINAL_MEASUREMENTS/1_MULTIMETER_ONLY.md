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
- Display should show `Ω`. If not, press `SELECT` until it does.
- Wrist strap on. Hold boards by the edges.

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
- Press `SELECT` until the **diode symbol** shows.
- Touch the two ends of `100R LOAD`. **Read out.**

**1g**
- Press `SELECT` four times. **Read out the order the four icons appear in.**

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

- Press `SELECT` until `Ω` shows.
- If REL is showing, press `REL Δ` once.
- Hold `RANGE` **2 seconds** until `AUTO` appears.
- Red probe on the gold square just left of `TH1`. Black probe on a small pad marked `GND`
  in a top corner.
- Press `RANGE` **once**.
- **Read out.**
- Move the red probe to `TH2`, then `TH3`, then `TH4`. **Read out each.**

---

## Step 4 — board check (each board)

- Press `SELECT` until `Ω`. If REL is showing, press `REL Δ` once.
- Hold `RANGE` **2 seconds** until `AUTO`.
- Touch the tips together. Press `RANGE` **once**. Press `REL Δ` **once**.

**4a** Touch pin `4`, then D1's 4th gold pad. **Read out.**
Repeat with pins `8, 12, 16, 20, 24, 28, 32` against D2 to D8's 4th gold pad.

**4b** Touch pin `1` and pin `29`. **Read out.**

**4c**
- Press `SELECT` **once** (sound-wave icon).
- Touch pin `1` to each of `5, 9, 13, 17, 21, 25, 29`. **Read out: beeps or not**, for each.
- Press `SELECT` until `Ω` again.

**4d**
- Hold `RANGE` **2 seconds**. Hold the probes apart in the air. Press `RANGE` **once**.
- Touch pin `2` and `3`. **Read out.**
- Touch pin `3` and `4`. **Read out.**
- Touch pin `4` and `5`. **Read out.**

---

## Step 5 — shorts (each board, each die)

Stay on `Ω`, locked at 60.00 MΩ from 4d.

For each die, using its four pins from the table above, **read out each**:
- K_G and K_B
- K_B and K_R
- K_G and K_R
- A and K_R, then swap the probes over and read again
- A and K_G, then swap and read again
- A and K_B, then swap and read again

---

## Step 6 — light up every channel (each board, each die)

- Press `SELECT` until the **diode symbol** shows.
- Turn the lights down so you can see the die glow.
- Backlight quits after 15 seconds. Long-press `HOLD` to bring it back.

For each die: red probe on its **A** pin, black probe on:
- **K_R** → **read out the number, and `lit` or `dark`**
- **K_G** → **read out the number, and `lit` or `dark`**
- **K_B** → **read out the number, and `lit` or `dark`**

If all three say `OL`: put both probes on that die's own two solder edges instead of the
header, and **read out** what you get.

---

## Step 7 — chains (boards 1 and 2 only)

**7a**
- Press `SELECT` until `Ω`. Hold `RANGE` **2 seconds**. Hold the probes apart in the air.
  Press `RANGE` **once**.
- Touch the gold pad marked `IN` and the one marked `OUT` on the **left** chain.
  **Read out.** Swap the probes over. **Read out.**
- Same on the **right** chain. **Read out** both ways.

**7b**
- Press `SELECT` until the **diode symbol**.
- Put both probes on the two solder edges of the first chain die. **Read out.**
- Lift both probes, land them again. **Read out.**
- Do that for all 6 dice in the left chain and all 12 in the right chain, on both boards.

---

## Done

Tell me when every step is finished. Only then, tell me which bonding process each tag was.
