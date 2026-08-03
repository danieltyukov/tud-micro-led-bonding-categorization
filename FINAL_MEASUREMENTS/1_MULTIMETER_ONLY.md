# Round 1: multimeter and boards only

Hardware on the table: the 5 green PCBs with paper tags 1 - 8, and the orange Thsinde
18B+ with its two probes. Nothing else.

Probe locations: `board-probe-map.png` in this folder. Every name below is printed on the
board silkscreen.

## What you end up with

One row per LED channel across all 5 boards saying pass, open or short, with a voltage on
each pass. Plus a visual record of every die, a temperature reading per board, and a
proven meter. That ranks the 8 bonding conditions on integrity and on how tightly their
voltages cluster.

---

## Before you start

Black probe in **COM**. Red probe in the **rightmost jack** (`VΩHz`). Leave them there all
day. Wrist strap on. Hold boards by the edges only.

**Which tag owns which die.** On the boards carrying two paper tags, the purple line down
the middle splits them: D1-D4 on the left belong to the odd tag, D5-D8 on the right belong
to the even tag. Boards 1 and 2 are a single condition each, whole board, and are the only
two with bonded daisy chains.

| Board tag(s) | Sample | Dice | Chains |
|---|---|---|---|
| 1 | 1 | D1 - D8 | both |
| 2 | 2 | D1 - D8 | both |
| 3 / 4 | 3 = D1-D4, 4 = D5-D8 | 4 each | none |
| 5 / 6 | 5 = D1-D4, 6 = D5-D8 | 4 each | none |
| 7 / 8 | 7 = D1-D4, 8 = D5-D8 | 4 each | none |

**South header pin numbering.** The bottom black strip. Numbers `1 5 10 15 20 25 30 32` are
printed above it. Each die owns 4 consecutive pins in the order **A, K_G, K_B, K_R**:

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

All eight A pins are one common wire.

**Write `OL` as the literal text `OL`.** Never as a number, never as blank. Blank means
"not measured yet" and the two must stay distinguishable.

---

## Step 1. Prove the meter, on the red box

Dial to **Ω**. Press `RANGE` until the display locks at `600.0`.

1. Touch the probe tips together. Note the raw number.
2. Press **`REL Δ`**. Display goes to `0.0`.
3. Lift and re-touch the tips **ten times**. Write down all ten readings.
4. Still zeroed, touch the two ends of the small grey part marked **100R LOAD**.
5. Touch the two gold pads marked **SHORT**.
6. Switch `RANGE` up to `60M` and touch the two gold pads marked **OPEN**. Must be `OL`.
   Anything else means the board is contaminated and every isolation reading on it is void.
7. Press `SELECT` to the diode symbol. Touch the **100R LOAD** ends again.
   **Reading ÷ 100 = your test current in amps.** `0.098` means 0.98 mA.
8. If you have any loose resistor around 10 kΩ, touch it in diode mode. That reading is the
   meter's ceiling voltage. `OL` means the ceiling is above what the display can show.

Repeat item 4 two or three times during the day and once at the end.

### Record: `R1_meter.csv`

```
when,item,dial,range,rel,reading,unit,note
```

- `item` values: `lead_zero_raw`, `lead_zero_rep` (ten rows), `load_100R`, `cal_short`,
  `cal_open`, `diode_across_100R`, `diode_across_10k`, `load_100R_drift`
- `rel`: `on` or `off`

```
2026-08-05T09:12,lead_zero_raw,ohm,600,off,0.34,ohm,before REL
2026-08-05T09:13,lead_zero_rep,ohm,600,on,0.1,ohm,rep 1 of 10
2026-08-05T09:20,load_100R,ohm,600,on,100.2,ohm,board tag 1
2026-08-05T09:23,cal_open,ohm,60M,off,OL,ohm,
2026-08-05T09:25,diode_across_100R,diode,auto,off,0.098,V,test current 0.98 mA
2026-08-05T14:40,load_100R_drift,ohm,600,on,100.3,ohm,end of session
```

---

## Step 2. Look at every die

No meter. Loupe or phone macro. 76 dice: D1 - D8 on all five boards (40), plus the 6-die
and 12-die chains on boards 1 and 2 (36).

For each: is a die present, is it square to the pads, does the solder look normal.
Photograph anything that is not `ok` and put the filename in the row.

Chain dice are numbered from the **IN** pad end. L1 is nearest IN.

