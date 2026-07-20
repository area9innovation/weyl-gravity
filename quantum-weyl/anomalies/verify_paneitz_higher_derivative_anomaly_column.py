#!/usr/bin/env python3
"""Independent exact replay of the Paneitz anomaly column and lattice."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ

try:
    from local_bv.schema_validation import validate_instance
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from local_bv.schema_validation import validate_instance


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/PANEITZ_HIGHER_DERIVATIVE_ANOMALY_COLUMN.json"
SCHEMA = HERE / "schema/paneitz-higher-derivative-anomaly-column-v1.schema.json"
SOURCES = (
    "paneitz_higher_derivative_anomaly_column.py",
    "paneitz_higher_derivative_anomaly_column_certificate.py",
    "verify_paneitz_higher_derivative_anomaly_column.py",
    "schema/paneitz-higher-derivative-anomaly-column-v1.schema.json",
    "tests/test_paneitz_higher_derivative_anomaly_column.py",
    "../reports/paneitz-higher-derivative-anomaly-column.md",
)
Q = Fraction


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def _fraction(row: dict[str, int]) -> Fraction:
    return Q(row["numerator"], row["denominator"])


def _vector(rows: list[dict[str, int]]) -> tuple[Fraction, ...]:
    return tuple(_fraction(row) for row in rows)


def verify_payload(value: dict[str, Any]) -> None:
    errors = validate_instance(value, _load(SCHEMA))
    if errors:
        raise ValueError(f"Paneitz schema failed: {errors}")
    for pin in value["input_pins"].values():
        path = ROOT / pin["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != pin["sha256"]:
            raise ValueError("Paneitz dependency hash failed")

    k = 2
    a_gjms = Q(k**3, 144) - Q(k**5, 240)
    beta = Q(k, 180)
    c_gjms = a_gjms + beta
    r2 = sum(
        Q(i * i * (i + 1) * (i + 1), 288) - Q(1, 2160)
        for i in range(k)
    )
    w2 = sum(Q(1, 180) for _ in range(k))
    casimir = -Q(k**3 * (2 * k**2 - 5), 720)
    gamma = 16 * (a_gjms - casimir)
    box_r = (4 * a_gjms - gamma) / 6
    expected = (c_gjms, -a_gjms, Q(0), box_r)
    if (
        a_gjms != Q(-7, 90)
        or beta != Q(1, 90)
        or r2 != -a_gjms / 6
        or w2 != beta
        or casimir != Q(-1, 30)
        or gamma != Q(-32, 45)
        or expected != (Q(-1, 15), Q(7, 90), Q(0), Q(1, 15))
        or _vector(value["verified_column"]["coordinates"]) != expected
    ):
        raise ValueError("independent Paneitz coefficient replay failed")
    routes = value["coefficient_routes"]
    if any(_vector(route["column"]) != expected for route in routes.values()):
        raise ValueError("Paneitz two-route mismatch")
    spectral = routes["factorized_spectral_and_Casimir"]
    if (
        _fraction(spectral["summed_R2_b4"]) != r2
        or _fraction(spectral["summed_W2_b4"]) != w2
        or _fraction(spectral["improved_Casimir_energy"]) != casimir
        or _fraction(spectral["gamma_DeltaJ"]) != gamma
    ):
        raise ValueError("Paneitz factorized route payload failed")

    projected = value["projected_anomaly_lattice"]
    matrix = sp.Matrix(projected["integer_matrix_scaled_by_720"])
    rhs = sp.Matrix(projected["right_hand_side"])
    smith = smith_normal_form(matrix, domain=ZZ)
    invariants = [
        abs(int(smith[i, i]))
        for i in range(min(smith.shape))
        if smith[i, i]
    ]
    particular = sp.Matrix(projected["particular_solution"])
    kernel = [sp.Matrix(row) for row in projected["kernel_basis"]]
    fixture_values = projected["first_solution_by_minimal_vector_count"][
        "multiplicities"
    ]
    fixture = sp.Matrix(
        [
            fixture_values["N_s"],
            fixture_values["N_W_absolute"],
            fixture_values["N_D"],
            fixture_values["N_vector"],
            fixture_values["N_Paneitz"],
        ]
    )
    if (
        invariants != [1, 30]
        or matrix * particular != rhs
        or any(matrix * row != sp.zeros(2, 1) for row in kernel)
        or matrix * fixture != rhs
        or list(fixture) != [0, 0, 0, 61, 191]
    ):
        raise ValueError("independent projected lattice replay failed")
    for vector_count in range(61):
        upper = 8 + 3 * vector_count
        lower = (308 + 20 * vector_count + 7) // 8
        if lower <= upper:
            raise ValueError("minimal-vector witness failed")

    raw = value["raw_reference_scheme_lattice"]
    raw_matrix = sp.Matrix(raw["integer_matrix_scaled_by_720"])
    raw_rhs = sp.Matrix(raw["right_hand_side"])
    separator = sp.Matrix(
        raw["separating_functional"]["coordinates_C2_E4_BoxR"]
    )
    gravity = sp.Matrix([Q(199, 30), Q(-87, 20), Q(0)])
    species = [
        sp.Matrix([Q(1, 120), Q(-1, 360), Q(1, 180)]),
        sp.Matrix([Q(1, 40), Q(-11, 720), Q(1, 60)]),
        sp.Matrix([Q(1, 20), Q(-11, 360), Q(1, 30)]),
        sp.Matrix([Q(1, 10), Q(-31, 180), Q(-1, 10)]),
        sp.Matrix([expected[0], expected[1], expected[3]]),
    ]
    if (
        (separator.T * gravity)[0] != Q(37, 20)
        or any((separator.T * row)[0] <= 0 for row in species)
    ):
        raise ValueError("raw-scheme dual separator failed")
    modular = raw["integer_modular_obstruction"]
    y = modular["left_row_on_C2_E4_BoxR"]
    modulus = modular["modulus"]
    columns = [
        sum(y[i] * int(raw_matrix[i, j]) for i in range(3))
        for j in range(raw_matrix.cols)
    ]
    target = sum(y[i] * int(raw_rhs[i]) for i in range(3))
    if any(entry % modulus for entry in columns) or target % modulus != 2:
        raise ValueError("raw-scheme modular obstruction failed")

    if (
        value["operator_payload"]["principal_symbol"]
        != "(g^{mu nu} xi_mu xi_nu)^2"
        or "det_prime(P4)" not in value["operator_payload"]["zero_mode_policy"]
        or value["kinetic_sign_audit"]["opposite_residues"] is not True
        or value["kinetic_sign_audit"]["healthy_standard_sign_matter"] is not False
        or value["next_gauge_field_gate"]["column_appended"] is not False
        or value["claim_flags"]["HIGHER_DERIVATIVE_GAUGE_COLUMN_VERIFIED"]
        is not False
    ):
        raise ValueError("Paneitz operator/sign/gauge boundary failed")
    manifest = {
        path: hashlib.sha256((HERE / path).read_bytes()).hexdigest()
        for path in SOURCES
    }
    if value["provenance"]["source_manifest"] != manifest:
        raise ValueError("Paneitz source manifest drifted")


def verify() -> dict[str, Any]:
    value = _load(OUTPUT)
    verify_payload(value)
    print("Paneitz higher-derivative anomaly independent replay: PASS")
    return value


if __name__ == "__main__":
    verify()
