# Rule 03: Verification & Artifact Gates

## Requirement
Every substantial modification cycle must conclude with verified evidence:

1. **Artifact Proof**:
   - Confirm modified files exist and have non-zero size.
   - Run relevant unit tests or syntax checks (e.g. `python -m py_compile`, linters, or test suites).

2. **Rollback Availability**:
   - Provide a clear revert strategy in responses when performing non-trivial refactoring.
   - Example: `git checkout -- <file>` or backup file restoration.
