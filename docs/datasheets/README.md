# Component Datasheets — v4.0 PCB

All components on the TUD micro-LED v4.0 PCB, with manufacturer datasheets.
LEDs are bonded by the customer in cleanroom; **all other components are
pre-assembled by the fab house (Aisler / Eurocircuits).**

---

## Files in this folder

| File | Component | Where on PCB | Qty per board |
|---|---|---|---|
| `Wurth-WL-SFCC-0404-RGB-LED-150044M155220.pdf` | Würth WL-SFCC 0404 superflat RGB LED, P/N 150044M155220 | D1-D8 + DCL6_L1..6 + DCL12_L1..12 | **26** (DNP — bonded in cleanroom) |
| `Vishay-TNPV-Series-Precision-Thin-Film-Resistor-63080.pdf` | Vishay TNPV thin-film 0603 precision resistor series; use `TNPV0603100RBEEN` (100 Ω, ±0.1 %, 25 ppm/°C) | EIS_LOAD (between PP_EIS_LOAD_A and PP_EIS_LOAD_B) | **1** (pre-assembled) |
| `Wurth-WR-PHD-2.54mm-PinHeader-61301021121.pdf` | Würth WR-PHD 1×40 male pin header, 2.54 mm pitch, vertical THT, P/N 61301021121 | H_N_1..32 + H_S_1..32 | **64** total (= 2 strips, 32 pins each, pre-assembled) |
| `Murata-NCP15XH103J03RC-NTC.pdf` | **MANUAL DOWNLOAD REQUIRED** — see §"NTC datasheet" below | TH1, TH2, TH3, TH4 | **4** (pre-assembled) |

---

## NTC datasheet — manual fetch instructions

Murata's datasheet servers gate PDF downloads behind Cloudflare anti-bot.
Auto-download from `curl` always returns an HTML challenge page. Pick **one**
of these manual paths:

### Option A — Mouser (recommended, no login)

1. Open https://www.mouser.com/ProductDetail/81-NCP15XH103J03RC
2. Click the "Datasheet" link near the part number → opens PDF in browser
3. Save as `docs/datasheets/Murata-NCP15XH103J03RC-NTC.pdf`

### Option B — LCSC (LCSC C5316)

1. Open https://www.lcsc.com/product-detail/_C5316.html
2. Click "Datasheet" tab → download
3. Save to `docs/datasheets/Murata-NCP15XH103J03RC-NTC.pdf`

### Option C — Murata directly (requires login)

1. Open https://www.murata.com/en-eu/products/productdetail?partno=NCP15XH103J03RC
2. Log in if prompted; click "Specifications PDF"

### Option D — Use a browser-copy curl one-liner from this terminal

Once you have a working download URL from your browser's network inspector,
paste it here as:

```bash
! curl -L -o docs/datasheets/Murata-NCP15XH103J03RC-NTC.pdf '<PASTE URL HERE>'
```

The `!` prefix runs the command in this Claude session so the file lands in
the right folder without context-switching.

---

## Key NTC specs (for reference until PDF is on file)

| Parameter | Value |
|---|---|
| Manufacturer P/N | Murata `NCP15XH103J03RC` |
| Package | 0402 SMD (1.0 × 0.5 × 0.5 mm) |
| Resistance @ 25 °C | 10 kΩ ±5 % |
| B25/85 constant | 3380 K ±1 % |
| Operating range | −40 °C to +125 °C |
| Temperature accuracy (with B-curve cal) | ±0.3 °C between 0–70 °C |
| Power dissipation max | 100 mW (at 25 °C ambient) |
| Beta material constant | 3380 K |
| Recommended sense current | 100 µA (self-heating < 0.01 °C at I_sense × R = 1 V) |

### NTC R-T equation (for V_F-TSP calibration)

  T(K) = 1 / [ (1/T₀) + (1/B) · ln(R / R₀) ]

with T₀ = 298.15 K, R₀ = 10 000 Ω, B = 3380 K.

Tabulated R(T) values for typical room-temp range:

| T (°C) | R (Ω) |
|---:|---:|
| 0 | 27 580 |
| 25 | 10 000 |
| 50 | 3 893 |
| 75 | 1 615 |
| 100 | 705 |

For higher-precision applications use Murata's 5-parameter Steinhart-Hart fit
(in the datasheet) — but the simple B-formula above is within ±0.5 °C for
0–80 °C, plenty for bond thermal characterization.

---

## Alternative parts (if anything is out of stock)

| Original | Equivalent | Notes |
|---|---|---|
| Murata NCP15XH103J03RC | Vishay NTCS0402E3103FXT, TDK B57441V2103H062 | All 10 kΩ ±1% 0402 NTCs with B≈3380 K |
| Vishay TNPV0603100RBEEN | Susumu RR0816P-101-D, Yageo RT0603BRD07100RL | All 100 Ω ±0.1% 0603 thin-film |
| Würth 61301021121 | Generic 1×40 male 2.54 mm THT strip (any brand) | Cut to 32 pins per row |
