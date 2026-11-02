# bambu-profiels

Personal Bambu Studio presets (process, filament, machine) for a **Bambu Lab X2D**,
versioned in git so they survive reinstalls, upgrades and OS changes — and stay reviewable
as diffs.

> Typo in the repo name (`profiels`) is intentional: it matches the remote URL.

## Layout

```
filament/        filament presets; base/ holds hidden bases
process/         process presets;  base/ holds hidden bases
machine/         printer presets;  base/ holds hidden bases
vendor/esun/     provenance of the eSUN numbers
tools/           check-presets.sh
AGENTS.md        contribution/privacy rules — read before committing
```

### Included presets

| Material | Filament preset | Process preset |
|---|---|---|
| eSUN PLA+ | `eSUN PLA+ @BBL X2D 0.4 nozzle` | `eSUN PLA+ Process @BBL X2D` |
| eSUN ASA+ | `eSUN ASA+ @BBL X2D 0.4 nozzle` | `eSUN ASA+ Process @BBL X2D` |

Each visible preset is a thin layer over a hidden `@base` file in `base/`, so vendor numbers
stay untouched and your own tweaks remain a small diff. `base/` is the only subfolder Bambu
Studio loads — anything else placed under `filament/` or `process/` is invisible to the slicer.

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
