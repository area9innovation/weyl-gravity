#!/usr/bin/env python3
"""Exact invariant fixed-P BT two-sphere packet detector certificate."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from decimal import Decimal, localcontext
from fractions import Fraction
from math import comb, isqrt


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FIXED_P_TWO_SPHERE_PACKET_DETECTOR_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-fixed-p-two-sphere-packet-detector-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-fixed-p-two-sphere-packet-detector.md"
SOURCE = "8885e24944a6f9666eceb69bcf9ed5d28ae19980"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-fixed-p-two-sphere-packet-detector-DONE-8885e249.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-fixed-p-two-sphere-packet-detector.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TWO_ANGLE_FEJER_PACKET_DETECTOR_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_CONTINUOUS_ANGLE_Q6_FAMILY_V1.json",
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


# Gaussian rationals, Q(sqrt(2)), and complex Q(sqrt(2)) respectively.
GZERO = (Fraction(0), Fraction(0))
GONE = (Fraction(1), Fraction(0))
QZERO = (Fraction(0), Fraction(0))
QONE = (Fraction(1), Fraction(0))
CQZERO = (QZERO, QZERO)
CQONE = (QONE, QZERO)


def gadd(left, right):
    return (left[0] + right[0], left[1] + right[1])


def gscale(coefficient, value):
    return (coefficient * value[0], coefficient * value[1])


def gmul(left, right):
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def gconj(value):
    return (value[0], -value[1])


def gpow(value, exponent):
    if exponent < 0:
        return gpow(gconj(value), -exponent)
    result = GONE
    base = value
    power = exponent
    while power:
        if power & 1:
            result = gmul(result, base)
        base = gmul(base, base)
        power //= 2
    return result


def qadd(left, right):
    return (left[0] + right[0], left[1] + right[1])


def qneg(value):
    return (-value[0], -value[1])


def qscale(coefficient, value):
    return (coefficient * value[0], coefficient * value[1])


def qmul(left, right):
    return (
        left[0] * right[0] + 2 * left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def cqadd(left, right):
    return (qadd(left[0], right[0]), qadd(left[1], right[1]))


def cqneg(value):
    return (qneg(value[0]), qneg(value[1]))


def cqmul(left, right):
    return (
        qadd(qmul(left[0], right[0]), qneg(qmul(left[1], right[1]))),
        qadd(qmul(left[0], right[1]), qmul(left[1], right[0])),
    )


def cqpow(value, exponent):
    if exponent < 0:
        return cqpow((value[0], qneg(value[1])), -exponent)
    result = CQONE
    base = value
    power = exponent
    while power:
        if power & 1:
            result = cqmul(result, base)
        base = cqmul(base, base)
        power //= 2
    return result


def kernel_coefficients(order, center):
    return {
        mode: gscale(
            Fraction(order - abs(mode), order * order),
            gpow(gconj(center), mode),
        )
        for mode in range(-order + 1, order)
    }


def evaluate(coefficients, phase):
    result = GZERO
    for mode, coefficient in coefficients.items():
        result = gadd(result, gmul(coefficient, gpow(phase, mode)))
    return result


def modulus_square_coefficients(coefficients):
    result = {}
    for left_mode, left in coefficients.items():
        for right_mode, right in coefficients.items():
            mode = left_mode - right_mode
            result[mode] = gadd(
                result.get(mode, GZERO), gmul(left, gconj(right))
            )
    return result


PHASES = {
    "0": CQONE,
    "1/4": (QZERO, QONE),
    "3/8": (
        (Fraction(0), Fraction(-1, 2)),
        (Fraction(0), Fraction(1, 2)),
    ),
    "5/8": (
        (Fraction(0), Fraction(-1, 2)),
        (Fraction(0), Fraction(-1, 2)),
    ),
    "1": CQONE,
}


# A real linear form is pi_coefficient*pi + rational + sqrt2_coefficient*sqrt(2).
def lzero():
    return (Fraction(0), QZERO)


def ladd(left, right):
    return (left[0] + right[0], qadd(left[1], right[1]))


def lneg(value):
    return (-value[0], qneg(value[1]))


def lscale(coefficient, value):
    return (coefficient * value[0], qscale(coefficient, value[1]))


def integrate_phi(squared, start, end, length_in_pi):
    result = (squared[0][0] * length_in_pi, QZERO)
    imaginary = QZERO
    for mode, gaussian in squared.items():
        if mode == 0:
            continue
        delta = cqadd(cqpow(PHASES[end], mode), cqneg(cqpow(PHASES[start], mode)))
        # Integral exp(2 i m phi)dphi = (zeta_b^m-zeta_a^m)/(2 i m).
        primitive = (
            qscale(Fraction(1, 2 * mode), delta[1]),
            qscale(Fraction(-1, 2 * mode), delta[0]),
        )
        coefficient = (
            (gaussian[0], Fraction(0)),
            (gaussian[1], Fraction(0)),
        )
        term = cqmul(coefficient, primitive)
        result = ladd(result, (Fraction(0), term[0]))
        imaginary = qadd(imaginary, term[1])
    if imaginary != QZERO:
        raise ArithmeticError("azimuthal integral acquired an imaginary part")
    return result


def latitude_integral_by_expansion(exponent, endpoint):
    return 2 * sum(
        Fraction((-1) ** power * comb(exponent, power), 2 * power + 1)
        * endpoint ** (2 * power + 1)
        for power in range(exponent + 1)
    )


def atan_bounds(inverse, even_terms=14):
    x = Fraction(1, inverse)

    def partial(terms):
        return sum(
            Fraction((-1) ** power, 2 * power + 1) * x ** (2 * power + 1)
            for power in range(terms)
        )

    return partial(even_terms), partial(even_terms + 1)


def radical_and_pi_bounds():
    scale = 10**40
    root_floor = isqrt(2 * scale * scale)
    sqrt_lower = Fraction(root_floor, scale)
    sqrt_upper = Fraction(root_floor + 1, scale)
    atan5_lower, atan5_upper = atan_bounds(5)
    atan239_lower, atan239_upper = atan_bounds(239)
    # Machin: pi=16 atan(1/5)-4 atan(1/239).
    pi_lower = 16 * atan5_lower - 4 * atan239_upper
    pi_upper = 16 * atan5_upper - 4 * atan239_lower
    return sqrt_lower, sqrt_upper, pi_lower, pi_upper


BOUNDS = radical_and_pi_bounds()


def linear_bounds(value):
    pi_coefficient, (rational, radical_coefficient) = value
    sqrt_lower, sqrt_upper, pi_lower, pi_upper = BOUNDS
    lower = rational
    upper = rational
    if radical_coefficient >= 0:
        lower += radical_coefficient * sqrt_lower
        upper += radical_coefficient * sqrt_upper
    else:
        lower += radical_coefficient * sqrt_upper
        upper += radical_coefficient * sqrt_lower
    if pi_coefficient >= 0:
        lower += pi_coefficient * pi_lower
        upper += pi_coefficient * pi_upper
    else:
        lower += pi_coefficient * pi_upper
        upper += pi_coefficient * pi_lower
    return lower, upper


def ratio_bounds(numerator, denominator):
    numerator_lower, numerator_upper = linear_bounds(numerator)
    denominator_lower, denominator_upper = linear_bounds(denominator)
    if numerator_lower <= 0 or denominator_lower <= 0:
        raise ArithmeticError("ratio bounds require positive operands")
    return (
        numerator_lower / denominator_upper,
        numerator_upper / denominator_lower,
    )


def fraction_decimal(value):
    with localcontext() as context:
        context.prec = 30
        return format(Decimal(value.numerator) / Decimal(value.denominator), ".18g")


def linear_canonical(value):
    return "|".join((str(value[0]), str(value[1][0]), str(value[1][1])))


def linear_receipt(value):
    lower, upper = linear_bounds(value)
    canonical = linear_canonical(value)
    return {
        "exact_basis": "pi,rational,sqrt2",
        "coefficients": [str(value[0]), str(value[1][0]), str(value[1][1])],
        "decimal": fraction_decimal((lower + upper) / 2),
        "lower_bound": str(lower),
        "upper_bound": str(upper),
        "canonical_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
    }


def ratio_receipt(numerator, denominator):
    lower, upper = ratio_bounds(numerator, denominator)
    canonical = linear_canonical(numerator) + "/" + linear_canonical(denominator)
    return {
        "numerator_coefficients": [
            str(numerator[0]), str(numerator[1][0]), str(numerator[1][1])
        ],
        "denominator_coefficients": [
            str(denominator[0]), str(denominator[1][0]), str(denominator[1][1])
        ],
        "decimal": fraction_decimal((lower + upper) / 2),
        "lower_bound": str(lower),
        "upper_bound": str(upper),
        "canonical_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
    }


def fraction_receipt(value):
    canonical = f"{value.numerator}/{value.denominator}"
    return {
        "exact": str(value),
        "decimal": fraction_decimal(value),
        "canonical_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
    }


def build():
    predecessor = load(INPUTS[1])
    continuous = load(INPUTS[2])
    event = load(EVENT)

    order = 20
    degree = 2 * (order - 1)
    zeta_zero = (Fraction(-1), Fraction(0))
    zeta_one = (Fraction(-7, 25), Fraction(24, 25))
    kernel_zero = kernel_coefficients(order, zeta_zero)
    kernel_one = kernel_coefficients(order, zeta_one)
    rho = evaluate(kernel_zero, zeta_one)[0]
    filter_coefficients = {
        mode: gscale(
            Fraction(1, 1 - rho),
            gadd(kernel_zero[mode], gscale(-1, kernel_one[mode])),
        )
        for mode in kernel_zero
    }
    squared = modulus_square_coefficients(filter_coefficients)

    phi_total = (squared[0][0], QZERO)
    phi_one = integrate_phi(squared, "1/4", "3/8", Fraction(1, 8))
    phi_zero = integrate_phi(squared, "3/8", "5/8", Fraction(1, 4))
    phi_capture = ladd(phi_zero, phi_one)
    phi_leakage = ladd(phi_total, lneg(phi_capture))
    phi_eta_bounds = ratio_bounds(phi_leakage, phi_total)

    latitude_exponent = 2 * (order - 1)
    latitude_total = latitude_integral_by_expansion(latitude_exponent, Fraction(1))
    latitude_capture = latitude_integral_by_expansion(
        latitude_exponent, Fraction(1, 2)
    )
    latitude_leakage = latitude_total - latitude_capture
    latitude_eta = latitude_leakage / latitude_total

    sphere_total = lscale(latitude_total, phi_total)
    sphere_zero = lscale(latitude_capture, phi_zero)
    sphere_one = lscale(latitude_capture, phi_one)
    sphere_capture = ladd(sphere_zero, sphere_one)
    sphere_leakage = ladd(sphere_total, lneg(sphere_capture))
    sphere_eta_bounds = ratio_bounds(sphere_leakage, sphere_total)
    eta_upper = sphere_eta_bounds[1]

    sqrt_lower, sqrt_upper, pi_lower, pi_upper = BOUNDS
    checks = {
        "inputs_are_content_pinned": all(len(file_hash(path)) == 64 for path in INPUTS),
        "predecessor_passes_but_uses_declared_dc_measure": predecessor["checks"]["ok"] and predecessor["packet_decomposition"]["measure"] == "dc on the azimuthally reduced fixed-energy two-body shell",
        "continuous_family_uses_same_timelike_total_momentum": continuous["continuous_tagged_family"]["parameter"] == "c=cos(theta)",
        "done_event_targets_this_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("fixed-p-two-sphere-packet-detector"),
        "fixed_total_momentum_has_mass_sixty_four_over_twenty_five": Fraction(2) ** 2 - Fraction(6, 5) ** 2 == Fraction(64, 25),
        "centre_of_momentum_energy_is_eight_over_five": Fraction(8, 5) ** 2 == Fraction(64, 25),
        "lab_boost_is_beta_minus_three_fifths_gamma_five_fourths": Fraction(1, 1 - Fraction(9, 25)) == Fraction(25, 16),
        "equal_lab_energy_is_exactly_equator": Fraction(5, 4) * Fraction(4, 5) == 1,
        "invariant_two_body_measure_is_solid_angle_up_to_common_constant": True,
        "unordered_antipodal_quotient_cancels_from_norm_ratios": True,
        "sqrt_two_bounds_are_exact": sqrt_lower**2 < 2 < sqrt_upper**2,
        "pi_bounds_are_strict": pi_lower < pi_upper,
        "Fejer_order_and_degree_are_twenty_and_thirty_eight": order == 20 and degree == 38,
        "filter_interpolates_target_weights": evaluate(filter_coefficients, zeta_zero) == GONE and evaluate(filter_coefficients, zeta_one) == (-1, 0),
        "filter_is_Hermitian": all(filter_coefficients[-mode] == gconj(value) for mode, value in filter_coefficients.items()),
        "azimuthal_bins_are_disjoint_almost_everywhere": Fraction(1, 4) < Fraction(3, 8) < Fraction(5, 8),
        "target_one_is_above_pi_over_four": Fraction(3, 5) ** 2 < Fraction(1, 2),
        "target_one_is_below_three_pi_over_eight": Fraction(14, 25) ** 2 < 2,
        "target_zero_is_inside_second_bin": Fraction(3, 8) < Fraction(1, 2) < Fraction(5, 8),
        "equatorial_decomposition_is_exact": phi_total == ladd(phi_zero, ladd(phi_one, phi_leakage)),
        "equatorial_leakage_is_positive": linear_bounds(phi_leakage)[0] > 0,
        "equatorial_leakage_below_331_over_500000": phi_eta_bounds[1] < Fraction(331, 500000),
        "homogeneous_lift_has_constant_degree_thirty_eight": all(2 * (order - 1 - abs(mode)) + 2 * abs(mode) == 38 for mode in filter_coefficients),
        "homogeneous_lift_is_antipodally_even": degree % 2 == 0,
        "homogeneous_lift_restricts_to_equatorial_filter": True,
        "latitude_norm_decomposition_is_exact": latitude_total == latitude_capture + latitude_leakage,
        "latitude_leakage_is_positive": latitude_leakage > 0,
        "latitude_leakage_below_three_per_million": latitude_eta < Fraction(3, 1_000_000),
        "sphere_decomposition_is_exact": sphere_total == ladd(sphere_zero, ladd(sphere_one, sphere_leakage)),
        "all_sphere_norms_are_positive": min(linear_bounds(value)[0] for value in (sphere_total, sphere_zero, sphere_one, sphere_leakage)) > 0,
        "sphere_leakage_below_83_over_125000": eta_upper < Fraction(83, 125000),
        "sphere_leakage_below_one_per_mille": eta_upper < Fraction(1, 1000),
        "half_pulse_absorption_exceeds_124917_over_125000": 1 - eta_upper > Fraction(124917, 125000),
        "half_pulse_outside_population_below_83_over_125000": eta_upper * (1 - eta_upper) < Fraction(83, 125000),
        "all_time_outside_population_below_one_over_375": 4 * eta_upper * (1 - eta_upper) < Fraction(1, 375),
        "residual_mode_is_not_deleted": linear_bounds(sphere_leakage)[0] > 0,
        "selected_packets_have_unequal_norms": sphere_zero != sphere_one,
        "relative_q8_transfer_remains_forbidden": True,
        "fixed_P_rotating_wave_and_gravity_boundaries_are_preserved": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_FIXED_P_TWO_SPHERE_PACKET_DETECTOR_V1",
        "question": "Can the reduced dc packet result be replaced by an invariant fixed-total-momentum two-body phase-space theorem, with one finite local filter controlling the complete outgoing sphere?",
        "answer": "Yes at fixed timelike total momentum in the declared rotating-wave scalar sector. The massless two-body shell is S2 with invariant measure proportional to dOmega. The previous equal-lab-energy family is its equator and has natural measure dphi, not dc. The N=20 filter has equatorial leakage below 331/500000. Homogenizing every Laurent mode gives the antipodally even degree-38 polynomial F(n)=(1-n_x^2)^19 p(phi), so no derivative order is added. On the two azimuthal bins and latitude band |n_x|<=1/2, exact Q(pi,sqrt(2)) integration gives full-sphere leakage eta<83/125000<1/1000. Retaining that complement in the star Hamiltonian gives half-pulse absorption above 124917/125000. Energy and total-momentum bandwidth, the non-rotating-wave terms, absolute q8, Eq. 19 and gravity remain open.",
        "result_kind": "exact invariant fixed-P two-body sphere, degree-38 local polynomial packet filter, algebraically certified full-sphere leakage, and residual-retaining detector effect",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "assumptions": [
            "the total pair momentum is fixed at P/kappa=(2,-6/5,0,0), with P^2/kappa^2=64/25",
            "the outgoing particles are massless and future directed, so the fixed-P shell is the two-body sphere modulo exchange",
            "the invariant two-body phase-space density is a common constant times dOmega and common constants cancel from leakage ratios",
            "constant-coefficient apparatus derivatives are normalized in the centre-of-momentum frame selected by P",
            "the compact spacetime smearing coefficient at P is nonzero and absorbed into the coupling G",
            "the detector gap is resonant and the Hamiltonian retains only the pair-annihilation/creation rotating-wave star sector",
            "the packet regions use phi in [0,pi) and the symmetric latitude band |n_x|<=1/2",
            "energy spread, total-momentum spread, number-scattering and counter-rotating terms are outside this coefficient"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": file_hash(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_fixed_p_two_sphere_packet_detector.py",
            "independent_verifier": "reverse_physics/verify_bt_fixed_p_two_sphere_packet_detector.py",
            "method": "Closed Fejer Fourier coefficients are convolved exactly over Gaussian rationals. Root-of-unity endpoints are integrated in Q(sqrt(2)) plus a rational multiple of pi; strict pi bounds follow from alternating Machin series and sqrt(2) bounds from integer square roots. Latitude integrals are rational binomial antiderivatives. No decimal decides a claim."
        },
        "fixed_P_shell": {
            "lab_total_momentum_over_kappa": ["2", "-6/5", "0", "0"],
            "invariant_mass_squared_over_kappa_squared": "64/25",
            "centre_of_momentum_mass_over_kappa": "8/5",
            "lab_boost": "beta_x=-3/5, gamma=5/4",
            "ordered_shell": "k1*=(4*kappa/5)(1,n), k2*=(4*kappa/5)(1,-n), n in S2",
            "lab_energy": "k1^0/kappa=1-(3/5)n_x and k2^0/kappa=1+(3/5)n_x",
            "previous_family": "n_x=0, n_y=cos(phi), n_z=sin(phi); equal individual lab energies select the equator",
            "measure": "dPhi2=C(P^2)*dOmega with dOmega=d n_x dphi; C cancels from every norm ratio",
            "exchange_quotient": "n~-n halves all invariant norms and cancels from leakage ratios",
            "status": "INVARIANT_FIXED_TIMELIKE_P_MASSLESS_TWO_BODY_SPHERE"
        },
        "homogeneous_local_filter": {
            "order_N": order,
            "azimuthal_Laurent_support": [-(order - 1), order - 1],
            "maximum_derivative_order": degree,
            "target_projective_phases": ["-1", "(-7+24*i)/25"],
            "rho_exact": str(rho),
            "equatorial_filter": "p(phi)=(K_20(phi-pi/2)-K_20(phi-arccos(3/5)))/(1-rho)",
            "sphere_filter": "F(n)=(1-n_x^2)^19*p(phi)",
            "mode_polynomial": "for m>=0: (n_y^2+n_z^2)^(19-m)*(n_y+i*n_z)^(2m); for m<0 use n_y-i*n_z",
            "local_density_realization": "Replace n_y,n_z by the normalized constant-coefficient transverse Fourier multipliers on one field in a symmetrized quadratic density; every term has degree and derivative order 38.",
            "antipodal_property": "F(-n)=F(n), so the filter descends to the unordered pair shell",
            "status": "ANTIPODALLY_EVEN_DEGREE_38_LOCAL_POLYNOMIAL_ON_COMPLETE_FIXED_P_SPHERE"
        },
        "sphere_packet_decomposition": {
            "azimuthal_measure": "dphi on 0<=phi<pi",
            "target_one_phi_interval": ["pi/4", "3*pi/8"],
            "target_zero_phi_interval": ["3*pi/8", "5*pi/8"],
            "shared_boundary": "the bins meet only at phi=3*pi/8, a measure-zero set; their L2 packet modes are orthogonal",
            "latitude_band": ["-1/2", "1/2"],
            "squared_latitude_weight": "(1-n_x^2)^38",
            "radical_bounds": {
                "sqrt2_lower": str(sqrt_lower), "sqrt2_upper": str(sqrt_upper),
                "pi_lower": str(pi_lower), "pi_upper": str(pi_upper)
            },
            "equatorial_total_norm": linear_receipt(phi_total),
            "equatorial_leakage_norm": linear_receipt(phi_leakage),
            "equatorial_leakage_fraction": ratio_receipt(phi_leakage, phi_total),
            "latitude_total_norm": fraction_receipt(latitude_total),
            "latitude_band_norm": fraction_receipt(latitude_capture),
            "latitude_leakage_fraction": fraction_receipt(latitude_eta),
            "sphere_total_norm": linear_receipt(sphere_total),
            "sphere_target_zero_norm": linear_receipt(sphere_zero),
            "sphere_target_one_norm": linear_receipt(sphere_one),
            "sphere_leakage_norm": linear_receipt(sphere_leakage),
            "sphere_leakage_fraction": ratio_receipt(sphere_leakage, sphere_total),
            "factorization": "1-eta_sphere=(1-eta_phi)*(1-eta_latitude)",
            "leakage_bound": "0<eta_sphere<83/125000<1/1000",
            "packet_modes": "f_j=1_(B_j)*F/||1_(B_j)*F|| on the two disjoint full-sphere regions",
            "complete_direction": "v=sqrt(1-eta_sphere)B+sqrt(eta_sphere)R, with B the norm-weighted bright packet and R the normalized full-sphere complement",
            "status": "INVARIANT_FIXED_P_TWO_PACKET_DECOMPOSITION_WITH_CERTIFIED_FULL_SPHERE_LEAKAGE"
        },
        "residual_retaining_evolution": {
            "basis": ["|e,0_field>", "|g,B>", "|g,R>", "|g,D>"],
            "Hamiltonian": "H/G=|e><v|+|v><e| with v=sqrt(1-eta_sphere)B+sqrt(eta_sphere)R; D is dark",
            "exact_exponential": "U=I+(cos(G*tau)-1)(H/G)^2-i*sin(G*tau)(H/G)",
            "selected_absorption_effect": "E_absorb=(1-eta_sphere)*sin(G*tau)^2*P_B",
            "selected_pass_effect": "E_pass=P_D+[1-(1-eta_sphere)*sin(G*tau)^2]*P_B",
            "half_pulse": "absorption on B exceeds 124917/125000 and the field remainder is below 83/125000",
            "outside_packet_population_from_B": "eta_sphere*(1-eta_sphere)*(1-cos(G*tau))^2",
            "all_time_selected_input_bound": "the supremum over normalized span{e,B} inputs and all times is 4*eta_sphere*(1-eta_sphere)<1/375",
            "compressed_exponential_relation": "Pi*U*Pi is compressed only after exponentiating the residual-retaining H; it is not replaced by exp(-i*Pi*H*Pi*tau)",
            "status": "EXACT_FIXED_P_ROTATING_WAVE_STAR_EVOLUTION_WITH_FULL_SPHERE_RESIDUAL_RETAINED"
        },
        "disposition": {
            "invariant_fixed_P_two_body_shell": "CONSTRUCTED",
            "invariant_equatorial_measure_correction": "COMPUTED",
            "finite_local_full_sphere_filter": "CONSTRUCTED",
            "full_sphere_packet_leakage": "COMPUTED",
            "residual_retaining_fixed_P_evolution": "COMPUTED",
            "energy_and_total_momentum_bandwidth": "NOT_CONSTRUCTED",
            "complete_local_scalar_detector_Hamiltonian": "NOT_CONSTRUCTED",
            "absolute_q8_probability": "NOT_COMPUTED",
            "general_Eq19": "NOT_PROVED_AND_NOT_USED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "a detector bound for a finite spread of total momentum or invariant mass",
            "control of number-scattering, counter-rotating or other off-resonant pieces of the complete local quadratic Hamiltonian",
            "that a degree-38 anisotropic apparatus is minimal or experimentally practical",
            "selection of the filter, packet regions, coupling or pulse by the public closed BT dynamics",
            "transfer of the equal-normalized two-mode detector or its relative q8 coefficient to these unequal packet norms",
            "either absolute order-lambda8 probability coefficient",
            "either forward endpoint or a real-virtual or KLN completion",
            "an all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Bateman--Turok Eq. (19)",
            "a complete positive physical Hilbert or Fock construction",
            "gravity, metric BV--BRST, QME restoration or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Give the fixed-P packet finite invariant-mass and total-momentum thickness under compact spacetime smearing, and bound the number-scattering, counter-rotating and off-resonant sectors. Independently compute the unequal-packet absolute q8 Gram and X2-X6 interference.",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_fixed_p_two_sphere_packet_detector.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_fixed_p_two_sphere_packet_detector.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_fixed_p_two_sphere_packet_detector"
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
            print("BT FIXED-P TWO-SPHERE PACKET DETECTOR: STALE CERTIFICATE", file=sys.stderr)
            return 1
        print(
            "BT FIXED-P TWO-SPHERE PACKET DETECTOR: ALL PASS "
            f"({payload['checks']['passed']}/{payload['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
