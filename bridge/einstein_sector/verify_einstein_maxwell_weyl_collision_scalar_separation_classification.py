"""Independent verifier for the all-collision scalar-separation theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_collision_scalar_separation_classification.json"
MASS_SQUARED = {"q_minus": 6 - 2 * sp.sqrt(3), "p_extra": sp.Rational(16, 3), "q_plus": 6 + 2 * sp.sqrt(3)}
CURRENT_SIGN = {"q_minus": -1, "p_extra": 1, "q_plus": 1}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def feature(rho: sp.Expr, n: int, branch: str) -> sp.Matrix:
    omega = sp.sqrt(n * n * rho + MASS_SQUARED[branch])
    return sp.Matrix([omega**2, n * omega, n * n])


def verify() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema_path = ROOT / payload["schema_path"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == sha(schema_path)
    for item in payload["provenance"]["inputs"].values():
        assert item["sha256"] == sha(ROOT / item["path"])

    for row in payload["candidate_rows"]:
        rho = sp.sympify(row["rho"])
        if row["classification"] == "STRICT_SCALAR_SEPARATOR":
            omega_m1 = sp.sqrt(rho + MASS_SQUARED["q_minus"])
            omega_p1 = sp.sqrt(rho + MASS_SQUARED["p_extra"])
            omega_m2 = sp.sqrt(4 * rho + MASS_SQUARED["q_minus"])
            omega_p2 = sp.sqrt(4 * rho + MASS_SQUARED["p_extra"])
            t1 = (omega_m1 + omega_p1) / 2
            t2 = (omega_m2 + omega_p2) / 2
            covector = sp.Matrix([1, t2 / 2 - t1, -t1 * t2 / 2])
            assert row["midpoints"] == {"t1": sp.sstr(t1), "t2": sp.sstr(t2)}
            assert row["separating_covector_abc"] == [sp.sstr(value) for value in covector]
            for coefficient in row["branch_fibre_coefficients"]:
                value = CURRENT_SIGN[coefficient["branch"]] * covector.dot(feature(rho, coefficient["signed_momentum_n"], coefficient["branch"]))
                assert value.is_positive is True
                assert sp.sstr(sp.factor(value)) == coefficient["exact_signed_coefficient"]
        else:
            columns = []
            for item in row["support"]:
                columns.append(CURRENT_SIGN[item["branch"]] * feature(rho, item["signed_momentum_n"], item["branch"]))
            matrix = sp.Matrix.hstack(*columns)
            exact_weights = []
            for column in range(4):
                minor = matrix[:, [j for j in range(4) if j != column]].det()
                exact_weights.append((-1) ** column * minor)
            if exact_weights[0].is_negative is True:
                exact_weights = [-value for value in exact_weights]
            assert all(value.is_positive is True for value in exact_weights)
            assert [sp.sstr(sp.factor(value)) for value in exact_weights] == row["positive_weights"]
            assert all(sp.simplify(value) == 0 for value in matrix * sp.Matrix(exact_weights))

    flags = payload["classification"]
    assert flags["all_21_collision_backgrounds_checked_exactly"]
    assert not flags["floating_point_sign_decision_used"]
    assert flags["universal_positive_rho_opposite_sign_separator_certified"]
    assert flags["fifteen_complete_bounded_generic_cones_are_origin"]
    assert flags["six_positive_farkas_dependences_certified"]
    assert flags["six_scalar_common_zero_sets_nontrivial"]
    assert not flags["six_full_resonance_joined_bounded_cones_classified"]
    assert not flags["cross_background_mode_identification_made"]
    assert not flags["causal_residual_observational_or_quantum_claim"]
    print("EINSTEIN_MAXWELL_WEYL_COLLISION_SCALAR_SEPARATION_CLASSIFICATION verifier: PASS")


if __name__ == "__main__":
    verify()
