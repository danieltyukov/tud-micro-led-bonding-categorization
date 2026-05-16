# Custom KiCad Library — Würth WL-SFCC RGB Chip LED

Symbol, footprint, and 3D model for the **Würth Elektronik WL-SFCC family**
of 0404 full-color RGB chip LEDs. Vendored from Würth's official open KiCad
repository so the design is self-contained — no SnapEDA / Ultra Librarian
account, no manual download.

**Source**: https://github.com/WurthElektronik/KiCad-Library (revision pulled
2026-05-16, master branch).

## Parts included

| File                                            | Variant      | P/N            | Body (mm)        | Datasheet match  |
|------------------------------------------------|--------------|----------------|------------------|------------------|
| `symbols/LED_Wurth_WL-SFCC.kicad_sym`          | both         | —              | —                | both variants    |
| `footprints/.../D_Wurth_WL-SFCC-0404.kicad_mod`           | standard 0404 | `150044M155260` | 1.00 × 1.00 × 0.65 | not ours       |
| `footprints/.../D_Wurth_WL-SFCC-0404superflat.kicad_mod`  | super-flat    | **`150044M155220`** | **0.95 × 0.95 × 0.25** | **← use this** |
| `3dmodels/.../D_Wurth_WL-SFCC-0404.step`                  | standard      | —              | —                | —                |
| `3dmodels/.../D_Wurth_WL-SFCC-0404superflat.step`         | super-flat    | —              | —                | **← use this**   |

The PDF datasheet in `docs/150044M155220-RGB LEDs.pdf` is for the **super-flat
0404** variant. Both KiCad symbols share the library file:

- `0404_150044M155260` — standard 0404
- `0404superflat_150044M155220` — super-flat, **the one matching our datasheet**

Pad layout (both variants share the same recommended land pattern):

```
      Y
      ↑
  ┌───┴───┐
  │ 2   3 │   pin 1 = + (common anode)
  │   ◌   │   pin 2 = − R (cathode)
  │ 1   4 │   pin 3 = − B (cathode)
  └───────┘   pin 4 = − G (cathode)
              (per the WL-SFCC symbol library)
```

- 4 SMD rect pads at (±0.4 mm, ±0.4 mm), each **0.4 × 0.4 mm**
- Courtyard 1.7 × 1.7 mm
- Polarity mark "+" on F.SilkS near pin 1 (upper-left, **note**: the WL-SFCC
  KiCad library's polarity dot is on the **upper-left at pin 2** because the
  silkscreen mark sits *above* the −R cathode in their convention — this is
  the same as the printed mark on the LED itself in the datasheet
  "Dimensions" view. Pin 1, the common anode, sits **lower-left**.)

## Configuring KiCad to find the 3D models

The footprint references the 3D model via the `${WE_3DMODEL_DIR}` environment
variable so the path stays portable:

```
(model "${WE_3DMODEL_DIR}/LED_SMD_Wurth.3dshapes/D_Wurth_WL-SFCC-0404superflat.step" ...)
```

Set this once per workstation in **KiCad → Preferences → Configure Paths**:

| Name              | Value                                                          |
|-------------------|----------------------------------------------------------------|
| `WE_3DMODEL_DIR`  | `<absolute-path-to-this-repo>/new-pcb/library/3dmodels`        |

## Adding the library to a KiCad project

In KiCad's Project Manager:

1. **Symbols** → *Preferences → Manage Symbol Libraries → Project tab → add*:
   - Nickname: `LED_SFCC_Wurth`
   - Library Path: `${KIPRJMOD}/../library/symbols/LED_Wurth_WL-SFCC.kicad_sym`
   - Plugin Type: `KiCad`
2. **Footprints** → *Preferences → Manage Footprint Libraries → Project tab → add*:
   - Nickname: `LED_SMD_Wurth`
   - Library Path: `${KIPRJMOD}/../library/footprints/LED_SMD_Wurth.pretty`
   - Plugin Type: `KiCad`

(Both nicknames match what the symbol file references in its `Footprint`
property; do not rename.)

## License

Würth Elektronik's KiCad library is distributed under the terms documented in
`LICENSE_WE_KiCad_library.pdf` and `DISCLAIMER_WE_KiCad_library.pdf` (both
included verbatim in this folder). In short: **free use including
commercial, no warranty, no resale of the library files themselves**.
