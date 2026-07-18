#!/usr/bin/env python3
"""Independent replay of the FV-conformized C2 logarithmic carrier."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
import json

try:
    from .fv_conformized_c2_log_gamma1 import OUTPUT, ROOT, build, validate
except ImportError:
    from fv_conformized_c2_log_gamma1 import OUTPUT, ROOT, build, validate


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def verify() -> None:
    stored = json.loads(OUTPUT.read_text())
    if stored != build():
        raise ValueError("stored FV conformization certificate does not reproduce")
    validate(stored)

    for reference in stored["dependencies"].values():
        path = ROOT / reference["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
            raise ValueError(f"dependency hash drifted: {reference['path']}")

    scalar = stored["fv_scalar_flat_representative"]
    covariance = stored["weyl_covariance"]
    carrier = stored["conformized_C2_log"]
    cubic = stored["cubic_carrier"]
    weights = covariance["weight_ledger"]
    if (
        _fraction(scalar["yamabe_residual"]) != 0
        or 2 * weights["u"] + weights["metric"] != weights["u_squared_metric"]
        or weights["u_squared_metric"] != 0
        or _fraction(carrier["logarithmic_coefficient"]) != Fraction(-199, 60)
        or carrier["leading_curvature_order"] != 2
        or cubic["first_completion_order"] != 3
        or stored["carrier_crosswalk"]["identity_status"]
        != "DISTINCT_CARRIERS_NO_IDENTIFICATION"
    ):
        raise ValueError("independent FV coefficient/weight/filtration replay failed")

    mutations = []
    for flag in (
        "INDEPENDENT_CUBIC_WEYL_INVARIANT_FORM_FACTORS_COMPUTED",
        "NONLOCAL_R2_FORM_FACTOR_COMPUTED",
        "FINITE_C2_NORMALIZATION_FIXED",
        "ABSOLUTE_DRESSED_RHAT2_NORMALIZATION_FIXED",
        "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED",
        "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
        "RESIDUAL_TRANSFER_AUTHORIZED",
        "LORENTZIAN_CERTIFIED",
    ):
        mutation = deepcopy(stored)
        mutation["claim_flags"][flag] = True
        mutations.append(mutation)
    mutation = deepcopy(stored)
    mutation["decision"]["complete_Gamma1"] = "CERTIFIED"
    mutations.append(mutation)
    mutation = deepcopy(stored)
    mutation["carrier_crosswalk"]["identity_status"] = "IDENTIFIED"
    mutations.append(mutation)
    for mutation in mutations:
        try:
            validate(mutation)
        except Exception:
            pass
        else:
            raise ValueError("FV conformization overclaim mutation was accepted")

    print("FV-conformized C2-log Gamma1 independent replay: PASS")


if __name__ == "__main__":
    verify()
