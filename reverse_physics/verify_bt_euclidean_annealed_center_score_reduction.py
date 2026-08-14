#!/usr/bin/env python3
"""Independent verifier for the BT annealed-center score reduction."""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_CENTER_SCORE_REDUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-euclidean-annealed-center-score-reduction-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def close(left: float, right: float, tolerance: float = 1.0e-12) -> bool:
    return math.isclose(left, right, rel_tol=tolerance, abs_tol=tolerance)


def independent_summary(run: dict) -> dict[str, float | int]:
    count = sum(block["sample_count"] for block in run["blocks"])

    def average(name: str) -> float:
        return math.fsum(block[name] for block in run["blocks"]) / count

    volume = run["lattice"]["volume"]
    omega = run["mode"]["omega"]
    scale = volume * omega * omega
    t2 = average("sum_t2")
    center2 = average("sum_mode_center2")
    score2 = average("sum_zero_fiber_score2")
    return {
        "sample_count": count,
        "mean_t2": t2,
        "mean_mode_center2": center2,
        "mean_recentered_about_mode2": average("sum_recentered2"),
        "mean_action_density": average("sum_action_density"),
        "mean_zero_fiber_score2": score2,
        "scaled_mode_center2_N_omega2": scale * center2,
        "scaled_zero_fiber_score2_over_N_omega2": score2 / scale,
        "mode_center_fraction_of_raw_t2": center2 / t2,
        "certified_conditional_variance_upper_bound": 9.0 / (2.0 * scale),
        "free_real_mode_variance": 2.0 / scale,
    }


def verify(path: str = CERT_PATH) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
        if list(Draft202012Validator(schema).iter_errors(data)):
            return False
        for source in data["provenance"]["inputs"]:
            if file_hash(source["path"]) != source["sha256"]:
                return False

        reduction = data["exact_center_reduction"]
        coefficient = decode(reduction["curvature_coefficient"])
        if coefficient != Fraction(2, 9):
            return False
        if decode(reduction["sufficient_score_normalization_coefficient"]) != coefficient**2:
            return False
        if reduction["status"] != "PROVED_REDUCTION_ONLY":
            return False
        # If kappa=a*N*omega^2 and E score^2<=Cs*N*omega^2,
        # 3/kappa+2*E(score^2)/kappa^2 has these two coefficients.
        if 3 / coefficient != Fraction(27, 2):
            return False
        if 2 / coefficient**2 != Fraction(81, 2):
            return False

        fixture = data["logical_input_obstruction"]["exact_fixture"]
        kappa = decode(fixture["kappa"])
        radius = decode(fixture["R"])
        hessian_tt = kappa
        hessian_ty = -kappa
        hessian_yy = kappa + 1 / radius**2
        determinant = hessian_tt * hessian_yy - hessian_ty**2
        if determinant != Fraction(2, 25):
            return False
        if decode(fixture["hessian_determinant"]) != determinant:
            return False
        conditional_variance = 1 / hessian_tt
        center_variance = hessian_tt / determinant
        total_variance = hessian_yy / determinant
        score_variance = kappa**2 * center_variance
        if decode(fixture["conditional_variance"]) != conditional_variance:
            return False
        if center_variance != 25 or decode(fixture["center_variance"]) != center_variance:
            return False
        if total_variance != Fraction(51, 2) or decode(fixture["total_t_variance"]) != total_variance:
            return False
        if score_variance != 100 or decode(fixture["zero_fiber_score_variance"]) != score_variance:
            return False
        if decode(fixture["mean_action"]) != 1:
            return False
        if decode(fixture["radial_virial_expectation"]) != 2:
            return False

        diagnostic = data["finite_volume_diagnostic"]
        if file_hash(diagnostic["observation_path"]) != diagnostic["observation_sha256"]:
            return False
        with open(os.path.join(ROOT, diagnostic["observation_path"]), encoding="utf-8") as handle:
            observations = json.load(handle)
        summaries = diagnostic["summaries"]
        if len(observations["runs"]) != len(summaries) != 2:
            return False
        for run, recorded in zip(observations["runs"], summaries):
            independent = independent_summary(run)
            if recorded["length"] != run["lattice"]["length"]:
                return False
            if recorded["volume"] != run["lattice"]["volume"]:
                return False
            for name, value in independent.items():
                if isinstance(value, int):
                    if recorded[name] != value:
                        return False
                elif not close(recorded[name], value):
                    return False
            if recorded["maximum_absolute_mode_score_residual"] >= 1.0e-8:
                return False
            if recorded["maximum_center_score_inequality_residual"] > 1.0e-14:
                return False
            if recorded["scaled_mode_center2_N_omega2"] >= 0.1:
                return False
            if recorded["scaled_zero_fiber_score2_over_N_omega2"] >= 0.02:
                return False

        perturbative = data["perturbative_interface"]
        if perturbative["claim_boundary"] != "PERTURBATIVE_SOURCE_ONLY_NOT_USED_AS_NONPERTURBATIVE_EVIDENCE":
            return False
        disposition = data["method_disposition"]
        if disposition["annealed_zero_fiber_score_bound"] != "OPEN":
            return False
        if disposition["normalized_lowest_mode_second_moment"] != "OPEN":
            return False
        if disposition["actual_interacting_h_minus_one_second_moment"] != "OPEN":
            return False
        if disposition["finite_volume_center_scaling"] != "OBSERVED_L4_L6_NOT_CERTIFIED_UNIFORM":
            return False
        if not all(data["checks"].values()):
            return False
        return True
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else CERT_PATH
    raise SystemExit(0 if verify(target) else 1)
