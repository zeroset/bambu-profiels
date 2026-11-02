# bambu-profiels

Personal Bambu Studio presets (process, filament, machine) for a **Bambu Lab X2D**,
versioned in git so they survive reinstalls, upgrades and OS changes — and stay reviewable
as diffs.

> Typo in the repo name (`profiels`) is intentional: it matches the remote URL.

## Layout

```
filament/        filament presets
process/         process presets
machine/         printer presets
vendor/esun/     provenance of the eSUN numbers
tools/           check-presets.sh, link-cloud-info.py, mark-for-upload.py
AGENTS.md        contribution/privacy rules — read before committing
```

### Included presets

| Material | Filament preset | Process preset |
|---|---|---|
| eSUN PLA+ | `eSUN PLA+ @BBL X2D 0.4 nozzle` | `eSUN PLA+ Process @BBL X2D` |
| eSUN ASA+ | `eSUN ASA+ @BBL X2D 0.4 nozzle` | `eSUN ASA+ Process @BBL X2D` |

Personal presets carry a `zz ` prefix so they sort to the end of every preset list — Bambu
Studio's drop-downs, the cloud, and Bambuddy's slice dialog:

| Preset | What it is |
|---|---|
| `zz Generic PLA Fast @BBL X2D 0.4 nozzle` | Generic PLA with volumetric speed 20 on every variant and 4 s layer cooling, for fast PLA prints |
| `zz 0.2mm Speed Custom` | 0.20 mm process, walls/infill 450, outer wall 200, top surface 230 |

Each preset inherits a **system** preset and carries only the vendor numbers, so Bambu's own
updates keep flowing in. There are deliberately no user-level base presets: Bambu Studio cannot
upload a preset whose parent is another user preset, because the parent's cloud id never reaches
its children (see AGENTS.md, "Bambu Cloud sync"). Run `tools/link-cloud-info.py` once per machine
to generate the `.info` sidecars that Bambu Studio needs before it will sync anything.

The repository root is the per-account preset folder, i.e.
`~/.config/BambuStudio/user/<account-id>/`. Preset paths therefore never contain the
account id.

## Using these presets

Quit Bambu Studio first — it rewrites presets from memory and would overwrite your edits.

```bash
git clone git@github.com:zeroset/bambu-profiels.git ~/bambu-presets
cp ~/bambu-presets/{filament,process,machine}/*.json \
   ~/.config/BambuStudio/user/<account-id>/{filament,process,machine}/ 2>/dev/null
```

Restart Bambu Studio and pick the presets in the drop-downs. Alternatively clone the repo
straight into your account folder (if it is empty) or symlink the individual JSON files.

Presets are **diffs**: each one `"inherits"` a bundled system preset, so they require a
matching Bambu Studio version (currently `02.08.x`) and the same printer model. If a parent
preset is missing after an upgrade, the preset shows as broken in the UI rather than printing
with wrong values.

## Privacy

This repository is public and is kept free of credentials and personal data: no account ids,
cloud preset ids (`*.info` files are gitignored), printer serials, LAN access codes, tokens,
absolute home paths or email addresses. `AGENTS.md` lists the full policy and a pre-commit
hook enforces the mechanical part of it.

## License

No license declared. All rights reserved — ask before redistributing.
