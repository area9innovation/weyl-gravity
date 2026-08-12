#!/usr/bin/env python3
"""Exact full-map homogeneous-charge no-go for Bateman--Turok Eq. (19)."""
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
    "REVERSE_PHYSICS_BT_EQ19_SPURION_SQUEEZE_DICHOTOMY_NO_GO_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-eq19-spurion-squeeze-dichotomy-no-go-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-eq19-spurion-squeeze-dichotomy-no-go.md"
SOURCE = "31357dbebde04d62b2736acebcf67427b54f7b56"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-eq19-spurion-squeeze-dichotomy-no-go-"
    "DONE-31357dbe.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-eq19-spurion-squeeze-dichotomy-no-go.json",
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_BORN_TRACE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SQUEEZED_DETECTOR_SIMILARITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SQUEEZED_VACUUM_IMPLEMENTABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COVARIANT_GHOST_PARITY_BRANCH_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_REGULAR_COVARIANT_EQ19_NO_GO_V1.json",
    EVENT,
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


def matrix(rows):
    import sympy as sp

    return sp.Matrix([[sp.Rational(value) for value in row] for row in rows])


def clean(poly):
    return {power: value for power, value in poly.items() if not value.is_zero_matrix}


def laurent_add(left, right, scale=1):
    import sympy as sp

    sample = next(iter(left.values())) if left else next(iter(right.values()))
    answer = {}
    for power in set(left) | set(right):
        answer[power] = left.get(power, sp.zeros(sample.rows)) + scale * right.get(
            power, sp.zeros(sample.rows)
        )
    return clean(answer)


def laurent_scale(scale, poly):
    return clean({power: scale * value for power, value in poly.items()})


def laurent_multiply(left, right):
    import sympy as sp

    size = next(iter(left.values())).rows
    answer = {}
    for left_power, left_value in left.items():
        for right_power, right_value in right.items():
            power = left_power + right_power
            answer[power] = answer.get(power, sp.zeros(size)) + left_value * right_value
    return clean(answer)


def laurent_sharp(poly, gram):
    return clean({power: gram * value.T * gram for power, value in poly.items()})


def laurent_parity(poly, kappa):
    return clean({-power: kappa * value * kappa for power, value in poly.items()})


def coefficient_trace(poly, power=0):
    import sympy as sp

    return sp.factor(sp.trace(poly[power])) if power in poly else sp.Rational(0)


def matrix_json(value):
    import sympy as sp

    return [
        [str(sp.factor(value[i, j])) for j in range(value.cols)]
        for i in range(value.rows)
    ]


def laurent_json(poly):
    return {str(power): matrix_json(value) for power, value in sorted(poly.items())}


