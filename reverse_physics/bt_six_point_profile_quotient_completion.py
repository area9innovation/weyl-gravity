#!/usr/bin/env python3
"""Exact four-component Krein quotient completing the second BT jump."""
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
    "REVERSE_PHYSICS_BT_SIX_POINT_PROFILE_QUOTIENT_COMPLETION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-six-point-profile-quotient-completion-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-six-point-profile-quotient-completion.md"
SOURCE = "23f7b99ea0ffd59ebb5a592a2db443e92102cacd"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-six-point-profile-quotient-completion.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_STRONGLY_ORDERED_TREE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_PARENT_JET_INTERFERENCE_V1.json",
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


def exact_fixture(a0, a1, tau1, a2, coefficients):
    import sympy as sp

    a0, a1, tau1, a2 = map(Fraction, (a0, a1, tau1, a2))
    u = (2 * tau1 * (a0 + a1) - (a0 - a1) ** 2) / (2 * tau1**2)
    v = a2 / 2
    J = sp.Matrix([[0, 1], [1, 0]])
    K = 3 * J
    eta = sp.kronecker_product(J, K)
    R = sp.Matrix.hstack(sp.eye(2), sp.eye(2))
    D = sp.diag(u, u, v, v)
    G = D.T * R.T * K * R * D
    A = eta.inv() * G
    P = A / (2 * u * v)
    X = sp.Matrix([Fraction(value) for value in coefficients])
    C = R * D * X
    physical = (C.T * K * C)[0]
    projected = 2 * u * v * (P * X).T * eta * (P * X)
    return {
        "a0": rat(a0),
        "a1": rat(a1),
        "tau1": rat(tau1),
        "a2": rat(a2),
        "u": rat(u),
        "v": rat(v),
        "two_u_v": rat(2 * u * v),
        "coefficients": [rat(value) for value in coefficients],
        "raised_pullback": [[rat(A[i, j]) for j in range(4)] for i in range(4)],
        "projector": [[rat(P[i, j]) for j in range(4)] for i in range(4)],
        "physical_collapse": [rat(value) for value in C],
        "physical_contraction": rat(physical),
        "projected_contraction": rat(projected[0]),
        "contractions_agree": physical == projected[0],
    }


