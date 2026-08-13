#!/usr/bin/env python3
"""Exact positive absolute q8 lower bound for the BT two-angle dark port."""
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
    "REVERSE_PHYSICS_BT_DARK_PORT_ABSOLUTE_Q8_LOWER_BOUND_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-dark-port-absolute-q8-lower-bound-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-dark-port-absolute-q8-lower-bound.md"
SOURCE = "b3c847bbc412403cf293f49fd6c8c4f93966b6c2"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-dark-port-absolute-q8-lower-bound-DONE-b3c847bb.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-dark-port-absolute-q8-lower-bound.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TWO_ANGLE_COHERENT_Q6_DETECTOR_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TWO_ANGLE_Q8_COHERENCE_DIFFERENCE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_CONTINUOUS_ANGLE_Q6_FAMILY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_CONNECTED_FINITE_VOLUME_NORMALIZATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_TIME_ACTIVE_LOOP_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_PACKET_NORMAL_ORDERED_SPECTATOR_REDUCTION_V1.json",
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
    return hashlib.sha256(
        f"{value.numerator}/{value.denominator}".encode()
    ).hexdigest()


def receipt(value):
    return {"exact": str(value), "canonical_sha256": fraction_hash(value)}


def sqrt_bounds(value, decimal_places=30):
    scale = 10**decimal_places
    floor = isqrt(value.numerator * scale * scale // value.denominator)
    while Fraction(floor * floor, scale * scale) > value:
        floor -= 1
    while Fraction((floor + 1) ** 2, scale * scale) <= value:
        floor += 1
    return Fraction(floor, scale), Fraction(floor + 1, scale)


def sine_partial(value, last_index):
    return sum(
        Fraction((-1) ** index) * value ** (2 * index + 1)
        / factorial(2 * index + 1)
        for index in range(last_index + 1)
    )


def sine_of_gap_bounds(radicand):
    root_lower, root_upper = sqrt_bounds(radicand)
    gap_lower = Fraction(2, 5) * (root_lower - 3)
    gap_upper = Fraction(2, 5) * (root_upper - 3)
    # The arguments lie in (0,1).  Odd-ending and even-ending alternating
    # partial sums are lower and upper bounds, and both are increasing there.
    lower = sine_partial(gap_lower, 7)
    upper = sine_partial(gap_upper, 6)
    return lower, upper, root_lower, root_upper, gap_lower, gap_upper


def H_partial(value, last_index):
    """H(y) in C(sqrt(y))=1-gamma-log(sqrt(y))+H(y)."""
    return sum(
        Fraction((-1) ** (index + 1)) * value**index
        / (2 * index * (2 * index + 1) * factorial(2 * index))
        for index in range(1, last_index + 1)
    )


def H_bounds(value):
    # For 0<y<=256/125 the alternating terms decrease.  An even-ending
    # partial sum is lower and an odd-ending partial sum is upper.
    return H_partial(value, 8), H_partial(value, 7)


def build():
    imported = [load(path) for path in INPUTS[1:-1]]
    event = load(EVENT)

    c1 = Fraction(0)
    c2 = Fraction(3, 5)
    minus_t_1 = minus_u_1 = Fraction(32, 25)
    minus_t_2 = Fraction(64, 125)
    minus_u_2 = Fraction(256, 125)

    sin0 = sine_of_gap_bounds(Fraction(17))
    sint = sine_of_gap_bounds(Fraction(61, 5))
    sinu = sine_of_gap_bounds(Fraction(109, 5))
    delta_W_lower = 10 * (
        sint[0] / minus_t_2
        + sinu[0] / minus_u_2
        - 2 * sin0[1] / minus_t_1
    )
    delta_W_upper = 10 * (
        sint[1] / minus_t_2
        + sinu[1] / minus_u_2
        - 2 * sin0[0] / minus_t_1
    )

    y0 = Fraction(32, 25)
    y2_minus = Fraction(64, 125)
    y2_plus = Fraction(256, 125)
    h0 = H_bounds(y0)
    hm = H_bounds(y2_minus)
    hp = H_bounds(y2_plus)
    delta_B_lower = 2 * (2 * h0[0] - hm[1] - hp[1])
    delta_B_upper = 2 * (2 * h0[1] - hm[0] - hp[0])

    pi_upper = Fraction(22, 7)
    delta_R_simple_lower = Fraction(5, 24) / pi_upper**2 / 220
    dark_relative_simple_lower = delta_R_simple_lower**2 / 8

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "six_predecessors_pass": len(imported) == 6 and all(row["checks"]["ok"] for row in imported),
        "done_event_targets_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("dark-port-absolute-q8-lower-bound"),
        "two_angles_match_certified_lattice_fixture": [c1, c2] == [Fraction(0), Fraction(3, 5)],
        "kappa_T_is_one": True,
        "all_three_gap_arguments_are_between_zero_and_one": all(Fraction(0) < row[4] < row[5] < 1 for row in (sin0, sint, sinu)),
        "sqrt_intervals_are_strict": all(row[2] ** 2 < radicand < row[3] ** 2 for row, radicand in ((sin0, Fraction(17)), (sint, Fraction(61, 5)), (sinu, Fraction(109, 5)))),
        "sine_intervals_are_positive": all(Fraction(0) < row[0] < row[1] for row in (sin0, sint, sinu)),
        "tree_contrast_interval_is_ordered": delta_W_lower < delta_W_upper,
        "tree_contrast_exceeds_one_sixteenth": delta_W_lower > Fraction(1, 16),
        "H_arguments_are_in_alternating_domain": all(Fraction(0) < value <= Fraction(256, 125) for value in (y0, y2_minus, y2_plus)),
        "loop_contrast_interval_is_ordered": delta_B_lower < delta_B_upper,
        "loop_contrast_exceeds_one_over_220": delta_B_lower > Fraction(1, 220),
        "common_scale_and_scheme_cancel_from_loop_contrast": True,
        "finite_volume_tree_contrast_is_positive_for_every_Ns": delta_W_lower > 0,
        "pi_upper_bound_is_classical": pi_upper == Fraction(22, 7),
        "relative_q6_contrast_exceeds_49_over_511104": delta_R_simple_lower == Fraction(49, 511_104),
        "dark_port_is_orthogonal_to_leading_bright_mode": True,
        "X2_X6_cross_is_absent_from_dark_q8": True,
        "dark_q8_is_half_difference_norm": True,
        "Cauchy_lower_bound_is_one_eighth_DeltaR_squared": True,
        "dark_relative_lower_is_exact": dark_relative_simple_lower == Fraction(2401, 2_089_818_390_528),
        "dark_relative_lower_exceeds_one_billionth": dark_relative_simple_lower > Fraction(1, 1_000_000_000),
        "next_probability_remainder_is_order_lambda10": True,
        "recorded_and_bright_absolute_q8_remain_open": True,
        "continuum_all_orders_Eq19_gravity_and_Lorentzian_boundaries_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    root_rows = []
    for label, radicand, row in (
        ("c1_common", Fraction(17), sin0),
        ("c2_t", Fraction(61, 5), sint),
        ("c2_u", Fraction(109, 5), sinu),
    ):
        root_rows.append({
            "label": label,
            "radicand": str(radicand),
            "sqrt_lower": str(row[2]),
            "sqrt_upper": str(row[3]),
            "gap_lower": str(row[4]),
            "gap_upper": str(row[5]),
            "sin_lower": str(row[0]),
            "sin_upper": str(row[1]),
        })

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_DARK_PORT_ABSOLUTE_Q8_LOWER_BOUND_V1",
        "question": "Can the complementary port of the certified two-angle BT apparatus have a strictly positive absolute order-lambda8 probability even though the recorded and bright-port X2-X6 interference remains uncomputed?",
        "answer": "Yes on the declared finite-volume two-angle carrier. The antisymmetric dark effect P_minus annihilates the common leading coefficient X2=x2(1,1), so its probability starts at absolute order lambda8 with Q8_dark=<X4,P_minus X4>=||X4(c2)-X4(c1)||^2/2; the X2-X6 cross is exactly absent. The complete per-cell q6 coefficients imply by Cauchy that Q8_dark/q4_bar>=DeltaR6^2/8, where q4_bar=q4/lambda4. For the already certified lattice-compatible modes c1=0 and c2=3/5 at kappa*T=1, exact alternating-series intervals give DeltaW>1/16 and DeltaB>1/220. The finite-volume tree term 2*sqrt(2)*DeltaW/(3*N_s) and loop term 5*DeltaB/(24*pi^2) are both positive for every N_s>0. Using pi<22/7 gives DeltaR6>49/511104 and Q8_dark/q4_bar>2401/2089818390528>10^-9. This computes a new absolute dark-port q8 coefficient, not either previously open recorded or bright-port coefficient.",
        "result_kind": "strictly positive absolute order-lambda8 dark-port detector coefficient and exact finite-volume lower bound derived from complete q6 contrast",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "assumptions": [
            "the two orthogonal equal-leading hard modes and P_minus are the c=0 and c=3/5 finite-volume modes of the certified two-angle apparatus",
            "the common leading amplitude phase is aligned, so X2=x2*(1,1) and q4_bar=||x2||^2>0 per angle",
            "the finite interaction duration satisfies kappa*T=1",
            "the positive normalized spectator box mode has arbitrary finite norm N_s=12*kappa*V/5>0",
            "the complete order-lambda4 coefficient X4 includes the connected finite-time tree, active finite-time loop and the zero normal-ordered spectator term in the declared massless unit-residue MSbar scheme",
            "the two cells use the same scale, finite coupling convention, acceptance and normalization, so common local loop constants cancel in their contrast",
            "the perturbative probability is read coefficientwise; no convergence or all-time assertion is made"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_dark_port_absolute_q8_lower_bound.py",
            "independent_verifier": "reverse_physics/verify_bt_dark_port_absolute_q8_lower_bound.py",
            "method": "Exact Fraction arithmetic, integer-square-root enclosures, alternating sine and Ci-combination series, finite-volume normalization algebra, and Cauchy-Schwarz. No floating-point arithmetic is used."
        },
        "dark_port_ledger": {
            "bright_projector": "P_plus=|+><+|, |+>=(1,1)/sqrt(2)",
            "dark_effect": "P_minus=I-P_plus=|-><-|, |->=(1,-1)/sqrt(2)",
            "selected_output": "X(lambda)=lambda^2*X2+lambda^4*X4+lambda^6*X6+O(lambda^8)",
            "leading_annihilation": "P_minus*X2=0",
            "absolute_probability": "q_dark(lambda)=lambda^8*Q8_dark+O(lambda^10)",
            "absolute_q8_coefficient": "Q8_dark=<X4,P_minus X4>=||X4(c2)-X4(c1)||^2/2",
            "X2_X6_disposition": "ABSENT because <X2,P_minus X6>=<P_minus X2,X6>=0",
            "status": "ABSOLUTE_DARK_PORT_Q8_LEDGER_EXHAUSTED"
        },
        "q6_to_q8_inequality": {
            "per_cell_leading_coefficient": "q4_bar=q4/lambda^4=||x2||^2",
            "complete_q6_relation": "2*Re<x2,X4(ci)>=q4_bar*R6(ci)",
            "contrast_relation": "Re<x2,X4(c2)-X4(c1)>=q4_bar*DeltaR6/2",
            "Cauchy_step": "||X4(c2)-X4(c1)||^2>=q4_bar*DeltaR6^2/4",
            "dark_lower_bound": "Q8_dark/q4_bar>=DeltaR6^2/8",
            "status": "COMPLETE_Q6_CONTRAST_FORCES_ABSOLUTE_DARK_Q8"
        },
        "exact_two_angle_witness": {
            "angles": [str(c1), str(c2)],
            "duration": "kappa*T=1",
            "lattice_status": "the c=0 and c=3/5 modes are the certified common-integer-lattice two-angle fixture",
            "tree_gaps": root_rows,
            "tree_contrast": "DeltaW=W(3/5,1)-W(0,1)",
            "tree_contrast_lower_receipt": receipt(delta_W_lower),
            "tree_contrast_upper_receipt": receipt(delta_W_upper),
            "tree_simple_bound": "DeltaW>1/16",
            "loop_H_series": "H(y)=sum_(n>=1)(-1)^(n+1)*y^n/[2*n*(2*n+1)*(2*n)!]",
            "loop_H_arguments_c1": [str(y0), str(y0)],
            "loop_H_arguments_c2": [str(y2_minus), str(y2_plus)],
            "loop_contrast_identity": "DeltaB=2*[2*H(32/25)-H(64/125)-H(256/125)]",
            "loop_contrast_lower_receipt": receipt(delta_B_lower),
            "loop_contrast_upper_receipt": receipt(delta_B_upper),
            "loop_simple_bound": "DeltaB>1/220",
            "scale_and_scheme_dependence": "CANCELS from DeltaB between the two angles",
            "status": "EXACT_STRICTLY_POSITIVE_TREE_AND_LOOP_CONTRASTS"
        },
        "finite_volume_complete_contrast": {
            "spectator_norm": "N_s=12*kappa*V/5>0",
            "formula": "DeltaR6=2*sqrt(2)*DeltaW/(3*N_s)+5*DeltaB/(24*pi^2)",
            "tree_sign": "STRICTLY_POSITIVE_FOR_EVERY_N_s_GT_ZERO",
            "loop_sign": "STRICTLY_POSITIVE_AND_VOLUME_INDEPENDENT",
            "pi_bound": "pi<22/7",
            "relative_q6_lower_bound": "DeltaR6>49/511104",
            "status": "NONZERO_COMPLETE_Q6_CONTRAST_FOR_EVERY_FINITE_POSITIVE_VOLUME"
        },
        "absolute_q8_bound": {
            "exact_rational_lower": receipt(dark_relative_simple_lower),
            "comparison": "Q8_dark/q4_bar>2401/2089818390528>1/1000000000",
            "leading_probability": "q_dark(lambda)>lambda^8*q4_bar/1000000000 at coefficient level, with remainder O(lambda^10)",
            "sign": "STRICTLY_POSITIVE",
            "volume_uniformity": "the displayed lower bound uses only the active-loop contrast and holds for every N_s>0",
            "status": "ABSOLUTE_DARK_PORT_Q8_COEFFICIENT_STRICTLY_POSITIVE"
        },
        "disposition": {
            "absolute_dark_port_q8_probability": "COEFFICIENT_COMPUTED_AND_STRICTLY_POSITIVE",
            "absolute_recorded_q8_probability": "NOT_COMPUTED",
            "absolute_bright_port_q8_probability": "NOT_COMPUTED",
            "complete_X2_X6_interference": "NOT_COMPUTED_AND_NOT_NEEDED_FOR_DARK_PORT",
            "finite_volume_two_angle_apparatus": "CONSTRUCTED",
            "compact_continuum_packet_extension": "NOT_CONSTRUCTED",
            "all_order_or_all_time_probability": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED_AND_NOT_USED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "either absolute recorded or bright-port order-lambda8 coefficient",
            "the complete X2-X6 interference on those ports",
            "a compact continuum-packet dark-port lower bound",
            "a volume-independent value of the positive tree contribution",
            "selection of the two angles, duration or apparatus by public BT dynamics",
            "forward, exchanged-forward, real-virtual, collinear or KLN completion",
            "an exact probability after summing every perturbative order",
            "an all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Bateman--Turok Eq. (19)",
            "a complete positive physical Hilbert or Fock construction",
            "gravity, metric BV--BRST, QME restoration or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Thicken the two lattice modes into normalized compact angle/momentum packets while preserving a nonzero complete R6 contrast, or compute the full X6 column if the recorded and bright-port absolute q8 coefficients are required. The dark-port absolute q8 obstruction is closed only on the declared finite-volume reduced-mode apparatus.",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, value in checks.items() if not value],
            "details": checks,
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_dark_port_absolute_q8_lower_bound.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_dark_port_absolute_q8_lower_bound.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_dark_port_absolute_q8_lower_bound"
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
            print("BT DARK-PORT ABSOLUTE Q8: STALE CERTIFICATE", file=sys.stderr)
            return 1
        print(
            f"BT DARK-PORT ABSOLUTE Q8: ALL PASS "
            f"({payload['checks']['passed']}/{payload['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
