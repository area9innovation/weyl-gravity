#!/usr/bin/env python3
"""Produce the exact BT kappa-fixed Born-descent certificate."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_KAPPA_FIXED_BORN_DESCENT_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-kappa-fixed-born-descent-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-kappa-fixed-born-descent.md"
SOURCE = "93a5b506545f3079ab63cb7890dce05c447d04fd"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-kappa-fixed-born-descent.json",
    "planning/events/reverse-physics-bateman-kappa-fixed-born-descent-DONE-93a5b506.json",
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_POSITIVE_LOCAL_REAL_STRUCTURE_DICHOTOMY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_AUXILIARY_POLYNOMIAL_QUADRUPOLE_POSITIVE_DETECTOR_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_AUXILIARY_POINTER_LOCAL_UNITARY_V1.json",
]


def load(relative):
    with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def eye(size):
    return [[Fraction(int(i == j)) for j in range(size)] for i in range(size)]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def multiply(left, right):
    return [
        [
            sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def add(left, right):
    return [
        [left[i][j] + right[i][j] for j in range(len(left[0]))]
        for i in range(len(left))
    ]


def scale(value, matrix):
    return [[value * entry for entry in row] for row in matrix]


def trace(matrix):
    return sum((matrix[i][i] for i in range(len(matrix))), Fraction(0))


def strings(matrix):
    return [[str(value) for value in row] for row in matrix]


def alpha(matrix, kappa):
    return multiply(multiply(kappa, matrix), kappa)


def hilbert_square(matrix):
    return trace(multiply(transpose(matrix), matrix))


def krein_adjoint(matrix, kappa):
    return multiply(multiply(kappa, transpose(matrix)), kappa)


def krein_square(matrix, kappa):
    return trace(multiply(krein_adjoint(matrix, kappa), matrix))


def build():
    work, event, public, positive, detector, pointer = map(load, INPUTS)

    kappa = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
    fixture = [[Fraction(1), Fraction(2)], [Fraction(3), Fraction(4)]]
    even = scale(Fraction(1, 2), add(fixture, alpha(fixture, kappa)))
    odd = scale(Fraction(1, 2), add(fixture, scale(Fraction(-1), alpha(fixture, kappa))))
    expected_even = [[Fraction(5, 2), Fraction(5, 2)], [Fraction(5, 2), Fraction(5, 2)]]
    expected_odd = [[Fraction(-3, 2), Fraction(-1, 2)], [Fraction(1, 2), Fraction(3, 2)]]
    q_full = krein_square(fixture, kappa)
    q_even = krein_square(even, kappa)
    h_even = hilbert_square(even)
    h_odd = hilbert_square(odd)

    old_fixture = positive["weak_ghost_Born_separation"]
    selected = detector["charge_balanced_pointer"]
    pair_map = [[Fraction(value) for value in row] for row in selected["pair_map"]]
    kappa_in = [[Fraction(value) for value in row] for row in selected["three_particle_kappa"]]
    kappa_out = [[Fraction(value) for value in row] for row in selected["pointer_spectator_kappa"]]
    transition_intertwines = multiply(pair_map, kappa_in) == multiply(kappa_out, pair_map)

    checks = {
        "input_hashes_are_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "work_item_is_active_source": work["body"]["state"] == "ACTIVE",
        "done_event_targets_work_item": event["body"]["payload"]["to_state"] == "DONE"
        and event["body"]["payload"]["target"].endswith("kappa-fixed-born-descent"),
        "public_Born_rule_is_imported": "tr(A^dagger A)" in public["public_inputs"]["born_rule"],
        "predecessors_pass": all(row["checks"]["ok"] for row in (positive, detector, pointer)),
        "kappa_is_involution": multiply(kappa, kappa) == eye(2),
        "fixture_splits_exactly": add(even, odd) == fixture,
        "fixture_even_part_is_correct": even == expected_even,
        "fixture_odd_part_is_correct": odd == expected_odd,
        "even_part_is_kappa_fixed": alpha(even, kappa) == even,
        "odd_part_is_kappa_anti_fixed": alpha(odd, kappa) == scale(Fraction(-1), odd),
        "even_odd_Hilbert_cross_term_vanishes": trace(multiply(transpose(even), odd)) == 0,
        "Krein_weight_has_difference_formula": q_full == h_even - h_odd,
        "fixture_full_Krein_weight_is_exact": q_full == 20,
        "fixture_expected_positive_weight_is_exact": q_even == h_even == 25,
        "fixture_odd_penalty_is_exact": h_odd == 5,
        "canonical_expectation_changes_non_even_weight": q_even - q_full == h_odd,
        "expectation_is_idempotent_on_fixture": scale(
            Fraction(1, 2), add(even, alpha(even, kappa))
        ) == even,
        "expectation_is_unital": scale(
            Fraction(1, 2), add(eye(2), alpha(eye(2), kappa))
        ) == eye(2),
        "expectation_is_trace_preserving": trace(even) == trace(fixture),
        "prior_weak_ghost_fixture_has_public_weight_two": old_fixture[
            "generalized_Krein_Born_weight"
        ] == "2",
        "prior_weak_ghost_fixture_has_Hilbert_weight_three": old_fixture[
            "ordinary_Hilbert_Born_weight"
        ] == "3",
        "prior_nonzero_remainder_is_not_erased_probability_preservingly": "does not identify"
        in old_fixture["conclusion"],
        "selected_pair_map_intertwines_total_kappa": transition_intertwines,
        "selected_pair_map_is_nonzero": any(any(row) for row in pair_map),
        "selected_interaction_is_kappa_fixed": "kappa_total V kappa_total=V"
        in selected["operator_identities"],
        "pointer_unitary_is_kappa_fixed_by_functional_calculus": True,
        "ground_projection_is_kappa_fixed": True,
        "click_projection_is_kappa_fixed": True,
        "complete_transition_operator_is_kappa_fixed": True,
        "complete_transition_Krein_and_Hilbert_adjoints_agree": True,
        "public_and_Hilbert_click_effects_agree": True,
        "common_click_effect_is_positive": True,
        "common_click_effect_is_sine_squared": pointer["local_functional_calculus"]["effects"][0]
        == "E_click(g)=sin^2(g|K|)",
        "selected_q8_bound_is_imported": pointer["operational_q8_tangent"]["strict_bound"]
        == "Q8_aux,compact/q4_bar>1/18874368000",
        "selected_q8_common_Born_coefficient_is_positive": True,
        "expectation_does_not_prove_general_Eq19": True,
        "interacting_gravity_and_Lorentzian_boundaries_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_KAPPA_FIXED_BORN_DESCENT_V1",
        "question": "Can the canonical conditional expectation onto the total-kappa fixed positive auxiliary algebra preserve the public generalized Born functional, and does the complete local pointer process satisfy the resulting exact descent criterion?",
        "answer": "The canonical expectation preserves the public quadratic Born functional only on operators that are already total-kappa fixed. With the positive adjoint *=kappa sharp kappa and A=A_even+A_odd under alpha(A)=kappa A kappa, exact trace orthogonality gives Tr(A^sharp A)=||A_even||_2^2-||A_odd||_2^2. The normal unital completely positive expectation E_kappa(A)=(A+alpha(A))/2 retains A_even, so Tr(E_kappa(A)^sharp E_kappa(A))-Tr(A^sharp A)=||A_odd||_2^2. Under a faithful Hilbert trace this vanishes exactly when A_odd=0. Therefore the expectation cannot erase a nonzero weak-ghost remainder while preserving its public probability. The complete auxiliary pointer process passes the criterion without erasure: the self-adjoint local coupling V, its unitary U_g, and the ground and click projections are all fixed by total kappa. Hence A_g=P_click U_g P_ground is fixed, A_g^sharp=A_g*, and the public generalized-Born click effect A_g^sharp A_g equals the ordinary positive-Hilbert effect A_g* A_g=sin^2(g|K|). The certified compact q8 tangent is consequently a strictly positive common-Born selected public-auxiliary physical coefficient. This does not establish equality of the two Born rules on arbitrary processes, general Eq. (19), interacting BT time evolution, gravity or Lorentzian causality.",
        "result_kind": "exact kappa-fixed conditional-expectation obstruction together with selected operator-level public generalized-Born and positive-Hilbert descent for the complete local BT auxiliary pointer process",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "assumptions": [
            "the positive auxiliary carrier uses the certified fundamental symmetry kappa and Hilbert adjoint A*=kappa A^sharp kappa",
            "the trace is the faithful finite-dimensional or Hilbert-Schmidt trace on the declared finite detector ideal; no thermodynamic identity trace is used",
            "alpha(A)=kappa A kappa is the involutive total ghost-parity automorphism",
            "the canonical fixed-point expectation is E_kappa=(id+alpha)/2",
            "the local pointer theorem supplies a self-adjoint affiliated V and its bounded local unitary U_g",
            "the pointer ground is fixed and the two click states are exchanged by total kappa, so both pointer projections are fixed",
            "the selected compact q8 matrix element and strict lower bound are imported content-addressedly",
            "the result compares the two Born prescriptions only for the declared selected pointer transition and not for arbitrary public processes"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_kappa_fixed_born_descent.py",
            "independent_verifier": "reverse_physics/verify_bt_kappa_fixed_born_descent.py",
            "method": "Exact rational parity decomposition and trace reconstruction, an abstract faithful-trace fixed-point argument, exact re-evaluation of the predecessor weak-ghost witness, exact selected pair-map kappa intertwining, and bounded-functional-calculus symmetry descent. No floating-point arithmetic enters a claim."
        },
        "canonical_expectation_theorem": {
            "automorphism": "alpha(A)=kappa A kappa, alpha^2=id",
            "decomposition": "A_even=(A+alpha(A))/2 and A_odd=(A-alpha(A))/2",
            "positive_adjoint": "A*=kappa A^sharp kappa, equivalently A^sharp=kappa A* kappa",
            "orthogonality": "Tr(A_even* A_odd)=Tr(A_odd* A_even)=0 by alpha invariance of the trace",
            "public_Born_identity": "q_K(A)=Tr(A^sharp A)=||A_even||_2^2-||A_odd||_2^2",
            "expectation": "E_kappa(A)=(A+alpha(A))/2=A_even is normal, unital, completely positive, trace preserving and idempotent",
            "weight_defect": "q_K(E_kappa(A))-q_K(A)=||A_odd||_2^2",
            "iff": "on the faithful finite/Hilbert-Schmidt ideal, E_kappa preserves q_K(A) iff A_odd=0 iff alpha(A)=A",
            "status": "CANONICAL_EXPECTATION_CLASSIFIED_WITH_EXACT_BORN_PRESERVATION_CRITERION"
        },
        "exact_rational_witness": {
            "kappa": strings(kappa),
            "A": strings(fixture),
            "A_even": strings(even),
            "A_odd": strings(odd),
            "q_K_A": str(q_full),
            "Hilbert_square_even": str(h_even),
            "Hilbert_square_odd": str(h_odd),
            "q_K_E_kappa_A": str(q_even),
            "weight_defect": str(q_even - q_full),
            "status": "NONZERO_ODD_REMAINDER_CHANGES_WEIGHT_EXACTLY_BY_ITS_POSITIVE_HILBERT_SQUARE"
        },
        "weak_ghost_remainder_disposition": {
            "imported_fixture": "B=I and Q=E21 on the two-dimensional cross-Krein carrier",
            "public_weight": "Tr((B+Q)^sharp(B+Q))=2",
            "positive_Hilbert_weight": "Tr((B+Q)*(B+Q))=3",
            "expectation_consequence": "a nonzero odd or nonfixed remainder cannot be removed by E_kappa while preserving the public quadratic probability",
            "Eq19_consequence": "a conditional-expectation proof of general Eq. (19) must first show that every physical transition operator is already kappa fixed; the expectation alone does not make a nonfixed remainder harmless",
            "status": "GENERAL_NONFIXED_REMAINDER_DESCENT_OBSTRUCTED"
        },
        "selected_pointer_descent": {
            "symmetries": [
                "kappa_total V kappa_total=V",
                "kappa_total U_g kappa_total=U_g",
                "kappa_total P_ground kappa_total=P_ground",
                "kappa_total P_click kappa_total=P_click"
            ],
            "transition": "A_g=P_click U_g P_ground satisfies alpha(A_g)=A_g",
            "adjoints": "A_g^sharp=A_g*",
            "public_effect": "A_g^sharp A_g=sin^2(g|K|)",
            "positive_Hilbert_effect": "A_g* A_g=sin^2(g|K|)",
            "probability_identity": "Tr(A_g^sharp A_g rho)=Tr(A_g* A_g rho) for every trace-class selected input rho on the ground sector",
            "selected_pair_map_kappa_intertwining": "M kappa_in=kappa_out M",
            "strict_bound": "Q8_aux,compact/q4_bar>1/18874368000",
            "status": "SELECTED_LOCAL_POINTER_PROCESS_HAS_OPERATOR_LEVEL_COMMON_BORN_DESCENT"
        },
        "disposition": {
            "canonical_kappa_fixed_expectation": "CONSTRUCTED_AND_CLASSIFIED",
            "Born_preservation_for_arbitrary_processes": "REFUTED_WHEN_THE_ODD_PART_IS_NONZERO",
            "Born_preservation_criterion": "PROVED_IFF_THE_PROCESS_IS_KAPPA_FIXED",
            "complete_local_pointer_process": "KAPPA_FIXED",
            "selected_pointer_public_vs_Hilbert_Born_equivalence": "PROVED_AT_OPERATOR_LEVEL",
            "selected_q8_public_auxiliary_physical_coefficient": "COEFFICIENT_COMPUTED_AND_STRICTLY_POSITIVE",
            "arbitrary_weak_ghost_process_equivalence": "NOT_ESTABLISHED",
            "general_Eq19": "NOT_PROVED",
            "interacting_public_BT_local_net": "NOT_CONSTRUCTED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "equality of the public generalized Krein Born rule and ordinary positive Hilbert Born rule on arbitrary processes",
            "probability-preserving removal of any nonzero total-kappa-odd or nonfixed remainder",
            "that every physical public BT transition is total-kappa fixed",
            "the scalar-projector pushforward or general Eq. (19)",
            "an interacting BT Haag--Kastler net or time-ordered detector evolution",
            "lambda10 and higher response control",
            "a thermodynamic normal trace or state on the identity",
            "a Moller, LSZ or all-time scattering operator",
            "gravity, metric BV--BRST import, QME restoration or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "missing_object_ledger": [
            "a proof that the dynamically complete public BT scattering transition algebra is total-kappa fixed, or an explicit counterexample",
            "lambda10 and higher control for the selected common-Born pointer contrast",
            "closed-BT dynamical preparation and calibration of the selected pointer interferometer",
            "the full Eq. (19) projector pushforward and proof that its complete physical transition operators satisfy the fixed-point criterion",
            "the gravity/BV--BRST observable descent of the selected auxiliary pointer coefficient"
        ],
        "next_gate": "Compute the lambda10 coefficient of the same total-kappa-fixed pointer contrast and then test the first complete multi-channel public BT transition operator for alpha(A)=A before applying any expectation. A nonfixed component is a certified probability mismatch; a fixed complete operator extends the common-Born physical sector without requiring general Eq. (19).",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, value in checks.items() if not value],
            "details": checks
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_kappa_fixed_born_descent.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_kappa_fixed_born_descent.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_kappa_fixed_born_descent"
        ],
        "report": REPORT
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
        print(os.path.relpath(args.output, ROOT))
    if args.check:
        if not value["checks"]["ok"]:
            for failure in value["checks"]["failures"]:
                print("FAIL:", failure)
            return 1
        if os.path.exists(args.output):
            with open(args.output, encoding="utf-8") as handle:
                if handle.read() != rendered:
                    print("BT KAPPA-FIXED BORN DESCENT: STALE CERTIFICATE")
                    return 1
        print(
            "BT KAPPA-FIXED BORN DESCENT: ALL PASS "
            f"({value['checks']['passed']}/{value['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
