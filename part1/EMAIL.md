**Subject:** ET4277 + ET4391 — Part 1 submission — micro-LED bonding characterization PCB

---

Dear professors,

Please find attached part 1 of my joint project for **ET4277 — Microelectronics Reliability** and **ET4391 — Advanced Microelectronics Packaging** (7 credits combined). The project extends the v1 board of A. Abdelwahab into a v2 platform for electrical characterization of solder-bonded micro-LEDs.

What has been completed in part 1:

- A 93 × 93 mm, two-layer FR-4 PCB (v4.0.7) carrying 26 Würth WL-SFCC 0404 RGB LEDs (8 addressable + 6 + 12 in two daisy chains), four NTCs for V_F-TSP thermometry, an EIS calibration block (OPEN / SHORT / 100 Ω LOAD reference), three TLM ladders, four van der Pauw cloverleaves, and a 6×6 DoE bond-pad array. The board is DRC clean (0 violations, 0 unconnected items) and fab-ready on the standard pool at either Aisler or Eurocircuits with ENIG plating.
- A single-sheet A2 KiCad schematic linked to the PCB by reference and footprint.
- A full set of fab outputs: gerbers + drill, pick-and-place CSV, Beagle-format BOM with verified manufacturer part numbers, top/bottom review PDFs, and the 3D STEP model.
- An IEEE-format report (4 pages, 9 references — including the TU Delft Pertijs group's V_F-TSP technique and the TU Delft / Heraeus polymer-paste paper).

**I have also completed the full safety training for EKL laboratory access, including both required lectures.**

Next step: I plan to place the order on **Monday with express shipping**, either through Aisler (Beagle assembly, ~€115–125 for 3 boards, 5–8 day standard turnaround) or through Eurocircuits (eC-stencil-mate or full SMT line, ~€135–160 for 3 boards, 3–5 day turnaround at TU Delft's traditional fab). Whichever fab is selected, the order will include the assembly option so the four NTCs, the reference resistor, and the 64 header pins are factory-soldered. The 26 LEDs are flagged as do-not-populate in the BOM and will be bonded in the EKL cleanroom under controlled paste, reflow, and die-bonder conditions. This split lets the prototype move faster while keeping the bond joint, the actual research subject, under proper control. The side-by-side comparison and the DNP instruction are in `FABRICATION_ORDER.md` inside the project zip.

For part 2 I will work alongside Ahmed at EKL on the pick-and-place machine for the LED bonding step, and (timeline permitting) carry out the electrical characterization runs described in Section VI of the report — the four-paste comparison across SAC305, SAC0307, Au-Sn eutectic, and the polymer-reinforced paste.

The submission folder includes the report PDF, the full KiCad project for inspection, the fab-ready order bundle (works for either Aisler or Eurocircuits), all four component datasheets, and the five reference papers cited in the report.

Best regards,

Daniel Tyukov  
Student no. 5714699  
ET4277 Microelectronics Reliability + ET4391 Advanced Microelectronics Packaging