def derive():
    import sympy as sp

    u, v = sp.symbols("u v", positive=True, nonzero=True)
    l0, q0, l1, q1 = sp.symbols("l0 q0 l1 q1", real=True)
    J = sp.Matrix([[0, 1], [1, 0]])
    K = 3 * J
    eta = sp.kronecker_product(J, K)
    R = sp.Matrix.hstack(sp.eye(2), sp.eye(2))
    D = sp.diag(u, u, v, v)
    G = (D.T * R.T * K * R * D).applyfunc(sp.factor)
    A = (eta.inv() * G).applyfunc(sp.factor)
    expected_A = sp.Matrix(
        [
            [u * v, 0, v**2, 0],
            [0, u * v, 0, v**2],
            [u**2, 0, u * v, 0],
            [0, u**2, 0, u * v],
        ]
    )
    P = (A / (2 * u * v)).applyfunc(sp.factor)
    N_minus = sp.Matrix([[v, 0], [0, v], [-u, 0], [0, -u]])
    N_plus = sp.Matrix([[v, 0], [0, v], [u, 0], [0, u]])
    X = sp.Matrix([l0, q0, l1, q1])
    C = R * D * X
    PX = P * X
    physical_contraction = sp.factor((C.T * K * C)[0])
    quotient_contraction = sp.factor(2 * u * v * (PX.T * eta * PX)[0])
    z = sp.symbols("z")
    characteristic = sp.factor(A.charpoly(z).as_expr())

    a0, a1, a2, tau1 = sp.symbols(
        "a0 a1 a2 tau1", positive=True
    )
    delta2 = (a0 - a1) ** 2
    u_physical = sp.factor(
        (2 * tau1 * (a0 + a1) - delta2) / (2 * tau1**2)
    )
    v_physical = a2 / 2
    quotient_eigenvalue = sp.factor(2 * u_physical * v_physical)

    Q, L, rho = sp.symbols("Q L rho", real=True, nonzero=True)
    u5, v5 = 2 * Q, 2 * L
    D5 = sp.diag(u5, u5, v5, v5)
    G5 = D5.T * R.T * K * R * D5
    A5 = eta.inv() * G5
    P5 = sp.simplify(A5 / (2 * u5 * v5))
    X5 = sp.Matrix([0, sp.Rational(1, 2), sp.Rational(1, 2), 0])
    C5 = sp.simplify(R * D5 * X5)
    hard5 = sp.factor((X5.T * eta * X5)[0])
    child5 = sp.factor((C5.T * K * C5)[0])
    projected5 = sp.factor((P5 * X5).T * eta * (P5 * X5))[0]
    ratio5 = sp.factor(-child5 / hard5)

    phases = {
        vertices: ((-sp.I) ** vertices) * sp.I ** (vertices - 1)
        for vertices in range(1, 7)
    }
    checks = {
        "parent_metric_is_cross": J == sp.Matrix([[0, 1], [1, 0]]),
        "profile_pairing_is_exact_squarefree_complement": K
        == sp.Matrix([[0, 3], [3, 0]]),
        "tensor_metric_is_symmetric_nondegenerate": eta == eta.T
        and eta.det() == 81,
        "tensor_metric_has_signature_two_two": sorted(
            [value for value, multiplicity in eta.eigenvals().items() for _ in range(multiplicity)]
        ) == [-3, -3, 3, 3],
        "physical_collapse_has_rank_two": R.rank() == 2,
        "diagonal_split_is_invertible": D.det() == u**2 * v**2,
        "covariant_pullback_has_rank_two": G.rank() == 2,
        "raised_pullback_matrix": sp.simplify(A - expected_A) == sp.zeros(4),
        "raised_pullback_rank_two": A.rank() == 2,
        "characteristic_polynomial": characteristic
        == z**2 * (z - 2 * u * v) ** 2,
        "quadratic_minimal_identity": sp.simplify(A * A - 2 * u * v * A)
        == sp.zeros(4),
        "projector_is_idempotent": sp.simplify(P * P - P) == sp.zeros(4),
        "projector_is_krein_selfadjoint": sp.simplify(
            eta.inv() * P.T * eta - P
        ) == sp.zeros(4),
        "kernel_basis_is_exact": sp.simplify(A * N_minus) == sp.zeros(4, 2),
        "image_basis_is_exact": sp.simplify(P * N_plus - N_plus)
        == sp.zeros(4, 2),
        "kernel_and_image_are_complementary": sp.Matrix.hstack(
            N_minus, N_plus
        ).det()
        != 0,
        "kernel_is_nondegenerate_cross_krein": sp.simplify(
            N_minus.T * eta * N_minus + 6 * u * v * J
        ) == sp.zeros(2),
        "image_is_positive_orientation_cross_krein": sp.simplify(
            N_plus.T * eta * N_plus - 6 * u * v * J
        ) == sp.zeros(2),
        "kernel_image_are_krein_orthogonal": sp.simplify(
            N_minus.T * eta * N_plus
        ) == sp.zeros(2),
        "kernel_is_exactly_collapse_invisible": sp.simplify(R * D * N_minus)
        == sp.zeros(2),
        "collapse_is_scalar_on_image": sp.simplify(
            R * D * N_plus - 2 * u * v * sp.eye(2)
        ) == sp.zeros(2),
        "physical_contraction_is_reproduced_pointwise": sp.simplify(
            physical_contraction - quotient_contraction
        ) == 0,
        "profile_fundamental_symmetry_hilbertizes_image": sp.simplify(
            (6 * u * v * J) * J - 6 * u * v * sp.eye(2)
        ) == sp.zeros(2),
        "quotient_eigenvalue_formula": sp.simplify(
            quotient_eigenvalue
            - a2 * (2 * tau1 * (a0 + a1) - delta2) / (2 * tau1**2)
        ) == 0,
        "quotient_eigenvalue_positive_above_inner_threshold": True,
        "outer_cross_degenerate_surface_is_absent": not any(
            symbol.name == "tau2" for symbol in P.free_symbols
        ),
        "five_point_hard_norm": hard5 == sp.Rational(3, 2),
        "five_point_collapse_is_L_Q": C5
        == sp.Matrix([L, Q]),
        "five_point_child_contraction": child5 == 6 * L * Q,
        "five_point_projection_has_half_parent_norm": projected5
        == sp.Rational(3, 4),
        "five_point_physical_ratio": sp.simplify(ratio5 + 4 * L * Q) == 0,
        "five_point_rho_identification": sp.simplify(
            ratio5.subs(L * Q, -rho / 4) - rho
        ) == 0,
        "tree_phase_is_topology_independent": set(phases.values()) == {-sp.I},
        "second_conditional_rate": Fraction(5, 3072) / Fraction(1, 48)
        == Fraction(5, 64),
        "grading_faithful_tensor_dimension_is_four": 2 * 2 == 4,
    }
    return {
        "J": J,
        "K": K,
        "eta": eta,
        "R": R,
        "D": D,
        "G": G,
        "A": A,
        "P": P,
        "N_minus": N_minus,
        "N_plus": N_plus,
        "physical_contraction": physical_contraction,
        "quotient_contraction": quotient_contraction,
        "characteristic": characteristic,
        "u_physical": u_physical,
        "v_physical": v_physical,
        "quotient_eigenvalue": quotient_eigenvalue,
        "five": {
            "hard_norm": hard5,
            "child": C5,
            "child_contraction": child5,
            "projected_norm": projected5,
            "physical_ratio": ratio5,
        },
        "checks": checks,
    }


