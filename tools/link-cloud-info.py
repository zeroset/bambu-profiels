#!/usr/bin/env python3
"""Create the `.info` sidecars Bambu Studio needs before it will upload a preset.

`PresetCollection::get_user_presets()` skips any user preset that has an `inherits`
but an empty `base_id`:

    if (preset.base_id.empty() && preset.inherits() != "") continue;

`base_id` (the parent preset's `setting_id`) only ever lives in the `.info` sidecar,
never in the preset JSON. Bambu Studio writes that file when *it* creates a preset,
so hand-written ones stay local forever until they get one.

This script fills the gap: for every preset in filament/ process/ machine/ that
inherits a system preset, it writes a matching `<name>.info` with `base_id` set.
It never overwrites an existing `.info`, so cloud `setting_id`s are preserved.

The files are gitignored on purpose: they contain the account id and cloud ids.

Usage: tools/link-cloud-info.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HOME = os.path.expanduser("~")
CONFIG_DIR = os.path.join(HOME, ".config/BambuStudio")
SYSTEM = os.path.join(CONFIG_DIR, "system/BBL")
ACCOUNT = os.path.join(CONFIG_DIR, "user")
COLLECTIONS = ("filament", "process", "machine")


def account_id() -> str:
    """Bambu cloud account id, from BambuStudio.conf -> preset_folder."""
    conf = os.path.join(CONFIG_DIR, "BambuStudio.conf")
    try:
        with open(conf, encoding="utf-8") as fh:
            data = json.load(fh)
        return str(data.get("app", {}).get("preset_folder") or "")
    except (OSError, ValueError):
        return ""


def system_setting_ids() -> dict[tuple[str, str], str]:
    """(collection, preset name) -> setting_id, for the bundled system presets."""
    found: dict[tuple[str, str], str] = {}
    for coll in COLLECTIONS:
        base = os.path.join(SYSTEM, coll)
        if not os.path.isdir(base):
            continue
        for dirpath, _dirnames, filenames in os.walk(base):
            for fn in filenames:
                if not fn.lower().endswith(".json"):
                    continue
                path = os.path.join(dirpath, fn)
                try:
                    with open(path, encoding="utf-8-sig") as fh:
                        data = json.load(fh)
                except (OSError, ValueError):
                    continue
                sid = data.get("setting_id")
                if sid:
                    found[(coll, fn[:-5])] = sid
    return found


def repo_presets(account_dir: str) -> list[tuple[str, str, dict]]:
    """(collection, path, data) for every preset in this repository."""
    out = []
    for coll in COLLECTIONS:
        base = os.path.join(account_dir, coll)
        if not os.path.isdir(base):
            continue
        for fn in sorted(os.listdir(base)):
            if not fn.lower().endswith(".json"):
                continue
            path = os.path.join(base, fn)
            try:
                with open(path, encoding="utf-8-sig") as fh:
                    out.append((coll, path, json.load(fh)))
            except (OSError, ValueError) as exc:
                print(f"skip {path}: {exc}", file=sys.stderr)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    uid = account_id()
    if not uid:
        print("warning: could not read preset_folder from BambuStudio.conf", file=sys.stderr)
        return 1

    account_dir = os.path.join(ACCOUNT, uid)
    if not os.path.isdir(account_dir):
        print(f"error: account preset folder not found: {account_dir}", file=sys.stderr)
        return 1

    system_ids = system_setting_ids()
    written = skipped = unresolved = 0

    for coll, path, data in repo_presets(account_dir):
        parent = (data.get("inherits") or "").strip()
        if not parent:
            continue

        info_path = os.path.splitext(path)[0] + ".info"
        if os.path.exists(info_path):
            skipped += 1
            continue

        base_id = system_ids.get((coll, parent))
        if not base_id:
            unresolved += 1
            print(f"warning: {os.path.basename(path)}: parent {parent!r} is not a system "
                  f"preset of this installation; no base_id to write", file=sys.stderr)
            continue

        body = (
            "sync_info = \n"
            f"user_id = {uid}\n"
            "setting_id = \n"
            f"base_id = {base_id}\n"
            "updated_time = 0\n"
        )
        if args.dry_run:
            print(f"would write {info_path}  (base_id = {base_id})")
        else:
            with open(info_path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(body)
            print(f"wrote {info_path}  (base_id = {base_id})")
        written += 1

    print(f"\n{written} written, {skipped} already present, {unresolved} unresolved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
