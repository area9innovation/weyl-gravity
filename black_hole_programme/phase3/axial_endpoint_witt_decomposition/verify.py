#!/usr/bin/env python3
"""Independent exact verifier for the axial endpoint Witt decomposition."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"
OMEGA = sp.Symbol("omega", positive=True, real=True)
I = sp.I


class WittError(AssertionError):
    """Raised when the exact Witt certificate or its boundary drifts."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise WittError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expr(value: str | int) -> sp.Expr:
    return sp.sympify(value, locals={"omega": OMEGA, "I": I})


def _matrix(rows: list[list[str | int]]) -> sp.Matrix:
    return sp.Matrix([[_expr(value) for value in row] for row in rows])


def _vector(entries: list[str | int]) -> sp.Matrix:
    return sp.Matrix([_expr(value) for value in entries])


def _equal(left: sp.Expr, right: sp.Expr) -> bool:
    return sp.simplify(left - right) == 0


def _matrix_equal(left: sp.Matrix, right: sp.Matrix) -> bool:
    return left.shape == right.shape and all(
        _equal(left[row, column], right[row, column])
        for row in range(left.rows)
        for column in range(left.cols)
    )


def _dagger(matrix: sp.Matrix) -> sp.Matrix:
    return sp.conjugate(matrix).T


def _strict_sign_on_pilot(expression: sp.Expr, sign: int) -> bool:
    """Certify the simple exact monomial signs used by this result."""
    factored = sp.factor(expression)
    quotient = sp.simplify(factored / OMEGA ** sp.degree(factored, OMEGA))
    if quotient.has(OMEGA):
        return False
    if sign > 0:
        return bool(quotient.is_positive)
    return bool(quotient.is_negative)


