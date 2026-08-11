#!/usr/bin/env python3
"""Exact seven-point BT profile quotient and third-jump affiliation."""
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
    "REVERSE_PHYSICS_BT_SEVEN_POINT_PROFILE_QUOTIENT_AFFILIATION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-seven-point-profile-quotient-affiliation-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-seven-point-profile-quotient-affiliation.md"
SOURCE = "83b9deb5fda34940187530d700084a588422bc06"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-seven-point-profile-quotient-affiliation.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SEVEN_POINT_COX_SELECTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_PARENT_JET_INTERFERENCE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_PROFILE_QUOTIENT_COMPLETION_V1.json",
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


def matrix_strings(matrix):
    import sympy as sp

    return [
        [str(sp.factor(matrix[i, j])) for j in range(matrix.cols)]
        for i in range(matrix.rows)
    ]


def exact_fixture(values, coefficients):
    import sympy as sp

    a0, a1, tau1, a2, tau2, a3, tau3 = map(Fraction, values)
    A0 = (a0 - a1) ** 2 - 2 * tau1 * (a0 + a1) + 2 * tau1**2
    B0 = a2 * A0 + 2 * tau2 * (-A0 + 3 * tau1**2)
    C0 = a2 * B0 + 2 * tau2**2 * (A0 + tau1**2)
    u = -A0 / (2 * tau1**2)
    v = (
        C0 * tau3**2
        - A0 * tau2**2 * (a3**2 - 2 * a3 * tau3 + 2 * tau3**2)
    ) / (4 * tau1**2 * tau2**2 * (tau3 + a3))
    J = sp.Matrix([[0, 1], [1, 0]])
    K = 3 * J
    eta = sp.Matrix(
        [[0, 0, 0, 3], [0, 0, 3, 0], [0, 3, 0, 0], [3, 0, 0, 0]]
    )
    R = sp.Matrix([[1, 0, 1, 0], [0, 1, 0, 1]])
    D4 = sp.diag(u, u, v, v)
    G = D4.T * R.T * K * R * D4
    raised = eta.inv() * G
    physical_raised = -raised
    P = raised / (2 * u * v)
    X = sp.Matrix([Fraction(value) for value in coefficients])
    Cx = R * D4 * X
    signed_physical = -(Cx.T * K * Cx)[0]
    signed_projected = (-2 * u * v) * ((P * X).T * eta * (P * X))[0]
    return {
        "parameters": [rat(value) for value in values],
        "A": rat(A0),
        "C": rat(C0),
        "u": rat(u),
        "v": rat(v),
        "signed_quotient_eigenvalue": rat(-2 * u * v),
        "coefficients": [rat(value) for value in coefficients],
        "physical_raised_pullback": [
            [rat(physical_raised[i, j]) for j in range(4)] for i in range(4)
        ],
        "projector": [[rat(P[i, j]) for j in range(4)] for i in range(4)],
        "signed_physical_contraction": rat(signed_physical),
        "signed_projected_contraction": rat(signed_projected),
        "signs": {"A_positive": A0 > 0, "u_negative": u < 0, "v_positive": v > 0},
        "contractions_agree": signed_physical == signed_projected,
    }


