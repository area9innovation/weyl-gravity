#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from foundations.build_finite_graph_wave_causality import generated
from foundations.check_finite_graph_wave_causality import check

RESULT = ROOT / "foundations/results/FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1.json"
REPORT = ROOT / "foundations/reports/finite-graph-wave-causality.md"
SCHEMA = ROOT / "foundations/schema/foundational-finite-graph-wave-causality-v1.schema.json"


def verify(*, result=None, report=None):
    value = json.loads(RESULT.read_text()) if result is None else result
    text = REPORT.read_text() if report is None else report
    errors = ["schema " + e.message for e in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(value)]
    checker_errors, summary = check(value)
    errors += ["checker " + e for e in checker_errors]
    expected_result, expected_report = generated()
    if (json.dumps(value, indent=2) + "\n").encode() != expected_result: errors.append("deterministic result drift")
    if text.encode() != expected_report: errors.append("deterministic report drift")
    if summary.get("fixtures") != 3 or summary.get("support_violations") != 0: errors.append("expected exact summary")
    flags = value.get("claim_flags", {})
    if flags.get("graph_step_support_certified") is not True or flags.get("lorentzian_causal_claim") is not False or flags.get("continuum_limit_proved") is not False: errors.append("claim boundary")
    return errors, ["schema", "independent exact recurrence", "deterministic artifacts", "claim boundary"]


def main():
    errors, checks = verify()
    print("FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors: print("  - " + item)
    return bool(errors)


if __name__ == "__main__": raise SystemExit(main())
