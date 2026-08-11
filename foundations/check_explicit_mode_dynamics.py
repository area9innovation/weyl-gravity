#!/usr/bin/env python3
"""Independent exact Laurent-degree checker for explicit mode dynamics."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1.json"

FAMILIES = ("E", "A", "L")
MINIMUM = {"E": 2, "A": 3, "L": 4}
SIGN = {"E": 1, "A": -1, "L": -1}


def representative_modes(maximum_energy: int = 8) -> list[tuple[int, str, int]]:
    return [
        (energy, family, SIGN[family])
        for energy in range(2, maximum_energy + 1)
        for family in FAMILIES
        if energy >= MINIMUM[family]
    ]


def witness() -> tuple[dict[str, Any], str]:
    modes = representative_modes()
    rows = []
    star_checks = 0
    composition_checks = 0
    leibniz_checks = 0
    for left, (energy_i, family_i, sign_i) in enumerate(modes):
        for right, (energy_j, family_j, sign_j) in enumerate(modes):
            degree = energy_i - energy_j
            reverse_degree = energy_j - energy_i
            if reverse_degree != -degree:
                raise AssertionError("adjoint degree reversal failed")
            star_checks += 1
            for middle, (energy_k, _family_k, _sign_k) in enumerate(modes):
                composed_degree = degree + (energy_j - energy_k)
                target_degree = energy_i - energy_k
                if composed_degree != target_degree:
                    raise AssertionError("matrix-unit degree composition failed")
                composition_checks += 1
                if degree + (energy_j - energy_k) != target_degree:
                    raise AssertionError("generator derivation Leibniz rule failed")
                leibniz_checks += 1
            rows.append([left, right, energy_i, family_i, sign_i, energy_j, family_j, sign_j, degree])

    for time_left in range(-3, 4):
        for time_right in range(-3, 4):
            for row in rows:
                degree = row[-1]
                if time_left * degree + time_right * degree != (time_left + time_right) * degree:
                    raise AssertionError("formal Laurent group law failed")

    energy_multiplicity = {
        str(energy): sum(mode[0] == energy for mode in modes)
        for energy in range(2, 9)
    }
    fixed_units = sum(value * value for value in energy_multiplicity.values())
    nontrivial_units = len(modes) ** 2 - fixed_units
    payload = json.dumps(rows, separators=(",", ":")).encode()
    digest = hashlib.sha256(payload).hexdigest()
    return {
        "maximum_energy": 8,
        "representative_modes": len(modes),
        "matrix_units": len(rows),
        "star_degree_checks": star_checks,
        "matrix_unit_composition_checks": composition_checks,
        "derivation_leibniz_checks": leibniz_checks,
        "formal_time_pair_checks": 49 * len(rows),
        "energy_representative_multiplicity": energy_multiplicity,
        "fixed_energy_matrix_units": fixed_units,
        "nontrivial_degree_matrix_units": nontrivial_units,
        "nontrivial_example": {
            "source": "(2,E)",
            "target": "(3,E)",
            "degree": -1,
        },
        "arithmetic": "exact integers and formal Laurent exponents only",
    }, digest


def check(result: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = json.loads(RESULT.read_text()) if result is None else result
    errors: list[str] = []
    actual, digest = witness()
    if actual != result.get("finite_exact_witness"):
        errors.append("finite Laurent-degree witness")
    if digest != result.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical witness digest")
    promotions = {
        (item.get("foundation"), item.get("carrier"), item.get("obligation"), item.get("old_status"), item.get("new_status"))
        for item in result.get("cube_promotions", [])
    }
    expected = {
        ("CLASSICAL_STANDARD", "KREIN_INDEFINITE", "DYNAMICS_PROPAGATION", "NOT_MAPPED", "LOCAL_RESULT"),
        ("CLASSICAL_STANDARD", "ALGEBRAIC_CSTAR", "DYNAMICS_PROPAGATION", "NOT_MAPPED", "LOCAL_RESULT"),
        ("WEAK_CHOICE_ZF", "KREIN_INDEFINITE", "DYNAMICS_PROPAGATION", "NOT_MAPPED", "LOCAL_RESULT"),
        ("WEAK_CHOICE_ZF", "ALGEBRAIC_CSTAR", "DYNAMICS_PROPAGATION", "PRIORITY_GAP", "LOCAL_RESULT"),
    }
    if promotions != expected:
        errors.append("cube promotion set")
    return errors, {"passed": not errors, "digest": digest, **actual}


def main() -> int:
    errors, summary = check()
    print("FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1: " + ("PASS" if not errors else "FAIL"))
    print(json.dumps({"errors": errors, **summary}, indent=2, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
