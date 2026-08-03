# R1_photos

| File | Board tag | Samples |
|---|---|---|
| `2026-08-03_board1_overview.jpg` | 1 | 1 |
| `2026-08-03_board2_overview.jpg` | 2 | 2 |
| `2026-08-03_board3-4_overview.jpg` | 3/4 | 3 (D1-D4), 4 (D5-D8) |
| `2026-08-03_board5-6_overview.jpg` | 5/6 | 5 (D1-D4), 6 (D5-D8) |
| `2026-08-03_board7-8_overview.jpg` | 7/8 | 7 (D1-D4), 8 (D5-D8) |

Strips of the LED row, about 1600 x 350 each.

## What these photos can and cannot show

**Can:** flag *some* missing dice. Where a site is well lit and square to the camera, four
bare bond pads in a 2 x 2 are visible. Two were found that way.

**But the photo pass is not a census.** It found 2 of the 3 missing dice. Board 5/6 D6 was
called present from the photo and is actually absent; at the zoom needed to judge it, the
image is blurred past the point of reading. Presence must be confirmed on the physical
board, site by site. Treat the photos as a first cut only.

**Cannot:** alignment, tilt, rotation, or solder quality. At the magnification needed to
judge a 0.95 mm die's placement against its pads, these images are already blurred past
the point of reading. `alignment` and `solder` in `R1_dies.csv` are therefore left as
not-assessed rather than guessed.

Getting those columns needs a microscope pass, roughly 20x, one frame per die.

## Findings

- **Board 1, D5: die absent.** (found in photo)
- **Board 2, D7: die absent.** (found in photo)
- **Board 5/6, D6: die absent.** (found by eye on the board; photo pass missed it)
- Other 37 individual dice believed present, pending physical confirmation.
- Board 1 both chains populated, 6 and 12 dice counted.
- Boards 5/6 and 7/8 show noticeable white residue around most sites, consistent with
  flux. Not a defect on its own; worth a note if those samples read oddly.
