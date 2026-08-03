# R1_photos

| File | Board tag | Samples |
|---|---|---|
| `2026-08-03_board1_overview.jpg` | 1 | 1 |
| `2026-08-03_board2_overview.jpg` | 2 | 2 |
| `2026-08-03_board3-4_overview.jpg` | 3/4 | 3 (D1-D4), 4 (D5-D8) |
| `2026-08-03_board5-6_overview.jpg` | 5/6 | 5 (D1-D4), 6 (D5-D8) |
| `2026-08-03_board7-8_overview.jpg` | 7/8 | 7 (D1-D4), 8 (D5-D8) |

Strips of the LED row, about 1600 x 350 each.

## Do not use these photos to decide whether a die is present

An attempt was made to read die presence from them. It got **two of three calls wrong**:

| Site | Photo said | Truth (physical board) |
|---|---|---|
| board 2, D7 | absent | **present** |
| board 5/6, D6 | present | **absent** |
| board 1, D5 | absent | not yet confirmed |

The failure mode is that at the zoom needed to resolve a 0.95 mm die against its pads,
these images are already blurred, and glare on a bare pad looks like a die while a dark
die looks like bare board. The two errors went in opposite directions, so there is no
correction to apply. The photo-derived presence data has been discarded.

**Presence, alignment and solder all come from the physical board.** These photos are
useful only as a record of what the boards looked like on the day, and for locating
features.

Anything worth documenting properly needs a microscope pass at roughly 20x, one frame per
die.

## Observation that does survive

Boards 5/6 and 7/8 show noticeably more white residue around the die sites than 1, 2 and
3/4. Consistent with flux. Not a defect on its own, but worth remembering if those four
samples read oddly.
