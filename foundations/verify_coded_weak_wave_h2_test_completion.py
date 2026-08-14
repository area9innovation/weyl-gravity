#!/usr/bin/env python3
"""Fail-closed verifier for the named H2 weak-wave completion."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from foundations.build_coded_weak_wave_h2_test_completion import generated
from foundations.check_coded_weak_wave_h2_test_completion import check


RESULT = ROOT / "foundations/results/FOUNDATIONAL_CODED_WEAK_WAVE_H2_TEST_COMPLETION_V1.json"
REPORT = ROOT / "foundations/reports/coded-weak-wave-h2-test-completion-v1.md"
SCHEMA = ROOT / "foundations/schema/foundational-coded-weak-wave-h2-test-completion-v1.schema.json"
CHECKER = ROOT / "foundations/check_coded_weak_wave_h2_test_completion.py"


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
    for key in ("rational_h2_test_code_carrier_constructed", "named_h2_test_completion_constructed", "explicit_residual_modulus_proved", "weak_solution_extended_to_every_named_h2_test", "represented_smooth_tests_covered", "continuous_distributional_state_map_constructed", "energy_image_evolution_wellposed"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("bare_extensional_smooth_tests_uniformly_named", "full_lf_test_topology_reconstructed", "uniqueness_among_arbitrary_distributions_proved", "strict_causal_support_proved", "green_operator_constructed", "weyl_or_metric_bv_equation_proved", "empirical_calibration_proved", "new_lorentzian_claim"):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    for token in ("Named H2", "right next gate", "not metrizable", "N_F(k)=k+ell(A)", "does not establish"):
        if token not in text:
            errors.append("report token " + token)
    return errors, ["Draft 2020-12 schema", "independent exact checker", "deterministic artifacts", "checker isolation", "96 exact cutoff inequalities", "represented-test completion boundary", "fail-closed LF, uniqueness, and causal boundaries"]


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_CODED_WEAK_WAVE_H2_TEST_COMPLETION_V1: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
