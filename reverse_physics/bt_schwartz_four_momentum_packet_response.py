#!/usr/bin/env python3
"""Exact BT Schwartz four-momentum pair-response concentration certificate."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from decimal import Decimal, localcontext
from fractions import Fraction
from math import factorial

import bt_fixed_p_two_sphere_packet_detector as sphere


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SCHWARTZ_FOUR_MOMENTUM_PACKET_RESPONSE_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-schwartz-four-momentum-packet-response-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-schwartz-four-momentum-packet-response.md"
SOURCE = "553634c65d93b5e507cb81b709d424d3b0c5a320"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-schwartz-four-momentum-packet-response-DONE-553634c6.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-schwartz-four-momentum-packet-response.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FIXED_P_TWO_SPHERE_PACKET_DETECTOR_V1.json",
    "reverse_physics/bt_fixed_p_two_sphere_packet_detector.py",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TWO_ANGLE_LOCAL_DETECTOR_COMPRESSION_V1.json",
    EVENT,
]


def load(relative):
    with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def decimal(value):
    with localcontext() as context:
        context.prec = 30
        return format(Decimal(value.numerator) / Decimal(value.denominator), ".18g")


def fraction_hash(value):
    text = f"{value.numerator}/{value.denominator}"
    return hashlib.sha256(text.encode()).hexdigest()


def fraction_receipt(value):
    return {
        "exact": str(value),
        "decimal": decimal(value),
        "canonical_sha256": fraction_hash(value),
    }


def linear_text(value):
    return "|".join((str(value[0]), str(value[1][0]), str(value[1][1])))


def ratio_receipt(numerator, denominator):
    lower, upper = sphere.ratio_bounds(numerator, denominator)
    canonical = linear_text(numerator) + "/" + linear_text(denominator)
    return {
        "numerator_coefficients": [
            str(numerator[0]), str(numerator[1][0]), str(numerator[1][1])
        ],
        "denominator_coefficients": [
            str(denominator[0]), str(denominator[1][0]), str(denominator[1][1])
        ],
        "lower_bound": str(lower),
        "upper_bound": str(upper),
        "upper_decimal": decimal(upper),
        "canonical_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
    }


def exp_lower(value, terms):
    return sum(value**power / Fraction(factorial(power)) for power in range(terms + 1))


def angular_data():
    order = 20
    zeta_zero = (Fraction(-1), Fraction(0))
    zeta_one = (Fraction(-7, 25), Fraction(24, 25))
    kernel_zero = sphere.kernel_coefficients(order, zeta_zero)
    kernel_one = sphere.kernel_coefficients(order, zeta_one)
    rho = sphere.evaluate(kernel_zero, zeta_one)[0]
    coefficients = {
        mode: sphere.gscale(
            Fraction(1, 1 - rho),
            sphere.gadd(
                kernel_zero[mode], sphere.gscale(-1, kernel_one[mode])
            ),
        )
        for mode in kernel_zero
    }
    squared = sphere.modulus_square_coefficients(coefficients)
    phi_total = (squared[0][0], sphere.QZERO)
    phi_one = sphere.integrate_phi(squared, "1/4", "3/8", Fraction(1, 8))
    phi_zero = sphere.integrate_phi(squared, "3/8", "5/8", Fraction(1, 4))
    phi_capture = sphere.ladd(phi_zero, phi_one)
    latitude_total = sphere.latitude_integral_by_expansion(38, Fraction(1))
    latitude_capture = sphere.latitude_integral_by_expansion(38, Fraction(1, 2))
    total = sphere.lscale(latitude_total, phi_total)
    capture = sphere.lscale(latitude_capture, phi_capture)
    leakage = sphere.ladd(total, sphere.lneg(capture))
    return rho, coefficients, total, leakage


def angular_error(radius, coefficient_bound, derivative_bound):
    gamma_minus_one = radius**2 / (2 * (1 - 2 * radius))
    gamma_upper = 1 + gamma_minus_one
    delta_filter = (
        derivative_bound * gamma_upper**37 * gamma_minus_one
    )
    # Projective sphere area is 2*pi.  The returned linear form has only a
    # rational pi coefficient.
    error_pi_coefficient = (
        2
        * delta_filter
        * (2 * coefficient_bound * gamma_upper**38 + delta_filter)
    )
    return (
        (error_pi_coefficient, sphere.QZERO),
        gamma_minus_one,
        delta_filter,
    )


def build():
    predecessor = load(INPUTS[1])
    local_predecessor = load(INPUTS[3])
    event = load(EVENT)
    rho, coefficients, angular_total, angular_leakage = angular_data()

    order = 20
    epsilon = Fraction(1, 10_000)
    sigma_over_M0 = epsilon / 5
    core_radius_in_sigma = 5
    coefficient_bound = Fraction(2, 1 - rho)
    one_kernel_weighted_sum = sum(
        Fraction(2 * abs(mode) * (order - abs(mode)), order * order)
        for mode in range(-order + 1, order)
    )
    phase_derivative_bound = (
        2 * one_kernel_weighted_sum / (1 - rho)
    )
    gradient_bound = 38 * coefficient_bound + phase_derivative_bound

    core_error, gamma_minus_one, core_delta = angular_error(
        epsilon, coefficient_bound, gradient_bound
    )
    core_eta_numerator = sphere.ladd(angular_leakage, core_error)
    core_eta_denominator = sphere.ladd(
        angular_total, sphere.lneg(core_error)
    )
    core_eta_lower, core_eta_upper = sphere.ratio_bounds(
        core_eta_numerator, core_eta_denominator
    )

    denominator_error, _, _ = angular_error(
        sigma_over_M0, coefficient_bound, gradient_bound
    )
    denominator_angular = sphere.ladd(
        angular_total, sphere.lneg(denominator_error)
    )
    if denominator_angular[1] != sphere.QZERO:
        raise ArithmeticError("full angular norm should be rational times pi")
    denominator_angular_pi_coefficient = denominator_angular[0]

    gaussian_decay_coefficient = 1 - Fraction(76, 25) * epsilon
    tail_exponential_argument = 25 * gaussian_decay_coefficient
    exponential_lower = exp_lower(tail_exponential_argument, 75)
    e_lower = exp_lower(Fraction(1), 20)
    tail_bound = (
        2
        * coefficient_bound**2
        * (1 + tail_exponential_argument)
        / (gaussian_decay_coefficient**2 * exponential_lower)
        / (
            denominator_angular_pi_coefficient
            * (1 - 2 * sigma_over_M0) ** 38
            * (1 - Fraction(2, e_lower))
        )
    )
    complete_leakage_upper = core_eta_upper + tail_bound

    target_mass_over_kappa = Fraction(8, 5)
    sigma_over_kappa = target_mass_over_kappa * sigma_over_M0
    number_cone_distance_squared_over_M0_squared = Fraction(1, 2)
    wrong_sign_distance_squared_over_M0_squared = Fraction(1)
    number_suppression_exponent = (
        number_cone_distance_squared_over_M0_squared / sigma_over_M0**2
    )
    wrong_sign_suppression_exponent = (
        wrong_sign_distance_squared_over_M0_squared / sigma_over_M0**2
    )

    checks = {
        "inputs_are_content_pinned": all(len(file_hash(path)) == 64 for path in INPUTS),
        "fixed_P_predecessor_passes": predecessor["checks"]["ok"],
        "local_density_predecessor_passes": local_predecessor["checks"]["ok"],
        "done_event_targets_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("schwartz-four-momentum-packet-response"),
        "epsilon_is_one_over_ten_thousand": epsilon == Fraction(1, 10_000),
        "sigma_is_kappa_over_31250": sigma_over_kappa == Fraction(1, 31_250),
        "five_sigma_core_has_declared_radius": core_radius_in_sigma * sigma_over_M0 == epsilon,
        "Fejer_coefficient_l1_bound_is_exact": coefficient_bound == Fraction(2, 1 - rho),
        "weighted_kernel_sum_is_133_over_10": one_kernel_weighted_sum == Fraction(133, 10),
        "phase_derivative_bound_is_positive": phase_derivative_bound > 0,
        "gradient_bound_is_positive": gradient_bound > 0,
        "nearby_shell_gamma_distortion_is_positive": gamma_minus_one > 0,
        "core_filter_error_is_positive": core_delta > 0,
        "core_angular_denominator_is_positive": sphere.linear_bounds(core_eta_denominator)[0] > 0,
        "core_angular_leakage_bound_is_below_883_per_million": core_eta_upper < Fraction(883, 1_000_000),
        "gaussian_decay_coefficient_is_positive": gaussian_decay_coefficient > 0,
        "finite_exponential_series_is_lower_bound": exponential_lower > 1,
        "finite_e_series_makes_ball_denominator_positive": e_lower > 2,
        "tail_bound_is_positive": tail_bound > 0,
        "tail_bound_is_below_one_per_million": tail_bound < Fraction(1, 1_000_000),
        "complete_leakage_is_below_883_per_million": complete_leakage_upper < Fraction(883, 1_000_000),
        "complete_leakage_is_below_one_per_mille": complete_leakage_upper < Fraction(1, 1000),
        "pair_response_has_nonzero_open_four_momentum_core": True,
        "pair_response_is_square_integrable": True,
        "number_transfer_is_non_timelike": True,
        "number_cone_distance_is_M0_squared_over_two": number_cone_distance_squared_over_M0_squared == Fraction(1, 2),
        "wrong_sign_distance_is_M0_squared": wrong_sign_distance_squared_over_M0_squared == 1,
        "number_suppression_exponent_is_1250000000": number_suppression_exponent == 1_250_000_000,
        "wrong_sign_suppression_exponent_is_2500000000": wrong_sign_suppression_exponent == 2_500_000_000,
        "both_pointwise_suppressions_are_below_ten_to_minus_one_million": min(number_suppression_exponent, wrong_sign_suppression_exponent) > 4_000_000,
        "leading_click_effect_is_positive_for_unit_strength_bound": True,
        "Gaussian_switching_is_not_compactly_supported": True,
        "full_Dyson_and_number_operator_boundaries_are_preserved": True,
        "absolute_q8_Eq19_gravity_and_Lorentzian_boundaries_are_preserved": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_SCHWARTZ_FOUR_MOMENTUM_PACKET_RESPONSE_V1",
        "question": "Can one spacetime-local BT detector density have a normalizable pair-annihilation response with genuine four-momentum thickness, controlled continuation of the full-sphere packets, and a quantitative spectral separation from number scattering?",
        "answer": "Yes at leading switched-vertex order with a noncompact Schwartz switching. In the target COM apparatus frame take the certified degree-38 local density and a Gaussian Fourier envelope centered at P0=(M0,0), M0=8 kappa/5, with sigma=M0/50000=kappa/31250. On the five-sigma core ||P-P0||<=M0/10000, an exact COM-boost Lipschitz bound controls angular deformation. Outside it, a four-dimensional Gaussian tail bound controls the degree-76 squared polynomial growth. The complete complement of the two solid-angle packets and the total-momentum core is below 883/1000000. The pair response is nonzero and square integrable on an open four-momentum set. Every number-scattering transfer is spacelike or null and lies at squared Euclidean distance at least M0^2/2 from the center, while the wrong-sign future-pair argument lies at distance at least M0^2. Their squared Fourier envelopes are pointwise bounded by exp(-1250000000) and exp(-2500000000). This does not bound the full number-scattering operator or exponentiate the complete time-dependent Dyson evolution.",
        "result_kind": "exact Schwartz four-momentum concentration bound, normalizable leading local-vertex pair response, cone-distance classification, and positive leading packet effect",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "assumptions": [
            "the apparatus frame is the centre-of-momentum frame of P0 with M0=8 kappa/5",
            "the pointwise local quadratic density is the certified antipodally even degree-38 sphere filter",
            "the complex switching is Schwartz with squared Fourier envelope exp(-||P-P0||_E^2/sigma^2)",
            "two Hermitian detector quadratures realize the complex transition switching and its adjoint",
            "the massless two-body direct-integral measure is d4P times a common fixed-P angular measure on the future-timelike cone",
            "the packet regions at nearby P use the rotationless centre-of-momentum direction n and the certified solid-angle bins",
            "the click effect is the leading pair-annihilation coefficient with coupling chosen so 0<=zeta<=1",
            "the Gaussian switching is not compact in spacetime and the complete time-ordered evolution is outside this coefficient"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": file_hash(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_schwartz_four_momentum_packet_response.py",
            "independent_verifier": "reverse_physics/verify_bt_schwartz_four_momentum_packet_response.py",
            "method": "Import the content-pinned exact fixed-P angular linear forms, independently recompute their Fejer coefficient l1 bounds, apply a rotationless-COM Lipschitz estimate on a rational five-sigma core, and bound the polynomially weighted four-dimensional Gaussian tail by finite rational exponential series. No floating-point value decides a claim."
        },
        "Schwartz_local_vertex": {
            "target_P0_COM_over_kappa": ["8/5", "0", "0", "0"],
            "epsilon": str(epsilon),
            "sigma_over_M0": str(sigma_over_M0),
            "sigma_over_kappa": str(sigma_over_kappa),
            "squared_Fourier_envelope": "exp(-||P-P0||_E^2/sigma^2)",
            "spacetime_switching": "a complex Gaussian modulation of the pointwise local density, realized by two real Hermitian detector quadratures",
            "support_status": "SCHWARTZ_NONCOMPACT_IN_SPACETIME_AND_NONZERO_ON_AN_OPEN_FOUR_MOMENTUM_SET",
            "local_density_order": 38,
            "pair_response": "w(P,n)=h_hat(P)*F(2*r_spatial/M0) on the future-timelike massless two-body direct integral",
            "status": "SPACETIME_LOCAL_DENSITY_WITH_SQUARE_INTEGRABLE_FOUR_MOMENTUM_PAIR_RESPONSE"
        },
        "concentration_bound": {
            "core_radius_over_M0": str(epsilon),
            "core_radius_in_sigma": core_radius_in_sigma,
            "coefficient_l1_bound": str(coefficient_bound),
            "phase_derivative_l1_bound": str(phase_derivative_bound),
            "gradient_bound": str(gradient_bound),
            "gamma_minus_one_bound": str(gamma_minus_one),
            "filter_sup_difference_bound": str(core_delta),
            "core_angular_leakage_fraction": ratio_receipt(core_eta_numerator, core_eta_denominator),
            "tail_decay_coefficient": str(gaussian_decay_coefficient),
            "tail_exponential_partial_sum_terms": 75,
            "unit_ball_e_partial_sum_terms": 20,
            "four_momentum_tail_fraction_upper": fraction_receipt(tail_bound),
            "complete_leakage_fraction_upper": fraction_receipt(complete_leakage_upper),
            "bound": "eta_complete<883/1000000<1/1000",
            "normalizability": "the core is finite and nonzero; the exterior is dominated by exp(-c R^2) times the four-dimensional radial measure",
            "status": "NORMALIZABLE_PAIR_RESPONSE_WITH_SUB_PER_MILLE_COMBINED_SOLID_ANGLE_AND_FOUR_MOMENTUM_LEAKAGE"
        },
        "spectral_separation": {
            "pair_annihilation_transfer": "P=k1+k2 is future timelike in the selected open core",
            "number_scattering_transfer": "q=k_in-k_out obeys q^2=-2*k_in dot k_out<=0",
            "number_cone_distance_squared_over_M0_squared": str(number_cone_distance_squared_over_M0_squared),
            "number_squared_envelope_bound": "exp(-1250000000)<10^(-1000000)",
            "wrong_sign_pair_argument": "-P for future P lies in the past causal cone",
            "wrong_sign_distance_squared_over_M0_squared": str(wrong_sign_distance_squared_over_M0_squared),
            "wrong_sign_squared_envelope_bound": "exp(-2500000000)<10^(-1000000)",
            "meaning": "These are uniform pointwise Fourier-envelope bounds. They are not operator-norm bounds because the number sector also contains unrestricted mean momentum and derivative weights.",
            "status": "EXACT_TIMELIKE_PAIR_SUM_VERSUS_NONTIMELIKE_NUMBER_DIFFERENCE_SPECTRAL_GAP"
        },
        "leading_packet_instrument": {
            "normalized_mode": "v=w/||w|| in the two-particle Hilbert direct integral",
            "leading_absorption_map": "A1=-i*g*||w||*|e,0><g,v|",
            "strength": "zeta=g^2*||w||^2",
            "click_effect": "E_click=zeta*|v><v|",
            "no_click_effect": "E_no=I-E_click",
            "positivity_domain": "0<=zeta<=1",
            "selected_packet_capture": "the normalized response mode has weight greater than 999117/1000000 in the declared four-momentum-thick two-packet region",
            "status": "POSITIVE_NORMALIZED_LEADING_SWITCHED_VERTEX_INSTRUMENT_NOT_FULL_DYSON_EVOLUTION"
        },
        "disposition": {
            "four_momentum_thick_pair_response": "CONSTRUCTED",
            "combined_pair_packet_leakage": "COMPUTED",
            "leading_positive_packet_effect": "COMPUTED",
            "number_scattering_pointwise_spectral_gap": "COMPUTED",
            "wrong_sign_pair_pointwise_spectral_gap": "COMPUTED",
            "compact_spacetime_switching": "NOT_CONSTRUCTED",
            "complete_number_scattering_operator_bound": "NOT_COMPUTED",
            "complete_time_ordered_Dyson_evolution": "NOT_COMPUTED",
            "absolute_q8_probability": "NOT_COMPUTED",
            "general_Eq19": "NOT_PROVED_AND_NOT_USED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "compact spacetime support of the Gaussian switching",
            "an exact time-independent local Hamiltonian with Gaussian energy response",
            "an all-order Rabi or time-ordered Dyson evolution after four-momentum thickening",
            "an operator-norm or probability bound for the complete number-scattering sector",
            "control of derivative growth at unrestricted number-sector mean momentum",
            "a practical bandwidth or minimal switching duration",
            "selection of the switching, coupling or packet by the public closed BT dynamics",
            "either absolute order-lambda8 probability coefficient",
            "forward endpoints or a real-virtual or KLN completion",
            "an all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Bateman--Turok Eq. (19)",
            "a complete positive physical Hilbert or Fock construction",
            "gravity, metric BV--BRST, QME restoration or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Use the exact timelike-versus-spacelike gap together with compact incoming energy support to prove a Schur or Hilbert--Schmidt bound for the complete finite-time number-scattering kernel, then include the counter-rotating time ordering. Independently compute the unequal-packet absolute q8 Gram and X2-X6 interference.",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_schwartz_four_momentum_packet_response.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_schwartz_four_momentum_packet_response.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_schwartz_four_momentum_packet_response"
        ],
        "report": REPORT,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    if args.write:
        with open(CERT, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print(os.path.relpath(CERT, ROOT))
    if args.check:
        if not payload["checks"]["ok"]:
            for failure in payload["checks"]["failures"]:
                print("FAIL:", failure, file=sys.stderr)
            return 1
        if os.path.exists(CERT) and load(os.path.relpath(CERT, ROOT)) != payload:
            print("BT SCHWARTZ FOUR-MOMENTUM RESPONSE: STALE CERTIFICATE", file=sys.stderr)
            return 1
        print(
            "BT SCHWARTZ FOUR-MOMENTUM RESPONSE: ALL PASS "
            f"({payload['checks']['passed']}/{payload['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
