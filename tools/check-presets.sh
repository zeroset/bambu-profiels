#!/usr/bin/env bash
# Validate every user preset in this repository.
#
# Checks, per preset file:
#   * filename == preset "name"      (Bambu Studio derives the name from the filename)
#   * "type" matches the folder      (filament/ process/ machine/)
#   * "instantiation" is present     ("false" = hidden base, "true" = visible in the UI)
#   * "inherits" resolves            (to a system preset or another preset in this repo)
#   * no preset inherits itself
#
# Usage:  tools/check-presets.sh [--quiet]
# Env:    BAMBU_SYSTEM_DIR=/path/to/system/BBL    (default: ~/.config/BambuStudio/system/BBL)
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SYSTEM="${BAMBU_SYSTEM_DIR:-$HOME/.config/BambuStudio/system/BBL}"

if [ ! -d "$SYSTEM" ]; then
    echo "warning: system preset dir not found: $SYSTEM" >&2
    echo "         inheritance against system presets cannot be verified" >&2
fi

python3 - "$ROOT" "$SYSTEM" <<'PY'
import json, os, sys

root, system = sys.argv[1], sys.argv[2]
collections = ("filament", "process", "machine")
errors, warnings, checked = [], [], 0

# ---- system preset names (needed for collision + inheritance checks) -------
system_names = set()
if os.path.isdir(system):
    for dirpath, _dirnames, filenames in os.walk(system):
        for fn in filenames:
            if fn.lower().endswith(".json"):
                system_names.add(fn[:-5])

# ---- collect presets in this repo -----------------------------------------
repo = {}          # name -> (path, collection, data)
for coll in collections:
    base = os.path.join(root, coll)
    if not os.path.isdir(base):
        continue
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for fn in filenames:
            if not fn.lower().endswith(".json"):
                continue
            path = os.path.join(dirpath, fn)
            stem = fn[:-5]
            try:
                with open(path, encoding="utf-8-sig") as fh:
                    data = json.load(fh)
            except Exception as exc:                       # noqa: BLE001
                errors.append(f"{path}: invalid JSON: {exc}")
                continue
            checked += 1
            if stem in repo:
                errors.append(f"{path}: duplicate preset name, also in {repo[stem][0]}")
            repo[stem] = (path, coll, data)

            rel = os.path.relpath(path, root)
            if stem in system_names:
                errors.append(f"{rel}: name collides with a system preset; the user copy would "
                              f"be skipped at load (\"Preset already present, not loading\")")
            if data.get("name") != stem:
                errors.append(f"{rel}: name {data.get('name')!r} != filename {stem!r}")
            if data.get("type") != coll:
                errors.append(f"{rel}: type {data.get('type')!r} != folder {coll!r}")
            if "instantiation" not in data:
                errors.append(f"{rel}: missing 'instantiation' (\"true\" or \"false\")")
            elif str(data["instantiation"]).lower() not in ("true", "false"):
                errors.append(f"{rel}: instantiation must be \"true\" or \"false\"")

# ---- inheritance -----------------------------------------------------------
for name, (path, _coll, data) in repo.items():
    parent = (data.get("inherits") or "").strip()
    rel = os.path.relpath(path, root)
    if not parent:
        warnings.append(f"{rel}: no 'inherits' (root preset)")
        continue
    if parent == name:
        errors.append(f"{rel}: inherits itself")
    elif parent not in repo and parent not in system_names:
        errors.append(f"{rel}: parent not found: {parent!r}")

# ---- report ----------------------------------------------------------------
for w in warnings:
    print(f"warning: {w}", file=sys.stderr)
for e in errors:
    print(f"error: {e}", file=sys.stderr)

if errors:
    print(f"\n{len(errors)} error(s) in {checked} preset(s).", file=sys.stderr)
    sys.exit(1)

print(f"ok: {checked} preset(s) checked, inheritance resolves")
PY
