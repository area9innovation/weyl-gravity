#!/usr/bin/env python3
"""Independent integer checker for the explicit E/A/L Krein symmetry."""

from __future__ import annotations

import hashlib
import json
from math import comb
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "foundations/results/FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1.json"


def load_result(path: Path = RESULT_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def cantor_pair(left: int, right: int) -> int:
    total = left + right
    return total * (total + 1) // 2 + right


def mode_code(energy: int, chirality_code: int, family_code: int, coordinate: int) -> int:
    return cantor_pair(cantor_pair(cantor_pair(energy - 2, chirality_code), family_code), coordinate)


def block_dimension(family: str, energy: int) -> int:
    if family == "E":
        return (energy + 3) * (energy - 1)
    if family == "A":
        return (energy + 1) * (energy - 1)
    if family == "L":
        return (energy + 1) * (energy - 3)
    raise ValueError(f"unknown family: {family}")


def occupation_sign(negative_occupancy: int) -> int:
    return -1 if negative_occupancy % 2 else 1


def check(data: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    if data is None:
        data = load_result()
    errors: list[str] = []
    witness = data.get("mode_witness", {})
    families = witness.get("families", [])
    chiralities = witness.get("chiralities", [])
    minima = witness.get("branch_minimum", {})
    signs = witness.get("form_sign", {})
    cutoff = witness.get("regression_cutoff")
    if families != ["E", "A", "L"] or chiralities != [1, -1]:
        errors.append("family or chirality ordering drifted")
    if minima != {"E": 2, "A": 3, "L": 4}:
        errors.append("branch minima drifted")
    if signs != {"E": 1, "A": -1, "L": -1}:
        errors.append("form signs drifted")
    if not isinstance(cutoff, int) or cutoff < 6:
        return ["regression cutoff is invalid"], {}

    level_dimensions: dict[str, int] = {}
    positive = 0
    negative = 0
    codes: set[int] = set()
    expanded: list[list[int | str]] = []
    explicit_positive_energies: set[int] = set()
    explicit_negative_energies: set[int] = set()
    for energy in range(2, cutoff + 1):
        level = 0
        for chirality_code, chirality in enumerate(chiralities):
            for family_code, family in enumerate(families):
                if energy < minima[family]:
                    continue
                dimension = block_dimension(family, energy)
                if dimension <= 0:
                    errors.append(f"nonpositive block dimension: {energy}/{family}")
                sign = signs[family]
                if sign not in (-1, 1) or sign * sign != 1:
                    errors.append(f"bad involution sign: {family}")
                level += dimension
                if sign > 0:
                    positive += dimension
                    explicit_positive_energies.add(energy)
                else:
                    negative += dimension
                    explicit_negative_energies.add(energy)
                for coordinate in range(dimension):
                    code = mode_code(energy, chirality_code, family_code, coordinate)
                    if code in codes:
                        errors.append("mode-code collision")
                    codes.add(code)
                    expanded.append([energy, chirality, family, coordinate, sign, code])
        expected_level = 10 if energy == 2 else 40 if energy == 3 else 6 * energy * energy - 14
        if level != expected_level:
            errors.append(f"level formula failed at energy {energy}")
        level_dimensions[str(energy)] = level

    regression = witness.get("regression", {})
    actual_regression = {
        "level_dimensions": level_dimensions,
        "positive_dimensions_through_cutoff": positive,
        "negative_dimensions_through_cutoff": negative,
        "expanded_cutoff_dimension": positive + negative,
    }
    if regression != actual_regression:
        errors.append("signature or dimension regression drifted")
    if len(codes) != positive + negative:
        errors.append("mode coding is not injective through the cutoff")
    if explicit_positive_energies != set(range(2, cutoff + 1)):
        errors.append("positive tower lacks an explicit mode at some energy")
    if explicit_negative_energies != set(range(3, cutoff + 1)):
        errors.append("negative tower lacks an explicit mode at some allowed energy")

    fock = data.get("fock_construction", {}).get("finite_controls", {})
    if fock.get("dimension_sym2_of_energy2") != comb(10 + 2 - 1, 2):
        errors.append("energy-2 symmetric-square dimension failed")
    two_signs = fock.get("two_mode_signs")
    expected_two_particle = [
        two_signs[0] * two_signs[0],
        two_signs[0] * two_signs[1],
        two_signs[1] * two_signs[1],
    ] if isinstance(two_signs, list) and len(two_signs) == 2 else []
    if expected_two_particle != fock.get("two_mode_sym2_occupation_signs"):
        errors.append("two-mode Fock sign control failed")
    if [occupation_sign(value) for value in range(6)] != [1, -1, 1, -1, 1, -1]:
        errors.append("occupation parity formula failed")

    payload = json.dumps(expanded, separators=(",", ":"), ensure_ascii=True).encode()
    digest = hashlib.sha256(payload).hexdigest()
    expected_digest = data.get("independent_checker", {}).get("expected_cutoff_digest")
    if expected_digest is not None and digest != expected_digest:
        errors.append("cutoff witness digest mismatch")
    summary = {
        "passed": not errors,
        "cutoff": cutoff,
        "positive_dimensions": positive,
        "negative_dimensions": negative,
        "total_dimensions": positive + negative,
        "unique_mode_codes": len(codes),
        "j_signs_self_adjoint_involutive_norm_one": set(signs.values()) == {-1, 1},
        "two_mode_sym2_signs": expected_two_particle,
        "cutoff_witness_digest": digest,
        "arithmetic": "exact natural numbers and signs only",
    }
    return errors, summary


def main() -> int:
    errors, summary = check()
    if errors:
        print("FOUNDATIONAL_KREIN_EXPLICIT_J_CHECKER: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("FOUNDATIONAL_KREIN_EXPLICIT_J_CHECKER: PASS")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
