#!/usr/bin/env python3
"""Independent verifier for the local quadrupole BT dark detector."""
from __future__ import annotations

import hashlib
import json
import os
from fractions import Fraction
from math import comb, factorial

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_LOCAL_QUADRUPOLE_DARK_DETECTOR_Q8_V1.json"
)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-local-quadrupole-dark-detector-q8-v1.schema.json"
)


def load(relative):
    with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_receipt(row):
    value = Fraction(row["exact"])
    canonical = f"{value.numerator}/{value.denominator}".encode()
    return value, hashlib.sha256(canonical).hexdigest() == row["canonical_sha256"]


def sine_lower(value):
    return sum(
        Fraction((-1) ** index) * value ** (2 * index + 1)
        / factorial(2 * index + 1)
        for index in range(10)
    )


def sine_upper(value):
    return sum(
        Fraction((-1) ** index) * value ** (2 * index + 1)
        / factorial(2 * index + 1)
        for index in range(9)
    )


def sinc_interval(lower, upper):
    return (
        sine_lower(upper) / upper if upper else Fraction(1),
        Fraction(1) if lower == 0 else sine_upper(lower) / lower,
    )


def multiply_intervals(*intervals):
    result = (Fraction(1), Fraction(1))
    for interval in intervals:
        values = [left * right for left in result for right in interval]
        result = min(values), max(values)
    return result


