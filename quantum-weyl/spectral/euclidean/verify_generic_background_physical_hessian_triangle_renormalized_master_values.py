#!/usr/bin/env python3
"""Independently replay the renormalized physical triangle master certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import mpmath as mp
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_RENORMALIZED_MASTER_VALUES.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-triangle-renormalized-master-values-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def verify(value: dict) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    payload = {
        key: value[key]
        for key in (
            "template_rows",
            "sector_substitutions",
            "master_rows",
            "identity_ledger",
        )
    }
    if _digest(payload) != value["formula_digest"]:
        raise ValueError("formula digest mismatch")
    for reference in value["dependencies"].values():
        path = ROOT / reference["path"]
        source = json.loads(path.read_text())
        if _sha256(path) != reference["sha256"] or source["result_id"] != reference["result_id"]:
            raise ValueError(f"dependency mismatch: {path}")

    expected_coefficients = {
        "M14_singlet": ((1, 0, 0), (1, 0, 0), (1, 0, 0)),
        "M15_standard_u": ((1, -2, 1), (-1, 1, 1), (0, 1, -2)),
        "M16_standard_v": ((0, 1, -2), (1, -2, 1), (-1, 1, 1)),
    }
    rows = {row["master_id"]: row for row in value["master_rows"]}
    if set(rows) != set(expected_coefficients):
        raise ValueError("master id set drifted")
    for master_id, expected in expected_coefficients.items():
        actual = tuple(
            tuple(sector["template_coefficients"])
            for sector in rows[master_id]["sector_rows"]
        )
        if actual != expected:
            raise ValueError(f"sector coefficient crosswalk drifted: {master_id}")

    x1, x2, x3, z = sp.symbols("x1 x2 x3 z", positive=True)
    local_dict = {"x1": x1, "x2": x2, "x3": x3, "z": z, "log": sp.log}
    expressions = {
        master_id: sp.sympify(row["renormalized_value"], locals=local_dict)
        for master_id, row in rows.items()
    }
    for master_id, row in rows.items():
        scale = sp.sympify(row["scale_derivative"], locals=local_dict)
        if sp.expand(z * sp.diff(expressions[master_id], z) - scale) != 0:
            raise ValueError(f"scale derivative drifted: {master_id}")

    # Independent direct quadrature of the defining radial finite part.  This
    # checks the integration-by-parts signs in all six universal templates.
    mp.mp.dps = 50
    bx1, bx2, bx3, bz = map(mp.mpf, (2, 3, 5, 7))

    def direct_template(kind: str, half_id: str) -> mp.mpf:
        if half_id == "left":
            radius = lambda t: 1 / (2 - t)
            lower, upper = mp.mpf(0), mp.mpf("0.5")
        else:
            radius = lambda t: 1 / (1 + t)
            lower, upper = mp.mpf("0.5"), mp.mpf(1)

        def outer(t: mp.mpf) -> mp.mpf:
            endpoint = radius(t)
            linear = t * bx1 + (1 - t) * bx2
            correction = t * (1 - t) * bx3 - linear
            h0, h1 = {
                "K0": (mp.mpf(1), mp.mpf(0)),
                "Kp": (mp.mpf(0), mp.mpf(1)),
                "Kq": (mp.mpf(0), t),
            }[kind]
            leading = t * (1 - t) * h0 / linear**4

            def numerator(radial: mp.mpf) -> mp.mpf:
                return (
                    t
                    * (1 - t)
                    * (1 - radial)
                    * (h0 + radial * h1)
                    / (linear + correction * radial) ** 4
                )

            derivative = mp.diff(numerator, 0)

            def subtracted(radial: mp.mpf) -> mp.mpf:
                if radial == 0:
                    return derivative
                return (numerator(radial) - leading) / radial

            return leading * mp.log(endpoint * bz) + mp.quad(
                subtracted, [0, endpoint]
            )

        return mp.quad(outer, [lower, upper])

    direct_point = {x1: 2, x2: 3, x3: 5, z: 7}
    for half_id in ("left", "right"):
        for kind in ("K0", "Kp", "Kq"):
            stored = sp.sympify(
                value["template_rows"][half_id][kind]["value"], locals=local_dict
            )
            exact_value = mp.mpf(str(sp.N(stored.subs(direct_point), 50)))
            if abs(exact_value - direct_template(kind, half_id)) > mp.mpf("1e-35"):
                raise ValueError(f"direct finite-part quadrature failed: {half_id} {kind}")

    # High-precision regressions are not the proof rail; they independently
    # catch branch/sign mistakes in the positive Euclidean log arguments.
    fixtures = ((2, 3, 5, 7), (3, 5, 7, 11))
    for fixture in fixtures:
        point = dict(zip((x1, x2, x3, z), map(sp.Rational, fixture)))
        m14 = expressions["M14_singlet"]
        m15 = expressions["M15_standard_u"]
        m16 = expressions["M16_standard_v"]
        defects = (
            m14.subs({x1: x3, x2: x2, x3: x1}, simultaneous=True) - m14,
            m15.subs({x1: x3, x2: x2, x3: x1}, simultaneous=True) + m15,
            m16.subs({x1: x3, x2: x2, x3: x1}, simultaneous=True) - m15 - m16,
            m14.subs({x1: x1, x2: x3, x3: x2}, simultaneous=True) - m14,
            m15.subs({x1: x1, x2: x3, x3: x2}, simultaneous=True) + m16,
            m16.subs({x1: x1, x2: x3, x3: x2}, simultaneous=True) + m15,
        )
        if any(abs(complex(sp.N(defect.subs(point), 80))) > 1e-60 for defect in defects):
            raise ValueError(f"S3 high-precision regression failed: {fixture}")

    flags = value["claim_flags"]
    if not (
        flags["RENORMALIZED_M14_SINGLET_VALUE_COMPUTED"]
        and flags["RENORMALIZED_STANDARD_S3_PAIR_VALUES_COMPUTED"]
        and flags["RENORMALIZED_SIX_MASTER_VALUES_COMPUTED"]
    ):
        raise ValueError("renormalized master flags are not closed")
    if (
        flags["PHYSICAL_N3_TRIANGLE_MASTER_COORDINATES_COMPUTED"]
        or flags["PHYSICAL_N3_TRIANGLE_INTEGRATED"]
        or flags["REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"]
        or flags["COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED"]
        or flags["COMPLETE_RENORMALIZED_Q1_SUPPLIED"]
        or flags["QME_RESTORED"]
        or flags["RESIDUAL_TRANSFER_AUTHORIZED"]
        or flags["LORENTZIAN_CERTIFIED"]
    ):
        raise ValueError("a downstream lifecycle flag was promoted")


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    verify(value)
    print("generic physical triangle renormalized master values: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
