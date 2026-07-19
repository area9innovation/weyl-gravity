#!/usr/bin/env python3
"""Independent replay of symmetric physical mixed-boundary incidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_SYMMETRIC_MIXED_BOUNDARY_INCIDENCE.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-symmetric-mixed-boundary-incidence-v1.schema.json"


def _q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    dependencies = {}
    for name, reference in value["dependencies"].items():
        path = ROOT / reference["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
            raise ValueError(f"dependency drifted: {name}")
        dependencies[name] = json.loads(path.read_text())

    obstruction = dependencies["isolated_triangle_obstruction"]
    contacts = dependencies["generic_contact_projection"]
    for index, row in enumerate(value["channel_rows"]):
        triangle = 6 * _q(obstruction["channel_rows"][index]["log_corner_coefficient"])
        contact = 2 * sum(
            sum(_q(term["coefficient"]) for term in contacts["projection_rows"][11 * leg + index]["single_endpoint_terms"])
            for leg in range(3)
        )
        if (
            _q(row["triangle_full_log_coefficient"]) != triangle
            or _q(row["contact_full_log_coefficient"]) != contact
            or _q(row["combined_log_mu2_coefficient"]) != triangle + contact
        ):
            raise ValueError(f"incidence row drifted: {index}")

    reconstruction = value["equal_box_tensor_reconstruction"]
    if (
        _q(reconstruction["triangle_full_log_coefficient"]) != -sp.Rational(1975, 72)
        or _q(reconstruction["contact_full_log_coefficient"]) != sp.Rational(2704, 27)
        or _q(reconstruction["combined_log_mu2_coefficient"]) != sp.Rational(15707, 216)
    ):
        raise ValueError("equal-box incidence arithmetic drifted")
    if value["M14_disposition"] != {
        "symmetric_point_algebraic_H2_cancellation": "REFUTED",
        "combined_scale_row": "NONZERO",
        "common_Mellin_distribution_extension": "FIXED",
        "generic_box_disposition": "NOT_COMPUTED",
    }:
        raise ValueError("M14 scope drifted")
    print("independent symmetric physical mixed-boundary incidence: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
