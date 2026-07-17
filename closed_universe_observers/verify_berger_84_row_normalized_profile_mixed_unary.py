#!/usr/bin/env python3
"""Independent verifier for the normalized-profile mixed Berger unary gate."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from jsonschema import Draft202012Validator, ValidationError
import sympy as sp

from closed_universe_observers.generate_berger_84_row_normalized_profile_mixed_unary import (
    CERTIFICATE,
    DEPENDENCIES,
    SCHEMA,
    SOURCE_FILES,
    build,
)


def _independent_normalization_check() -> None:
    """Use exact finite metric matrices, rather than the producer's tangent formula."""

    r = sp.symbols("r")
    eta = sp.diag(-1, 1, 1, 1)
    theta = sp.Matrix([sp.Rational(3, 4), 0, 0, 0])
    rods = sp.Matrix([[0, 0, 0], [0, 1, 0], [0, 0, 1], [1, 0, 0]])
    fixtures = [
        sp.Matrix([[2, 1, -1, 3], [1, 5, 2, -2], [-1, 2, 7, 1], [3, -2, 1, 11]]),
        sp.Matrix([[-3, 2, 1, -1], [2, 4, -2, 3], [1, -2, 6, 2], [-1, 3, 2, -5]]),
        sp.Matrix([[7, -1, 2, 1], [-1, -2, 3, 2], [2, 3, 5, -4], [1, 2, -4, 9]]),
    ]
    for h in fixtures:
        g = eta + r * h
        inverse = g.inv()
        v = inverse * theta
        s = (theta.T * v)[0]
        projector = inverse - v * v.T / s
        gram = rods.T * projector * rods
        det_gram = sp.factor(gram.det())
        sigma = sp.simplify(sp.diff(det_gram, r).subs(r, 0) / (2 * det_gram.subs(r, 0)))
        d1 = sp.trace(eta * h) / 2
        expected_sigma = -(h[1, 1] + h[2, 2] + h[3, 3]) / 2
        if sp.simplify(sigma - expected_sigma) != 0:
            raise ValueError("independent transverse-Jacobian variation failed")
        if sp.simplify(d1 + sigma + h[0, 0] / 2) != 0:
            raise ValueError("independent coarea variation failed")


def _matrix_nonzero_count(value: sp.Matrix) -> int:
    return sum(sp.simplify(entry) != 0 for entry in value)


def _independent_green_check() -> None:
    """Replay the mixed inverse identity on unrelated exact dense fixtures."""

    fixtures = [
        (
            sp.Matrix([[2, 1, 0], [1, 1, 1], [0, 1, 3]]),
            sp.Matrix([[1, 2, 3], [0, -1, 4], [2, 1, 0]]),
            sp.Matrix([[0, 1, -2], [3, 0, 1], [1, 4, 2]]),
            sp.Matrix([[2, -1, 1], [1, 3, 0], [-2, 1, 5]]),
        ),
        (
            sp.Matrix([[3, 0, 1], [1, 2, 0], [0, 1, 1]]),
            sp.Matrix([[-2, 1, 0], [3, 4, 1], [1, -1, 2]]),
            sp.Matrix([[1, 2, 1], [0, -3, 2], [4, 1, 0]]),
            sp.Matrix([[5, 1, -1], [2, 0, 3], [1, -2, 4]]),
        ),
    ]
    mutation_detected = False
    for K00, K10, K01, K11 in fixtures:
        E00 = K00.inv()
        E10 = -E00 * K10 * E00
        E01 = -E00 * K01 * E00
        direct = E00 * K11 * E00
        E11 = E00 * K10 * E00 * K01 * E00 + E00 * K01 * E00 * K10 * E00 - direct
        left = K00 * E11 + K10 * E01 + K01 * E10 + K11 * E00
        right = E11 * K00 + E10 * K01 + E01 * K10 + E00 * K11
        if _matrix_nonzero_count(left) or _matrix_nonzero_count(right):
            raise ValueError("independent mixed inverse coefficient failed")
        mutant = E11 + direct
        mutant_left = K00 * mutant + K10 * E01 + K01 * E10 + K11 * E00
        mutant_right = mutant * K00 + E10 * K01 + E01 * K10 + E00 * K11
        mutation_detected |= _matrix_nonzero_count(mutant_left) + _matrix_nonzero_count(mutant_right) > 0
    if not mutation_detected:
        raise ValueError("independent direct-Q11 mutation was not detected")


