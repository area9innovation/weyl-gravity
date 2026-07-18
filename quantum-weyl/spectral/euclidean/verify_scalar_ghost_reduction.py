"""Independent verifier for the Diff x Weyl scalar ghost reduction."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/DIFF_WEYL_SCALAR_GHOST_REDUCTION.json"
SCHEMA = HERE / "schema/diff-weyl-scalar-ghost-reduction-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _term(lambda_degree: int, r_degree: int, coefficient: Fraction) -> dict[str, int]:
    return {
        "lambda_degree": lambda_degree,
        "R_degree": r_degree,
        "numerator": coefficient.numerator,
        "denominator": coefficient.denominator,
    }


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)

    identity = value["scalar_matrix_identity"]
    matrix = identity["matrix"]
    if matrix != {
        "longitudinal_gauge_from_xi_scalar": [
            _term(0, 1, Fraction(1, 2)),
            _term(1, 0, Fraction(-3, 2)),
        ],
        "longitudinal_gauge_from_weyl_ghost": [],
        "trace_gauge_from_xi_scalar": [_term(1, 0, Fraction(-2))],
        "trace_gauge_from_weyl_ghost": [_term(0, 0, Fraction(8))],
    }:
        raise ValueError("canonical scalar FP matrix drifted")
    expected_determinant = [
        _term(0, 1, Fraction(4)),
        _term(1, 0, Fraction(-12)),
    ]
    expected_target = [
        _term(0, 1, Fraction(-1, 3)),
        _term(1, 0, Fraction(1)),
    ]
    if (
        identity["determinant"] != expected_determinant
        or identity["target_scalar_operator"] != expected_target
        or identity["target_residual"] != []
        or identity["proportionality_constant"] != -12
        or identity["triangular"] is not True
        or identity["verified"] is not True
    ):
        raise ValueError("rank-two to rank-one determinant identity drifted")

    beta_zero = value["gauge_parameter_control"]["beta_zero_matrix"]
    if (
        beta_zero["determinant"] != expected_determinant
        or beta_zero["verified"] is not True
        or beta_zero["triangular"] is not False
    ):
        raise ValueError("beta-independence control drifted")
    mutant = value["negative_control"]["mutated_identity"]
    if mutant["verified"] is not False or not mutant["target_residual"]:
        raise ValueError("Ricci mutation was not rejected")

    target = value["target_match"]
    if (
        target["standard_factor_id"] != "ghost_depth_0"
        or target["standard_M_squared_at_R_12"] != -4
        or target["differential_input_rank"] != 2
        or target["differential_output_factor_rank"] != 1
    ):
        raise ValueError("standard scalar target match drifted")

    for relative, digest in value["provenance"]["source_sha256"].items():
        if _sha256(ROOT / relative) != digest:
            raise ValueError(f"scalar ghost source hash drifted: {relative}")
    return value


def main() -> int:
    verify()
    print("independent Diff x Weyl scalar ghost verifier: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
