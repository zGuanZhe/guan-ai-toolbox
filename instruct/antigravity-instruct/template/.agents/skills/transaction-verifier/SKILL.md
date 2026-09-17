---
name: transaction-verifier
description: Verify file diffs, compute cryptographic hashes, and generate atomic rollback scripts for safe file modifications. Use when performing critical code updates or needing automated verification artifacts.
---

# Transaction Verifier Skill

This skill provides deterministic verification and rollback capabilities for code changes made during agent sessions.

## Capabilities
1. **Diff Verification**: Compare baseline file with modified file and generate a unified diff report.
2. **Rollback Generation**: Generate an idempotent shell script (`rollback.sh` or `rollback.bat`) that restores all modified files to their original baseline hashes.

## Workflow

### 1. Verify Diffs
Run the diff verification helper:
```bash
python scripts/verify_diff.py --original <path_to_original> --modified <path_to_modified>
```

### 2. Generate Rollback Script
Run the rollback generator:
```bash
python scripts/generate_rollback.py --target <path_to_file> --backup <path_to_backup>
```
