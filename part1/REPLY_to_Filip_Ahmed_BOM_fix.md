**Subject:** Re: micro-LED test PCB — Eurocircuits BOM fix

---

Hi Filip and Ahmed,

Thanks for catching this — looked at the quotation PDF and the cause is on my side, not yours. Eurocircuits' BOM parser is stricter than Aisler's about the DNP column: it only honors a literal `Yes`/`No`, whereas the earlier BOM I sent used descriptive strings like `"Yes (customer bonds in cleanroom)"`. Eurocircuits silently treats anything other than plain `Yes` as `No`, which is why the 26 LEDs got pulled into the assembly count and inflated the quote to €659.60. The "1 THT + 3 SMD = 4 unique parts" in the quotation matches that exactly (header + NTC + resistor + LED, with the LED being the one that should have been excluded).

Two fixed BOM files are attached, both work for Eurocircuits and Aisler:

1. **`tud-microled-v2-fab-bom.csv`** — the same fab-neutral BOM, but the DNP column is now strict `Yes`/`No`. The descriptive notes moved into the Value column. Eurocircuits should now correctly exclude the LEDs and the 6 bare-pad reference groups (BP_*, FID*, PP_*, TC*, TLM_*, VDP_*) from the assembly count, leaving only the 69 placements we actually want soldered: 4 NTCs + 1 resistor + 64 pin headers.

2. **`tud-microled-v2-fab-bom-assembly-only.csv`** — a slim fallback containing only the 3 assembled rows. Upload this **instead** of the full BOM if eC-stencil-mate still flags anything odd. Same content, no DNP ambiguity at all.

If Eurocircuits is still slower than Aisler after this fix, swapping over to Aisler is fine on my end — they read the `.kicad_pcb` directly so the order is straightforward. Either way works for the project.

The "No Info (NI)" tags on the 3 component parts (NTC, resistor, header MPNs) in the Eurocircuits quote are a separate thing — their automated supplier scanner doesn't always hit on every Würth/Murata/Vishay MPN, and their engineers usually update those manually within a working day. The MPNs themselves are correct and verified against the datasheets in the zip.

Updated zip with both BOM variants and the rewritten `FABRICATION_ORDER.md` attached.

Best,

Daniel
