#!/usr/bin/env python3
"""Sync plaintext instructions with distribution ZIP archives and compute SHA256 checksums."""

from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
PACKAGES_DIR = PROJECT_ROOT / "packages"
MANIFEST_FILE = PACKAGES_DIR / "packages_manifest.json"


def calculate_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def build_archives() -> dict[str, dict]:
    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {}
    md_files = list(PACKAGES_DIR.glob("*.md"))

    if not md_files:
        print("[WARN] No markdown package files found in packages/")
        return manifest

    print(f"[SYNC] Building ZIP archives for {len(md_files)} package(s)...")

    for md_file in md_files:
        zip_file = md_file.with_suffix(".zip")
        with zipfile.ZipFile(zip_file, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(md_file, arcname=md_file.name)

        md_hash = calculate_sha256(md_file)
        zip_hash = calculate_sha256(zip_file)

        manifest[md_file.stem] = {
            "markdown_file": md_file.name,
            "markdown_sha256": md_hash,
            "zip_file": zip_file.name,
            "zip_sha256": zip_hash,
            "size_bytes": md_file.stat().st_size
        }
        print(f"  -> Built {zip_file.name} | SHA256: {zip_hash[:12]}...")

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"[SYNC] Updated manifest at {MANIFEST_FILE}")
    return manifest


def verify_archives() -> bool:
    if not MANIFEST_FILE.exists():
        print(f"[ERROR] Manifest file {MANIFEST_FILE} not found. Run with --build first.")
        return False

    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    all_valid = True
    print(f"[SYNC] Verifying {len(manifest)} package(s)...")

    for name, info in manifest.items():
        md_file = PACKAGES_DIR / info["markdown_file"]
        zip_file = PACKAGES_DIR / info["zip_file"]

        if not md_file.exists():
            print(f"  [FAIL] Missing markdown file: {md_file.name}")
            all_valid = False
            continue

        if not zip_file.exists():
            print(f"  [FAIL] Missing zip file: {zip_file.name}")
            all_valid = False
            continue

        cur_md_hash = calculate_sha256(md_file)
        cur_zip_hash = calculate_sha256(zip_file)

        if cur_md_hash != info["markdown_sha256"]:
            print(f"  [FAIL] Hash mismatch for {md_file.name}")
            all_valid = False
        elif cur_zip_hash != info["zip_sha256"]:
            print(f"  [FAIL] Hash mismatch for {zip_file.name}")
            all_valid = False
        else:
            print(f"  [OK] {name}: Verified ({cur_zip_hash[:12]}...)")

    return all_valid


def main() -> int:
    parser = argparse.ArgumentParser(description="Antigravity Instruct Archive Sync Tool")
    parser.add_argument("--build", action="store_true", help="Build/rebuild ZIP archives from markdown files")
    parser.add_argument("--verify", action="store_true", help="Verify existing archives against manifest")
    args = parser.parse_args()

    if args.verify:
        success = verify_archives()
        return 0 if success else 1

    # Default action is build
    build_archives()
    return 0


if __name__ == "__main__":
    sys.exit(main())
