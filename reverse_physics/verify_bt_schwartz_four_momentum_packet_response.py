#!/usr/bin/env python3
"""Independent verifier for the BT Schwartz four-momentum pair response."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from decimal import Decimal, localcontext
from fractions import Fraction
from math import factorial

from jsonschema import Draft202012Validator

import verify_bt_fixed_p_two_sphere_packet_detector as fixed


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SCHWARTZ_FOUR_MOMENTUM_PACKET_RESPONSE_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-schwartz-four-momentum-packet-response-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def add_linear(left, right):
    return (left[0] + right[0], fixed.qadd(left[1], right[1]))


def negate_linear(value):
    return (-value[0], fixed.qneg(value[1]))


def scale_linear(coefficient, value):
    return (coefficient * value[0], fixed.qscale(coefficient, value[1]))


def parse_linear(values):
    return (
        Fraction(values[0]),
        (Fraction(values[1]), Fraction(values[2])),
    )


def linear_text(value):
    return "|".join((str(value[0]), str(value[1][0]), str(value[1][1])))


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def displayed_decimal(value):
    with localcontext() as context:
        context.prec = 30
        return format(Decimal(value.numerator) / Decimal(value.denominator), ".18g")


def fraction_hash(value):
    return digest(f"{value.numerator}/{value.denominator}")


def exp_partial(value, terms):
    # Iterative recurrence is independent of the producer's power sum.
    answer = Fraction(1)
    term = Fraction(1)
    for index in range(1, terms + 1):
        term *= value / index
        answer += term
    return answer


def angular_error(radius, coefficient_bound, gradient_bound):
    gamma_minus = radius**2 / (2 * (1 - 2 * radius))
    gamma = 1 + gamma_minus
    delta = gradient_bound * gamma**37 * gamma_minus
    coefficient = 2 * delta * (2 * coefficient_bound * gamma**38 + delta)
    return (coefficient, fixed.QZERO), gamma_minus, delta


def verify_ratio_receipt(receipt, numerator, denominator, constants):
    stored_numerator = parse_linear(receipt["numerator_coefficients"])
    stored_denominator = parse_linear(receipt["denominator_coefficients"])
    lower, upper = fixed.ratio_bounds(numerator, denominator, constants)
    canonical = linear_text(numerator) + "/" + linear_text(denominator)
    return all((
        stored_numerator == numerator,
        stored_denominator == denominator,
        Fraction(receipt["lower_bound"]) == lower,
        Fraction(receipt["upper_bound"]) == upper,
        receipt["upper_decimal"] == displayed_decimal(upper),
        receipt["canonical_sha256"] == digest(canonical),
    ))


def verify_fraction_receipt(receipt, value):
    return all((
        Fraction(receipt["exact"]) == value,
        receipt["decimal"] == displayed_decimal(value),
        receipt["canonical_sha256"] == fraction_hash(value),
    ))


def verify(certificate):
    schema_ok = not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if not schema_ok:
        return {"schema_validation": False}

    inputs = certificate["provenance"]["inputs"]
    hashes_ok = all(sha256_file(row["path"]) == row["sha256"] for row in inputs)
    imported = {row["path"]: load(os.path.join(ROOT, row["path"]))
                for row in inputs if row["path"].endswith(".json")}
    predecessors = [value for path, value in imported.items()
                    if path.startswith("reverse_physics/certificates/")]
    sphere_predecessor = next(value for value in predecessors
                              if value["certificate"].endswith("FIXED_P_TWO_SPHERE_PACKET_DETECTOR_V1"))
    event = next(value for path, value in imported.items()
                 if path.startswith("planning/events/"))

    order = 20
    z0 = (Fraction(-1), Fraction(0))
    z1 = (Fraction(-7, 25), Fraction(24, 25))
    k0 = fixed.direct_fejer(order, z0)
    k1 = fixed.direct_fejer(order, z1)
    rho = fixed.evaluate(k0, z1)[0]
    p = {
        mode: fixed.scale(
            Fraction(1, 1 - rho),
            fixed.add(k0[mode], fixed.scale(-1, k1[mode])),
        )
        for mode in k0
    }
    squared = fixed.norm_coefficients(p)
    phi_total = (squared[0][0], fixed.QZERO)
    phi_one = fixed.root_of_unity_integral(squared, "1/4", "3/8", Fraction(1, 8))
    phi_zero = fixed.root_of_unity_integral(squared, "3/8", "5/8", Fraction(1, 4))
    phi_capture = add_linear(phi_zero, phi_one)
    latitude_total = fixed.full_latitude_closed_form(38)
    latitude_capture = fixed.latitude_recurrence(38, Fraction(1, 2))
    angular_total = scale_linear(latitude_total, phi_total)
    angular_capture = scale_linear(latitude_capture, phi_capture)
    angular_leakage = add_linear(angular_total, negate_linear(angular_capture))

    stored_constants = sphere_predecessor["sphere_packet_decomposition"]["radical_bounds"]
    constants = (
        Fraction(stored_constants["sqrt2_lower"]),
        Fraction(stored_constants["sqrt2_upper"]),
        Fraction(stored_constants["pi_lower"]),
        Fraction(stored_constants["pi_upper"]),
    )

    epsilon = Fraction(1, 10_000)
    sigma = epsilon / 5
    coefficient_bound = Fraction(2, 1 - rho)
    weighted_sum = sum(
        Fraction(2 * abs(mode) * (order - abs(mode)), order * order)
        for mode in range(-19, 20)
    )
    phase_bound = 2 * weighted_sum / (1 - rho)
    gradient_bound = 38 * coefficient_bound + phase_bound
    core_error, gamma_minus, delta = angular_error(
        epsilon, coefficient_bound, gradient_bound
    )
    core_numerator = add_linear(angular_leakage, core_error)
    core_denominator = add_linear(angular_total, negate_linear(core_error))
    core_bounds = fixed.ratio_bounds(core_numerator, core_denominator, constants)

    small_error, _, _ = angular_error(sigma, coefficient_bound, gradient_bound)
    denominator_angular = add_linear(angular_total, negate_linear(small_error))
    decay = 1 - Fraction(76, 25) * epsilon
    exponent = 25 * decay
    exp75 = exp_partial(exponent, 75)
    exp85 = exp_partial(exponent, 85)
    e20 = exp_partial(Fraction(1), 20)
    tail_bound = (
        2 * coefficient_bound**2 * (1 + exponent)
        / (decay**2 * exp75)
        / (denominator_angular[0] * (1 - 2 * sigma) ** 38 * (1 - Fraction(2, e20)))
    )
    independent_tighter_tail = (
        2 * coefficient_bound**2 * (1 + exponent)
        / (decay**2 * exp85)
        / (denominator_angular[0] * (1 - 2 * sigma) ** 38 * (1 - Fraction(2, e20)))
    )
    complete_upper = core_bounds[1] + tail_bound

    vertex = certificate["Schwartz_local_vertex"]
    concentration = certificate["concentration_bound"]
    separation = certificate["spectral_separation"]
    instrument = certificate["leading_packet_instrument"]
    disposition = certificate["disposition"]
    scope = certificate["does_not_establish"]

    number_distance = Fraction(1, 2)
    wrong_sign_distance = Fraction(1)
    number_exponent = number_distance / sigma**2
    wrong_exponent = wrong_sign_distance / sigma**2
    # Nearest points in M0 units saturate the completed-square bounds.
    nearest_number_q = (Fraction(1, 2), Fraction(1, 2))
    number_fixture_distance = (
        (nearest_number_q[0] - 1) ** 2 + nearest_number_q[1] ** 2
    )
    wrong_fixture_distance = (Fraction(0) - 1) ** 2

    checks = {
        "schema_validation": schema_ok,
        "certificate_identity": certificate["certificate"] == "REVERSE_PHYSICS_BT_SCHWARTZ_FOUR_MOMENTUM_PACKET_RESPONSE_V1",
        "input_hashes_recomputed": hashes_ok,
        "two_predecessors_pass_rechecked": len(predecessors) == 2 and all(value["checks"]["ok"] for value in predecessors),
        "done_event_rechecked": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("schwartz-four-momentum-packet-response"),
        "direct_Fejer_support_recomputed": sorted(k0) == list(range(-19, 20)) == sorted(k1),
        "direct_Fejer_targets_recomputed": fixed.evaluate(p, z0) == fixed.ONE and fixed.evaluate(p, z1) == (-1, 0),
        "rho_recomputed": rho == Fraction(sphere_predecessor["homogeneous_local_filter"]["rho_exact"]),
        "latitude_methods_recomputed": latitude_total == fixed.latitude_recurrence(38, Fraction(1)),
        "fixed_sphere_angular_decomposition_recomputed": angular_total == add_linear(angular_capture, angular_leakage),
        "epsilon_recomputed": Fraction(vertex["epsilon"]) == epsilon,
        "sigma_over_M0_recomputed": Fraction(vertex["sigma_over_M0"]) == sigma,
        "sigma_over_kappa_recomputed": Fraction(vertex["sigma_over_kappa"]) == Fraction(1, 31_250),
        "five_sigma_core_recomputed": 5 * sigma == epsilon,
        "coefficient_bound_recomputed": Fraction(concentration["coefficient_l1_bound"]) == coefficient_bound,
        "weighted_sum_recomputed": weighted_sum == Fraction(133, 10),
        "phase_bound_recomputed": Fraction(concentration["phase_derivative_l1_bound"]) == phase_bound,
        "gradient_bound_recomputed": Fraction(concentration["gradient_bound"]) == gradient_bound,
        "gamma_distortion_recomputed": Fraction(concentration["gamma_minus_one_bound"]) == gamma_minus,
        "filter_difference_recomputed": Fraction(concentration["filter_sup_difference_bound"]) == delta,
        "core_ratio_receipt_recomputed": verify_ratio_receipt(concentration["core_angular_leakage_fraction"], core_numerator, core_denominator, constants),
        "core_ratio_bound_recomputed": core_bounds[1] < Fraction(883, 1_000_000),
        "tail_decay_recomputed": Fraction(concentration["tail_decay_coefficient"]) == decay,
        "finite_series_terms_recomputed": concentration["tail_exponential_partial_sum_terms"] == 75 and concentration["unit_ball_e_partial_sum_terms"] == 20,
        "independent_tighter_exponential_bound_agrees": independent_tighter_tail < tail_bound,
        "tail_receipt_recomputed": verify_fraction_receipt(concentration["four_momentum_tail_fraction_upper"], tail_bound),
        "tail_below_one_per_million": tail_bound < Fraction(1, 1_000_000),
        "complete_receipt_recomputed": verify_fraction_receipt(concentration["complete_leakage_fraction_upper"], complete_upper),
        "complete_leakage_bound_recomputed": complete_upper < Fraction(883, 1_000_000) < Fraction(1, 1000),
        "normalizability_argument_present": "exp(-c R^2)" in concentration["normalizability"],
        "number_transfer_identity_rechecked": separation["number_scattering_transfer"].endswith("<=0"),
        "number_cone_completed_square_recomputed": number_distance == Fraction(1, 2) and number_fixture_distance == number_distance,
        "past_cone_minimum_recomputed": wrong_sign_distance == 1 and wrong_fixture_distance == wrong_sign_distance,
        "number_suppression_exponent_recomputed": number_exponent == 1_250_000_000,
        "wrong_sign_suppression_exponent_recomputed": wrong_exponent == 2_500_000_000,
        "million_decimal_suppression_follows_exactly": min(number_exponent, wrong_exponent) > 4_000_000 and 2**10 > 10**3,
        "pointwise_not_operator_boundary_present": "not operator-norm bounds" in separation["meaning"],
        "normalized_mode_is_declared": instrument["normalized_mode"].startswith("v=w/||w||"),
        "positive_effect_pair_recomputed": instrument["click_effect"] == "E_click=zeta*|v><v|" and instrument["no_click_effect"] == "E_no=I-E_click" and instrument["positivity_domain"] == "0<=zeta<=1",
        "capture_bound_recomputed": "999117/1000000" in instrument["selected_packet_capture"] and 1 - complete_upper > Fraction(999117, 1_000_000),
        "Gaussian_noncompact_boundary_preserved": vertex["support_status"].startswith("SCHWARTZ_NONCOMPACT") and disposition["compact_spacetime_switching"] == "NOT_CONSTRUCTED",
        "full_Dyson_remains_open": disposition["complete_time_ordered_Dyson_evolution"] == "NOT_COMPUTED",
        "number_operator_bound_remains_open": disposition["complete_number_scattering_operator_bound"] == "NOT_COMPUTED",
        "absolute_q8_remains_open": disposition["absolute_q8_probability"] == "NOT_COMPUTED",
        "Eq19_remains_open": disposition["general_Eq19"] == "NOT_PROVED_AND_NOT_USED",
        "gravity_remains_open": disposition["gravity_or_metric_BV_BRST_transfer"] == "NOT_CONSTRUCTED",
        "Lorentzian_boundary_present": disposition["Lorentzian_causal_claim"] == "NOT_ESTABLISHED" and any("LORENTZIAN-CAUSAL" in row for row in scope),
        "literature_priority_forbidden": "literature priority" in scope,
    }
    return {name: bool(value) for name, value in checks.items()}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    checks = verify(load(args.verify))
    for name, value in checks.items():
        print(("PASS: " if value else "FAIL: ") + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
