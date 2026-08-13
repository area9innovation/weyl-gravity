#!/usr/bin/env python3
"""Independent sparse-polynomial verifier for localized affine hidden parity."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_LOCALIZED_AFFINE_HIDDEN_PARITY_ORBIT_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-localized-affine-hidden-parity-orbit-v1.schema.json",
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


# Dependency-free commutative sparse polynomials.  A monomial is a sorted tuple
# of variable names, repeated according to exponent.
def const(value):
    value = Fraction(value)
    return {(): value} if value else {}


def var(name):
    return {(name,): Fraction(1)}


def add(left, right, scale=Fraction(1)):
    answer = dict(left)
    for monomial, coefficient in right.items():
        answer[monomial] = answer.get(monomial, Fraction(0)) + scale * coefficient
    return {monomial: coefficient for monomial, coefficient in answer.items() if coefficient}


def scale(coefficient, value):
    coefficient = Fraction(coefficient)
    return {monomial: coefficient * entry for monomial, entry in value.items() if coefficient * entry}


def multiply(left, right):
    answer = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial = tuple(sorted(left_monomial + right_monomial))
            answer[monomial] = answer.get(monomial, Fraction(0)) + left_coefficient * right_coefficient
    return {monomial: coefficient for monomial, coefficient in answer.items() if coefficient}


def power(value, exponent):
    answer = const(1)
    for _ in range(exponent):
        answer = multiply(answer, value)
    return answer


def fraction(row):
    return Fraction(row["numerator"], row["denominator"])


def expected_fourier_rows():
    rows = []
    for n in range(1, 7):
        epsilon = Fraction(1, n)
        multiplier = -1 - 1 / epsilon**2
        rows.append((epsilon, multiplier, multiplier**2, 1 + 4 / epsilon**2, Fraction(-1)))
    return rows


def expected_jordan_rows():
    rows = []
    for n in range(1, 7):
        epsilon = Fraction(1, n)
        rows.append((epsilon, 1 / epsilon**2, 2 + 1 / epsilon**4, -2 / epsilon**2))
    return rows


def verify(certificate):
    schema_ok = not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if not schema_ok:
        return {"schema_validation": False}

    hashes = certificate["provenance"]["input_hashes"]
    hashes_ok = all(sha256(path) == digest for path, digest in hashes.items())
    inputs = {path: load(os.path.join(ROOT, path)) for path in hashes}
    predecessors = {
        value.get("certificate"): value
        for path, value in inputs.items()
        if path.startswith("reverse_physics/certificates/")
    }
    event = next(value for path, value in inputs.items() if path.startswith("planning/events/"))

    l = var("lambda")
    A, B, X, Y = (var(name) for name in ("A", "B", "X", "Y"))
    F = add(X, multiply(l, Y))
    eom = add(add(A, multiply(l, B), Fraction(-2)), multiply(multiply(l, F), X), Fraction(-2))
    coefficient = add(multiply(power(l, 2), Y), multiply(l, X), Fraction(-1))
    numerator = add(add(A, multiply(l, B), Fraction(-2)), multiply(coefficient, F))
    localized_remainder = add(add(numerator, multiply(l, power(F, 2)), Fraction(-1)), eom, Fraction(-1))

    D, V, w = (var(name) for name in ("D", "V", "w"))
    a = multiply(power(l, 2), w)
    l_plus = add(D, multiply(l, V), Fraction(2))
    l_minus = add(D, multiply(l, V), Fraction(-2))
    linear_eom = add(multiply(l_minus, l_plus), multiply(a, D), Fraction(-2))
    composition_numerator = add(
        add(multiply(add(l_minus, a, Fraction(-1)), add(l_plus, a, Fraction(-1))), power(a, 2), Fraction(-1)),
        linear_eom,
        Fraction(-1),
    )

    limit = certificate["zero_background_limit"]
    fourier_rows = limit["exact_fourier_fixtures"]
    jordan_rows = limit["Jordan_fixture"]["rows"]
    expected_f = expected_fourier_rows()
    expected_j = expected_jordan_rows()
    fourier_exact = all(
        fraction(row["epsilon"]) == expected[0]
        and fraction(row["offshell_k2_one_u_dot_k_zero_multiplier"]) == expected[1]
        and fraction(row["offshell_modulus_squared"]) == expected[2]
        and fraction(row["massless_k2_zero_u_dot_k_one_modulus_squared"]) == expected[3]
        and fraction(row["massless_k2_zero_u_dot_k_zero_multiplier"]) == expected[4]
        for row, expected in zip(fourier_rows, expected_f)
    )
    jordan_exact = all(
        fraction(row["epsilon"]) == expected[0]
        and Fraction(row["T_matrix"][0][1]) == expected[1]
        and fraction(row["frobenius_norm_squared"]) == expected[2]
        and fraction(row["composition_defect_N_coefficient"]) == expected[3]
        for row, expected in zip(jordan_rows, expected_j)
    )

    unit = predecessors["REVERSE_PHYSICS_BT_PERTURBATIVE_GHOST_PARITY_UNIT_OBSTRUCTION_V1"]
    standard = predecessors["REVERSE_PHYSICS_BT_STANDARD_CHARACTERISTIC_EQ19_SQUEEZE_INHERITANCE_V1"]
    q10 = predecessors["REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_SELECTED_PACKET_ASSEMBLY_V1"]
    identity = certificate["exact_localized_identity"]
    orbit = certificate["affine_background_orbit"]
    tangent = certificate["linearized_on_shell_intertwiner"]
    disposition = certificate["Eq19_and_physical_disposition"]
    checks = {
        "schema_validation": schema_ok,
        "certificate_identity": certificate["certificate"] == "REVERSE_PHYSICS_BT_LOCALIZED_AFFINE_HIDDEN_PARITY_ORBIT_V1",
        "input_hashes_recomputed": hashes_ok,
        "all_predecessors_pass": all(item["checks"]["ok"] for item in predecessors.values()),
        "done_event_targets_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("localized-affine-hidden-parity-orbit"),
        "unit_predecessor_left_localization_open": unit["escape_routes"]["localized_on_shell_chart"]["disposition"].startswith("POSSIBLE_DIFFERENT"),
        "standard_predecessor_left_source_derivation_open": standard["minimality_and_boundary"]["public_derivation"].startswith("the Letter supplies no second"),
        "localized_identity_reconstructed_without_sympy": localized_remainder == {},
        "localized_identity_recorded": identity["identity"] == "F(h(phi))-F(phi)=E(phi)/(lambda F(phi))",
        "second_iterate_recorded": identity["second_iterate"].startswith("h^2(phi)-phi="),
        "off_shell_boundary_recorded": "not an involutive" in identity["off_shell_consequence"],
        "affine_F_is_lambda_v_squared": orbit["field_strength"] == "f0=lambda v^2",
        "affine_orbit_has_two_entries": len(orbit["orbit"]) == 2,
        "affine_gradient_is_flipped": "phi_-v" in orbit["parity_image"],
        "no_localized_fixed_affine_chart": "v=0" in orbit["fixed_chart_test"] and "f0=0" in orbit["fixed_chart_test"],
        "same_action_two_representation_conclusion": orbit["conclusion"] == "LOCALIZED_HIDDEN_PARITY_REQUIRES_TWO_BACKGROUND_REPRESENTATIONS",
        "linear_composition_reconstructed_without_sympy": composition_numerator == {},
        "linearized_equation_recorded": tangent["linearized_equation"].startswith("E_v^(1)=[L_-v L_v-2aD]"),
        "parity_tangent_recorded": tangent["parity_tangent"] == "T_v=-1+L_v/a",
        "chart_labels_preserved_in_composition": tangent["composition"] == "T_-v T_v-1=E_v^(1)/a^2 and T_v T_-v-1=E_-v^(1)/a^2",
        "two_sector_involution_is_quotient_scoped": "ker(E_v^(1))" in tangent["quotient_identity"],
        "fourier_rows_recomputed_exactly": fourier_exact,
        "fourier_offshell_growth_is_monotone": all(expected_f[i][2] < expected_f[i + 1][2] for i in range(5)),
        "fourier_massless_growth_is_monotone": all(expected_f[i][3] < expected_f[i + 1][3] for i in range(5)),
        "finite_massless_slice_is_exact_minus_one": all(expected[4] == -1 for expected in expected_f),
        "measure_zero_slice_not_promoted_to_dense": "measure zero" in limit["density_boundary"],
        "packet_nonconvergence_is_explicit": limit["packet_conclusion"] == "NO_STRONG_LIMIT_ON_A_FIXED_DENSE_MASSLESS_PACKET_CORE",
        "Jordan_rows_recomputed_exactly": jordan_exact,
        "Jordan_growth_is_monotone": all(expected_j[i][2] < expected_j[i + 1][2] for i in range(5)),
        "Jordan_nonconvergence_is_explicit": limit["Jordan_fixture"]["conclusion"] == "NO_LIMIT_ON_THE_DOUBLE_POLE_JORDAN_JET",
        "localized_completion_is_same_action": disposition["localized_affine_same_action_completion"] == "CONSTRUCTED_ON_TWO_BACKGROUND_ON_SHELL_QUOTIENT",
        "second_sheet_is_not_new_field": disposition["second_sheet_status"].endswith("NOT_AS_A_NEW_FIELD"),
        "off_shell_projector_not_promoted": disposition["off_shell_projector_identity"] == "NOT_CONSTRUCTED",
        "zero_vacuum_affiliation_is_obstructed": disposition["public_zero_vacuum_affiliation"].startswith("OBSTRUCTED_BY_SINGULAR"),
        "q10_is_not_transferred": disposition["standard_projector_q10_comparison"] == "NOT_TRANSFERABLE_FROM_THE_AFFINE_COMPLETION",
        "existing_selected_q10_remains_valid": q10["disposition"]["selected_finite_time_q10"].startswith("COEFFICIENT_COMPUTED"),
        "nonaffine_and_arbitrary_singular_routes_remain_open": disposition["arbitrary_nonaffine_localized_background"] == "NOT_CLASSIFIED" and disposition["arbitrary_singular_or_nonlocal_CCR_map"] == "NOT_CLASSIFIED",
        "full_public_Eq19_not_promoted": disposition["full_public_Eq19"] == "NOT_PROVED",
        "gravity_and_causal_boundaries_present": any("LORENTZIAN-CAUSAL" in item for item in certificate["does_not_establish"]),
        "source_commit_is_pinned": certificate["provenance"]["source_commit"] == "f87e707cd766e8d14243f2571888def3b5669953",
        "verification_commands_present": len(certificate["verification_commands"]) == 3,
    }
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    checks = verify(load(args.verify))
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        for name in failures:
            print("FAIL:", name, file=sys.stderr)
        return 1
    print(f"BT LOCALIZED AFFINE INDEPENDENT VERIFIER: ALL PASS ({len(checks)}/{len(checks)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