def verify_certificate(data: dict[str, Any]) -> None:
    _require(
        data.get("schema") == "phase3-axial-endpoint-witt-decomposition-v1",
        "wrong schema",
    )
    _require(data.get("lifecycle") == "CLASSIFIED", "wrong lifecycle")
    _require(
        data.get("dependency_tags") == ["LORENTZIAN-CAUSAL", "REDUCED-MODE"],
        "dependency boundary drift",
    )
    declaration = data["declaration"]
    _require(
        declaration["frequency_interval"] == ["1/2", "3/4"],
        "pilot interval drift",
    )
    _require(
        declaration["frequency_assumption"]
        == "omega is real and strictly positive",
        "positive-frequency assumption drift",
    )
    _require(
        declaration["coupling_assumption"] == "alpha_W>0",
        "coupling-sign assumption drift",
    )

    imported = data["import"]
    path = Path(imported["path"])
    _require(
        not path.is_absolute() and ".." not in path.parts,
        "unsafe import path",
    )
    full = ROOT / path
    _require(full.is_file(), "missing formal Gram import")
    _require(_sha256(full) == imported["sha256"], "formal Gram hash drift")
    _require(
        len(imported["commit"]) == 40
        and all(character in "0123456789abcdef" for character in imported["commit"]),
        "invalid import commit",
    )
    source = json.loads(full.read_text())
    _require(
        source["normalization"]
        == "i*F^r/(pi*alpha_W), before Stokes endpoint orientation",
        "source normalization drift",
    )
    _require(
        data["pairing_convention"] == "<u,v> = conjugate(u)^T G v",
        "pairing convention drift",
    )

    expected_orders = {
        "Iminus": ["XI0", "XI1", "EI0"],
        "Iplus": ["XI2", "XI3", "EI2"],
    }
    expected_orientations = {"Iminus": -1, "Iplus": 1}
    expected_second_null = {
        "Iminus": "X - 3*E/(4*omega**2)",
        "Iplus": "X + (16*omega**2-5)*E/4",
    }

    for endpoint in ("Iminus", "Iplus"):
        result = data["endpoints"][endpoint]
        _require(
            source[endpoint]["basis"] == expected_orders[endpoint]
            and result["coordinate_basis"] == expected_orders[endpoint],
            f"{endpoint} coordinate order drift",
        )
        orientation = result["orientation_multiplier"]
        _require(
            orientation == expected_orientations[endpoint],
            f"{endpoint} orientation drift",
        )
        raw = _matrix(source[endpoint]["gram_over_pi_alpha"])
        gram = orientation * raw
        _require(_matrix_equal(gram, _dagger(gram)), f"{endpoint} is not Hermitian")

        vectors = result["vectors"]
        E = _vector(vectors["E"])
        X = _vector(vectors["X"])
        Y = _vector(vectors["Y"])
        basis = sp.Matrix.hstack(E, X, Y)
        transformed = sp.simplify(_dagger(basis) * gram * basis)
        expected = _matrix(result["transformed_gram"])
        _require(
            _matrix_equal(transformed, expected),
            f"{endpoint} transformed Gram mismatch",
        )
        _require(
            _equal(basis.det(), _expr(result["basis_determinant"])),
            f"{endpoint} basis determinant mismatch",
        )

        E_norm = sp.simplify((_dagger(E) * gram * E)[0])
        cross = sp.simplify((_dagger(E) * gram * X)[0])
        Y_norm = sp.simplify((_dagger(Y) * gram * Y)[0])
        pair_determinant = sp.simplify(transformed[:2, :2].det())
        X_norm = sp.simplify((_dagger(X) * gram * X)[0])
        second_null = sp.simplify(X - X_norm * E / (2 * cross))
        _require(_equal(E_norm, _expr(result["E_norm"])), f"{endpoint} E is not null")
        _require(
            _equal(cross, _expr(result["E_X_cross"])),
            f"{endpoint} E-X cross mismatch",
        )
        _require(
            _equal(pair_determinant, _expr(result["EX_pair_determinant"])),
            f"{endpoint} pair determinant mismatch",
        )
        _require(
            _equal(
                (_dagger(second_null) * gram * second_null)[0],
                _expr(result["second_null_vector_norm"]),
            ),
            f"{endpoint} derived second Witt vector is not null",
        )
        _require(
            result["second_null_vector"] == expected_second_null[endpoint],
            f"{endpoint} displayed second null vector drift",
        )
        _require(
            _equal((_dagger(Y) * gram * E)[0], 0)
            and _equal((_dagger(Y) * gram * X)[0], 0)
            and _equal((_dagger(E) * gram * Y)[0], 0)
            and _equal((_dagger(X) * gram * Y)[0], 0),
            f"{endpoint} Y orthogonality mismatch",
        )
        _require(
            _equal(Y_norm, _expr(result["Y_norm"])),
            f"{endpoint} Y norm mismatch",
        )

        _require(
            _strict_sign_on_pilot(cross, 1),
            f"{endpoint} cross is not uniformly positive",
        )
        _require(
            _strict_sign_on_pilot(pair_determinant, -1),
            f"{endpoint} pair determinant is not uniformly negative",
        )
        _require(
            _strict_sign_on_pilot(Y_norm, -1),
            f"{endpoint} Y line is not uniformly negative",
        )
        _require(
            sp.simplify(basis.det()).is_zero is False,
            f"{endpoint} basis change is singular",
        )
        split = result["witt_split"]
        _require(
            split["EX_plane_inertia"] == [1, 1, 0]
            and split["Y_line_inertia"] == [0, 1, 0]
            and split["full_inertia"] == [1, 2, 0],
            f"{endpoint} inertia ledger drift",
        )

    conclusion = data["uniform_interval_conclusion"]
    _require(
        conclusion["witt_decomposition"]
        == "(1,1) orthogonal direct sum (0,1)"
        and conclusion["full_inertia"] == [1, 2, 0],
        "uniform Witt conclusion drift",
    )
    _require(
        all(
            conclusion[key] is True
            for key in (
                "basis_changes_invertible",
                "EX_cross_terms_strictly_positive",
                "EX_pair_determinants_strictly_negative",
                "Y_norms_strictly_negative",
                "radicals_zero",
            )
        ),
        "uniform sign or radical conclusion demoted",
    )

    flags = data["claim_flags"]
    _require(
        flags["exact_endpoint_witt_decomposition_certified"] is True
        and flags["uniform_on_closed_pilot_interval"] is True,
        "proved Witt claim demoted",
    )
    for forbidden in (
        "radial_Jordan_origin_certified",
        "time_translation_Jordan_origin_certified",
        "repeated_factor_origin_certified",
        "globally_populated_scattering_channel_certified",
    ):
        _require(flags[forbidden] is False, f"unproved claim promoted: {forbidden}")

    limits = set(data["does_not_establish"])
    _require(
        "that E, X or Y originates from a radial Jordan chain or spectral derivative"
        in limits
        and "that E, X or Y is a time-translation Jordan vector" in limits
        and "a scalar or matrix repeated-factor representation of the Bach operator"
        in limits,
        "Jordan/repeated-factor boundary drift",
    )


def verify() -> None:
    verify_certificate(json.loads(CERTIFICATE.read_text()))
    print("PASS exact axial endpoint Witt decomposition")


if __name__ == "__main__":
    verify()
