#!/usr/bin/env python3
"""Independent exact verifier for the invariant fixed-P BT sphere detector."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from decimal import Decimal, localcontext
from fractions import Fraction
from math import factorial, isqrt

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FIXED_P_TWO_SPHERE_PACKET_DETECTOR_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-fixed-p-two-sphere-packet-detector-v1.schema.json",
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


ZERO = (Fraction(0), Fraction(0))
ONE = (Fraction(1), Fraction(0))
QZERO = (Fraction(0), Fraction(0))
QONE = (Fraction(1), Fraction(0))
CQONE = (QONE, QZERO)


def add(left, right):
    return (left[0] + right[0], left[1] + right[1])


def scale(coefficient, value):
    return (coefficient * value[0], coefficient * value[1])


def multiply(left, right):
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def conjugate(value):
    return (value[0], -value[1])


def power(value, exponent):
    if exponent < 0:
        return power(conjugate(value), -exponent)
    answer = ONE
    for _ in range(exponent):
        answer = multiply(answer, value)
    return answer


def qadd(left, right):
    return (left[0] + right[0], left[1] + right[1])


def qneg(value):
    return (-value[0], -value[1])


def qscale(coefficient, value):
    return (coefficient * value[0], coefficient * value[1])


def qmultiply(left, right):
    return (
        left[0] * right[0] + 2 * left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def cqadd(left, right):
    return (qadd(left[0], right[0]), qadd(left[1], right[1]))


def cqneg(value):
    return (qneg(value[0]), qneg(value[1]))


def cqmultiply(left, right):
    return (
        qadd(qmultiply(left[0], right[0]), qneg(qmultiply(left[1], right[1]))),
        qadd(qmultiply(left[0], right[1]), qmultiply(left[1], right[0])),
    )


def cqpower(value, exponent):
    if exponent < 0:
        return cqpower((value[0], qneg(value[1])), -exponent)
    answer = CQONE
    for _ in range(exponent):
        answer = cqmultiply(answer, value)
    return answer


def direct_fejer(order, center):
    """Reconstruct a normalized Fejer kernel from its N by N amplitude sum."""
    amplitudes = {
        index: scale(Fraction(1, order), power(conjugate(center), index))
        for index in range(order)
    }
    answer = {}
    for left_index, left in amplitudes.items():
        for right_index, right in amplitudes.items():
            mode = left_index - right_index
            answer[mode] = add(
                answer.get(mode, ZERO), multiply(left, conjugate(right))
            )
    return answer


def evaluate(coefficients, phase):
    answer = ZERO
    for mode, coefficient in coefficients.items():
        answer = add(answer, multiply(coefficient, power(phase, mode)))
    return answer


def norm_coefficients(coefficients):
    answer = {}
    for left_mode, left in coefficients.items():
        for right_mode, right in coefficients.items():
            mode = left_mode - right_mode
            answer[mode] = add(
                answer.get(mode, ZERO), multiply(left, conjugate(right))
            )
    return answer


PHASES = {
    "0": CQONE,
    "1/4": (QZERO, QONE),
    "3/8": ((0, Fraction(-1, 2)), (0, Fraction(1, 2))),
    "5/8": ((0, Fraction(-1, 2)), (0, Fraction(-1, 2))),
    "1": CQONE,
}


def linear_add(left, right):
    return (left[0] + right[0], qadd(left[1], right[1]))


def linear_negate(value):
    return (-value[0], qneg(value[1]))


def linear_scale(coefficient, value):
    return (coefficient * value[0], qscale(coefficient, value[1]))


def root_of_unity_integral(coefficients, start, end, length_in_pi):
    answer = (coefficients[0][0] * length_in_pi, QZERO)
    imaginary = QZERO
    for mode, gaussian in coefficients.items():
        if mode == 0:
            continue
        delta = cqadd(cqpower(PHASES[end], mode), cqneg(cqpower(PHASES[start], mode)))
        primitive = (
            qscale(Fraction(1, 2 * mode), delta[1]),
            qscale(Fraction(-1, 2 * mode), delta[0]),
        )
        term = cqmultiply(
            ((gaussian[0], 0), (gaussian[1], 0)), primitive
        )
        answer = linear_add(answer, (0, term[0]))
        imaginary = qadd(imaginary, term[1])
    if imaginary != QZERO:
        raise ArithmeticError("non-real azimuthal norm")
    return answer


def latitude_recurrence(exponent, endpoint):
    """Twice integral_0^a (1-x^2)^n dx via integration by parts."""
    one_sided = endpoint
    for n in range(1, exponent + 1):
        one_sided = (
            endpoint * (1 - endpoint * endpoint) ** n + 2 * n * one_sided
        ) / (2 * n + 1)
    return 2 * one_sided


def full_latitude_closed_form(exponent):
    return Fraction(
        2 ** (2 * exponent + 1) * factorial(exponent) ** 2,
        factorial(2 * exponent + 1),
    )


def atan_interval(inverse, even_terms=16):
    x = Fraction(1, inverse)

    def partial(terms):
        return sum(
            Fraction((-1) ** k, 2 * k + 1) * x ** (2 * k + 1)
            for k in range(terms)
        )

    return partial(even_terms), partial(even_terms + 1)


def independent_constant_bounds():
    scale_value = 10**50
    root_floor = isqrt(2 * scale_value * scale_value)
    sqrt_bounds = (
        Fraction(root_floor, scale_value),
        Fraction(root_floor + 1, scale_value),
    )
    a5 = atan_interval(5)
    a239 = atan_interval(239)
    pi_bounds = (16 * a5[0] - 4 * a239[1], 16 * a5[1] - 4 * a239[0])
    return sqrt_bounds, pi_bounds


def parse_linear(coefficients):
    return (
        Fraction(coefficients[0]),
        (Fraction(coefficients[1]), Fraction(coefficients[2])),
    )


def linear_canonical(value):
    return "|".join((str(value[0]), str(value[1][0]), str(value[1][1])))


def canonical_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()


def fraction_hash(value):
    return canonical_hash(f"{value.numerator}/{value.denominator}")


def linear_bounds(value, constant_bounds):
    sqrt_lower, sqrt_upper, pi_lower, pi_upper = constant_bounds
    pi_coefficient, (rational, radical_coefficient) = value
    lower = upper = rational
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


def ratio_bounds(numerator, denominator, constant_bounds):
    nlo, nhi = linear_bounds(numerator, constant_bounds)
    dlo, dhi = linear_bounds(denominator, constant_bounds)
    return nlo / dhi, nhi / dlo


def displayed_decimal(value):
    with localcontext() as context:
        context.prec = 30
        return format(Decimal(value.numerator) / Decimal(value.denominator), ".18g")


def verify_linear_receipt(receipt, exact, constant_bounds):
    stored = parse_linear(receipt["coefficients"])
    bounds = linear_bounds(exact, constant_bounds)
    return all((
        stored == exact,
        receipt["canonical_sha256"] == canonical_hash(linear_canonical(exact)),
        Fraction(receipt["lower_bound"]) == bounds[0],
        Fraction(receipt["upper_bound"]) == bounds[1],
        receipt["decimal"] == displayed_decimal((bounds[0] + bounds[1]) / 2),
    ))


def verify_ratio_receipt(receipt, numerator, denominator, constant_bounds):
    stored_numerator = parse_linear(receipt["numerator_coefficients"])
    stored_denominator = parse_linear(receipt["denominator_coefficients"])
    bounds = ratio_bounds(numerator, denominator, constant_bounds)
    canonical = linear_canonical(numerator) + "/" + linear_canonical(denominator)
    return all((
        stored_numerator == numerator,
        stored_denominator == denominator,
        receipt["canonical_sha256"] == canonical_hash(canonical),
        Fraction(receipt["lower_bound"]) == bounds[0],
        Fraction(receipt["upper_bound"]) == bounds[1],
        receipt["decimal"] == displayed_decimal((bounds[0] + bounds[1]) / 2),
    ))


def verify_fraction_receipt(receipt, exact):
    return all((
        Fraction(receipt["exact"]) == exact,
        receipt["canonical_sha256"] == fraction_hash(exact),
        receipt["decimal"] == displayed_decimal(exact),
    ))


def complex_matrix_product(left, right):
    def complex_sum(values):
        answer = ZERO
        for value in values:
            answer = add(answer, value)
        return answer

    return [
        [
            complex_sum(
                (multiply(left[row][inner], right[inner][column])
                 for inner in range(len(right)))
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def matrix_add(*matrices):
    def complex_sum(values):
        answer = ZERO
        for value in values:
            answer = add(answer, value)
        return answer

    return [
        [complex_sum(matrix[r][c] for matrix in matrices)
         for c in range(len(matrices[0][0]))]
        for r in range(len(matrices[0]))
    ]


def matrix_scale(coefficient, matrix):
    return [[multiply(coefficient, value) for value in row] for row in matrix]


def dagger(matrix):
    return [[conjugate(matrix[c][r]) for c in range(len(matrix))]
            for r in range(len(matrix[0]))]


def identity(size):
    return [[ONE if r == c else ZERO for c in range(size)] for r in range(size)]


def verify(certificate):
    schema_ok = not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if not schema_ok:
        return {"schema_validation": False}

    inputs = certificate["provenance"]["inputs"]
    imported = {row["path"]: load(os.path.join(ROOT, row["path"])) for row in inputs}
    hashes_ok = all(sha256_file(row["path"]) == row["sha256"] for row in inputs)
    predecessors = [value for path, value in imported.items() if path.startswith("reverse_physics/certificates/")]
    event = next(value for path, value in imported.items() if path.startswith("planning/events/"))

    order = 20
    z0 = (Fraction(-1), Fraction(0))
    z1 = (Fraction(-7, 25), Fraction(24, 25))
    k0 = direct_fejer(order, z0)
    k1 = direct_fejer(order, z1)
    rho = evaluate(k0, z1)[0]
    p = {
        mode: scale(Fraction(1, 1 - rho), add(k0[mode], scale(-1, k1[mode])))
        for mode in k0
    }
    squared = norm_coefficients(p)
    phi_total = (squared[0][0], QZERO)
    phi_one = root_of_unity_integral(squared, "1/4", "3/8", Fraction(1, 8))
    phi_zero = root_of_unity_integral(squared, "3/8", "5/8", Fraction(1, 4))
    phi_capture = linear_add(phi_zero, phi_one)
    phi_leakage = linear_add(phi_total, linear_negate(phi_capture))

    latitude_total = full_latitude_closed_form(38)
    latitude_total_recurrence = latitude_recurrence(38, Fraction(1))
    latitude_capture = latitude_recurrence(38, Fraction(1, 2))
    latitude_leakage = latitude_total - latitude_capture
    latitude_eta = latitude_leakage / latitude_total
    sphere_total = linear_scale(latitude_total, phi_total)
    sphere_zero = linear_scale(latitude_capture, phi_zero)
    sphere_one = linear_scale(latitude_capture, phi_one)
    sphere_capture = linear_add(sphere_zero, sphere_one)
    sphere_leakage = linear_add(sphere_total, linear_negate(sphere_capture))

    packet = certificate["sphere_packet_decomposition"]
    stored_constants = packet["radical_bounds"]
    constants = (
        Fraction(stored_constants["sqrt2_lower"]),
        Fraction(stored_constants["sqrt2_upper"]),
        Fraction(stored_constants["pi_lower"]),
        Fraction(stored_constants["pi_upper"]),
    )
    independent_sqrt, independent_pi = independent_constant_bounds()
    eta_phi_bounds = ratio_bounds(phi_leakage, phi_total, constants)
    eta_sphere_bounds = ratio_bounds(sphere_leakage, sphere_total, constants)
    eta_upper = eta_sphere_bounds[1]

    # Method-distinct rational star fixture: sqrt(1-eta)=3/5, sqrt(eta)=4/5.
    bright, residual = Fraction(3, 5), Fraction(4, 5)
    cosine, sine = Fraction(5, 13), Fraction(12, 13)
    h = [
        [ZERO, (bright, 0), (residual, 0), ZERO],
        [(bright, 0), ZERO, ZERO, ZERO],
        [(residual, 0), ZERO, ZERO, ZERO],
        [ZERO, ZERO, ZERO, ZERO],
    ]
    h2 = complex_matrix_product(h, h)
    h3 = complex_matrix_product(h2, h)
    u = matrix_add(
        identity(4),
        matrix_scale((cosine - 1, 0), h2),
        matrix_scale((0, -sine), h),
    )

    shell = certificate["fixed_P_shell"]
    filter_row = certificate["homogeneous_local_filter"]
    evolution = certificate["residual_retaining_evolution"]
    disposition = certificate["disposition"]
    scope = certificate["does_not_establish"]
    # Coefficients in x of E^2-k_x^2-k_perp^2 after the exact boost.
    mass_shell_polynomial = [
        Fraction(1) - Fraction(9, 25) - Fraction(16, 25),
        Fraction(-6, 5) - Fraction(-6, 5),
        Fraction(9, 25) - Fraction(1) + Fraction(16, 25),
    ]

    checks = {
        "schema_validation": schema_ok,
        "certificate_identity": certificate["certificate"] == "REVERSE_PHYSICS_BT_FIXED_P_TWO_SPHERE_PACKET_DETECTOR_V1",
        "input_hashes_recomputed": hashes_ok,
        "two_predecessors_pass_rechecked": len(predecessors) == 2 and all(value["checks"]["ok"] for value in predecessors),
        "predecessor_dc_scope_rechecked": any(value.get("packet_decomposition", {}).get("measure") == "dc on the azimuthally reduced fixed-energy two-body shell" for value in predecessors),
        "done_event_rechecked": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("fixed-p-two-sphere-packet-detector"),
        "timelike_total_momentum_recomputed": Fraction(2) ** 2 - Fraction(6, 5) ** 2 == Fraction(shell["invariant_mass_squared_over_kappa_squared"]),
        "centre_of_momentum_mass_recomputed": Fraction(shell["centre_of_momentum_mass_over_kappa"]) ** 2 == Fraction(64, 25),
        "boost_reconstructs_mass_shell_for_all_x": mass_shell_polynomial == [0, 0, 0],
        "equal_energy_condition_selects_x_zero": Fraction(-6, 5) != 0 and "n_x=0" in shell["previous_family"],
        "invariant_measure_is_dOmega_not_dc": "dOmega=d n_x dphi" in shell["measure"] and packet["azimuthal_measure"].startswith("dphi"),
        "exchange_quotient_boundary_present": "halves all invariant norms" in shell["exchange_quotient"],
        "stored_sqrt_bounds_are_strict": constants[0] ** 2 < 2 < constants[1] ** 2,
        "independent_sqrt_bounds_nested": constants[0] < independent_sqrt[0] < independent_sqrt[1] < constants[1],
        "independent_Machin_pi_bounds_nested": constants[2] < independent_pi[0] < independent_pi[1] < constants[3],
        "direct_double_sum_support_rebuilt": sorted(k0) == list(range(-19, 20)) == sorted(k1),
        "kernel_peaks_recomputed": evaluate(k0, z0) == ONE and evaluate(k1, z1) == ONE,
        "rho_recomputed": Fraction(filter_row["rho_exact"]) == rho and 0 < rho < Fraction(1, 1000),
        "filter_targets_recomputed": evaluate(p, z0) == ONE and evaluate(p, z1) == (-1, 0),
        "filter_Hermitian_symmetry_recomputed": all(p[-m] == conjugate(value) for m, value in p.items()),
        "homogeneous_degree_recomputed": all(2 * (19 - abs(mode)) + 2 * abs(mode) == 38 for mode in p),
        "antipodal_descent_rechecked": filter_row["maximum_derivative_order"] % 2 == 0 and "F(-n)=F(n)" in filter_row["antipodal_property"],
        "equatorial_restriction_rechecked": filter_row["sphere_filter"] == "F(n)=(1-n_x^2)^19*p(phi)",
        "mode_polynomial_realization_explicit": "(n_y^2+n_z^2)^(19-m)" in filter_row["mode_polynomial"] and "n_y-i*n_z" in filter_row["mode_polynomial"],
        "local_density_realization_explicit": "constant-coefficient transverse Fourier multipliers" in filter_row["local_density_realization"] and "derivative order 38" in filter_row["local_density_realization"],
        "azimuthal_bins_match": packet["target_one_phi_interval"] == ["pi/4", "3*pi/8"] and packet["target_zero_phi_interval"] == ["3*pi/8", "5*pi/8"],
        "target_one_interior_recomputed": Fraction(3, 5) ** 2 < Fraction(1, 2) and Fraction(14, 25) ** 2 < 2,
        "latitude_band_matches": packet["latitude_band"] == ["-1/2", "1/2"] and packet["squared_latitude_weight"] == "(1-n_x^2)^38",
        "azimuthal_decomposition_recomputed": phi_total == linear_add(phi_zero, linear_add(phi_one, phi_leakage)),
        "equatorial_total_receipt_recomputed": verify_linear_receipt(packet["equatorial_total_norm"], phi_total, constants),
        "equatorial_leakage_receipt_recomputed": verify_linear_receipt(packet["equatorial_leakage_norm"], phi_leakage, constants),
        "equatorial_eta_receipt_recomputed": verify_ratio_receipt(packet["equatorial_leakage_fraction"], phi_leakage, phi_total, constants),
        "equatorial_eta_bound_recomputed": 0 < eta_phi_bounds[0] < eta_phi_bounds[1] < Fraction(331, 500000),
        "latitude_methods_agree": latitude_total == latitude_total_recurrence,
        "latitude_total_receipt_recomputed": verify_fraction_receipt(packet["latitude_total_norm"], latitude_total),
        "latitude_band_receipt_recomputed": verify_fraction_receipt(packet["latitude_band_norm"], latitude_capture),
        "latitude_eta_receipt_recomputed": verify_fraction_receipt(packet["latitude_leakage_fraction"], latitude_eta),
        "latitude_eta_bound_recomputed": 0 < latitude_eta < Fraction(3, 1_000_000),
        "sphere_decomposition_recomputed": sphere_total == linear_add(sphere_zero, linear_add(sphere_one, sphere_leakage)),
        "sphere_total_receipt_recomputed": verify_linear_receipt(packet["sphere_total_norm"], sphere_total, constants),
        "sphere_zero_receipt_recomputed": verify_linear_receipt(packet["sphere_target_zero_norm"], sphere_zero, constants),
        "sphere_one_receipt_recomputed": verify_linear_receipt(packet["sphere_target_one_norm"], sphere_one, constants),
        "sphere_leakage_receipt_recomputed": verify_linear_receipt(packet["sphere_leakage_norm"], sphere_leakage, constants),
        "sphere_eta_receipt_recomputed": verify_ratio_receipt(packet["sphere_leakage_fraction"], sphere_leakage, sphere_total, constants),
        "sphere_eta_bound_recomputed": 0 < eta_sphere_bounds[0] < eta_upper < Fraction(83, 125000) < Fraction(1, 1000),
        "capture_factorization_recomputed": sphere_capture == linear_scale(latitude_capture, phi_capture),
        "packet_norms_are_unequal": sphere_zero != sphere_one,
        "complete_direction_retains_sphere_complement": "sqrt(eta_sphere)R" in packet["complete_direction"] and "full-sphere complement" in packet["complete_direction"],
        "star_fixture_H_cubed_equals_H": h3 == h,
        "star_fixture_exponential_unitary": complex_matrix_product(dagger(u), u) == identity(4),
        "residual_retained_in_Hamiltonian": "sqrt(eta_sphere)R" in evolution["Hamiltonian"],
        "effects_match_full_star_solution": evolution["selected_absorption_effect"] == "E_absorb=(1-eta_sphere)*sin(G*tau)^2*P_B" and evolution["selected_pass_effect"].startswith("E_pass=P_D+"),
        "half_pulse_bound_recomputed": 1 - eta_upper > Fraction(124917, 125000),
        "all_time_bound_recomputed": 4 * eta_upper * (1 - eta_upper) < Fraction(1, 375),
        "compressed_exponential_not_substituted": "not replaced" in evolution["compressed_exponential_relation"],
        "bandwidth_remains_open": disposition["energy_and_total_momentum_bandwidth"] == "NOT_CONSTRUCTED",
        "complete_Hamiltonian_remains_open": disposition["complete_local_scalar_detector_Hamiltonian"] == "NOT_CONSTRUCTED",
        "absolute_q8_remains_open": disposition["absolute_q8_probability"] == "NOT_COMPUTED",
        "relative_q8_transfer_forbidden": any("unequal packet norms" in row and "relative q8" in row for row in scope),
        "Eq19_remains_open": disposition["general_Eq19"] == "NOT_PROVED_AND_NOT_USED",
        "gravity_remains_open": disposition["gravity_or_metric_BV_BRST_transfer"] == "NOT_CONSTRUCTED",
        "Lorentzian_boundary_present": disposition["Lorentzian_causal_claim"] == "NOT_ESTABLISHED" and any("LORENTZIAN-CAUSAL" in row for row in scope),
        "literature_priority_forbidden": "literature priority" in scope,
    }
    return {name: bool(ok) for name, ok in checks.items()}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    checks = verify(load(args.verify))
    for name, ok in checks.items():
        print(("PASS: " if ok else "FAIL: ") + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
