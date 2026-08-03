# measurements/photos

Reference photos for the lab sessions. Filenames are `YYYY-MM-DD_subject.jpg`.

| File | Date | What it shows |
|---|---|---|
| `2026-08-03_samples-01-08_overview.jpg` | 2026-08-03 | All 8 bonded samples on 5 v2 PCBs, laid out with paper number tags. Basis for `SAMPLES.md`. |
| `2026-08-03_dmm-thsinde-18B-plus.jpg` | 2026-08-03 | The digital multimeter available for phase 1. Basis for `EQUIPMENT_DMM.md`. |
| `2026-08-03_microcontrollers.jpg` | 2026-08-03 | Arduino UNO R3 (ATmega328P-PU) and Arduino Nano ESP32 (u-blox NORA-W106). Basis for `ARDUINO_IV_RIG.md`. The UNO is the one used; the Nano ESP32 is not suitable for the analog path. |

Notes on the overview photo:

- The handwritten purple marks are the sample numbers and, on PCBs C/D/E, the
  left/right divider line between the two bonding conditions on that PCB.
- Confirmed by the user, not readable from the photo: samples 1 and 2 (PCBs A and B)
  have D1 - D8 plus both daisy chains; samples 3 - 8 have **only** their four
  individual LEDs bonded, no chains. The DoE array, TLM ladders and Van der Pauw
  cloverleaves are bare ENIG on every board.
- Resolution is not sufficient to call per-site alignment or solder state. Do not use
  this photo as the site map. That comes from a microscope pass
  (`PHASE1_DMM_ONLY.md` step 0).

Photos to add as they are taken:

- One whole-board top shot per PCB, in focus, with the number tag in frame
- One close-up per LED daisy chain (DC-A N=6 and DC-B N=12)
- One close-up per anomaly (missing die, tombstone, bridge, shifted die), named
  `YYYY-MM-DD_<sample>_<site>_<anomaly>.jpg`
