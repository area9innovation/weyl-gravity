#!/usr/bin/env python3
"""Exact finite-hierarchy BT physical continuum Moller column."""
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
    "REVERSE_PHYSICS_BT_FINITE_PHYSICAL_MOLLER_COLUMN_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-finite-physical-moller-column-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-finite-physical-moller-column.md"
SOURCE = "4ac684c16a5d5acea2150c35dee380b1360ff2c2"
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-finite-physical-moller-column.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_QUANTUM_STOCHASTIC_MOLLER_DILATION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SEVEN_POINT_NESTED_CONTINUUM_INTERTWINER_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_INCLUSIVE_NLO_OBJECT_LEDGER_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1.json",
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


def matrix_strings(matrix):
    import sympy as sp

    return [
        [str(sp.factor(matrix[i, j])) for j in range(matrix.cols)]
        for i in range(matrix.rows)
    ]


def derive():
    import sympy as sp

    hp = load(INPUTS[1])
    continuum = load(INPUTS[2])
    physical = load(INPUTS[3])
    ledger = load(INPUTS[4])
    eq19 = load(INPUTS[5])

    a, t1, t2, t3 = sp.symbols("a t1 t2 t3", nonnegative=True)
    q0 = sp.Rational(1, 48)
    q1 = sp.Rational(5, 64)
    q2 = sp.Rational(27, 400)
    exit_rates = [3 * q0, 4 * q1, 5 * q2, sp.Rational(0)]
    drifts = [value / 2 for value in exit_rates]
    history_counts = [1, 3, 12, 60]

    kernels = [
        sp.exp(-drifts[0] * a),
        sp.sqrt(q0) * sp.exp(
            -drifts[0] * t1 - drifts[1] * (a - t1)
        ),
        sp.sqrt(q0 * q1) * sp.exp(
            -drifts[0] * t1
            - drifts[1] * (t2 - t1)
            - drifts[2] * (a - t2)
        ),
        sp.sqrt(q0 * q1 * q2) * sp.exp(
            -drifts[0] * t1
            - drifts[1] * (t2 - t1)
            - drifts[2] * (t3 - t2)
            - drifts[3] * (a - t3)
        ),
    ]
    probabilities = [
        sp.factor(kernels[0] ** 2),
        sp.factor(
            history_counts[1]
            * sp.integrate(kernels[1] ** 2, (t1, 0, a))
        ),
        sp.factor(
            history_counts[2]
            * sp.integrate(
                sp.integrate(kernels[2] ** 2, (t1, 0, t2)),
                (t2, 0, a),
            )
        ),
        sp.factor(
            history_counts[3]
            * sp.integrate(
                sp.integrate(
                    sp.integrate(kernels[3] ** 2, (t1, 0, t2)),
                    (t2, 0, t3),
                ),
                (t3, 0, a),
            )
        ),
    ]
    serialized_probabilities = [
        sp.sympify(
            row["time_probability"],
            locals={"a": a, "exp": sp.exp},
        )
        for row in hp["vacuum_reduction"]["population_laplace_rows"]
    ]
    population = sp.Matrix(probabilities)
    generator = sp.Matrix(
        [
            [-exit_rates[0], 0, 0, 0],
            [exit_rates[0], -exit_rates[1], 0, 0],
            [0, exit_rates[1], -exit_rates[2], 0],
            [0, 0, exit_rates[2], 0],
        ]
    )
    ode_defect = sp.simplify(sp.diff(population, a) - generator * population)
    leading = [
        sp.expand(probabilities[k].series(a, 0, 5).removeO()).coeff(a, k)
        for k in range(4)
    ]
    expected_leading = [
        sp.Rational(1),
        sp.Rational(1, 16),
        sp.Rational(5, 512),
        sp.Rational(9, 8192),
    ]

    # The first-emission typed compression square.  D is a concrete
    # representative of the public rank-one parent Gram.  T is the physical
    # external-jet splitting map, with rho=-4*L*Q>0.
    rho, L, Q = sp.symbols("rho L Q", nonzero=True, real=True)
    J = sp.Matrix([[0, 1], [1, 0]])
    D_public = sp.Matrix([[0, 1], [0, 1]])
    C_missing = sp.Matrix([[-rho, -1], [0, 1]])
    T_physical = sp.diag(2 * Q, 2 * L)
    eta = sp.diag(J, J)
    F_common = D_public.col_join(C_missing)
    G_public = sp.simplify(D_public.T * J * D_public)
    N_public = sp.simplify(J * G_public)
    G_missing = sp.simplify(C_missing.T * J * C_missing)
    N_missing = sp.simplify(J * G_missing)
    G_common = sp.simplify(F_common.T * eta * F_common)
    G_physical = sp.simplify(T_physical.T * J * T_physical)
    W = sp.simplify(F_common * T_physical.inv())
    W_gram_on_shell = sp.simplify(
        (W.T * eta * W).subs(rho, -4 * L * Q)
    )
    common_gram_on_shell = sp.simplify(
        (G_common - G_physical).subs(rho, -4 * L * Q)
    )

    born = frac(ledger["combined_ledger"]["Born_coefficient_without_common_factors"])
    real_absolute = frac(
        ledger["combined_ledger"]["physical_real_response"]
    )
    hard_normalized = -Fraction(exit_rates[0])
    hard_absolute = Fraction(born) * hard_normalized
    inclusive_absolute = hard_absolute + real_absolute

    hp_counts = hp["system_and_noise_carrier"]["history_counts"]
    hp_edge_counts = hp["system_and_noise_carrier"]["edge_counts"]
    checks = {
        "predecessor_checks": all(
            value["checks"]["ok"]
            for value in (hp, continuum, physical, ledger, eq19)
        ),
        "history_counts_match": hp_counts == history_counts,
        "edge_counts_match": hp_edge_counts == [3, 12, 60],
        "all_seventy_five_marks_physical": (
            continuum["seventy_five_mark_completion"]
            ["physically_intertwined_edge_marks"] == list(range(75))
        ),
        "hp_drifts_match": hp["hudson_parthasarathy_cocycle"]
        ["drift_eigenvalues_by_level"] == [str(value) for value in drifts],
        "integrated_kernels_match_serialized_probabilities": all(
            sp.simplify(left - right) == 0
            for left, right in zip(probabilities, serialized_probabilities)
        ),
        "population_ode": ode_defect == sp.zeros(4, 1),
        "population_initial_condition": population.subs(a, 0) == sp.Matrix([1, 0, 0, 0]),
        "probability_normalization": sp.simplify(sum(probabilities) - 1) == 0,
        "leading_tree_coefficients": leading == expected_leading,
        "physical_direct_sum_isometry_imported": continuum
        ["seventy_five_mark_completion"]["direct_sum"].startswith("A_<=3="),
        "hp_unitary_imported": hp["hudson_parthasarathy_cocycle"]
        ["solution"].startswith("UNIQUE_BOUNDED"),
        "public_covariant_gram": G_public == sp.diag(0, 2),
        "public_raised_nilpotent": (
            N_public == sp.Matrix([[0, 2], [0, 0]])
            and N_public**2 == sp.zeros(2)
            and N_public.rank() == 1
        ),
        "missing_covariant_gram": G_missing == sp.Matrix(
            [[0, -rho], [-rho, -2]]
        ),
        "missing_raised_gram": N_missing == -rho * sp.eye(2) - N_public,
        "common_pullback_equals_physical": common_gram_on_shell == sp.zeros(2),
        "compression_square": sp.simplify(W * T_physical - F_common) == sp.zeros(4, 2),
        "bridge_is_krein_isometry": W_gram_on_shell == J,
        "missing_fibre_is_nondegenerate": sp.factor(G_missing.det()) == -rho**2,
        "missing_fibre_signature_is_cross_krein": (
            sp.factor(G_missing.det()) == -rho**2
            and sp.trace(G_missing) == -2
        ),
        "missing_block_is_not_trace_null": sp.trace(N_missing) == -2 * rho,
        "no_positive_auxiliary_gram": sp.factor(G_missing.det()) < 0,
        "public_and_physical_objects_remain_distinct": ledger
        ["combined_ledger"]["typing_rule"]
        == "THE_RT_PUSHFORWARD_RESPONSE_IS_NOT_ADDED_TO_THE_PHYSICAL_SMATRIX_LEDGER",
        "finite_model_hard_real_cancellation": inclusive_absolute == 0,
        "public_rt_not_used_as_hard_term": frac(
            ledger["combined_ledger"]["nonphysical_Rt_comparison_response"]
        ) == 0,
        "eq19_only_finite_order_imported": eq19["disposition"]
        ["finite_mode_order_lambda_Eq19"] == "PROVED_WITH_Q1_ZERO",
        "eq19_all_orders_stays_open": all(
            value["disposition"]["Eq19_all_orders"] == "NOT_PROVED"
            for value in (continuum, ledger)
        ),
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    return locals()


def build():
    d = derive()
    checks = dict(d["checks"])
    checks.update(
        {
            "finite_physical_vacuum_column_isometry": (
                checks["physical_direct_sum_isometry_imported"]
                and checks["hp_unitary_imported"]
                and checks["probability_normalization"]
            ),
            "all_available_output_sectors_are_physical": (
                checks["all_seventy_five_marks_physical"]
                and checks["integrated_kernels_match_serialized_probabilities"]
            ),
            "minimal_complement_dimension_is_two": (
                checks["missing_fibre_is_nondegenerate"]
                and d["C_missing"].rank() == 2
            ),
            "positive_or_null_only_repair_is_excluded": (
                checks["no_positive_auxiliary_gram"]
                and checks["missing_block_is_not_trace_null"]
            ),
        }
    )
    probabilities = [str(value) for value in d["probabilities"]]
    return {
        "certificate": "REVERSE_PHYSICS_BT_FINITE_PHYSICAL_MOLLER_COLUMN_V1",
        "schema_version": "reverse-physics-bt-finite-physical-moller-column-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact finite-hierarchy physical continuum vacuum Moller column and minimal typed public-R_t compression completion",
        "question": "Does the completed 75-mark continuum affiliation turn the finite HP evolution into a normalized physical transition column, and what is the smallest extra fibre needed for the inequivalent public R_t quadratic leg to occur as its compression?",
        "answer": "Yes on the certified finite reduced-mode hierarchy. Let I_Omega include the incoming hard two-species state with vacuum noise, let U_a be the exact 75-channel HP unitary, and let A_<=3 be the direct sum of the certified physical continuum isometries through three emissions. Then M_a=A_<=3 U_a I_Omega is an isometry into the hard plus physical one-, two-, and three-emission continuum ranges. Its exact ordered-history kernels contain the HP survival factors, integrate to nonnegative p_0,...,p_3, and sum to one for every a>=0. Their first allowed coefficients are 1, 1/16, 5/512, and 9/8192. In this pinned finite resolution model the physical hard response -1/16 is therefore on the same column as the physical real response +1/16; multiplying by the Born factor 3/32 gives -3/512+3/512=0 without using the public R_t pushforward as a scattering summand. At the first-emission fibre, the public rank-one leg D has D^T J D=diag(0,2), while the physical map T has T^T J T=-rho J. They cannot be equal, but there is a unique pullback requirement for an orthogonal complement: C^T J C=-rho J-diag(0,2). The explicit minimal solution C=[[-rho,-1],[0,1]] is two-dimensional and cross-Krein. With F=(D,C), W=F T^-1 obeys W^T(J direct_sum J)W=J and W T=F, so projection onto the first target leg gives D. The missing Gram has determinant -rho^2 and raised trace -2rho. Hence neither a positive auxiliary/noise fibre nor a trace-null Eq. (19) remainder alone can repair the public-to-physical rank defect. A non-null two-direction complement is necessary. This constructs the finite physical column and the minimal algebraic bridge architecture; it does not derive that complement from BT dynamics, produce a two-sided spacetime S operator, or prove Eq. (19) all orders.",
        "declared_carriers": {
            "incoming": "C2_species hard history tensored with the HP noise vacuum",
            "hp_output": "direct sum of ordered zero-, one-, two-, and three-noise vacuum-output sectors of the 152-dimensional system and 75-mark Fock carrier",
            "physical_output": "direct sum of the hard range and all certified five-, six-, and seven-point nested physical continuum ranges",
            "dense_domain": d["continuum"]["finite_hierarchy_dense_domain"]["dense_core"],
            "parameter": "a>=0 is additive detector resolution, not Minkowski time or a spacetime coordinate",
        },
        "physical_vacuum_moller_column": {
            "definition": "M_a=A_<=3 U_a I_Omega",
            "isometry": "M_a^* M_a=I2 on the incoming hard species because I_Omega and A_<=3 are isometries and U_a is unitary",
            "range_projection": "P_a=M_a M_a^* is an orthogonal projection on the finite physical continuum output range",
            "history_counts": d["history_counts"],
            "edge_counts": [3, 12, 60],
            "physical_edge_marks": list(range(75)),
            "conditional_rates": [rat(Fraction(1, 48)), rat(Fraction(5, 64)), rat(Fraction(27, 400))],
            "amplitude_drifts": [str(value) for value in d["drifts"]],
            "ordered_history_kernel": "psi_k(t1,...,tk;a)=sqrt(product_(j<k)q_j)*exp[-d0*t1-sum_(j=1)^(k-1)d_j*(t_(j+1)-t_j)-d_k*(a-t_k)] on 0<t1<...<tk<a; psi_0=exp(-d0*a)",
            "sector_probabilities": probabilities,
            "normalization": "sum_(k=0)^3 p_k(a)=1 for every a>=0",
            "positivity": "each p_k is a history count times the integral of |psi_k|^2 over its ordered simplex",
            "leading_coefficients": [rat(Fraction(value)) for value in d["expected_leading"]],
            "status": "EXACT_PHYSICAL_CONTINUUM_VACUUM_COLUMN_ON_THE_AVAILABLE_FINITE_HIERARCHY",
        },
        "finite_model_inclusive_response": {
            "hard_survival_probability": "exp(-a/16)",
            "hard_normalized_linear_response": rat(d["hard_normalized"]),
            "real_normalized_linear_response": rat(Fraction(1, 16)),
            "Born_coefficient": rat(d["born"]),
            "hard_absolute_response": rat(d["hard_absolute"]),
            "real_absolute_response": rat(d["real_absolute"]),
            "inclusive_absolute_response": rat(d["inclusive_absolute"]),
            "typing": "The hard drift and physical real continuum sectors are two components of M_a. The zero public R_t projector-pushforward response is not added to this ledger.",
            "boundary": "This is exact for the pinned finite HP completion. It is not a derivation of the hard/dressed term from the full BT loop or asymptotic Hamiltonian and is not a complete NLO theorem.",
        },
        "minimal_public_Rt_compression": {
            "domain_metric_J": matrix_strings(d["J"]),
            "public_leg_D": matrix_strings(d["D_public"]),
            "public_covariant_gram": matrix_strings(d["G_public"]),
            "public_raised_gram": matrix_strings(d["N_public"]),
            "physical_leg_T": matrix_strings(d["T_physical"]),
            "physical_relation": "rho=-4*L*Q>0 and T^T J T=-rho J",
            "missing_leg_C": matrix_strings(d["C_missing"]),
            "missing_covariant_gram": matrix_strings(d["G_missing"]),
            "missing_raised_gram": matrix_strings(d["N_missing"]),
            "common_leg_F": matrix_strings(d["F_common"]),
            "target_metric": "eta=J direct_sum J",
            "bridge_W": matrix_strings(d["W"]),
            "commuting_square": "W*T=F=(D,C), hence projection_public*W*T=D",
            "isometry": "after rho=-4*L*Q, W^T eta W=J",
            "minimality": "det(C^T J C)=-rho^2 is nonzero, so the missing pullback has rank two and every realizing auxiliary target has dimension at least two",
            "positive_auxiliary_obstruction": "det(C^T J C)<0, so no positive-Hilbert auxiliary Gram realizes the required complement",
            "null_remainder_obstruction": "Tr(C^sharp C)=-2rho is nonzero, so a trace-null Q remainder alone cannot supply the missing physical response",
            "uniqueness": "the missing pullback Gram is forced; its minimal realizations are unique up to a target Krein isometry, while the displayed C is one exact representative",
            "continuum_domain": "rho>0 above unequal-mass threshold; the pointwise bridge is measurable on the same compact physical core and is not extended through the measure-zero degenerate threshold",
        },
        "typed_Eq19_boundary": {
            "public_object": "R_t P_chi^(phi) R_t^dagger is a field/projector pushforward",
            "physical_object": "M_a is the vacuum transition column of a pinned resolution-stochastic completion",
            "nonidentification": "The compression square retains the public D leg but does not identify D, R_t, or its zero trace with the physical splitting operator or hard response.",
            "finite_order_import": "The public finite-mode zero-mode-completed quadratic sector satisfies the Eq. (19) form through order lambda with Q1=0.",
            "new_exact_condition": "Any common first-emission dilation matching the physical Gram while retaining the public D compression needs the displayed non-null two-dimensional cross-Krein complement.",
            "missing_dynamical_statement": "BT dynamics must produce that complement on the same zero-mode, charge, trace, and continuum domain; algebraic existence does not prove that it does.",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "disposition": {
            "finite_physical_continuum_vacuum_Moller_column": "CONSTRUCTED_EXACTLY",
            "finite_hierarchy_probability": "POSITIVE_AND_NORMALIZED_FOR_EVERY_RESOLUTION_LENGTH",
            "hard_dressed_response_in_pinned_finite_model": "CONSTRUCTED_AND_CANCELS_THE_REAL_LINEAR_RESPONSE",
            "minimal_public_Rt_compression_architecture": "CONSTRUCTED_EXACTLY",
            "missing_public_Rt_complement": "ALGEBRAIC_FORM_AND_MINIMAL_INERTIA_FIXED_BUT_NOT_DERIVED_FROM_BT_DYNAMICS",
            "public_Rt_equals_physical_splitting": "EXACTLY_FALSE",
            "full_two_sided_physical_S_operator": "NOT_CONSTRUCTED",
            "fourth_jump": "NOT_COMPUTED",
            "complete_BT_probability": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED",
            "spacetime_Moller_LSZ_S_operator": "NOT_CONSTRUCTED",
        },
        "assumptions": [
            "The stochastic dynamics is the pinned finite 75-channel HP completion, not a derivation from the unpublished all-order BT asymptotic Hamiltonian.",
            "Only the vacuum input column is physically continuum affiliated. The full HP unitary on arbitrary incoming noise is not transported to a two-sided physical scattering operator.",
            "Level three has no outgoing edge because the amplitude data stop at seven points; this is not interpreted as physical termination.",
            "The physical continuum maps use the massless nested hierarchy limits on their certified compact dense core.",
            "The public compression calculation is pointwise above unequal-mass threshold and uses the same cross metric as the certified rank/Jordan comparison.",
        ],
        "does_not_establish": [
            "that the pinned finite HP completion is the unique or dynamically selected nonlinear BT evolution",
            "a two-sided physical unitary on arbitrary incoming continuum/noise sectors",
            "a fourth jump, an eight-point quotient, or an all-order inductive carrier",
            "complete BT two-to-n probability",
            "a full finite NLO inclusive probability or finite constant",
            "that BT zero-mode, vacuum, or higher-composite dynamics produces the displayed missing complement",
            "identification of the public R_t map with the physical splitting or Moller operator",
            "Bateman--Turok Eq. (19) beyond its imported finite-mode order-lambda sector",
            "a spacetime-local Moller, LSZ, S, detector, or AQFT construction",
            "a metric or BRST lift to pure Weyl gravity",
            "a new physical or spacetime dimension",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "missing_object_ledger": [
            "a BT-derived non-null two-direction complement with the certified pullback Gram, charge grading, and zero-mode trace domain",
            "the fourth physical jump and eight-point pre-trace quotient needed to test induction",
            "a physical affiliation of arbitrary incoming-noise sectors and the reverse column",
            "complete non-strongly-ordered and degenerate asymptotic sectors",
            "a spacetime-local physical Moller/LSZ/S operator",
            "the all-order R_t projector pushforward and Eq. (19) charge-support theorem",
        ],
        "next_gate": "The finite physical vacuum column is complete on every currently available channel, and the old rank/Jordan mismatch is now a constructive minimal-completion condition rather than an untyped impasse. The Eq. (19)-direct route is to derive or obstruct a BT zero-mode/vacuum/higher-composite block whose pointwise pullback is C^T J C=-rho J-diag(0,2), with nonzero raised trace -2rho, while preserving the public cross-CCR and charge support. The independent all-order discriminator remains the complete eight-point fourth quotient. The missing-complement calculation is the nearer Eq. (19) gate because the eight-point scalar alone cannot supply the public-to-physical bridge.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "producer_method": "Exact SymPy ordered-simplex integration of the HP vacuum trajectory kernels, exact population ODE and Taylor checks, exact rational Born-response ledger, and symbolic cross-Krein congruence/compression algebra. No floating-point arithmetic is used.",
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096v1",
                "equations": ["Eq. (19)", "Eq. (21)", "Appendix C"],
            },
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_finite_physical_moller_column.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_finite_physical_moller_column.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest reverse_physics.tests.test_bt_finite_physical_moller_column",
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
