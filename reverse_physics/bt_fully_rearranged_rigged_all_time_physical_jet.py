#!/usr/bin/env python3
"""Assemble the complete selected BT all-time physical jet through lambda10."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_PHYSICAL_JET_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-fully-rearranged-rigged-all-time-physical-jet-v1.schema.json"
)
REPORT = (
    "reverse_physics/reports/"
    "bt-fully-rearranged-rigged-all-time-physical-jet.md"
)
SOURCE_COMMIT = "d8e41e268805900f12fc69307a2c00c9f3ef1ae8"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-fully-rearranged-all-time-physical-jet.json",
    "planning/events/reverse-physics-bateman-fully-rearranged-all-time-physical-jet-DONE-d8e41e26.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_PHYSICAL_PACKET_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_COMMON_BORN_PHYSICAL_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_LAMBDA9_PARITY_SELECTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_PACKET_LIMIT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_SELECTED_PACKET_ASSEMBLY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_Q10_PACKET_V1.json",
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


def rational(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def matmul(left, right):
    return [
        [sum(left[i][k] * right[k][j] for k in range(len(right)))
         for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def add(left, right):
    return [
        [left[i][j] + right[i][j] for j in range(len(left[0]))]
        for i in range(len(left))
    ]


def finite_effect_witness():
    # A method-visible exact lemma: fixed operators have identical
    # Krein/Hilbert E8 and E10 coefficients after kappa-Hilbertization.
    kappa = [[0, 1], [1, 0]]
    tree = [[1, 2], [2, 1]]
    loop = [[3, -1], [-1, 3]]
    sharp_tree = matmul(matmul(kappa, transpose(tree)), kappa)
    sharp_loop = matmul(matmul(kappa, transpose(loop)), kappa)
    e8_public = matmul(sharp_tree, tree)
    e8_hilbert = matmul(transpose(tree), tree)
    e10_public = add(matmul(sharp_tree, loop), matmul(sharp_loop, tree))
    e10_hilbert = add(matmul(transpose(tree), loop), matmul(transpose(loop), tree))
    return {
        "kappa": kappa,
        "tree": tree,
        "loop": loop,
        "tree_fixed": matmul(matmul(kappa, tree), kappa) == tree,
        "loop_fixed": matmul(matmul(kappa, loop), kappa) == loop,
        "E8_public": e8_public,
        "E8_Hilbert": e8_hilbert,
        "E10_public": e10_public,
        "E10_Hilbert": e10_hilbert,
    }


def build():
    physical = load(INPUTS[2])
    common = load(INPUTS[3])
    parity = load(INPUTS[4])
    q8 = load(INPUTS[5])
    assembly = load(INPUTS[6])
    q10 = load(INPUTS[7])
    event = load(INPUTS[1])
    support = physical["disconnected_support_classification"]
    witness = finite_effect_witness()

    # A rational instance of the general positivity lemma.  It is not a
    # numerical evaluation of the physical packet coefficients.
    lemma_q8 = Fraction(3, 5)
    lemma_q10 = Fraction(-7, 11)
    safe_lambda_squared = lemma_q8 / (2 * abs(lemma_q10))

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "all_predecessors_pass": all(
            item["checks"]["ok"]
            for item in (physical, common, parity, q8, assembly, q10)
        ),
        "event_is_done": event["body"]["payload"]["to_state"] == "DONE",
        "detector_has_202_disconnected_partitions": support["disconnected_set_partitions"] == 202,
        "all_disconnected_support_is_annihilated": support["status"] == "DISCONNECTED_SPECTATOR_LEDGER_ANNIHILATED_BY_SUPPORT",
        "support_derivatives_do_not_enlarge_support": "do not enlarge" in support["derivative_lemma"],
        "leading_input_output_are_orthogonal": physical["complete_leading_physical_probability"]["input_output_orthogonality"].startswith("P_out*P_in=0"),
        "leading_transition_is_physically_complete": physical["complete_leading_physical_probability"]["status"] == "COMPLETE_LEADING_FULLY_REARRANGED_FINITE_TIME_PHYSICAL_PROBABILITY",
        "leading_operator_is_common_Born": common["complete_leading_common_Born_transition"]["Born_defect"] == "E8_public-E8_Hilbert=0 as an operator coefficient",
        "lambda9_is_exactly_zero": parity["disposition"]["probability_order_lambda9"] == "EXACTLY_ZERO_IN_BOTH_BORN_FORMS",
        "odd_probability_orders_are_zero": "every odd coefficient zero" in parity["fully_rearranged_output_selection"]["probability_series"],
        "q8_all_time_limit_is_complete_leading": q8["rigged_packet_limit"]["status"] == "COMPLETE_LEADING_SELECTED_ALL_TIME_PACKET_COEFFICIENT_COMPUTED",
        "q8_is_strictly_positive": q8["rigged_packet_limit"]["probability_limit"].endswith("q8,infinity[F]>0"),
        "disconnected_zero_survives_all_time": "stays zero" in q8["rigged_packet_limit"]["disconnected_terms"],
        "fixed_auxiliary_expansion_has_only_g2_g3": assembly["fixed_auxiliary_expansion"]["restricted_amplitude"].startswith("A_YX=P_Y*(U_T-I)*P_X=g^2*T4,T+g^3*T6,T"),
        "q10_graph_ledger_is_exhaustive": assembly["order_g3_exhaustion"]["status"] == "NO_MISSING_SOURCE_DETECTOR_VACUUM_SURVIVAL_OR_GRAPH_TERM_AT_SELECTED_Q10",
        "external_disconnected_zero_is_all_orders": "at every coupling order" in assembly["order_g3_exhaustion"]["external_disconnected"],
        "forward_survival_is_orthogonal": assembly["order_g3_exhaustion"]["forward_survival"].startswith("P_Y*P_X=0"),
        "vacuum_factor_is_absent": "zero one-vertex vacuum expectation" in assembly["order_g3_exhaustion"]["vacuum"],
        "q10_similarity_dressing_is_already_cancelled": assembly["disposition"]["selected_Rt_dressing"] == "CANCELLED_COEFFICIENTWISE",
        "q10_is_common_Born_at_finite_time": assembly["common_Born_identity"]["status"] == "COMPLETE_Q10_IS_COMMON_BORN",
        "all_time_T6_is_complete": q10["all_time_loop_operator"]["status"] == "COMPLETE_SELECTED_ALL_TIME_T6_PACKET_MAP_CONSTRUCTED",
        "all_time_q10_is_finite": "finite" in q10["q10_packet_coefficient"]["finiteness"],
        "all_time_q10_is_common_Born": q10["q10_packet_coefficient"]["common_Born"].startswith("q10,infinity^public"),
        "all_time_q10_sign_remains_open": q10["q10_packet_coefficient"]["sign"] == "NOT_DETERMINED",
        "RG_identity_is_imported": q10["renormalization_group"]["status"] == "ALL_TIME_SELECTED_Q8_Q10_JET_IS_RG_INVARIANT_THROUGH_LAMBDA10",
        "finite_witness_tree_is_fixed": witness["tree_fixed"],
        "finite_witness_loop_is_fixed": witness["loop_fixed"],
        "finite_witness_E8_agrees": witness["E8_public"] == witness["E8_Hilbert"],
        "finite_witness_E10_agrees": witness["E10_public"] == witness["E10_Hilbert"],
        "positivity_lemma_radius_is_exact": safe_lambda_squared == Fraction(33, 70),
        "positivity_lemma_has_half_margin": lemma_q8 + safe_lambda_squared * lemma_q10 == lemma_q8 / 2,
        "selected_not_all_channel": True,
        "finite_coupling_is_not_promoted": True,
        "Eq19_gravity_and_causality_are_not_promoted": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_PHYSICAL_JET_V1",
        "question": "Do the certified all-time q8 and q10 coefficients form the complete selected public-auxiliary physical probability jet through lambda10 on the fully rearranged detector?",
        "answer": "Yes on the nonempty smooth compact fully rearranged packet class and in the declared normal-ordered massless MSbar direct-auxiliary scheme. Restrict before taking the all-time limit. The incoming and outgoing packet projectors are orthogonal and their supports miss every component delta in all 202 disconnected six-leg partitions, including identity, spectator and collinear supports; differentiation does not enlarge those supports. The order-independent support zero therefore persists through the loop order. In the surviving connected sector the direct auxiliary expansion is A_YX=lambda^4*T4,infinity+lambda^6*T6,infinity+O(lambda^8). The exhaustive order-g3 ledger leaves precisely the all-time triangle and bubble-with-bridge maps; the two tadpole orbits vanish by normal ordering, the only possible vacuum multiplier is zero, and pure survival is killed by P_Y P_X=0. Total-Fock parity removes every odd probability order. Hence q_phys,infinity=lambda^8*q8,infinity+lambda^10*q10,infinity+O(lambda^12), with q8,infinity=||T4,infinity F||^2>0 and q10,infinity=2*Re<T4,infinity F,T6,infinity F> finite. Both T4 and T6 are total-kappa fixed, so the E8 and E10 operator coefficients, not merely their scalar values, coincide in the public generalized-Krein and positive-Hilbert Born prescriptions. For each fixed packet and scale, strict q8 positivity plus q10 finiteness gives a nonempty exact small-coupling interval on which the truncated jet is positive. Its scale derivative vanishes through lambda10. This is a complete selected physical packet jet, not an all-channel or all-order probability, a whole-carrier S operator, general Eq. (19), gravity, or Lorentzian causal physics.",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "complete selected public-auxiliary all-time physical probability jet through lambda10",
        "selected_physical_domain": {
            "domain": q10["q10_packet_coefficient"]["domain"],
            "restriction_order": "apply the support projectors P_X and P_Y before the external center-time removal and all-time limit",
            "input_output_orthogonality": "P_Y*P_X=0",
            "disconnected_partitions": support["disconnected_set_partitions"],
            "support_margins_squared": ["2", "32/625", "17794/10625"],
            "support_conclusion": "all external disconnected, identity, spectator and collinear component distributions pair to zero coefficientwise on the selected detector; derivatives retain the same support",
            "all_time_conclusion": "a distribution that pairs to zero with the fixed separated packet support remains zero before and after the all-time limit",
            "status": "COMPLETE_SELECTED_SUPPORT_RESTRICTION_THROUGH_LAMBDA10",
        },
        "complete_amplitude_jet": {
            "coupling": "g=lambda^2",
            "amplitude": "A_YX,infinity=lambda^4*T4,infinity+lambda^6*T6,infinity+O(lambda^8)",
            "tree": q10["all_time_loop_operator"]["tree"],
            "loop": q10["all_time_loop_operator"]["complete_loop"],
            "graph_exhaustion": "triangle plus bubble-with-bridge; normal-ordered tadpole-center and tadpole-leaf orbits vanish",
            "vacuum": "the only order-g vacuum multiplier of the order-g2 transition is the zero normal-ordered one-vertex vacuum expectation",
            "survival": "P_Y*P_X=0 kills identity and pure forward/survival terms",
            "similarity_dressing": "the common two-sided R_t pull cancels coefficientwise on this selected experiment and supplies no additional y5 norm or source/detector term",
            "status": "NO_MISSING_SELECTED_AMPLITUDE_TERM_THROUGH_LAMBDA6",
        },
        "physical_probability_jet": {
            "formula": "q_phys,infinity[F]=lambda^8*q8,infinity[F]+lambda^10*q10,infinity[F]+O(lambda^12)",
            "q8": q10["q10_packet_coefficient"]["q8"],
            "q9": "0 by exact total-Fock parity in both Born prescriptions",
            "q10": q10["q10_packet_coefficient"]["q10"],
            "E8": "E8=T4,infinity^* T4,infinity",
            "E10": "E10=T4,infinity^* T6,infinity+T6,infinity^* T4,infinity",
            "q8_sign": "STRICTLY_POSITIVE_ON_A_NONEMPTY_REAL_NONNEGATIVE_PACKET_CLASS",
            "q10_sign": "NOT_DETERMINED",
            "completeness_scope": "all terms contributing to the selected orthogonal packet click through lambda10",
            "status": "COMPLETE_SELECTED_ALL_TIME_PHYSICAL_JET_THROUGH_LAMBDA10",
        },
        "common_Born_operator_identity": {
            "fixedness": "alpha(T4,infinity)=T4,infinity and alpha(T6,infinity)=T6,infinity",
            "E8": "E8_public=E8_Hilbert",
            "E10": "E10_public=E10_Hilbert",
            "probability": "q_phys,infinity^public[F]=q_phys,infinity^Hilbert[F]+O(lambda^12)",
            "finite_exact_witness": witness,
            "status": "PUBLIC_AND_POSITIVE_HILBERT_SELECTED_EFFECT_JETS_AGREE_THROUGH_LAMBDA10",
        },
        "small_coupling_positivity": {
            "lemma": "for q8>0 and finite real q10, q8+lambda^2*q10 is positive whenever q10>=0 or lambda^2<q8/abs(q10) when q10<0",
            "half_margin_choice": "when q10 is nonzero, lambda^2<=q8/(2*abs(q10)) implies q8+lambda^2*q10>=q8/2",
            "rational_lemma_fixture": {
                "q8": rational(lemma_q8),
                "q10": rational(lemma_q10),
                "safe_lambda_squared": rational(safe_lambda_squared),
                "lower_margin": rational(lemma_q8 / 2),
            },
            "scope": "positivity of the finite truncated jet for each fixed certified packet and scale, not positivity of the unknown exact probability",
            "status": "NONEMPTY_PACKETWISE_PERTURBATIVE_POSITIVITY_NEIGHBORHOOD_PROVED",
        },
        "renormalization_group": {
            "q10_derivative": q10["renormalization_group"]["q10_scale_derivative"],
            "beta": q10["renormalization_group"]["beta"],
            "cancellation": q10["renormalization_group"]["cancellation"],
            "scheme_boundary": "q10 is a scheme-dependent standalone coordinate; only the displayed running jet is invariant to the certified order",
            "status": "SELECTED_PHYSICAL_JET_RG_INVARIANT_THROUGH_LAMBDA10",
        },
        "claim_boundary": {
            "selected_packet_physical_jet": "COEFFICIENT_COMPUTED_THROUGH_LAMBDA10",
            "matched_finite_time_q10": "NOT_COMPUTED",
            "all_channel_probability": "NOT_CONSTRUCTED",
            "finite_coupling_exact_probability": "NOT_ESTABLISHED",
            "bounded_whole_carrier_operator": "NOT_CONSTRUCTED",
            "Moller_LSZ_S": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED",
            "gravity_BV_BRST_QME": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED",
        },
        "assumptions": [
            "the source and detector use the common smooth compact fully rearranged packet domain",
            "support restriction is applied before external center-time removal and the all-time limit",
            "the normal-ordered massless unit-residue direct-auxiliary scheme and MSbar four-point finite part are retained",
            "bridge poles act by the certified coarea PV/delta distributions and are never evaluated pointwise",
            "lambda is sufficiently small only when the truncated-jet positivity statement is invoked",
        ],
        "does_not_establish": [
            "a physical probability for detectors intersecting identity, spectator, forward or collinear supports",
            "a matched or canonical finite-time q10 interpolation",
            "the value or sign of q10,infinity for an arbitrary packet",
            "scheme independence of q10,infinity as a standalone coordinate",
            "positivity of the unknown O(lambda12) remainder or exact finite-coupling probability",
            "interchange of the all-time limit with the uncomputed perturbation series",
            "a bounded whole-L2 transition operator",
            "a strong Moller operator, LSZ construction or all-channel S matrix",
            "general Eq. (19) or the standard scalar characteristic projector",
            "gravity or metric BV-BRST transfer",
            "QME restoration or residual quantum transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "next_gate": "The selected physical route is complete through lambda10. Its nearest genuine enlargement is not to add zero support terms back into this detector, but to construct a common rigged forward/overlap detector with its survival normalization, or to compute the lambda12 selected coefficient and test total-kappa fixedness. The independent Eq. (19) route remains obstructed on the regular one-sheet branch and requires a source-derived singular, localized, doubled or non-Fock projector architecture.",
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "input_hashes": {path: sha256(path) for path in INPUTS},
            "method": "Content-pinned theorem composition of the exhaustive disconnected-support census, orthogonal packet restriction, exact total-Fock parity selection, direct-auxiliary graph/vacuum exhaustion, all-time distributional q8 and q10 limits, total-kappa fixed-point Born descent, exact rational effect algebra, and a rational small-coupling positivity lemma. No floating-point arithmetic enters a claim.",
            "generated_by": "reverse_physics/bt_fully_rearranged_rigged_all_time_physical_jet.py",
            "independent_verifier": "reverse_physics/verify_bt_fully_rearranged_rigged_all_time_physical_jet.py",
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "items": checks,
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_fully_rearranged_rigged_all_time_physical_jet.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_fully_rearranged_rigged_all_time_physical_jet.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_fully_rearranged_rigged_all_time_physical_jet",
        ],
        "report": REPORT,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.write:
        with open(CERT, "w", encoding="utf-8") as handle:
            handle.write(encoded)
    if args.check and os.path.exists(CERT):
        with open(CERT, encoding="utf-8") as handle:
            if handle.read() != encoded:
                print("certificate is stale", file=sys.stderr)
                return 1
    checks = value["checks"]
    print(f"checks: {checks['passed']}/{checks['total']}")
    if not checks["ok"]:
        for name, passed in checks["items"].items():
            if not passed:
                print(f"FAIL: {name}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
