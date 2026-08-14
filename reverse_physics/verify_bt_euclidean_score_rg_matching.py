#!/usr/bin/env python3
"""Independent verifier for the BT score/RG matching certificate."""

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
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_SCORE_RG_MATCHING_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-euclidean-score-rg-matching-v1.schema.json",
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


def close(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=2.0e-12, abs_tol=2.0e-14)


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

        source_record = load(data["rg_normalization"]["source_record"])
        if source_record["source_archive_sha256"] != data["rg_normalization"]["source_archive_sha256"]:
            return False
        if "(4*pi)" not in source_record["equations_transcribed"]["field_and_coupling_renormalization"]:
            return False
        if source_record["equations_transcribed"]["three_loop_beta"] != "beta_lambda=-(epsilon/2)*lambda-5*lambda^3-30*lambda^5-(192*zeta(3)+617/2)*lambda^7+...":
            return False
        if source_record["equations_transcribed"]["all_order_relation"] != "gamma_sigma=epsilon/2+beta_lambda/lambda":
            return False

        # Derive the four-dimensional angular factor without using the producer.
        dimension = Fraction(4)
        cos2 = 1 / dimension
        cos4 = Fraction(3, 1) / (dimension * (dimension + 2))
        sin4 = 1 - 2 * cos2 + cos4
        residue = Fraction(4) * sin4 * Fraction(2, 16)
        lattice = data["lattice_log_residue"]
        moments = lattice["sphere_moments"]
        if (decode(moments["mean_cosine_squared"]), decode(moments["mean_cosine_fourth"]), decode(moments["mean_sine_fourth"])) != (cos2, cos4, sin4):
            return False
        if residue != Fraction(5, 16):
            return False
        if decode(lattice["residue_coefficient_over_pi_squared"]) != residue:
            return False
        if lattice["status"] != "PROVED_ANALYTICALLY":
            return False

        # Convert beta_(lambda_MS) to beta_g for g=4*pi*lambda_MS.
        beta0 = Fraction(5, 16)
        beta1 = Fraction(30, 256)
        rg = data["rg_normalization"]
        if decode(rg["beta0_coefficient_over_pi_squared"]) != beta0:
            return False
        if residue != beta0:
            return False
        if beta1 != Fraction(15, 128) or decode(rg["beta1_coefficient_over_pi_fourth"]) != beta1:
            return False

        predecessor = load(
            "reverse_physics/certificates/REVERSE_PHYSICS_BT_PERFECT_SQUARE_RG_SEPARATRIX_V1.json"
        )
        if predecessor["one_loop_beta_restriction"]["restricted_beta_lambda"] != "-5*lambda^3/(16*pi^2)":
            return False
        if predecessor["disposition"]["ps_one_loop_asymptotic_freedom"] != "PROVED_FROM_PUBLISHED_BETA_FUNCTIONS":
            return False

        running = 1 / (2 * beta0)
        matched = residue * running
        loglog = beta1 / (2 * beta0**2)
        refinement = data["matched_refinement"]
        if decode(refinement["running_limit_coefficient_pi_squared"]) != running or running != Fraction(8, 5):
            return False
        if decode(refinement["score_limit_exact"]) != matched or matched != Fraction(1, 2):
            return False
        if decode(refinement["two_loop_loglog_coefficient"]) != loglog or loglog != Fraction(3, 5):
            return False
        if refinement["status"] != "LEADING_AND_TWO_LOOP_RUNNING_MATCHED":
            return False

        score_predecessor = load(
            "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CUBIC_SCORE_LOG_OBSTRUCTION_V1.json"
        )
        table = {
            row["length"]: row["coefficient_C_L"]
            for row in score_predecessor["numerical_preflight"]["table"]
        }
        rows = data["numerical_preflight"]["slope_rows"]
        if [row["length_pair"] for row in rows] != [[4, 8], [6, 12], [8, 16], [12, 24], [16, 32]]:
            return False
        predicted = float(residue) / math.pi**2
        for row in rows:
            left, right = row["length_pair"]
            slope = (table[right] - table[left]) / math.log(2.0)
            if not close(row["dyadic_slope"], slope):
                return False
            if not close(row["predicted_residue"], predicted):
                return False
            if not close(row["slope_over_predicted_residue"], slope / predicted):
                return False

        split = data["scale_setting_split"]
        if split["status"] != "DISTINCT_LIMITS_CERTIFIED":
            return False
        ward = data["finite_lattice_ward_gate"]
        fixture = ward["exact_shifted_gaussian_fixture"]
        kappa = decode(fixture["kappa"])
        radius = decode(fixture["R"])
        if (kappa, radius) != (2, 5):
            return False
        if decode(fixture["conditional_full_score_variance"]) != kappa:
            return False
        if decode(fixture["conditional_expected_hessian"]) != kappa:
            return False
        if decode(fixture["annealed_zero_fiber_score_variance"]) != kappa**2 * radius**2 or kappa**2 * radius**2 != 100:
            return False
        if ward["status"] != "FULL_SCORE_IDENTITY_PROVED_ZERO_FIBER_TRANSFER_OBSTRUCTED_LOGICALLY":
            return False
        disposition = data["method_disposition"]
        required = {
            "lattice_score_logarithmic_residue": "PROVED",
            "fixed_bare_coupling_leading_score_uniformity": "OBSTRUCTED",
            "rg_matched_leading_score_uniformity": "RESTORED_AT_LEADING_LOG",
            "score_residue_equals_physical_beta0": "PROVED",
            "ordinary_finite_lattice_eom_score_identity": "PROVED",
            "ordinary_eom_to_zero_fiber_score_transfer": "OBSTRUCTED_AS_A_LOGICAL_INFERENCE",
            "bt_specific_zero_fiber_ward_identity": "OPEN",
            "finite_lattice_to_ms_scheme_matching": "OPEN",
            "all_order_leading_log_score_resummation": "OPEN",
            "nonperturbative_annealed_zero_fiber_score_bound": "OPEN",
            "fixed_spacing_large_volume_score_bound": "OPEN",
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
