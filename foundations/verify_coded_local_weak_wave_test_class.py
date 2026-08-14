#!/usr/bin/env python3
"""Fail-closed verifier for the localized coefficient-weak wave result."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from foundations.build_coded_local_weak_wave_test_class import generated
from foundations.check_coded_local_weak_wave_test_class import check


RESULT = ROOT / "foundations/results/FOUNDATIONAL_CODED_LOCAL_WEAK_WAVE_TEST_CLASS_V1.json"
REPORT = ROOT / "foundations/reports/coded-local-weak-wave-test-class-v1.md"
SCHEMA = ROOT / "foundations/schema/foundational-coded-local-weak-wave-test-class-v1.schema.json"
CHECKER = ROOT / "foundations/check_coded_local_weak_wave_test_class.py"


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.module != "__future__":
            found.add(node.module.split(".")[0])
    return found


def verify(*, result: dict | None = None, report: str | None = None) -> tuple[list[str], list[str]]:
    value = json.loads(RESULT.read_text()) if result is None else result
    text = REPORT.read_text() if report is None else report
    errors = ["schema " + error.message for error in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(value)]
    checker_errors, _ = check(value)
    errors += ["checker " + error for error in checker_errors]
    result_bytes, report_bytes = generated()
    if (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode() != result_bytes:
        errors.append("deterministic result drift")
    if text.encode() != report_bytes:
        errors.append("deterministic report drift")
    if imports(CHECKER) != {"fractions", "hashlib", "json", "pathlib", "typing"}:
        errors.append("checker import boundary")
    lowered = CHECKER.read_text().lower()
    for token in ("float(", "numpy", "sympy", "cmath", "random", "requests", "urlopen"):
        if token in lowered:
            errors.append("checker forbidden token " + token)
    flags = value.get("claim_flags", {})
    for key in ("finite_localized_test_class_constructed", "labelled_finite_carrier_separated", "coefficient_transport_identities_proved", "coefficient_scalar_weak_wave_identity_proved", "pra_finite_certificate", "rca0_completion_transfer"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("all_smooth_tests_covered", "unlabelled_scalar_field_separated", "full_state_reconstruction_proved", "strict_causal_support_proved", "green_operator_constructed", "weyl_or_metric_bv_equation_proved", "empirical_calibration_proved", "new_lorentzian_claim"):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    for token in ("rank **10**", "Coefficient-wise weak equation", "RCA₀", "not a claim for every smooth test", "does not establish"):
        if token not in text:
            errors.append("report token " + token)
    return errors, ["Draft 2020-12 schema", "independent exact checker", "deterministic artifacts", "checker isolation", "positive finite-test theorem flags", "fail-closed distributional and causal boundaries"]


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_CODED_LOCAL_WEAK_WAVE_TEST_CLASS_V1: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
