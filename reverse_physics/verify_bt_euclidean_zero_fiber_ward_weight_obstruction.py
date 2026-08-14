#!/usr/bin/env python3
"""Independent verifier for the BT zero-fiber Ward-weight obstruction."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ZERO_FIBER_WARD_WEIGHT_OBSTRUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-euclidean-zero-fiber-ward-weight-obstruction-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def load(relative: str) -> dict:
    with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
        return json.load(handle)


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

        identities = data["exact_disintegration"]
        required_identities = {
            "integrated_mode_density": "rho(t)=E_nu[q_eta(t)]",
            "first_derivative": "rho'(0)=-E_nu[q_eta(0)*s_eta]",
            "second_derivative": "rho''(0)=E_nu[q_eta(0)*(s_eta^2-H_eta)]",
            "status": "PROVED_BY_FINITE_DIMENSIONAL_DISINTEGRATION_AND_DIFFERENTIATION",
        }
        if any(identities.get(key) != value for key, value in required_identities.items()):
            return False

        change = data["constrained_measure_change"]
        required_change = {
            "radon_nikodym": "dmu_0/dnu=q_eta(0)/rho(0)",
            "inverse_radon_nikodym": "dnu/dmu_0=rho(0)/q_eta(0)",
            "weighted_ward_content": "rho''(0)/rho(0)=E_mu0[s_eta^2-H_eta]",
            "target_identity": "E_nu[s_eta^2]=rho(0)*E_mu0[s_eta^2/q_eta(0)]",
            "status": "EXACT_WEIGHT_MISMATCH_PROVED",
        }
        if any(change.get(key) != value for key, value in required_change.items()):
            return False

        # Recompute the complete shifted-Gaussian fixture independently.
        fixture = data["shifted_gaussian_no_transfer"]["fixture"]
        kappa = decode(fixture["kappa"])
        radius = decode(fixture["R"])
        if (kappa, radius) != (2, 5):
            return False
        marginal_variance = radius**2 + 1 / kappa
        posterior_variance = 1 / (kappa + 1 / radius**2)
        target = kappa**2 * radius**2
        weighted_score = kappa**2 * posterior_variance
        if decode(data["shifted_gaussian_no_transfer"]["marginal_variance"]) != marginal_variance:
            return False
        if decode(data["shifted_gaussian_no_transfer"]["posterior_variance_at_t_zero"]) != posterior_variance:
            return False
        if decode(fixture["unweighted_score_second_moment"]) != target or target != 100:
            return False
        if decode(fixture["q_zero_weighted_score_second_moment_divided_by_rho_zero"]) != weighted_score or weighted_score != Fraction(100, 51):
            return False
        if decode(fixture["q_zero_weighted_hessian_divided_by_rho_zero"]) != kappa:
            return False
        if decode(fixture["rho_second_derivative_divided_by_rho_zero"]) != -1 / marginal_variance:
            return False
        if data["shifted_gaussian_no_transfer"]["status"] != "GENERAL_WEIGHT_REMOVAL_OBSTRUCTED_LOGICALLY":
            return False

        # Independently import only the exact predecessor facts used in the BT step.
        escape = load(
            "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CONDITIONAL_MASS_ESCAPE_OBSTRUCTION_V1.json"
        )
        width = load(
            "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_RUNAWAY_FIBER_WIDTH_BOUND_V1.json"
        )
        if escape["exact_orthogonal_family"]["parameter"] != "m>=2 integer":
            return False
        comparison = escape["all_m_comparison"]
        if comparison["tail_probability_bound"] != "q_m({u>=-m})<=2^(50m-1-D_m)<=2^(-m)":
            return False
        if comparison["global_minimizer_consequence"] != "every global minimizer u_m^* satisfies u_m^*<-m":
            return False
        if width["uniform_lower_bound"]["lower_bound"] != {"numerator": 115, "denominator": 4}:
            return False
        if width["method_disposition"]["runaway_family_uniform_strong_convexity"] != "PROVED":
            return False

        bt = data["bt_runaway_density_obstruction"]
        if bt["coordinate_density_relation"] != "q_eta_m^(t)(0)=q_m^(u)(0)/log(2) because t=u*log(2)":
            return False
        if bt["density_bound"] != "q_m^(u)(0)<=2^-m/m":
            return False
        if bt["inverse_density_bound"] != "1/q_m^(u)(0)>=m*2^m":
            return False
        bt_fixture = bt["exact_m2_fixture"]
        m = bt_fixture["m"]
        tail = Fraction(1, 2**m)
        density = tail / m
        if m != 2 or decode(bt_fixture["tail_probability_upper_bound"]) != tail:
            return False
        if decode(bt_fixture["zero_fiber_density_upper_bound"]) != density or density != Fraction(1, 8):
            return False
        if decode(bt_fixture["inverse_zero_fiber_density_lower_bound"]) != 1 / density or 1 / density != 8:
            return False
        if bt["status"] != "POINTWISE_ZERO_FIBER_DENSITY_LOWER_BOUND_OBSTRUCTED_IN_BT":
            return False

        disposition = data["method_disposition"]
        required = {
            "integrated_marginal_derivative_identities": "PROVED",
            "zero_fiber_constrained_change_of_measure": "PROVED",
            "local_constrained_insertions_are_q_zero_weighted": "PROVED",
            "general_weight_removal_from_marginal_data": "OBSTRUCTED_AS_A_LOGICAL_INFERENCE",
            "bt_background_uniform_q_zero_lower_bound": "OBSTRUCTED",
            "pointwise_constrained_ward_to_annealed_score_transfer": "OBSTRUCTED_AS_FORMULATED",
            "annealed_inverse_density_or_center_bound": "OPEN",
            "bt_specific_annealed_multiscale_score_bound": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        }
        if any(disposition.get(name) != value for name, value in required.items()):
            return False
        if not all(data["checks"].values()):
            return False
        return True
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else CERT_PATH
    raise SystemExit(0 if verify(target) else 1)
