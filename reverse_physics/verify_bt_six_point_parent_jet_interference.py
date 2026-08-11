#!/usr/bin/env python3
"""Independent verifier for the six-point BT parent-jet obstruction.

The amplitude rail explicitly enumerates all 220 invariant-triangle trees at
exact rational points.  The factorization and Gram rail is then rebuilt from
the resulting spectator components rather than imported from the producer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator

from verify_bt_six_point_strongly_ordered_tree import exact_tree_kernel


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_PARENT_JET_INTERFERENCE_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-six-point-parent-jet-interference-v1.schema.json",
)
SIX = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_STRONGLY_ORDERED_TREE_V1.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


POINTS = [
    (1, 4, 9, Fraction(1, 5), 10, 17),
    (2, 7, 5, Fraction(2, 7), 13, 23),
    (4, 1, 11, Fraction(3, 8), 19, 29),
]


def exact_fixture(a0, a1, tau1, a2, tau2):
    a0, a1, tau1, a2, tau2 = map(
        Fraction, (a0, a1, tau1, a2, tau2)
    )
    u = (
        2 * tau1 * (a0 + a1) - (a0 - a1) ** 2
    ) / (2 * tau1**2)
    v = a2 / 2
    n01 = a2 * (tau2 + a2) / (tau2 - 2 * a2)
    n10 = -u**2 * a2 * (2 * tau2 - a2) / (tau2 - 2 * a2)
    return [[u * v, n01], [n10, u * v]], 4 * n01 * n10


def verify(certificate):
    import sympy as sp

    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    disposition = certificate.get("disposition", {})
    species = certificate.get("species_interference", {})
    factorization = certificate.get("parent_jet_factorization", {})
    components = certificate.get("amplitude_components", {})
    preflight = (
        not errors
        and certificate.get("certificate")
        == "REVERSE_PHYSICS_BT_SIX_POINT_PARENT_JET_INTERFERENCE_V1"
        and disposition.get("second_positive_scalar_I2_species_jump")
        == "EXACTLY_OBSTRUCTED_ON_DECLARED_CARRIER"
        and disposition.get("scalar_five_over_3072_history_weight")
        == "RETAINED"
        and disposition.get("channel_resolved_CPTP_instrument")
        == "RETAINED_AS_ABSTRACT_POSITIVE_COMPLETION"
        and disposition.get("Eq19_all_orders") == "NOT_PROVED"
        and len(components.get("finite_e_leading_components", {})) == 7
        and len(components.get("strong_order_components", {})) == 7
        and components.get("strong_order_components", {}).get("1")
        == components.get("strong_order_components", {}).get("2")
        == components.get("strong_order_components", {}).get("4")
        != "0"
        and components.get("strong_order_components", {}).get("3")
        == components.get("strong_order_components", {}).get("5")
        == components.get("strong_order_components", {}).get("6")
        != "0"
        and frac(components.get("scalar_selected_history_relative_to_Born"))
        == Fraction(5, 3072)
        and factorization.get("u") != "0"
        and factorization.get("v") != "0"
        and species.get("raised_profile_normalized_endomorphism", [["0"]])[0][1]
        != "0"
        and factorization.get("locality_disposition")
        == "THE_CONSTANT_PARENT_COEFFICIENT_PERSISTS_BUT_THE_LINEAR_PARENT_COEFFICIENT_IS_NOT_AN_INNER_LOCAL_SPLITTING_COEFFICIENT"
        and species.get("physical_domain_sign")
        == "strictly negative for tau2>a2>0 and tau2!=2*a2"
        and "anything LORENTZIAN-CAUSAL"
        in certificate.get("does_not_establish", [])
    )
    if not preflight:
        return {"serialized_claim_preflight": False}

    a0, a1, a2, e, tau1, tau2 = sp.symbols(
        "a0 a1 a2 e tau1 tau2"
    )
    symbols = (a0, a1, a2, e, tau1, tau2)
    local = {symbol.name: symbol for symbol in symbols}
    finite = {
        int(mask): sp.cancel(sp.sympify(value, locals=local))
        for mask, value in components["finite_e_leading_components"].items()
    }
    strong = {
        int(mask): sp.factor(sp.sympify(value, locals=local))
        for mask, value in components["strong_order_components"].items()
    }
    hard_fixtures = load(SIX)["correlated_boundary"]["hard_fixtures"]
    explicit_ok = True
    tree_counts = set()
    for point in POINTS:
        substitutions = dict(zip(symbols, point))
        expected = {
            mask: Fraction(
                int(sp.numer(value.subs(substitutions))),
                int(sp.denom(value.subs(substitutions))),
            )
            for mask, value in finite.items()
        }
        for hard in hard_fixtures:
            order, count, _projected, leading = exact_tree_kernel(
                point, hard, return_leading=True
            )
            tree_counts.add(count)
            explicit_ok &= (
                order == 2
                and set(leading.coefficients) == set(expected)
                and all(
                    leading.coefficients[mask] == value
                    for mask, value in expected.items()
                )
            )

    finite_to_strong = all(
        sp.simplify(finite[mask].subs(e, 0) - strong[mask]) == 0
        for mask in finite
    )
    singleton_symmetry = strong[1] == strong[2] == strong[4]
    pair_symmetry = strong[3] == strong[5] == strong[6]
    F1, F2 = strong[1], strong[3]

    L0 = -a2**2 / (4 * tau2)
    Q0 = a2 * (2 * tau2 - a2) / (4 * tau2**2)
    L1 = a2 / (2 * tau2)
    Q1 = (tau2 + a2) / (2 * tau2**2)
    matrix = sp.Matrix([[L0, L1], [Q0, Q1]])
    u, v = [
        sp.factor(value) for value in matrix.inv() * sp.Matrix([F1, F2])
    ]
    twice_q = (
        2 * tau1 * (a0 + a1) - (a0 - a1) ** 2
    ) / (2 * tau1**2)
    twice_l = -(a0 - a1) ** 2 / (2 * tau1)

    B00 = sp.factor(6 * L0 * Q0)
    B01 = sp.factor(3 * (L0 * Q1 + Q0 * L1))
    B11 = sp.factor(6 * L1 * Q1)
    covariant = sp.Matrix(
        [[u**2 * B00, u * v * B01], [u * v * B01, v**2 * B11]]
    )
    J = sp.Matrix([[0, 1], [1, 0]])
    raised = (J * covariant / B01).applyfunc(sp.factor)
    discriminant = sp.factor(
        sp.trace(raised) ** 2 - 4 * raised.det()
    )
    expected_discriminant = sp.factor(
        -4
        * u**2
        * a2**2
        * (tau2 + a2)
        * (2 * tau2 - a2)
        / (tau2 - 2 * a2) ** 2
    )

    fixture_rows = species.get("exact_fixtures", [])
    fixtures_ok = len(fixture_rows) == 3
    for row in fixture_rows:
        expected_matrix, expected_disc = exact_fixture(
            frac(row["a0"]), frac(row["a1"]), frac(row["tau1"]),
            frac(row["a2"]), frac(row["tau2"]),
        )
        serialized_matrix = [
            [frac(value) for value in line]
            for line in row["raised_profile_normalized_endomorphism"]
        ]
        fixtures_ok &= (
            serialized_matrix == expected_matrix
            and frac(row["characteristic_discriminant"]) == expected_disc
            and expected_disc < 0
            and row["discriminant_is_negative"] is True
        )

    predecessor_strong = sp.sympify(
        load(SIX)["correlated_boundary"]["rows"][0]["strong_order"],
        locals=local,
    )
    scalar_contraction = sp.factor(
        covariant[0, 0] + 2 * covariant[0, 1] + covariant[1, 1]
    )
    serialized_raised = [
        [sp.factor(sp.sympify(value, locals=local)) for value in line]
        for line in species["raised_profile_normalized_endomorphism"]
    ]
    serialized_disc = sp.factor(
        sp.sympify(species["characteristic_discriminant"], locals=local)
    )
    serialized_u = sp.factor(sp.sympify(factorization["u"], locals=local))
    serialized_v = sp.factor(sp.sympify(factorization["v"], locals=local))
    z = sp.symbols("z")
    serialized_characteristic = sp.factor(
        sp.sympify(species["characteristic_polynomial"], locals={**local, "z": z})
    )

    checks = {
        "schema": not errors,
        "identity_tags_lifecycle": certificate.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
        and certificate.get("lifecycle_state") == "CLASSIFIED",
        "explicit_220_tree_component_fixtures": explicit_ok
        and tree_counts == {220},
        "finite_e_to_strong_component_limit": finite_to_strong,
        "singleton_and_pair_profile_symmetry": singleton_symmetry
        and pair_symmetry,
        "outer_profile_matrix_invertible": sp.factor(matrix.det())
        == -3 * a2**2 / (8 * tau2**2),
        "unique_factorization_coefficients": sp.simplify(u - twice_q) == 0
        and sp.simplify(v - a2 / 2) == 0,
        "serialized_factorization_coefficients": sp.simplify(
            serialized_u - u
        ) == 0
        and sp.simplify(serialized_v - v) == 0,
        "linear_coefficient_not_five_point_inner_L": sp.simplify(
            v - twice_l
        ) != 0
        and sp.diff(v, a2) == sp.Rational(1, 2),
        "independent_complement_pairing": sp.factor(
            B00 * B11 - B01**2
        ) == -81 * a2**4 / (64 * tau2**4),
        "serialized_raised_matrix": all(
            sp.simplify(serialized_raised[i][j] - raised[i, j]) == 0
            for i in range(2)
            for j in range(2)
        ),
        "nonzero_offdiagonal_species_interference": raised[0, 1] != 0
        and raised[1, 0] != 0,
        "negative_characteristic_discriminant_identity": sp.simplify(
            discriminant - expected_discriminant
        ) == 0
        and sp.simplify(serialized_disc - discriminant) == 0,
        "serialized_characteristic_polynomial": sp.simplify(
            serialized_characteristic - raised.charpoly(z).as_expr()
        ) == 0,
        "exact_negative_discriminant_fixtures": fixtures_ok,
        "scalar_contraction_matches_predecessor": sp.simplify(
            scalar_contraction - 6 * F1 * F2
        ) == 0
        and sp.simplify(6 * F1 * F2 - predecessor_strong) == 0,
        "scalar_history_weight_retained": frac(
            components["scalar_selected_history_relative_to_Born"]
        ) == Fraction(5, 3072),
        "claim_boundary": disposition.get(
            "amplitude_affiliation_above_first_jump"
        ) == "REFUTED_FOR_IDENTITY_SPECIES_LIFT"
        and disposition.get("minimal_enlarged_profile_carrier")
        == "NOT_YET_CONSTRUCTED"
        and disposition.get("complete_BT_probability") == "NOT_CONSTRUCTED"
        and disposition.get("Eq19_all_orders") == "NOT_PROVED"
        and "anything LORENTZIAN-CAUSAL"
        in certificate.get("does_not_establish", []),
        "hashes": len(certificate.get("provenance", {}).get("inputs", []))
        == 4
        and all(
            row.get("sha256") == sha256(row.get("path", ""))
            for row in certificate.get("provenance", {}).get("inputs", [])
        ),
        "producer_checks": certificate.get("checks", {}).get("passed")
        == certificate.get("checks", {}).get("total")
        == 29
        and certificate.get("checks", {}).get("failures") == []
        and all(certificate.get("checks", {}).get("details", {}).values()),
    }
    for error in errors:
        print("schema", list(error.path), error.message)
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    checks = verify(load(args.verify))
    for name, ok in checks.items():
        print(("[OK ] " if ok else "[FAIL] ") + name)
    failures = [name for name, ok in checks.items() if not ok]
    print("checks %d/%d" % (len(checks) - len(failures), len(checks)))
    print("RESULT:", "PASS" if not failures else "FAIL")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
