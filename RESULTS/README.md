# RESULTS

Live data from the round 1 bench session. **You do not write in these files. I do.**

Every row that can be known in advance is already filled in: board tag, sample number, die,
channel, which header pins to touch. The only empty cells are the ones that need a meter
reading.

Procedure: `../FINAL_MEASUREMENTS/1_MULTIMETER_ONLY.md`

---

## How to report a reading

Say the location and the number. Nothing else. Examples:

```
board 1, D3, red, 1.812, lit
board 1, D3, green, OL, dark
3/4 board, D6, blue, 2.71, lit
board 2, D1, pin 4 to pad, 0.3
lead zero rep 4, 0.1
TH1 through TH4 on board 1: 10240, 10190, 10210, 10230
```

Rules that matter:

- **Say `OL` when the meter says `OL`.** Never convert it to a number or skip it.
- Read the digits exactly as displayed, including trailing zeros. `1.810` and `1.81` are
  different pieces of information about the last digit.
- If you re-land a probe and get a different number, give me both. Do not pick one.
- Anything odd, say it in words. Bad contact, probe slipped, reading drifting, die looked
  wrong. It goes in the note column and it is often the finding.

You can report in any order and jump around between boards. Every row is addressable, so I
fill whichever one you name.

## Files

| File | Rows | Pre-filled | You supply |
|---|---:|---|---|
| `R1_meter.csv` | 19 | item, dial, range, REL state | the reading |
| `R1_board.csv` | 65 | board, check, which pins | the reading, pass/fail |
| `R1_temp.csv` | 5 | board tag | four NTC resistances per visit |
| `R1_dies.csv` | 76 | board, sample, die | present, alignment, solder, the three isolation readings |
| `R1_channels.csv` | 156 | board, sample, die, channel, both pin numbers | diode volts, lit/dark, two isolation readings |
| `R1_chain_ends.csv` | 4 | board, sample, chain | forward and reverse readings |

`R1_channels.csv` is the main one: **120 individual-die channels** across the five boards.
The 36 chain-die rows are present but marked `excluded`, see below.

## Daisy chains are excluded

The chains on boards 1 and 2 are **electrically dead by a board design fault**, not by any
bond failure. The dice sit rotated 90°, so the chain wiring joins each die's red cathode to
its blue cathode and leaves the anode floating. Every chain die is two back-to-back diodes
and no series path exists.

Measured: `OL` in resistance mode on all four chains, and 0 V under a torch where a working
6-die chain would have given 5-9 V. Full reasoning in `../measurements/DECISIONS.md` D3.

Samples 1 and 2 are therefore worth **7 and 6 dice**, not 25 and 24.

## Board 3/4 is contaminated

Heavy solder smear around the pads, not cleanable. Confirmed to cause shorts. Every row for
that board carries a flag.

Its readings characterise a **post-process contamination failure**, not the bond. Keep them
in the analysis as a process result, but exclude them from any V_F statistics, otherwise
they will poison the comparison between the other samples.

## Blind

Do not tell me which bonding process belongs to which tag until every reading is in. The
mapping gets joined on afterwards, by sample number.

## Timestamps

The `when` columns stay blank unless you say a time. Rough is fine, and it only matters for
correlating drift against the temperature log.
