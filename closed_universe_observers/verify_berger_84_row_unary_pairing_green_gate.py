#!/usr/bin/env python3
"""Independent verification of the Berger 84-row unary completion gate."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
import json

from jsonschema import Draft202012Validator, ValidationError

from closed_universe_observers.generate_berger_84_row_unary_pairing_green_gate import (
    CERTIFICATE,
    DEPENDENCIES,
    SCHEMA,
    SOURCE_FILES,
    build,
    two_channel_inverse_defect_counts,
    unary_defect_counts,
)


Matrix = list[list[Fraction]]


def _zero(size: int = 2) -> Matrix:
    return [[Fraction(0) for _ in range(size)] for _ in range(size)]


def _identity(size: int = 2) -> Matrix:
    return [[Fraction(row == column) for column in range(size)] for row in range(size)]


def _add(*values: Matrix) -> Matrix:
    return [
        [sum(value[row][column] for value in values) for column in range(len(values[0][0]))]
        for row in range(len(values[0]))
    ]


def _scale(value: Matrix, coefficient: Fraction | int) -> Matrix:
    return [[Fraction(coefficient) * item for item in row] for row in value]


def _matmul(left: Matrix, right: Matrix) -> Matrix:
    return [
        [sum(left[row][middle] * right[middle][column] for middle in range(len(right))) for column in range(len(right[0]))]
        for row in range(len(left))
    ]


def _transpose(value: Matrix) -> Matrix:
    return [list(row) for row in zip(*value)]


def _block_multiply(left: list[list[Matrix]], right: list[list[Matrix]]) -> list[list[Matrix]]:
    return [
        [_add(*(_matmul(left[row][middle], right[middle][column]) for middle in range(len(right)))) for column in range(len(right[0]))]
        for row in range(len(left))
    ]


def _independent_two_channel_specialization(delete_cross: bool = False) -> tuple[list[list[Matrix]], list[list[Matrix]]]:
    """Specialize every abstract operator to exact rational 2x2 matrices."""

    M = [[Fraction(2), Fraction(1)], [Fraction(1), Fraction(1)]]
    G = [[Fraction(1), Fraction(-1)], [Fraction(-1), Fraction(2)]]
    T0 = [[Fraction(1), Fraction(1)], [Fraction(0), Fraction(1)]]
    H0 = [[Fraction(1), Fraction(-1)], [Fraction(0), Fraction(1)]]
    T1 = [[Fraction(2), Fraction(0)], [Fraction(1), Fraction(1)]]
    H1 = [[Fraction(1, 2), Fraction(0)], [Fraction(-1, 2), Fraction(1)]]
    T0s, J0 = _transpose(T0), _transpose(H0)
    T1s, J1 = _transpose(T1), _transpose(H1)
    B0 = [[Fraction(1), Fraction(2)], [Fraction(0), Fraction(1)]]
    B1 = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(1)]]
    B0s, B1s = _transpose(B0), _transpose(B1)
    kappa = Fraction(3, 2)
    z = _zero()
    K = [
        [M, z, z, _scale(B0s, -kappa), _scale(B1s, -kappa)],
        [z, z, z, T0s, z],
        [z, z, z, z, T1s],
        [_scale(B0, -kappa), T0, z, z, z],
        [_scale(B1, -kappa), z, T1, z, z],
    ]
    E = [[deepcopy(z) for _ in range(5)] for _ in range(5)]
    E[0][0] = G
    for a, (H, B, J) in enumerate(((H0, B0, J0), (H1, B1, J1))):
        m, p = 1 + a, 3 + a
        E[0][m] = _scale(_matmul(_matmul(G, _transpose(B)), J), kappa)
        E[m][0] = _scale(_matmul(_matmul(H, B), G), kappa)
        E[m][p] = H
        E[p][m] = J
        for b, (Bb, Jb) in enumerate(((B0, J0), (B1, J1))):
            mb = 1 + b
            E[m][mb] = _scale(_matmul(_matmul(_matmul(_matmul(H, B), G), _transpose(Bb)), Jb), kappa * kappa)
    if delete_cross:
        E[1][2] = deepcopy(z)
    return K, E


def _check_inverse(delete_cross: bool = False) -> bool:
    K, E = _independent_two_channel_specialization(delete_cross=delete_cross)
    z, one = _zero(), _identity()
    expected = [[deepcopy(one if row == column else z) for column in range(5)] for row in range(5)]
    return _block_multiply(K, E) == expected and _block_multiply(E, K) == expected


def _semantic_boundary(value: dict) -> None:
    flags = value["flags"]
    required_true = (
        "SHIFTED_BACKGROUND_EULER_AXES_CERTIFIED",
        "84_ROW_ODD_PAIRING_NONDEGENERATE",
        "TWO_CHANNEL_MEMORY_MAXWELL_UNARY_NILPOTENT_CYCLIC",
        "TWO_CHANNEL_MEMORY_MAXWELL_ADVANCED_RETARDED_GREEN",
        "BASE_MEMORY_72_ROW_CAUSAL_SUBCOMPLEX_CERTIFIED",
        "ROD_DIAGONAL_WAVE_CANDIDATE_EXPORTED",
    )
    required_false = (
        "SHIFTED_BACKGROUND_MIXED_AND_ALL_ORDERS_CERTIFIED",
        "ROD_GRAVITY_BV_BLOCKS_EXPORTED",
        "84_ROW_Q1_CERTIFIED",
        "84_ROW_UNARY_CYCLICITY_CERTIFIED",
        "84_ROW_ADVANCED_RETARDED_GREEN_CERTIFIED",
        "84_ROW_K_BERGER_EQUIVARIANCE_CERTIFIED",
        "QUANTUM_CLAIM",
    )
    if not all(flags[key] is True for key in required_true):
        raise ValueError("certified partial block was demoted")
    if not all(flags[key] is False for key in required_false):
        raise ValueError("full 84-row gate was over-promoted")
    included = value["base_memory_72_row_subcomplex"]["included_indices"]
    expected = list(range(64)) + [70, 71, 72, 73, 80, 81, 82, 83]
    if included != expected or len(set(included)) != 72:
        raise ValueError("72-row subcomplex indices drifted")
    missing_ids = [row["id"] for row in value["rod_completion_ledger"]["required_missing_blocks"]]
    if missing_ids != ["Gamma_R", "Gamma_R_sharp", "K_Rh", "K_hR", "Delta_K_hh", "W_rod"]:
        raise ValueError("rod completion interface drifted")


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("84-row unary completion gate is stale")
    for name, path in DEPENDENCIES.items():
        expected = hashlib.sha256(path.read_bytes()).hexdigest()
        if value["dependency_refs"][name]["sha256"] != expected:
            raise ValueError(f"dependency hash drifted: {name}")
    manifest = {entry["path"]: entry["sha256"] for entry in value["provenance"]["source_manifest"]}
    for path in SOURCE_FILES.values():
        expected_path = str(path.relative_to(CERTIFICATE.parents[2]))
        if manifest.get(expected_path) != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"source hash drifted: {expected_path}")
    if not _check_inverse():
        raise ValueError("independent exact two-channel inverse failed")
    if _check_inverse(delete_cross=True):
        raise ValueError("cross-detector Green mutation was not detected")
    if sum(two_channel_inverse_defect_counts(delete_cross_01=True)) == 0:
        raise ValueError("abstract cross-detector Green mutation was not detected")
    if unary_defect_counts(maxwell_compatible=False)[0] != 4:
        raise ValueError("Maxwell compatibility mutation was not detected")
    if unary_defect_counts(cotangent_sign=-1)[1] != 4:
        raise ValueError("cotangent-sign mutation was not detected")
    _semantic_boundary(value)
    for key in (
        "ROD_GRAVITY_BV_BLOCKS_EXPORTED",
        "84_ROW_Q1_CERTIFIED",
        "84_ROW_UNARY_CYCLICITY_CERTIFIED",
        "84_ROW_ADVANCED_RETARDED_GREEN_CERTIFIED",
        "84_ROW_K_BERGER_EQUIVARIANCE_CERTIFIED",
        "QUANTUM_CLAIM",
    ):
        mutant = deepcopy(value)
        mutant["flags"][key] = True
        try:
            _semantic_boundary(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"overclaim mutation accepted: {key}")
    schema_mutant = deepcopy(value)
    schema_mutant["unexpected"] = True
    try:
        Draft202012Validator(schema).validate(schema_mutant)
    except ValidationError:
        pass
    else:
        raise ValueError("strict-schema mutation accepted")
    return value


def main() -> int:
    verify()
    print("BERGER_84_ROW_UNARY_PAIRING_GREEN_GATE independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