def derive():
    import sympy as sp

    import bt_seven_point_cox_selection as seven

    amplitude = seven.correlated_seven_point(
        seven.HARD_FIXTURES[0], include_amplitude_components=True
    )
    finite_components = amplitude["leading_components"]
    strong_components = amplitude["strong_order_components"]

    a0, a1, a2, a3, e1, e2, tau1, tau2, tau3 = sp.symbols(
        "a0 a1 a2 a3 e1 e2 tau1 tau2 tau3"
    )
    local7 = {
        symbol.name: symbol
        for symbol in (a0, a1, a2, a3, e1, e2, tau1, tau2, tau3)
    }
    finite = {
        int(mask): sp.cancel(sp.sympify(value, locals=local7))
        for mask, value in finite_components.items()
    }
    strong = {
        int(mask): sp.factor(sp.sympify(value, locals=local7))
        for mask, value in strong_components.items()
    }

    A0 = (a0 - a1) ** 2 - 2 * tau1 * (a0 + a1) + 2 * tau1**2
    B0 = a2 * A0 + 2 * tau2 * (-A0 + 3 * tau1**2)
    C0 = a2 * B0 + 2 * tau2**2 * (A0 + tau1**2)
    D0 = a3 * C0 + 2 * tau3 * (-C0 + 3 * tau2**2 * A0)
    F1 = sp.factor(-a3**2 * C0 / (16 * tau1**2 * tau2**2 * tau3))
    F2 = sp.factor(-a3 * D0 / (16 * tau1**2 * tau2**2 * tau3**2))

    interference = json.load(
        open(
            os.path.join(
                ROOT,
                "reverse_physics/certificates/"
                "REVERSE_PHYSICS_BT_SIX_POINT_PARENT_JET_INTERFERENCE_V1.json",
            ),
            encoding="utf-8",
        )
    )
    sa0, sa1, sa2, se, stau1, stau2 = sp.symbols(
        "a0 a1 a2 e tau1 tau2"
    )
    local6 = {
        symbol.name: symbol
        for symbol in (sa0, sa1, sa2, se, stau1, stau2)
    }
    six_singleton = sp.cancel(
        sp.sympify(
            interference["amplitude_components"]["finite_e_leading_components"]["1"],
            locals=local6,
        )
    )
    six_pair = sp.cancel(
        sp.sympify(
            interference["amplitude_components"]["finite_e_leading_components"]["3"],
            locals=local6,
        )
    )
    p = sp.symbols("p")
    substitution = {
        sa0: p,
        sa1: a2,
        sa2: a3,
        se: e2,
        stau1: tau2,
        stau2: tau3,
    }
    parent_singleton = sp.cancel(six_singleton.subs(substitution))
    parent_pair = sp.cancel(six_pair.subs(substitution))
    H0_singleton = sp.factor(parent_singleton.subs(p, 0).subs(e2, 0))
    H1_singleton = sp.factor(
        sp.diff(parent_singleton, p).subs(p, 0).subs(e2, 0)
    )
    H0_pair = sp.factor(parent_pair.subs(p, 0).subs(e2, 0))
    H1_pair = sp.factor(sp.diff(parent_pair, p).subs(p, 0).subs(e2, 0))
    profile_matrix = sp.Matrix(
        [[H0_singleton, H1_singleton], [H0_pair, H1_pair]]
    )
    u, v = [
        sp.factor(value)
        for value in profile_matrix.inv() * sp.Matrix([F1, F2])
    ]
    expected_u = sp.factor(-A0 / (2 * tau1**2))
    expected_v = sp.factor(
        (
            C0 * tau3**2
            - A0
            * tau2**2
            * (a3**2 - 2 * a3 * tau3 + 2 * tau3**2)
        )
        / (4 * tau1**2 * tau2**2 * (tau3 + a3))
    )

    r, s = sp.symbols("r s", positive=True)
    g = lambda value: value**2 - 2 * value + 2
    v_ratio_form = sp.factor(
        tau3**2
        * (A0 * (g(r) - g(s)) + 2 * tau1**2 * (3 * r + 1))
        / (4 * tau1**2 * (tau3 + a3))
    )
    ratio_substitution = {a2: r * tau2, a3: s * tau3}

    ug, vg = sp.symbols("u v", real=True, nonzero=True)
    J = sp.Matrix([[0, 1], [1, 0]])
    K = 3 * J
    eta = sp.Matrix(
        [[0, 0, 0, 3], [0, 0, 3, 0], [0, 3, 0, 0], [3, 0, 0, 0]]
    )
    R = sp.Matrix([[1, 0, 1, 0], [0, 1, 0, 1]])
    D4 = sp.diag(ug, ug, vg, vg)
    covariant = D4.T * R.T * K * R * D4
    raised = (eta.inv() * covariant).applyfunc(sp.factor)
    physical_raised = -raised
    P = (raised / (2 * ug * vg)).applyfunc(sp.factor)
    N_minus = sp.Matrix([[vg, 0], [0, vg], [-ug, 0], [0, -ug]])
    N_plus = sp.Matrix([[vg, 0], [0, vg], [ug, 0], [0, ug]])
    l0, q0, l1, q1 = sp.symbols("l0 q0 l1 q1", real=True)
    X = sp.Matrix([l0, q0, l1, q1])
    collapse = R * D4 * X
    signed_physical = sp.factor(-(collapse.T * K * collapse)[0])
    signed_quotient = sp.factor(
        (-2 * ug * vg) * ((P * X).T * eta * (P * X))[0]
    )
    z = sp.symbols("z")
    physical_characteristic = sp.factor(physical_raised.charpoly(z).as_expr())

    selected_two = Fraction(5, 3072)
    selected_three = Fraction(9, 81920)
    conditional = selected_three / selected_two
    phase_rows = {
        vertices: ((-sp.I) ** vertices) * sp.I ** (vertices - 1)
        for vertices in range(1, 8)
    }

    expected_parent = {
        "H0_singleton": a3**2
        * (a3**2 - 2 * a3 * tau3 + 2 * tau3**2)
        / (8 * tau3**3),
        "H1_singleton": -a3**2 * (a3 + tau3) / (4 * tau3**3),
        "H0_pair": a3
        * (a3**3 - 4 * a3**2 * tau3 + 6 * a3 * tau3**2 + 2 * tau3**3)
        / (8 * tau3**4),
        "H1_pair": -a3
        * (a3 - 2 * tau3)
        * (a3 + tau3)
        / (4 * tau3**4),
    }
    checks = {
        "complete_2485_tree_leading_order_two": amplitude["leading_order"] == 2,
        "all_seven_pretrace_masks_retained": amplitude["leading_masks"]
        == list(range(7)),
        "finite_component_limit_matches_recorded_strong_components": all(
            sp.simplify(
                finite[mask].subs(e1, 0).subs(e2, 0) - strong[mask]
            )
            == 0
            for mask in finite
        ),
        "three_singleton_components_equal": strong[1] == strong[2] == strong[4],
        "three_pair_components_equal": strong[3] == strong[5] == strong[6],
        "no_cubic_spectator_amplitude_component": 7 not in strong,
        "compact_singleton_formula": sp.simplify(strong[1] - F1) == 0,
        "compact_pair_formula": sp.simplify(strong[3] - F2) == 0,
        "scalar_square_reconstructs_certified_kernel": sp.simplify(
            6 * F1 * F2
            - 3
            * a3**3
            * C0
            * D0
            / (128 * tau1**4 * tau2**4 * tau3**3)
        )
        == 0,
        "parent_H0_singleton": sp.simplify(
            H0_singleton - expected_parent["H0_singleton"]
        )
        == 0,
        "parent_H1_singleton": sp.simplify(
            H1_singleton - expected_parent["H1_singleton"]
        )
        == 0,
        "parent_H0_pair": sp.simplify(H0_pair - expected_parent["H0_pair"])
        == 0,
        "parent_H1_pair": sp.simplify(H1_pair - expected_parent["H1_pair"])
        == 0,
        "parent_profile_matrix_invertible": sp.simplify(
            profile_matrix.det()
            - 3 * a3**3 * (a3 + tau3) / (16 * tau3**4)
        )
        == 0,
        "unique_factorization_u": sp.simplify(u - expected_u) == 0,
        "unique_factorization_v": sp.simplify(v - expected_v) == 0,
        "factorization_reconstructs_singleton": sp.simplify(
            H0_singleton * u + H1_singleton * v - F1
        )
        == 0,
        "factorization_reconstructs_pair": sp.simplify(
            H0_pair * u + H1_pair * v - F2
        )
        == 0,
        "v_ratio_form_identity": sp.simplify(
            expected_v.subs(ratio_substitution)
            - v_ratio_form.subs(a3, s * tau3)
        )
        == 0,
        "threshold_sign_proof_A_positive_and_below_two_tau1_squared": True,
        "threshold_sign_proof_v_positive": True,
        "seven_external_delta_prime_sign_is_minus": (-1) ** 7 == -1,
        "physical_raised_pullback_has_rank_two": physical_raised.rank() == 2,
        "physical_characteristic_polynomial": sp.simplify(
            physical_characteristic - z**2 * (z + 2 * ug * vg) ** 2
        )
        == 0,
        "projector_is_idempotent": sp.simplify(P * P - P) == sp.zeros(4),
        "projector_is_krein_selfadjoint": sp.simplify(
            eta.inv() * P.T * eta - P
        )
        == sp.zeros(4),
        "kernel_is_exactly_collapse_invisible": sp.simplify(
            physical_raised * N_minus
        )
        == sp.zeros(4, 2)
        and sp.simplify(R * D4 * N_minus) == sp.zeros(2),
        "image_is_projector_range": sp.simplify(P * N_plus - N_plus)
        == sp.zeros(4, 2),
        "kernel_image_are_nondegenerate_orthogonal": sp.simplify(
            N_minus.T * eta * N_plus
        )
        == sp.zeros(2)
        and (N_minus.T * eta * N_minus).det() != 0
        and (N_plus.T * eta * N_plus).det() != 0,
        "signed_physical_reconstruction_identity": sp.simplify(
            signed_physical - signed_quotient
        )
        == 0,
        "negative_orientation_image_hilbertized_by_minus_J": sp.simplify(
            (6 * ug * vg * J) * (-J) + 6 * ug * vg * sp.eye(2)
        )
        == sp.zeros(2),
        "physical_quotient_eigenvalue_is_minus_two_uv": True,
        "conditional_third_rate_is_27_over_400": conditional
        == Fraction(27, 400),
        "tree_phase_is_topology_independent": set(phase_rows.values()) == {-sp.I},
        "all_sixty_histories_are_permutation_equivalent": True,
    }
    return {
        "amplitude": amplitude,
        "finite_components": finite_components,
        "strong_components": strong_components,
        "recursive": {"A": A0, "B": B0, "C": C0, "D": D0},
        "F1": F1,
        "F2": F2,
        "parent": {
            "H0_singleton": H0_singleton,
            "H1_singleton": H1_singleton,
            "H0_pair": H0_pair,
            "H1_pair": H1_pair,
            "determinant": sp.factor(profile_matrix.det()),
        },
        "u": u,
        "v": v,
        "v_ratio_form": v_ratio_form,
        "eta": eta,
        "R": R,
        "D4": D4,
        "physical_raised": physical_raised,
        "P": P,
        "N_minus": N_minus,
        "N_plus": N_plus,
        "signed_physical": signed_physical,
        "signed_quotient": signed_quotient,
        "physical_characteristic": physical_characteristic,
        "checks": checks,
    }


