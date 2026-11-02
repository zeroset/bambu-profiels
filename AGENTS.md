# AGENTS.md

Rules for anyone — human or AI agent — changing presets in this repository.

## This repository is PUBLIC

It is published at `git@github.com:zeroset/bambu-profiels.git`. Assume every commit is
permanently readable, forked, crawled and mirrored. Deleting a file in a later commit does
**not** remove it from history; it only hides it from the current tree.

## Hard rule: no credentials, no personal data — ever

Never add, and remove on sight, anything that identifies you, your account, your printer or
your network. Non-exhaustive list:

| Category | Examples to never commit |
|---|---|
| Bambu cloud account | `user_id`, `setting_id` / `base_id` (`PFUS…`, `GFSL…`), `sync_info`, login tokens, cookies, `localstorage/` |
| Printer identity | serial numbers (`20P…`), LAN access codes, hostnames, IP/MAC addresses, `BambuNetworkEngine.conf` |
| Secrets | passwords, API keys, OAuth tokens, private keys (`-----BEGIN …`), encrypted logs |
| People / machine | absolute home paths, OS usernames, email addresses, screenshots showing a serial or account name |
| Licensing | third-party bundles you have no right to redistribute |

Two specifics that matter here:

1. **Never commit `*.info` files.** These are Bambu Studio's cloud-sync sidecars; they contain
   your cloud account id and your cloud preset id. They are gitignored — keep them that way.
2. **Never let the account-id directory name reach a tracked path.** Bambu Studio stores user
   presets under `~/.config/BambuStudio/user/<account-id>/`. This repository's root *is* that
   account folder, so tracked paths start at `filament/`, `process/`, `machine/` and never
   contain the id itself.

Also strip personal content from preset `name`/`description` fields (project names, client
names, "for my …", notes about a specific print job) before committing.

`default/` is the guest preset folder and is out of scope: ignored, never committed.

## What this repo contains

The per-account Bambu Studio user preset folder:

```
filament/        filament presets   (*.json)
process/         process presets    (*.json)
machine/         printer presets    (*.json)
vendor/<name>/   provenance notes for third-party profiles (no preset data)
tools/           validation + cloud-sidecar helpers
.gitignore       excludes *.info, downloaded packs and scratch files
.githooks/       pre-commit privacy guard
```

System presets (`~/.config/BambuStudio/system/BBL/…`) are **not** part of this repo. They are
downloaded and overwritten by Bambu Studio; never copy them in.

### Folder semantics (verified against `Preset.cpp`)

Bambu Studio scans each preset folder **flat** — `boost::filesystem::directory_iterator` plus
`is_json_file()`, no recursion — with exactly one exception:

- `filament/esun/foo.json` → **never loaded**. Only `base/` is recursed into.
- `filament/base/foo.json` → loaded first, as a "custom root", so presets above it can inherit
  from it. Same for `process/base/` and `machine/base/`.

**This repo does not use `base/`.** Two presets are enough for the slicer, but a user-level
parent never reaches the cloud: `set_sync_info_and_save()` only propagates a parent's new
`setting_id` to children when the uploaded preset is a *root* (`get_preset_base(preset) ==
preset`, i.e. no `inherits` at all). A `base/` file that inherits a system preset is not a root,
so its children never get a `base_id` and are never uploaded. Every preset here therefore
inherits a **system** preset directly and carries its own values.

`instantiation: "false"` loads a preset but hides it from the drop-down; `"true"` shows it.

The **filename is the preset name** (`Preset preset(m_type, name, false)`), not the JSON `"name"`
field. Keep them identical or the drop-down and the repository will disagree; the app also
renames the file when a preset is saved under a new name.

A preset whose `inherits` cannot be resolved is **skipped** (`can not find parent …` in the log),
not loaded with defaults — so an upstream rename makes the preset vanish from the drop-down.
Run `tools/check-presets.sh` to catch that before committing.

## Preset conventions

- One JSON file per preset. The filename must equal the preset's `"name"` field, minus `.json`,
  or Bambu Studio will load a duplicate or resurrect the old name on the next save.
- `"from": "User"` for everything committed here. `"from": "system"` is reserved for Bambu.
- Presets are **diffs**: keep only the keys that differ from the parent, and put the parent in
  `"inherits"`. Always point at a **system** preset (e.g. `"Generic PLA @BBL X2D 0.4 nozzle"`).
  Do not chain user preset → user preset: it does not survive cloud sync (see Folder semantics)
  and the child disappears from the UI if the parent is renamed.
- Never give a preset the same name as a system preset. The user copy is discarded at load
  ("Preset already present, not loading") and children silently inherit Bambu's preset
  instead. `tools/check-presets.sh` fails on this, which is why the vendor bases carry an
  `@BBL X2D` marker.
