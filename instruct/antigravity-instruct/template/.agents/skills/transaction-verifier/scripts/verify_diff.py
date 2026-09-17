#!/usr/bin/env python3
"""Unified Diff and Hash Verification Script."""

from __future__ import annotations
import argparse
import difflib
import hashlib
import sys
from pathlib import Path


def get_sha256(filepath: Path) -> str:
    if not filepath.exists():
        return "MISSING"
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify diff and hash integrity")
    parser.add_argument("--original", required=True, type=Path, help="Original baseline file")
    parser.add_argument("--modified", required=True, type=Path, help="Modified target file")
    parser.add_argument("--output-diff", type=Path, help="Path to write unified diff")
    args = parser.parse_args()

    orig_hash = get_sha256(args.original)
    mod_hash = get_sha256(args.modified)

    print(f"[VERIFY] Original: {args.original} ({orig_hash[:12]})")
    print(f"[VERIFY] Modified: {args.modified} ({mod_hash[:12]})")

    if orig_hash == mod_hash and orig_hash != "MISSING":
        print("[VERIFY] Warning: Files are identical (zero delta).")
        return 0

    if not args.original.exists() or not args.modified.exists():
        print("[ERROR] One of the target files does not exist.")
        return 1

    with open(args.original, "r", encoding="utf-8", errors="replace") as f:
        orig_lines = f.readlines()
    with open(args.modified, "r", encoding="utf-8", errors="replace") as f:
        mod_lines = f.readlines()

    diff = list(difflib.unified_diff(
        orig_lines,
        mod_lines,
        fromfile=str(args.original),
        tofile=str(args.modified),
        lineterm=""
    ))

    diff_text = "\n".join(diff)
    print("\n--- DIFF SUMMARY ---")
    print(diff_text[:1000] + ("\n... [truncated]" if len(diff_text) > 1000 else ""))

    if args.output_diff:
        args.output_diff.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output_diff, "w", encoding="utf-8") as f:
            f.write(diff_text + "\n")
        print(f"[VERIFY] Diff saved to {args.output_diff}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
