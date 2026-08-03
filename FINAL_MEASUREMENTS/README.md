# FINAL_MEASUREMENTS

Bench procedures, in order. Self-contained: everything you need at the table is here.

| File | Hardware needed |
|---|---|
| `1_MULTIMETER_ONLY.md` | the 5 boards and the Thsinde 18B+ multimeter |
| `2_ARDUINO_IV.md` | the above, plus Arduino UNO, breadboard, jumpers, resistors, caps, and grabber clips for the chain dice |
| `board-probe-map.png` | where to put the probes, referenced by both |

Do round 1 completely before round 2. Round 1's short-and-bridge screen catches a fault
the Arduino rig cannot see.

Raw data goes into `data/` as it is collected:

```
FINAL_MEASUREMENTS/
└── data/
    ├── R1_meter.csv
    ├── R1_board.csv
    ├── R1_temp.csv
    ├── R1_dies.csv
    ├── R1_channels.csv
    ├── R1_chain_ends.csv
    ├── R1_photos/
    ├── R2_rig.csv
    ├── R2_index.csv
    ├── R2_selfheat.csv
    ├── R2_reverse.csv
    └── R2_sweeps/
```

Hand the folder back raw. No fitting, no averaging, no dropped rows.

Background and reasoning live in `../measurements/`: `EQUIPMENT_DMM.md` (what the meter
can and cannot resolve), `SAMPLES.md` (which tag owns which die, and the n = 4 problem),
`ARDUINO_IV_RIG.md` (rig theory, the sketch, the error budget), `DECISIONS.md` (why no SMU
yet).
