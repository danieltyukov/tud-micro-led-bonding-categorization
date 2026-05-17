**Subject:** micro-LED test PCB — order request (ET4277 / ET4391 project)

---

Hi Filip,

Attached is the KiCad project zip for the v2 micro-LED bonding characterization PCB. The project is mine for the two courses I'm currently taking, **ET4277 Microelectronics Reliability** and **ET4391 Advanced Microelectronics Packaging**. Ahmed will contact you separately with the project code for billing.

The board is fab-ready for either Aisler or Eurocircuits — whichever can turn it around faster. If possible, could the order go in on **Monday with the express shipping option** so the boards land this week? That would let the electrical characterization runs start straight away.

One assembly note: all the non-LED components on the board (4 NTCs, 1 reference resistor, 64 header pins, 69 placements in total) should be factory-soldered. Only the 26 WL-SFCC RGB LED footprints stay empty and are marked DNP in the BOM. The LEDs are the actual research subject and get bonded in the EKL cleanroom under controlled paste, reflow, and die-bonder conditions, so the only pick-and-place needed in-house is the LEDs themselves. Having the fab take care of everything else saves a step and gets us to characterization faster.

The verbatim DNP text to paste into the order notes, the full BOM with manufacturer part numbers, and a side-by-side Aisler vs Eurocircuits comparison (cost, lead time, what to upload where) are all in `FABRICATION_ORDER.md` inside the zip, under `fab_order/`. The same folder has the gerbers ZIP, the BOM CSV, the pick-and-place CSV, and the `.kicad_pcb` for whichever fab is picked.

Let me know if anything else is needed from my side.

Best,

Daniel Tyukov  
Student no. 5714699