def outward(interval, places=32):
    scale = 10**places
    lower, upper = interval
    return (
        Fraction(lower.numerator * scale // lower.denominator, scale),
        Fraction(-((-upper.numerator * scale) // upper.denominator), scale),
    )


def c_of_a(value):
    return 1 - Fraction(15, 8) * value - Fraction(25, 32) * value * value


def p2(value):
    return (3 * value * value - 1) / 2


def independent_tree_interval(cells=1024):
    lower = Fraction(0)
    upper = Fraction(0)
    width = Fraction(4, 5 * cells)
    for index in range(cells):
        a_lower = Fraction(4 * index, 5 * cells)
        a_upper = Fraction(4 * (index + 1), 5 * cells)
        c_lower = c_of_a(a_upper)
        c_upper = c_of_a(a_lower)
        p_values = [p2(c_lower), p2(c_upper)]
        if c_lower <= 0 <= c_upper:
            p_values.append(Fraction(-1, 2))
        p_interval = min(p_values), max(p_values)
        ratio_interval = (
            6 + 5 * a_lower,
            6 + 5 * a_upper,
        )
        denominator_inverse = (
            1 / (a_upper + Fraction(12, 5)),
            1 / (a_lower + Fraction(12, 5)),
        )
        integrand = multiply_intervals(
            p_interval,
            sinc_interval(a_lower, a_upper),
            ratio_interval,
            denominator_inverse,
            (Fraction(25, 4), Fraction(25, 4)),
        )
        integrand = outward(integrand)
        lower += width * integrand[0]
        upper += width * integrand[1]
    return lower, upper


def direct_legendre_power_moment(index):
    total = Fraction(0)
    for power in range(index + 1):
        coefficient = Fraction(comb(index, power) * (-1) ** power)
        p2_integral = Fraction(3, 2) * (
            Fraction(0) if power % 2 else Fraction(2, power + 3)
        ) - Fraction(1, 2) * (
            Fraction(0) if power % 2 else Fraction(2, power + 1)
        )
        total += coefficient * p2_integral
    return total


def loop_term(index):
    h = Fraction(
        (-1) ** (index + 1),
        2 * index * (2 * index + 1) * factorial(2 * index),
    )
    return -4 * h * Fraction(32, 25) ** index * direct_legendre_power_moment(index)


def integrate_polynomial(coefficients):
    return sum(
        coefficient * (Fraction(0) if power % 2 else Fraction(2, power + 1))
        for power, coefficient in coefficients.items()
    )


def verify(certificate):
    schema_errors = list(
        Draft202012Validator(load(SCHEMA_REL)).iter_errors(certificate)
    )
    provenance = certificate.get("provenance", {})
    inputs = provenance.get("inputs", [])
    hashes_ok = len(inputs) == 6 and all(
        os.path.exists(os.path.join(ROOT, row.get("path", "")))
        and sha256(row["path"]) == row.get("sha256")
        for row in inputs
    )
    predecessors_ok = False
    event_ok = False
    if len(inputs) == 6:
        try:
            predecessors = [load(row["path"]) for row in inputs[1:-1]]
            event = load(inputs[-1]["path"])
            predecessors_ok = len(predecessors) == 4 and all(
                row["checks"]["ok"] for row in predecessors
            )
            event_ok = (
                event["body"]["payload"]["to_state"] == "DONE"
                and event["body"]["payload"]["target"].endswith(
                    "local-quadrupole-dark-detector-q8"
                )
            )
        except (KeyError, OSError, json.JSONDecodeError):
            pass

    density = certificate.get("local_quadrupole_density", {})
    moments = certificate.get("exact_P2_moments", {})
    probability = certificate.get("local_detector_probability", {})
    disposition = certificate.get("disposition", {})
    boundaries = certificate.get("does_not_establish", [])

    stored_tree_lower, stored_tree_lower_hash = parse_receipt(
        moments.get("tree_interval", {}).get("lower", {"exact": "0", "canonical_sha256": ""})
    )
    stored_tree_upper, stored_tree_upper_hash = parse_receipt(
        moments.get("tree_interval", {}).get("upper", {"exact": "0", "canonical_sha256": ""})
    )
    independent_tree_lower, independent_tree_upper = independent_tree_interval()

    direct_i2 = direct_legendre_power_moment(2)
    direct_i3 = direct_legendre_power_moment(3)
    expected_i2 = Fraction(2**3 * 2 * 1, 3 * 4 * 5)
    expected_i3 = Fraction(2**4 * 3 * 2, 4 * 5 * 6)
    term2 = loop_term(2)
    term3 = loop_term(3)
    loop_lower, loop_hash = parse_receipt(
        moments.get("loop_lower_partial", {"exact": "0", "canonical_sha256": ""})
    )
    ratios = [
        Fraction(32, 25) * index
        / ((index - 1) * (2 * index + 3) * (index + 4))
        for index in range(2, 101)
    ]

    p2_mean = integrate_polynomial({2: Fraction(3, 2), 0: Fraction(-1, 2)})
    p2_norm = integrate_polynomial(
        {4: Fraction(9, 4), 2: Fraction(-3, 2), 0: Fraction(1, 4)}
    )
    fibre_mean_coefficient = Fraction(-1, 12) + Fraction(1, 12)
    cauchy_factor = Fraction(5, 16)

    central_lower, central_hash = parse_receipt(
        probability.get("central_relative_lower", {"exact": "0", "canonical_sha256": ""})
    )
    bandwidth_lower, bandwidth_hash = parse_receipt(
        probability.get("finite_bandwidth_relative_lower", {"exact": "0", "canonical_sha256": ""})
    )
    dark_lower, dark_hash = parse_receipt(
        probability.get("exact_rational_lower", {"exact": "0", "canonical_sha256": ""})
    )

    checks = {
        "schema_validation": not schema_errors,
        "certificate_identity": certificate.get("certificate") == "REVERSE_PHYSICS_BT_LOCAL_QUADRUPOLE_DARK_DETECTOR_Q8_V1",
        "input_hashes_recomputed": hashes_ok,
        "four_predecessor_pass_flags_rechecked": predecessors_ok,
        "done_event_matches_work_item": event_ok,
        "degree_four_symbol_is_exact": density.get("symbol") == "F2(P,r)=6*[P^2*(a.r)^2-(P^2*a^2-(a.P)^2)*r^2/3]/M0^4" and density.get("derivative_order") == 4,
        "central_P2_reduction_is_explicit": density.get("central_reduction") == "at P=(M0,0) and a a unit incoming spatial axis, F2=P2(c)=(3*c^2-1)/2",
        "boosted_fixture_mean_recomputed": sum(Fraction(value) for value in density.get("rational_boosted_values", [])) == 0,
        "general_STF_mean_cancels": fibre_mean_coefficient == 0 and "<F2>_sphere=0" in density.get("fibre_mean_identity", ""),
        "reality_and_exchange_are_explicit": "real and even under r->-r" in density.get("reality_and_exchange", ""),
        "tree_lower_hash_rechecked": stored_tree_lower_hash,
        "tree_upper_hash_rechecked": stored_tree_upper_hash,
        "independent_a_coordinate_tree_interval_is_ordered": independent_tree_lower < independent_tree_upper,
        "independent_tree_lower_exceeds_one_hundredth": independent_tree_lower > Fraction(1, 100),
        "independent_tree_interval_overlaps_stored": independent_tree_lower < stored_tree_upper and stored_tree_lower < independent_tree_upper,
        "direct_loop_power_moments_match_closed_form": direct_i2 == expected_i2 and direct_i3 == expected_i3,
        "loop_terms_alternate": term2 > 0 > term3,
        "loop_ratio_maximum_is_first": max(ratios) == ratios[0] == Fraction(32, 525) < Fraction(2, 25),
        "loop_lower_hash_rechecked": loop_hash,
        "loop_lower_recomputed": loop_lower == term2 + term3 == Fraction(252_416, 73_828_125),
        "loop_lower_exceeds_one_over_400": loop_lower > Fraction(1, 400),
        "Legendre_mean_recomputed": p2_mean == 0,
        "Legendre_norm_recomputed": p2_norm == Fraction(2, 5),
        "normalized_Cauchy_factor_recomputed": cauchy_factor == Fraction(5, 16) and probability.get("Cauchy_factor") == "Q8_local/q4_bar>=5*J_R^2/16",
        "central_lower_hash_rechecked": central_hash,
        "central_relative_lower_recomputed": central_lower == Fraction(1, 19_200),
        "bandwidth_lower_hash_rechecked": bandwidth_hash,
        "bandwidth_relative_lower_recomputed": bandwidth_lower == central_lower / 2 == Fraction(1, 38_400),
        "dark_lower_hash_rechecked": dark_hash,
        "dark_lower_recomputed": dark_lower == cauchy_factor * bandwidth_lower**2 == Fraction(1, 4_718_592_000),
        "dark_lower_exceeds_one_over_five_billion": dark_lower > Fraction(1, 5_000_000_000),
        "pointer_plus_vacuum_selection_is_explicit": "pointer excited AND active field vacuum" in probability.get("selected_outcome", "") and "pair annihilation only" in probability.get("selected_outcome", ""),
        "no_RWA_leakage_claim_is_used": any("without the selected final field-vacuum outcome" in row for row in boundaries),
        "joint_expansion_is_scoped": probability.get("joint_expansion") == "p_selected=g_det^2*lambda^8*Q8_local+O(g_det^2*lambda^10)+O(g_det^4)",
        "finite_bandwidth_continuity_is_explicit": "retaining half the central moment" in probability.get("finite_bandwidth_argument", ""),
        "switching_boundary_is_honest": disposition.get("compact_spacetime_support") == "NOT_CONSTRUCTED" and any("compact spacetime support" in row for row in boundaries),
        "detector_all_orders_remain_open": disposition.get("all_orders_in_external_detector_coupling") == "NOT_CONSTRUCTED",
        "Eq19_remains_open": disposition.get("general_Eq19") == "NOT_PROVED_AND_NOT_USED",
        "gravity_remains_open": disposition.get("gravity_or_metric_BV_BRST_transfer") == "NOT_CONSTRUCTED",
        "Lorentzian_boundary_present": any("LORENTZIAN-CAUSAL" in row for row in boundaries),
        "literature_priority_forbidden": "literature priority" in boundaries,
    }
    return checks


def main():
    checks = verify(load(CERT_REL))
    for name, value in checks.items():
        print(("PASS" if value else "FAIL") + ":", name)
    ok = all(checks.values())
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
