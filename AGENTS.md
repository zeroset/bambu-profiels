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
filament/    filament presets   (*.json)
process/     process presets    (*.json)
machine/     printer presets    (*.json)
.gitignore   excludes *.info and scratch files
.githooks/   pre-commit privacy guard
```

System presets (`~/.config/BambuStudio/system/BBL/…`) are **not** part of this repo. They are
downloaded and overwritten by Bambu Studio; never copy them in.

## Preset conventions

- One JSON file per preset. The filename must equal the preset's `"name"` field, minus `.json`,
  or Bambu Studio will load a duplicate or resurrect the old name on the next save.
- `"from": "User"` for everything committed here. `"from": "system"` is reserved for Bambu.
- Presets are **diffs**: keep only the keys that differ from the parent. Put the parent in
  `"inherits"` and always point it at a **system** preset (e.g.
  `"Generic PLA @BBL X2D 0.4 nozzle"`). Do not chain user preset → user preset: renaming or
  deleting the parent, or a different cloud-sync order, breaks the child with
  "base preset not found".
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
git status --short            # nothing unexpected staged
git diff --cached             # read every added line
git ls-files '*.info'         # must print nothing
git log --oneline -1          # sanity
```

If something sensitive did get committed and not yet pushed, rewrite it out
(`git commit --amend`, `git reset`, `git filter-repo`). Once pushed, rotate the secret —
history rewriting cannot un-publish it.