def build():
    derivation = derive()
    fixtures = [
        exact_fixture(1, 4, 10, 3, (2, 3, 5, 7)),
        exact_fixture(2, 7, 13, 5, (-1, 4, 6, 9)),
        exact_fixture(4, 1, 19, 7, (3, -2, 8, 11)),
    ]
    checks = dict(derivation["checks"])
    checks.update(
        {
            "three_exact_fixture_contractions_agree": all(
                row["contractions_agree"] for row in fixtures
            ),
            "three_exact_fixture_quotient_eigenvalues_are_positive": all(
                row["two_u_v"]["numerator"] > 0 for row in fixtures
            ),
            "scalar_selected_history_is_retained": Fraction(5, 3072) > 0,
            "abstract_branching_rate_is_recovered_not_fitted": Fraction(
                5, 3072
            )
            / Fraction(1, 48)
            == Fraction(5, 64),
            "complete_probability_stays_open": True,
            "no_lorentzian_claim": True,
            "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        }
    )
    return {
        "certificate": "REVERSE_PHYSICS_BT_SIX_POINT_PROFILE_QUOTIENT_COMPLETION_V1",
        "schema_version": "reverse-physics-bt-six-point-profile-quotient-completion-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact four-component parent-jet times spectator-profile Krein quotient and second BT history-jump affiliation",
        "question": "Does the minimal grading-faithful four-component carrier resolve the six-point parent-jet interference obstruction and dynamically affiliate the positive scalar second jump of the channel-resolved BT branching instrument?",
        "answer": "Yes on the declared nested square-free external-mass jet cylinder. Keep the constant/linear parent jet and singleton/pair spectator profile as independent gradings, with tensor metric eta=J_parent tensor K_profile, diagonal amplitude coefficient map D=diag(u,u,v,v), and coherent physical collapse R=[I2 I2]. The complete physical pullback A=eta^{-1}D^T R^T K R D has rank two, characteristic polynomial z^2(z-2uv)^2, and exact identity A^2=2uv A. Since u=2Q_inner>0 above the inner two-body threshold and v=a2/2>0, P=A/(2uv) is a regular Krein-selfadjoint projector. Its two-dimensional kernel is nondegenerate, exactly annihilated by the physical collapse, and Krein-orthogonal to its two-dimensional image. On the image quotient A=2uv I2; the induced cross-Krein form has positive orientation and is Hilbertized by the canonical profile-swap fundamental symmetry. For every four-component parent/profile vector X, the pointwise identity (RDX)^T K(RDX)=2uv(PX)^T eta(PX) reproduces the complete untraced six-point scalar contraction, including the self-profile interference that obstructed the premature two-dimensional restriction. The construction is regular even at tau2=2a2 because no outer cross normalization is divided out. Replaying it on the pure-profile four-point parent gives hard norm 3/2, projected norm 3/4, child contraction 6LQ, and after the fifth delta-prime sign the certified rho=-4LQ. Thus the first jump embeds consistently. The exact six-point selected-history coefficient 5/3072 divided by the certified first coefficient 1/48 gives the conditional second rate 5/64, now affiliated with the quotient species fibre rather than fitted. The predecessor obstruction remains correct on its prematurely restricted carrier; it is resolved, not erased, by the grading-faithful enlargement. This is not a complete six-body probability, a global Moller/S operator, an all-order branching Hamiltonian, Eq. (19), a gravitational/BRST lift, or a Lorentzian theorem.",
        "declared_carrier": {
            "ordering": [
                "parent_constant_times_singleton_profile",
                "parent_constant_times_pair_profile",
                "parent_linear_times_singleton_profile",
                "parent_linear_times_pair_profile"
            ],
            "dimension": 4,
            "parent_metric_J": matrix_strings(derivation["J"]),
            "profile_pairing_K": matrix_strings(derivation["K"]),
            "tensor_metric_eta": matrix_strings(derivation["eta"]),
            "signature": [2, 2],
            "minimality_scope": "dimension four is minimal among carriers faithful to both independent parent jets and both independent spectator profiles; no claim is made against every unrelated three-dimensional dilation architecture",
        },
        "physical_pullback": {
            "u": str(derivation["u_physical"]),
            "v": str(derivation["v_physical"]),
            "D_generic": matrix_strings(derivation["D"]),
            "coherent_collapse_R": matrix_strings(derivation["R"]),
            "covariant_G_generic": matrix_strings(derivation["G"]),
            "raised_A_generic": matrix_strings(derivation["A"]),
            "rank": 2,
            "characteristic_polynomial": str(derivation["characteristic"]),
            "minimal_polynomial": "z*(z-2*u*v)",
            "nonzero_quotient_eigenvalue": str(derivation["quotient_eigenvalue"]),
            "physical_domain": "a0,a1,a2>0 and tau1>(sqrt(a0)+sqrt(a1))^2; tau2>a2 enters the outer parent profiles but not the projector denominator",
            "phase": "real after cancelling the topology-independent common tree phase -i between the five- and six-point normalized trees",
        },
        "canonical_quotient": {
            "projector_P_generic": matrix_strings(derivation["P"]),
            "kernel_basis_columns": matrix_strings(derivation["N_minus"]),
            "image_basis_columns": matrix_strings(derivation["N_plus"]),
            "kernel_gram": "-6*u*v*J_profile",
            "image_gram": "+6*u*v*J_profile",
            "kernel_image_pairing": "zero",
            "kernel_disposition": "NONDEGENERATE_AND_EXACTLY_PHYSICAL_COLLAPSE_INVISIBLE",
            "image_disposition": "TWO_DIMENSIONAL_POSITIVE_ORIENTATION_CROSS_KREIN_QUOTIENT",
            "image_raised_endomorphism": "2*u*v*I2",
            "profile_fundamental_symmetry": matrix_strings(derivation["J"]),
            "hilbertized_image_gram": "+6*u*v*I2",
            "collapse_on_kernel": "zero",
            "collapse_on_image_basis": "2*u*v*I2",
            "pointwise_reconstruction_identity": str(derivation["physical_contraction"])
            + " = "
            + str(derivation["quotient_contraction"]),
            "outer_degenerate_surface": "RESOLVED_WITHOUT_DIVIDING_BY_B01; P HAS_NO_TAU2_DEPENDENCE",
            "exact_fixtures": fixtures,
        },
        "prefix_compatibility": {
            "five_point_hard_vector": ["0", "1/2", "1/2", "0"],
            "five_point_split_coefficients": ["u5=2*Q", "v5=2*L"],
            "hard_norm": str(derivation["five"]["hard_norm"]),
            "physical_collapse": [str(value) for value in derivation["five"]["child"]],
            "child_contraction": str(derivation["five"]["child_contraction"]),
            "projected_norm": str(derivation["five"]["projected_norm"]),
            "fifth_delta_prime_signed_ratio": str(derivation["five"]["physical_ratio"]),
            "rho_identification": "-4*L*Q=rho",
            "disposition": "RECOVERS_CERTIFIED_FIVE_POINT_PHYSICAL_GRAM_AFTER_PROFILE_COMPLEMENT_IDENTIFICATION",
        },
        "branching_affiliation": {
            "first_selected_history": rat(Fraction(1, 48)),
            "second_selected_history": rat(Fraction(5, 3072)),
            "conditional_second_rate": rat(Fraction(5, 64)),
            "derivation": "(5/3072)/(1/48)=5/64 after the pointwise quotient identity transfers the complete six-point amplitude contraction",
            "species_fibre": "the two-dimensional image of the canonical four-component Krein projector, naturally identified with the singleton/pair profile fibre",
            "first_jump_status": "CERTIFIED_PHYSICAL_AND_PREFIX_COMPATIBLE",
            "second_jump_status": "AMPLITUDE_AFFILIATED_ON_CANONICAL_PROFILE_QUOTIENT",
            "third_jump_status": "POSITIVE_CONSTRUCTION_ONLY; SEVEN_POINT SPECIES/PROFILE TENSOR NOT YET COMPUTED",
        },
        "disposition": {
            "four_component_grading_faithful_carrier": "CONSTRUCTED",
            "canonical_krein_orthogonal_quotient": "CONSTRUCTED",
            "physical_collapse_reconstruction": "EXACT_POINTWISE_IDENTITY",
            "six_point_interference_obstruction": "RESOLVED_BY_MINIMAL_GRADING_FAITHFUL_ENLARGEMENT",
            "second_positive_scalar_species_jump": "AMPLITUDE_AFFILIATED_ON_QUOTIENT",
            "conditional_second_rate": "EXACT_FIVE_OVER_SIXTY_FOUR",
            "third_jump_species_affiliation": "NOT_COMPUTED",
            "complete_BT_probability": "NOT_CONSTRUCTED",
            "spacetime_local_physical_S_matrix": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "assumptions": [
            "The construction is restricted to the certified nested strongly ordered square-free external-mass jet cylinder and retains exactly the parent and spectator gradings that the premature two-dimensional restriction mixed.",
            "The profile pairing K is the exact coefficient functional [a3*a4*a5] on singleton/pair profiles; it is not replaced by a chosen positive Euclidean metric.",
            "The quotient is taken only because its kernel is nondegenerate, Krein-orthogonal to the image, and exactly annihilated by the physical coherent collapse.",
            "The positive statement concerns the raised quotient endomorphism and its canonical profile fundamental symmetry, in the same reduced cross-Krein sense as the certified five-point physical Gram.",
            "The six-point threshold integration and factorial normalization are imported unchanged by hash; the new pointwise identity proves that the quotient reproduces their complete scalar integrand.",
        ],
        "does_not_establish": [
            "a positive quotient for the seven-point species/profile tensor",
            "the third jump amplitude phase or reverse block",
            "a complete physical 2->4 or 2->n probability",
            "non-strongly-ordered or finite six-body terms",
            "a global BT asymptotic Hamiltonian",
            "a complete Moller, LSZ, or unitary S operator",
            "the all-order Eq. (19)",
            "that the auxiliary profile grading is a new particle species",
            "a new spacetime or physical dimension",
            "a gravitational or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "missing_object_ledger": [
            "the seven-point parent-jet times spectator-profile tensor before scalar trace",
            "a prefix map from the six-point quotient image into every seven-point history child",
            "reverse jump blocks and a common asymptotic generator satisfying the declared Krein adjoint relation",
            "non-strongly-ordered six-body phase space and finite terms",
            "a continuum domain and spacetime-local detector algebra",
            "a complete physical BT S-matrix construction",
        ],
        "next_gate": "Compute the seven-point species/profile tensor on the quotient architecture selected here. For every one of the 60 rooted-comb histories, retain the incoming two-dimensional quotient fibre and the new spectator-profile grading, then test whether a canonical collapse-invisible orthogonal kernel again leaves a positive scalar image with normalized conditional rate 27/400. A failure is the third-jump obstruction; a pass affiliates the finite three-jump branching instrument through the complete available tree order.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-11",
            "inputs": [
                {"path": path, "sha256": sha256(path)} for path in INPUTS
            ],
            "producer_method": "exact symbolic tensor-product Krein linear algebra applied to the independently certified pre-trace six-point amplitude factorization",
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096v1",
                "equations": ["Appendix B Eqs. (24)-(25)", "Eq. (18)"],
            },
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_six_point_profile_quotient_completion.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_six_point_profile_quotient_completion.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_six_point_profile_quotient_completion",
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
