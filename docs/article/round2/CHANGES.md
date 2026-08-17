# Edits to the electrical-characterization section

Daniel Tyukov, 17 August 2026. Source: `Article_from_Ahmed_2026-08-17.docx`. Output: `Article_edited_DanielTyukov_2026-08-17.docx`.

Numbers are paragraph indices in the source file. Citations are red, everything else is plain so it reads as normal body text.

- 31  daisy-chain and sheet-resistance sentences: added [R1] twice, closed the gap in '2.86× 10⁻⁸'
- 36  daisy-chain figure caption expanded to say what was measured
- 42  'between assembly condition and channel p = ...' was missing a word. Now 'channel outcome (p = ...)'
- 60  5 ms pulsing: added [R4], which reports self-heating bias for pulses of 10 ms and longer. Also spaced '(2⁶−1 =63)' as '2⁶ − 1 = 63'
- 64  equation legend: 'series resistance. which is the sum' had a full stop mid-sentence, changed to a comma. The symbols were left untouched
- 81  shunt fraction corrected. The meter sources 1.42 mA in diode mode, not 1 mA, so the shunt takes 0.62 mA and the junction 0.80 mA. Added [R3]
- 82  ideality window: added [R2], which reads n = 1 as radiative, n = 2 as SRH through defect levels and n > 2 as deep-level-assisted tunnelling
- 83  DELETED the paragraph beginning 'One numerical correction:'. It was an editing note written in the first person, and its 61 % figure assumed a 1 mA test current
- 88  variance share: the draft gave both 83 % and 85 %. From the unrounded standard deviations, 0.843² / 0.9147² = 84.9 %, so 85 %
- 95  pulse-duration argument: added [R4]
- 99  self-heating estimate rewritten. The stated inputs (200 K/W, −2 mV/K, 2.01 V) give 0.80 Ω, not 1.2 Ω, so the claimed agreement to within 25 % did not hold. Inverted the calculation instead: the measured 1.49 Ω implies about 370 K/W. Added [R5]
- 102 reverse-bias check: added [R3]
- 104 diode-test current corrected to 1.42 mA here as well
- T3  measurement-setup table: DMM diode-test excitation corrected from ≈1 mA to 1.42 mA, measured as 0.142 V across a 100 Ω 0.1 % reference
- END appended a red reference key listing [R1] to [R5] in full, to be deleted once the entries are in EndNote

## Checked and deliberately left alone

- The inline symbols in the equation legend, and in the sentence about the three correlated parameters. They are OMML objects: invisible to text extraction, correct in Word. I flagged these as missing in my previous mail. They are not missing.
- The Section B, C and D cross-references. They are correct as written. The subsections letter A Channel screening, B Forward characteristics, C Defect detection, D Measurement repeatability, E Self-heating, F Reverse bias, G Summary. I flagged these too, also wrongly.
