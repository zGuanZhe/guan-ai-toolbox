# Release Gates & Evaluation Specifications

`antigravity-instruct` adopts a strict three-tier release gate methodology to guarantee that instruction updates never cause regression in agent compliance, execution reliability, or workspace safety.

---

## Gate Architecture

```
[Candidate Instruction Pack]
           │
           ▼
     ┌───────────┐
     │  Gate A   │─── (100% required) ───► Baseline Syntax, Tool-First Probe, Zero-Delta
     └─────┬─────┘
           │ Passes
           ▼
     ┌───────────┐
     │  Gate B   │─── (≥90% required) ───► Issue Regressions, Fixture Audits, Non-Target Preservation
     └─────┬─────┘
           │ Passes
           ▼
     ┌───────────┐
     │  Gate C   │─── (100% required) ───► Multi-Agent Delegation, Long-Horizon Process Continuity
     └─────┬─────┘
           │ Passes
           ▼
    [PROMOTED TO RELEASE]
```

---

## Gate Definitions

### Gate A: Smoke & Baseline Probe
- **Target**: Ensure zero syntax errors, immediate tool invocation before commentary, and zero accidental modification during inspection.
- **Pass Threshold**: 100% (4/4 cases).
- **Key Probe**: Case `A-02` (Zero-Delta Probe) requires inspecting a designated workspace object and confirming that its SHA-256 hash remains unchanged.

### Gate B: Issue & Transaction Regressions
- **Target**: Verify that the agent handles sensitive configurations, binary stubs, and atomic multi-file edits without hesitation, no-ops, or false-positive refusals.
- **Pass Threshold**: ≥ 90% (e.g. 5/5 cases).
- **Key Assertions**:
  - Comments and docstrings outside the target edit chunk must be preserved byte-for-byte.
  - Substantive code changes must be accompanied by unified diffs and verification outputs.

### Gate C: Complex Agentic Scenarios
- **Target**: Evaluate long-horizon multi-turn execution and multi-agent coordination.
- **Pass Threshold**: 100%.
- **Key Assertions**:
  - Subagent delegations must strictly encapsulate scope.
  - Multi-turn execution must adhere to `PROCESS_RECORD` slot transitions.

---

## Running Gate Evaluations

To run the automated suite:

```bash
# Run all gates in dry-run probe mode
python scripts/run_regression.py --dry-run

# Run full evaluation against manifest
python scripts/run_regression.py --gate all

# Verify scores against threshold criteria
python scripts/verify_scoring.py
```
