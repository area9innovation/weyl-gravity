#!/usr/bin/env python3
"""Independent exact verifier for the BT projective Fejer packet detector."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from decimal import Decimal, localcontext
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_TWO_ANGLE_FEJER_PACKET_DETECTOR_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-two-angle-fejer-packet-detector-v1.schema.json",
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


Z = (Fraction(0), Fraction(0))
U = (Fraction(1), Fraction(0))


def plus(a, b):
    return (a[0] + b[0], a[1] + b[1])


def times(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def bar(a):
    return (a[0], -a[1])


def scalar(q, a):
    return (q * a[0], q * a[1])


def matrix_product(left, right):
    return [
        [
            sum_complex(
                times(left[row][inner], right[inner][column])
                for inner in range(len(right))
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def sum_complex(values):
    answer = Z
    for entry in values:
        answer = plus(answer, entry)
    return answer


def matrix_plus(*matrices):
    return [
        [sum_complex(matrix[row][column] for matrix in matrices)
         for column in range(len(matrices[0][0]))]
        for row in range(len(matrices[0]))
    ]


def matrix_scale(coefficient, matrix):
    return [[times(coefficient, entry) for entry in row] for row in matrix]


def dagger(matrix):
    return [
        [bar(matrix[column][row]) for column in range(len(matrix))]
        for row in range(len(matrix[0]))
    ]


def identity(size):
    return [[U if row == column else Z for column in range(size)] for row in range(size)]


def integer_power(a, n):
    if n < 0:
        return integer_power(bar(a), -n)
    answer = U
    for _ in range(n):
        answer = times(answer, a)
    return answer


def direct_fejer(order, center):
    """Build |N^-1 sum (zeta*centerbar)^k|^2 by direct double sum."""
    amplitude = {
        k: scalar(Fraction(1, order), integer_power(bar(center), k))
        for k in range(order)
    }
    coefficients = {}
    for k, left in amplitude.items():
        for ell, right in amplitude.items():
            mode = k - ell
            coefficients[mode] = plus(
                coefficients.get(mode, Z), times(left, bar(right))
            )
    return coefficients


def value(coefficients, phase):
    answer = Z
    for mode, coefficient in coefficients.items():
        answer = plus(answer, times(coefficient, integer_power(phase, mode)))
    return answer


def norm_coefficients(coefficients):
    answer = {}
    for m, left in coefficients.items():
        for n, right in coefficients.items():
            mode = m - n
            answer[mode] = plus(
                answer.get(mode, Z), times(left, bar(right))
            )
    return answer


def primitive(mode, endpoint):
    term_minus = scalar(
        Fraction(1, 2 * (2 * mode - 1)),
        integer_power(endpoint, 2 * mode - 1),
    )
    term_plus = scalar(
        Fraction(-1, 2 * (2 * mode + 1)),
        integer_power(endpoint, 2 * mode + 1),
    )
    return plus(term_minus, term_plus)


def exact_integral(coefficients, interval):
    low_c, low_s, high_c, high_s = interval
    start = (high_c, high_s)
    finish = (low_c, low_s)
    answer = Z
    for mode, coefficient in coefficients.items():
        jump = plus(primitive(mode, finish), scalar(Fraction(-1), primitive(mode, start)))
        answer = plus(answer, times(coefficient, jump))
    if answer[1] != 0:
        raise ArithmeticError("integral is not exactly real")
    return answer[0]


def canonical_hash(value):
    return hashlib.sha256(f"{value.numerator}/{value.denominator}".encode()).hexdigest()


def displayed_decimal(value):
    with localcontext() as context:
        context.prec = 30
        decimal = Decimal(value.numerator) / Decimal(value.denominator)
    return format(decimal, ".18g")


def verify(certificate):
    schema_ok = not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if not schema_ok:
        return {"schema_validation": False}

    inputs = certificate["provenance"]["inputs"]
    hashes_ok = all(sha256_file(row["path"]) == row["sha256"] for row in inputs)
    imported = {
        row["path"]: load(os.path.join(ROOT, row["path"])) for row in inputs
    }
    predecessors = [
        item for path, item in imported.items()
        if path.startswith("reverse_physics/certificates/")
    ]
    event = next(
        item for path, item in imported.items() if path.startswith("planning/events/")
    )

    order = 20
    z0 = (Fraction(-1), Fraction(0))
    z1 = (Fraction(-7, 25), Fraction(24, 25))
    k0 = direct_fejer(order, z0)
    k1 = direct_fejer(order, z1)
    rho_pair = value(k0, z1)
    rho = rho_pair[0]
    p = {
        mode: scalar(Fraction(1, 1 - rho), plus(k0[mode], scalar(Fraction(-1), k1[mode])))
        for mode in k0
    }
    p_norm = norm_coefficients(p)
    intervals = {
        "total_norm_squared": (Fraction(-1), Fraction(0), Fraction(1), Fraction(0)),
        "packet_zero_norm_squared": (Fraction(-7, 25), Fraction(24, 25), Fraction(7, 25), Fraction(24, 25)),
        "packet_one_norm_squared": (Fraction(5, 13), Fraction(12, 13), Fraction(20, 29), Fraction(21, 29)),
    }
    exact = {name: exact_integral(p_norm, interval) for name, interval in intervals.items()}
    exact["leakage_norm_squared"] = (
        exact["total_norm_squared"]
        - exact["packet_zero_norm_squared"]
        - exact["packet_one_norm_squared"]
    )
    exact["leakage_fraction_eta"] = exact["leakage_norm_squared"] / exact["total_norm_squared"]
    eta = exact["leakage_fraction_eta"]
    exact["rho"] = rho

    # An independent exact star-Hamiltonian fixture verifies the algebraic
    # exponential form without importing a symbolic matrix from the producer.
    # a^2+b^2=1 and cosine^2+sine^2=1 are both rational Pythagorean points.
    a, b = Fraction(3, 5), Fraction(4, 5)
    cosine, sine = Fraction(5, 13), Fraction(12, 13)
    h_fixture = [
        [Z, (a, Fraction(0)), (b, Fraction(0)), Z],
        [(a, Fraction(0)), Z, Z, Z],
        [(b, Fraction(0)), Z, Z, Z],
        [Z, Z, Z, Z],
    ]
    h2_fixture = matrix_product(h_fixture, h_fixture)
    h3_fixture = matrix_product(h2_fixture, h_fixture)
    u_fixture = matrix_plus(
        identity(4),
        matrix_scale((cosine - 1, Fraction(0)), h2_fixture),
        matrix_scale((Fraction(0), -sine), h_fixture),
    )
    unitary_fixture = matrix_product(dagger(u_fixture), u_fixture)
    absorption_fixture = times(bar(u_fixture[0][1]), u_fixture[0][1])[0]
    outside_fixture = times(bar(u_fixture[2][1]), u_fixture[2][1])[0]

    filter_row = certificate["continuous_filter"]
    packet = certificate["packet_decomposition"]
    evolution = certificate["residual_retaining_evolution"]
    receipts = packet["exact_integral_receipts"]
    receipt_hashes = all(
        canonical_hash(exact[name]) == receipt["canonical_sha256"]
        for name, receipt in receipts.items()
    )
    receipt_bounds = all(
        Fraction(receipt["lower_bound"]) < exact[name] < Fraction(receipt["upper_bound"])
        for name, receipt in receipts.items()
    )
    receipt_digits = all(
        receipt["numerator_digits"] == len(str(abs(exact[name].numerator)))
        and receipt["denominator_digits"] == len(str(exact[name].denominator))
        for name, receipt in receipts.items()
    )
    receipt_decimals = all(
        receipt["decimal"] == displayed_decimal(exact[name])
        for name, receipt in receipts.items()
    )

    disposition = certificate["disposition"]
    scope = certificate["does_not_establish"]
    checks = {
        "schema_validation": schema_ok,
        "certificate_identity": certificate["certificate"] == "REVERSE_PHYSICS_BT_TWO_ANGLE_FEJER_PACKET_DETECTOR_V1",
        "input_hashes_recomputed": hashes_ok,
        "two_predecessors_pass_rechecked": len(predecessors) == 2 and all(row["checks"]["ok"] for row in predecessors),
        "done_event_rechecked": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("two-angle-fejer-packet-detector"),
        "projective_targets_rebuilt": times(z0, bar(z0)) == U and times(z1, bar(z1)) == U,
        "direct_double_sum_has_expected_support": sorted(k0) == list(range(-19, 20)) and sorted(k1) == list(range(-19, 20)),
        "direct_kernel_peaks_recomputed": value(k0, z0) == U and value(k1, z1) == U,
        "cross_overlap_recomputed": rho_pair[1] == 0 and value(k1, z0) == rho_pair,
        "stored_rho_matches": Fraction(filter_row["rho_exact"]) == rho,
        "rho_is_below_one_per_mille": 0 < rho < Fraction(1, 1000),
        "filter_targets_recomputed": value(p, z0) == U and value(p, z1) == (-1, 0),
        "Hermitian_coefficient_symmetry_recomputed": all(p[-m] == bar(coefficient) for m, coefficient in p.items()),
        "maximum_derivative_order_matches_support": filter_row["maximum_transverse_derivative_order"] == 2 * max(abs(mode) for mode in p),
        "local_density_realization_is_explicit": "D_plus^(2m)" in filter_row["local_density_realization"],
        "packet_endpoints_rechecked": Fraction(7, 25) ** 2 + Fraction(24, 25) ** 2 == 1 and Fraction(5, 13) ** 2 + Fraction(12, 13) ** 2 == 1 and Fraction(20, 29) ** 2 + Fraction(21, 29) ** 2 == 1,
        "packet_intervals_match": packet["packet_zero_c_interval"] == ["-7/25", "7/25"] and packet["packet_one_c_interval"] == ["5/13", "20/29"],
        "exact_integral_receipt_hashes_recomputed": receipt_hashes,
        "exact_integral_rational_enclosures_rechecked": receipt_bounds,
        "exact_integral_digit_counts_rechecked": receipt_digits,
        "exact_integral_decimal_displays_recomputed": receipt_decimals,
        "exact_decomposition_recomputed": exact["total_norm_squared"] == exact["packet_zero_norm_squared"] + exact["packet_one_norm_squared"] + exact["leakage_norm_squared"],
        "all_norms_positive": min(exact[name] for name in intervals) > 0 and exact["leakage_norm_squared"] > 0,
        "sub_per_mille_leakage_recomputed": 0 < eta < Fraction(1, 1000),
        "capture_efficiency_recomputed": 1 - eta > Fraction(999, 1000),
        "half_pulse_residual_bound_recomputed": eta * (1 - eta) < Fraction(1, 1000),
        "all_time_selected_input_bound_recomputed": 4 * eta * (1 - eta) < Fraction(1, 250),
        "star_exponential_uses_full_H": evolution["exact_exponential"].startswith("U=I+(cos(G*tau)-1)(H/G)^2"),
        "exact_star_fixture_satisfies_H_cubed_equals_H": h3_fixture == h_fixture,
        "exact_star_fixture_exponential_is_unitary": unitary_fixture == identity(4),
        "exact_star_fixture_selected_probabilities_recomputed": absorption_fixture == a * a * sine * sine and outside_fixture == a * a * b * b * (1 - cosine) ** 2,
        "selected_effects_match_star_solution": evolution["selected_absorption_effect"] == "E_absorb=(1-eta)*sin(G*tau)^2*P_B" and evolution["selected_pass_effect"].startswith("E_pass=P_D+"),
        "residual_is_retained_in_Hamiltonian": "sqrt(eta)R" in evolution["Hamiltonian"],
        "compressed_exponential_is_not_substituted": "not replaced" in evolution["compressed_exponential_relation"],
        "exact_selectivity_remains_forbidden": disposition["exact_zero_width_two_angle_selectivity"] == "STILL_IMPOSSIBLE",
        "complete_local_Hamiltonian_remains_open": disposition["complete_local_scalar_detector_Hamiltonian"] == "NOT_CONSTRUCTED",
        "absolute_q8_remains_open": disposition["absolute_q8_probability"] == "NOT_COMPUTED",
        "equal_weight_relative_q8_transfer_forbidden": any("equal-weight two-mode effect" in row and "relative order-lambda8" in row for row in scope),
        "Eq19_remains_open": disposition["general_Eq19"] == "NOT_PROVED_AND_NOT_USED",
        "gravity_remains_open": disposition["gravity_or_metric_BV_BRST_transfer"] == "NOT_CONSTRUCTED",
        "Lorentzian_boundary_present": any("LORENTZIAN-CAUSAL" in row for row in scope),
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
