# Arduino I-V rig, build drawings

Offline copy of the build sheet for `../2_ARDUINO_IV.md`. Drawn hole for hole, so nothing
in it needs interpreting against the ASCII in the markdown.

| File | What it is |
|---|---|
| `build.pdf` | the whole sheet: both drawings, wiring tables, build order, capacitor sizing. 4 pages, 330 x 470 mm |
| `build.html` | same thing, opens in a browser with no network |
| `breadboard.pdf` / `.png` / `.svg` | the full rig, one page, native size. Print this for the bench |
| `closeup.pdf` / `.png` / `.svg` | the RETURN cluster and both rails at 2x |

Breadboard conventions used in the drawings:

- Rail holes follow the column numbers. First one under column 3, five in a row, a one-hole
  gap, five more. Columns 8, 14, 20 and 26 are gaps and have no rail hole.
- Bottom outer rail is FORCE, bottom inner rail is GND. Both top rails and the whole top
  half of the board stay empty.
- Only eight hole numbers matter: A4, C4, D4, E4 and A8, B8, D8, E8. Everything else is a
  rail, where any hole on the strip is the same node.

Regenerate from `gen.py` / `closeup.py` if the wiring changes; they emit the SVGs, and the
PDFs come from `rsvg-convert -f pdf` and headless Chrome respectively.
