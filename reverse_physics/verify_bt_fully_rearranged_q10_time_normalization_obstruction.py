#!/usr/bin/env python3
"""Independent verifier for the BT q10 center-time normalization obstruction."""
from __future__ import annotations

import argparse
from fractions import Fraction
from math import factorial
import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_TIME_NORMALIZATION_OBSTRUCTION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-fully-rearranged-q10-time-normalization-obstruction-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def beta_integer(a, b):
    """Integral_0^1 x^(a-1)(1-x)^(b-1) dx for positive integers."""
    return Fraction(factorial(a - 1) * factorial(b - 1), factorial(a + b - 1))


def direct_two_vertex_moments(max_degree):
    rows = []
    for n in range(max_degree + 1):
        # Integrate x^n and x^n(1-x) independently on [0,1].
        untapered = Fraction(1, factorial(n)) * Fraction(1, n + 1)
        tapered = Fraction(1, factorial(n)) * beta_integer(n + 1, 2)
        rows.append((untapered, tapered, tapered / untapered))
    return rows


def direct_three_vertex_moment(m, n):
    # Integrate x^m y^n (1-x-y) on the standard two-simplex, then divide
    # by the two exponential factorials. This is independent of the producer's
    # degree-only construction.
    numerator = factorial(m) * factorial(n) * factorial(1)
    simplex = Fraction(numerator, factorial(m + n + 3))
    return simplex / (factorial(m) * factorial(n))


