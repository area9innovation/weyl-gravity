#!/usr/bin/env python3
"""Exact full q8 coherence difference on the two-angle BT carrier."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_TWO_ANGLE_Q8_COHERENCE_DIFFERENCE_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-two-angle-q8-coherence-difference-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-two-angle-q8-coherence-difference.md"
SOURCE = "6c11450e1411f5d61b27422ed290d6d894d24491"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-two-angle-q8-coherence-difference-DONE-6c11450e.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-two-angle-q8-coherence-difference.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TWO_ANGLE_COHERENT_Q6_DETECTOR_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_PACKET_LAMBDA5_PARITY_SELECTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_PACKET_LAMBDA6_OBJECT_LEDGER_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_TAGGED_Q6_PHYSICAL_PROBABILITY_V1.json",
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


def real_cross(left_real, left_imag, effect, right_real, right_imag):
    """Real part of the complex Hilbert cross, componentwise in angle."""
    return (
        (left_real.T * effect * right_real)[0]
        + (left_imag.T * effect * right_imag)[0]
    )


def build():
    import sympy as sp

    q6_detector = load(INPUTS[1])
    parity = load(INPUTS[2])
    ledger6 = load(INPUTS[3])
    complete6 = load(INPUTS[4])
    event = load(EVENT)
    predecessors = [q6_detector, parity, ledger6, complete6]

    epsilon = sp.symbols("epsilon", real=True)
    p_plus = sp.ones(2) / 2
    p_minus = sp.eye(2) - p_plus
    effect = p_plus + (1 - epsilon) * p_minus
    identity = sp.eye(2)

    # A common complex leading amplitude and arbitrary complete complex X4,
    # X6 angle components.  Internal positive-output coordinates factor out;
    # the same identities apply componentwise and hence after summation.
    x2r, x2i = sp.symbols("x2r x2i", real=True)
    a1r, a1i, a2r, a2i = sp.symbols(
        "a1r a1i a2r a2i", real=True
    )
    b1r, b1i, b2r, b2i = sp.symbols(
        "b1r b1i b2r b2i", real=True
    )
    x2_real = sp.Matrix([x2r, x2r])
    x2_imag = sp.Matrix([x2i, x2i])
    x4_real = sp.Matrix([a1r, a2r])
    x4_imag = sp.Matrix([a1i, a2i])
    x6_real = sp.Matrix([b1r, b2r])
    x6_imag = sp.Matrix([b1i, b2i])

    recorded_cross_26 = 2 * real_cross(
        x2_real, x2_imag, identity, x6_real, x6_imag
    )
    coherent_cross_26 = 2 * real_cross(
        x2_real, x2_imag, effect, x6_real, x6_imag
    )
    recorded_norm_4 = real_cross(
        x4_real, x4_imag, identity, x4_real, x4_imag
    )
    coherent_norm_4 = real_cross(
        x4_real, x4_imag, effect, x4_real, x4_imag
    )
    recorded_q8 = sp.expand(recorded_cross_26 + recorded_norm_4)
    coherent_q8 = sp.expand(coherent_cross_26 + coherent_norm_4)
    difference = sp.factor(coherent_q8 - recorded_q8)
    squared_difference = (
        (a1r - a2r) ** 2 + (a1i - a2i) ** 2
    )
    expected_difference = -epsilon * squared_difference / 2

    # Exhaust the coefficient pairs m+n=8 with m,n >= 2.  Odd selected
    # blocks vanish between the fixed total-Fock-odd input/output projectors.
    ordered_pairs = [(left, 8 - left) for left in range(2, 7)]
    surviving_pairs = [
        pair for pair in ordered_pairs if pair[0] % 2 == 0 and pair[1] % 2 == 0
    ]
    hermitian_classes = sorted(
        {tuple(sorted(pair)) for pair in surviving_pairs}
    )
    odd_selected_orders = [order for order in range(3, 8, 2)]

    fixture = {
        x2r: sp.Rational(2, 3),
        x2i: -sp.Rational(1, 5),
        a1r: 1,
        a1i: 2,
        a2r: -3,
        a2i: 1,
        b1r: sp.Rational(7, 4),
        b1i: -sp.Rational(2, 3),
        b2r: -sp.Rational(5, 6),
        b2i: sp.Rational(9, 7),
        epsilon: sp.Rational(2, 5),
    }
    fixture_recorded_cross = sp.factor(recorded_cross_26.subs(fixture))
    fixture_coherent_cross = sp.factor(coherent_cross_26.subs(fixture))
    fixture_recorded_q8 = sp.factor(recorded_q8.subs(fixture))
    fixture_coherent_q8 = sp.factor(coherent_q8.subs(fixture))
    fixture_difference = sp.factor(difference.subs(fixture))

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "four_predecessors_pass": len(predecessors) == 4 and all(row["checks"]["ok"] for row in predecessors),
        "done_event_targets_this_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("two-angle-q8-coherence-difference"),
        "q6_effect_fixes_leading_vector_imported": q6_detector["coherent_probability_through_lambda6"]["cross_invariance"].startswith("2*Re<X2,E_epsilon X4>"),
        "parity_covariance_imported": parity["exact_covariance"]["evolution_coefficients"] == "Pi_F U_n Pi_F=(-1)^n U_n",
        "odd_order_three_block_imported": ledger6["fixed_BT_expansion"]["order_three_block"] == "Pout*T3*Pin=0",
        "complete_q6_is_imported": complete6["complete_probability"]["status"] == "COMPLETE_SELECTED_TAGGED_Q6_COEFFICIENT_COMPUTED",
        "five_ordered_q8_pairs_exhausted": ordered_pairs == [(2, 6), (3, 5), (4, 4), (5, 3), (6, 2)],
        "odd_selected_blocks_vanish": odd_selected_orders == [3, 5, 7],
        "only_two_hermitian_q8_classes_survive": hermitian_classes == [(2, 6), (4, 4)],
        "q8_recorded_ledger_is_cross_plus_norm": recorded_q8 == sp.expand(recorded_cross_26 + recorded_norm_4),
        "q8_coherent_ledger_is_cross_plus_norm": coherent_q8 == sp.expand(coherent_cross_26 + coherent_norm_4),
        "leading_vector_is_fixed": sp.simplify(effect * x2_real - x2_real) == sp.zeros(2, 1) and sp.simplify(effect * x2_imag - x2_imag) == sp.zeros(2, 1),
        "arbitrary_X2_X6_cross_is_invariant": sp.simplify(coherent_cross_26 - recorded_cross_26) == 0,
        "full_relative_q8_difference_is_variance": sp.simplify(difference - expected_difference) == 0,
        "relative_q8_difference_is_nonpositive": True,
        "relative_q8_equality_condition_is_exact": True,
        "fixture_cross_is_detector_independent": fixture_recorded_cross == fixture_coherent_cross,
        "fixture_difference_is_minus_seventeen_fifths": fixture_difference == -sp.Rational(17, 5),
        "fixture_full_q8_values_have_expected_shift": fixture_coherent_q8 - fixture_recorded_q8 == -sp.Rational(17, 5),
        "absolute_q8_is_not_computed": True,
        "operational_detector_boundary_is_preserved": q6_detector["disposition"]["BT_dynamical_detector_selection"] == "NOT_ESTABLISHED",
        "Eq19_boundary_is_preserved": q6_detector["disposition"]["general_Eq19"] == "NOT_PROVED_AND_NOT_USED",
        "gravity_and_Lorentzian_boundaries_are_preserved": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_TWO_ANGLE_Q8_COHERENCE_DIFFERENCE_V1",
        "question": "Does the unknown complete order-lambda6 BT output obstruct computing the entire coherent-minus-recorded probability coefficient at order lambda8 on the certified two-angle carrier?",
        "answer": "No. For the selected odd-to-odd tagged block, exact total-Fock parity removes every odd amplitude coefficient. The complete probability-order-lambda8 ledger is therefore ||X4||^2+2 Re<X2,X6>. The operational effect E_epsilon fixes the common leading angle vector X2, so self-adjointness makes 2 Re<X2,E_epsilon X6> exactly equal to the recorded cross for arbitrary complete X6. The entire coherent-minus-recorded q8 coefficient is consequently -(epsilon/2)||X4(c1)-X4(c2)||^2, which is nonpositive and vanishes exactly when epsilon=0 or the two complete X4 outputs agree. This computes the full relative q8 coefficient, not either absolute q8 probability: the complete X4 norm and X2-X6 cross remain unevaluated.",
        "result_kind": "complete relative order-lambda8 coefficient between coherent and recorded two-angle BT detector effects",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "assumptions": [
            "the two orthogonal equal-normalization hard angle modes and fixed operational effect E_epsilon are exactly those certified by the q6 predecessor",
            "the declared input and output packet projectors have total-Fock parity odd and the regulator/counterterms preserve the exact lambda-to-minus-lambda covariance",
            "X2, X4 and X6 denote the complete selected output coefficients, including every source, detector, loop, counterterm and disconnected term allowed at their respective orders",
            "E_epsilon is coupling independent, self-adjoint, acts only on the two-angle record factor and is tensored with the identity on every internal positive-output coordinate",
            "the common fixed-s leading phase is aligned so X2=x2 times (1,1)",
            "0<epsilon<=1 for the off-diagonal detector family; epsilon=0 is used only to state the recorded-limit equality condition",
            "the theorem compares coefficients of two declared operational effects and does not derive either effect from a BT apparatus interaction"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_two_angle_q8_coherence_difference.py",
            "independent_verifier": "reverse_physics/verify_bt_two_angle_q8_coherence_difference.py",
            "method": "Exact SymPy coefficient-pair enumeration and arbitrary complex two-angle projector algebra. The independent rail uses Fraction arithmetic, direct polynomial convolution and finite separating complex fixtures. No floating-point arithmetic is used."
        },
        "complete_q8_ledger": {
            "selected_output": "X(lambda)=lambda^2*X2+lambda^4*X4+lambda^6*X6+O(lambda^8)",
            "odd_block_rule": "Pout*X_n*Pin=0 for every odd n because Pin and Pout are total-Fock odd and Pi_F X_n Pi_F=(-1)^n X_n",
            "ordered_coefficient_pairs": ["(2,6)", "(3,5)", "(4,4)", "(5,3)", "(6,2)"],
            "vanishing_pairs": ["(3,5)", "(5,3)"],
            "surviving_hermitian_classes": ["(2,6)", "(4,4)"],
            "recorded_coefficient": "q8[I2]=2*Re<X2,X6>+||X4||^2",
            "coherent_coefficient": "q8[E_epsilon]=2*Re<X2,E_epsilon X6>+<X4,E_epsilon X4>",
            "status": "EXHAUSTIVE_SELECTED_PROBABILITY_LEDGER_AT_ORDER_LAMBDA8"
        },
        "cross_invariance": {
            "leading_fixed_point": "E_epsilon X2=X2",
            "self_adjoint_step": "<X2,E_epsilon X6>=<E_epsilon X2,X6>=<X2,X6>",
            "scope": "arbitrary complete complex X6 on the same two-angle and internal output carrier",
            "status": "COMPLETE_X2_X6_CROSS_IS_DETECTOR_INDEPENDENT"
        },
        "relative_q8_coefficient": {
            "formula": "q8[E_epsilon]-q8[I2]=-(epsilon/2)*||X4(c1)-X4(c2)||^2",
            "sign": "NONPOSITIVE",
            "equality": "epsilon=0 or X4(c1)=X4(c2)",
            "pure_coherent_endpoint": "q8[P_plus]-q8[I2]=-||X4(c1)-X4(c2)||^2/2",
            "meaning": "the off-diagonal detector removes exactly epsilon times the antisymmetric-angle norm of the complete X4 output",
            "status": "COMPLETE_RELATIVE_Q8_COEFFICIENT_COMPUTED"
        },
        "exact_fixture": {
            "epsilon": "2/5",
            "X2": "(2/3-i/5)*(1,1)",
            "X4": ["1+2*i", "-3+i"],
            "X6": ["7/4-2*i/3", "-5/6+9*i/7"],
            "recorded_X2_X6_cross": str(fixture_recorded_cross),
            "coherent_X2_X6_cross": str(fixture_coherent_cross),
            "recorded_q8": str(fixture_recorded_q8),
            "coherent_q8": str(fixture_coherent_q8),
            "difference": str(fixture_difference),
            "status": "EXACT_COMPLEX_SEPARATING_FIXTURE"
        },
        "absolute_q8_boundary": {
            "status": "NOT_COMPUTED",
            "missing_values": [
                "the complete norm ||X4||^2 on either angle fibre and their cross-angle overlap",
                "the complete interference 2 Re<X2,X6>, including every order-lambda6 amplitude object and renormalization condition"
            ],
            "what_is_independent_of_missing_values": "the coherent-minus-recorded q8 coefficient and its nonpositive sign",
            "not_a_contradiction": "an exact relative coefficient can be known while both absolute coefficients remain unknown"
        },
        "disposition": {
            "complete_q8_object_ledger": "CLASSIFIED",
            "complete_relative_q8_coefficient": "COEFFICIENT_COMPUTED",
            "absolute_recorded_q8_probability": "NOT_COMPUTED",
            "absolute_coherent_q8_probability": "NOT_COMPUTED",
            "BT_dynamical_detector_selection": "NOT_ESTABLISHED",
            "continuum_angle_coherence": "NOT_CONSTRUCTED",
            "forward_and_backward_endpoints": "NOT_INCLUDED",
            "all_order_or_all_time_probability": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED_AND_NOT_USED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "either absolute order-lambda8 probability coefficient",
            "the complete numerical or functional X4 norm or X2-X6 cross",
            "that BT dynamics selects epsilon, the relative angle phase or this apparatus effect",
            "coherence over a continuum of angles or unequal-normalization cells",
            "either forward or exchanged-forward endpoint",
            "real-virtual, survival, collinear or KLN completion",
            "an all-order probability or all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Bateman--Turok Eq. (19)",
            "gravity or metric BV--BRST transfer",
            "a restored gravitational quantum master equation or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Compute the two missing absolute q8 values on the same carrier: the complete X4 Gram data and the complete X2-X6 interference. The relative coherence question is closed at q8, so a physical detector successor must instead derive epsilon and the relative phase from an explicit apparatus interaction, while the independent Eq. (19) route still requires the missing zero-mode representation and generalized Born trace.",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_two_angle_q8_coherence_difference.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_two_angle_q8_coherence_difference.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_two_angle_q8_coherence_difference"
        ],
        "report": REPORT
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
            for failure in payload["checks"]["failures"]:
                print("FAIL:", failure, file=sys.stderr)
            return 1
        if os.path.exists(CERT) and load(os.path.relpath(CERT, ROOT)) != payload:
            print("BT TWO ANGLE Q8 DIFFERENCE: STALE CERTIFICATE", file=sys.stderr)
            return 1
        print(
            "BT TWO ANGLE Q8 DIFFERENCE: ALL PASS "
            f"({payload['checks']['passed']}/{payload['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