def _semantic_boundary(value: dict) -> None:
    flags = value["flags"]
    required_true = (
        "TRANSVERSE_PROFILE_METRIC_NORMALIZATION_EXPORTED",
        "PROFILE_NORMALIZATION_EXACT",
        "MIXED_Q11_PROFILE_BLOCKS_EXACT",
        "MIXED_Q11_NILPOTENCY_CYCLICITY_CERTIFIED",
        "MIXED_EPSILON_R2_KAPPA_UNARY_CERTIFIED",
        "BIVARIATE_FORMAL_GREEN_COEFFICIENT_CERTIFIED",
        "84_ROW_COEFFICIENTWISE_BIDEGREE_FIRST_JET_CERTIFIED",
    )
    required_false = (
        "FINITE_R_84_ROW_GREEN_HYPERBOLICITY_CERTIFIED",
        "84_ROW_Q2_Q3_CERTIFIED",
        "84_ROW_K_BERGER_EQUIVARIANCE_CERTIFIED",
        "OBSERVER_EVALUATION_MORPHISM_CERTIFIED",
        "DEFORMED_RANK_TWO_CERTIFIED",
        "QUANTUM_CLAIM",
    )
    if not all(flags[key] is True for key in required_true):
        raise ValueError("certified normalized-profile result was demoted")
    if not all(flags[key] is False for key in required_false):
        raise ValueError("normalized-profile result was over-promoted")
    if value["normalization_rule"]["normalization_defect_count"] != 0:
        raise ValueError("normalization defect was hidden")
    if value["mixed_Q11_profile"]["nilpotency_defect_count"] != 0:
        raise ValueError("mixed nilpotency defect was hidden")
    if value["mixed_Q11_profile"]["cyclicity_defect_count"] != 0:
        raise ValueError("mixed cyclicity defect was hidden")
    if value["mixed_Q11_profile"]["nonzero_Q11_operator_block_count"] != 4:
        raise ValueError("mixed Q11 block support drifted")
    if value["mixed_Q11_profile"]["all_other_Q11_carrier_blocks_zero"] is not True:
        raise ValueError("undeclared mixed Q11 blocks entered the carrier")


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("normalized-profile mixed unary certificate is stale")
    for name, path in DEPENDENCIES.items():
        expected = hashlib.sha256(path.read_bytes()).hexdigest()
        if value["dependency_refs"][name]["sha256"] != expected:
            raise ValueError(f"dependency hash drifted: {name}")
    manifest = {entry["path"]: entry["sha256"] for entry in value["provenance"]["source_manifest"]}
    for path in SOURCE_FILES.values():
        relative = str(path.relative_to(CERTIFICATE.parents[2]))
        if manifest.get(relative) != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"source hash drifted: {relative}")
    _independent_normalization_check()
    _independent_green_check()
    _semantic_boundary(value)
    for key in (
        "FINITE_R_84_ROW_GREEN_HYPERBOLICITY_CERTIFIED",
        "84_ROW_Q2_Q3_CERTIFIED",
        "84_ROW_K_BERGER_EQUIVARIANCE_CERTIFIED",
        "OBSERVER_EVALUATION_MORPHISM_CERTIFIED",
        "DEFORMED_RANK_TWO_CERTIFIED",
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
    print("BERGER_84_ROW_NORMALIZED_PROFILE_MIXED_UNARY independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
