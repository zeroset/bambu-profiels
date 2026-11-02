# eSUN profiles — provenance and deviations

eSUN's own Bambu Lab preset packs, downloaded 2026-11-02 from
<https://www.esun3d.com/parameters-download> (Brand: Bambu Lab). Only the numbers were taken
from them; the JSON in this repository is written by hand. **No downloaded file is committed**
— eSUN's packs carry no explicit redistribution licence, so they stay local.

## Source files

| File | Used for |
|---|---|
| `X2D ESUN PLA+ FILAMENT.JSON` | textured plate temp 60 °C |
| `X2D ESUN PLA+ PROCESS.JSON` | PLA+ process speeds |
| `X2D ESUN ASA+ PROCESS.JSON` | ASA+ process speeds |
| `H2D ESUN ASA+ FILAMENT.JSON` | ASA+ flow 0.96, MVS 16, chamber 50 °C, fan max 40 % |

Bambu Studio ships `eSUN PLA+` (vendor base + X1/A1/P1/H2D variants, no X2D). No eSUN ASA+
preset is shipped at all, which is why the ASA+ numbers come from the H2D pack instead.

## Resulting presets

| Preset | Inherits | Material numbers |
|---|---|---|
| `filament/eSUN PLA+ @BBL X2D 0.4 nozzle` | `filament/base/eSUN PLA+ @BBL X2D @base` | 220 °C, MVS 16, flow 0.98, 22.99 €/kg, 1.25 g/cm³, textured plate 60 °C |
| `filament/eSUN ASA+ @BBL X2D 0.4 nozzle` | `filament/base/eSUN ASA+ @BBL X2D @base` | 260 °C, MVS 16, flow 0.96, 24.99 €/kg, 1.04 g/cm³, chamber 50 °C, fan max 40 % |
| `process/eSUN PLA+ Process @BBL X2D` | `process/base/eSUN PLA+ Process @base` | walls 280/200, infill 280, top 250, first layer 50 |
| `process/eSUN ASA+ Process @BBL X2D` | `process/base/eSUN ASA+ Process @base` | walls 200/150, infill 150–200 |

The `@base` files are hidden (`instantiation: false`) and loaded from `base/`, so eSUN's numbers
stay untouched while the visible presets above them stay thin. Edit the visible ones in the UI;
Bambu Studio writes the diff back there.

The base names carry the `@BBL X2D` marker on purpose: Bambu Studio already ships a system
preset literally named `eSUN PLA+ @base`, and a user preset with the same name is discarded at
load time ("Preset already present, not loading").

## Deliberate deviations from the downloaded files

- **`small_perimeter_threshold` dropped.** eSUN set it to `280` (PLA+) and `150` (ASA+) — the
  same numbers as their wall speeds, which looks like a copy-paste slip. The key is a *length*
  in mm, so those values would flag nearly every perimeter as "small". Not reproduced.
- **`filament_start_gcode` not copied.** eSUN's vendor base drives the exhaust fan (`M106 P3`)
  from bed temperature; the X2D presets leave filament start G-code empty. Kept empty, add it
  manually if you want the chamber fan behaviour.
- **`filament_id` omitted.** eSUN PLA+ already owns `GFL03` as a built-in system preset;
  duplicating the id makes AMS auto-matching ambiguous. AMS matches on type + vendor + colour.
- **Variant arrays kept at 4 slots** (Direct Std/HF, Bowden Std/HF) as eSUN shipped them. The
  loader maps per-variant values by name, so the two E3D High Flow variants keep the values of
  the X2D parent preset they inherit from.

## Numbers worth double-checking

eSUN's own published values disagree across sources: the Bambu-shipped `eSUN PLA+ @base` says
MVS 16, cost 22.99, density 1.25; third-party X2D profiles claim MVS 21, cost 24.99, density
1.26. The Bambu-shipped values are used here. If PLA+ flow-starves at 16 mm³/s, raise
`filament_max_volumetric_speed` in `filament/base/eSUN PLA+ @BBL X2D @base.json`.
