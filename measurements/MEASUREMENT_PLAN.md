# Lab measurement plan - micro-LED bond characterization (v2 PCB, 8 samples / 5 boards)
# Version: PSU + DMM (no SMU available)

> **Scope update (2026-08-03):** there are **8 bonded samples on 5 PCBs**, not 2 boards.
> See `SAMPLES.md`.
>
> - Samples 1 and 2 are whole boards: D1 - D8 plus both daisy chains (26 sites each).
> - Samples 3 - 8 sit two to a PCB, split at the x = 46.5 mm centreline, and have
>   **only D1 - D4 (odd) or D5 - D8 (even) bonded**. No chains.
> - Sections 9, 10 and 12's chain items therefore apply to samples 1 and 2 only.
> - The DoE bond-pad array, TLM ladders and Van der Pauw cloverleaves carry no solder
>   and no dice on any board. **Section 13 has been removed** and they are out of scope
>   for the whole campaign.
>
> This plan needs a bench PSU. For the session that runs with only the handheld DMM,
> see `PHASE1_DMM_ONLY.md` and `EQUIPMENT_DMM.md`.

Goal: extract per-bond electrical data from the two boards Ahmed assembled (same solder paste,
two different reflow processes) so the process types can be compared. You collect raw data per
this plan; analysis, simulation and formatting happen afterwards.

Board: tud-microled-v2, 93 x 93 mm, ENIG. LEDs: Wurth WL-SFCC 0404 RGB (150044M155220).
Nominal V_F at 10 mA: R ~ 2.0 V, G/B ~ 3.0 V. Chains run through the RED channel only (A -> K_R).

---

## 0. Deliverables (what you bring back)

1. `00_boards.csv` - board metadata (1 row per board)
2. `01_site_map.csv` - status of all 26 LED sites per board (1 row per site)
3. `02_data_log.csv` - EVERY electrical reading, one row per point (template in section 8)
4. Photos: each board whole, each chain, any anomaly (bridge, tombstone, missing LED)

Log into a laptop spreadsheet directly, one row per reading. No paper-only notes.

---

## 1. Equipment (confirmed available in the hall)

| Item | Role |
|---|---|
| Techtron SP304 (0-30 V, 4 A) | Main source. Analog meters = coarse indication only |
| Tektronix PWS2185 (0-18 V) | In series with the SP304 for the N=12 chain (48 V total); also the fixed 2 V source for reverse leakage |
| Fluke 177 (x2 if possible - borrow one from a neighboring bench) | DMM-V across the device; second one across R_series. Also ohms, diode mode, continuity |
| Escort ELC 2260 or Digimess RLC 200 (LCR meter, 4-wire Kelvin) | Series resistors, board CAL resistor, NTCs. PASSIVE only - never on an LED. RLC 200 DC V input can replace the second Fluke. Nice to have, not required now that the bare test structures are out of scope |
| Resistors | 1 kOhm (x2) and 10 kOhm, 1/4 W, any tolerance (their exact value gets measured, section 4) |
| Breadboard + wires | To build the series loop; female 0.1" jumpers to plug onto the board's south header |
| 2-4 needle probes or fine tweezers-probes | Probe pads are 1.27 mm; chain LED pad wings are smaller |
| Stereo or USB microscope | Landing probes, joint inspection, photos |
| ESD wrist strap | Wear the whole session |
| USB stick / laptop | For the log and photos |

NOT needed: TDS 2022B oscilloscope, AFG 3021B function generator. Farnell VC14 optional.

## 2. The measurement circuit (used for ALL LED points)

```
PSU (+) ---- R_series ----+---- [device anode side]
                          |          device
        Fluke B (V mode) reads V_R across R_series
                          |
PSU (-) ------------------+---- [device cathode side]

Fluke A (V mode) probes DIRECTLY across the device pads
```

- R_series makes the PSU a quasi current source.
- CURRENT IS READ AS VOLTAGE: I = V_R / R_series. Do NOT use the Fluke 177 mA jack -
  its 0.1 mA resolution is too coarse. Across a 1 kOhm resistor, 1 mA = 1.000 V, which
  the Fluke resolves to 0.1%.
- Fluke A reads V at the device, so lead/resistor drops do not pollute the reading.
- With only ONE meter: set the PSU, read V_R, move the meter to the device, read V_F,
  read V_R again to confirm it did not drift. Two meters = one step, so borrow one.
- To set a current: raise PSU voltage until V_R / R hits the target (within a few %),
  then record the honest pair (I, V). Exact setpoints do not matter.
- SP304 current knob: minimum + a small nudge (~backstop of tens of mA), always.
- Output OFF / voltage to zero while moving probes. Start every device at the lowest current.

