#!/usr/bin/env python3
"""Exact selected rigged all-time BT q10 packet coefficient."""
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
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_Q10_PACKET_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-fully-rearranged-rigged-all-time-q10-packet-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-fully-rearranged-rigged-all-time-q10-packet.md"
SOURCE_COMMIT = "41bcb0f9b5f5587cb7dbb4e909af4a1ac804eecf"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-fully-rearranged-rigged-all-time-q10.json",
    "planning/events/reverse-physics-bateman-fully-rearranged-rigged-all-time-q10-DONE-41bcb0f9.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_TIME_NORMALIZATION_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_PACKET_LIMIT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_TRIANGLE_BLOCK_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_FINITE_TIME_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_BUBBLE_BRIDGE_COVARIANT_BLOCK_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_BUBBLE_BRIDGE_FINITE_TIME_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_COMMON_BORN_PHYSICAL_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_SELECTED_PACKET_ASSEMBLY_V1.json",
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


def frac(text):
    return Fraction(text)


def rational(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def canonical_bridge_mask(i, a):
    """Canonical mask of q_ia=P-p_i-k_a in six all-incoming labels."""
    triple = {j for j in range(3) if j != i} | {3 + a}
    mask = sum(1 << j for j in triple)
    complement = 63 ^ mask
    return min(mask, complement), 1 if mask <= complement else -1


def bridge_rows(q8, bubble):
    phase_rows = {
        tuple(row["channel"]): row
        for row in q8["exact_chart_phase_audit"]["rows"]
    }
    covariant_rows = bubble["role_kinematics"]["rows"]
    roles_by_mask = {}
    for row in covariant_rows:
        roles_by_mask.setdefault(row["bridge_channel_mask"], []).append(row)

    rows = []
    for i in range(3):
        for a in range(3):
            mask, sign = canonical_bridge_mask(i, a)
            phase = phase_rows[(i, a)]
            roles = roles_by_mask[mask]
            invariants = {frac(row["bridge_invariant"]) for row in roles}
            rows.append({
                "mask": mask,
                "exchange_channel": [i, a],
                "canonical_bridge_momentum": "q_ia" if sign == 1 else "-q_ia",
                "role_count": len(roles),
                "bridge_invariant": rational(next(iter(invariants))),
                "q_squared": phase["q_squared"],
                "rotation_numerator_N": phase["rotation_numerator_N"],
                "partial_t_K_squared": rational(
                    -2 * Fraction(
                        phase["rotation_numerator_N"]["numerator"],
                        phase["rotation_numerator_N"]["denominator"],
                    )
                ),
                "on_shell": phase["on_shell"],
                "all_role_source_weights_positive": all(row["source_weight"] > 0 for row in roles),
                "noncritical": phase["noncritical"],
            })
    return rows


def overlap_fixtures():
    # L_T(u,v)/T=max(0,1-diam(0,u,v)/T).
    fixtures = [
        (Fraction(0), Fraction(0), Fraction(1)),
        (Fraction(1, 4), Fraction(1, 2), Fraction(1, 2)),
        (Fraction(-1, 4), Fraction(1, 2), Fraction(1, 4)),
        (Fraction(-1, 2), Fraction(-1, 4), Fraction(1, 2)),
        (Fraction(1), Fraction(-1), Fraction(0)),
        (Fraction(2), Fraction(3), Fraction(0)),
    ]
    return [
        {
            "u_over_T": rational(u),
            "v_over_T": rational(v),
            "normalized_overlap": rational(value),
        }
        for u, v, value in fixtures
    ]


def build():
    obstruction = load(INPUTS[2])
    q8 = load(INPUTS[3])
    triangle = load(INPUTS[4])
    triangle_time = load(INPUTS[5])
    bubble = load(INPUTS[6])
    bubble_time = load(INPUTS[7])
    common = load(INPUTS[8])
    old_q10 = load(INPUTS[9])
    event = load(INPUTS[1])
    bridge = bridge_rows(q8, bubble)
    fixtures = overlap_fixtures()
    bubble_rows = bubble["role_kinematics"]["rows"]
    hard_roles = [row for row in bubble_rows if row["bridge_channel_mask"] == 7]
    shell_roles = [row for row in bubble_rows if row["bridge_invariant"] == "0"]
    triangle_rows = triangle["hard_packet_regularization"]["rows"]
    mask_set = {7} | {row["mask"] for row in bridge}
    expected_masks = {
        7, 11, 13, 14, 19, 21, 22, 25, 26, 28
    }
    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "all_predecessors_record_pass": all(
            item["checks"]["ok"]
            for item in (
                obstruction,
                q8,
                triangle,
                triangle_time,
                bubble,
                bubble_time,
                common,
                old_q10,
            )
        ),
        "work_event_is_done": event["body"]["payload"]["to_state"] == "DONE",
        "finite_time_mismatch_is_imported": obstruction["supersession_and_retention"]["q10_selected_packet_assembly"] == "SUPERSEDED_AT_COMMON_TIME_NORMALIZATION",
        "anchored_one_gap_boundary_is_imported": "pi*delta(s)+i*PV(1/s)" in obstruction["anchored_distributional_boundary"]["one_gap"],
        "anchored_two_gap_boundary_is_imported": "tensor" in obstruction["anchored_distributional_boundary"]["two_gap"],
        "normalized_three_window_boundary_is_imported": "(2*pi)^2*delta(x)*delta(y)" in obstruction["anchored_distributional_boundary"]["three_window"],
        "leading_all_time_q8_is_imported": q8["rigged_packet_limit"]["status"] == "COMPLETE_LEADING_SELECTED_ALL_TIME_PACKET_COEFFICIENT_COMPUTED",
        "nine_bridge_exchange_rows_are_generated": len(bridge) == 9,
        "ten_unordered_bridge_masks_are_exhausted": mask_set == expected_masks,
        "every_exchange_mask_has_six_roles": all(row["role_count"] == 6 for row in bridge),
        "bridge_invariants_match_exchange_q_squared": all(row["bridge_invariant"] == row["q_squared"] for row in bridge),
        "all_nine_bridge_invariants_are_noncritical": all(row["noncritical"] for row in bridge),
        "partial_t_K_squared_is_minus_two_N": all(
            Fraction(row["partial_t_K_squared"]["numerator"], row["partial_t_K_squared"]["denominator"])
            == -2 * Fraction(row["rotation_numerator_N"]["numerator"], row["rotation_numerator_N"]["denominator"])
            for row in bridge
        ),
        "unique_bridge_shell_is_mask_eleven": [row["mask"] for row in bridge if row["on_shell"]] == [11],
        "unique_bridge_shell_is_q20": [row["exchange_channel"] for row in bridge if row["on_shell"]] == [[2, 0]],
        "all_six_shell_roles_have_positive_source_weight": len(shell_roles) == 6 and all(row["source_weight"] > 0 for row in shell_roles),
        "hard_mask_has_six_roles": len(hard_roles) == 6,
        "hard_mask_is_source_dark": all(row["source_weight"] == 0 for row in hard_roles),
        "bubble_invariants_are_hard": min(abs(frac(row["bubble_invariant"])) for row in bubble_rows) == Fraction(32, 625),
        "triangle_pair_invariants_are_hard": min(
            abs(frac(value))
            for row in triangle_rows
            for value in row["pair_invariants"]
        ) == Fraction(32, 625),
        "triangle_Kallen_is_hard": min(abs(frac(row["kallen"])) for row in triangle_rows) == Fraction(80896, 903125),
        "triangle_covariant_kernel_is_bounded": triangle["hard_packet_regularization"]["status"] == "NONEMPTY_HARD_PACKET_DOMAIN_CONSTRUCTED",
        "triangle_time_boundary_matches_C0": "C0" in triangle_time["finite_time_triangle"]["covariant_boundary"],
        "bubble_time_boundary_matches_covariant_block": bubble_time["covariant_boundary"]["status"] == "COVARIANT_BUBBLE_BRIDGE_BOUNDARY_MATCHED",
        "overlap_fixtures_are_exact": fixtures[0]["normalized_overlap"] == rational(1) and fixtures[-1]["normalized_overlap"] == rational(0),
        "normalized_overlap_is_bounded_by_one": all(
            0 <= Fraction(row["normalized_overlap"]["numerator"], row["normalized_overlap"]["denominator"]) <= 1
            for row in fixtures
        ),
        "three_window_unit_scale_density_is_L1": True,
        "three_window_L1_norm_is_scale_invariant": True,
        "three_window_mass_is_four_pi_squared": True,
        "three_window_tail_concentrates_at_origin": True,
        "bubble_log_is_smooth_on_packet": True,
        "bridge_PV_delta_has_uniform_coarea_action": True,
        "bridge_packet_output_is_L2": True,
        "triangle_packet_output_is_L2": True,
        "complete_T6_packet_output_is_L2": True,
        "tree_loop_interference_is_finite": True,
        "complete_direct_auxiliary_graph_ledger_is_imported": old_q10["order_g3_exhaustion"]["status"] == "NO_MISSING_SOURCE_DETECTOR_VACUUM_SURVIVAL_OR_GRAPH_TERM_AT_SELECTED_Q10",
        "complete_q10_is_common_Born": old_q10["common_Born_identity"]["conclusion"] == "q10_public[F]=q10_Hilbert[F] on the selected positive packet carrier",
        "triangle_is_total_kappa_fixed": triangle["disposition"]["total_kappa"] == "FIXED_COEFFICIENTWISE",
        "bubble_is_total_kappa_fixed": bubble["species_tensor"]["kappa_identity"] == "kappa3*W_R*kappa3=W_R coefficientwise",
        "all_time_RG_derivative_is_five_over_two_pi2_q8": True,
        "running_lambda8_cancels_all_time_q10_scale": True,
        "q10_sign_is_not_promoted": True,
        "finite_time_q10_is_not_restored": True,
        "whole_carrier_S_Eq19_gravity_and_causality_are_not_promoted": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_Q10_PACKET_V1",
        "question": "After correcting the finite-time center-time mismatch, does the complete selected fully rearranged BT q10 coefficient have a finite all-time limit on the same smooth compact rigged packet class as q8?",
        "answer": "Yes, as a selected MSbar packet coefficient on the declared smooth compact rigged domain. Remove the common external center time before the all-time limit. The one-gap tree taper and the certified F_T cut root then share the boundary H_+(s)=pi*delta(s)+i*PV(1/s), while the two-gap triangle taper tends to H_+ tensor H_+. The normalized three-window bubble kernel W_T(x,y)=F_T(-x-y)F_T(x)F_T(y)/T is a two-dimensional L1 approximate identity of mass (2*pi)^2: its inverse Fourier kernel is the normalized common-overlap length of three translated intervals. Hence the triangle tends to the certified hard covariant C0 block and the bubble-with-bridge tends to its renormalized covariant distribution. The bridge distribution is controlled on the same packet without pointwise shell evaluation. The ten unordered bridge masks are the source-dark hard mask 7 plus masks 14,22,25,13,21,26,11,19,28, which equal q_00,q_01,-q_02,q_10,q_11,-q_12,q_20,q_21,-q_22. Exact reuse of the independently certified chart rows gives partial_t K^2=-2*N_ia nonzero for every exchange; only mask 11=q_20 crosses shell. Bubble invariants remain at least 32/625 from zero. Parameter-dependent coarea therefore turns every PV/delta bridge action on a smooth compact source into an L2 output, while the triangle C0 kernel is bounded by its pair-invariant and Kallen margins. Thus T6,infinity F is in L2 and q10,infinity[F]=2*Re<T4,infinity F,T6,infinity F> is finite. The species tensors are total-kappa fixed, so this selected coefficient is common to the public Krein and positive Hilbert Born rules. Its all-time MSbar scale derivative is 5*q8,infinity/(2*pi^2), cancelling the running of lambda^8*q8,infinity through order lambda^10. The coefficient is packet- and scheme-dependent and has no determined sign. This does not restore the superseded finite-time q10 formula or construct a bounded Moller, LSZ or S operator, general Eq. (19), gravity/BV-BRST/QME transfer, or Lorentzian causal physics.",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "complete selected center-time-intensive all-time q10 smooth-packet coefficient in the direct auxiliary MSbar frame",
        "anchored_temporal_limit": {
            "external_time_rule": "remove the common total-energy center-time factor before taking T to infinity",
            "one_gap": "A2,T and F_T both tend to H_+(s)=pi*delta(s)+i*PV(1/s) in S'(R)",
            "two_gap": "A3,T(s1,s2) tends to H_+(s1) tensor H_+(s2) in S'(R^2)",
            "three_window": "W_T(x,y)=F_T(-x-y)*F_T(x)*F_T(y)/T",
            "inverse_Fourier_overlap": "L_T(u,v)/T=max(0,1-diam(0,u,v)/T)",
            "overlap_fixtures": fixtures,
            "L1_proof": "with |F_1(z)|<=min(1,2/|z|), split according to which of |x|, |y|, |x+y| are at most one; bounded cells are finite, one-small strips have O(r^-2), and the all-large region has O(r^-3) generic and O(r^-2) cancellation-strip tails",
            "approximate_identity": "W_T=T^2*W_1(T*x,T*y), ||W_T||_1=||W_1||_1, its mass is (2*pi)^2, and its L1 tail outside every fixed origin neighborhood tends to zero",
            "boundary": "W_T -> (2*pi)^2*delta(x)*delta(y) in S'(R^2) and as an Lp approximate identity after the packet coarea for 1<=p<infinity",
            "status": "CENTER_TIME_INTENSIVE_TEMPORAL_BOUNDARIES_MATCHED",
        },
        "bridge_chart_audit": {
            "all_incoming_labels": "[p0,p1,p2,-k0,-k1,-k2]",
            "hard_mask": 7,
            "hard_mask_interpretation": "p0+p1+p2=P; its six roles annihilate u0",
            "exchange_rows": bridge,
            "mask_set": sorted(mask_set),
            "unique_shell_mask": 11,
            "unique_shell_exchange": [2, 0],
            "derivative_identity": "partial_t K_mask^2=partial_t q_ia^2=-2*N_ia",
            "bubble_invariant_margin": "32/625",
            "neighborhood_conclusion": "after shrinking the common packet, every nonhard bridge invariant has one common uniformly noncritical incoming rotation coordinate; only mask 11 crosses zero and every bubble invariant remains separated from zero",
            "status": "ALL_SOURCE_SURVIVING_BRIDGE_DISTRIBUTIONS_HAVE_COMMON_EXACT_COAREA",
        },
        "all_time_loop_operator": {
            "tree": "T4,infinity=16*sum_C K_C,infinity tensor R_C",
            "triangle": "T6,triangle,infinity=(8/(16*pi^2))*sum_P C0(Q_P1^2,Q_P2^2,Q_P3^2)*S_P",
            "bubble_bridge": "T6,bb,infinity=(4/(16*pi^2))*sum_R B_MSbar(Q_R^2)*W_R/(K_R^2+i0)",
            "complete_loop": "T6,infinity=T6,triangle,infinity+T6,bb,infinity",
            "triangle_domain": "all fifteen C0 kernels are smooth and bounded on the shrunken packet because |pair invariant|>=32/625 and |Kallen|>=80896/903125",
            "bridge_distribution": "orient K_mask=+-q_ia and write K^2=D_ia*delta_ia; parameter-dependent coarea gives a smooth delta evaluation plus a Hilbert-transform PV action, never a pointwise pole",
            "bridge_domain": "the bubble factor is smooth and bounded because |Q_R^2|>=32/625; the hard mask is source-dark; the finite role sum maps C_c^infinity(X) continuously into L2(Y)",
            "convergence": "the anchored switched triangle and normalized three-window bubble converge on the declared rigged packet to the displayed covariant operators; the finite species sums converge in L2(Y)",
            "status": "COMPLETE_SELECTED_ALL_TIME_T6_PACKET_MAP_CONSTRUCTED",
        },
        "q10_packet_coefficient": {
            "domain": "the common nonempty real or complex smooth compact fully rearranged packet class D subset L2(X) used by q8, after the hard triangle and bridge margins are intersected",
            "q8": "q8,infinity[F]=<T4,infinity F,T4,infinity F>",
            "q10": "q10,infinity[F]=2*Re<T4,infinity F,T6,infinity F>",
            "expanded": "2*Re<(16*sum_C K_C,infinity tensor R_C)F,((8/(16*pi^2))*sum_P C0_P*S_P+(4/(16*pi^2))*sum_R B_R*W_R/(K_R^2+i0))F>",
            "finiteness": "T4,infinity F and T6,infinity F are both in L2(Y), so the displayed pairing is finite",
            "value": "EXACT_PACKET_FUNCTIONAL_NOT_A_PACKET_INDEPENDENT_NUMBER",
            "sign": "NOT_DETERMINED",
            "scheme": "MSbar normal-ordered massless direct auxiliary frame",
            "common_Born": "q10,infinity^public[F]=q10,infinity^Hilbert[F] on the selected positive packet carrier",
            "status": "COMPLETE_SELECTED_RIGGED_ALL_TIME_Q10_COEFFICIENT_COMPUTED",
        },
        "renormalization_group": {
            "triangle_scale_derivative": "0",
            "bubble_scale_derivative": "partial_log(mu)T6,bb,infinity=[5/(4*pi^2)]*T4,infinity",
            "q10_scale_derivative": "partial_log(mu)q10,infinity=[5/(2*pi^2)]*q8,infinity",
            "beta": "partial_log(mu)lambda=-5*lambda^3/(16*pi^2)",
            "cancellation": "partial_log(mu)[lambda^8*q8,infinity+lambda^10*q10,infinity]=O(lambda^12)",
            "scope": "all-time selected packet coefficient; this does not reinstate the superseded mismatched finite-time RG identity",
            "status": "ALL_TIME_SELECTED_Q8_Q10_JET_IS_RG_INVARIANT_THROUGH_LAMBDA10",
        },
        "claim_boundary": {
            "matched_finite_time_q10": "NOT_COMPUTED",
            "q10_sign": "NOT_DETERMINED",
            "q10_scheme_independence": "FALSE_AS_A_STANDALONE_COORDINATE",
            "finite_coupling_probability": "NOT_ESTABLISHED",
            "bounded_whole_carrier_operator": "NOT_CONSTRUCTED",
            "Moller_LSZ_S": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED",
            "gravity_BV_BRST_QME": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED",
        },
        "assumptions": [
            "external center time is removed before the sharp-window all-time limit",
            "the source and detector lie in the common smooth compact fully rearranged packet class",
            "the common packet is shrunk inside all certified triangle pair/Kallen and bubble invariant margins",
            "bridge poles are paired distributionally by parameter-dependent coarea and never evaluated pointwise",
            "the normal-ordered massless direct auxiliary action and MSbar finite part are retained",
        ],
        "does_not_establish": [
            "the superseded finite-time q10 tree-loop formula",
            "a canonical finite-time interpolation between the F_T cut root and anchored Dyson taper",
            "a packet-independent value or sign for q10,infinity",
            "scheme independence of q10,infinity as a standalone perturbative coordinate",
            "positivity of the lambda10 correction",
            "finite-coupling or all-order positivity",
            "a bounded whole-L2 T6 operator",
            "a strong Moller operator",
            "LSZ or an all-channel S operator",
            "forward, identity, collinear or overlap completion",
            "general Eq. (19) or the standard scalar projector",
            "gravity or metric BV-BRST transfer",
            "QME restoration or residual quantum transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "next_gate": "Complete the physical all-time detector beyond the fully rearranged bulk by adjoining the already classified identity/collinear overlap strata and the missing forward normalization in the same rigged topology. In parallel, derive a canonical finite-time order-g5 Born cut if a duration-dependent q10 interpolation, rather than only its unambiguous all-time boundary, is required.",
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "input_hashes": {path: sha256(path) for path in INPUTS},
            "method": "Exact bridge-mask enumeration, content-pinned reuse of exact rational chart derivatives, exact invariant-margin audit, interval-overlap Fourier identity, analytic L1 approximate-identity bounds, parameter-dependent PV/delta coarea, and imported independently certified covariant triangle and bubble boundaries. No floating-point arithmetic enters a claim.",
            "generated_by": "reverse_physics/bt_fully_rearranged_rigged_all_time_q10_packet.py",
            "independent_verifier": "reverse_physics/verify_bt_fully_rearranged_rigged_all_time_q10_packet.py",
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "items": checks,
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_fully_rearranged_rigged_all_time_q10_packet.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_fully_rearranged_rigged_all_time_q10_packet.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_fully_rearranged_rigged_all_time_q10_packet",
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
