#!/usr/bin/env python3
"""Independent replay of the scalar-flat Berger Schur surrogate obstruction."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator, ValidationError


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = (
    HERE
    / "certificates/SCALAR_FLAT_BERGER_SCHUR_SURROGATE_OBSTRUCTION.json"
)
SCHEMA = (
    HERE
    / "schema/scalar-flat-berger-schur-surrogate-obstruction-v1.schema.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _direct_spin_half_replay() -> tuple[sp.Matrix, sp.Matrix]:
    """Use explicit Pauli matrices, not the producer's Casimir formula."""

    imaginary = sp.I
    j1 = sp.Matrix([[0, 1], [1, 0]]) / 2
    j2 = sp.Matrix([[0, -imaginary], [imaginary, 0]]) / 2
    j3 = sp.diag(sp.Rational(1, 2), sp.Rational(-1, 2))
    delta = j1**2 + j2**2 + sp.Rational(1, 4) * j3**2
    d_w = 2 * (j1**2 + j2**2) - j3**2
    return sp.simplify(delta), sp.simplify(d_w)


def verify(payload: dict | None = None) -> None:
    schema = json.loads(SCHEMA.read_text())
    if payload is None:
        payload = json.loads(CERTIFICATE.read_text())
    Draft202012Validator.check_schema(schema)
    try:
        Draft202012Validator(schema).validate(payload)
    except ValidationError as exc:
        raise ValueError("Berger Schur obstruction schema rejected payload") from exc

    dependencies = payload["dependencies"]
    expected = {
        "receiver_shortfall": (
            "quantum-weyl/spectral/euclidean/certificates/"
            "BACKGROUND_SPECIFIC_FIVE_FORM_FACTOR_SPECTRAL_REALIZATION_"
            "SHORTFALL.json",
            "45c0debd97f904f80d4454d69582515761a97eafb83e9babc69af91eadcab890",
        ),
        "normalized_Schur_operator": (
            "quantum-weyl/spectral/euclidean/certificates/"
            "GENERIC_BACKGROUND_GHOST_LONGITUDINAL_SCHUR_RESUMMATION.json",
            "b40ec3a8bd3a21d8e0ece7c98f98e1776e8c47d557b8c8b5427e422b60c65a78",
        ),
    }
    for name, (relative, digest) in expected.items():
        path = ROOT / relative
        assert dependencies[name]["path"] == relative
        assert dependencies[name]["sha256"] == digest
        assert _sha256(path) == digest

    background = payload["scope"]["background"]
    assert background["metric"] == (
        "g=dtheta^2+sigma1^2+sigma2^2+4 sigma3^2"
    )
    assert [_fraction(x) for x in background["ricci_orthonormal_diagonal"]] == [
        Fraction(0),
        Fraction(-1),
        Fraction(-1),
        Fraction(2),
    ]
    assert _fraction(background["scalar_curvature"]) == 0

    delta, d_w = _direct_spin_half_replay()
    identity = sp.eye(2)
    assert delta == sp.Rational(9, 16) * identity
    assert d_w == sp.Rational(3, 4) * identity
    surrogate_derivative = sp.simplify(delta.inv() * d_w / 3)
    true_derivative = sp.simplify(-delta.inv() * d_w * delta.inv() / 3)
    assert surrogate_derivative == sp.Rational(4, 9) * identity
    assert true_derivative == sp.Rational(-64, 81) * identity
    assert surrogate_derivative != true_derivative

    lowest = payload["operator_obstruction"]["lowest_block"]
    assert _fraction(lowest["Delta_0"]) == Fraction(9, 16)
    assert _fraction(lowest["D_W"]) == Fraction(3, 4)
    assert _fraction(lowest["one_inverse_surrogate_t_derivative"]) == Fraction(
        4, 9
    )
    assert _fraction(lowest["true_normalized_Schur_t_derivative"]) == Fraction(
        -64, 81
    )
    assert lowest["derivatives_agree"] is False

    # Directly contract W=diag(0,2,2,-4) with four unit covectors.
    w_diagonal = [Fraction(0), Fraction(2), Fraction(2), Fraction(-4)]
    direct_symbols = [1 + value / 3 for value in w_diagonal]
    stored_symbols = [
        _fraction(row["surrogate_principal_symbol"])
        for row in payload["operator_obstruction"][
            "surrogate_principal_symbol_witnesses"
        ]
    ]
    assert stored_symbols == direct_symbols == [
        Fraction(1),
        Fraction(5, 3),
        Fraction(5, 3),
        Fraction(-1, 3),
    ]
    assert len(set(stored_symbols)) == 3
    assert payload["operator_obstruction"][
        "normalized_Schur_principal_symbol"
    ] == "1"
    assert payload["operator_obstruction"][
        "requested_surrogate_correction_order"
    ] == 0
    assert payload["operator_obstruction"][
        "normalized_Schur_correction_order"
    ] == -2

    scalar_rows = payload["exact_scalar_decomposition"][
        "lowest_nonconstant_blocks"
    ]
    for row in scalar_rows:
        n = row["n"]
        twice_j = row["twice_j"]
        twice_m = row["twice_m"]
        casimir = Fraction(twice_j * (twice_j + 2), 4)
        weight_squared = Fraction(twice_m * twice_m, 4)
        expected_delta = (
            n * n + casimir - Fraction(3, 4) * weight_squared
        )
        expected_d_w = 2 * casimir - 3 * weight_squared
        assert _fraction(row["Delta_0"]) == expected_delta
        assert _fraction(row["D_W"]) == expected_d_w

    flags = payload["claim_flags"]
    assert flags["SCALAR_FOURIER_SU2_DELTA_AND_DW_BLOCKS_COMPUTED"] is True
    assert flags["ONE_INVERSE_SURROGATE_OBSTRUCTED"] is True
    assert all(
        flag is False
        for name, flag in flags.items()
        if name
        not in {
            "SCALAR_FOURIER_SU2_DELTA_AND_DW_BLOCKS_COMPUTED",
            "ONE_INVERSE_SURROGATE_OBSTRUCTED",
        }
    )
    assert payload["analytic_consequence"][
        "requested_complete_measure_constructible_as_written"
    ] is False
    print("Scalar-flat Berger Schur surrogate obstruction: PASS")


if __name__ == "__main__":
    verify()
