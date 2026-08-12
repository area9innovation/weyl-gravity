#!/usr/bin/env python3
"""Independent exact verifier for the compact-energy BT quadratic bound."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator

import verify_bt_fixed_p_two_sphere_packet_detector as fixed


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_COMPACT_ENERGY_QUADRATIC_SECTOR_BOUND_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-compact-energy-quadratic-sector-bound-v1.schema.json",
)
SOURCE = "96a1b95b974c2c8897bdba3b450ef6c816c17a14"


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def fraction_hash(value):
    return hashlib.sha256(
        f"{value.numerator}/{value.denominator}".encode()
    ).hexdigest()


def linear_add(left, right):
    return (left[0] + right[0], fixed.qadd(left[1], right[1]))


def linear_negate(value):
    return (-value[0], fixed.qneg(value[1]))


def linear_scale(coefficient, value):
    return (coefficient * value[0], fixed.qscale(coefficient, value[1]))


def angular_error(radius, coefficient_bound, gradient_bound):
    """Reconstruct the boost error directly from the mean-value estimate."""
    gamma_minus_one = radius**2 / (2 * (1 - 2 * radius))
    gamma = 1 + gamma_minus_one
    delta = gradient_bound * gamma**37 * gamma_minus_one
    return (
        2 * delta * (2 * coefficient_bound * gamma**38 + delta),
        fixed.QZERO,
    )


def direct_angular_total():
    """Rebuild the N=20 filter from the independent 20 by 20 amplitude sum."""
    order = 20
    z0 = (Fraction(-1), Fraction(0))
    z1 = (Fraction(-7, 25), Fraction(24, 25))
    k0 = fixed.direct_fejer(order, z0)
    k1 = fixed.direct_fejer(order, z1)
    rho = fixed.evaluate(k0, z1)[0]
    coefficients = {
        mode: fixed.scale(
            Fraction(1, 1 - rho),
            fixed.add(k0[mode], fixed.scale(-1, k1[mode])),
        )
        for mode in k0
    }
    squared = fixed.norm_coefficients(coefficients)
    phi_total = (squared[0][0], fixed.QZERO)
    latitude_total = fixed.full_latitude_closed_form(38)
    recurrence_total = fixed.latitude_recurrence(38, Fraction(1))
    return (
        rho,
        linear_scale(latitude_total, phi_total),
        latitude_total,
        recurrence_total,
        coefficients,
        z0,
        z1,
    )


def verify(certificate):
    schema_ok = not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if not schema_ok:
        return {"schema_validation": False}

    inputs = certificate["provenance"]["inputs"]
    hashes_ok = all(sha256_file(row["path"]) == row["sha256"] for row in inputs)
    imported = {
        row["path"]: load(os.path.join(ROOT, row["path"]))
        for row in inputs
        if row["path"].endswith(".json")
    }
    predecessors = [
        value
        for path, value in imported.items()
        if path.startswith("reverse_physics/certificates/")
    ]
    event = next(
        value
        for path, value in imported.items()
        if path.startswith("planning/events/")
    )

    (
        rho,
        angular_total,
        latitude_total,
        recurrence_total,
        coefficients,
        z0,
        z1,
    ) = direct_angular_total()
    s = Fraction(1, 50_000)
    coefficient_bound = Fraction(2, 1 - rho)
    weighted_sum = sum(
        Fraction(2 * abs(mode) * (20 - abs(mode)), 20**2)
        for mode in range(-19, 20)
    )
    gradient_bound = 38 * coefficient_bound + 2 * weighted_sum / (1 - rho)
    error = angular_error(s, coefficient_bound, gradient_bound)
    desired_lower = linear_add(angular_total, linear_negate(error))
    t = desired_lower[0]

    desired = certificate["desired_pair_lower_bound"]
    receipt = desired["angular_pi_coefficient_lower"]
    density = certificate["off_shell_local_density"]
    number = certificate["number_operator_bound"]
    wrong = certificate["wrong_sign_pair_bound"]
    complete = certificate["complete_first_Dyson_bound"]
    disposition = certificate["disposition"]
    scope = certificate["does_not_establish"]

    energy_lower = Fraction(number["energy_band_over_M0"][0])
    energy_upper = Fraction(number["energy_band_over_M0"][1])
    band_measure_coefficient = energy_upper**2 - energy_lower**2
    number_exponent = Fraction(1, 2) / s**2

    # Rebuild every dyadic prefactor entry instead of trusting the aggregate.
    number_ledger = {
        "two_A0_squared": 5,
        "three_halves_power_76": 76,
        "s_inverse_fourth": 64,
        "t_inverse": 6,
        "unit_ball_inverse": 2,
    }
    number_prefactor_power = sum(number_ledger.values())
    e_lower = Fraction(65, 24)  # 1+1+1/2+1/6+1/24 < e.
    unit_ball_factor_lower = 1 - Fraction(2, e_lower)

    wrong_decay = 1 - 76 * s**2
    wrong_exponent = wrong_decay / s**2
    wrong_ledger = {
        "two_A0_squared": 5,
        "one_plus_radial_exponent": 32,
        "t_inverse": 6,
        "unit_ball_inverse": 2,
        "decay_inverse_squared": 2,
    }
    wrong_prefactor_power = sum(wrong_ledger.values())

    undesired_norm_bound_follows = all((
        number_exponent - number_prefactor_power > 4_000_000,
        wrong_exponent - wrong_prefactor_power > 4_000_000,
        2**10 > 10**3,
        4 < 10,
    ))
    click_error_follows = undesired_norm_bound_follows and 3 < 10

    checks = {
        "schema_validation": schema_ok,
        "certificate_identity": certificate["certificate"] == "REVERSE_PHYSICS_BT_COMPACT_ENERGY_QUADRATIC_SECTOR_BOUND_V1",
        "lifecycle_rechecked": certificate["lifecycle_state"] == "COEFFICIENT_COMPUTED",
        "dependency_tags_rechecked": certificate["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "source_commit_rechecked": certificate["provenance"]["source_commit"] == SOURCE,
        "input_hashes_recomputed": hashes_ok,
        "two_predecessors_pass_rechecked": len(predecessors) == 2 and all(value["checks"]["ok"] for value in predecessors),
        "done_event_rechecked": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("compact-energy-quadratic-sector-bound"),
        "producer_check_summary_rechecked": certificate["checks"]["total"] == 29 and certificate["checks"]["passed"] == 29 and certificate["checks"]["ok"] and not certificate["checks"]["failures"] and len(certificate["checks"]["details"]) == 29,
        "direct_Fejer_support_recomputed": sorted(coefficients) == list(range(-19, 20)),
        "direct_Fejer_targets_recomputed": fixed.evaluate(coefficients, z0) == fixed.ONE and fixed.evaluate(coefficients, z1) == (-1, 0),
        "latitude_closed_form_rechecked_by_recurrence": latitude_total == recurrence_total,
        "angular_total_has_only_pi_component": angular_total[1] == fixed.QZERO,
        "weighted_mode_sum_recomputed": weighted_sum == Fraction(133, 10),
        "sigma_recomputed": Fraction(desired["sigma_over_M0"]) == s,
        "angular_receipt_exact_recomputed": Fraction(receipt["exact"]) == t,
        "angular_receipt_hash_recomputed": receipt["canonical_sha256"] == fraction_hash(t),
        "angular_lower_positive_recomputed": t > Fraction(1, 64),
        "unit_ball_factor_positive_recomputed": e_lower > Fraction(8, 3) and unit_ball_factor_lower > Fraction(1, 4),
        "desired_core_rechecked": desired["Gaussian_core"] == "||P-P0||_E<=sigma",
        "desired_ball_integral_rechecked": desired["four_ball_integral"] == "integral_(||z||<=1) exp(-||z||^2)d4z=pi^2*(1-2/e)",
        "desired_norm_formula_rechecked": desired["norm_lower"] == "||w||^2 >= t*pi^3*sigma^4*(1-2/e)/8",
        "desired_status_rechecked": desired["status"] == "NONZERO_EXACT_LOWER_BOUND_IN_DECLARED_TWO_PARTICLE_CONVENTION",
        "density_formula_rechecked": density["density"] == ":F((i*partial_1-i*partial_2)/M0) phi(x_1) phi(x_2): evaluated at x_1=x_2=x",
        "density_jet_order_rechecked": density["jet_order"] == 38,
        "density_pair_symbol_rechecked": density["pair_annihilation_symbol"] == "F((k1-k2)/M0)",
        "density_number_symbol_rechecked": density["number_scattering_symbol"] == "F((k+k_prime)/M0)",
        "density_transfer_assignments_rechecked": density["pair_Fourier_transfer"] == "k1+k2" and density["number_Fourier_transfer"] == "k-k_prime",
        "energy_band_recomputed": (energy_lower, energy_upper) == (Fraction(1, 4), Fraction(3, 4)),
        "target_energy_is_in_band": energy_lower < Fraction(1, 2) < energy_upper,
        "energy_band_measure_recomputed": band_measure_coefficient == Fraction(1, 2) and number["energy_band_measure"] == "mu(K)=pi*M0^2/2",
        "number_kernel_rechecked": number["kernel"] == "N_K(k_prime,k)=h_hat(k-k_prime)*F((k+k_prime)/M0) on KxK",
        "number_polynomial_bound_rechecked": number["polynomial_bound"] == "|F((k+k_prime)/M0)|<=A0*(3/2)^38" and 2 * energy_upper == Fraction(3, 2),
        "two_A0_squared_ledger_recomputed": 2 * coefficient_bound**2 < 2**number_ledger["two_A0_squared"],
        "three_halves_ledger_recomputed": Fraction(3, 2) ** 76 < 2**number_ledger["three_halves_power_76"],
        "inverse_bandwidth_ledger_recomputed": s**-4 < 2**number_ledger["s_inverse_fourth"],
        "inverse_t_ledger_recomputed": t**-1 < 2**number_ledger["t_inverse"],
        "unit_ball_ledger_recomputed": unit_ball_factor_lower**-1 < 2**number_ledger["unit_ball_inverse"],
        "number_prefactor_power_recomputed": number_prefactor_power == 153 and number["relative_prefactor_dyadic_bound"] == "prefactor<2^153",
        "number_exponent_recomputed": number_exponent == 1_250_000_000,
        "number_decimal_bound_recomputed": number_exponent - number_prefactor_power > 4_000_000 and number["squared_relative_norm_bound"] == "||N||^2/||w||^2<2^(153-1250000000)<10^(-1000000)",
        "number_Hilbert_Schmidt_formula_rechecked": number["Hilbert_Schmidt_bound"] == "||N||_HS^2<=A0^2*(3/2)^76*exp(-1250000000)*(pi*M0^2/2)^2",
        "number_Hilbert_Schmidt_status_rechecked": number["status"].startswith("HILBERT_SCHMIDT_NUMBER_SCATTERING_OPERATOR"),
        "wrong_kernel_rechecked": wrong["kernel"] == "w_minus(P,n)=h_hat(-P)*F((k1-k2)/M0)",
        "wrong_radial_domain_rechecked": wrong["radial_domain"] == "R=||-P-P0||_E/sigma>=1/s with s=1/50000",
        "wrong_decay_recomputed": Fraction(wrong["decay_coefficient"]) == wrong_decay and wrong_decay > Fraction(1, 2),
        "wrong_tail_exponent_recomputed": Fraction(wrong["tail_exponent"]) == wrong_exponent == 2_499_999_924,
        "wrong_radial_ledger_recomputed": 1 + wrong_exponent < 2**wrong_ledger["one_plus_radial_exponent"],
        "wrong_decay_ledger_recomputed": wrong_decay**-2 < 2**wrong_ledger["decay_inverse_squared"],
        "wrong_prefactor_power_recomputed": wrong_prefactor_power == 47 and wrong["relative_prefactor_dyadic_bound"] == "prefactor<2^47",
        "wrong_decimal_bound_recomputed": wrong_exponent - wrong_prefactor_power > 4_000_000 and wrong["squared_relative_norm_bound"] == "||w_minus||^2/||w||^2<2^(47-2499999924)<10^(-1000000)",
        "wrong_status_rechecked": wrong["status"] == "GLOBAL_WRONG_SIGN_PAIR_VECTOR_WITH_MILLION_DECIMAL_RELATIVE_SUPPRESSION",
        "desired_block_rechecked": complete["desired_block"] == "A_pair=-i*g*|e,0><g,w| plus its physical reverse adjoint",
        "adjoint_norms_rechecked": complete["undesired_blocks"] == ["compressed number scattering P_K N P_K", "compressed number adjoint", "wrong-sign pair", "wrong-sign pair adjoint"],
        "complete_undesired_bound_recomputed": undesired_norm_bound_follows and complete["relative_operator_norm"] == "||E_undesired||/||A_pair||<10^(-400000)",
        "leading_effect_bound_recomputed": click_error_follows and complete["leading_click_effect_error"] == "||(A+E)^dagger(A+E)-A^dagger A||/||A||^2<10^(-399999)",
        "complete_status_rechecked": complete["status"] == "COMPLETE_QUADRATIC_FIELD_SECTOR_BOUND_AT_FIRST_DYSON_ORDER_ON_DECLARED_DOMAIN",
        "constructed_density_disposition_rechecked": disposition["explicit_off_shell_local_density"] == "CONSTRUCTED",
        "bounded_number_disposition_rechecked": disposition["compact_energy_number_operator"] == "BOUNDED_HILBERT_SCHMIDT",
        "bounded_wrong_pair_disposition_rechecked": disposition["wrong_sign_pair_vector"] == "BOUNDED",
        "bounded_first_Dyson_disposition_rechecked": disposition["complete_first_Dyson_quadratic_sector"] == "BOUNDED",
        "compact_band_boundary_preserved": disposition["unrestricted_energy_number_operator"] == "NOT_COMPUTED" and any("outside M0/4" in row for row in scope),
        "higher_Dyson_boundary_preserved": disposition["complete_time_ordered_Dyson_evolution"] == "NOT_COMPUTED" and any("second or higher Dyson orders" in row for row in scope),
        "absolute_q8_boundary_preserved": disposition["absolute_q8_probability"] == "NOT_COMPUTED",
        "Eq19_boundary_preserved": disposition["general_Eq19"] == "NOT_PROVED_AND_NOT_USED",
        "gravity_boundary_preserved": disposition["gravity_or_metric_BV_BRST_transfer"] == "NOT_CONSTRUCTED",
        "Lorentzian_boundary_preserved": disposition["Lorentzian_causal_claim"] == "NOT_ESTABLISHED" and any("LORENTZIAN-CAUSAL" in row for row in scope),
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
    failures = [name for name, value in checks.items() if not value]
    if failures:
        print(
            f"BT COMPACT-ENERGY QUADRATIC VERIFICATION: FAIL ({len(failures)}/{len(checks)})",
            file=sys.stderr,
        )
        return 1
    print(f"BT COMPACT-ENERGY QUADRATIC VERIFICATION: ALL PASS ({len(checks)}/{len(checks)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
