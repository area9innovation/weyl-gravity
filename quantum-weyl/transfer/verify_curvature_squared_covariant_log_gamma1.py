#!/usr/bin/env python3
"""Independent replay of the curvature-squared covariant logarithmic form factor."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
import json

try:
    from .curvature_squared_covariant_log_gamma1 import OUTPUT, ROOT, build, validate
except ImportError:
    from curvature_squared_covariant_log_gamma1 import OUTPUT, ROOT, build, validate


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def verify() -> None:
    stored = json.loads(OUTPUT.read_text())
    if stored != build():
        raise ValueError("stored curvature-squared covariant-log certificate does not reproduce")
    validate(stored)

    for reference in stored["dependencies"].values():
        path = ROOT / reference["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
            raise ValueError(f"dependency hash drifted: {reference['path']}")

    form = stored["covariant_curvature_squared_form_factor"]
    comparison = stored["operator_choice_independence"]
    coefficient = _fraction(form["logarithmic_coefficient"])
    scale_derivative = _fraction(form["mu_log_derivative_on_source_complement"])
    response = _fraction(form["RG_scale_response"])
    order_sum = (
        comparison["left_C_order"]
        + comparison["operator_variation_order"]
        + comparison["right_C_order"]
    )
    if (
        coefficient != Fraction(-199, 60)
        or coefficient * scale_derivative != Fraction(199, 30)
        or response != Fraction(199, 30)
        or form["curvature_order"] != 2
        or order_sum != comparison["first_difference_order"]
        or order_sum != 3
    ):
        raise ValueError("independent curvature-squared coefficient/order replay failed")

    mutations = []
    for flag in (
        "FINITE_C2_NORMALIZATION_FIXED",
        "FINITE_R2_NORMALIZATION_FIXED",
        "COMPLETE_CURVED_WEYL_INVARIANT_REMAINDER_SUPPLIED",
        "EXTENDED_CLASSICAL_CONTRACTION_SUPPLIED",
        "RESIDUAL_TRANSFER_AUTHORIZED",
    ):
        mutation = deepcopy(stored)
        mutation["claim_flags"][flag] = True
        mutations.append(mutation)
    mutation = deepcopy(stored)
    mutation["decision"]["residual_transfer"] = "AUTHORIZED"
    mutations.append(mutation)
    for mutation in mutations:
        try:
            validate(mutation)
        except Exception:
            pass
        else:
            raise ValueError("curvature-squared covariant-log overclaim mutation was accepted")

    print("Curvature-squared covariant-log Gamma1 independent replay: PASS")


if __name__ == "__main__":
    verify()
