#!/usr/bin/env python3
"""Independent exact replay of the flat-TT logarithmic Gamma_1 coefficient."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
import json

try:
    from .flat_tt_logarithmic_gamma1 import OUTPUT, ROOT, build, validate
except ImportError:
    from flat_tt_logarithmic_gamma1 import OUTPUT, ROOT, build, validate


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def verify() -> None:
    stored = json.loads(OUTPUT.read_text())
    if stored != build():
        raise ValueError("stored flat-TT logarithmic Gamma1 certificate does not reproduce")
    validate(stored)

    for reference in stored["dependencies"].values():
        path = ROOT / reference["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
            raise ValueError(f"dependency hash drifted: {reference['path']}")

    form_factor = stored["exact_logarithmic_form_factor"]
    c = _fraction(form_factor["anomaly_C2_coefficient_c"])
    beta2 = _fraction(form_factor["heat_kernel_beta2"])
    coefficient = _fraction(form_factor["logarithmic_coefficient"])
    kernel_derivative = _fraction(form_factor["log_kernel_mu_derivative"])
    response = _fraction(form_factor["RG_scale_response"])
    if (
        c != Fraction(199, 30)
        or beta2 != 2 * c
        or coefficient != -c / 2
        or coefficient != -beta2 / 4
        or coefficient * kernel_derivative != response
        or response != c
    ):
        raise ValueError("independent flat-TT logarithmic coefficient replay failed")

    fixture = stored["flat_TT_fixture"]
    if (
        _fraction(fixture["C1_squared_response"]) != 1
        or _fraction(fixture["R1_response"]) != 0
        or _fraction(fixture["R1_squared_response"]) != 0
        or fixture["anomaly_induced_Riegert_pure_TT_onset"] != "O(h^4)"
    ):
        raise ValueError("independent flat-TT fixture audit failed")

    mutations = []
    mutation = deepcopy(stored)
    mutation["claim_flags"]["FINITE_C2_NORMALIZATION_FIXED"] = True
    mutations.append(mutation)
    mutation = deepcopy(stored)
    mutation["claim_flags"]["GENERAL_CURVED_WEYL_INVARIANT_REMAINDER_SUPPLIED"] = True
    mutations.append(mutation)
    mutation = deepcopy(stored)
    mutation["excluded_promotions"]["zero_momentum"] = "INCLUDED"
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
            raise ValueError("flat-TT logarithmic Gamma1 claim-boundary mutation was accepted")

    print("Flat-TT logarithmic Gamma1 independent replay: PASS")


if __name__ == "__main__":
    verify()
