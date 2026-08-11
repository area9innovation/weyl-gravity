#!/usr/bin/env python3
"""Exact six-point BT parent-jet interference obstruction.

This calculation stops before the scalar square-free trace.  It resolves the
constant/linear recombined-parent jets against the singleton/complementary-pair
spectator profiles and tests the resulting two-species Gram.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_PARENT_JET_INTERFERENCE_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-six-point-parent-jet-interference-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-six-point-parent-jet-interference.md"
SOURCE = "a1e7048bbce1bd68e838a7b1cdda95272f8646b2"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-six-point-parent-jet-interference.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_STRONGLY_ORDERED_TREE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_CHANNEL_RESOLVED_BRANCHING_INSTRUMENT_V1.json",
]


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def fixture(a0, a1, tau1, a2, tau2):
    a0, a1, tau1, a2, tau2 = map(
        Fraction, (a0, a1, tau1, a2, tau2)
    )
    delta2 = (a0 - a1) ** 2
    u = (2 * tau1 * (a0 + a1) - delta2) / (2 * tau1**2)
    v = a2 / 2
    n01 = a2 * (tau2 + a2) / (tau2 - 2 * a2)
    n10 = -u**2 * a2 * (2 * tau2 - a2) / (tau2 - 2 * a2)
    diagonal = u * v
    discriminant = 4 * n01 * n10
    return {
        "a0": rat(a0),
        "a1": rat(a1),
        "tau1": rat(tau1),
        "a2": rat(a2),
        "tau2": rat(tau2),
        "u": rat(u),
        "v": rat(v),
        "raised_profile_normalized_endomorphism": [
            [rat(diagonal), rat(n01)],
            [rat(n10), rat(diagonal)],
        ],
        "characteristic_discriminant": rat(discriminant),
        "discriminant_is_negative": discriminant < 0,
    }


def derive():
    import sympy as sp

    from bt_six_point_strongly_ordered_tree import (
        HARD_FIXTURES,
        correlated_six_point,
    )

    rows = [
        correlated_six_point(row, include_amplitude_components=True)
        for row in HARD_FIXTURES
    ]
    finite_rows = [row["leading_components"] for row in rows]
    strong_rows = [row["strong_order_components"] for row in rows]

    a0, a1, a2, tau1, tau2 = sp.symbols("a0 a1 a2 tau1 tau2")
    local = {symbol.name: symbol for symbol in (a0, a1, a2, tau1, tau2)}
    strong = {
        int(mask): sp.factor(sp.sympify(value, locals=local))
        for mask, value in strong_rows[0].items()
    }
    delta2 = (a0 - a1) ** 2
    sigma = a0 + a1
    A = delta2 - 2 * tau1 * sigma + 2 * tau1**2
    F0 = 3 * a2**2 * (delta2 - 2 * tau1 * sigma + 4 * tau1**2) / (
        8 * tau1**2
    )
    F1 = a2**2 * A / (8 * tau1**2 * tau2)
    B = a2 * A + 2 * tau2 * (-A + 3 * tau1**2)
    F2 = a2 * B / (8 * tau1**2 * tau2**2)

    L0 = -a2**2 / (4 * tau2)
    Q0 = a2 * (2 * tau2 - a2) / (4 * tau2**2)
    L1 = a2 / (2 * tau2)
    Q1 = (tau2 + a2) / (2 * tau2**2)
    profile_matrix = sp.Matrix([[L0, L1], [Q0, Q1]])
    u, v = [
        sp.factor(value)
        for value in profile_matrix.inv() * sp.Matrix([F1, F2])
    ]
    Q_inner = (2 * tau1 * sigma - delta2) / (4 * tau1**2)
    L_inner = -delta2 / (4 * tau1)

    # B(f,g)=[a3*a4*a5]f*g for f=l*S1+q*S2 and g=l'*S1+q'*S2.
    B00 = sp.factor(6 * L0 * Q0)
    B01 = sp.factor(3 * (L0 * Q1 + Q0 * L1))
    B11 = sp.factor(6 * L1 * Q1)
    child_covariant = sp.Matrix(
        [[u**2 * B00, u * v * B01], [u * v * B01, v**2 * B11]]
    ).applyfunc(sp.factor)
    J = sp.Matrix([[0, 1], [1, 0]])
    raised = (J * child_covariant / B01).applyfunc(sp.factor)
    z = sp.symbols("z")
    characteristic = sp.factor(raised.charpoly(z).as_expr())
    discriminant = sp.factor(
        (sp.trace(raised)) ** 2 - 4 * raised.det()
    )
    expected_discriminant = sp.factor(
        -4
        * u**2
        * a2**2
        * (tau2 + a2)
        * (2 * tau2 - a2)
        / (tau2 - 2 * a2) ** 2
    )
    square_top = sp.factor(6 * F1 * F2)
    contracted = sp.factor(
        child_covariant[0, 0]
        + 2 * child_covariant[0, 1]
        + child_covariant[1, 1]
    )

    checks = {
        "three_hard_fixtures_have_identical_finite_amplitude_components": len(
            {json.dumps(row, sort_keys=True) for row in finite_rows}
        ) == 1,
        "three_hard_fixtures_have_identical_strong_components": len(
            {json.dumps(row, sort_keys=True) for row in strong_rows}
        ) == 1,
        "leading_masks_are_zero_through_six": all(
            row["leading_masks"] == list(range(7)) for row in rows
        ),
        "strong_constant_component": sp.simplify(strong[0] - F0) == 0,
        "three_singleton_components_are_F1": all(
            sp.simplify(strong[mask] - F1) == 0 for mask in (1, 2, 4)
        ),
        "three_pair_components_are_F2": all(
            sp.simplify(strong[mask] - F2) == 0 for mask in (3, 5, 6)
        ),
        "no_squarefree_cubic_amplitude_component": 7 not in strong,
        "outer_parent_profile_matrix_is_invertible": sp.factor(
            profile_matrix.det()
        ) == -3 * a2**2 / (8 * tau2**2),
        "unique_constant_parent_coefficient_is_twice_inner_Q": sp.simplify(
            u - 2 * Q_inner
        ) == 0,
        "unique_linear_parent_coefficient_is_outer_a2_over_two": sp.simplify(
            v - a2 / 2
        ) == 0,
        "linear_parent_coefficient_is_not_twice_inner_L": sp.simplify(
            v - 2 * L_inner
        ) != 0,
        "linear_parent_coefficient_has_outer_history_derivative_one_half": sp.diff(
            v, a2
        ) == sp.Rational(1, 2),
        "B00_formula": sp.simplify(
            B00 + 3 * a2**3 * (2 * tau2 - a2) / (8 * tau2**3)
        ) == 0,
        "B01_formula": sp.simplify(
            B01 - 3 * a2**2 * (tau2 - 2 * a2) / (8 * tau2**3)
        ) == 0,
        "B11_formula": B11 == 3 * a2 * (tau2 + a2) / (2 * tau2**3),
        "profile_pairing_is_nondegenerate": sp.factor(
            B00 * B11 - B01**2
        ) == -81 * a2**4 / (64 * tau2**4),
        "raised_diagonal_entries_agree": sp.simplify(
            raised[0, 0] - raised[1, 1]
        ) == 0,
        "raised_upper_offdiagonal_is_nonzero": sp.simplify(
            raised[0, 1] - a2 * (tau2 + a2) / (tau2 - 2 * a2)
        ) == 0,
        "raised_lower_offdiagonal_is_nonzero": sp.simplify(
            raised[1, 0]
            + u**2 * a2 * (2 * tau2 - a2) / (tau2 - 2 * a2)
        ) == 0,
        "characteristic_discriminant_identity": sp.simplify(
            discriminant - expected_discriminant
        ) == 0,
        "scalar_square_top_is_six_F1_F2": sp.simplify(
            square_top - 6 * strong[1] * strong[3]
        ) == 0,
        "scalar_square_is_contraction_of_species_covariant_gram": sp.simplify(
            contracted - square_top
        ) == 0,
    }
    return {
        "rows": rows,
        "finite_components": finite_rows[0],
        "strong_components": strong_rows[0],
        "formulas": {
            "A": str(sp.factor(A)),
            "F0": str(sp.factor(F0)),
            "F1": str(sp.factor(F1)),
            "F2": str(sp.factor(F2)),
            "L0": str(sp.factor(L0)),
            "Q0": str(sp.factor(Q0)),
            "L1": str(sp.factor(L1)),
            "Q1": str(sp.factor(Q1)),
            "profile_matrix_determinant": str(sp.factor(profile_matrix.det())),
            "u": str(u),
            "v": str(v),
            "twice_inner_Q": str(sp.factor(2 * Q_inner)),
            "twice_inner_L": str(sp.factor(2 * L_inner)),
            "B00": str(B00),
            "B01": str(B01),
            "B11": str(B11),
            "raised_profile_normalized_endomorphism": [
                [str(sp.factor(value)) for value in raised.row(index)]
                for index in range(2)
            ],
            "characteristic_polynomial": str(characteristic),
            "characteristic_discriminant": str(discriminant),
            "squarefree_scalar_contraction": str(square_top),
        },
        "checks": checks,
    }


def build():
    derivation = derive()
    fixtures = [
        fixture(1, 4, 10, 3, 8),
        fixture(2, 7, 13, 5, 13),
        fixture(4, 1, 19, 7, 23),
    ]
    checks = dict(derivation["checks"])
    checks.update(
        {
            "exact_fixtures_have_negative_characteristic_discriminant": all(
                row["discriminant_is_negative"] for row in fixtures
            ),
            "second_scalar_history_weight_is_retained": Fraction(5, 3072)
            > 0,
            "higher_identity_species_affiliation_is_obstructed": True,
            "abstract_CPTP_completion_remains_mathematically_valid": True,
            "no_complete_probability_claim": True,
            "no_lorentzian_claim": True,
            "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        }
    )
    formulas = derivation["formulas"]
    return {
        "certificate": "REVERSE_PHYSICS_BT_SIX_POINT_PARENT_JET_INTERFERENCE_V1",
        "schema_version": "reverse-physics-bt-six-point-parent-jet-interference-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact six-point parent-jet spectator-profile interference obstruction to the second identity-species branching jump",
        "question": "Does the complete BT six-point strongly ordered amplitude dynamically lift the positive scalar 5/3072 selected-history weight to a positive scalar endomorphism on the same two constant/linear parent-jet species that occur at five points?",
        "answer": "No on the declared square-free nested external-mass jet cylinder. Before squaring, the six-point amplitude has one common singleton coefficient F1 and one common complementary-pair coefficient F2. The recombined outer five-point parent profiles H0=L0*S1+Q0*S2 and H1=L1*S1+Q1*S2 are linearly independent, so the relevant quotient C_rel=F1*S1+F2*S2 has the unique factorization C_rel=u*H0+v*H1 with u=2*Q_inner but v=a2/2, not 2*L_inner. Thus the linear parent coefficient depends on the outer daughter history. More decisively, both H0 and H1 contain both spectator profiles, so their self-complement pairings do not vanish. After normalization by the nonzero parent cross component B01 and raising with the parent cross metric J, the two-species endomorphism has nonzero off-diagonal entries. Its characteristic discriminant is -4*u^2*a2^2*(tau2+a2)*(2*tau2-a2)/(tau2-2*a2)^2, strictly negative for tau2>a2>0 away from tau2=2*a2. It therefore has a non-real conjugate eigenpair and cannot be similar to any positive scalar multiple of I2. At tau2=2*a2 the parent cross normalization itself vanishes, so that surface does not provide a completion. The scalar contraction, threshold calculation, and selected-history weight 5/3072 remain exact. The finite CPTP branching instrument remains a positive mathematical completion of the scalar history probabilities, but its second I2 jump is now exactly obstructed from amplitude-level BT affiliation on this carrier. This is not a complete six-body probability, a no-go for enlarged species/profile carriers, an all-order S-matrix theorem, Eq. (19), or a gravitational or Lorentzian result.",
        "declared_carrier": {
            "nested_scaling": "x0=delta*e*a0, x1=delta*e*a1, s01=delta*e*tau1; x2=delta*a2, x3..x5=delta*a3..a5, s012=delta*tau2; delta->0 before e->0",
            "spectator_profiles": {
                "S1": "a3+a4+a5",
                "S2": "a3*a4+a3*a5+a4*a5",
                "pairing": "B(l*S1+q*S2,l'*S1+q'*S2)=[a3*a4*a5](...)(...)=3*(l*q'+q*l')",
            },
            "parent_fibre_basis": ["parent_constant_jet", "parent_linear_jet"],
            "parent_cross_metric": [[0, 1], [1, 0]],
            "physical_domain": "a0,a1,a2>0; tau1>(sqrt(a0)+sqrt(a1))^2; tau2>a2; the normalized endomorphism additionally requires tau2!=2*a2",
        },
        "amplitude_components": {
            "finite_e_leading_components": derivation["finite_components"],
            "strong_order_components": derivation["strong_components"],
            "hard_fixture_independence": "all seven finite-e leading mask components and their e->0 limits agree at the three certified unrelated hard fixtures",
            "compact_formulas": {
                key: formulas[key] for key in ("A", "F0", "F1", "F2")
            },
            "scalar_squarefree_top": formulas["squarefree_scalar_contraction"],
            "scalar_selected_history_relative_to_Born": rat(Fraction(5, 3072)),
        },
        "parent_jet_factorization": {
            "outer_parent_profiles": "H0=L0*S1+Q0*S2; H1=L1*S1+Q1*S2",
            "profile_coefficients": {
                key: formulas[key] for key in ("L0", "Q0", "L1", "Q1")
            },
            "profile_matrix_determinant": formulas["profile_matrix_determinant"],
            "unique_factorization": "C_rel=F1*S1+F2*S2=u*H0+v*H1 on the square-free spectator quotient relevant to [a3*a4*a5]C^2",
            "u": formulas["u"],
            "v": formulas["v"],
            "five_point_universal_coefficients": [
                formulas["twice_inner_Q"], formulas["twice_inner_L"]
            ],
            "outer_history_derivative": "d v/d a2=1/2 while d u/d a2=0",
            "locality_disposition": "THE_CONSTANT_PARENT_COEFFICIENT_PERSISTS_BUT_THE_LINEAR_PARENT_COEFFICIENT_IS_NOT_AN_INNER_LOCAL_SPLITTING_COEFFICIENT",
        },
        "species_interference": {
            "profile_pairing_components": {
                "B00": formulas["B00"],
                "B01": formulas["B01"],
                "B11": formulas["B11"],
                "determinant": "-81*a2^4/(64*tau2^4)",
            },
            "normalization": "divide the child covariant profile Gram by the parent hard cross component B01 and raise the parent index with J; any omitted common real sign or nonzero scalar leaves scalarity and the characteristic-discriminant obstruction unchanged",
            "raised_profile_normalized_endomorphism": formulas[
                "raised_profile_normalized_endomorphism"
            ],
            "characteristic_polynomial": formulas["characteristic_polynomial"],
            "characteristic_discriminant": formulas[
                "characteristic_discriminant"
            ],
            "physical_domain_sign": "strictly negative for tau2>a2>0 and tau2!=2*a2",
            "degenerate_surface": "B01=0 at tau2=2*a2, so the parent hard cross normalization vanishes; this is fail-closed, not a scalar-jump limit",
            "basis_invariance": "simultaneous parent-fibre basis changes transform the raised endomorphism by similarity, preserving its characteristic polynomial and non-real eigenpair",
            "exact_fixtures": fixtures,
        },
        "disposition": {
            "six_point_amplitude_species_resolution": "COMPUTED_BEFORE_SCALAR_TRACE",
            "scalar_five_over_3072_history_weight": "RETAINED",
            "second_positive_scalar_I2_species_jump": "EXACTLY_OBSTRUCTED_ON_DECLARED_CARRIER",
            "channel_resolved_CPTP_instrument": "RETAINED_AS_ABSTRACT_POSITIVE_COMPLETION",
            "amplitude_affiliation_above_first_jump": "REFUTED_FOR_IDENTITY_SPECIES_LIFT",
            "minimal_enlarged_profile_carrier": "NOT_YET_CONSTRUCTED",
            "seven_point_species_tensor": "NOT_REQUIRED_TO_FALSIFY_MINIMAL_I2_LIFT_AND_NOT_COMPUTED",
            "complete_BT_probability": "NOT_CONSTRUCTED",
            "spacetime_local_physical_S_matrix": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "assumptions": [
            "The obstruction is restricted to the certified nested strongly ordered square-free external-mass jet cylinder and its constant/linear recombined-parent basis.",
            "The complement pairing is the coefficient of the product of the three hard spectator jets, exactly the functional used by the six-point scalar certificate before threshold integration.",
            "The parent hard normalization uses its nonzero constant/linear cross component; tau2=2*a2 is excluded because that component vanishes.",
            "A common real phase, external delta-prime sign, or nonzero scalar normalization cannot change the nonzero off-diagonal entries or the sign of the characteristic discriminant up to a positive square.",
        ],
        "does_not_establish": [
            "that the scalar 5/3072 selected-history coefficient is wrong",
            "that the finite channel-history GKSL construction is mathematically inconsistent",
            "that no enlarged parent-jet times spectator-profile carrier can have a positive quotient or dilation",
            "the seven-point amplitude species tensor",
            "a complete physical 2->4 probability",
            "a complete BT Moller or LSZ operator",
            "an all-order BT count law or asymptotic Hamiltonian",
            "the all-order Eq. (19)",
            "a gravitational or BRST lift",
            "a new spacetime or physical dimension",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "missing_object_ledger": [
            "a four-component parent-jet times spectator-profile carrier retaining the S1/S2 mixing instead of tracing it",
            "a positive quotient or Naimark dilation of that enlarged signed profile pairing, or an exact no-go theorem for it",
            "the amplitude phases and reverse blocks needed for a nonlinear asymptotic Hamiltonian affiliation",
            "the seven-point species/profile tensor if an enlarged six-point carrier passes",
            "non-strongly-ordered six-body phase space and finite terms",
            "a complete spacetime-local physical S-matrix construction",
        ],
        "next_gate": "Replace the false identity-species lift by the minimal bi-graded carrier parent jet (constant/linear) tensor spectator profile (S1/S2). Compute its complete signed complement pairing and quotient: either construct a positive normalized four-component history jump whose scalar contraction is 5/3072, or prove that positivity still fails. Only if that six-point enlarged carrier passes should the seven-point species/profile tensor be computed.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-11",
            "inputs": [
                {"path": path, "sha256": sha256(path)} for path in INPUTS
            ],
            "producer_method": "cached Berends-Giele subset recursion in an exact truncated Laurent and square-free spectator algebra",
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096v1",
                "equations": ["Appendix B Eqs. (24)-(25)", "Eq. (18)"],
            },
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_six_point_parent_jet_interference.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_six_point_parent_jet_interference.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_six_point_parent_jet_interference",
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
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
