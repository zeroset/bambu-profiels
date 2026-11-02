# bambu-profiels

Personal Bambu Studio presets (process, filament, machine) for a **Bambu Lab X2D**,
versioned in git so they survive reinstalls, upgrades and OS changes — and stay reviewable
as diffs.

> Typo in the repo name (`profiels`) is intentional: it matches the remote URL.

## Layout

```
filament/    filament presets
process/     process presets
machine/     printer presets
AGENTS.md    contribution/privacy rules — read before committing
```

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
