#!/usr/bin/env python3
"""Scoring Verification for Antigravity Instruct Gates."""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORT = PROJECT_ROOT / "reports" / "regression_results.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify regression scoring against release thresholds")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT, help="Path to regression report")
    args = parser.parse_args()

    if not args.report.exists():
        print(f"[ERROR] Report file {args.report} does not exist. Run scripts/run_regression.py first.")
        return 1

    with open(args.report, "r", encoding="utf-8") as f:
        data = json.load(f)

    gates = data.get("gates", {})
    all_passed = True

    print("=================== GATE SCORING VERIFICATION ===================")
    for gkey, gres in gates.items():
        title = gres.get("title", gkey)
        passed = gres.get("passed", False)
        pass_rate = gres.get("pass_rate", 0.0)
        req_rate = gres.get("required_pass_rate", 1.0)
        p_cases = gres.get("passed_cases", 0)
        t_cases = gres.get("total_cases", 0)

        status_str = "[PASS]" if passed else "[FAIL]"
        print(f"  {status_str} {title}: {p_cases}/{t_cases} ({pass_rate:.1%} / Req: {req_rate:.1%})")

        if not passed:
            all_passed = False

    print("==================================================================")
    if all_passed:
        print("[VERIFIED] All release gate scoring criteria are satisfied.")
        return 0
    else:
        print("[REJECTED] One or more gates failed to meet the required pass rate.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
