#!/usr/bin/env python3
"""Independent exact replay of the anomaly-induced Gamma_1 representative."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
import json

try:
    from .anomaly_induced_nonlocal_gamma1 import OUTPUT, ROOT, build, validate
except ImportError:
    from anomaly_induced_nonlocal_gamma1 import OUTPUT, ROOT, build, validate


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def verify() -> None:
    stored = json.loads(OUTPUT.read_text())
    if stored != build():
        raise ValueError("stored anomaly-induced Gamma1 certificate does not reproduce")
    validate(stored)

    for reference in stored["dependencies"].values():
        path = ROOT / reference["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
            raise ValueError(f"dependency hash drifted: {reference['path']}")

    solve = stored["exact_coefficient_solve"]
    matrix = [[_fraction(entry) for entry in row] for row in solve["weyl_response_matrix"]]
    solution = [_fraction(entry) for entry in solve["solution_vector"]]
    product = [sum((entry * coefficient for entry, coefficient in zip(row, solution)), Fraction()) for row in matrix]
    target = [_fraction(entry) for entry in solve["modified_target_vector"]]
    if product != target:
        raise ValueError("independent Weyl-response matrix replay failed")

    # Ecal4=E4-(2/3)BoxR, so A_Ecal Ecal4+A_box BoxR has
    # repository BoxR coordinate -(2/3)A_Ecal+A_box.
    repository = [target[0], target[1], -Fraction(2, 3) * target[1] + target[2]]
    expected = [_fraction(entry) for entry in solve["source_vector"]]
    if repository != expected or repository != [Fraction(199, 30), Fraction(-87, 20), Fraction()]:
        raise ValueError("independent BoxR=0 scheme conversion failed")

    expanded = stored["anomaly_induced_representative"]["expanded_coefficients"]
    if (
        _fraction(expanded["<Ecal4,G4 C2>"]) != Fraction(199, 120)
        or _fraction(expanded["<Ecal4,G4 Ecal4>"]) != Fraction(-87, 160)
        or _fraction(expanded["integral_R2"]) != Fraction(29, 120)
    ):
        raise ValueError("expanded anomaly-induced coefficients drifted")

    mutations = []
    mutation = deepcopy(stored)
    mutation["claim_flags"]["COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED"] = True
    mutations.append(mutation)
    mutation = deepcopy(stored)
    mutation["decision"]["residual_transfer"] = "AUTHORIZED"
    mutations.append(mutation)
    mutation = deepcopy(stored)
    mutation["green_operator_contract"]["existence_status"] = "UNCONDITIONAL"
    mutations.append(mutation)
    for mutation in mutations:
        try:
            validate(mutation)
        except Exception:
            pass
        else:
            raise ValueError("claim-boundary mutation was accepted")

    print("Anomaly-induced nonlocal Gamma1 independent replay: PASS")


if __name__ == "__main__":
    verify()