| Target | R_series | PSU voltage needed | Max current |
|---|---|---|---|
| Single LED channel, forward | 1 kOhm | 0 -> ~13 V (SP304 alone) | 10 mA |
| Chain N=6 (red) | 1 kOhm | 0 -> ~25 V (SP304 alone) | 10 mA |
| Chain N=12 (red) | 1 kOhm | 0 -> ~40 V (SP304 + PWS2185 in series) | 10 mA |
| Any LED, reverse | 10 kOhm | 2 V fixed (5 V only on suspects) | ~200 uA worst case |

Never connect a PSU directly across an LED without the series resistor.
Series stacking: PWS2185 (+) into SP304 (-); the load sees SP304(+) to PWS2185(-).
Verify the stacked open-circuit voltage with the Fluke before first contact.

## 3. Board intake (10 min)

1. Confirm Ahmed's process labels. Name the boards `T1` and `T2`. Write the ID on the
   board edge (marker on soldermask, away from structures) and on its bag.
2. Fill `00_boards.csv`:
   `board_id, ahmed_label, process_desc, paste_type, reflow_method, assembly_date, notes`
3. Photograph each board top side fully, plus a close-up of each LED row and chain.

## 4. Rig verification (10 min, once)

1. Measure YOUR series resistors first: LCR meter 4-wire (R function, 100 Hz) on the
   1 kOhm and 10 kOhm. Write the exact values on tape on the breadboard and in the log.
   Every current in this session is computed from these numbers.
2. Board CAL pads (OPEN pair, SHORT pair, R_EIS_LOAD = 100 Ohm 0.1%): LCR 4-wire on the
   LOAD pads, expect 100.0 +/- 0.2 Ohm. Fluke 2-wire on the same pads: the difference is
   your lead offset for later. SHORT pair: log the residual mOhm-level value.
3. Build the section 2 loop with the CAL resistor as device: set ~1 mA (V_R ~ 1 V),
   check V_device/I = ~100 Ohm. This proves the whole rig before any LED sees current.
4. Log everything in `02_data_log.csv`.

## 5. Temperature (2 min per block)

Fluke ohms across each NTC probe pad (PP_NTC1..4) to the GND pad (PP_GND1/2). Log all four
raw resistances (~10 kOhm at 25 C, lower when warmer). Repeat at the start of each numbered
section below. Conversion to degrees C happens in analysis.

## 6. Visual site map (15 min per board)

Under the microscope. Samples 1 and 2: all 26 sites (D1-D8, DCL6_L1-L6, DCL12_L1-L12).
Samples 3-8: the 4 individual LEDs of that half only (D1-D4 odd, D5-D8 even). 76 sites
in total across the campaign.

- Numbering convention: chain LEDs count from the IN pad side. L1 = nearest IN.
- Record in `01_site_map.csv`:
  `board_id, site, present(y/n), alignment(ok/shifted/rotated), solder(ok/excess/starved/bridged), notes`
- Photograph anything not "ok". A K_G-to-K_B bridge or a missing chain LED changes what you
  measure below, so this map comes first.

## 7. Continuity and short screen (10 min per board)

Fluke, gentle probing:

1. Each chain, IN pad to OUT pad, resistance mode BOTH polarities: screening for a hard
   SHORT (solder bridge across a die: < 100 Ohm resistive both ways). A healthy diode
   chain reads OL / very high - that is normal.
2. Each individual LED D1-D8: check adjacent cathode pins on the south header for shorts
   (KG-KB, KB-KR). Any short: note in site map, skip that channel later.
3. DMM diode mode on each D1-D8 red channel (A pin to KR pin): should read ~1.8-2.1 V or
   OL if V_F exceeds the DMM test voltage; a reading near 0 V = shorted joint.

## 8. Data log format

Single file `02_data_log.csv`, one row per reading:

```
timestamp, board_id, device, channel, test, I_meas_mA, V_meas_V, T_ntc_ohm, notes
```

- Add a `sample_id` column (1-8) next to `board_id`; on PCBs C/D/E the board alone does
  not identify the condition.
- Devices: `D1..D8`, `DCL6`, `DCL12`, `DCL6-L01..`, `DCL12-L01..`, `CAL`.
- Channels: `R`, `G`, `B` (blank for non-LED). Tests: `fwd`, `rev`, `cont`, `ntc`.
- I = V_R / R_series (computed), V from the meter across the device. Log measured values,
  never the PSU setpoints. Logging V_R directly in the notes column is also fine.

## 9. Chain I-V, point by point (25 min per board) - SAMPLES 1 AND 2 ONLY

Chains exist only on samples 1 and 2. For DCL6 and DCL12 on those two boards, using the
section 2 loop:

