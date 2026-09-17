# Rule 01: Tool Transaction Protocol

## Purpose
Ensure all workspace modifications are deterministic, observable, and reversible.

## Protocol
1. **Mandatory Pre-Read**:
   - Before executing `replace_file_content` on any file, verify exact line numbers and target content using `view_file`.
   - Never guess line numbers or indentation.

2. **Atomic Modification**:
   - Make single, contiguous changes per tool call whenever possible.
   - Do not delete or refactor surrounding functional code unless requested.

3. **Post-Modification Confirmation**:
   - Inspect the modified file or run a dry-run test immediately following modification to confirm syntax validity.