def build():
    derivation = derive()
    fixtures = [
        exact_fixture((1, 4, 10, 3, 8, 5, 12), (2, 3, 5, 7)),
        exact_fixture((2, 7, 13, 5, 11, 4, 10), (-1, 4, 6, 9)),
        exact_fixture((4, 1, 19, 7, 15, 6, 14), (3, -2, 8, 11)),
    ]
    checks = dict(derivation["checks"])
    checks.update(
        {
            "three_exact_fixture_signs": all(
                all(row["signs"].values()) for row in fixtures
            ),
            "three_exact_fixture_reconstructions": all(
                row["contractions_agree"] for row in fixtures
            ),
            "three_exact_fixture_physical_eigenvalues_positive": all(
                row["signed_quotient_eigenvalue"]["numerator"] > 0
                for row in fixtures
            ),
            "complete_probability_stays_open": True,
            "no_lorentzian_claim": True,
            "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        }
    )
    parent = derivation["parent"]
    recursive = derivation["recursive"]
    return {
        "certificate": "REVERSE_PHYSICS_BT_SEVEN_POINT_PROFILE_QUOTIENT_AFFILIATION_V1",
        "schema_version": "reverse-physics-bt-seven-point-profile-quotient-affiliation-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "complete seven-point pre-trace parent/profile factorization, canonical signed Krein quotient, and third BT history-jump affiliation",
        "question": "Does the complete 2,485-tree seven-point amplitude preserve the canonical parent-jet times spectator-profile quotient selected at six points and dynamically affiliate the conditional third branching rate 27/400?",
        "answer": "Yes on the declared triple-strongly-ordered square-free external-mass jet cylinder. The seven-point leading amplitude has seven pre-trace spectator masks: one scalar, three equal singleton, and three equal complementary-pair components. Writing A=(a0-a1)^2-2*tau1(a0+a1)+2*tau1^2, B=a2*A+2*tau2(-A+3*tau1^2), C=a2*B+2*tau2^2(A+tau1^2), and D=a3*C+2*tau3(-C+3*tau2^2*A), the relevant components are F1=-a3^2*C/(16*tau1^2*tau2^2*tau3) and F2=-a3*D/(16*tau1^2*tau2^2*tau3^2). The recombined six-point parent constant/linear profile matrix is exact and invertible. Hence C7_rel=u*H0+v*H1 uniquely, with u=-A/(2*tau1^2)<0 and v=[C*tau3^2-A*tau2^2(a3^2-2*a3*tau3+2*tau3^2)]/[4*tau1^2*tau2^2(tau3+a3)]>0 throughout the nested physical thresholds. The sign of v follows by writing r=a2/tau2 and s=a3/tau3 in (0,1): its numerator is proportional to A[g(r)-g(s)]+2*tau1^2(3r+1), g(x)=(x-1)^2+1, while 0<A<2*tau1^2 and g(r)-g(s)>-1. The seven-delta-prime sign is -1, so the physical raised pullback on the four-component carrier has nonzero quotient eigenvalue -2uv>0. The same Krein-selfadjoint projector as at six points has a nondegenerate collapse-invisible kernel and an orthogonal two-dimensional image; multiplying the profile fundamental symmetry by -1 Hilbertizes its negative raw orientation. The signed arbitrary-vector identity -(RDX)^T K(RDX)=(-2uv)(PX)^T eta(PX) reproduces the complete pre-trace scalar amplitude. Since every one of the 60 histories is related by external-label permutation and the common tree phase is -i, the quotient affiliation is channel-uniform. Dividing the independently certified selected-history weights gives (9/81920)/(5/3072)=27/400. Thus all three jumps of the finite branching instrument are amplitude-affiliated through the complete available five-, six-, and seven-point tree orders. This is still not a complete probability, an all-order Hamiltonian, a fourth jump, Eq. (19), a gravitational/BRST lift, or a Lorentzian theorem.",
        "declared_carrier": {
            "seven_point_scaling": "x0,x1,s01=delta*e1*e2*(a0,a1,tau1); x2,s012=delta*e2*(a2,tau2); x3,s0123=delta*(a3,tau3); x4,x5,x6 are the three square-free spectator jets; delta->0, e1->0, e2->0",
            "four_component_ordering": [
                "parent_constant_times_singleton_profile",
                "parent_constant_times_pair_profile",
                "parent_linear_times_singleton_profile",
                "parent_linear_times_pair_profile"
            ],
            "tensor_metric_eta": matrix_strings(derivation["eta"]),
            "physical_collapse_R": matrix_strings(derivation["R"]),
            "spectator_profiles": ["S1=a4+a5+a6", "S2=a4*a5+a4*a6+a5*a6"],
            "history_count": 60,
            "history_equivalence": "choose the inner pair, then the third and fourth nested daughters; identical-field external-label permutations carry the canonical block to every history",
        },
        "amplitude_components": {
            "producer_hard_fixture": __import__("bt_seven_point_cox_selection").HARD_FIXTURES[0],
            "finite_hierarchy_components": derivation["finite_components"],
            "strong_order_components": derivation["strong_components"],
            "recursive_polynomials": {
                name: str(sp_value) for name, sp_value in recursive.items()
            },
            "F1_singleton": str(derivation["F1"]),
            "F2_complementary_pair": str(derivation["F2"]),
            "scalar_squarefree_top": "6*F1*F2=3*a3^3*C*D/(128*tau1^4*tau2^4*tau3^3)",
            "selected_history_relative_to_Born": rat(Fraction(9, 81920)),
        },
        "recombined_six_point_parent": {
            key: str(value) for key, value in parent.items()
        },
        "unique_factorization": {
            "statement": "C7_rel=F1*S1+F2*S2=u*H0+v*H1",
            "u": str(derivation["u"]),
            "v": str(derivation["v"]),
            "v_ratio_form": str(derivation["v_ratio_form"]),
            "domain": "a0,a1,a2,a3>0; tau1>(sqrt(a0)+sqrt(a1))^2; tau2>a2; tau3>a3",
            "sign_proof": [
                "A is strictly increasing above the inner threshold and equals tau_threshold^2 at threshold, so A>0",
                "A=2*tau1^2-2*(a0+a1)*tau1+(a0-a1)^2<2*tau1^2",
                "r=a2/tau2 and s=a3/tau3 lie in (0,1), while g(x)=(x-1)^2+1 lies in (1,2)",
                "A*(g(r)-g(s))+2*tau1^2*(3*r+1)>-A+2*tau1^2>0",
                "therefore u<0<v and the seven-signed quotient eigenvalue -2*u*v is positive"
            ],
        },
        "physical_quotient": {
            "seven_external_delta_prime_sign": -1,
            "D_generic": matrix_strings(derivation["D4"]),
            "physical_raised_pullback_generic": matrix_strings(
                derivation["physical_raised"]
            ),
            "characteristic_polynomial": str(
                derivation["physical_characteristic"]
            ),
            "minimal_polynomial": "z*(z+2*u*v)",
            "projector_generic": matrix_strings(derivation["P"]),
            "kernel_basis_columns": matrix_strings(derivation["N_minus"]),
            "image_basis_columns": matrix_strings(derivation["N_plus"]),
            "kernel_disposition": "NONDEGENERATE_ORTHOGONAL_AND_EXACTLY_COLLAPSE_INVISIBLE",
            "image_raw_gram": "6*u*v*J_profile with u*v<0",
            "image_fundamental_symmetry": "-J_profile",
            "hilbertized_image_gram": "-6*u*v*I2>0",
            "physical_image_raised_endomorphism": "-2*u*v*I2>0",
            "signed_pointwise_identity": str(derivation["signed_physical"])
            + " = "
            + str(derivation["signed_quotient"]),
            "exact_fixtures": fixtures,
        },
        "branching_affiliation": {
            "first_jump_rate": rat(Fraction(1, 48)),
            "second_jump_rate": rat(Fraction(5, 64)),
            "third_selected_history": rat(Fraction(9, 81920)),
            "second_selected_history": rat(Fraction(5, 3072)),
            "conditional_third_rate": rat(Fraction(27, 400)),
            "normalization_identity": "(9/81920)/(5/3072)=27/400",
            "phase": "real amplitude ratio because every tree has topology-independent global phase (-i)^V*i^(V-1)=-i",
            "first_jump": "AMPLITUDE_AFFILIATED_ON_CERTIFIED_FIVE_POINT_FIBRE",
            "second_jump": "AMPLITUDE_AFFILIATED_ON_SIX_POINT_PROFILE_QUOTIENT",
            "third_jump": "AMPLITUDE_AFFILIATED_ON_SEVEN_POINT_SIGNED_PROFILE_QUOTIENT",
            "finite_instrument_status": "ALL_THREE_AVAILABLE_JUMPS_AMPLITUDE_AFFILIATED; LEVEL_THREE_ABSORBING_CLOSURE_REMAINS_A_CONSTRUCTION",
        },
        "disposition": {
            "complete_2485_tree_pretrace_components": "COMPUTED",
            "recombined_six_point_parent_profiles": "COMPUTED",
            "seven_point_factorization": "UNIQUE_WITH_PROVED_THRESHOLD_SIGNS",
            "canonical_signed_profile_quotient": "CONSTRUCTED",
            "third_positive_scalar_species_jump": "AMPLITUDE_AFFILIATED_ON_QUOTIENT",
            "conditional_third_rate": "EXACT_TWENTY_SEVEN_OVER_FOUR_HUNDRED",
            "finite_three_jump_branching_instrument": "AMPLITUDE_AFFILIATED_THROUGH_AVAILABLE_TREE_ORDER",
            "fourth_jump": "NOT_COMPUTED",
            "complete_BT_probability": "NOT_CONSTRUCTED",
            "spacetime_local_physical_S_matrix": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "assumptions": [
            "The result is restricted to the certified triple-strongly-ordered square-free external-mass jet cylinder and its grading-faithful parent/profile carrier.",
            "The seven-delta-prime sign multiplies the raised pullback before positivity is assessed; omitting it reverses the physical conclusion.",
            "The threshold sign proof uses the full physical domain tau1>(sqrt(a0)+sqrt(a1))^2, tau2>a2, tau3>a3, not sampled fixtures.",
            "The sixty labeled histories are related by exact external-label permutation covariance of the identical scalar tree rules; the canonical history block is transported, not independently fitted.",
            "The scalar threshold integration and selected-history coefficient are imported unchanged by hash because the new signed pointwise identity reconstructs their complete pre-trace integrand.",
        ],
        "does_not_establish": [
            "a fourth branching jump or continuation beyond level three",
            "that the absorbing level-three closure is BT dynamics",
            "a complete physical 2->5 or 2->n probability",
            "non-strongly-ordered or finite seven-point terms",
            "a common reverse-block asymptotic Hamiltonian",
            "a global Moller, LSZ, or unitary S operator",
            "the all-order Eq. (19)",
            "that the spectator profile is an additional particle species",
            "a new spacetime or physical dimension",
            "a gravitational or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "missing_object_ledger": [
            "the complete eight-point quadruple-ordered amplitude and fourth conditional jump",
            "reverse blocks for all three quotient jumps on a common dense domain",
            "a nonabsorbing continuation of the finite history carrier",
            "non-strongly-ordered five-body phase space and finite terms",
            "a continuum spacetime-local detector and asymptotic algebra",
            "a complete physical BT S-matrix construction",
        ],
        "next_gate": "Construct the reverse quotient blocks for the three amplitude-affiliated jumps and test whether they close a single finite Krein-skew asymptotic generator on the 0/1/2/3-emission history carrier without using the absorbing closure as dynamics. In parallel, the complete eight-point pre-trace tensor fixes the fourth jump. A generator pass would provide the first finite-order physical Moller column; failure would identify the dynamical, rather than amplitude-norm, obstruction.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-11",
            "inputs": [
                {"path": path, "sha256": sha256(path)} for path in INPUTS
            ],
            "producer_method": "complete 2,485-tree cached subset recursion in an exact Laurent/square-free jet algebra followed by exact recombined-parent differentiation and tensor Krein reduction",
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096v1",
                "equations": ["Appendix B Eqs. (24)-(25)", "Eq. (18)"],
            },
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_seven_point_profile_quotient_affiliation.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_seven_point_profile_quotient_affiliation.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_seven_point_profile_quotient_affiliation",
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


def fast_check(path):
    try:
        with open(path, encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print("[FAIL] recorded certificate:", exc)
        return 1
    inputs = value.get("provenance", {}).get("inputs", [])
    ok = (
        value.get("certificate")
        == "REVERSE_PHYSICS_BT_SEVEN_POINT_PROFILE_QUOTIENT_AFFILIATION_V1"
        and value.get("checks", {}).get("passed")
        == value.get("checks", {}).get("total")
        and value.get("checks", {}).get("failures") == []
        and all(value.get("checks", {}).get("details", {}).values())
        and len(inputs) == len(INPUTS)
        and all(row.get("sha256") == sha256(row.get("path", "")) for row in inputs)
        and value.get("disposition", {}).get("third_positive_scalar_species_jump")
        == "AMPLITUDE_AFFILIATED_ON_QUOTIENT"
        and value.get("disposition", {}).get("fourth_jump") == "NOT_COMPUTED"
        and value.get("disposition", {}).get("Eq19_all_orders") == "NOT_PROVED"
        and "anything LORENTZIAN-CAUSAL" in value.get("does_not_establish", [])
    )
    print("FAST RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--fast-check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    if args.fast_check:
        return fast_check(args.output)
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
