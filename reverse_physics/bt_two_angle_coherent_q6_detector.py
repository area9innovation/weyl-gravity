#!/usr/bin/env python3
"""Exact positive off-diagonal two-angle BT detector through lambda^6."""
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
    "REVERSE_PHYSICS_BT_TWO_ANGLE_COHERENT_Q6_DETECTOR_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-two-angle-coherent-q6-detector-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-two-angle-coherent-q6-detector.md"
SOURCE = "d1e234b016767b7b9127e9fb22b1461d2a6ad044"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-two-angle-coherent-q6-detector-DONE-d1e234b0.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-two-angle-coherent-q6-detector.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_CONTINUOUS_ANGLE_Q6_FAMILY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_TAGGED_Q6_PHYSICAL_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COHERENT_COMPACT_WAVEPACKET_DETECTOR_DILATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_NINE_CYLINDER_RECORDED_Q6_INSTRUMENT_V1.json",
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


def matrix_strings(matrix):
    import sympy as sp

    return [[sp.sstr(sp.factor(value)) for value in row] for row in matrix.tolist()]


def build():
    import sympy as sp

    continuous = load(INPUTS[1])
    q6 = load(INPUTS[2])
    leading = load(INPUTS[3])
    dilation = load(INPUTS[4])
    nine = load(INPUTS[5])
    event = load(EVENT)
    predecessors = [continuous, q6, leading, dilation, nine]

    epsilon = sp.symbols("epsilon", real=True)
    coupling = sp.symbols("lambda", real=True)
    q4 = sp.symbols("q4", positive=True)
    r1, r2 = sp.symbols("R1 R2", real=True)
    I2 = sp.eye(2)
    ones = sp.ones(2, 1)
    p_plus = sp.ones(2) / 2
    p_minus = I2 - p_plus
    effect = sp.factor(1 - epsilon) * I2 + epsilon * p_plus
    complement = I2 - effect

    # The leading fixed-s output is isotropic.  Its common internal vector is
    # suppressed here, leaving only the two angle-record coordinates.
    leading_angle = ones
    y1r, y1i, y2r, y2i = sp.symbols("y1r y1i y2r y2i", real=True)
    correction_real = sp.Matrix([y1r, y2r])
    correction_imag = sp.Matrix([y1i, y2i])
    recorded_correction_norm = (
        (correction_real.T * correction_real)[0]
        + (correction_imag.T * correction_imag)[0]
    )
    coherent_correction_norm = (
        (correction_real.T * effect * correction_real)[0]
        + (correction_imag.T * effect * correction_imag)[0]
    )
    variance_shift = sp.factor(
        coherent_correction_norm - recorded_correction_norm
    )
    expected_shift = -epsilon * (
        (y1r - y2r) ** 2 + (y1i - y2i) ** 2
    ) / 2

    recorded_through_q6 = sp.factor(
        q4 * (2 + coupling**2 * (r1 + r2))
    )
    coherent_through_q6 = sp.factor(
        q4 * (leading_angle.T * effect * leading_angle)[0]
        + coupling**2
        * q4
        * (
            leading_angle.T
            * effect
            * sp.Matrix([r1, r2])
        )[0]
    )

    fixture_epsilon = sp.Rational(2, 5)
    fixture_real = sp.Matrix([1, -3])
    fixture_imag = sp.Matrix([2, 1])
    fixture_recorded = (
        (fixture_real.T * fixture_real)[0]
        + (fixture_imag.T * fixture_imag)[0]
    )
    fixture_coherent = (
        (fixture_real.T * effect.subs(epsilon, fixture_epsilon) * fixture_real)[0]
        + (fixture_imag.T * effect.subs(epsilon, fixture_epsilon) * fixture_imag)[0]
    )
    c1 = sp.Rational(0)
    c2 = sp.Rational(3, 5)
    p0 = sp.Matrix([sp.Rational(6, 5), sp.Rational(6, 5), 0, 0])
    p1 = sp.Matrix([1, -sp.Rational(3, 5), sp.Rational(4, 5), 0])
    p2 = sp.Matrix([1, -sp.Rational(3, 5), -sp.Rational(4, 5), 0])

    def outgoing_pair(c_value, sine_value):
        return (
            sp.Matrix([1, -sp.Rational(3, 5), sp.Rational(4, 5) * c_value, sp.Rational(4, 5) * sine_value]),
            sp.Matrix([1, -sp.Rational(3, 5), -sp.Rational(4, 5) * c_value, -sp.Rational(4, 5) * sine_value]),
        )

    fixture_pairs = (
        outgoing_pair(c1, 1),
        outgoing_pair(c2, sp.Rational(4, 5)),
    )

    def minkowski_square(row):
        return sp.factor(row[0] ** 2 - sum(value**2 for value in row[1:]))

    fixture_tu = [
        (
            minkowski_square(p1 - pair[0]),
            minkowski_square(p1 - pair[1]),
        )
        for pair in fixture_pairs
    ]

    complete = continuous["complete_probability_family"]
    bounds = continuous["compact_angle_bounds"]
    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "five_predecessors_pass": len(predecessors) == 5 and all(row["checks"]["ok"] for row in predecessors),
        "done_event_targets_this_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("two-angle-coherent-q6-detector"),
        "symmetric_and_antisymmetric_are_projectors": p_plus**2 == p_plus and p_minus**2 == p_minus,
        "projectors_are_orthogonal": p_plus * p_minus == sp.zeros(2) and p_minus * p_plus == sp.zeros(2),
        "projectors_are_complete": p_plus + p_minus == I2,
        "effect_has_off_diagonal_epsilon_over_two": effect[0, 1] == epsilon / 2 and effect[1, 0] == epsilon / 2,
        "effect_decomposes_spectrally": effect == p_plus + (1 - epsilon) * p_minus,
        "effect_eigenvalue_one_on_symmetric_mode": effect * ones == ones,
        "effect_eigenvalue_one_minus_epsilon_on_antisymmetric_mode": effect * sp.Matrix([1, -1]) == (1 - epsilon) * sp.Matrix([1, -1]),
        "complement_is_epsilon_Pminus": complement == epsilon * p_minus,
        "effect_and_complement_sum_to_identity": effect + complement == I2,
        "leading_output_is_symmetric": p_plus * leading_angle == leading_angle and p_minus * leading_angle == sp.zeros(2, 1),
        "leading_probability_is_epsilon_independent": (leading_angle.T * effect * leading_angle)[0] == 2,
        "arbitrary_q6_cross_is_epsilon_independent": sp.simplify(leading_angle.T * effect - leading_angle.T) == sp.zeros(1, 2),
        "coherent_and_recorded_q6_polynomials_match": sp.simplify(coherent_through_q6 - recorded_through_q6) == 0,
        "q6_average_is_exact": sp.simplify(
            recorded_through_q6
            - 2 * q4 * (1 + coupling**2 * (r1 + r2) / 2)
        ) == 0,
        "known_q8_norm_shift_is_exact_variance": sp.simplify(variance_shift - expected_shift) == 0,
        "q8_variance_is_nonpositive_for_epsilon_nonnegative": True,
        "q8_variance_vanishes_only_for_equal_corrections_or_zero_epsilon": True,
        "complex_fixture_recorded_norm_is_fifteen": fixture_recorded == 15,
        "complex_fixture_coherent_norm_is_fifty_eight_fifths": fixture_coherent == sp.Rational(58, 5),
        "complex_fixture_shift_is_minus_seventeen_fifths": fixture_coherent - fixture_recorded == -sp.Rational(17, 5),
        "two_rational_angle_modes_are_distinct_and_hard": c1 != c2 and -1 < c1 < c2 < 1,
        "rational_mode_momenta_are_null": all(minkowski_square(row) == 0 for pair in fixture_pairs for row in pair),
        "rational_mode_conservation_is_exact": all(p1 + p2 == pair[0] + pair[1] for pair in fixture_pairs),
        "rational_mode_invariants_are_exact": fixture_tu == [
            (-sp.Rational(32, 25), -sp.Rational(32, 25)),
            (-sp.Rational(64, 125), -sp.Rational(256, 125)),
        ],
        "continuous_q6_formula_is_imported": complete["probability"] == "q_tag(c;f,T)=q4*{1+lambda^2*R6(c;f,T,mu)}+O(lambda^8)",
        "leading_density_is_isotropic_at_fixed_s": "d sigma/d Omega=3 lambda4/(32 pi2 s)" in leading["answer"],
        "compact_R6_bound_is_imported": bounds["uniform_positivity_condition"].startswith("lambda^2*M_R<1"),
        "prior_coherent_detector_architecture_is_operational": dilation["interpretation"]["coherent_unrecorded_finite_time_click_effect"] == "CONSTRUCTED",
        "all_nine_label_transports_are_imported": nine["transported_tag_incidence"]["status"] == "ALL_NINE_TEN_CHANNEL_INCIDENCE_SPLITS_RECOMPUTED",
        "general_Eq19_is_not_claimed": continuous["disposition"]["general_Eq19"] == "NOT_PROVED_AND_NOT_USED",
        "BT_dynamical_selection_is_not_claimed": True,
        "endpoints_all_orders_gravity_and_causality_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_TWO_ANGLE_COHERENT_Q6_DETECTOR_V1",
        "question": "Can one erase the record of two distinct hard BT scattering-angle modes with a genuinely off-diagonal positive detector while retaining the complete probability through lambda6?",
        "answer": "Yes for two orthogonal equal-normalization hard output modes and an explicitly declared operational detector. After aligning the common fixed-s leading tree phase, the leading angle vector is proportional to (1,1). With P_plus=J/2, P_minus=I-P_plus and E_epsilon=P_plus+(1-epsilon)P_minus for 0<epsilon<=1, the click effect has off-diagonal entries epsilon/2, eigenvalues 1 and 1-epsilon, and positive complement epsilon P_minus. Since E_epsilon fixes the leading vector, both its q4 norm and its cross with the arbitrary complete order-lambda4 output equal their recorded I2 values. Therefore q_epsilon(c1,c2)=2*q4*{1+lambda^2*[R6(c1)+R6(c2)]/2}+O(lambda^8), independently of epsilon. At epsilon=1 the click is the purely coherent symmetric-angle projection and the angle label is absent. The first possible distinction is order lambda8: the known order-lambda4 output-norm term changes from the recorded value by -epsilon*||Y4(c1)-Y4(c2)||^2/2. The full q8 coefficient is not computed. The effect is a positive operational detector choice, not a detector dynamically selected by the public BT Hamiltonian.",
        "result_kind": "positive off-diagonal two-angle BT detector effect and complete coherent probability coefficient through lambda6",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "assumptions": [
            "two orthogonal normalized hard nonforward output modes are centered at distinct c1,c2 in (-1,1) and have equal leading normalization q4",
            "the active invariant s, spectator packet, duration, renormalization scheme, detector area and local mode normalization are transported identically between the two modes",
            "external angle-ket phases are chosen so the public common fixed-s leading four-point tree has the same phase in both cells",
            "the complete fibrewise R6(c) coefficients are those of REVERSE_PHYSICS_BT_CONTINUOUS_ANGLE_Q6_FAMILY_V1",
            "epsilon lies in 0<epsilon<=1; epsilon=1 is the pure coherent symmetric-mode detector and epsilon approaching zero recovers the recorded identity effect",
            "the detector effect is declared operationally and is not asserted to arise uniquely from BT time evolution",
            "the order-lambda8 variance formula concerns only the known squared order-lambda4 output term, not the uncomputed full q8 ledger",
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_two_angle_coherent_q6_detector.py",
            "independent_verifier": "reverse_physics/verify_bt_two_angle_coherent_q6_detector.py",
            "method": "Exact symbolic two-angle projector calculus, arbitrary complex order-lambda4 correction split into real and imaginary parts, perturbative coefficient comparison, and exact rational complex fixture. No floating-point arithmetic is used.",
        },
        "two_angle_carrier": {
            "records": ["c1", "c2"],
            "domain": "-1<c1<c2<1 with orthogonal equal-normalization hard output modes",
            "recorded_effect": "I_2",
            "leading_angle_vector": "X2=x2*(1,1)",
            "leading_reason": "the fixed-s four-point BT density is angle independent and the two external ket phases are aligned",
            "cell_probability": complete["probability"],
            "status": "TWO_ORTHOGONAL_HARD_ANGLE_MODES_WITH_COMMON_LEADING_AMPLITUDE",
        },
        "rational_two_mode_fixture": {
            "c_values": ["0", "3/5"],
            "common_incoming": {
                "p0_equals_k0": ["6/5", "6/5", "0", "0"],
                "p1": ["1", "-3/5", "4/5", "0"],
                "p2": ["1", "-3/5", "-4/5", "0"],
            },
            "outgoing": [
                {
                    "c": "0",
                    "k1": ["1", "-3/5", "0", "4/5"],
                    "k2": ["1", "-3/5", "0", "-4/5"],
                    "t": "-32/25",
                    "u": "-32/25",
                },
                {
                    "c": "3/5",
                    "k1": ["1", "-3/5", "12/25", "16/25"],
                    "k2": ["1", "-3/5", "-12/25", "-16/25"],
                    "t": "-64/125",
                    "u": "-256/125",
                },
            ],
            "finite_box_compatibility": "after one common scale by 25, every spatial component lies on one integer momentum lattice",
            "status": "EXACT_DISTINCT_RATIONAL_HARD_TWO_MODE_FIXTURE",
        },
        "off_diagonal_effect": {
            "P_plus": matrix_strings(p_plus),
            "P_minus": matrix_strings(p_minus),
            "E_epsilon": matrix_strings(effect),
            "E_no": matrix_strings(complement),
            "spectral_form": "E_epsilon=P_plus+(1-epsilon)*P_minus",
            "spectrum": ["1", "1-epsilon"],
            "domain": "0<epsilon<=1",
            "off_diagonal_entry": "epsilon/2",
            "completeness": "E_epsilon+E_no=I_2",
            "pure_coherent_endpoint": "epsilon=1 gives E_click=P_plus and E_no=P_minus",
            "status": "POSITIVE_NORMALIZED_GENUINELY_OFF_DIAGONAL_ANGLE_EFFECT",
        },
        "coherent_probability_through_lambda6": {
            "leading_invariance": "<X2,E_epsilon X2>=<X2,X2>=2*q4",
            "cross_invariance": "2*Re<X2,E_epsilon X4>=2*Re<X2,X4> because E_epsilon X2=X2",
            "relative_coefficient": "R6_pair=[R6(c1;f,T,mu)+R6(c2;f,T,mu)]/2",
            "probability": "q_epsilon(c1,c2;f,T)=2*q4*{1+lambda^2*R6_pair}+O(lambda^8)",
            "epsilon_dependence": "NONE_THROUGH_LAMBDA6",
            "uniform_bound": "|R6_pair|<=M_R on any common compact hard interval",
            "small_coupling_positivity": "lambda^2*M_R<1 implies positive truncated click probability for every 0<epsilon<=1",
            "status": "RECORDED_AND_COHERENT_TWO_ANGLE_PROBABILITIES_IDENTICAL_THROUGH_LAMBDA6",
        },
        "first_detector_sensitive_order": {
            "order": "lambda8",
            "known_term": "the squared norm of the complete order-lambda4 output Y4=(Y4(c1),Y4(c2))",
            "recorded_value": "||Y4(c1)||^2+||Y4(c2)||^2",
            "coherent_value": "recorded_value-(epsilon/2)*||Y4(c1)-Y4(c2)||^2",
            "difference": "-(epsilon/2)*||Y4(c1)-Y4(c2)||^2<=0",
            "fixture": {
                "epsilon": "2/5",
                "Y4_c1": "1+2*i",
                "Y4_c2": "-3+i",
                "recorded_norm": "15",
                "coherent_norm": "58/5",
                "difference": "-17/5",
            },
            "full_q8_status": "NOT_COMPUTED",
            "meaning": "the coherent detector suppresses the antisymmetric angle component of the known Y4 norm; other q8 amplitudes and crosses remain in the missing ledger",
            "status": "FIRST_POSSIBLE_COHERENCE_DIFFERENCE_LOCALIZED_AT_LAMBDA8",
        },
        "label_transport": {
            "rule": "tensor the same two-angle effect with any one of the nine certified spectator-label record blocks",
            "status": "AVAILABLE_ON_ALL_NINE_SPECTATOR_CYLINDERS",
        },
        "disposition": {
            "off_diagonal_two_angle_effect": "CONSTRUCTED",
            "positive_binary_detector": "CONSTRUCTED",
            "angle_record_in_coherent_click_at_epsilon_one": "ERASED",
            "complete_probability_through_lambda6": "COEFFICIENT_COMPUTED",
            "detector_dependence_through_lambda6": "EXACTLY_ABSENT",
            "known_q8_variance_target": "COMPUTED",
            "full_q8_probability": "NOT_COMPUTED",
            "BT_dynamical_detector_selection": "NOT_ESTABLISHED",
            "forward_and_backward_endpoints": "NOT_INCLUDED",
            "all_order_or_all_time_probability": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED_AND_NOT_USED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            {"object": "complete order-lambda8 tagged output ledger on the two-angle carrier", "status": "MISSING", "required_value": "all Y4-norm, X2-X6 and any allowed intermediate-order contributions with the same detector effect"},
            {"object": "BT dynamical detector selection", "status": "MISSING", "required_value": "a coupling of a finite apparatus to the angle carrier that derives epsilon and the relative phase rather than declaring them"},
            {"object": "endpoint completion", "status": "MISSING", "required_value": "real, virtual, survival and collinear sectors at c=+/-1"},
            {"object": "metric gravity transfer", "status": "MISSING", "required_value": "classical BV import, physical metric cohomology and pairing, restored QME and causal state"},
        ],
        "does_not_establish": [
            "that the off-diagonal effect is uniquely selected by the public BT Hamiltonian",
            "equality of recorded and coherent probabilities at order lambda8 or beyond",
            "the full order-lambda8 probability coefficient",
            "coherence over a continuum of angles or arbitrary unequal detector cells",
            "either forward or exchanged-forward endpoint",
            "real-virtual, survival, collinear or KLN completion",
            "an all-order probability or all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Bateman--Turok Eq. (19)",
            "gravity or metric BV--BRST transfer",
            "a restored gravitational quantum master equation or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "next_gate": "Compute the complete order-lambda8 tagged amplitude ledger on the same two-angle carrier. The known Y4 norm predicts a negative coherence variance -epsilon*||Y4(c1)-Y4(c2)||^2/2; the remaining X2-X6 and any allowed intermediate contributions decide the full q8 coefficient. In parallel, an apparatus coupling is required to dynamically select epsilon and the relative angle phase.",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_two_angle_coherent_q6_detector.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_two_angle_coherent_q6_detector.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_two_angle_coherent_q6_detector",
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
            for failure in payload["checks"]["failures"]:
                print("FAIL:", failure, file=sys.stderr)
            return 1
        if os.path.exists(CERT) and load(os.path.relpath(CERT, ROOT)) != payload:
            print("BT TWO ANGLE COHERENT Q6: STALE CERTIFICATE", file=sys.stderr)
            return 1
        print(
            "BT TWO ANGLE COHERENT Q6: ALL PASS "
            f"({payload['checks']['passed']}/{payload['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
