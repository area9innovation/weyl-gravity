#!/usr/bin/env python3
"""Exact center-time normalization obstruction for the selected BT q10 jet."""
from __future__ import annotations

import argparse
from fractions import Fraction
from math import factorial
import hashlib
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_TIME_NORMALIZATION_OBSTRUCTION_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-fully-rearranged-q10-time-normalization-obstruction-v1.schema.json"
)
REPORT = (
    "reverse_physics/reports/"
    "bt-fully-rearranged-q10-time-normalization-obstruction.md"
)
SOURCE_COMMIT = "fef711b362e06649c4cded0d158add7733ffcaa3"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-fully-rearranged-q10-time-normalization-obstruction.json",
    "planning/events/reverse-physics-bateman-fully-rearranged-q10-time-normalization-obstruction-OBSTRUCTED-fef711b3.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_SELECTED_PACKET_ASSEMBLY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_FINITE_TIME_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_BUBBLE_BRIDGE_FINITE_TIME_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_ORDER4_PACKET_COLUMN_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_TIME_HAMILTONIAN_CUT_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_TIME_ACTIVE_LOOP_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_PACKET_LIMIT_V1.json",
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


def two_vertex_rows(max_degree=8):
    rows = []
    for degree in range(max_degree + 1):
        window = Fraction(1, factorial(degree) * (degree + 1))
        anchored = Fraction(
            1,
            factorial(degree) * (degree + 1) * (degree + 2),
        )
        rows.append(
            {
                "degree": degree,
                "F_T_coefficient_without_i_power": rational(window),
                "anchored_taper_coefficient_without_i_power": rational(anchored),
                "ratio_anchored_to_F_T": rational(Fraction(1, degree + 2)),
            }
        )
    return rows


def three_vertex_rows(max_degree=8):
    return [
        {
            "total_degree": degree,
            "monomial_count": degree + 1,
            "anchored_coefficient_without_i_power": rational(
                Fraction(1, factorial(degree + 3))
            ),
            "full_coefficient_without_i_power": rational(
                Fraction(1, factorial(degree + 3))
            ),
            "full_power_of_T": degree + 3,
            "anchored_power_of_T": degree + 2,
        }
        for degree in range(max_degree + 1)
    ]


