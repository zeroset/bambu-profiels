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

| Preset | Inherits | Numbers |
|---|---|---|
| `filament/eSUN PLA+ @BBL X2D 0.4 nozzle` | `Generic PLA @BBL X2D 0.4 nozzle` | 220 °C, MVS 20/38/20/20/29/20, flow 0.98, 22.99 €/kg, 1.25 g/cm³, textured plate 60 °C |
| `filament/eSUN ASA+ @BBL X2D 0.4 nozzle` | `Bambu ASA @BBL X2D 0.4 nozzle` | 260 °C, MVS 16, flow 0.96, 24.99 €/kg, 1.04 g/cm³, chamber 50 °C, fan max 40 % |
| `process/eSUN PLA+ Process @BBL X2D` | `0.20mm Standard @BBL X2D` | walls 280/200, infill 280, top 250, first layer 50 |
| `process/eSUN ASA+ Process @BBL X2D` | `0.20mm Standard @BBL X2D` | walls 200/150, infill 150–200 |

Each preset inherits a **system** preset and carries the eSUN numbers inline. An earlier layout
put those numbers in hidden `@base` user presets and inherited from them, which works locally but
never uploads to Bambu Cloud: a user-level parent's `setting_id` is only propagated to its
children when the parent is a root preset (no `inherits` at all), so the children never receive a
`base_id` and `get_user_presets()` skips them. See AGENTS.md, "Bambu Cloud sync".

All four carry `"version": "02.08.02.61"`; without a parseable `version` Bambu Studio skips the
file entirely, which is why earlier AI-written presets never appeared in the UI or the cloud.

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

## Volumetric speed

eSUN publishes a flat 16 mm³/s; third-party X2D profiles derived from their packs claim 21.
This repo uses **20 mm³/s for Direct Drive Standard** (matching the `Generic PLA Fast` preset)
and scales the other extruder variants after Bambu's own X2D ratios (`21 / 40 / 21 / 21 / 30 / 21`):

| Variant | MVS | Basis |
|---|---:|---|
| Direct Drive Standard | 20 | chosen |
| Direct Drive High Flow | 38 | Bambu 40/21 × 20 |
| Direct Drive E3D High Flow | 20 | Bambu leaves E3D at the standard value |
| Bowden Standard | 20 | Bambu keeps Bowden at parity with Direct (21/21) |
| Bowden High Flow | 29 | Bambu 30/21 × 20 |
| Bowden E3D High Flow | 20 | Bambu leaves E3D at the standard value |

The X2D is a two-extruder machine (`extruder_type: Direct Drive, Bowden`), so slots 4–6 are the
second, Bowden-fed extruder, not an alternative nozzle on extruder 1.

At 0.2 mm layers those limits work out to ~227 mm/s on 0.45 mm walls/infill and ~243 mm/s on
0.42 mm lines before the slicer throttles. The cost/density values remain Bambu's shipped eSUN
numbers (22.99 / 1.25) rather than the third-party 24.99 / 1.26.