1. Hookup: PSU/loop wires on the IN and OUT probe pads (grabbers or needles); voltmeter
   needles also on the IN/OUT pads (two contacts on a 1.27 mm pad is fine). Some north
   header pins are routed to the chain endpoints (marked with silk circles); usable for
   the force loop AFTER a continuity check pin-to-pad.
2. N=12 only: SP304 + PWS2185 in series (verify stacked voltage with the Fluke first).
3. Take points at approximately: 0.2, 0.5, 1, 2, 5, 8, 10 mA. Log each row.
4. Re-take the 10 mA point once after lifting and re-landing a probe (contact stability
   check; log both, note `repeat`).
5. If current stays ~0 with PSU voltage railed: chain is open (missing LED or open joint).
   Log it as `fwd, 0 mA at max V`, then localize in section 10. An open is a result.

## 10. Per-site V_F on chain LEDs (30-45 min per board) - SAMPLES 1 AND 2 ONLY

Localizes bad joints and gives per-site statistics. For EACH chain LED, land the loop +
voltmeter needles on the exposed solder wings of that LED's own pads: anode-side wing and
K_R-side wing. V = die V_F + both bond joints.

1. Two points per site: ~1 mA and ~10 mA. Log as `DCL6-L03` style rows.
2. Mandatory for every LED of an open or outlier chain; for healthy chains do all sites
   if time permits, else at least 3 sites per chain.
3. Optional on suspect sites: G/B channels via the K_G/K_B pad wings, ~1 mA point only -
   tests the other two bonds of the same die.

## 11. Individual LEDs D1-D8 (30-40 min per board) - THE PRIMARY DATASET

This is the only structure common to all 8 samples, so it carries the whole cross-sample
comparison. 40 dice: 8 on each of samples 1 and 2, 4 on each of samples 3-8.

The south header is pre-wired: each 4-pin block = one LED, order A, KG, KB, KR
(pins 1-4 = D1, 5-8 = D2, ... 29-32 = D8). All A pins are one common anode net.
On PCBs C/D/E, D1-D4 belong to the odd sample and D5-D8 to the even one.

1. Loop via jumper wires: PSU + R_series into the block's A pin, return from the channel's
   K pin. Voltmeter: easiest is the same header pins (adds ~0.1-0.3 Ohm of trace, fine for
   V_F); for the golden subset below, its needles go on the PP_Dn_A / PP_Dn_K* probe pads.
2. RED channel, every LED: points at 0.5, 1, 2, 5, 10 mA (5 rows per LED). Red matters
   most - it is the same channel the chains test.
3. GREEN and BLUE, every LED: points at 1 and 10 mA (2 rows per channel). Densify to the
   full 5 points if you are ahead of schedule.
4. Golden subset: on D1 and D8 of each board, repeat the 10 mA red point with DMM2 on the
   probe pads (true Kelvin) - quantifies the header-path error for analysis.

## 12. Reverse leakage screen (10 min per board)

Swap R_series to 10 kOhm, reverse the device connection, PWS2185 at 2.0 V. Read leakage as
mV across the 10 kOhm (Fluke mV range): 1 uA = 10 mV, resolvable down to ~10 nA.

1. Per LED channel on D1-D8: log V_R (compute I) after ~5 s settle. Healthy: well under
   1 uA, i.e. under 10 mV.
2. Chain sites (samples 1 and 2): only the suspects from sections 9-10.
3. Only if a channel already looks damaged, also record a 5 V point. Never beyond 5 V.

## 13. Removed

Was "Solder-film QC structures" (sheet-R strips, Van der Pauw, TLM ladders). Those
structures carry no solder and no dice on any of the five PCBs, so there is nothing to
measure on them. Out of scope for the whole campaign. See `SAMPLES.md` section 2.

## 14. Shutdown checklist

- [ ] CAL rig check logged (section 4)
- [ ] All 5 PCBs: D1-D8 red 5-point sets, G/B 2-point sets, golden subset (section 11)
- [ ] Samples 1 and 2: chain point sets, DCL6 + DCL12, with repeats (section 9)
- [ ] Samples 1 and 2: per-site chain points logged, all outliers localized (section 10)
- [ ] Reverse leakage logged (section 12)
- [ ] Site maps complete, NTC logged per block. Process metadata (`00_samples.csv`) stays
      withheld until all readings are in, see `SAMPLES.md` section 4
- [ ] Photos backed up; boards back in ESD bags, labeled

Priority if time runs short, in order: section 11 (D1-D8 across all 8 samples, this is
the cross-sample comparison and nothing replaces it), then 9 and 10 (chains, samples 1
and 2), then 12 (reverse).
