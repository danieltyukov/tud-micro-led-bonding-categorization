# Round 2 progress and what to measure next

Written by the analysis side. Operator does not edit this file.

## Immediate next action

**Put the 100 Ω dummy back and run the closing verify for board 3/4.**
FORCE rail to B4, both F/M jumpers off the PCB. This is outstanding and it blocks
the sample 4 result below. Boards 1 and 2 each closed at 98.4 and 98.6 Ω; board 3/4
has no closing bracket at all yet.

## Done

| board | samples | live channels | opens confirmed | verify open | verify close |
|---|---|---|---|---|---|
| 1 | s1 | 20 | 1 | pass | 98.398 Ω, −0.72 mV |
| 2 | s2 | 14 | 4 | — | 98.626 Ω, −0.78 mV |
| 3/4 | s3, s4 | 12 | 0 (11 skipped on R1 verdicts) | — | **MISSING** |

Rig constants in use: `R_SENSE = 98.61`, `VCC_DMM = 5.034`, `VBG_X1024 = 1110.70`,
`ADC_OFFSET = 0.0144`, `OVERSAMPLE = 64`.

## Red R_s so far, the only colour with physical fits

| sample | n | mean | sd |
|---|---|---|---|
| 1 | 6 | 10.770 Ω | 0.785 |
| 2 | 5 | 11.120 Ω | 0.344 |
| 3 | 1 | 10.918 Ω | — |
| 4 | 3 | **12.788 Ω** | 0.650 |

s1 vs s2 not significant (t = −0.92). **s1 vs s4 t = −3.81 and s2 vs s4 t = −4.87, both
significant.** Provisional until board 3/4 has a closing verify.

Green and blue are not usable for R_s: green fits at ideality 3.2–4.0, which is
unphysical, because the 5 V rail only gives a 20× current range at V_F ≈ 2.8 V.
Blue at 2.2–2.5 is borderline. Report red only.

## Board 5/6 — next board. 21 channels, all pass on R1

Sample 5 = D1–D4, sample 6 = D5–D8. **D8 is die_detached, skip all three of it.**
This is the cleanest board in the set and should give a full n = 4 on sample 5.

| sample | die | FORCE pin | RETURN R / G / B |
|---|---|---|---|
| 5 | D1 | 2 | 1 / 3 / 4 |
| 5 | D2 | 6 | 5 / 7 / 8 |
| 5 | D3 | 10 | 9 / 11 / 12 |
| 5 | D4 | 14 | 13 / 15 / 16 |
| 6 | D5 | 18 | 17 / 19 / 20 |
| 6 | D6 | 22 | 21 / 23 / 24 |
| 6 | D7 | 26 | 25 / 27 / 28 |
| 6 | D8 | — | detached, skip |

## Board 7/8 — last board. 22 channels

Sample 7 = D1–D4 (all 12 pass), sample 8 = D5–D8.
**Skip s8 D5 green and s8 D8 red, both shorts on R1 (0.002 V).**

| sample | die | FORCE pin | RETURN R / G / B |
|---|---|---|---|
| 7 | D1 | 2 | 1 / 3 / 4 |
| 7 | D2 | 6 | 5 / 7 / 8 |
| 7 | D3 | 10 | 9 / 11 / 12 |
| 7 | D4 | 14 | 13 / 15 / 16 |
| 8 | D5 | 18 | 17 / **skip G** / 20 |
| 8 | D6 | 22 | 21 / 23 / 24 |
| 8 | D7 | 26 | 25 / 27 / 28 |
| 8 | D8 | 30 | **skip R** / 31 / 32 |

Samples 7 and 8 will both give a full n = 4 on red. With 5, 6, 7, 8 complete you get
four samples at n = 4 and two at n = 5–6, which is the strongest the DoE can be.

## Still outstanding

- **NTC readings.** Never taken, for any board. Four per board, read with the DMM off
  the TH1–TH4 pads. They separate ambient drift from self-heating and cannot be
  reconstructed later. Take them before each board goes on the bench.
- **Seat repeats.** One channel per board re-seated and re-swept as `_seat2` and
  `_seat3`. None taken. This is what measures the F/M jumper and contact term, and
  after the 2.9 Ω link episode it is not optional.
- **Opening verify** for boards 2 and 3/4 was never run, only closing. From board 5/6
  on, run the dummy at both ends of every board.

## Known open items on the rig

- ~1.3 mV residual on red not fully accounted for.
- Green ideality unphysical, headroom limited, not fixable at 5 V.
- Link contact resistance 0.4–0.5 Ω, outside the measurement loops but a sign of
  worn sockets. C4 is where the cathode jumper lives.
- USB path ~2.8 Ω, rail sag 20–46 mV, divided out per point by the bandgap.
