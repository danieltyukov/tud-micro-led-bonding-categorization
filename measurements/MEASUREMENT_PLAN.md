# Lab measurement plan - micro-LED bond characterization (v2 PCB, 2 boards)

Goal: extract per-bond electrical data from the two boards Ahmed assembled (same solder paste,
two different reflow processes) so the process types can be compared. You collect raw data per
this plan; analysis, simulation and formatting happen afterwards.

Board: tud-microled-v2, 93 x 93 mm, ENIG. LEDs: Wurth WL-SFCC 0404 RGB (150044M155220).
Nominal V_F at 10 mA: R ~ 2.0 V, G/B ~ 3.0 V. Chains run through the RED channel only (A -> K_R).

---

## 0. Deliverables (what you bring back)

1. `00_boards.csv` - board metadata (1 row per board)
2. `01_site_map.csv` - status of all 26 LED sites per board (1 row per site)
3. Sweep CSVs - one file per I-V sweep, named per section 8
4. `02_spot_log.csv` - every single-point measurement (1 row each)
5. Photos: each board whole, each chain, any anomaly (bridge, tombstone, missing LED)

Make a folder per board: `T1/`, `T2/`. Anything unusual goes in a `notes` column, never on paper only.

---

## 1. Equipment (TU Delft measurement lab)

| Item | Purpose |
|---|---|
| SMU, Keithley 2400/2450 or Keysight B290x class | All I-V. Must reach 35 V compliance for the N=12 chain |
| 6.5-digit bench DMM | Continuity, NTC resistance, spot checks |
| 4 Kelvin/mini-grabber leads + 2-4 needle probes (or probe station) | Probe pads are 1.27 mm ENIG squares |
| Stereo or USB microscope | Landing probes, joint inspection, photos |
| ESD wrist strap + mat | LEDs are ESD sensitive; wear it the whole session |
| Female 0.1" jumper wires or 32-pin ribbon | Plug directly onto the soldered south header |

## 2. Default instrument config

- Source CURRENT, measure voltage, for every LED measurement. Never source voltage
  forward across an LED without a current limit.
- 4-wire (remote sense) ON wherever the wiring supports it, autozero ON.
- NPLC 1 for sweeps, NPLC 10 for single spot readings.
- Room temp stable; log NTC (section 5) at the start of each measurement block.

Safe-limits card:

| Target | Source | Limit / compliance |
|---|---|---|
| Single LED channel, forward | 0 -> 10 mA sweep | 5 V compliance, 10 mA max |
| Chain N=6 (red) | 0 -> 10 mA sweep | 20 V compliance |
| Chain N=12 (red) | 0 -> 10 mA sweep | 35 V compliance |
| Any LED, reverse | -2 V (optional -5 V on suspects only) | 100 uA compliance |
| NTC (TH1-TH4) | DMM 2-wire ohms, or SMU 10 uA | 1 V |
| CAL resistor / strips / VDP | 1 mA (CAL), 100 mA (strips/VDP) | 1 V |

---

## 3. Board intake (10 min)

1. Confirm Ahmed's process labels. Name the boards `T1` and `T2`. Write the ID on the
   board edge (marker on soldermask, away from structures) and on its bag.
2. Fill `00_boards.csv`:
   `board_id, ahmed_label, process_desc, paste_type, reflow_method, assembly_date, notes`
3. Photograph each board top side fully, plus a close-up of each LED row and chain.

## 4. Setup verification on the 100 ohm CAL resistor (5 min, once)

The board has EIS CAL pads: OPEN pair, SHORT pair, and R_EIS_LOAD = 100 Ω 0.1%.

1. 4-wire, source 1 mA: measure LOAD. Expect 100.0 ± 0.2 Ω. If not, fix the Kelvin wiring
   before touching any LED.
2. Measure SHORT pair: expect < 50 mΩ (this is your residual lead/trace error).
3. Log both in `02_spot_log.csv`.

## 5. Temperature (2 min per block)

DMM across each NTC probe pad (PP_NTC1..4) to the GND pad (PP_GND1/2). Log all four raw
resistances (~10 kΩ at 25 °C, lower when warmer) in `02_spot_log.csv`. Repeat at the start of
each numbered section below and whenever the room or board changed. Conversion to °C happens in analysis.

## 6. Visual site map (15 min per board)

Under the microscope, for all 26 sites (D1-D8, DCL6_L1-L6, DCL12_L1-L12):

- Numbering convention: chain LEDs count from the IN pad side. L1 = nearest IN.
- Record in `01_site_map.csv`:
  `board_id, site, present(y/n), alignment(ok/shifted/rotated), solder(ok/excess/starved/bridged), notes`
- Photograph anything not "ok". A K_G-to-K_B bridge or a missing chain LED changes what you
  measure below, so this map comes first.

## 7. Continuity and short screen (10 min per board)

DMM continuity, gentle probing:

1. Each chain: IN pad to OUT pad. A diode chain reads OPEN to a DMM continuity beeper
   (that is normal); use DMM diode mode instead: it should show OL (12 chain) or conduct
   faintly; the real test is the SMU sweep. What you are screening for here is a hard SHORT
   (solder bridge across a die: reads < 100 Ω resistive both polarities).
2. On each individual LED D1-D8: check adjacent cathode pins on the south header for
   shorts (KG-KB, KB-KR). Any short: note in site map, skip that channel later.

