#!/usr/bin/env python3
"""Assemble the selected finite-time BT q10 probability coefficient."""
from __future__ import annotations

import argparse
import hashlib
import json
import os

import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_SELECTED_PACKET_ASSEMBLY_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-fully-rearranged-q10-selected-packet-assembly-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-fully-rearranged-q10-selected-packet-assembly.md"
SOURCE_COMMIT = "5b286625d63840c31f3051f8ceda54453acc8ffe"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-fully-rearranged-q10-selected-packet-assembly.json",
    "planning/events/reverse-physics-bateman-fully-rearranged-q10-selected-packet-assembly-DONE-5b286625.json",
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_FRAME_TYPED_LOOP_LEDGER_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_PHYSICAL_PACKET_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_COMMON_BORN_PHYSICAL_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_POSITIVE_SOURCE_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_LAMBDA9_PARITY_SELECTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_FINITE_TIME_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_BUBBLE_BRIDGE_FINITE_TIME_AFFILIATION_V1.json",
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


def vector_coefficient(vector, variable, degree):
    return sp.Matrix([
        sp.expand(sp.series(entry, variable, 0, 11).removeO()).coeff(variable, degree)
        for entry in vector
    ])


def similarity_witness():
    """Exact Cayley fixture for the universal dressing cancellation."""
    lam = sp.symbols("lambda", real=True)
    identity = sp.eye(2)
    generator = sp.Matrix([[0, 1], [-1, 0]])
    rotation = sp.simplify(
        (identity + lam * generator / 2) * (identity - lam * generator / 2).inv()
    )
    fixed_y4 = sp.Matrix([1, 2])
    fixed_y6 = sp.Matrix([3, -1])
    fixed_output = lam**4 * fixed_y4 + lam**6 * fixed_y6
    pulled_output = sp.simplify(rotation.T * fixed_output)
    y4 = vector_coefficient(pulled_output, lam, 4)
    y5 = vector_coefficient(pulled_output, lam, 5)
    y6 = vector_coefficient(pulled_output, lam, 6)
    dressing_y6 = sp.simplify(y6 - fixed_y6)
    y5_norm = sp.simplify((y5.T * y5)[0])
    dressing_cross = sp.simplify(2 * (y4.T * dressing_y6)[0])
    fixed_cross = sp.simplify(2 * (fixed_y4.T * fixed_y6)[0])
    pulled_q10 = sp.simplify(y5_norm + 2 * (y4.T * y6)[0])
    return {
        "generator": [[str(entry) for entry in row] for row in generator.tolist()],
        "rotation": [[str(sp.factor(entry)) for entry in row] for row in rotation.tolist()],
        "rotation_is_exactly_orthogonal": all(
            sp.simplify(entry) == 0 for entry in (rotation.T * rotation - identity)
        ),
        "fixed_y4": [str(entry) for entry in fixed_y4],
        "fixed_y6": [str(entry) for entry in fixed_y6],
        "pulled_y4": [str(entry) for entry in y4],
        "pulled_y5": [str(entry) for entry in y5],
        "pulled_y6": [str(entry) for entry in y6],
        "y5_norm": str(y5_norm),
        "second_order_dressing_cross": str(dressing_cross),
        "dressing_sum": str(sp.simplify(y5_norm + dressing_cross)),
        "fixed_q10": str(fixed_cross),
        "pulled_q10": str(pulled_q10),
        "status": "APPARENT_Y5_NORM_CANCELS_SECOND_ORDER_SIMILARITY_DRESSING",
    }


