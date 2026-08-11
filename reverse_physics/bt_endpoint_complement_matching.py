#!/usr/bin/env python3
"""Exact matching law for the BT endpoint extension and missing Krein leg."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from math import comb


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_ENDPOINT_COMPLEMENT_MATCHING_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-endpoint-complement-matching-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-endpoint-complement-matching.md"
SOURCE = "523a9fa799a3f5eda93849fdb4d0e9221ff7b74b"
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-endpoint-complement-matching.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_ENDPOINT_EXTENSION_AMBIGUITY_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FINITE_PHYSICAL_MOLLER_COLUMN_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1.json",
]


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def derivative_at(coefficients, order, point):
    total = Fraction(0)
    for power, coefficient in enumerate(coefficients):
        if power < order:
            continue
        falling = 1
        for factor in range(power - order + 1, power + 1):
            falling *= factor
        total += coefficient * falling * Fraction(point) ** (power - order)
    return total


def reflect(coefficients):
    result = [Fraction(0)] * len(coefficients)
    for power, coefficient in enumerate(coefficients):
        for degree in range(power + 1):
            result[degree] += coefficient * comb(power, degree) * (-1) ** degree
    return result


def subtract_second_jet(coefficients):
    result = list(coefficients) + [Fraction(0)] * max(0, 3 - len(coefficients))
    result[0] -= derivative_at(coefficients, 0, 0)
    result[1] -= derivative_at(coefficients, 1, 0)
    result[2] -= derivative_at(coefficients, 2, 0) / 2
    return result


def left_triple_plus(coefficients):
    remainder = subtract_second_jet(coefficients)
    return sum(
        coefficient / Fraction(power - 2)
        for power, coefficient in enumerate(remainder)
        if power >= 3
    )


def symmetric_triple_plus(coefficients):
    return -Fraction(1, 2) * (
        left_triple_plus(coefficients) + left_triple_plus(reflect(coefficients))
    )


def endpoint_jet_action(coefficients, order):
    # E_n=delta_0^(n)+(-1)^n delta_1^(n), and
    # delta_x^(n)[f]=(-1)^n f^(n)(x).
    left = (-1) ** order * derivative_at(coefficients, order, 0)
    right = derivative_at(coefficients, order, 1)
    return left + right


def matrix_to_rationals(matrix):
    return [[rat(value) for value in row] for row in matrix]


def derive():
    import sympy as sp

    endpoint = load(INPUTS[1])
    moller = load(INPUTS[2])
    physical = load(INPUTS[3])
    eq19 = load(INPUTS[4])
    zero_mode = load(INPUTS[5])

    # The fixed two-profile lift.  Its three symmetric products are exactly
    # the independent endpoint probes used by the predecessor certificate.
    f00 = [Fraction(1)]
    f01 = [Fraction(0), Fraction(1), Fraction(-1)]
    f11 = [Fraction(0), Fraction(0), Fraction(1), Fraction(-2), Fraction(1)]
    probes = [f00, f01, f11]
    jet_matrix = [
        [endpoint_jet_action(probe, order) for order in range(3)]
        for probe in probes
    ]
    reference_actions = [symmetric_triple_plus(probe) for probe in probes]
    determinant = sp.Matrix(jet_matrix).det()

    rho = sp.symbols("rho", positive=True)
    c0, c1, c2 = sp.symbols("c0 c1 c2", real=True)
    b00, b01, b11 = [sp.Rational(value.numerator, value.denominator)
                     for value in reference_actions]
    K = sp.Matrix(
        [
            [b00 + 2 * c0, b01 - 2 * c1 - 4 * c2],
            [b01 - 2 * c1 - 4 * c2, b11 + 4 * c2],
        ]
    )
    target = sp.Matrix([[0, -rho], [-rho, -2]])
    solutions = sp.solve(
        [K[0, 0] - target[0, 0], K[0, 1] - target[0, 1],
         K[1, 1] - target[1, 1]],
        [c0, c1, c2],
        dict=True,
    )
    solution = solutions[0]
    solved_K = sp.simplify(K.subs(solution))

    # Reference-independent affine law.  Any other fixed reference changes
    # the intercepts but cannot remove dc1/drho=1/2.
    beta00, beta01, beta11 = sp.symbols("beta00 beta01 beta11", real=True)
    generic_solution = {
        c0: -beta00 / 2,
        c2: (-2 - beta11) / 4,
        c1: (rho + beta01 + beta11 + 2) / 2,
    }

    fixture_rows = []
    for index, row in enumerate(physical["amplitude_factorization"]["exact_fixtures"]):
        rho_i = frac(row["rho"])
        substitutions = {rho: sp.Rational(rho_i.numerator, rho_i.denominator)}
        coeffs = [sp.factor(solution[symbol].subs(substitutions))
                  for symbol in (c0, c1, c2)]
        K_i = sp.simplify(K.subs(dict(zip((c0, c1, c2), coeffs))))
        fixture_rows.append(
            {
                "fixture_index": index,
                "rho": rat(rho_i),
                "coefficients": [rat(Fraction(value)) for value in coeffs],
                "matched_gram": [
                    [rat(Fraction(K_i[i, j])) for j in range(2)]
                    for i in range(2)
                ],
            }
        )

    fixture_rhos = [frac(row["rho"]) for row in fixture_rows]
    fixture_c1s = [frac(row["coefficients"][1]) for row in fixture_rows]
    rho_a, rho_b = sp.symbols("rho_a rho_b", real=True)
    target_difference = sp.Matrix([[0, rho_b - rho_a], [rho_b - rho_a, 0]])

    imported_jet_matrix = [
        [frac(value) for value in row]
        for row in endpoint["extension_classification"]["jet_action_matrix"]
    ]
    imported_missing = moller["minimal_public_Rt_compression"]["missing_covariant_gram"]
    checks = {
        "predecessor_checks": all(
            value["checks"]["ok"]
            for value in (endpoint, moller, physical, eq19, zero_mode)
        ),
        "fixed_profiles_reconstruct_certified_probes": probes == [f00, f01, f11],
        "jet_action_matrix_reconstructed": jet_matrix == imported_jet_matrix,
        "jet_action_matrix_is_invertible": determinant == -16,
        "triple_plus_reference_actions": reference_actions == [0, 0, Fraction(3, 2)],
        "affine_reference_term_retained": b11 == sp.Rational(3, 2),
        "forced_missing_gram_imported": imported_missing == [["0", "-rho"], ["-rho", "-2"]],
        "unique_symbolic_solution": len(solutions) == 1,
        "matching_law": solution == {
            c0: 0,
            c1: sp.Rational(7, 4) + rho / 2,
            c2: -sp.Rational(7, 8),
        },
        "symbolic_pointwise_match": solved_K == target,
        "generic_reference_solution": sp.simplify(
            generic_solution[c1] - (rho + beta01 + beta11 + 2) / 2
        ) == 0,
        "reference_invariant_slope": sp.diff(generic_solution[c1], rho) == sp.Rational(1, 2),
        "only_delta_prime_coordinate_varies": (
            sp.diff(solution[c0], rho) == 0
            and sp.diff(solution[c1], rho) == sp.Rational(1, 2)
            and sp.diff(solution[c2], rho) == 0
        ),
        "three_physical_fixtures_imported": len(fixture_rows) == 3,
        "physical_fixture_rhos_distinct": len(set(fixture_rhos)) == 3,
        "physical_fixture_matches": all(
            row["matched_gram"]
            == [[rat(0), rat(-frac(row["rho"]))],
                [rat(-frac(row["rho"])), rat(-2)]]
            for row in fixture_rows
        ),
        "required_delta_prime_coefficients_distinct": len(set(fixture_c1s)) == 3,
        "two_target_grams_equal_only_if_rhos_equal": (
            target_difference.subs(rho_b, rho_a) == sp.zeros(2)
            and target_difference[0, 1] == rho_b - rho_a
        ),
        "fixed_coefficients_cannot_match_distinct_rhos": all(
            fixture_c1s[i] != fixture_c1s[j]
            for i in range(len(fixture_c1s))
            for j in range(i + 1, len(fixture_c1s))
        ),
        "pointwise_fit_remains_algebraically_possible": all(
            row["matched_gram"][0][1] == rat(-frac(row["rho"]))
            for row in fixture_rows
        ),
        "public_eq19_only_finite_order": eq19["disposition"]["finite_mode_order_lambda_Eq19"] == "PROVED_WITH_Q1_ZERO",
        "zero_mode_trace_still_missing": zero_mode["disposition"]["Eq19_order_lambda_pushforward"] == "NOT_REPRODUCED_FROM_PUBLIC_DATA",
        "public_and_physical_maps_stay_distinct": moller["disposition"]["public_Rt_equals_physical_splitting"] == "EXACTLY_FALSE",
        "complete_physical_theory_stays_open": moller["disposition"]["complete_BT_probability"] == "NOT_CONSTRUCTED",
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    return locals()


def build():
    d = derive()
    checks = d["checks"]
    return {
        "certificate": "REVERSE_PHYSICS_BT_ENDPOINT_COMPLEMENT_MATCHING_V1",
        "schema_version": "reverse-physics-bt-endpoint-complement-matching-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact affine matching classification and fixed-extension nonuniversality theorem on the declared BT endpoint two-profile lift",
        "question": "Can one fixed reflection-even scaling-degree-three extension of the public BT endpoint kernel supply the forced two-dimensional cross-Krein complement for every physical external-jet fibre, and what endpoint coefficients are necessary if matching is imposed pointwise?",
        "answer": "On the declared fixed two-profile lift v=(1,z(1-z)), the three profile products are exactly the certified independent probes 1, z(1-z), and z^2(1-z)^2. The triple-plus reference extension acts on them by (0,0,3/2), while the reflection-even endpoint jets have action matrix [[2,0,0],[0,-2,-4],[0,0,4]]. Consequently the complete affine extension induces K(c)=[[2c0,-2c1-4c2],[-2c1-4c2,3/2+4c2]]. Exact equality with the missing physical Gram [[0,-rho],[-rho,-2]] has the unique solution c0=0, c2=-7/8, and c1=7/4+rho/2. The three imported exact physical fixtures have distinct positive rho and therefore require distinct c1. No single rho-independent coefficient triple can match even two of them, hence no fixed universal extension on this declared lift supplies the physical complement across the continuum. The conclusion is reference-independent: changing the fixed affine reference shifts intercepts, but dc1/drho=1/2 remains. Pointwise matching is algebraically possible and uniquely classified; it requires kinematics-dependent delta-prime data. The public Letter and the certified finite order-lambda R_t sector do not derive that dependence. This is a scoped obstruction to the fixed-profile, fixed-coefficient endpoint shortcut, not a no-go for spectator-dependent local terms, a dynamically generated zero-mode/higher-composite block, Eq. (19) all orders, or the constructed finite physical column.",
        "declared_lift": {
            "endpoint_variable": "z in (0,1)",
            "profiles": ["v0(z)=1", "v1(z)=z*(1-z)"],
            "product_probes": ["f00=1", "f01=z*(1-z)", "f11=z^2*(1-z)^2"],
            "interpretation": "This is the minimal fixed two-profile Gram lift of the three certified reflection-even endpoint probes. It is a diagnostic carrier, not a derivation that every BT endpoint or spectator-dependent completion must use these profiles.",
        },
        "endpoint_extension": {
            "interior_shape": d["endpoint"]["interior_kernel"]["partial_fraction"],
            "reference": "H_plus=-(1/2)*([z^-3]_+++[(1-z)^-3]_+++)",
            "endpoint_basis": [
                "E0=delta_0+delta_1",
                "E1=delta_0_prime-delta_1_prime",
                "E2=delta_0_double_prime+delta_1_double_prime",
            ],
            "jet_action_matrix": matrix_to_rationals(d["jet_matrix"]),
            "jet_matrix_determinant": rat(d["determinant"]),
            "reference_actions_on_product_probes": [rat(value) for value in d["reference_actions"]],
            "induced_gram": "K(c)=[[2*c0,-2*c1-4*c2],[-2*c1-4*c2,3/2+4*c2]]",
        },
        "matching_theorem": {
            "target_gram": "G_missing(rho)=[[0,-rho],[-rho,-2]]",
            "unique_coefficients": ["c0=0", "c1=7/4+rho/2", "c2=-7/8"],
            "coefficient_derivative_with_respect_to_rho": ["0", "1/2", "0"],
            "generic_fixed_reference_law": [
                "c0=-beta00/2",
                "c1=(rho+beta01+beta11+2)/2",
                "c2=(-2-beta11)/4",
            ],
            "reference_invariant_statement": "For every fixed affine reference with probe actions beta00,beta01,beta11, the required delta-prime coordinate has derivative dc1/drho=1/2. A change of fixed reference changes only the intercept.",
            "pointwise_status": "UNIQUE_ALGEBRAIC_MATCH_EXISTS_FOR_EACH_FIXED_RHO",
            "universal_status": "NO_SINGLE_RHO_INDEPENDENT_COEFFICIENT_TRIPLE_MATCHES_DISTINCT_PHYSICAL_RHOS",
        },
        "physical_fixtures": d["fixture_rows"],
        "universality_obstruction": {
            "proof": "K(c) is fixed when c is fixed. If K(c)=G_missing(rho_a)=G_missing(rho_b), subtraction gives [[0,rho_b-rho_a],[rho_b-rho_a,0]]=0, hence rho_a=rho_b. The imported physical domain contains three exact fixtures with distinct rho, so one fixed c cannot cover it.",
            "varying_coordinate": "Only c1, the coefficient of delta_0_prime-delta_1_prime, must vary; c0 and c2 remain 0 and -7/8 relative to H_plus.",
            "scope": "The obstruction applies to a rho-independent reflection-even extension on the declared fixed profiles. It does not exclude endpoint coefficients depending on external invariants, a different dynamically derived profile lift, or a non-endpoint complement.",
        },
        "disposition": {
            "fixed_profile_endpoint_matching_system": "SOLVED_EXACTLY",
            "pointwise_endpoint_match": "EXISTS_UNIQUELY_BUT_IS_NOT_DERIVED_FROM_BT_DYNAMICS",
            "fixed_universal_endpoint_extension": "EXACTLY_OBSTRUCTED_ON_DISTINCT_PHYSICAL_RHO_FIXTURES",
            "spectator_dependent_or_dynamical_extension": "NOT_CLASSIFIED",
            "BT_derived_missing_complement": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED",
            "complete_BT_probability": "NOT_CONSTRUCTED",
            "physical_two_sided_S_operator": "NOT_CONSTRUCTED",
        },
        "assumptions": [
            "The endpoint distribution is lifted on the fixed two-profile diagnostic carrier v=(1,z(1-z)); no claim is made that every dynamical BT completion is confined to this carrier.",
            "The complete extension is parameterized relative to the certified triple-plus reference, whose nonzero f11 action 3/2 is retained rather than silently discarded.",
            "The forced missing Gram is imported pointwise above unequal-mass threshold from the finite physical Moller-column compression theorem.",
            "A universal extension means one rho-independent coefficient triple on the declared fixed profiles; coefficients depending on spectator invariants are a different, still-open object.",
        ],
        "does_not_establish": [
            "a no-go theorem for every local or spectator-dependent distribution extension",
            "that the pointwise fitted delta-prime coefficient is generated by Bateman--Turok dynamics",
            "a dynamical zero-mode, squeezed-vacuum, or higher-composite complement",
            "the all-order public R_t projector pushforward or Bateman--Turok Eq. (19)",
            "a fourth physical jump, complete BT probability, or finite NLO constant",
            "a two-sided spacetime Moller, LSZ, S, detector, or AQFT construction",
            "a metric or BRST transfer to pure Weyl gravity",
            "a new physical or spacetime dimension",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "missing_object_ledger": [
            "derive or obstruct the required rho-dependent delta-prime coefficient from the covariant zero-mode, squeezed-vacuum, or higher-composite BT dynamics",
            "decide whether locality and covariance permit the required dependence on the external invariant rho on the complete endpoint test-function domain",
            "construct the missing generalized-Born trace on the dynamical zero-mode module and evaluate the neutral squeeze contribution",
            "derive the fourth physical jump and eight-point pre-trace quotient as the independent all-order discriminator",
            "construct arbitrary incoming-sector and reverse columns before any two-sided physical scattering claim",
        ],
        "next_gate": "The fixed universal endpoint shortcut is closed on the declared minimal lift. The nearest Eq. (19) gate is now to compute the covariant zero-mode and squeezed-vacuum endpoint distribution on the same external-jet domain and test whether BT dynamics produces the necessary c1(rho)=7/4+rho/2 law, or an equivalent law after a fixed reference change, while retaining the public cross-CCR identities and the nonzero raised trace of the missing complement. If locality forbids this spectator dependence, that would upgrade the scoped fixed-extension obstruction; if the dynamics derives it, the public-to-physical compression bridge would be supplied pointwise. The independent all-order physical gate remains the eight-point fourth quotient.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "producer_method": "Exact rational endpoint-distribution actions on polynomial probes, exact SymPy solution of the affine three-equation Gram-matching system, and exact substitution of all physical rational rho fixtures. No floating-point arithmetic is used.",
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096v1",
                "equations": ["Eq. (16)", "Eq. (19)", "Appendix C"],
            },
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_endpoint_complement_matching.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_endpoint_complement_matching.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest reverse_physics.tests.test_bt_endpoint_complement_matching",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "report": REPORT,
        "schema": SCHEMA,
    }


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    value = build()
    rendered = canonical(value)
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check and os.path.exists(args.output):
        with open(args.output, encoding="utf-8") as handle:
            if handle.read() != rendered:
                print("certificate drift", file=sys.stderr)
                return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    if value["checks"]["failures"]:
        print("failures:", ", ".join(value["checks"]["failures"]))
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
