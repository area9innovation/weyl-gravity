#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from foundations.check_finite_qubit_interaction_core import check

RESULT = ROOT / "foundations/results/FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1.json"
SCHEMA = ROOT / "foundations/schema/foundational-finite-qubit-interaction-core-v1.schema.json"
REPORT = ROOT / "foundations/reports/finite-qubit-interaction-core.md"


def load(path: Path):
    return json.loads(path.read_text())


def verify(*, result=None, report=None):
    r = load(RESULT) if result is None else result
    text = REPORT.read_text() if report is None else report
    errors: list[str] = []
    errors.extend("schema " + e.message for e in Draft202012Validator(load(SCHEMA), format_checker=FormatChecker()).iter_errors(r))
    checker_errors, summary = check()
    errors.extend("checker " + e for e in checker_errors)
    if summary["digest"] != r.get("independent_checker", {}).get("expected_digest"):
        errors.append("checker digest")
    flags = r.get("claim_flags", {})
    for key in ("exact_finite_interaction_model", "exact_state_and_probability_witness", "exact_entanglement_generation_witness", "exact_finite_krein_companion"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("weakest_base_classified", "continuum_limit_established", "renormalization_established", "qme_restored", "lorentzian_causal_claim"):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    for token in ("M_4(Q(i))", "P(00)=1/2", "one-qubit reduction is exactly `I/2`", "finite Krein companion", "sufficiency statement", "no continuum limit", "LORENTZIAN-CAUSAL"):
        if token not in text:
            errors.append("report token " + token)
    return errors


def main() -> int:
    errors = verify()
    print("FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