### Record: `R1_dies.csv` (one row per die, 76 rows)

```
board_tag,sample,die,present,alignment,solder,iso_kg_kb,iso_kb_kr,iso_kg_kr,photo,note
```

- `die`: `D1`..`D8`, `DCL6-L01`..`L06`, `DCL12-L01`..`L12`
- `present`: `y` / `n`
- `alignment`: `ok` / `shifted` / `rotated` / `tombstoned`
- `solder`: `ok` / `excess` / `starved` / `bridged`
- the three `iso_*` columns stay blank now and get filled in step 5

```
1,1,D1,y,ok,ok,,,,,
3,3,D2,y,shifted,excess,,,,IMG_0412.jpg,visibly rotated ~10 deg
1,1,DCL6-L01,y,ok,ok,,,,,
```

---

## Step 3. Temperature

Dial to **Ω**, `RANGE` locked to `60.00k`, **REL off**.

Red probe on the gold square immediately left of **TH1**. Black probe on either small pad
marked **GND** in the top corners. Repeat for TH2, TH3, TH4. Expect roughly 10 kΩ.

Do this once every time you pick up a different board, and again if you take a long break.
Log raw ohms only. Do not convert to degrees.

### Record: `R1_temp.csv`

```
when,board_tag,th1_ohm,th2_ohm,th3_ohm,th4_ohm,room_note
```

```
2026-08-05T09:40,1,10240,10190,10210,10230,window closed
2026-08-05T10:35,3/4,10180,10150,10160,10170,after 1 h of handling
```

---

## Step 4. Prove the board, on the bottom header

Dial to **Ω**, `600.0` locked. Touch the tips together, press `REL Δ`.

1. Pin **4** to the 4th gold square in D1's group. Expect under 1 Ω. Repeat for a couple
   more dice on the first board, then spot-check two per board after that.
2. Pins **1, 5, 9, 13, 17, 21, 25, 29** should all be connected to each other. Beeper for
   the sweep, then one resistance reading pin 1 to pin 29.
3. Pins **2 - 3**, **3 - 4**, **4 - 5** on `60M`. All must be `OL`.

A failure here is the board, not a bond. Record it and stop trusting that pin.

### Record: `R1_board.csv`

```
board_tag,check,detail,dial,range,rel,reading,unit,verdict,note
```

- `check`: `pin_to_pad`, `anode_bus`, `adj_iso`
- `verdict`: `pass` / `fail`

```
1,pin_to_pad,pin4 to D1 4th gold pad,ohm,600,on,0.3,ohm,pass,
1,anode_bus,pin1 to pin29,ohm,600,on,0.2,ohm,pass,
1,anode_bus,beeper across pins 1/5/9/13/17/21/25/29,cont,-,on,beep,-,pass,all 8 continuous
1,adj_iso,pin4 to pin5,ohm,60M,off,OL,ohm,pass,
```

---

## Step 5. Find shorts

Dial to **Ω**, `RANGE` up to `60M`. **Everything here must read `OL`.**

Per die, using its 4 pins (A, K_G, K_B, K_R):

- **cathode pairs:** K_G-K_B, K_B-K_R, K_G-K_R. These go into `R1_dies.csv`.
- **A to each cathode**, then swap the probes and repeat. These go into
  `R1_channels.csv`.

Anything under about 1 MΩ is a finding. Near 0 Ω between A and a cathode means the die is
shorted; mark it and exclude that die from the averages later.

### Record

Cathode pairs into the three `iso_*` columns of `R1_dies.csv`. A-to-cathode into the
`iso_ak_fwd` and `iso_ak_rev` columns of `R1_channels.csv` (step 6 creates that file, so
either do step 6 first or create the rows now and fill `diode_V` after).

```
1,1,D1,y,ok,ok,OL,OL,OL,,
3,3,D2,y,shifted,excess,OL,0.4,OL,IMG_0412.jpg,KB to KR bridged
```

---

## Step 6. Light up every channel. This is the main measurement.

Dial to **diode**. Work in a darkened corner so you can see the die glow.

Red probe on the die's **A** pin, black probe on **K_G**, then **K_B**, then **K_R**. Hold
2 seconds before reading, every time, so the settle is consistent.

24 readings per board, **120 total**.

Reading it:

