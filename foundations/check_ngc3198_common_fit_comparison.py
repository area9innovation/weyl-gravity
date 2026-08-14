#!/usr/bin/env python3
"""Independently check the common-fit result with C++ Bessel functions and Nelder--Mead."""
from __future__ import annotations

import json
import math
from pathlib import Path
import subprocess
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1.json"
SOURCE = ROOT / "foundations/ngc3198_common_fit_checker.cpp"


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = json.loads(RESULT.read_text()) if value is None else value
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="ngc3198-common-fit-") as directory:
        executable = Path(directory) / "checker"
        compiled = subprocess.run(["c++", "-std=c++17", "-O2", str(SOURCE), "-o", str(executable)], text=True, capture_output=True)
        if compiled.returncode:
            return ["C++ compile: " + compiled.stderr.strip()], {}
        run = subprocess.run([str(executable), str(ROOT)], text=True, capture_output=True)
        if run.returncode:
            return ["C++ run: " + run.stderr.strip()], {}
        independent = json.loads(run.stdout)
    by_id = {item["model_id"]: item for item in result.get("models", [])}
    if set(by_id) != set(independent):
        errors.append("model family closure")
        return errors, independent
    for family, checked in independent.items():
        reported = by_id[family]
        for key, checked_value in checked.items():
            reported_value = reported["metrics"]["chi_squared"] if key == "chi_squared" else reported["fitted_parameters"].get(key)
            if reported_value is None:
                errors.append(f"missing parameter {family}.{key}")
                continue
            tolerance = 1e-6 if key == "chi_squared" else 5e-5 * max(1.0, abs(checked_value))
            if not math.isclose(reported_value, checked_value, rel_tol=0.0, abs_tol=tolerance):
                errors.append(f"independent optimizer agreement {family}.{key}: {reported_value} vs {checked_value}")
    ranking = [item["model_id"] for item in sorted(result.get("models", []), key=lambda item: item["metrics"]["AICc"])]
    if result.get("ranking_by_AICc") != ranking or not ranking or ranking[0] != "GR_NFW_DARK_HALO":
        errors.append("AICc ranking closure")
    passed = {key: item["random_error_gate"]["passed"] for key, item in by_id.items()}
    if passed != {"NEWTONIAN_BARYONS_ONLY": False, "GR_NFW_DARK_HALO": True, "MANNHEIM_CONFORMAL_GRAVITY": False}:
        errors.append("fail-closed random-error gates")
    if result.get("claim_flags", {}).get("complete_theory_selected") is not False:
        errors.append("complete-theory boundary")
    return errors, independent


def main() -> int:
    errors, independent = check()
    print("FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors: print("  - " + error)
    else:
        for family, values in independent.items(): print(f"  - {family}: chi2={values['chi_squared']:.9f}")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
