#!/usr/bin/env python3
"""Independent verifier for the BT exponential-action/current-spike gate."""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator, ValidationError


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ACTION_EXPONENTIAL_CURRENT_SPIKE_GATE_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-euclidean-action-exponential-current-spike-gate-v1.schema.json")
EXPECTED_SUPPORT = {
    (0, 0, 0, 0): -1,
    (0, 1, 0, 0): 1,
    (1, 0, 0, 0): 1,
    (1, 2, 0, 0): -1,
}


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def frac(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def digest(relative: str) -> str:
    result = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            result.update(block)
    return result.hexdigest()


def dyadic(exponent: int) -> Fraction:
    return Fraction(2**exponent) if exponent >= 0 else Fraction(1, 2 ** (-exponent))


def enumerate_motif(length: int) -> dict:
    points = list(itertools.product(range(length), repeat=4))

    def moved(point, axis, step):
        result = list(point)
        result[axis] = (result[axis] + step) % length
        return tuple(result)

    omega = {point: dyadic(EXPECTED_SUPPORT.get(point, 0)) for point in points}
    residual = {}
    for point in points:
        residual[point] = sum(
            (omega[moved(point, axis, step)] / omega[point] for axis in range(4) for step in (-1, 1)),
            Fraction(-8),
        )
    currents = {}
    for point in points:
        other = moved(point, 0, 1)
        currents[point] = residual[point] * omega[other] / omega[point] - residual[other] * omega[point] / omega[other]
    return {
        "action": sum(value**2 for value in residual.values()) / 2,
        "current": sum(currents.values(), Fraction(0)),
        "residual_count": sum(value != 0 for value in residual.values()),
        "current_count": sum(value != 0 for value in currents.values()),
    }


def verify(path: str = DEFAULT_CERT) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA, encoding="utf-8") as handle:
            Draft202012Validator(json.load(handle)).validate(cert)
        require(cert["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], "dependency boundary drift")
        require(all(digest(item["path"]) == item["sha256"] for item in cert["provenance"]["inputs"]), "input hash drift")

        affine_defect = Fraction(488, 5)
        affine_shift = affine_defect / 2
        coupling_squared = Fraction(4, 25)
        theta = Fraction(25, 8)
        cutoff = Fraction(50)
        log_two_upper = Fraction(7, 10)
        rate = theta * (cutoff - affine_shift) - log_two_upper / 2
        require(theta * coupling_squared == Fraction(1, 2), "MGF radius calculation drift")
        require(rate == Fraction(17, 5), "Chernoff rate calculation drift")

        mgf = cert["actual_gibbs_exponential_moment"]
        require(frac(mgf["affine_shift"]) == affine_shift, "affine shift drift")
        tail = cert["lambda_point_four_bulk_tail"]
        require(frac(tail["lambda"]) == Fraction(2, 5), "coupling drift")
        require(frac(tail["theta"]) == theta, "theta drift")
        require(frac(tail["action_density_cutoff"]) == cutoff, "cutoff drift")
        require(frac(tail["log_two_upper_bound"]) == log_two_upper, "log bound drift")
        require(frac(tail["tail_rate"]) == rate, "tail rate drift")

        degree = 8
        residual_coefficient = 10
        require(2 * residual_coefficient * (residual_coefficient + degree) == 360, "point-current threshold drift")
        require(2 * degree * cutoff + degree**2 * residual_coefficient == 1440, "current l1 threshold drift")

        motif = cert["compact_slice_current_motif"]
        decoded_support = {tuple(item["site"]): item["exponent"] for item in motif["exponent_support"]}
        require(decoded_support == EXPECTED_SUPPORT, "compact motif support drift")
        require(all(sum(value for point, value in EXPECTED_SUPPORT.items() if point[0] == time) == 0 for time in (0, 1)), "rowwise slice cancellation failed")
        fixture_five = enumerate_motif(5)
        fixture_seven = enumerate_motif(7)
        require(fixture_five == fixture_seven, "compact motif volume stability failed")
        require(fixture_five["action"] == Fraction(2085, 16), "compact motif action drift")
        require(fixture_five["current"] == Fraction(339, 16), "compact motif current drift")
        require(motif["nonzero_residual_count"] == fixture_five["residual_count"], "residual support count drift")
        require(motif["nonzero_current_count"] == fixture_five["current_count"], "current support count drift")
        require(frac(motif["action"]) == fixture_five["action"], "serialized motif action drift")
        require(frac(motif["total_time_current"]) == fixture_five["current"], "serialized motif current drift")

        disposition = cert["method_disposition"]
        require(disposition["actual_action_exponential_moment"] == "PROVED", "MGF theorem omitted")
        require(disposition["actual_bulk_action_density_tail"] == "PROVED_EXPONENTIALLY_IN_VOLUME", "bulk tail omitted")
        require(disposition["all_current_carried_by_macroscopic_slabs"] == "OBSTRUCTED_BY_COMPACT_SLICE_MOTIF", "compact motif consequence drift")
        require(disposition["moderate_current_phase_coherence"] == "OPEN", "coherence gate promoted")
        require(disposition["background_marginal_zero_fiber_action_tail"] == "OPEN", "background marginal promoted")
        require(disposition["translation_invariant_current_susceptibility_bound"] == "OPEN", "susceptibility promoted")
        require(disposition["actual_interacting_H_minus_one_second_moment"] == "OPEN", "H-minus-one promoted")
        require(disposition["continuum_limit"] == "NOT_ESTABLISHED", "continuum promoted")
        require(disposition["born_rule"] == "NOT_ESTABLISHED", "Born promoted")
        require(disposition["krein_reconstruction"] == "NOT_ASSESSED", "Krein promoted")
        require(disposition["lorentzian_transfer"] == "NOT_ESTABLISHED", "Lorentzian promoted")
        require(all(cert["checks"].values()), "producer check false")
        return True
    except (OSError, KeyError, TypeError, ValueError, VerificationError, ValidationError):
        return False


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CERT
    ok = verify(path)
    print("BT exponential-action/current-spike gate: PASS" if ok else "BT exponential-action/current-spike gate: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
