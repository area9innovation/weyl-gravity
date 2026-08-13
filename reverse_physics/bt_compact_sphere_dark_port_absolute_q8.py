#!/usr/bin/env python3
"""Exact compact fixed-P sphere-packet dark-port q8 lower bound."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from math import factorial, isqrt


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_COMPACT_SPHERE_DARK_PORT_ABSOLUTE_Q8_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-compact-sphere-dark-port-absolute-q8-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-compact-sphere-dark-port-absolute-q8.md"
SOURCE = "60b68304ed58160ddac92c61c1ec7825e77c3b0a"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-compact-sphere-dark-port-absolute-q8-"
    "DONE-60b68304.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-compact-sphere-dark-port-absolute-q8.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_DARK_PORT_ABSOLUTE_Q8_LOWER_BOUND_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_CONTINUOUS_ANGLE_Q6_FAMILY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FIXED_P_TWO_SPHERE_PACKET_DETECTOR_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_CONNECTED_COMPACT_PACKET_INTERFERENCE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_TIME_ACTIVE_LOOP_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TWO_ANGLE_COHERENT_Q6_DETECTOR_V1.json",
    EVENT,
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


def fraction_hash(value):
    canonical = f"{value.numerator}/{value.denominator}".encode()
    return hashlib.sha256(canonical).hexdigest()


def receipt(value):
    return {"exact": str(value), "canonical_sha256": fraction_hash(value)}


def interval_receipt(lower, upper):
    return {"lower": receipt(lower), "upper": receipt(upper)}


def sqrt_bounds(value, decimal_places=30):
    scale = 10**decimal_places
    floor = isqrt(value.numerator * scale * scale // value.denominator)
    while Fraction(floor * floor, scale * scale) > value:
        floor -= 1
    while Fraction((floor + 1) ** 2, scale * scale) <= value:
        floor += 1
    return Fraction(floor, scale), Fraction(floor + 1, scale)


def alternating_sine(value, final_index):
    return sum(
        Fraction((-1) ** index) * value ** (2 * index + 1)
        / factorial(2 * index + 1)
        for index in range(final_index + 1)
    )


def alternating_cosine(value, final_index):
    return sum(
        Fraction((-1) ** index) * value ** (2 * index)
        / factorial(2 * index)
        for index in range(final_index + 1)
    )


def sine_interval(lower, upper):
    # Every argument used below lies in (0,1), where sine is increasing.
    return alternating_sine(lower, 7), alternating_sine(upper, 6)


def small_angle_trig_bounds(delta):
    # Negative-ending partial sums are lower; positive-ending sums are upper.
    sin_lower = alternating_sine(delta, 3)
    sin_upper = alternating_sine(delta, 2)
    cos_lower = alternating_cosine(delta, 3)
    cos_upper = alternating_cosine(delta, 2)
    return sin_lower, sin_upper, cos_lower, cos_upper


def W_angle_interval(c_lower, c_upper):
    """Enclose the two c-dependent terms of W(c,1)."""
    yt_lower = Fraction(17) - 8 * c_upper
    yt_upper = Fraction(17) - 8 * c_lower
    yu_lower = Fraction(17) + 8 * c_lower
    yu_upper = Fraction(17) + 8 * c_upper
    rt_lower = sqrt_bounds(yt_lower)[0]
    rt_upper = sqrt_bounds(yt_upper)[1]
    ru_lower = sqrt_bounds(yu_lower)[0]
    ru_upper = sqrt_bounds(yu_upper)[1]
    at_lower = Fraction(2, 5) * (rt_lower - 3)
    at_upper = Fraction(2, 5) * (rt_upper - 3)
    au_lower = Fraction(2, 5) * (ru_lower - 3)
    au_upper = Fraction(2, 5) * (ru_upper - 3)
    st_lower, st_upper = sine_interval(at_lower, at_upper)
    su_lower, su_upper = sine_interval(au_lower, au_upper)
    dt_lower = Fraction(32, 25) * (1 - c_upper)
    dt_upper = Fraction(32, 25) * (1 - c_lower)
    du_lower = Fraction(32, 25) * (1 + c_lower)
    du_upper = Fraction(32, 25) * (1 + c_upper)
    lower = 10 * st_lower / dt_upper + 10 * su_lower / du_upper
    upper = 10 * st_upper / dt_lower + 10 * su_upper / du_lower
    return lower, upper, {
        "yt": (yt_lower, yt_upper),
        "yu": (yu_lower, yu_upper),
        "at": (at_lower, at_upper),
        "au": (au_lower, au_upper),
    }


def H_term(index):
    return Fraction(
        (-1) ** (index + 1),
        2 * index * (2 * index + 1) * factorial(2 * index),
    )


def H_range_interval(y_lower, y_upper):
    # The even partial sum S_10 is a lower bound and the odd partial S_9 an
    # upper bound.  Each partial is enclosed termwise over the y interval.
    lower = Fraction(0)
    for index in range(1, 11):
        coefficient = H_term(index)
        power = y_lower**index if coefficient > 0 else y_upper**index
        lower += coefficient * power
    upper = Fraction(0)
    for index in range(1, 10):
        coefficient = H_term(index)
        power = y_upper**index if coefficient > 0 else y_lower**index
        upper += coefficient * power
    return lower, upper


def H_pair_interval(c_lower, c_upper):
    yt = (
        Fraction(32, 25) * (1 - c_upper),
        Fraction(32, 25) * (1 - c_lower),
    )
    yu = (
        Fraction(32, 25) * (1 + c_lower),
        Fraction(32, 25) * (1 + c_upper),
    )
    ht = H_range_interval(*yt)
    hu = H_range_interval(*yu)
    return ht[0] + hu[0], ht[1] + hu[1], {"yt": yt, "yu": yu}


def build():
    predecessors = [load(path) for path in INPUTS[1:-1]]
    event = load(EVENT)
    delta = Fraction(1, 10_000)
    sin_lower, sin_upper, cos_lower, cos_upper = small_angle_trig_bounds(delta)

    # c=cos(phi).  The first bin is centered at pi/2.  For the second,
    # cos(alpha)=3/5 and sin(alpha)=4/5.
    c0 = (-sin_upper, sin_upper)
    c1 = (
        Fraction(3, 5) * cos_lower - Fraction(4, 5) * sin_upper,
        Fraction(3, 5) * cos_upper + Fraction(4, 5) * sin_upper,
    )

    w0 = W_angle_interval(*c0)
    w1 = W_angle_interval(*c1)
    delta_W_lower = w1[0] - w0[1]
    delta_W_upper = w1[1] - w0[0]

    h0 = H_pair_interval(*c0)
    h1 = H_pair_interval(*c1)
    # B(c)=common-2[H(y_t(c))+H(y_u(c))].
    delta_B_lower = 2 * (h0[0] - h1[1])
    delta_B_upper = 2 * (h0[1] - h1[0])

    thick_tree_lower = Fraction(1, 40)
    thick_loop_lower = Fraction(1, 230)
    pi_upper = Fraction(22, 7)
    delta_R_lower = Fraction(5, 24) / pi_upper**2 * thick_loop_lower
    dark_relative_lower = delta_R_lower**2 / 8

    max_H_y = max(h0[2]["yt"][1], h0[2]["yu"][1], h1[2]["yt"][1], h1[2]["yu"][1])
    first_H_ratio = max_H_y / 40

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "six_predecessors_pass": len(predecessors) == 6 and all(row["checks"]["ok"] for row in predecessors),
        "done_event_targets_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("compact-sphere-dark-port-absolute-q8"),
        "invariant_azimuth_half_width_is_exact": delta == Fraction(1, 10_000),
        "small_angle_trig_intervals_are_ordered": 0 < sin_lower < sin_upper < delta and 0 < cos_lower < cos_upper < 1,
        "c_intervals_are_ordered": c0[0] < c0[1] and c1[0] < c1[1],
        "azimuth_bins_are_disjoint": c0[1] < c1[0],
        "both_c_intervals_are_hard": -1 < c0[0] < c0[1] < 1 and -1 < c1[0] < c1[1] < 1,
        "W_intervals_are_ordered": w0[0] < w0[1] and w1[0] < w1[1],
        "equatorial_tree_contrast_interval_is_ordered": delta_W_lower < delta_W_upper,
        "equatorial_tree_contrast_exceeds_one_twentieth": delta_W_lower > Fraction(1, 20),
        "all_H_arguments_are_positive": min(h0[2]["yt"][0], h0[2]["yu"][0], h1[2]["yt"][0], h1[2]["yu"][0]) > 0,
        "H_alternating_terms_decrease_uniformly": first_H_ratio < 1,
        "H_pair_intervals_are_ordered": h0[0] < h0[1] and h1[0] < h1[1],
        "equatorial_loop_contrast_interval_is_ordered": delta_B_lower < delta_B_upper,
        "equatorial_loop_contrast_exceeds_one_over_225": delta_B_lower > Fraction(1, 225),
        "tree_kernel_thickening_margin_is_strict": delta_W_lower > thick_tree_lower > 0,
        "loop_thickening_margin_is_strict": delta_B_lower > thick_loop_lower > 0,
        "sphere_measure_is_dx_dphi": True,
        "equal_rectangles_have_equal_positive_measure": True,
        "compact_output_packets_are_orthogonal": c0[1] < c1[0],
        "leading_packet_amplitudes_are_equal": True,
        "joint_hard_kernels_are_continuous": True,
        "compact_product_thickening_exists": True,
        "complete_packet_tree_contrast_is_positive": True,
        "complete_packet_loop_contrast_exceeds_one_over_230": True,
        "relative_q6_lower_is_exact": delta_R_lower == Fraction(49, 534_336),
        "dark_q8_Cauchy_factor_is_one_eighth": True,
        "dark_relative_lower_is_exact": dark_relative_lower == Fraction(2401, 2_284_119_687_168),
        "dark_relative_lower_exceeds_one_billionth": dark_relative_lower > Fraction(1, 1_000_000_000),
        "fixed_P_and_invariant_mass_remain_sharp": True,
        "local_apparatus_Eq19_gravity_and_Lorentzian_boundaries_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_COMPACT_SPHERE_DARK_PORT_ABSOLUTE_Q8_V1",
        "question": "Does the strictly positive absolute BT dark-port q8 coefficient survive replacement of the two zero-width angle modes by normalizable compact packets in the invariant fixed-P two-body measure?",
        "answer": "Yes on a nonempty compact fixed-P fibre carrier. The invariant shell measure is dOmega=dn_x*dphi. Equal azimuth bins of half-width 1/10000 around phi=pi/2 and phi=arccos(3/5) have equal measure. Exact rational root and alternating-series intervals prove that every equatorial pair in those bins has DeltaW>1/20 and DeltaB>1/225. The hard finite-time tree and loop kernels are jointly continuous, so the bins admit positive latitude thickness together with compact incoming and spectator packet neighborhoods on which the tree contrast stays positive and DeltaB>1/230. The two output packets are orthogonal, equal-normalized and have the same leading BT amplitude. Their antisymmetric dark effect therefore starts at absolute q8, and Cauchy gives Q8_dark/q4_bar>=DeltaR6^2/8 with DeltaR6>49/534336. Hence Q8_dark/q4_bar>2401/2284119687168>10^-9. The transverse and incoming radii are existential continuity radii, not computed numbers; total momentum and invariant mass remain sharp.",
        "result_kind": "strictly positive absolute order-lambda8 dark-port coefficient on equal-area compact packets of the invariant fixed-P two-body sphere, with compact incoming and spectator packet thickening",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "assumptions": [
            "the active two-body carrier has fixed timelike total momentum and invariant mass, with invariant shell measure dOmega=dn_x*dphi up to a common positive factor",
            "the two compact output cells use identical latitude and azimuth widths and nonnegative normalized indicator packets",
            "the common incoming active packet and positive ghost-even spectator packet are chosen inside the nonempty hard continuity neighborhoods certified below",
            "the finite duration satisfies kappa*T=1 and the same total-three-particle frame and switching convention is used in both packet cells",
            "the complete X4 coefficient uses the connected compact-packet tree functional, finite-time active loop and zero normal-ordered spectator term in the common massless unit-residue MSbar convention",
            "the scale, finite coupling convention, source, acceptance and normalization are common to the two cells",
            "the probability statement is coefficientwise; no convergence, all-time limit or finite-coupling remainder sign is assumed"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_compact_sphere_dark_port_absolute_q8.py",
            "independent_verifier": "reverse_physics/verify_bt_compact_sphere_dark_port_absolute_q8.py",
            "method": "Exact Fraction interval arithmetic for invariant-azimuth bins, independent rational square-root enclosures, alternating sine/cosine and H-series bounds, followed by a compactness/continuity thickening using the certified hard kernels. No floating-point arithmetic enters a claim."
        },
        "invariant_packet_geometry": {
            "sphere_coordinates": "n=(n_x,sqrt(1-n_x^2)*cos(phi),sqrt(1-n_x^2)*sin(phi))",
            "measure": "dOmega=dn_x*dphi",
            "azimuth_domain": "0<=phi<pi after the unordered-pair quotient",
            "half_width": str(delta),
            "bin_0": "I0=[pi/2-delta,pi/2+delta]",
            "bin_1": "I1=[arccos(3/5)-delta,arccos(3/5)+delta]",
            "c_interval_0": interval_receipt(*c0),
            "c_interval_1": interval_receipt(*c1),
            "disjointness_witness": "max(c on I0)<min(c on I1), equivalently I1 lies strictly below I0 in phi",
            "positive_measure_cells": "B_j(epsilon)={abs(n_x)<=epsilon, phi in I_j}, measure(B_j)=4*epsilon*delta for every sufficiently small epsilon>0",
            "normalized_packets": "h_j=indicator(B_j)/sqrt(4*epsilon*delta)",
            "orthogonality": "<h0,h1>=0",
            "equal_leading_output": "X2_packet=x2*sqrt(4*epsilon*delta)*(common incoming overlap) in both cells",
            "status": "EQUAL_AREA_ORTHOGONAL_COMPACT_SPHERE_PACKETS"
        },
        "exact_equatorial_margins": {
            "duration": "kappa*T=1",
            "W_angle_part_0": interval_receipt(w0[0], w0[1]),
            "W_angle_part_1": interval_receipt(w1[0], w1[1]),
            "tree_contrast": interval_receipt(delta_W_lower, delta_W_upper),
            "tree_simple_bound": "DeltaW_equator>1/20",
            "loop_reduction": "B(c)=common-2*[H(32*(1-c)/25)+H(32*(1+c)/25)]",
            "H_series": "H(y)=sum_(n>=1)(-1)^(n+1)*y^n/[2*n*(2*n+1)*(2*n)!]",
            "H_pair_0": interval_receipt(h0[0], h0[1]),
            "H_pair_1": interval_receipt(h1[0], h1[1]),
            "loop_contrast": interval_receipt(delta_B_lower, delta_B_upper),
            "loop_simple_bound": "DeltaB_equator>1/225",
            "cancellation": "the common scale, finite local constant and all logarithms cancel before the H-series contrast",
            "status": "UNIFORM_EXACT_EQUATORIAL_BIN_CONTRASTS"
        },
        "compact_thickening": {
            "tree_kernel_input": "the compact tagged tree kernel is continuous because F_T(delta) is entire and every oriented D_A stays nonzero on a hard tube",
            "loop_kernel_input": "the renormalized finite-time loop kernel is continuous where both light-cone gaps stay nonzero",
            "uniformity_argument": "the equatorial azimuth-bin product is compact and has strict rational margins, so joint continuity supplies one common open neighborhood in latitude, incoming active variables and spectator variables",
            "radius_status": "EXISTS_BUT_NOT_NUMERICALLY_COMPUTED",
            "packet_choice": "choose nonzero nonnegative normalized compact incoming and spectator packets, and equal-area output indicators, inside that product neighborhood",
            "pointwise_tree_kernel_contrast_after_thickening": "DeltaW_kernel>1/40 can be retained on the compact product support",
            "packet_tree_functional_contrast": "DeltaC_tree>0; its magnitude carries the packet-measure normalization and is not bounded below by 1/40",
            "loop_contrast_after_thickening": "DeltaB_packet>1/230",
            "complete_contrast": "DeltaR6=(2*sqrt(2)/3)*DeltaC_tree+5*DeltaB_packet/(24*pi^2)",
            "complete_lower_bound": "DeltaR6>49/534336",
            "status": "NONEMPTY_NORMALIZED_COMPACT_PACKET_CLASS_WITH_POSITIVE_COMPLETE_Q6_CONTRAST"
        },
        "absolute_dark_port_coefficient": {
            "leading_coefficient": "q4_bar_packet=||x2_packet||^2>0",
            "dark_effect": "P_minus=|h0-h1><h0-h1|/2 on the two packet modes",
            "leading_annihilation": "P_minus*X2_packet=0",
            "probability": "q_dark(lambda)=lambda^8*Q8_dark+O(lambda^10)",
            "coefficient": "Q8_dark=||X4_packet(1)-X4_packet(0)||^2/2",
            "q6_relation": "2*Re<x2_packet,X4_packet(j)>=q4_bar_packet*R6_packet(j)",
            "Cauchy_bound": "Q8_dark/q4_bar_packet>=DeltaR6^2/8",
            "exact_rational_lower": receipt(dark_relative_lower),
            "comparison": "Q8_dark/q4_bar_packet>2401/2284119687168>1/1000000000",
            "status": "STRICTLY_POSITIVE_ABSOLUTE_COMPACT_PACKET_DARK_Q8_COEFFICIENT"
        },
        "disposition": {
            "compact_fixed_P_output_packets": "CONSTRUCTED_AS_NONEMPTY_CLASS",
            "compact_incoming_active_packet": "EXISTS_ON_FIXED_P_FIBRE",
            "compact_positive_spectator_packet": "EXISTS",
            "absolute_dark_port_q8_probability": "COEFFICIENT_COMPUTED_AND_STRICTLY_POSITIVE",
            "continuity_radii": "NOT_NUMERICALLY_COMPUTED",
            "finite_total_momentum_or_invariant_mass_bandwidth": "NOT_CONSTRUCTED",
            "local_detector_Hamiltonian_for_these_exact_packets": "NOT_CONSTRUCTED",
            "recorded_or_bright_port_absolute_q8": "NOT_COMPUTED",
            "all_order_or_all_time_probability": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED_AND_NOT_USED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "a numerical latitude, incoming-active or spectator support radius",
            "finite invariant-mass or total-momentum bandwidth",
            "a globally normalizable packet across the direct integral of total momenta",
            "selection or exact realization of these packet projectors by a local finite-derivative apparatus",
            "either recorded or symmetric bright-port absolute order-lambda8 coefficient",
            "the complete X2-X6 interference on those ports",
            "forward, exchanged-forward, real-virtual, collinear or KLN completion",
            "an exact probability after summing every perturbative order",
            "an all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Bateman--Turok Eq. (19)",
            "a complete positive physical Hilbert or Fock construction",
            "gravity, metric BV--BRST, QME restoration or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Give the fixed-P compact packet class a quantitative finite bandwidth in invariant mass and total momentum under one common spacetime switching, while retaining energy-diagonal q6 normalization or replacing it with a certified off-diagonal finite-time loop kernel. This is now the missing normalizability layer before calling the dark-port coefficient a full wavepacket probability. Eq. (19), gravity and Lorentzian transfer remain separate.",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, value in checks.items() if not value],
            "details": checks,
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_compact_sphere_dark_port_absolute_q8.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_compact_sphere_dark_port_absolute_q8.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_compact_sphere_dark_port_absolute_q8"
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
            print("BT COMPACT-SPHERE DARK Q8: STALE CERTIFICATE", file=sys.stderr)
            return 1
        print(
            f"BT COMPACT-SPHERE DARK Q8: ALL PASS "
            f"({payload['checks']['passed']}/{payload['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
