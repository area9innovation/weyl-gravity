#!/usr/bin/env python3
"""Independent exact replay of the matter anomaly lattice."""

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
OUTPUT = HERE / "certificates/MATTER_CONTENT_ANOMALY_CANCELLATION_LATTICE.json"
SCHEMA = HERE / "schema/matter-content-anomaly-cancellation-lattice-v1.schema.json"
SOURCES = (
    "matter_content_anomaly_cancellation_lattice.py",
    "matter_content_anomaly_cancellation_lattice_certificate.py",
    "verify_matter_content_anomaly_cancellation_lattice.py",
    "schema/matter-content-anomaly-cancellation-lattice-v1.schema.json",
    "tests/test_matter_content_anomaly_cancellation_lattice.py",
    "../reports/matter-content-anomaly-cancellation-lattice.md",
)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def _fraction(row: dict[str, int]) -> Fraction:
    return Fraction(row["numerator"], row["denominator"])


def _vector(rows: list[dict[str, int]]) -> tuple[Fraction, ...]:
    return tuple(_fraction(row) for row in rows)


def verify_payload(value: dict[str, Any]) -> None:
    errors = validate_instance(value, _load(SCHEMA))
    if errors:
        raise ValueError(f"matter lattice schema failed: {errors}")
    for pin in value["input_pins"].values():
        path = ROOT / pin["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != pin["sha256"]:
            raise ValueError("matter lattice dependency hash failed")
    expected = {
        "real_conformal_scalar": (
            Fraction(1, 120), Fraction(-1, 360), Fraction(0), Fraction(1, 180)
        ),
        "ordinary_homogeneous_conformal_compensator_scalar": (
            Fraction(1, 120), Fraction(-1, 360), Fraction(0), Fraction(1, 180)
        ),
        "left_Weyl_fermion": (
            Fraction(1, 40), Fraction(-11, 720), Fraction(0), Fraction(1, 60)
        ),
        "right_Weyl_fermion": (
            Fraction(1, 40), Fraction(-11, 720), Fraction(0), Fraction(1, 60)
        ),
        "Dirac_fermion": (
            Fraction(1, 20), Fraction(-11, 360), Fraction(0), Fraction(1, 30)
        ),
        "Abelian_gauge_vector": (
            Fraction(1, 10), Fraction(-31, 180), Fraction(0), Fraction(-1, 10)
        ),
    }
    actual = {
        name: _vector(row["vector"])
        for name, row in value["matter_vectors_absolute_determinant"].items()
    }
    if actual != expected:
        raise ValueError("single-field coefficient mutation detected")
    heat = value["coefficient_methods"]["repository_heat_kernel"]["rows"]
    vector_sum = tuple(
        left + right
        for left, right in zip(
            _vector(heat["gauge_one_form_boson_half_logdet"]),
            _vector(heat["gauge_complex_scalar_FP_ghost_minus_logdet"]),
        )
    )
    if vector_sum != expected["Abelian_gauge_vector"]:
        raise ValueError("independent gauge ghost ledger failed")
    index = value["coefficient_methods"]["independent_index_trace"][
        "reconstructed_rows"
    ]
    if any(_vector(index[name]) != vector for name, vector in expected.items()):
        raise ValueError("independent index reconstruction failed")

    matrix = sp.Matrix(value["signed_determinant_lattice"]["integer_matrix_scaled_by_720"])
    rhs = sp.Matrix(value["signed_determinant_lattice"]["right_hand_side"])
    smith = smith_normal_form(matrix, domain=ZZ)
    invariants = [
        abs(int(smith[i, i]))
        for i in range(min(smith.shape))
        if smith[i, i]
    ]
    particular = sp.Matrix(
        value["signed_determinant_lattice"]["particular_solution_Ns_NW_ND_NV"]
    )
    kernel = [
        sp.Matrix(row) for row in value["signed_determinant_lattice"]["kernel_basis"]
    ]
    if (
        invariants != [1, 30]
        or matrix * particular != rhs
        or any(matrix * row != sp.zeros(2, 1) for row in kernel)
        or value["signed_determinant_lattice"][
            "complete_parameterization"
        ]["parameter_domain"]
        != "Z"
        or value["signed_determinant_lattice"][
            "complete_rational_parameterization"
        ]["parameter_domain"]
        != "Q"
    ):
        raise ValueError("independent Smith/lattice replay failed")
    gravity = _vector(value["gravity_vector"])
    if gravity[0] <= 0 or any(vector[0] <= 0 for vector in expected.values()):
        raise ValueError("C2 separating functional failed")
    phase = value["chiral_phase_ledger"]
    if (
        "p=0 for each left or right Weyl determinant"
        not in phase["declared_common_Ward_regulator"]
        or not phase["nonzero_Pontryagin_alternative"].startswith(
            "NOT_ADMITTED_IN_THE_COMMON_BV_COMPLEX:"
        )
    ):
        raise ValueError("chiral Ward-policy mutation detected")
    if (
        value["healthy_nonnegative_classification"][
            "unbounded_nonnegative_integer_lattice"
        ]
        != "EMPTY"
        or value["claim_flags"]["HEALTHY_NONNEGATIVE_CANCELLATION_EXISTS"]
        is not False
    ):
        raise ValueError("healthy matter no-go over-promoted")
    scheme_pin = value["input_pins"]["BoxR_scheme_conversion"]
    scheme = _load(ROOT / scheme_pin["path"])
    if (
        scheme["result_id"] != "WEYL_GRAVITON_BOX_R_SCHEME_CONVERSION"
        or scheme["claim_flags"]["RAW_TO_REPOSITORY_R2_SCHEME_SHIFT_FIXED"]
        is not True
    ):
        raise ValueError("BoxR scheme-conversion provenance failed")
    manifest = {
        path: hashlib.sha256((HERE / path).read_bytes()).hexdigest()
        for path in SOURCES
    }
    if value["provenance"]["source_manifest"] != manifest:
        raise ValueError("matter lattice source manifest drifted")


def verify() -> dict[str, Any]:
    value = _load(OUTPUT)
    verify_payload(value)
    print("matter-content anomaly lattice independent replay: PASS")
    return value


if __name__ == "__main__":
    verify()