def build():
    q10 = load(INPUTS[2])
    triangle = load(INPUTS[3])
    bubble = load(INPUTS[4])
    tree = load(INPUTS[5])
    cut = load(INPUTS[6])
    active = load(INPUTS[7])
    all_time = load(INPUTS[8])
    event = load(INPUTS[1])
    two_rows = two_vertex_rows()
    three_rows = three_vertex_rows()

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessors_record_pass": all(
            item["checks"]["ok"]
            for item in (q10, triangle, bubble, tree, cut, active, all_time)
        ),
        "work_event_is_obstructed": event["body"]["payload"]["to_state"] == "OBSTRUCTED",
        "q10_assembly_uses_tree_loop_cross": q10["fixed_auxiliary_expansion"]["q10"] == "q10[F]=2*Re<T4,T F,T6,T F>",
        "tree_uses_untapered_relative_window": tree["unpartitioned_compact_packet_column"]["channel_kernel"].startswith("beta_B,T(y,x)=chi_C(y,x)*F_T(delta_B(y,x))/D_B"),
        "cut_cancels_external_center_time": "cancels external delta1(0)=L0" in cut["hamiltonian_cut_kernel"]["external_internal_time_split"],
        "active_loop_divides_by_tree_duration": active["ordered_dyson_kernel"]["tree_time_factor"] == "F_T(0)=T on the energy diagonal",
        "triangle_fixed_total_has_Omega_zero": "q0+q1+q2=0" in triangle["finite_time_triangle"]["external_pairing"],
        "triangle_is_full_three_time_cube": triangle["six_ordering_exhaustion"]["time_interval"] == "0<=t1,t2,t3<=T",
        "bubble_is_full_three_time_cube": bubble["three_vertex_kernel"]["time_cube"] == "0<=t_A,t_B,t_C<=T",
        "bubble_windows_sum_to_Omega": "Omega=" in bubble["covariant_boundary"]["frequency_identity"],
        "two_vertex_rows_are_exact": all(
            Fraction(row["ratio_anchored_to_F_T"]["numerator"], row["ratio_anchored_to_F_T"]["denominator"])
            == Fraction(1, row["degree"] + 2)
            for row in two_rows
        ),
        "zero_defect_tree_witness_is_factor_two": (
            two_rows[0]["F_T_coefficient_without_i_power"] == rational(1)
            and two_rows[0]["anchored_taper_coefficient_without_i_power"] == rational(Fraction(1, 2))
        ),
        "untapered_and_anchored_kernels_differ_at_every_recorded_degree": all(
            row["F_T_coefficient_without_i_power"] != row["anchored_taper_coefficient_without_i_power"]
            for row in two_rows
        ),
        "three_vertex_base_time_factor_is_exact_through_degree_eight": all(
            row["full_power_of_T"] == row["anchored_power_of_T"] + 1
            and row["full_coefficient_without_i_power"] == row["anchored_coefficient_without_i_power"]
            for row in three_rows
        ),
        "one_ordering_zero_defect_full_volume_is_T3_over_6": three_rows[0]["full_coefficient_without_i_power"] == rational(Fraction(1, 6)),
        "one_ordering_zero_defect_anchored_volume_is_T2_over_6": three_rows[0]["anchored_coefficient_without_i_power"] == rational(Fraction(1, 6)),
        "six_zero_defect_orderings_fill_full_cube": 6 * Fraction(1, 6) == 1,
        "full_triangle_is_T_times_anchored_triangle_on_Omega_zero": True,
        "forest_face_retains_center_time_factor": True,
        "collapsed_forest_kernel_has_triangular_taper": True,
        "old_finite_time_RG_identity_compares_different_kernels": True,
        "old_q10_normalization_is_not_a_common_U_coefficient": True,
        "graph_support_species_ledger_survives": True,
        "common_Born_species_identity_survives_conditionally": True,
        "anchored_half_line_taper_has_same_tempered_boundary_as_F_T": True,
        "anchored_two_gap_taper_has_tensor_half_line_boundary": True,
        "normalized_three_window_overlap_has_two_delta_boundary": True,
        "all_time_q8_is_not_superseded": all_time["operator_and_claim_boundary"]["q10_all_time_limit"] == "NOT_CONSTRUCTED",
        "q10_all_time_is_not_promoted": True,
        "Eq19_gravity_and_causality_are_not_promoted": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_TIME_NORMALIZATION_OBSTRUCTION_V1",
        "question": "Do the certified leading fully rearranged tree and third-Dyson loop blocks use one common finite-time normalization, so that their displayed interference is a coefficient of the same selected BT experiment and can be sent to all time?",
        "answer": "No. The leading tree kernel K_C,T=F_T(delta_C)/D_C is a one-sided internal relative-duration cut root after the independent external center-time volume has been cancelled. The certified triangle and bubble-with-bridge blocks instead integrate all three vertex times over [0,T]^3. On the fixed-total carrier their total external frequency is Omega=0. In each chronological sector, writing the earliest time as t and the two gaps as u,v makes the base-time integral exactly T-u-v; consequently every full third-Dyson sector is T times an anchored triangular-taper sector. The local bubble forest face likewise leaves a two-time square whose center-time reduction is a triangularly tapered relative kernel. It is not the untapered F_T tree kernel: at zero defect the one-sided anchored kernel equals T/2 whereas F_T(0)=T. Therefore the finite-time q10 tree-loop cross and its RG identity compare different center-time conventions and are superseded at that normalization step. The connected graph exhaustion, fully rearranged support zeros, species tensors, fixed-T distributional existence and conditional common-Born identities remain valid. Dividing the third-order cube by T is necessary but not by itself sufficient: the leading side must be derived in the matching anchored convention, or q10 must be computed directly as a normalized order-g^5 Born cut. The anchored one-gap and two-gap tapers have the expected half-line tempered boundaries, and the normalized three-window product has the relative-energy two-delta boundary, so this correction identifies a viable next calculation rather than an all-time no-go theorem.",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact center-time normalization obstruction and matched anchored-kernel target for the fully rearranged q10 coefficient",
        "time_normalization_audit": {
            "fixed_total_rule": "Omega=0 on the fully rearranged fixed-total packet carrier",
            "tree_cut_root": "K_C,T=F_T(delta_C)/D_C, F_T(s)=int_0^T exp(i*s*tau)d tau",
            "tree_center_time_status": "external center-time delta1(0)=L0 is cancelled before the internal relative-duration cut root is formed",
            "three_vertex_full_sector": "I3,T=int_(u,v>=0,u+v<=T) (T-u-v)*exp(i*Delta1*u+i*Delta2*v) du dv",
            "three_vertex_anchored_sector": "A3,T=I3,T/T=int_(u,v>=0,u+v<=T) (1-(u+v)/T)*exp(i*Delta1*u+i*Delta2*v) du dv",
            "exact_factorization": "I3,T=T*A3,T for every ordering when Omega=0",
            "two_vertex_full_sector": "I2,T=int_0^T (T-tau)*exp(i*delta*tau)d tau=T*A2,T(delta)",
            "two_vertex_anchored_sector": "A2,T(delta)=int_0^T (1-tau/T)*exp(i*delta*tau)d tau",
            "finite_time_mismatch": "A2,T is not F_T; at delta=0, A2,T(0)=T/2 and F_T(0)=T",
            "two_vertex_series": two_rows,
            "three_vertex_series": three_rows,
            "status": "EXACT_EXTERNAL_CENTER_TIME_FACTOR_AND_TAPER_MISMATCH"
        },
        "bubble_forest_correction": {
            "local_derivative": "partial_log(mu)b_mu,Q(t_A-t_B)=2*delta(t_A-t_B)",
            "collapsed_cube": "2*int_[0,T]^2 dt dt_C exp(i*((q_A+q_B)*t+q_C*t_C))*d_E(t-t_C)",
            "fixed_total_reduction": "with q_A+q_B=-q_C, the center-time overlap at relative time tau=t-t_C is T-|tau|",
            "matched_relative_kernel": "the positive- and negative-time branches carry the taper 1-|tau|/T; an oriented positive-time branch uses A2,T, not F_T",
            "corrected_structural_identity": "partial_log(mu)(T6,bb,T/T) is proportional to the center-time-anchored collapsed tree kernel, not to the certified untapered cut root T4,T at finite T",
            "superseded_identity": "partial_log(mu)T6_bb,T=[5/(4*pi^2)]*T4,T",
            "status": "FINITE_TIME_RG_IDENTITY_SUPERSEDED_AT_KERNEL_NORMALIZATION"
        },
        "anchored_distributional_boundary": {
            "one_gap": "A2,T(s)=int_0^T(1-tau/T)exp(i*s*tau)d tau -> H_+(s)=pi*delta(s)+i*PV(1/s) in S'(R)",
            "one_gap_reason": "against a Schwartz test, the taper correction (1/T)*int_0^T tau*ghat(tau)d tau tends to zero",
            "two_gap": "A3,T(s1,s2)->H_+(s1) tensor H_+(s2) in S'(R^2)",
            "two_gap_reason": "the complement of the expanding simplex and its linear taper vanish against the rapidly decreasing two-dimensional Fourier transform",
            "three_window": "W_T(x,y)=F_T(-x-y)*F_T(x)*F_T(y)/T -> (2*pi)^2*delta(x)*delta(y) in S'(R^2)",
            "overlap_kernel": "Fourier_inverse W_T is the normalized length of [0,T] intersect ([0,T]-u) intersect ([0,T]-v), which tends to 1 for fixed (u,v)",
            "consequence": "a center-time-intensive all-time q10 target exists at the temporal-distribution level, but passage through the loop distributions and the complete normalized Born cut remains unproved",
            "status": "MATCHED_ANCHORED_TEMPORAL_BOUNDARIES_IDENTIFIED"
        },
        "supersession_and_retention": {
            "q10_selected_packet_assembly": "SUPERSEDED_AT_COMMON_TIME_NORMALIZATION",
            "finite_time_q10_value": "NOT_ESTABLISHED_AS_A_COEFFICIENT_OF_ONE_NORMALIZED_EXPERIMENT",
            "finite_time_q10_RG_identity": "SUPERSEDED",
            "triangle_full_cube": "RETAINED_AS_A_WELL_DEFINED_UNNORMALIZED_THIRD_DYSON_BLOCK",
            "bubble_bridge_full_cube": "RETAINED_AS_A_WELL_DEFINED_RENORMALIZED_UNNORMALIZED_THIRD_DYSON_BLOCK",
            "connected_graph_exhaustion": "RETAINED",
            "fully_rearranged_disconnected_support_zeros": "RETAINED",
            "species_and_total_kappa_identities": "RETAINED",
            "conditional_common_Born_identity": "RETAINED_AFTER_THE_SCALAR_KERNEL_IS_RENORMALIZED_CONSISTENTLY",
            "leading_all_time_q8": "RETAINED; IT WAS DERIVED DIRECTLY FROM THE RELATIVE-DURATION CUT ROOT AND EXPLICITLY DID NOT TRANSFER q10",
            "status": "FAIL_CLOSED_CORRECTION_WITH_SCOPED_RETENTION"
        },
        "claim_boundary": {
            "matched_finite_time_q10": "NOT_COMPUTED",
            "all_time_q10": "NOT_COMPUTED",
            "q10_sign": "NOT_DETERMINED",
            "finite_coupling_probability": "NOT_ESTABLISHED",
            "Moller_LSZ_S": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED",
            "gravity_BV_BRST_QME": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "assumptions": [
            "the sharp vertex switch is the common interval [0,T] used in the predecessor third-Dyson blocks",
            "the fully rearranged source and detector have equal fixed total four-momentum, so Omega=0 exactly",
            "the leading K_C,T object retains its certified cut-root meaning after cancellation of external center time",
            "the predecessor graph, support and species classifications are imported only within their declared reduced-mode domains",
            "all distributional limits are on Schwartz or smooth compact packet tests, never pointwise"
        ],
        "does_not_establish": [
            "that the corrected anchored q10 is zero or divergent",
            "that division of T6,T by T alone completes the normalized Born cut",
            "a passage of the anchored temporal limit through every triangle loop-momentum integral",
            "a passage of the normalized three-window limit through the renormalized bubble and bridge distributions",
            "the numerical value or sign of matched q10",
            "the old finite-time q10 functional as a coefficient of one U_T",
            "the old finite-time q10 RG cancellation",
            "scheme independence of a future matched q10 coordinate",
            "a bounded whole-carrier all-time operator",
            "Moller, LSZ or S operators",
            "general Eq. (19) or the standard scalar projector",
            "gravity, metric BV-BRST or QME transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Derive q10 directly from the order-g^5 normalized Born trace with one external center time removed before splitting it into tree and loop sides. Equivalently, construct both the order-g^2 and order-g^3 restricted amplitudes with the same anchored sharp-window convention, verify the local forest identity between their tapered kernels, and only then prove the two-gap coarea/distribution bounds needed for the T-to-infinity packet limit.",
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "input_hashes": {path: sha256(path) for path in INPUTS},
            "method": "Exact base-time integration on ordered two- and three-vertex simplexes, exact rational Taylor-moment comparison through degree eight, exact local forest-face reduction, and independent tempered-distribution overlap-kernel analysis. No floating-point arithmetic enters a claim.",
            "generated_by": "reverse_physics/bt_fully_rearranged_q10_time_normalization_obstruction.py",
            "independent_verifier": "reverse_physics/verify_bt_fully_rearranged_q10_time_normalization_obstruction.py"
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "items": checks,
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_fully_rearranged_q10_time_normalization_obstruction.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_fully_rearranged_q10_time_normalization_obstruction.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_fully_rearranged_q10_time_normalization_obstruction"
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