## 8. Data file conventions

Sweep files: `{board}_{device}_{channel}_{test}.csv` with header `V,I`, e.g.
`T1_D3_G_fwd.csv`, `T2_DCL12_R_fwd.csv`, `T1_DCL6-L04_R_spot.csv`.
Devices: `D1..D8`, `DCL6`, `DCL12`, `DCL6-L01..`, `DCL12-L01..`, `CAL`, `STRIP1..`, `VDP0.25` etc.
Channels: `R`, `G`, `B` (omit for non-LED). Tests: `fwd`, `rev`, `spot`.

Spot log columns:
`timestamp, board_id, device, channel, test, source_A_or_V, measured_V_or_A, wires(2/4), T_ntc_ohm, notes`

If the SMU cannot export CSV to USB, photograph the screen AND type the numbers into the
spot log; for sweeps, use the lab PC (most benches have KickStart or a LabVIEW logger).

## 9. Chain I-V - the primary bond metric (20 min per board)

For DCL6 and DCL12 on each board:

1. Hookup: force HI on IN pad, force LO on OUT pad (mini-grabbers or needles). Sense HI/LO
   with separate needles on the same IN/OUT pads (two contacts per 1.27 mm pad is fine).
   Some north header pins are routed to the chain endpoints (marked with silk circles);
   you may use those for force AFTER verifying continuity pin-to-pad with the DMM.
2. Sweep 0 -> 10 mA, 51 points min (log spacing 10 uA -> 10 mA even better), compliance
   20 V (N=6) / 35 V (N=12). Save as `{board}_DCL6_R_fwd.csv` etc.
3. Immediately repeat once (checks contact stability; keep both files, suffix `_b`).
4. If the chain hits compliance at near-zero current: it is open (missing LED or open joint).
   Note it and go to section 10 to localize; still a result, not a failure.

## 10. Per-site V_F on chain LEDs (30-45 min per board)

This localizes bad joints and gives per-site statistics. For EACH chain LED, land two
needles on the exposed solder wings of that LED's own pads: anode-side wing and K_R-side wing.

1. Source 1 mA, NPLC 10, read V. Then 10 mA, read V. Log both as `spot` rows
   (device `DCL6-L03` style). V = die V_F + both bond joints.
2. Mandatory for every LED of an open or outlier chain; for healthy chains measure all
   sites anyway if time permits, else at least 3 sites per chain.
3. Optional bonus on suspect sites: G/B channels via the K_G/K_B pad wings (source 1 mA,
   compliance 5 V) - tests the other two bonds of the same die.

## 11. Individual LEDs D1-D8, all 3 channels (30 min per board)

The south header is pre-wired: each 4-pin block = one LED, order A, KG, KB, KR
(pins 1-4 = D1, 5-8 = D2, ... 29-32 = D8). All A pins are the common anode bus.

1. Hookup via jumper wires: force HI on the block's A pin, force LO on the channel's K pin.
   For Kelvin: sense HI on ANY OTHER A pin (they are all one net), sense LO stays 2-wire or
   goes to the LED's PP_Dn_K* probe pad with a needle.
2. Per LED, per channel (R, G, B): sweep 0 -> 10 mA, 51 pts, compliance 5 V.
   Save `{board}_D{n}_{R|G|B}_fwd.csv`. 24 sweeps per board; with the header this is fast.
3. On 2 LEDs per board (pick D1 and D8), also take a needle-probed 4-wire spot at 10 mA on
   the PP pads and log it - this quantifies the header lead error for the analysis.

## 12. Reverse leakage screen (10 min per board)

Per LED channel (D1-D8 minimum; chain sites only if suspect): source -2 V, compliance
100 uA, NPLC 10, read I. Log as `rev` spot rows. Healthy: well under 1 uA.
Only if a channel looks damaged, also record -5 V. Do not go beyond -5 V.

## 13. Solder-film QC structures (optional, 20 min per board, do if time remains)

Same paste and reflow as the LED joints, so they compare T1 vs T2 directly:

1. Sheet-R strips ("solder-paste sheet-R after reflow", lengths 2000/4000 um, widths per
   silk): 4-wire, source 100 mA, read V (expect only mV). Two needles each strip end.
   Log R per strip as spot rows, device `STRIP{n}` counted left to right.
2. VDP cloverleaves (W = 1.0/0.5/0.25/0.15 mm): 4 contacts each. Source 100 mA through two
   adjacent corners, read V across the other two; repeat rotated 90 degrees. Log both V/I.
   Skip the 0.15/0.25 mm ones if paste transfer visibly failed there (known stencil limit).
3. TLM ladders: 30 second job - DMM continuity across each finger gap. Expect OPEN (gaps
   are only bridged if solder flowed). Log any gap that conducts, with bank and finger.

## 14. Shutdown checklist

- [ ] Both boards: chain sweeps (4 files) + repeats
- [ ] Both boards: D1-D8 x RGB sweeps (48 files)
- [ ] Per-site chain spots logged, all outliers localized
- [ ] Reverse leakage logged
- [ ] Site maps + board metadata + spot log complete, NTC logged per block
- [ ] Photos backed up; boards back in ESD bags, labeled

Priority if time runs short, in order: section 9 (chains), 10 (per-site spots), 11 (D1-D8),
12 (reverse), 13 (QC structures).
