#!/usr/bin/env python3
"""Independent integer-elimination replay of the Level-2 braiding no-go."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical/certificates/"
    "COMPENSATOR_KINETIC_BRAIDING_LEVEL2_NO_GO_V1.json"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical/schema/"
    "compensator-kinetic-braiding-level2-no-go-v1.schema.json"
)
IMPORT_HASHES = {
    "visibility": "bfce9fd2897511d43802c504ce10f9342b85f2e3d89ce9c4cb3e66b788905e10",
    "P2_freeze": "9bda4b758616427bdbf401a499ffd2b7cd9dd69a87223f05fcdf636bb31cd533",
    "background_stability": "8a3afc04d72427313fe8770936b03d4f4301277c9783a92e8df6d329e8c0ccba",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _dense(record: dict[str, Any]) -> sp.Matrix:
    value = sp.zeros(record["row_count"], record["column_count"])
    for item in record["entries"]:
        value[item["row"], item["column"]] = sp.sympify(item["coefficient"])
    return value


def _integer_stationary_matrix() -> tuple[sp.Matrix, list[int]]:
    # Reconstructed independently by clearing one denominator per background
    # Euler row, rather than by reading or importing the producer matrix.
    rational = sp.Matrix(
        [
            [0, 36, 3, 1, 0, 0, 0],
            [0, 12, -1, -1, 0, 0, 0],
            [
                sp.Rational(961, 9600),
                sp.Rational(22801, 6400),
                sp.Rational(151, 160),
                1,
                sp.Rational(9, 16),
                -sp.Rational(243, 256),
                0,
            ],
            [
                sp.Rational(403, 9600),
                sp.Rational(20083, 6400),
                -sp.Rational(9, 160),
                -1,
                sp.Rational(9, 16),
                -sp.Rational(81, 256),
                0,
            ],
            [
                sp.Rational(31, 1920),
                -sp.Rational(3473, 1280),
                -sp.Rational(133, 160),
                -1,
                sp.Rational(9, 16),
                -sp.Rational(81, 256),
                0,
            ],
        ]
    )
    scales = [1, 1, 19200, 19200, 3840]
    integer = sp.diag(*scales) * rational
    if any(not value.is_Integer for value in integer):
        raise AssertionError("integer row clearing failed")
    return integer, scales


def _verify_locus(payload: dict[str, Any]) -> None:
    integer, scales = _integer_stationary_matrix()
    serialized = _dense(
        payload["complete_stationary_locus"]["extended_stacked_matrix"]
    )
    recovered = sp.diag(*[sp.Rational(1, x) for x in scales]) * integer
    if recovered != serialized:
        raise AssertionError("SERIALIZED_STATIONARY_MATRIX_MISMATCH")
    K = sp.Matrix(
        [
            sp.Rational(81, 20),
            sp.Rational(27, 3290),
            -sp.Rational(324, 1645),
            sp.Rational(486, 1645),
            sp.Rational(18, 25),
            1,
            0,
        ]
    )
    B = sp.Matrix([0, 0, 0, 0, 0, 0, 1])
    if integer * K != sp.zeros(5, 1) or integer * B != sp.zeros(5, 1):
        raise AssertionError("KERNEL_BASIS_MISMATCH")
    witness = integer[:, :5].det()
    if witness == 0 or integer.rank() != 5 or len(integer.nullspace()) != 2:
        raise AssertionError("RANK_OR_NULLITY_MISMATCH")
    serialized_basis = payload["complete_stationary_locus"]["kernel_basis"]
    if (
        sp.Matrix([sp.sympify(x) for x in serialized_basis["P2_ray"]]) != K
        or sp.Matrix(
            [sp.sympify(x) for x in serialized_basis["pure_braiding_axis"]]
        )
        != B
    ):
        raise AssertionError("SERIALIZED_KERNEL_BASIS_MISMATCH")


def _verify_zero_replay(payload: dict[str, Any]) -> None:
    eps = sp.Symbol("eps")
    metric_atoms = sp.symbols("m1 m2")
    x_atoms = sp.symbols("x2 x3")
    box_atoms = sp.symbols("b1 b2")
    density = sp.expand(
        (1 + eps * metric_atoms[0] + eps**2 * metric_atoms[1])
        * (eps**2 * x_atoms[0] + eps**3 * x_atoms[1])
        * (eps * box_atoms[0] + eps**2 * box_atoms[1])
    )
    if density.coeff(eps, 2) != 0 or density.coeff(eps, 3) != x_atoms[0] * box_atoms[0]:
        raise AssertionError("CYLINDER_ORDER_REPLAY_MISMATCH")
    if _dense(
        payload["independent_cylinder_zero_replay"]["full_metric_clock_Hessian"]
    ) != sp.zeros(11):
        raise AssertionError("NONZERO_BRAIDING_CYLINDER_HESSIAN")


def verify(value: dict[str, Any] | None = None) -> None:
    payload = value if value is not None else json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    for name, expected in IMPORT_HASHES.items():
        path = ROOT / payload["imports"][name]["path"]
        if _sha(path) != expected or payload["imports"][name]["sha256"] != expected:
            raise AssertionError(f"{name} import drifted")
    _verify_locus(payload)
    _verify_zero_replay(payload)
    for field, section in (
        ("imports_sha256", "imports"),
        ("locus_sha256", "complete_stationary_locus"),
        ("cylinder_sha256", "independent_cylinder_zero_replay"),
        ("gates_sha256", "stratified_gate_disposition"),
        ("verdict_sha256", "terminal_verdict"),
    ):
        if payload["content_hashes"][field] != _digest(payload[section]):
            raise AssertionError(f"{field} drifted")
    if (
        payload["stratified_gate_disposition"]["good_locus"]
        != "EMPTY_FOR_ALL_(t,beta)_IN_R2"
        or payload["terminal_verdict"]["selected_level2_action"]
        or payload["terminal_verdict"]["nonlinear_q2_required"]
        or any(payload["claim_flags"].values())
    ):
        raise AssertionError("CLAIM_BOUNDARY_DRIFT")


def main() -> None:
    verify()
    print(
        "COMPENSATOR_KINETIC_BRAIDING_LEVEL2_NO_GO_V1 "
        "independent integer replay: PASS"
    )


if __name__ == "__main__":
    main()