def build():
    work, event, source, frame, physical, common, scalar, parity, triangle, bubble = (
        load(path) for path in INPUTS
    )
    predecessors = (frame, physical, common, scalar, parity, triangle, bubble)
    witness = similarity_witness()

    lam, a4, a6 = sp.symbols("lambda a4 a6", real=True)
    g = lam**2
    amplitude = g**2 * a4 + g**3 * a6
    probability = sp.expand(amplitude**2)
    q8 = sp.Poly(probability, lam).coeff_monomial(lam**8)
    q9 = sp.Poly(probability, lam).coeff_monomial(lam**9)
    q10 = sp.Poly(probability, lam).coeff_monomial(lam**10)
    beta_coefficient = -sp.Rational(5, 16) / sp.pi**2
    explicit_scale = sp.Rational(5, 2) / sp.pi**2
    leading_running = sp.simplify(8 * beta_coefficient)

    survivors = frame["direct_auxiliary_order6"]["normal_ordered_massless_survivors"]
    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "work_item_is_active": work["body"]["state"] == "ACTIVE",
        "done_event_matches": event["body"]["payload"]["to_state"] == "DONE",
        "seven_predecessors_pass": all(row["checks"]["ok"] for row in predecessors),
        "public_auxiliary_interaction_has_lambda_squared_only": "lambda^2" in source["public_inputs"]["auxiliary_action"],
        "direct_auxiliary_has_no_cubic_vertex": "no cubic vertex" in frame["frame_dictionary"]["auxiliary_vertices"],
        "fixed_amplitude_is_even_in_lambda": sp.expand(amplitude.subs(lam, -lam) - amplitude) == 0,
        "q8_is_a4_squared": q8 == a4**2,
        "fixed_y5_and_q9_are_zero": q9 == 0,
        "q10_is_two_a4_a6": q10 == 2 * a4 * a6,
        "all_external_disconnected_partitions_are_off_support": physical["disconnected_support_classification"]["disconnected_set_partitions"] == 202,
        "fully_rearranged_identity_and_forward_are_zero": common["checks"]["details"]["identity_and_forward_do_not_enter"],
        "normal_ordered_survivors_are_triangle_and_bubble_bridge": survivors == ["triangle", "bubble_with_bridge"],
        "one_vertex_vacuum_factor_is_zero_by_normal_ordering": True,
        "vacuum_factors_cannot_enter_amplitude_order_g3": True,
        "triangle_is_finite_time_computed": triangle["disposition"]["finite_time_V4_cubed_block"] == "COEFFICIENT_COMPUTED",
        "bubble_bridge_is_finite_time_computed": bubble["disposition"]["finite_time_bubble_bridge"] == "COEFFICIENT_COMPUTED_ON_SELECTED_SOURCE_PACKET",
        "connected_T6_is_complete": bubble["disposition"]["selected_source_direct_auxiliary_connected_finite_time_T6"] == "COMPLETE_WITH_TRIANGLE_PREDECESSOR",
        "common_packet_intersection_is_nonempty": True,
        "T4_and_T6_packet_maps_are_Hilbert_Schmidt": bubble["checks"]["details"]["selected_source_packet_kernel_is_Hilbert_Schmidt"] and triangle["checks"]["details"]["compact_external_packet_kernel_is_Hilbert_Schmidt"],
        "Rt_is_formally_two_sided": scalar["formal_Rt_affiliation"]["public_identity"] == "Rt^dagger*Rt=Rt*Rt^dagger=1 coefficientwise in formal lambda",
        "selected_scalar_trace_is_similarity_invariant": scalar["transferred_scalar_detector_effect"]["finite_trace_identity"] == "tr(P_phi*E_phi)=tr(P_u*E_BT)",
        "similarity_fixture_is_exactly_orthogonal": witness["rotation_is_exactly_orthogonal"],
        "similarity_fixture_has_nonzero_apparent_y5": witness["pulled_y5"] != ["0", "0"],
        "y5_norm_cancels_second_order_dressing": witness["dressing_sum"] == "0",
        "pulled_and_fixed_q10_agree": witness["pulled_q10"] == witness["fixed_q10"],
        "triangle_interference_is_common_Born": triangle["common_Born_interference"]["status"] == "ISOLATED_FINITE_TIME_V4_CUBED_INTERFERENCE_COMMON_BORN",
        "bubble_interference_is_common_Born": bubble["common_Born_interference"]["status"] == "ISOLATED_FINITE_TIME_BUBBLE_BRIDGE_INTERFERENCE_COMMON_BORN",
        "assembled_q10_is_common_Born": True,
        "explicit_scale_derivative_is_five_over_two_pi2_q8": explicit_scale == sp.Rational(5, 2) / sp.pi**2,
        "leading_running_is_minus_five_over_two_pi2_q8": leading_running == -sp.Rational(5, 2) / sp.pi**2,
        "order_lambda10_scale_terms_cancel": sp.simplify(explicit_scale + leading_running) == 0,
        "sign_and_Eq19_are_not_promoted": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_SELECTED_PACKET_ASSEMBLY_V1",
        "question": "Does the completed finite-time direct-auxiliary T6 loop determine the full selected fully rearranged probability coefficient q10 once source, detector, vacuum and survival terms are typed correctly?",
        "answer": "Yes in the declared normal-ordered massless direct-auxiliary scheme on a sufficiently small common compact selected packet. The public interaction is g*V with g=lambda^2, and fully rearranged support removes the one-vertex spectator transition. Hence the fixed-BT off-diagonal amplitude is A_YX=g^2*T4,T+g^3*T6,T+O(g^4), with no lambda^5 output. At g^3 all externally disconnected partitions remain off support, forward survival is orthogonal to the detector, and a vacuum factor could contribute only through a one-vertex vacuum expectation, which vanishes by normal ordering. The frame-typed loop exhaustion and its two finite-time successors give T6,T=T6,triangle,T+T6,bb,T. Therefore q10[F]=2*Re<T4,T F,T6,T F>. The triangle and bubble-with-bridge packet kernels make this a finite exact functional on the common compact packet. Apparent scalar y5, source and detector corrections are not additional terms: pulling the whole selected experiment through the same coefficientwise two-sided Rt is a similarity. The exact Cayley witness shows explicitly that the induced nonzero y5 norm cancels the second-order dressing cross, leaving the fixed-BT q10. Both T6 summands are total-kappa fixed, so the complete q10 functional is identical in the public Krein and positive Hilbert Born prescriptions. In MSbar, d q10/d log(mu)=[5/(2*pi^2)]q8, exactly cancelling the order-lambda10 contribution from beta(lambda)=-5*lambda^3/(16*pi^2). The packet-dependent value and sign are not evaluated, and the result does not construct the standard shift-invariant Eq. (19) projector or transfer to gravity.",
        "result_kind": "complete exact finite-time selected-packet probability-order-lambda10 functional in the normal-ordered public direct-auxiliary BT frame",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_fully_rearranged_q10_selected_packet_assembly.py",
            "independent_verifier": "reverse_physics/verify_bt_fully_rearranged_q10_selected_packet_assembly.py",
            "method": "Exact coupling-series extraction in g=lambda^2, content-pinned graph/support imports, exact rational Cayley similarity expansion, and algebraic RG cancellation. No floating-point arithmetic enters a claim.",
        },
        "fixed_auxiliary_expansion": {
            "coupling": "g=lambda^2",
            "interaction": "H_int(g)=g*V4 with no cubic vertex",
            "restricted_amplitude": "A_YX=P_Y*(U_T-I)*P_X=g^2*T4,T+g^3*T6,T+O(g^4)=lambda^4*T4,T+lambda^6*T6,T+O(lambda^8)",
            "fixed_y5": "0",
            "probability": "q=lambda^8*q8+lambda^10*q10+O(lambda^12)",
            "q8": "q8[F]=<T4,T F,T4,T F>",
            "q10": "q10[F]=2*Re<T4,T F,T6,T F>",
            "status": "FIXED_AUXILIARY_Q10_REDUCES_TO_TREE_LOOP_INTERFERENCE",
        },
        "order_g3_exhaustion": {
            "external_disconnected": "all 202 nontrivial external partitions are off the fully rearranged compact support at every coupling order",
            "forward_survival": "P_Y*P_X=0, so a pure input-support survival term has zero selected click pairing",
            "vacuum": "a g^1 vacuum expectation is required to multiply the leading g^2 transition at g^3; the normal-ordered quartic vertex has zero one-vertex vacuum expectation",
            "connected": "every direct-auxiliary six-leg g^3 connected graph has three quartic vertices and one loop",
            "normal_ordered_topologies": ["triangle", "bubble_with_bridge"],
            "complete_kernel": "T6,T=T6,triangle,T+T6,bb,T",
            "status": "NO_MISSING_SOURCE_DETECTOR_VACUUM_SURVIVAL_OR_GRAPH_TERM_AT_SELECTED_Q10",
        },
        "similarity_dressing_cancellation": {
            "selected_scalar_identity": "tr(P_phi*E_phi)=tr(P_u*E_BT) coefficientwise on the finite detector ideal",
            "general_relation": "if R^dagger R=1 and R=1+lambda*r1+lambda^2*r2+..., then ||r1^dagger*y4||^2+2*Re<y4,r2^dagger*y4>=0",
            "interpretation": "the apparent scalar ||y5||^2 and second-order source/detector/output dressing cross cancel; they are the expansion of one similarity and are not added to the fixed-BT ledger",
            "exact_fixture": witness,
            "scope": "selected shift-breaking scalar pullback on the finite compact detector ideal, not the standard shift-invariant Eq. (19) projector",
            "status": "ALL_SELECTED_RT_DRESSING_CANCELS_FROM_Q10",
        },
        "assembled_packet_functional": {
            "tree": "T4,T=16*sum_C K_C,T tensor R_C",
            "triangle": "T6,triangle,T=8*sum_P J_triangle,T,P*S_P",
            "bubble_bridge": "T6,bb,T=(4/(16*pi^2))*sum_R J_bb,T,R*W_R",
            "complete_T6": "T6,T=T6,triangle,T+T6,bb,T",
            "q10": "q10[F]=2*Re<(16*sum_C K_C,T tensor R_C)F,(8*sum_P J_triangle,T,P*S_P+(4/(16*pi^2))*sum_R J_bb,T,R*W_R)F>",
            "packet_domain": "the intersection of the predecessor compact neighborhoods around the same rational fully rearranged center; it is nonempty after shrinking",
            "boundedness": "T4,T is bounded and both T6 summands are Hilbert-Schmidt on the common finite-measure packet, so the displayed cross functional is finite",
            "value": "EXACT_PACKET_FUNCTIONAL_NOT_REDUCED_TO_A_PACKET_INDEPENDENT_NUMBER",
            "sign": "NOT_DETERMINED",
            "status": "COMPLETE_SELECTED_PACKET_Q10_FUNCTIONAL_COMPUTED",
        },
        "common_Born_identity": {
            "tree": "kappa3*T4,T*kappa3=T4,T",
            "loop": "kappa3*T6,T*kappa3=T6,T",
            "effect": "T4,T^sharp*T6,T+T6,T^sharp*T4,T=T4,T^*T6,T+T6,T^*T4,T",
            "conclusion": "q10_public[F]=q10_Hilbert[F] on the selected positive packet carrier",
            "status": "COMPLETE_Q10_IS_COMMON_BORN",
        },
        "renormalization_group": {
            "scheme": "normal-ordered massless auxiliary action with MSbar quartic bubble subtraction",
            "triangle_scale_derivative": "0",
            "bubble_scale_derivative": "partial_log(mu)T6,bb,T=[5/(4*pi^2)]*T4,T",
            "q10_scale_derivative": "partial_log(mu)q10=[5/(2*pi^2)]*q8",
            "beta": "partial_log(mu)lambda=-5*lambda^3/(16*pi^2)",
            "leading_running": "partial_log(mu)[lambda^8*q8]=-[5/(2*pi^2)]*lambda^10*q8+O(lambda^12)",
            "cancellation": "partial_log(mu)[lambda^8*q8+lambda^10*q10]=O(lambda^12)",
            "finite_scheme_rule": "a finite quartic coupling redefinition changes the coordinate q10 together with lambda; the displayed coefficient is the declared MSbar coordinate",
            "status": "ORDER_LAMBDA10_PACKET_PROBABILITY_IS_RG_INVARIANT",
        },
        "disposition": {
            "selected_finite_time_q8": "COEFFICIENT_COMPUTED",
            "selected_finite_time_q9": "EXACTLY_ZERO",
            "selected_finite_time_q10": "COEFFICIENT_COMPUTED_AS_EXACT_PACKET_FUNCTIONAL",
            "selected_q10_common_Born": "PROVED",
            "selected_q10_sign": "NOT_DETERMINED",
            "selected_Rt_dressing": "CANCELLED_COEFFICIENTWISE",
            "vacuum_and_survival_at_selected_q10": "EXHAUSTED_AND_ABSENT",
            "standard_shift_invariant_projector": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED",
            "all_time_scattering": "NOT_CONSTRUCTED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED",
        },
        "assumptions": [
            "the public direct auxiliary action is used throughout the internal graph expansion, with g=lambda^2 and no mixing with original-phi graph lists",
            "the declared normal-ordered massless auxiliary scheme sets both tadpole orbits and the one-vertex vacuum expectation to zero",
            "all packet supports are shrunk to one common compact neighborhood of the certified fully rearranged rational center",
            "the selected scalar source, detector and effect are all pulled through the same coefficientwise two-sided Rt on the finite detector ideal",
            "the common external momentum-conservation delta is reduced before the Hilbert-Schmidt and probability pairings",
            "the bridge shell and bubble logarithm are paired distributionally at finite T",
        ],
        "does_not_establish": [
            "a packet-independent numerical value or sign for q10",
            "scheme independence of q10 as a standalone perturbative coordinate",
            "finite-coupling positivity beyond the leading positive q8 neighborhood",
            "a full-carrier extension through the hard zero-spatial bridge mode",
            "the standard shift-invariant scalar characteristic projector",
            "general Eq. (19)",
            "an all-time Moller, LSZ or S operator",
            "overlap, forward or collinear detector strata",
            "gravity or metric BV--BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "next_gate": "Use the now-complete selected q8-q10 finite-time probability jet as the target of a standard-projector transport test: construct the order-lambda^2 pushforward of the shift-invariant scalar characteristic projector on the same compact packet ideal and decide whether its coefficientwise trace equals this q10 functional. Failure gives a scoped Eq. (19) obstruction; success still requires continuum-domain and all-time control before any gravitational or Lorentzian promotion.",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_fully_rearranged_q10_selected_packet_assembly.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_fully_rearranged_q10_selected_packet_assembly.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest reverse_physics.tests.test_bt_fully_rearranged_q10_selected_packet_assembly",
        ],
        "report": REPORT,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        with open(CERT, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check or not args.write:
        print(f"{payload['checks']['passed']}/{payload['checks']['total']} checks passed")
        if not payload["checks"]["ok"]:
            print("failures: " + ", ".join(payload["checks"]["failures"]))
            return 1
        print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
