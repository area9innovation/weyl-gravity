#!/usr/bin/env python3
"""Independent replay of the FV anomaly action and Ricci-sector disposition."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
import json

try:
    from .fv_anomaly_action_ricci_sector import OUTPUT, ROOT, build, validate
except ImportError:
    from fv_anomaly_action_ricci_sector import OUTPUT, ROOT, build, validate


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def verify() -> None:
    stored = json.loads(OUTPUT.read_text())
    if stored != build():
        raise ValueError("stored FV anomaly-action certificate does not reproduce")
    validate(stored)

    for reference in stored["dependencies"].values():
        path = ROOT / reference["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
            raise ValueError(f"dependency hash drifted: {reference['path']}")

    c = _fraction(stored["coefficients"]["c"])
    a = _fraction(stored["coefficients"]["a"])
    ledger = stored["exact_cancellation_ledger"]
    if (
        c != Fraction(199, 30)
        or a != Fraction(87, 20)
        or _fraction(ledger["Ecal4_Sigma_cross_response"])
        + _fraction(ledger["Sigma_Delta4_Sigma_cross_response"])
        != 0
        or _fraction(ledger["Ecal4_induced_BoxR_response"])
        + _fraction(ledger["local_R2_BoxR_response"])
        != 0
    ):
        raise ValueError("independent FV response cancellation failed")

    reconstructed = [
        _fraction(value)
        for value in stored["rft_crosscheck"]["reconstructed_coefficients"]
    ]
    if reconstructed != [c / 4, -a / 8, a / 18]:
        raise ValueError("independent FV/RFT specialization failed")

    mutations = []
    for flag in (
        "SEPARATE_NONLOCAL_R2_FORM_FACTOR_REQUIRED",
        "SEPARATE_NONLOCAL_R2_FORM_FACTOR_COMPUTED",
        "INDEPENDENT_CUBIC_WEYL_FORM_FACTORS_COMPUTED",
        "FINITE_C2_NORMALIZATION_FIXED",
        "ABSOLUTE_EXTENDED_RHAT2_NORMALIZATION_FIXED",
        "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED",
        "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
        "RESIDUAL_TRANSFER_AUTHORIZED",
        "LORENTZIAN_CERTIFIED",
    ):
        mutation = deepcopy(stored)
        mutation["claim_flags"][flag] = True
        mutations.append(mutation)
    mutation = deepcopy(stored)
    mutation["decision"]["independent_nonlocal_R2_form_factor"] = "OPEN"
    mutations.append(mutation)
    mutation = deepcopy(stored)
    mutation["decision"]["complete_Gamma1"] = "CERTIFIED"
    mutations.append(mutation)

    for mutation in mutations:
        try:
            validate(mutation)
        except Exception:
            pass
        else:
            raise ValueError("FV anomaly-action overclaim mutation was accepted")

    print("FV anomaly-action/Ricci-sector independent replay: PASS")


if __name__ == "__main__":
    verify()