| What you see | What it means |
|---|---|
| all three `OL` | anode bond open, or no die |
| exactly one `OL` | that cathode bond open |
| near 0 V | shorted |
| green and blue `OL` on *every* die on *every* board | the meter's ceiling, not 80 failures |
| a plausible voltage but no light | a finding, write it down |

For a die reading `OL` on all three, put both probes on that die's own two solder edges
instead of the header. If it lights there, the fault is the board trace, not the bond.
Note that in the `note` column.

### Record: `R1_channels.csv` (one row per channel, 120 rows)

```
board_tag,sample,die,channel,pin_a,pin_k,diode_V,lit,iso_ak_fwd,iso_ak_rev,verdict,note
```

- `channel`: `R` / `G` / `B`
- `diode_V`: the number as displayed, or `OL`
- `lit`: `lit` / `dark`
- `verdict`: `pass` / `open` / `short` / `voc_limited`

```
1,1,D1,R,1,4,1.812,lit,OL,OL,pass,
1,1,D1,G,1,2,OL,dark,OL,OL,voc_limited,G and B OL on every die, meter ceiling
3,3,D2,R,5,8,0.003,dark,0.5,0.5,short,
5,5,D3,R,9,12,OL,dark,OL,OL,open,probed solder edges directly, still OL
```

---

## Step 7. Chains. Boards 1 and 2 only.

**Ends.** Dial to **Ω**, `60M`. Touch the gold pad marked **IN** and the one marked **OUT**
on the left chain (6 dice), then the right chain (12 dice). Swap probes and repeat.

`OL` both ways is the healthy answer and tells you nothing. Below about 1 kΩ means solder
is shorting out dice inside the chain.

**Per die.** Dial to **diode**. Put the two probes on the solder edges of one chain die at
a time: the anode-side edge and the red-cathode-side edge. 6 dice on the left, 12 on the
right, on each of boards 1 and 2. **36 sites reachable no other way.**

Take two readings per die, lifting and re-landing the probes in between. If they differ by
more than a few mV, take a third and record all of them.

### Record

Ends into `R1_chain_ends.csv`:

```
board_tag,sample,chain,range,reading_fwd,reading_rev,verdict,note
```

```
1,1,DC-A_N6,60M,OL,OL,pass,
1,1,DC-B_N12,60M,OL,OL,pass,
2,2,DC-A_N6,60M,340,350,short,bridge somewhere in the chain
```

Per-die readings into `R1_channels.csv`, same columns as step 6, with `die` set to
`DCL6-L03` style, `channel` = `R`, and `pin_a` / `pin_k` = `edge`:

```
1,1,DCL6-L01,R,edge,edge,1.834,lit,,,pass,reading 1 of 2
1,1,DCL6-L01,R,edge,edge,1.831,lit,,,pass,reading 2 of 2 after re-landing
```

---

## Step 8. Reverse

Dial to **Ω**, `60M`. Same A-to-cathode pairs as step 5, probes the other way round.

`OL` is expected. A finite reading is a definite finding. An `OL` tells you nothing, so do
not read a pass as evidence of low leakage.

### Record

The `iso_ak_rev` column of `R1_channels.csv`, already covered in step 5.

A quantitative version of this measurement, good to about 10 nA, is round 2 step 7. It
needs the UNO only as a 5 V source; the DMM is still the meter.

---

## Hand-off

Send back these six files:

| File | Rows |
|---|---|
| `R1_meter.csv` | about 20 |
| `R1_board.csv` | about 30 |
| `R1_temp.csv` | one per board visit |
| `R1_dies.csv` | 76 |
| `R1_channels.csv` | 120, plus 36 chain rows (72 if you take two readings each) |
| `R1_chain_ends.csv` | 4 |

Plus the photo folder. Do not pre-process, do not average, do not drop rows you think look
wrong. Send it raw with the notes intact.

## What round 1 cannot tell you

Bond resistance. At about 1 mA a 1 Ω joint adds 1 mV, so this separates intact from failed
and catches grossly resistive joints, but it cannot rank two healthy bonds against each
other. That is round 2.

Also not covered: driving the chains end to end, which is the only way to put all 12 or 24
bonds of a chain in one series path. It needs about 12 V and 24 V, so it needs a battery
stack. Deferred, see `../measurements/DECISIONS.md` entry D2.

When comparing samples, use the **spread of voltages within each sample**, not a pass rate.
Samples 3 - 8 have only 4 dice each, and 4 dice cannot support a percentage.
