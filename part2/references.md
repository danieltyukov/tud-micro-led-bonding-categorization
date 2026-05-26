# Part 2 — References (micro-LED bonding, capillary self-alignment, die tilt)

All IEEE links go through the TU Delft proxy (`ieeexplore-ieee-org.tudelft.idm.oclc.org`) so they open directly with library access. Verified to exist on IEEE Xplore on 2026-05-26.

## Already downloaded (shared by Ahmed, in `RE_ PCB Design for electrical tests/`)

1. **J. Berthier, K. A. Brakke, S. Mermoz, C. Frétigny, L. Di Cioccio**, "Stabilization of the tilt motion during capillary self-alignment of rectangular chips," *Sensors and Actuators A: Physical*, vol. 234, pp. 180–187, 2015. DOI: 10.1016/j.sna.2015.09.008
   - The key tilt reference: of the four CSA displacement modes (shift, twist, lift, tilt), only **tilt is non-restoring/unstable**; tilting can trigger direct chip–pad contact that jams alignment. Shows an LED-on-solder tilt example. Stabilized by lyophilic bands patterned on the substrate.

2. **V. Vareilles et al.**, "Experimental and Simulative Correlations of the Influence of Solder Volume and Receptor Size on the Capillary Self-Alignment of Micro Solar Cells," *J. Microelectromechanical Systems*, vol. 33, no. 2, pp. 290–xxx, Apr. 2024. DOI: 10.1109/JMEMS.2024.3352396
   - IEEE: https://ieeexplore-ieee-org.tudelft.idm.oclc.org/document/10413356/
   - Guideline: **low solder volume + receptor pad smaller than the chip + initial offset ≈10 % of chip size → best placement accuracy.** Solder volume drives both translation and tilt.

3. **M. Mastrangeli**, "The Fluid Joint: The Soft Spot of Micro- and Nanosystems," *Advanced Materials*, vol. 27, no. 29, pp. 4254–4272, 2015. DOI: 10.1002/adma.201501260
   - Fluid-joint physics. Molten-solder surface tension γ ≈ 500 mN/m, capillary length L_c ≈ 2 mm; surface tension dominates gravity below that scale.

4. **M. Mastrangeli, Q. Zhou, V. Sariola, P. Lambert**, "Surface tension-driven self-alignment," *Soft Matter*, vol. 13, no. 2, pp. 304–327, 2017. DOI: 10.1039/C6SM02078J
   - Definitive review of capillary self-alignment statics and dynamics.

## To download from IEEE Xplore (TU Delft proxy)

5. **O. Krammer, B. Sinkovics, B. Illes**, "Studying the Dynamic Behaviour of Chip Components during Reflow Soldering," *30th ISSE*, 2007.
   - https://ieeexplore-ieee-org.tudelft.idm.oclc.org/document/4432814/
   - Chip movement and self-alignment dynamics during reflow.

6. **O. Krammer, Z. Radvanszki, Z. Illyefalvi-Vitez**, "Investigating the movement of chip components during reflow soldering," *2nd ESTC*, 2008.
   - https://ieeexplore-ieee-org.tudelft.idm.oclc.org/document/4684463/
   - Follow-up quantifying chip self-alignment displacement during reflow.

7. **T. Lesueur et al.**, "Self-Alignment of Active Si Bridge using Solder Joints Capillary Forces," *IEEE 75th ECTC*, 2025.
   - https://ieeexplore-ieee-org.tudelft.idm.oclc.org/document/11038257/
   - Most recent: solder-joint capillary self-alignment of an active component, same year as Abdelwahab's ECTC work.

8. **"Micro-LED Mass Transfer Technologies"** (review).
   - https://ieeexplore-ieee-org.tudelft.idm.oclc.org/document/9201923/
   - Context: where solder/self-assembly bonding sits among micro-LED mass-transfer methods.

9. **"An Alternative Micro LED Mass Transfer Technology: Self-Assembly."**
   - https://ieeexplore-ieee-org.tudelft.idm.oclc.org/document/9873296/

10. **"Fluidic Self-Assembly Transfer Technology for Micro-LED Display."**
    - https://ieeexplore-ieee-org.tudelft.idm.oclc.org/document/8808352/

## Component / process datasheets (already in repo)

- Würth WL-SFCC 0404 RGB LED (150044M155220) — `docs/datasheets/Wurth-WL-SFCC-0404-RGB-LED-150044M155220.pdf`
- ChipQuik TS391LT solder paste, Sn42/Bi57.6/Ag0.4 T4, mp 138 °C — from `part2/manual printing.pdf` (Ahmed's KET3 deck)
