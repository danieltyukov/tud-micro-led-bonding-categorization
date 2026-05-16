# IEEE Xplore references — cited in the report

All accessible through the TU Delft proxy:
`https://ieeexplore-ieee-org.tudelft.idm.oclc.org/`

Login with NetID when prompted. Use the search snippet in each row to locate
and download the PDF; bibliographic data is already in `report/refs.bib`.

## Cited papers

### Micro-LED bonding (mechanical + electrical reliability)

1. **Yin, L., et al. (2024).** *Investigating the Performance and Reliability of Au-Sn Bonded Flip-Chip Micro-LEDs.* IEEE Transactions on Electron Devices, Vol. 71, Issue 3. 10 citations.
   - Search: `Au-Sn Bonded Flip-Chip Micro-LEDs Yin 2024`
   - Why it matters: direct comparator for our solder-paste-bonded boards; eutectic Au-Sn is the industry baseline.

2. **Wang, K., et al. (2023).** *Mechanical Properties of Flip-Chip Bonding Structures for Micro-LED Devices: Cu-Cu Bonding with Passivation Layer and Indium Bumps Bonding.* CSTIC 2023.
   - Search: `Mechanical Properties Flip-Chip Bonding Cu-Cu Indium Micro-LED Wang 2023`
   - Why it matters: shear strength + electrical resistance characterization workflow we will replicate (TLM + daisy-chain yield, plus push test).

3. **Ji, X., et al. (2022).** *Fabrication and Mechanical Properties Improvement of Micro Bumps for High-Resolution Micro-LED Display Application.* IEEE Transactions on Electron Devices, Vol. 69, Issue 7. 27 citations.
   - Search: `Fabrication Mechanical Properties Micro Bumps High-Resolution Ji 2022`
   - Why it matters: state-of-the-art reference for sub-10 µm bond pitch.

4. **Ji, L., et al. (2023).** *Polymer Reinforced Solder Paste for Improving Impact Energy Absorption Capability in Micro LED Laser-Assisted Mass Transfer.* SSLCHINA / IFWS 2023. 4 citations.
   - Search: `Polymer Reinforced Solder Paste Impact Energy Absorption Micro LED Ji 2023`
   - Why it matters: directly addresses solder-paste mixture characterization — our primary research target.

5. **Mani, A. A., et al. (2025).** *Mass Transfer Solution for Micro-LEDs Based Displays.* IEEE EPTC 2025.
   - Search: `Mass Transfer Solution Micro-LEDs Displays Mani 2025`
   - Why it matters: 2025 mass-transfer survey contextualizing our cleanroom workflow.

### V_F-TSP (forward-voltage thermal sensing parameter) thermometry

6. **Roscam Abbing, F. D., & Pertijs, M. A. P. (2011).** *Light-emitting diode junction-temperature sensing using differential voltage/current measurements.* IEEE SENSORS 2011. 8 citations.  
   **TU Delft authors** (Pertijs group, ECTM).
   - Search: `Light-emitting diode junction-temperature differential voltage current Pertijs 2011`
   - Why it matters: TU Delft house technique for V_F-TSP — the calibration procedure we follow on TH1-TH4.

7. **Della Corte, F. G., et al. (2020).** *Temperature Sensing Characteristics and Long Term Stability of Power LEDs Used for Voltage vs. Junction Temperature Measurements and Related Procedure.* IEEE Access, Vol. 8. 15 citations.
   - Search: `Temperature Sensing Characteristics Long Term Stability Power LEDs Voltage Della Corte 2020`
   - Why it matters: long-term V_F drift quantification — informs how often we recalibrate NTCs.

8. **Pangallo, G., et al. (2018).** *A Direct Junction Temperature Measurement Technique for Power LEDs.* IEEE AMPS 2018. 5 citations.
   - Search: `Direct Junction Temperature Measurement Power LEDs Pangallo 2018`
   - Why it matters: pulsed V_F measurement that avoids self-heating bias.

9. **Liu, Z. H., et al. (2019).** *A Continuous Rectangular-Wave Method for Junction Temperature Measurement of Light-Emitting Diodes.* IEEE Trans. Power Electronics, Vol. 34, Issue 11. 11 citations.
   - Search: `Continuous Rectangular-Wave Method Junction Temperature Light-Emitting Diodes Liu 2019`
   - Why it matters: continuous-mode V_F sensing — alternative to our pulsed protocol.

10. **Schwan, H., Schmid, M., & Elger, G. (2024).** *Layer Resolved Thermal Impedance Measurement with Laser Stimulated Transient Thermal Analysis of Semiconductor Modules.* THERMINIC 2024.
    - Search: `Layer Resolved Thermal Impedance Laser Transient Thermal Analysis Schwan 2024`
    - Why it matters: transient Z_th(t) deconvolution method we'll apply to extract bond-layer thermal resistance.

### Laser-Assisted Bonding (LAB) — alternative to reflow

11. **Choi, K. S., et al. (2021).** *Simultaneous Transfer and Bonding (SITRAB) Process for Micro-LEDs Using Laser-Assisted Bonding with Compression (LABC) Process and SITRAB Adhesive.* IEEE ECTC 2021. 13 citations.
    - Search: `Simultaneous Transfer Bonding SITRAB Micro-LEDs LABC Choi 2021`
    - Why it matters: LAB alternative whose electrical fingerprint is what we benchmark our reflow boards against.

12. **Fettke, M., et al. (2020).** *A study on laser-assisted bonding (LAB) and its influence on luminescence characteristics of blue and YAG phosphor encapsulated InGaN LEDs.* IEEE ECTC 2020. 10 citations.
    - Search: `laser-assisted bonding LAB luminescence InGaN LEDs Fettke 2020`
    - Why it matters: prior art linking bond process to V_F + radiometric drift.

### Project context (already in repo, not on IEEE Xplore)

13. **Abdelwahab, A., et al. (2025).** *[Title from ECTC 2025 paper].* IEEE ECTC 2025.
    - Local: `docs/ECTC-2025-published Ahmed Abdelwahab.pdf`
    - Why it matters: prior TU Delft v1 board that this v2 extends.

---

## How to download the PDFs

1. Open `https://ieeexplore-ieee-org.tudelft.idm.oclc.org/` in a browser.
2. Sign in with NetID + TU Delft password.
3. Paste one of the search strings above into the IEEE Xplore search bar.
4. Click the matching title → "PDF" button on the article page.
5. Save into `report/refs_pdf/` for offline reference (already gitignored — large binary).

The bibliographic entries are already wired into `report/refs.bib`, so the
LaTeX build resolves the citations even without the PDFs on disk.
