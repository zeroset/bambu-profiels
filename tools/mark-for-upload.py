#!/usr/bin/env python3
"""Mark hand-edited presets for upload to Bambu Cloud.

Why this exists
---------------
Bambu Studio compares the local `updated_time` (in the `.info` sidecar) with the
cloud's `update_time` and, if the cloud value is greater, **overwrites the local
preset file** with the cloud copy (Preset.cpp, load_user_preset: "update the one
from cloud which is newer"). Tagging a preset with the current local clock is not
enough: Bambu's server timestamps can run hours ahead of the local clock, so a
hand edit silently loses to the cloud copy on the next start.

This script sets `sync_info = update` and pushes `updated_time` past whatever the
cloud last reported (which is already in the `.info`), so the upload path wins:

    cloud_update_time <= updated_time  ->  keep local, sync_info = "update"

Bambu Studio then PUTs the diff on its next start.

Usage:
    tools/mark-for-upload.py                      # every preset with an .info
    tools/mark-for-upload.py "eSUN PLA+ ...json"  # only these files
"""
from __future__ import annotations

import argparse
import os
import sys
import time

HOME = os.path.expanduser("~")
CONFIG_DIR = os.path.join(HOME, ".config/BambuStudio")
COLLECTIONS = ("filament", "process", "machine")
MARGIN = 3600  # seconds past the highest timestamp we know about


def account_dir() -> str:
    conf = os.path.join(CONFIG_DIR, "BambuStudio.conf")
    try:
        import json
        with open(conf, encoding="utf-8") as fh:
            data = json.load(fh)
        uid = str(data.get("app", {}).get("preset_folder") or "")
    except (OSError, ValueError):
        uid = ""
    if not uid:
        raise SystemExit("error: cannot read preset_folder from BambuStudio.conf")
    return os.path.join(CONFIG_DIR, "user", uid)


def read_info(path: str) -> dict[str, str]:
    out: dict[str, str] = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if "=" in line:
                k, _, v = line.partition("=")
                out[k.strip()] = v.strip()
    return out


def write_info(path: str, info: dict[str, str]) -> None:
    order = ("sync_info", "user_id", "setting_id", "base_id", "updated_time")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for key in order:
            fh.write(f"{key} = {info.get(key, '')}\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="preset .json files (default: all)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = account_dir()
    if args.files:
        targets = [os.path.abspath(f) for f in args.files]
    else:
        targets = []
        for coll in COLLECTIONS:
            base = os.path.join(root, coll)
            if os.path.isdir(base):
                targets += [os.path.join(base, f) for f in sorted(os.listdir(base))
                            if f.lower().endswith(".json")]

    now = int(time.time())
    changed = 0
    for path in targets:
        info_path = os.path.splitext(path)[0] + ".info"
        if not os.path.exists(info_path):
            print(f"skip {os.path.basename(path)}: no .info (run tools/link-cloud-info.py first)",
                  file=sys.stderr)
            continue
        info = read_info(info_path)
        if not info.get("setting_id"):
            print(f"skip {os.path.basename(path)}: never uploaded yet, nothing to update",
                  file=sys.stderr)
            continue
        try:
            cloud_time = int(info.get("updated_time") or 0)
        except ValueError:
            cloud_time = 0
        stamp = max(cloud_time, now) + MARGIN
        info["sync_info"] = "update"
        info["updated_time"] = str(stamp)
        if args.dry_run:
            print(f"would mark {os.path.basename(path)}  updated_time -> {stamp}")
        else:
            write_info(info_path, info)
            print(f"marked {os.path.basename(path)}  updated_time -> {stamp}")
        changed += 1

    print(f"\n{changed} preset(s) marked; restart Bambu Studio to upload")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