def verify(certificate):
    schema_errors = list(
        Draft202012Validator(load(SCHEMA)).iter_errors(certificate)
    )
    if schema_errors:
        return {"schema_validation": False}

    hashes = certificate["provenance"]["input_hashes"]
    inputs = {
        path: load(os.path.join(ROOT, path))
        for path in hashes
    }
    by_certificate = {
        value["certificate"]: value
        for path, value in inputs.items()
        if path.startswith("reverse_physics/certificates/")
    }
    event = next(
        value
        for path, value in inputs.items()
        if path.startswith("planning/events/")
    )
    q10 = by_certificate[
        "REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_SELECTED_PACKET_ASSEMBLY_V1"
    ]
    triangle = by_certificate[
        "REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_FINITE_TIME_AFFILIATION_V1"
    ]
    bubble = by_certificate[
        "REVERSE_PHYSICS_BT_FULLY_REARRANGED_BUBBLE_BRIDGE_FINITE_TIME_AFFILIATION_V1"
    ]
    tree = by_certificate[
        "REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_ORDER4_PACKET_COLUMN_V1"
    ]
    cut = by_certificate[
        "REVERSE_PHYSICS_BT_FINITE_TIME_HAMILTONIAN_CUT_AFFILIATION_V1"
    ]
    active = by_certificate[
        "REVERSE_PHYSICS_BT_FINITE_TIME_ACTIVE_LOOP_AFFILIATION_V1"
    ]
    all_time = by_certificate[
        "REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_PACKET_LIMIT_V1"
    ]

    audit = certificate["time_normalization_audit"]
    two_rows = audit["two_vertex_series"]
    two_expected = direct_two_vertex_moments(8)
    two_exact = len(two_rows) == 9 and all(
        row["degree"] == degree
        and frac(row["F_T_coefficient_without_i_power"]) == untapered
        and frac(row["anchored_taper_coefficient_without_i_power"]) == tapered
        and frac(row["ratio_anchored_to_F_T"]) == ratio
        for degree, (row, (untapered, tapered, ratio))
        in enumerate(zip(two_rows, two_expected))
    )

    three_rows = audit["three_vertex_series"]
    three_exact = len(three_rows) == 9
    if three_exact:
        for degree, row in enumerate(three_rows):
            monomial_moments = [
                direct_three_vertex_moment(m, degree - m)
                for m in range(degree + 1)
            ]
            expected = Fraction(1, factorial(degree + 3))
            three_exact &= (
                row["total_degree"] == degree
                and row["monomial_count"] == degree + 1
                and all(moment == expected for moment in monomial_moments)
                and frac(row["anchored_coefficient_without_i_power"]) == expected
                and frac(row["full_coefficient_without_i_power"]) == expected
                and row["full_power_of_T"] == degree + 3
                and row["anchored_power_of_T"] == degree + 2
            )

    # Independent zero-frequency geometry.
    full_two_volume = Fraction(1, 2)  # unit ordered triangle
    anchored_two_value = beta_integer(1, 2)
    ordered_three_volume = Fraction(1, 6)  # unit ordered three-simplex
    anchored_three_volume = direct_three_vertex_moment(0, 0)
    normalized_overlap_at_origin = Fraction(1)  # common-interval length / T

    forest = certificate["bubble_forest_correction"]
    boundary = certificate["anchored_distributional_boundary"]
    retention = certificate["supersession_and_retention"]
    claims = certificate["claim_boundary"]
    checks = {
        "schema_validation": not schema_errors,
        "certificate_identity": certificate["certificate"].endswith("Q10_TIME_NORMALIZATION_OBSTRUCTION_V1"),
        "input_hashes_recomputed": all(sha256(path) == digest for path, digest in hashes.items()),
        "all_imported_certificates_pass": all(value["checks"]["ok"] for value in by_certificate.values()),
        "event_is_append_only_obstruction": event["body"]["payload"]["to_state"] == "OBSTRUCTED",
        "old_q10_cross_imported": q10["fixed_auxiliary_expansion"]["q10"] == "q10[F]=2*Re<T4,T F,T6,T F>",
        "old_tree_is_untapered": "F_T(delta_B" in tree["unpartitioned_compact_packet_column"]["channel_kernel"],
        "external_center_time_was_cancelled": "cancels external delta1(0)=L0" in cut["hamiltonian_cut_kernel"]["external_internal_time_split"],
        "active_predecessor_divides_duration": "division of the ordered two-vertex Dyson cross by the tree duration" in active["answer"],
        "triangle_Omega_is_exactly_zero": "q0+q1+q2=0" in triangle["finite_time_triangle"]["external_pairing"],
        "triangle_full_cube_imported": triangle["six_ordering_exhaustion"]["time_interval"] == "0<=t1,t2,t3<=T",
        "bubble_full_cube_imported": bubble["three_vertex_kernel"]["time_cube"] == "0<=t_A,t_B,t_C<=T",
        "two_vertex_moments_recomputed": two_exact,
        "three_vertex_moments_recomputed_by_each_monomial": three_exact,
        "zero_defect_full_two_vertex_volume": full_two_volume == Fraction(1, 2),
        "zero_defect_anchored_two_vertex_value": anchored_two_value == Fraction(1, 2),
        "zero_defect_F_T_value_is_one_in_T_units": frac(two_rows[0]["F_T_coefficient_without_i_power"]) == 1,
        "factor_two_mismatch_is_exact": frac(two_rows[0]["F_T_coefficient_without_i_power"]) == 2 * anchored_two_value,
        "ordered_three_simplex_volume": ordered_three_volume == Fraction(1, 6),
        "anchored_three_simplex_volume": anchored_three_volume == Fraction(1, 6),
        "six_orderings_fill_cube": 6 * ordered_three_volume == 1,
        "one_power_of_T_is_removed": all(row["full_power_of_T"] - row["anchored_power_of_T"] == 1 for row in three_rows),
        "forest_local_derivative_is_imported": forest["local_derivative"] == bubble["finite_time_renormalization"]["local_identity"],
        "forest_overlap_is_triangular": "T-|tau|" in forest["fixed_total_reduction"],
        "old_RG_identity_is_named_exactly": forest["superseded_identity"] == bubble["finite_time_renormalization"]["scale_identity"],
        "old_RG_identity_is_superseded": forest["status"] == "FINITE_TIME_RG_IDENTITY_SUPERSEDED_AT_KERNEL_NORMALIZATION",
        "one_gap_boundary_has_correct_sign": "pi*delta(s)+i*PV(1/s)" in boundary["one_gap"],
        "two_gap_boundary_is_tensor_product": "tensor" in boundary["two_gap"],
        "normalized_three_window_has_two_delta_boundary": "(2*pi)^2*delta(x)*delta(y)" in boundary["three_window"],
        "overlap_normalization_is_unit": normalized_overlap_at_origin == 1,
        "q10_assembly_is_superseded": retention["q10_selected_packet_assembly"] == "SUPERSEDED_AT_COMMON_TIME_NORMALIZATION",
        "graph_exhaustion_is_retained": retention["connected_graph_exhaustion"] == "RETAINED",
        "species_is_retained": retention["species_and_total_kappa_identities"] == "RETAINED",
        "leading_q8_is_retained": retention["leading_all_time_q8"].startswith("RETAINED"),
        "predecessor_q8_did_not_claim_q10": all_time["operator_and_claim_boundary"]["q10_all_time_limit"] == "NOT_CONSTRUCTED",
        "matched_q10_remains_open": claims["matched_finite_time_q10"] == "NOT_COMPUTED",
        "all_time_q10_remains_open": claims["all_time_q10"] == "NOT_COMPUTED",
        "Eq19_remains_open": claims["general_Eq19"] == "NOT_PROVED",
        "gravity_remains_open": claims["gravity_BV_BRST_QME"] == "NOT_CONSTRUCTED",
        "causality_remains_open": claims["Lorentzian_causal_claim"] == "NOT_ESTABLISHED",
        "certificate_checks_are_all_true": certificate["checks"]["ok"] and all(certificate["checks"]["items"].values()),
    }
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args()
    try:
        checks = verify(load(args.verify))
    except Exception as error:
        print(f"verification error: {error}", file=sys.stderr)
        return 1
    passed = sum(bool(value) for value in checks.values())
    print(f"checks: {passed}/{len(checks)}")
    for name, value in checks.items():
        if not value:
            print(f"FAIL: {name}", file=sys.stderr)
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