- `"instantiation": "true"` makes the preset appear in the UI drop-down; `false` marks a base.
- `"compatible_printers": ["Bambu Lab X2D 0.4 nozzle"]` must list the exact system machine
  preset names, or the preset will not be selectable.
- X2D/H2D filament presets use 6-element arrays ordered by `filament_extruder_variant`
  (`Direct Drive Standard`, `Direct Drive High Flow`, `Direct Drive E3D High Flow`,
  `Bowden Standard`, `Bowden High Flow`, `Bowden E3D High Flow`). Do not copy 2-element arrays
  from X1/A1/P1 presets — the values land in the wrong slots.
- When adapting a vendor profile (eSUN, Polymaker, …), inherit the **X2D system preset for the
  same material** and override only the vendor numbers (cost, density, flow ratio, max
  volumetric speed, temperatures). This keeps the X2D-specific retraction, plate temperature
  and `include: fdm_filament_template_direct_bowden_e3d` behaviour intact.
- `"version"` records the Bambu Studio version that wrote the file. Leave it alone when hand
  editing; the app refreshes it on save.

## Bambu Cloud sync

Two things decide whether a preset ever reaches your Bambu account:

- **`"version"`** — must be a parseable version string, e.g. `"02.08.02.61"`. `load_presets()`
  runs `if (!Semver::parse(version)) continue;`, so a preset without it is **silently skipped**:
  absent from the drop-down and therefore never synced. `tools/check-presets.sh` fails on a
  missing or unparseable version.
- **`<name>.info`** — the sidecar holding `base_id`, the parent preset's `setting_id`.
  `get_user_presets()` skips every preset that has an `inherits` but an empty `base_id`, so a
  hand-written preset without this file never uploads, no matter how often you restart.

`tools/link-cloud-info.py` writes the missing sidecars (never touching an existing `setting_id`).
They are gitignored because they contain the account id and cloud ids; a fresh clone must run the
script once before Bambu Studio will sync.

The `version` value is uploaded to the cloud as the preset's slicer version — keep it equal to
the Bambu Studio build that wrote the file, and put human-readable provenance in `"description"`.
Bambu's parser accepts `AA.BB.CC` and `AA.BB.CC.DD` (four-part: `patch = CC*100 + DD`) and only
compares the major number against the running app, so any `2.x` works.

### Editing a preset that is already in the cloud

The cloud is authoritative. On startup Bambu Studio compares the cloud's `update_time` with the
local `updated_time` and, when the cloud is greater, **rewrites the local JSON with the cloud
copy** (`Preset.cpp`, `load_user_preset`: *"update the one from cloud which is newer"*). Bambu's
server timestamps can run hours ahead of the local clock, so a hand edit plus
`updated_time = now` still loses the race.

`tools/mark-for-upload.py` is the fix: it sets `sync_info = update` and moves `updated_time`
past the last cloud value, so the upload path wins (`cloud_update_time <= updated_time`) and the
diff is PUT on the next start.

A successful cloud round-trip also rewrites the file in **round-trip form**: `type`,
`instantiation` and `description` disappear, `version` becomes `2.8.2.61`, and every value equal
to the parent is dropped because it is inherited. `tools/check-presets.sh` fails on that — which
is the alarm. Recovery is `git checkout -- <file>` followed by `tools/mark-for-upload.py`.

## Workflow

1. Quit Bambu Studio (`pgrep -f bin/bambu-studio` must be empty). It rewrites presets and
   `BambuStudio.conf` from memory and will silently discard edits made while it runs.
2. Add/edit/delete JSON files here.
3. Start Bambu Studio and confirm the preset appears under the right drop-down and for the
   right machine.
4. `git add -A && git commit`.
5. Push.

Bambu Studio holds these presets in memory for the whole session, so a change is only visible
after a restart.

## Pre-commit guard

The repo uses `.githooks/pre-commit` through `core.hooksPath` (enable on a fresh clone with
`git config core.hooksPath .githooks`). It rejects staged `*.info` files, account-id-looking
directories and staged JSON containing cloud metadata, access codes, serials, home paths or
private keys.

The hook is a safety net, not the policy. It only inspects **staged JSON diffs**; Markdown,
scripts and anything already in history are your responsibility. `git commit --no-verify`
bypasses it and is never an acceptable workaround for a real finding.

## Before every commit

```bash
tools/check-presets.sh        # names, types, instantiation, inheritance
git status --short            # nothing unexpected staged
git diff --cached             # read every added line
git ls-files '*.info'         # must print nothing
git log --oneline -1          # sanity
```

If something sensitive did get committed and not yet pushed, rewrite it out
(`git commit --amend`, `git reset`, `git filter-repo`). Once pushed, rotate the secret —
history rewriting cannot un-publish it.
