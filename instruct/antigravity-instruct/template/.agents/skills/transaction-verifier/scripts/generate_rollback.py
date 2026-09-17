#!/usr/bin/env python3
"""Rollback Script Generator for Atomic Transactions."""

from __future__ import annotations
import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate atomic rollback script")
    parser.add_argument("--target", required=True, type=Path, help="Target file that was modified")
    parser.add_argument("--backup", required=True, type=Path, help="Backup file to restore from")
    parser.add_argument("--output-script", default=Path("rollback.py"), type=Path, help="Output rollback script path")
    args = parser.parse_args()

    target_abs = args.target.resolve()
    backup_abs = args.backup.resolve()

    script_content = f"""#!/usr/bin/env python3
# AUTO-GENERATED ATOMIC ROLLBACK SCRIPT
import shutil
import sys
from pathlib import Path

TARGET = Path(r"{target_abs}")
BACKUP = Path(r"{backup_abs}")

def main():
    if not BACKUP.exists():
        print(f"[ROLLBACK ERROR] Backup file {{BACKUP}} does not exist!")
        sys.exit(1)
    
    print(f"[ROLLBACK] Restoring {{TARGET}} from {{BACKUP}}...")
    shutil.copy2(BACKUP, TARGET)
    print(f"[ROLLBACK] Successfully restored {{TARGET}}.")

if __name__ == "__main__":
    main()
"""

    args.output_script.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_script, "w", encoding="utf-8") as f:
        f.write(script_content)

    print(f"[ROLLBACK] Generated rollback script at: {args.output_script.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
