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
| `filament/eSUN PLA+ @BBL X2D 0.4 nozzle` | `Generic PLA @BBL X2D 0.4 nozzle` | 225 °C, MVS 24/45/24/24/35/24, flow 0.98, 22.99 €/kg, 1.25 g/cm³, textured plate 60 °C |
| `filament/eSUN ASA+ @BBL X2D 0.4 nozzle` | `Bambu ASA @BBL X2D 0.4 nozzle` | 260 °C, MVS 18/25/18/18/20/18, flow 0.96, 24.99 €/kg, 1.04 g/cm³, chamber 60 °C, fan max 35 % |
| `process/eSUN PLA+ Process @BBL X2D` | `0.20mm Standard @BBL X2D` | 3 walls, gyroid 12 %, 4 top layers, back seam, walls 240/200, infill 280, first layer 50 |
| `process/eSUN ASA+ Process @BBL X2D` | `0.20mm Standard @BBL X2D` | 3 walls, gyroid 15 %, back seam, walls 200/150, infill 200, top 150, first layer 50 |

Each preset inherits a **system** preset and carries the eSUN numbers inline. An earlier layout
put those numbers in hidden `@base` user presets and inherited from them, which works locally but
never uploads to Bambu Cloud: a user-level parent's `setting_id` is only propagated to its
children when the parent is a root preset (no `inherits` at all), so the children never receive a
`base_id` and `get_user_presets()` skips them. See AGENTS.md, "Bambu Cloud sync".

All four carry `"version": "02.08.02.61"`; without a parseable `version` Bambu Studio skips the
file entirely, which is why earlier AI-written presets never appeared in the UI or the cloud.

## Speed/quality tuning (ASA+)

ASA is a different material and the levers are ordered differently: **chamber and cooling first,
flow second, structure third.** Its failure mode is warping and layer splitting, not
under-extrusion.

Filament side:

- **Chamber 50 → 60 °C.** eSUN ship 50 (from their H2D pack) and Bambu's own ASA preset uses 65.
  A warm chamber is the single biggest lever against warp and layer splitting on tall, flat or
  thin parts. 60 is the compromise: enough heat, without the fumes and cooldown cost of 65.
- **Part fan 40 → 35 %.** ASA wants as little airflow as it can get away with; 40 was above
  Bambu's own 35. The aux fan is already 0 and `slow_down_layer_time` stays at 12 s.
- **Volumetric speed 16 flat → 18/25/18/18/20/18**, i.e. Bambu's ASA ceilings. eSUN's flat 16
  capped 0.45 mm walls and infill at 185 mm/s; 18 lifts that to 208, which is just above what the
  process asks for. Not raised further: ASA stringing and surface finish degrade well before
  under-extrusion appears, so flow is the wrong place to look for speed here.
- **260 °C kept** (Bambu uses 270). If layer bonding looks weak at 18 mm³/s, 265 is the first
  step, not 270.

Process side:

- **3 walls** (from 2) — ASA delaminates before PLA does, so shell strength is worth the time.
- **Gyroid at 15 %** (from grid 15 %): same density, isotropic and no self-crossing. Density is
  deliberately *not* raised even though ASA parts are often functional — ASA warps from thermal
  contraction, and more infill adds shrink force while the third wall already carries the
  strength. Bump to 20 % only for genuinely load-bearing parts.
- **Top shells stay at 5** (PLA+ was cut to 4): the top surface is where warp and pillowing show
  first on ASA, so the extra material earns its time here.
- **Back seam, merged infill, reduced wall crossings** — same reasons as PLA+, no time cost.
- **Speeds unchanged.** eSUN's 200 mm/s inner wall / 200 infill now sit under the 208 mm/s
  ceiling, so the numbers are honest without being lowered; ASA simply does not need a lower
  request once the flow cap stops binding.
- **No ironing**, as with PLA+.

If corners still lift on large flat parts, the next two levers are a brim (`brim_type:
outer_only`, `brim_width: 8`) and raising the chamber to 65.

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
This repo now uses **24 mm³/s for Direct Drive Standard** and scales the other extruder variants
after Bambu's X2D ratios:

| Variant | MVS | Basis |
|---|---:|---|
| Direct Drive Standard | 24 | raised from Bambu's 21 — see *Verified flow* below |
| Direct Drive High Flow | 45 | Bambu's 40 scaled by 24/21 |
| Direct Drive E3D High Flow | 24 | Bambu leaves E3D at the standard value |
| Bowden Standard | 24 | Bambu keeps Bowden at parity with Direct |
| Bowden High Flow | 35 | Bambu's 30 scaled by 24/21 |
| Bowden E3D High Flow | 24 | Bambu leaves E3D at the standard value |

The X2D is a two-extruder machine (`extruder_type: Direct Drive, Bowden`), so slots 4–6 are the
second, Bowden-fed extruder, not an alternative nozzle on extruder 1.

At 0.2 mm layers those limits work out to ~272 mm/s on 0.45 mm walls/infill and ~292 mm/s on
0.42 mm lines before the slicer throttles. The process preset's requested speeds (inner wall 240,
sparse infill 270, internal solid 280) all sit under that now, so none of them are silently
capped any more — the same process ran 233/238/255 mm/s at the previous 21 mm³/s ceiling. The
cost/density values remain Bambu's shipped eSUN numbers (22.99 / 1.25) rather than the
third-party 24.99 / 1.26.

### Verified flow (2026-11-02)

A print sliced with the 21 mm³/s profile and then run with the printer's **Sport** setting
(124 % feedrate override) came out clean. Sport multiplies feedrate *after* slicing, so it
bypasses the slicer's volumetric cap: the binding roles (0.45 mm walls and infill, capped at
238 mm/s) ran at ~295 mm/s ≈ **26 mm³/s**, 24 % above the profile's limit.

That is evidence rather than a measurement — Sport is a blunt override that ignores layer-time
and cooling rules and also raises accelerations, so one clean part is a lower bar than the same
speed baked into the profile. The cap was therefore raised to **24**, not 26. The next step
(26 mm³/s at 228–230 °C) stays pending a proper max-volumetric-speed test.

## Speed/quality tuning (PLA+)

Filament side:

- **225 °C** (from 220) gives viscosity headroom at the 233 mm/s ceiling without changing gloss
  much. Auto flow-dynamics calibration is on (`flow_cali: 1`), so no `pressure_advance` is baked
  in — Bambu's own tooltip calls that key useless for their printers.
- **Layer cooling 5 s / 25 mm/s** (from 6 s / 20) — 6 s stalled every small layer and the top
  layers for no benefit on PLA.

Process side:

- **3 walls** (from 2) — the largest single quality gain: no infill show-through, better
  dimensional accuracy, stronger shells.
- **Gyroid at 12 %** (from grid 15 %) — pays back the third wall, no self-crossing paths.
- **4 top layers** (from 5) — 0.8 mm of top material is still generous.
- **Back seam** and **reduced wall crossings** — hides the seam and cuts surface blobs, no time cost.
- **Merged infill** — fewer travels inside the part, less stringing.
- **Inner wall 240** (from 280) — honest number at the 21 mm³/s ceiling; the real speed is unchanged.

Ironing is deliberately off: it costs 3–8 % on top layers for a cosmetic gain.
