#!/usr/bin/env python3
"""Independent verifier for the Plebanski-Hacyan common-zero cone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/PH_HOMOGENEOUS_TWIST_ELL2_EXTRA_BOUNDED_TANGENT_CONE_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/ph-homogeneous-twist-ell2-extra-bounded-tangent-cone-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERT.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if payload["schema_sha256"] != _sha(SCHEMA):
        raise AssertionError("schema hash mismatch")
    for relative, digest in payload["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise AssertionError(f"source hash mismatch: {relative}")

    r, i = sp.sqrt(3), sp.I
    position = sp.Matrix([
        [0, 24 * r, 0, 0],
        [24 * r, 0, 0, sp.Rational(96, 5)],
        [0, 0, 0, 0],
        [0, sp.Rational(24, 5), 0, 0],
    ])
    v0 = sp.Matrix([
        [0, -2 * i, 0, 0],
        [36 * i, 0, 0, -sp.Rational(448, 15) * r * i],
        [0, 0, 0, -4248 * i],
        [0, -sp.Rational(32, 5) * r * i, sp.Rational(81, 2) * i, 0],
    ])
    d_d = sp.diag(72 * r * i, -sp.Rational(104, 27) * r * i, -6 * r * i, 552 * r * i)
    d_a = sp.diag(144 * r * i, -sp.Rational(208, 27) * r * i, -12 * r * i, 1104 * r * i)
    d_b2 = d_a / 2
    if d_b2.det() == 0:
        raise AssertionError("independent b-leading matrix became singular")
    modes = list(range(-2, 3))

    def angular(q: int) -> sp.Matrix:
        fixture = clebsch_gordan(1, 2, 2, 1, 0, 1)
        return sp.Matrix(
            5,
            5,
            lambda row, column: sp.simplify(clebsch_gordan(1, 2, 2, q, modes[column], modes[row]) / fixture)
            if modes[column] + q == modes[row]
            else 0,
        )

    t0, tm, tp = angular(0), angular(-1), angular(1)
    a = sp.symbols("a", real=True)
    for mode in (-2, -1, 0, 1, 2):
        coefficient = t0[mode + 2, mode + 2]
        pencil = a * d_a + coefficient * position
        for root in (root for root in sp.solve(pencil.det(), a) if root != 0):
            kernel = pencil.subs(a, root).nullspace()
            if len(kernel) != 1 or kernel[0][2] != 0:
                raise AssertionError("independent nonzero-a kernel mismatch")
            if sp.simplify(coefficient * v0[2, 3] * kernel[0][3]) == 0:
                raise AssertionError("independent nonzero-a exclusion witness vanished")
    leading = sp.kronecker_product(position, t0)
    basis = sp.Matrix.hstack(*leading.nullspace())
    d, parallel, perpendicular = sp.symbols("d parallel perpendicular", real=True)
    t_a = parallel * t0 + perpendicular * (tm - tp) / sp.sqrt(2)
    reduced = (
        d * sp.kronecker_product(d_d, sp.eye(5))
        + sp.kronecker_product(position, t_a)
        + sp.kronecker_product(v0, t0)
    ) * basis

    d_rows = payload["coefficient_elimination"]["d"]["normalized_B_axis_minor_rows_zero_based"]
    d_minor = sp.factor(reduced[d_rows, :].det())
    if d_minor != sp.Rational(663364720915390660608, 625) * d**12:
        raise AssertionError("independent d minor mismatch")
    if len(reduced.subs({d: 0, perpendicular: 1}).nullspace()) != 2:
        raise AssertionError("off-axis nullity mismatch")
    if len(reduced.subs({d: 0, perpendicular: 0}).nullspace()) != 4:
        raise AssertionError("aligned nullity mismatch")

    flags = payload["classification"]
    if not flags["complete_common_zero_locus_in_declared_nonzero_extra_carrier"]:
        raise AssertionError("complete locus flag missing")
    if flags["off_axis_branch_exists"]:
        raise AssertionError("off-axis branch over-promoted")
    if flags["bounded_second_order_right_inverse_constructed"]:
        raise AssertionError("bounded sufficiency over-promoted")
    parameterization = payload["complete_nonzero_extra_parameterization"]
    if parameterization["energy_balance"] != "beta^2=Q_e^2/2+(2/3)*X":
        raise AssertionError("energy balance changed")
    if "SO(3) rotation" not in parameterization["orbit_statement"]:
        raise AssertionError("orbit statement missing")


if __name__ == "__main__":
    verify()
    print("PH_HOMOGENEOUS_TWIST_ELL2_EXTRA_BOUNDED_TANGENT_CONE_V1 independent verification: PASS")