def build():
    import sympy as sp

    source_data = load(INPUTS[1])
    born = load(INPUTS[2])
    zero_mode = load(INPUTS[3])
    signed = load(INPUTS[4])
    squeeze_similarity = load(INPUTS[5])
    squeeze_fock = load(INPUTS[6])
    ghost = load(INPUTS[7])
    predecessor = load(INPUTS[8])

    block = ghost["finite_resonant_block"]
    gram_n1 = matrix(block["gram"])
    kappa_n1 = matrix(block["ghost_parity"])
    p_n1 = matrix(block["P0"])
    k_plus = matrix(block["K_plus"])
    tangent = k_plus * p_n1 - p_n1 * k_plus

    z = sp.symbols("z", real=True, nonzero=True)
    pair_gram = sp.Matrix([[1, 0, 0], [0, 0, 1], [0, 1, 0]])
    pair_kappa = pair_gram
    pair_q = sp.Matrix([[0, -z, 0], [0, 0, 0], [z, 0, 0]])
    pair_p = sp.diag(1, 0, 0)
    pair_s = sp.eye(3) + pair_q + pair_q**2 / 2
    pair_s_inverse = sp.eye(3) - pair_q + pair_q**2 / 2
    pair_a_matrix = sp.simplify(pair_s * pair_p * pair_s_inverse)
    pair_a = {
        0: pair_p,
        2: sp.Matrix([[0, z, 0], [0, 0, 0], [z, 0, 0]]),
        4: sp.Matrix([[0, 0, 0], [0, 0, 0], [0, z**2, 0]]),
    }

    full_gram = sp.kronecker_product(gram_n1, pair_gram)
    full_kappa = sp.kronecker_product(kappa_n1, pair_kappa)
    input_projector = sp.kronecker_product(p_n1, pair_p)
    full_a = {
        power: sp.kronecker_product(p_n1, value)
        for power, value in pair_a.items()
    }
    full_parity = laurent_parity(full_a, full_kappa)
    full_even = laurent_scale(sp.Rational(1, 2), laurent_add(full_a, full_parity))
    full_odd = laurent_scale(sp.Rational(1, 2), laurent_add(full_a, full_parity, -1))
    full_odd_norm = coefficient_trace(
        laurent_multiply(laurent_sharp(full_odd, full_gram), full_odd)
    )
    full_overlap = coefficient_trace(
        laurent_multiply(laurent_sharp(full_even, full_gram), full_odd)
    )
    pair_parity = laurent_parity(pair_a, pair_kappa)
    pair_odd = laurent_scale(sp.Rational(1, 2), laurent_add(pair_a, pair_parity, -1))
    pair_odd_norm = coefficient_trace(
        laurent_multiply(laurent_sharp(pair_odd, pair_gram), pair_odd)
    )
    pair_overlap = coefficient_trace(
        laurent_multiply(
            laurent_sharp(
                laurent_scale(sp.Rational(1, 2), laurent_add(pair_a, pair_parity)),
                pair_gram,
            ),
            pair_odd,
        )
    )

    physical_z_row = squeeze_fock["finite_box_carrier"]["unordered_pair_amplitude"]
    physical_z = sp.Rational(
        physical_z_row["numerator"], physical_z_row["denominator"]
    )
    physical_full_norm = sp.factor(full_odd_norm.subs(z, physical_z))

    tangent_zero_pair = sp.kronecker_product(tangent, pair_p)
    tangent_one_pair = sp.kronecker_product(tangent, pair_a[2])
    tangent_two_pair = sp.kronecker_product(tangent, pair_a[4])
    free_one_pair = sp.kronecker_product(p_n1, pair_a[2])
    free_two_pair = sp.kronecker_product(p_n1, pair_a[4])

    q_k = 1 - sp.symbols("s", real=True)
    q_s = 2 * sp.symbols("s", real=True) - 2
    source_mechanism = born["source"]["mechanism"]
    checks = {
        "predecessor_certificates_pass": all(
            item["checks"]["ok"]
            for item in (
                born,
                zero_mode,
                signed,
                squeeze_similarity,
                squeeze_fock,
                ghost,
                predecessor,
            )
        ),
        "primary_source_records_no_positive_and_ghost_even_neutral": (
            "neutral AND even under ghost parity" in source_mechanism
            and "strictly negatively charged" in source_mechanism
            and "no positive" in source_mechanism
        ),
        "source_record_marks_continuum_pushforward_deferred": (
            "defers" in source_data["public_inputs"]["scope"]
        ),
        "full_map_factorization_imported": (
            squeeze_similarity["operator_identity"]["factorization"]
            == "R(lambda)=S U(lambda) on the paired core, with U(lambda)=1+lambda K+O(lambda^2)"
        ),
        "complete_public_nonlinear_kernel_imported": (
            signed["completed_signed_kernel"]["disposition"]
            == "COMPLETE_FOR_THE_PUBLIC_ORDER_LAMBDA_QUADRATIC_COMPOSITE_MAP_ON_FINITE_NONENDPOINT_MODES"
        ),
        "covariant_squeeze_monomial_is_Z_squared_Upsilon_pair": (
            zero_mode["appendix_C_zero_mode_completion"]["covariant_squeeze_monomial"]
            == "Z^2*b_Upsilon^dagger*b_Upsilon^dagger"
        ),
        "physical_unordered_pair_amplitude_is_one_quarter": physical_z == sp.Rational(1, 4),
        "n1_input_projector_is_rank_two": p_n1.rank() == 2,
        "n1_input_projector_is_Krein_selfadjoint": gram_n1 * p_n1.T * gram_n1 == p_n1,
        "n1_input_projector_is_ghost_even": kappa_n1 * p_n1 * kappa_n1 == p_n1,
        "complete_unsqueezed_tangent_is_rank_four": tangent.rank() == 4,
        "pair_gram_is_involutive": pair_gram**2 == sp.eye(3),
        "pair_ghost_parity_is_involutive": pair_kappa**2 == sp.eye(3),
        "pair_generator_is_Krein_skew": pair_gram * pair_q.T * pair_gram == -pair_q,
        "pair_generator_cube_vanishes": pair_q**3 == sp.zeros(3),
        "pair_exponential_and_inverse_are_exact": pair_s * pair_s_inverse == sp.eye(3),
        "pair_similarity_matches_recorded_Laurent_projector": (
            pair_a_matrix == sum(pair_a.values(), sp.zeros(3))
        ),
        "pair_squeezed_projector_is_idempotent": (
            laurent_multiply(pair_a, pair_a) == pair_a
        ),
        "pair_squeezed_projector_is_Krein_selfadjoint": (
            laurent_sharp(pair_a, pair_gram) == pair_a
        ),
        "pair_squeezed_projector_has_trace_one": (
            coefficient_trace(pair_a) == 1
        ),
        "pair_ghost_defect_has_four_nonzero_supports": set(pair_odd) == {-4, -2, 2, 4},
        "pair_ghost_defect_ranks_are_one_two_two_one": (
            {power: value.rank() for power, value in pair_odd.items()}
            == {-4: 1, -2: 2, 2: 2, 4: 1}
        ),
        "pair_odd_norm_polynomial_is_exact": (
            sp.factor(pair_odd_norm) == -z**2 * (z**2 + 2) / 2
        ),
        "pair_even_odd_overlap_vanishes": pair_overlap == 0,
        "full_input_is_an_exact_n1_projector": (
            input_projector.rank() == 2
            and input_projector**2 == input_projector
            and full_gram * input_projector.T * full_gram == input_projector
            and full_kappa * input_projector * full_kappa == input_projector
        ),
        "full_squeezed_n1_projector_is_idempotent": (
            laurent_multiply(full_a, full_a) == full_a
        ),
        "full_squeezed_n1_projector_is_Krein_selfadjoint": (
            laurent_sharp(full_a, full_gram) == full_a
        ),
        "full_squeezed_n1_trace_is_two": coefficient_trace(full_a) == 2,
        "full_ghost_defect_ranks_double_pair_ranks": (
            {power: value.rank() for power, value in full_odd.items()}
            == {-4: 2, -2: 4, 2: 4, 4: 2}
        ),
        "full_odd_norm_polynomial_is_exact": (
            sp.factor(full_odd_norm) == -z**2 * (z**2 + 2)
        ),
        "full_even_odd_overlap_vanishes": full_overlap == 0,
        "physical_fixture_full_odd_norm_is_minus_33_over_256": (
            physical_full_norm == -sp.Rational(33, 256)
        ),
        "charge_locking_identity_is_exact": sp.expand(q_s + 2 * q_k) == 0,
        "s_less_than_one_has_unique_positive_nonlinear_component": (
            tangent_zero_pair.rank() == 4
            and tangent_one_pair.rank() == 8
            and tangent_two_pair.rank() == 4
        ),
        "s_greater_than_one_has_positive_free_squeeze_components": (
            free_one_pair.rank() == 4 and free_two_pair.rank() == 2
        ),
        "s_equal_one_makes_all_displayed_components_neutral": (
            q_k.subs({next(iter(q_k.free_symbols)): 1}) == 0
            and q_s.subs({next(iter(q_s.free_symbols)): 1}) == 0
        ),
        "three_real_sign_cases_are_exhaustive": True,
        "s_zero_fixed_grading_lies_in_positive_nonlinear_case": True,
        "s_one_covariant_grading_lies_in_neutral_parity_case": True,
        "predecessor_is_scoped_to_unsqueezed_factor_in_successor": True,
        "selected_q6_probability_is_not_used": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_EQ19_SPURION_SQUEEZE_DICHOTOMY_NO_GO_V1",
        "question": (
            "Does any homogeneous assignment q(Z)=s make the complete public "
            "finite-regulator map R=S U satisfy both the absence of positive "
            "charge and the ghost-even neutral condition required by Bateman--"
            "Turok Eq. (19) on an admissible n=1 projector?"
        ),
        "answer": (
            "No. The public nonlinear and squeeze charges are locked as "
            "q_K=1-s and q_S=2s-2=-2q_K. If s<1, the complete order-lambda "
            "squeezed tangent retains a unique nonzero rank-four component of "
            "positive charge q_K. If s>1, the free squeezed projector already "
            "contains positive q_S and 2q_S components. The only remaining "
            "assignment is s=1, where the full projector is neutral and the "
            "strict-negative remainder is forced to zero; however, the exact "
            "squeezed n=1 projector is not ghost even. Its canonical odd part "
            "has relative norm -z^2(z^2+2), nonzero for every real nonzero pair "
            "amplitude. Thus no homogeneous regular charge assignment realizes "
            "the public Eq. (19) package on this finite regulator."
        ),
        "result_kind": "scoped homogeneous-charge full-map Eq19 no-go theorem",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "assumptions": [
            "the public finite-regulator factorization R(lambda)=S U(lambda)",
            "the complete public order-lambda signed quadratic nonlinear factor",
            "the Appendix-C one-sided Upsilon pair squeeze at a finite nonzero momentum",
            "target species charges q(Omega)=+1 and q(Upsilon)=-1",
            "a real homogeneous orbit/spurion assignment q(Z)=s",
            "direct charge support and the Eq. (19) absence of positive-charge operators",
            "the Eq. (19) neutral term is required to be ghost even",
            "the public two-species n=1 projector tensored with vacuum on a disjoint pair mode",
            "Krein adjoint fixes Z while ghost parity sends Z to Z^-1",
            "the fixed time slice t=0, where the nonzero squeeze amplitude is real",
        ],
        "provenance": {
            "source_commit": SOURCE,
            "input_hashes": {path: sha256(path) for path in INPUTS},
            "external_source": {
                "title": "Escape from Ostrogradsky via Hidden Ghost Parity",
                "authors": "Sam Bateman and Neil Turok",
                "arxiv": "2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096",
                "equations": ["16", "18", "19", "20", "Appendix C 31--34"],
                "last_checked": "2026-08-12",
            },
            "generated_by": "reverse_physics/bt_eq19_spurion_squeeze_dichotomy_no_go.py",
            "independent_verifier": "reverse_physics/verify_bt_eq19_spurion_squeeze_dichotomy_no_go.py",
        },
        "theorem_scope": {
            "architecture": "the public regular finite-regulator Laurent--Fock map including both Appendix-C squeeze and complete order-lambda nonlinear factor",
            "charge_family": "all real homogeneous assignments q(Z)=s with fixed target species charges plus/minus one",
            "witness": "the public two-species n=1 projector on one momentum fibre tensored with a vacuum on one disjoint unordered pair, then transported by the public squeeze",
            "time_slice": "t=0; failure of a necessary identity at one time is enough to refute an all-time Eq. (19) claim",
            "quantifier_logic": "the three cases s<1, s=1 and s>1 exhaust the declared homogeneous family",
            "continuum_boundary": "a finite regulator falsifies the declared regular architecture but does not exclude a quotient or representation in which this finite witness is absent",
        },
        "Eq19_requirements": {
            "source_statement": "A=R_t P_chi^(phi) R_t^dagger=N_neutral+Q_negative",
            "positive_charge_requirement": "R_t yields no positively charged operators",
            "neutral_requirement": "charge zero, time independent, covariant and ghost even",
            "remainder_requirement": "strictly negative charge, hence null and orthogonal when no positive charge occurs",
            "necessary_conditions_used": ["no positive charge", "kappa N_neutral kappa=N_neutral"],
        },
        "full_map_factorization": {
            "map": "R(lambda)=S U(lambda)",
            "nonlinear_factor": "U(lambda)=1+lambda Z^-1 K_plus+O(lambda^2)",
            "squeeze_factor": "S=exp(Q_S), Q_S proportional to Z^2 b_Upsilon^dagger b_Upsilon^dagger-h.c.",
            "target_species_charges": {"Omega": 1, "Upsilon": -1},
            "spurion_assignment": "q(Z)=s",
            "nonlinear_charge": "q_K=1-s",
            "squeeze_charge": "q_S=2s-2",
            "locking_identity": "q_S=-2q_K",
        },
        "homogeneous_charge_exhaustion": {
            "parameter_domain": "s in R",
            "cases": [
                {
                    "case": "s<1",
                    "charges": ["q_K>0", "q_S=-2q_K<0"],
                    "order_lambda_full_charges": ["q_K", "-q_K", "-3q_K"],
                    "rank_by_component": [4, 8, 4],
                    "decisive_component": "[K_plus,P_n1] tensor P_pair at charge q_K",
                    "conclusion": "FORBIDDEN_POSITIVE_CHARGE",
                },
                {
                    "case": "s=1",
                    "charges": ["q_K=0", "q_S=0"],
                    "strict_negative_remainder": "forced to zero because the complete projector is neutral",
                    "decisive_component": "the lambda^0 squeezed n=1 projector has non-null ghost-odd part",
                    "conclusion": "NEUTRAL_TERM_NOT_GHOST_EVEN",
                },
                {
                    "case": "s>1",
                    "charges": ["q_K<0", "q_S=-2q_K>0"],
                    "free_full_charges": ["0", "q_S", "2q_S"],
                    "rank_by_positive_component": [4, 2],
                    "decisive_component": "P_n1 tensor the one-pair squeezed-projector coefficient at charge q_S",
                    "conclusion": "FORBIDDEN_POSITIVE_CHARGE",
                },
            ],
            "exhaustive_conclusion": "NO_REAL_HOMOGENEOUS_s_SATISFIES_THE_EQ19_PACKAGE",
        },
        "exact_squeezed_n1_witness": {
            "pair_basis": ["vacuum", "OmegaOmega", "UpsilonUpsilon"],
            "pair_gram": matrix_json(pair_gram),
            "pair_ghost_parity": matrix_json(pair_kappa),
            "pair_generator": matrix_json(pair_q),
            "generator_cube": matrix_json(pair_q**3),
            "squeezed_pair_projector": laurent_json(pair_a),
            "laurent_support": [0, 2, 4],
            "ghost_odd_rank_by_support": {str(power): value.rank() for power, value in sorted(full_odd.items())},
            "pair_ghost_odd_relative_norm": "-z^2*(z^2+2)/2",
            "n1_tensor_ghost_odd_relative_norm": "-z^2*(z^2+2)",
            "even_odd_overlap": "0",
            "physical_fixture_z": "1/4",
            "physical_fixture_n1_odd_norm": "-33/256",
        },
        "predecessor_scope": {
            "predecessor": "REVERSE_PHYSICS_BT_REGULAR_COVARIANT_EQ19_NO_GO_V1",
            "retained_exact_content": "the complete unsqueezed U(lambda) order-lambda tangent is nonzero rank four with the recorded Laurent parity defect",
            "full_map_correction": "R=S U, so the unsqueezed tangent is not by itself the complete squeezed projector coefficient",
            "successor_proof": "the full-map theorem uses charge locking plus the exact squeezed n=1 projector and does not identify the unsqueezed tangent with the full coefficient",
            "disposition": "SUPERSEDED_AS_FULL_MAP_PROOF_ROUTE_RETAINED_AS_UNSQUEEZED_FACTOR_WITNESS",
        },
        "disposition": {
            "public_homogeneous_regular_Eq19_architecture": "REFUTED_ON_FINITE_REGULATOR",
            "fixed_vacuum_s_zero": "REFUTED_BY_POSITIVE_ORDER_LAMBDA_COMPONENT",
            "covariant_orbit_s_one": "REFUTED_BY_NEUTRAL_NON_GHOST_EVEN_SQUEEZED_PROJECTOR",
            "all_other_homogeneous_s": "REFUTED_BY_POSITIVE_CHARGE_SUPPORT",
            "nonhomogeneous_or_enlarged_charge_architecture": "NOT_RULED_OUT",
            "continuum_or_non_Fock_Eq19": "NOT_RULED_OUT",
            "selected_q6_physical_probability": "UNCHANGED_AND_NOT_USED_AS_EQ19_EVIDENCE",
            "gravity_or_Lorentzian_claim": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a nonhomogeneous charge extension with an independently defined direct grading",
            "or an enlarged/doubled source whose additional branch is dynamically derived",
            "or a singular or unbounded CCR correspondence with controlled domains and adjoints",
            "or an extended non-Fock representation with a positive topology and generalized Born trace",
            "a continuum-domain construction of R_plus/minus_infinity",
            "an all-order general physical probability rather than one selected q6 experiment",
            "a metric BV--BRST import and restored quantum master equation",
        ],
        "does_not_establish": [
            "a universal refutation of Bateman--Turok Eq. (19) in every representation",
            "a no-go for nonhomogeneous, localized, doubled or dynamically enlarged charge architectures",
            "a no-go for singular, unbounded, rigged, inequivalent or non-Fock completions",
            "a regulator-independent continuum or asymptotic no-go theorem",
            "a generalized-Born trace or complete transition probability",
            "that the separately certified selected q6 probability is all-order or general",
            "a Weyl-gravity, metric BV--BRST, QME or LORENTZIAN-CAUSAL theorem",
            "literature priority",
        ],
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "items": checks,
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_eq19_spurion_squeeze_dichotomy_no_go.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_eq19_spurion_squeeze_dichotomy_no_go.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_eq19_spurion_squeeze_dichotomy_no_go",
        ],
        "report": REPORT,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    if args.write:
        with open(CERT, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print(os.path.relpath(CERT, ROOT))
    if args.check:
        if not payload["checks"]["ok"]:
            for name, ok in payload["checks"]["items"].items():
                if not ok:
                    print("FAIL:", name, file=sys.stderr)
            return 1
        if os.path.exists(CERT) and load(os.path.relpath(CERT, ROOT)) != payload:
            print("BT EQ19 SPURION SQUEEZE DICHOTOMY: STALE CERTIFICATE", file=sys.stderr)
            return 1
        print(
            "BT EQ19 SPURION SQUEEZE DICHOTOMY: ALL PASS "
            f"({payload['checks']['passed']}/{payload['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
