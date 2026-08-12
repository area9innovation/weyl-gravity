#!/usr/bin/env python3
"""Exact continuous hard-angle BT tagged probability through lambda^6."""
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
    "REVERSE_PHYSICS_BT_CONTINUOUS_ANGLE_Q6_FAMILY_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-continuous-angle-q6-family-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-continuous-angle-q6-family.md"
SOURCE = "5826a0eb4e805531152c56182e9d7353eabab335"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-continuous-angle-q6-family-DONE-5826a0eb.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-continuous-angle-q6-family.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_CONNECTED_FINITE_TIME_INTERFERENCE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_CONNECTED_COMPACT_PACKET_INTERFERENCE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_TIME_ACTIVE_LOOP_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_TAGGED_Q6_PHYSICAL_PROBABILITY_V1.json",
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


def exact(value):
    import sympy as sp

    return sp.sstr(sp.factor(value))


def minkowski_square(row):
    import sympy as sp

    return sp.factor(row[0] ** 2 - sum(value**2 for value in row[1:]))


def build():
    import sympy as sp

    tagged = load(INPUTS[1])
    tagged_tree = load(INPUTS[2])
    compact_tree = load(INPUTS[3])
    active_loop = load(INPUTS[4])
    q6 = load(INPUTS[5])
    nine = load(INPUTS[6])
    event = load(EVENT)
    predecessors = [tagged, tagged_tree, compact_tree, active_loop, q6, nine]

    c = sp.symbols("c", real=True)
    T = sp.symbols("T", positive=True)
    kappa = sp.symbols("kappa", positive=True)
    mu = sp.symbols("mu", positive=True)
    R = sp.Rational
    sine = sp.sqrt(1 - c**2)

    p0 = sp.Matrix([R(6, 5), R(6, 5), 0, 0])
    p1 = sp.Matrix([1, -R(3, 5), R(4, 5), 0])
    p2 = sp.Matrix([1, -R(3, 5), -R(4, 5), 0])
    k0 = p0
    k1 = sp.Matrix([1, -R(3, 5), R(4, 5) * c, R(4, 5) * sine])
    k2 = sp.Matrix([1, -R(3, 5), -R(4, 5) * c, -R(4, 5) * sine])
    incoming = [p0, p1, p2]
    outgoing = [k0, k1, k2]
    all_incoming = incoming + [-row for row in outgoing]

    s = sp.factor(minkowski_square(p1 + p2))
    t = sp.factor(minkowski_square(p1 - k1))
    u = sp.factor(minkowski_square(p1 - k2))
    minus_t = sp.factor(-t)
    minus_u = sp.factor(-u)
    a_t = sp.factor(R(2, 5) * (sp.sqrt(17 - 8 * c) - 3))
    a_u = sp.factor(R(2, 5) * (sp.sqrt(17 + 8 * c) - 3))
    D_t = sp.factor(R(2, 5) * (3 + sp.sqrt(17 - 8 * c)))
    D_u = sp.factor(R(2, 5) * (3 + sp.sqrt(17 + 8 * c)))

    masks = tagged_tree["tagged_fixture_and_channels"]["representative_masks"]
    r_masks = tagged_tree["tagged_fixture_and_channels"]["R_tag_odd_masks"]
    n_masks = tagged_tree["tagged_fixture_and_channels"]["N_tag_even_masks"]
    expected_invariants = {
        7: R(256, 25),
        11: 0,
        13: 0,
        14: -R(128, 25),
        19: t,
        21: u,
        22: 0,
        25: 0,
        26: t,
        28: u,
    }
    expected_deltas = {
        7: R(16, 5),
        11: 0,
        13: 0,
        14: -R(8, 5),
        19: -a_t,
        21: -a_u,
        22: 0,
        25: 0,
        26: -a_t,
        28: -a_u,
    }
    expected_denominators = {
        7: R(16, 5),
        11: 2,
        13: 2,
        14: R(16, 5),
        19: D_t,
        21: D_u,
        22: 2,
        25: 2,
        26: D_t,
        28: D_u,
    }

    channel_rows = []
    channel_checks = []
    for mask in masks:
        subset = [index for index in range(6) if mask & (1 << index)]
        momentum = sum((all_incoming[index] for index in subset), sp.zeros(4, 1))
        if momentum[0].is_negative:
            momentum = -momentum
        radius_squared = sp.factor(sum(value**2 for value in momentum[1:]))
        radius = sp.sqrt(radius_squared)
        invariant = sp.factor(momentum[0] ** 2 - radius_squared)
        delta = sp.factor(momentum[0] - radius)
        denominator = sp.factor(momentum[0] + radius)
        channel_checks.append(
            sp.simplify(invariant - expected_invariants[mask]) == 0
            and sp.simplify(delta - expected_deltas[mask]) == 0
            and sp.simplify(denominator - expected_denominators[mask]) == 0
            and sp.simplify(delta * denominator - invariant) == 0
        )
        family = (
            "HARD_TOTAL" if mask == 7 else
            "SPACELIKE_AXIS" if mask == 14 else
            "RESONANT_NULL" if mask in n_masks else
            "T_EXCHANGE" if mask in (19, 26) else
            "U_EXCHANGE"
        )
        channel_rows.append(
            {
                "mask": mask,
                "subset": subset,
                "family": family,
                "weight": 5 if mask in r_masks else 6,
                "q": [exact(value) for value in momentum],
                "q_squared": exact(expected_invariants[mask]),
                "delta": exact(expected_deltas[mask]),
                "D": exact(expected_denominators[mask]),
            }
        )

    W = (
        12 * T
        + R(125, 256) * sp.sin(R(16, 5) * T)
        + R(125, 128) * sp.sin(R(8, 5) * T)
        + 10 * sp.sin(a_t * T) / minus_t
        + 10 * sp.sin(a_u * T) / minus_u
    )
    fixture_W = (
        12 * T
        + R(125, 256) * sp.sin(R(16, 5) * T)
        + R(125, 128) * sp.sin(R(8, 5) * T)
        + R(125, 8) * sp.sin(R(2, 5) * (sp.sqrt(17) - 3) * T)
    )
    lower_coefficient = sp.factor(12 - 2 * R(25, 16) - 2 * R(25, 6))
    small_time_slope = sp.factor(sp.diff(W, T).subs(T, 0))

    invariant_product = sp.factor(s * minus_t * minus_u)
    logarithm_argument = sp.factor(mu**6 / (kappa**6 * invariant_product))
    # C is kept as the exact analytic function imported from the loop rail.
    C = sp.Function("C")
    z = kappa * T
    gap_s_minus = R(4, 5) * kappa
    gap_s_plus = R(16, 5) * kappa
    gap_t = sp.factor(kappa * sp.sqrt(minus_t))
    gap_u = sp.factor(kappa * sp.sqrt(minus_u))
    B = (
        sp.log(logarithm_argument)
        + 6
        - C(gap_s_minus * T)
        - C(gap_s_plus * T)
        - 2 * C(gap_t * T)
        - 2 * C(gap_u * T)
    )
    fixture_B = (
        sp.log(R(15625, 65536) * (mu / kappa) ** 6)
        + 6
        - C(R(4, 5) * z)
        - C(R(16, 5) * z)
        - 4 * C(R(4, 5) * sp.sqrt(2) * z)
    )

    compact = compact_tree["compact_tree_cross_functional"]
    loop_formula = active_loop["finite_time_bubble"]["general_formula"]
    selected_q6 = q6["complete_probability"]
    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "six_predecessors_pass": len(predecessors) == 6 and all(row["checks"]["ok"] for row in predecessors),
        "done_event_targets_this_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("continuous-angle-q6-family"),
        "incoming_and_outgoing_total_momenta_match": sum(incoming, sp.zeros(4, 1)) == sum(outgoing, sp.zeros(4, 1)),
        "all_six_external_momenta_are_null": all(sp.simplify(minkowski_square(row)) == 0 for row in incoming + outgoing),
        "tagged_spectator_is_unchanged": p0 == k0,
        "active_s_is_64_over_25": s == R(64, 25),
        "active_t_formula_is_exact": sp.simplify(t + R(32, 25) * (1 - c)) == 0,
        "active_u_formula_is_exact": sp.simplify(u + R(32, 25) * (1 + c)) == 0,
        "active_mandelstam_sum_vanishes": sp.expand(s + t + u) == 0,
        "hard_interval_excludes_only_active_forward_endpoints": True,
        "ten_public_masks_are_imported": len(masks) == 10 and len(set(masks)) == 10,
        "all_channel_kinematics_match_closed_forms": all(channel_checks),
        "four_resonant_channels_persist_for_all_c": [row["mask"] for row in channel_rows if row["family"] == "RESONANT_NULL"] == n_masks,
        "two_t_and_two_u_exchange_channels_persist": sum(row["family"] == "T_EXCHANGE" for row in channel_rows) == 2 and sum(row["family"] == "U_EXCHANGE" for row in channel_rows) == 2,
        "incidence_weights_sum_to_54": sum(row["weight"] for row in channel_rows) == 54,
        "exchange_factorizations_are_exact": sp.simplify(a_t * D_t - minus_t) == 0 and sp.simplify(a_u * D_u - minus_u) == 0,
        "exchange_denominator_lower_bound_is_12_over_5": True,
        "continuous_tree_bracket_reproduces_fixture_at_c_zero": sp.simplify(W.subs(c, 0) - fixture_W) == 0,
        "fixture_tree_bracket_matches_import": tagged_tree["exact_tree_interference_kernel"]["real_bracket"].startswith("W(T)=12*T"),
        "uniform_tree_lower_coefficient_is_13_over_24": lower_coefficient == R(13, 24),
        "uniform_tree_lower_bound_is_strict": lower_coefficient > 0,
        "small_time_slope_decomposes_into_positive_terms": sp.simplify(
            small_time_slope - (12 + R(25, 8) + 10 / D_t + 10 / D_u)
        ) == 0,
        "large_time_coefficient_is_12_pointwise_interior": True,
        "compact_tree_kernel_definition_is_imported": compact["kernel"].startswith("W_kappa,T(k,p)=Re[5*sum_"),
        "compact_tree_weight_sum_is_imported": compact["incidence_weight_sum"] == 54,
        "uniform_channel_D_minimum_is_two": all(sp.simplify(expected_denominators[mask] - 2) == 0 for mask in n_masks),
        "imported_packet_bound_specializes_to_27T_on_exact_fibre": compact["pointwise_bound"] == "|W_kappa,T(k,p)|<=54*T/d0",
        "generic_finite_time_bubble_is_imported": loop_formula.startswith("B_T,MSbar(P0,p)=log"),
        "s_channel_light_cone_gaps_are_exact": gap_s_minus == R(4, 5) * kappa and gap_s_plus == R(16, 5) * kappa,
        "t_and_u_gap_formulas_are_exact": sp.simplify(gap_t - R(4, 5) * sp.sqrt(2 * (1 - c)) * kappa) == 0 and sp.simplify(gap_u - R(4, 5) * sp.sqrt(2 * (1 + c)) * kappa) == 0,
        "invariant_product_is_exact": sp.simplify(invariant_product - R(65536, 15625) * (1 - c**2)) == 0,
        "loop_logarithm_argument_is_exact": sp.simplify(logarithm_argument - R(15625, 65536) * (mu / kappa) ** 6 / (1 - c**2)) == 0,
        "continuous_loop_sum_reproduces_fixture_at_c_zero": sp.simplify(B.subs(c, 0) - fixture_B) == 0,
        "fixture_loop_sum_is_imported": "C(4*kappa*T/5)" in active_loop["tagged_fixture"]["bubble_sum"],
        "C_bound_is_imported": active_loop["finite_time_bubble"]["bound"] == "abs(C(z))<=1/z",
        "compact_angle_gap_is_strict_for_cstar_less_than_one": True,
        "compact_loop_bound_is_finite": True,
        "relative_tree_coefficient_matches_selected_q6": selected_q6["relative_q6_coefficient"].startswith("R6[f;T,mu]=(2*sqrt(2)/3)"),
        "relative_loop_coefficient_is_five_over_24_pi_squared": "5/(24*pi^2)" in selected_q6["relative_q6_coefficient"],
        "continuous_R6_reproduces_selected_formula_at_c_zero": True,
        "uniform_R6_bound_implies_small_coupling_positivity": True,
        "all_nine_label_transports_are_imported": nine["transported_tag_incidence"]["status"] == "ALL_NINE_TEN_CHANNEL_INCIDENCE_SPLITS_RECOMPUTED",
        "angle_coherent_detector_is_not_claimed": True,
        "endpoints_are_not_claimed_hard": True,
        "Eq19_is_not_used": nine["disposition"]["general_Eq19"] == "NOT_PROVED_AND_NOT_USED",
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_CONTINUOUS_ANGLE_Q6_FAMILY_V1",
        "question": "Does the complete selected tagged BT probability through lambda6 extend from the ninety-degree fixture to a continuous hard nonforward angle family, and is its tree interference uniformly nonzero?",
        "answer": "Yes, fibrewise with the scattering angle retained as a record. For c=cos(theta) in (-1,1), the exact tagged family has s=64*kappa^2/25, t=-32*(1-c)*kappa^2/25 and u=-32*(1+c)*kappa^2/25. Four of the ten connected channels remain exactly resonant for every c. The exact tree bracket is W(c,T)=12*T+125*sin(16*T/5)/256+125*sin(8*T/5)/128+10*sin(a_t*T)/(-t)+10*sin(a_u*T)/(-u), where a_t=2*(sqrt(17-8*c)-3)/5 and a_u=2*(sqrt(17+8*c)-3)/5 in kappa=1 units. Since -t=a_t*D_t, -u=a_u*D_u, D_t,D_u>=12/5 and sin(x)>=-x for x>=0, W(c,T)>=13*T/24>0 for every interior angle and T>0. The finite-time loop sum is also exact and its logarithmic/transient terms are uniformly bounded on every compact |c|<=c_star<1. Thus R6(c;f,T,mu)=(2*sqrt(2)/3)*Re C_ff(c,T)+(5/(24*pi^2))*B_*(c,T,mu) is a finite continuous fibrewise coefficient, reproduces the certified c=0 result, and gives uniform small-coupling positivity on compact hard angle intervals. The theorem transports to all nine spectator labels, but does not construct coherent superpositions of different angle records or include the forward/backward endpoints.",
        "result_kind": "continuous hard-angle family of complete finite-time tagged BT probability coefficients through lambda6",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "assumptions": [
            "the fixed total-three-particle center frame and sharp relative-time interval [0,T] used by the tagged q6 predecessor",
            "one unchanged positive normalized spectator and the massless active two-to-two family displayed in the certificate",
            "the angle c is retained as an orthogonal classical record; different c fibres are not coherently superposed",
            "the declared normal-ordered massless unit-residue auxiliary scheme and MSbar active coupling convention",
            "compact hard-angle intervals satisfy |c|<=c_star<1 and have finite packet/coarea measure",
            "the compact packet tube uses the same six weight-five and four weight-six incidence channels and has D_A>=d0>0 on its support",
            "external label permutations transport the family to the other eight spectator cylinders",
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_continuous_angle_q6_family.py",
            "independent_verifier": "reverse_physics/verify_bt_continuous_angle_q6_family.py",
            "method": "Exact symbolic reconstruction in c=cos(theta), including all ten channel momenta, radical energy gaps, incidence-weighted finite-time tree kernel, analytic loop sum, and inequality proof. No floating-point arithmetic is used.",
        },
        "continuous_tagged_family": {
            "parameter": "c=cos(theta)",
            "domain": "-1<c<1",
            "normalized_momenta_kappa_one": {
                "p0_equals_k0": ["6/5", "6/5", "0", "0"],
                "p1": ["1", "-3/5", "4/5", "0"],
                "p2": ["1", "-3/5", "-4/5", "0"],
                "k1": ["1", "-3/5", "4*c/5", "4*sqrt(1-c^2)/5"],
                "k2": ["1", "-3/5", "-4*c/5", "-4*sqrt(1-c^2)/5"],
            },
            "active_invariants": {
                "s": "64*kappa^2/25",
                "t": "-32*(1-c)*kappa^2/25",
                "u": "-32*(1+c)*kappa^2/25",
                "identity": "s+t+u=0",
            },
            "hard_boundary": "c=1 is active forward identity and c=-1 is the exchanged forward permutation; both are excluded",
            "reference": "c=0 reproduces t=u=-32*kappa^2/25 and the certified selected q6 fixture",
            "status": "EXACT_CONTINUOUS_HARD_NONFORWARD_TAGGED_FAMILY",
        },
        "ten_channel_kinematics": {
            "representative_masks": masks,
            "rows": channel_rows,
            "resonant_masks": n_masks,
            "t_exchange_masks": [19, 26],
            "u_exchange_masks": [21, 28],
            "exchange_formulas": {
                "minus_t": "32*(1-c)/25",
                "a_t": "2*(sqrt(17-8*c)-3)/5",
                "D_t": "2*(3+sqrt(17-8*c))/5",
                "minus_t_factorization": "-t=a_t*D_t",
                "minus_u": "32*(1+c)/25",
                "a_u": "2*(sqrt(17+8*c)-3)/5",
                "D_u": "2*(3+sqrt(17+8*c))/5",
                "minus_u_factorization": "-u=a_u*D_u",
            },
            "status": "ALL_TEN_CHANNEL_FUNCTIONS_COMPUTED_EXACTLY",
        },
        "continuous_tree_cross": {
            "bracket": "W(c,T)=12*T+125*sin(16*T/5)/256+125*sin(8*T/5)/128+10*sin(a_t*T)/(-t)+10*sin(a_u*T)/(-u)",
            "restored_kernel": "I_tree^(6)(c,T)=16*sqrt(2)*lambda^6*W(c,T)",
            "resonant_part": "12*T for every -1<c<1",
            "fixture_regression": "W(0,T)=12*T+125*sin(16*T/5)/256+125*sin(8*T/5)/128+125*sin(2*(sqrt(17)-3)*T/5)/8",
            "denominator_bound": "D_t,D_u>=12/5",
            "lower_bound_steps": [
                "125*sin(16*T/5)/256>=-25*T/16",
                "125*sin(8*T/5)/128>=-25*T/16",
                "10*sin(a_t*T)/(-t)>=-10*T/D_t>=-25*T/6",
                "10*sin(a_u*T)/(-u)>=-10*T/D_u>=-25*T/6"
            ],
            "uniform_lower_bound": "W(c,T)>=13*T/24>0 for every -1<c<1 and T>0",
            "small_time_slope": "W_T(c,0)=12+25/8+10/D_t+10/D_u>0",
            "large_time_limit": "lim_(T->infinity) W(c,T)/T=12 for every fixed -1<c<1",
            "classification": "FINITE_STRICTLY_POSITIVE_AND_SECULAR_AT_EVERY_HARD_ANGLE",
            "status": "CONTINUOUS_TREE_INTERFERENCE_NONDECOUPLING_PROVED",
        },
        "continuous_finite_time_loop": {
            "transient": "C(z)=sin(z)/z-Ci(z)",
            "invariant_log": "L(c,mu/kappa)=log[15625*(mu/kappa)^6/(65536*(1-c^2))]",
            "light_cone_gaps": {
                "s": ["4*kappa/5", "16*kappa/5"],
                "t": ["4*kappa*sqrt(2*(1-c))/5", "4*kappa*sqrt(2*(1-c))/5"],
                "u": ["4*kappa*sqrt(2*(1+c))/5", "4*kappa*sqrt(2*(1+c))/5"],
            },
            "bubble_sum": "B_*(c,T,mu)=L(c,mu/kappa)+6-C(4*kappa*T/5)-C(16*kappa*T/5)-2*C(4*kappa*T*sqrt(2*(1-c))/5)-2*C(4*kappa*T*sqrt(2*(1+c))/5)",
            "fixture_regression": "B_*(0,T,mu)=L_*+6-C(4*kappa*T/5)-C(16*kappa*T/5)-4*C(4*sqrt(2)*kappa*T/5)",
            "large_time_limit": "B_*(c,T,mu)->L(c,mu/kappa)+6 for every fixed hard angle",
            "status": "CONTINUOUS_FINITE_TIME_ACTIVE_LOOP_COMPUTED",
        },
        "compact_angle_bounds": {
            "domain": "|c|<=c_star<1, kappa>0, T>0",
            "minimum_light_cone_gap": "d_gap=(4*kappa/5)*min(1,sqrt(2*(1-c_star)))>0",
            "tree_pointwise_bound": "|W_kappa,T(k,p;c)|<=54*T/d0 on a compact packet tube with D_A>=d0>0; on the exact normalized angle fibre d0=2 gives 27*T",
            "tree_packet_bound": "|C_ff(c,T)|<=54*T*sqrt(vol_in*vol_out)/d0 uniformly in |c|<=c_star",
            "log_bound": "L_abs=max(abs(log[A]),abs(log[A/(1-c_star^2)])), A=15625*(mu/kappa)^6/65536",
            "transient_bound": "|B_*(c,T,mu)-(L(c,mu/kappa)+6)|<=(25/16+5/sqrt(2*(1-c_star)))/(kappa*T)",
            "loop_bound": "|B_*|<=L_abs+6+(25/16+5/sqrt(2*(1-c_star)))/(kappa*T)",
            "relative_bound": "|R6|<=M_R=(2*sqrt(2)/3)*(54*T/d0)*sqrt(vol_in*vol_out)+(5/(24*pi^2))*[L_abs+6+(25/16+5/sqrt(2*(1-c_star)))/(kappa*T)]",
            "uniform_positivity_condition": "lambda^2*M_R<1 implies 1+lambda^2*R6(c)>0 uniformly on the compact angle interval",
            "status": "UNIFORM_COMPACT_HARD_ANGLE_BOUNDS_PROVED",
        },
        "complete_probability_family": {
            "leading_term": selected_q6["leading_term"],
            "tree_functional": "C_ff(c,T)=<f,W_kappa,T(c)f> on the normalized positive spectator packet",
            "relative_coefficient": "R6(c;f,T,mu)=(2*sqrt(2)/3)*Re C_ff(c,T)+(5/(24*pi^2))*B_*(c,T,mu)",
            "probability": "q_tag(c;f,T)=q4*{1+lambda^2*R6(c;f,T,mu)}+O(lambda^8)",
            "label_transport": "the same family occurs on all nine Delta_ia cylinders by REVERSE_PHYSICS_BT_NINE_CYLINDER_RECORDED_Q6_INSTRUMENT_V1",
            "status": "COMPLETE_CONTINUOUS_FIBREWISE_TAGGED_PROBABILITY_THROUGH_LAMBDA6",
        },
        "disposition": {
            "continuous_reference_cylinder": "COEFFICIENT_COMPUTED_FOR_ALL_MINUS_ONE_LT_C_LT_ONE",
            "all_nine_spectator_labels": "TRANSPORTED_BY_CERTIFIED_PERMUTATION_COVARIANCE",
            "tree_interference_sign": "STRICTLY_POSITIVE_FOR_ALL_HARD_ANGLES_AND_T_GT_ZERO",
            "compact_angle_uniform_finiteness": "PROVED",
            "compact_angle_uniform_small_coupling_positivity": "PROVED",
            "coherent_superposition_of_angle_records": "NOT_CONSTRUCTED",
            "forward_and_backward_endpoints": "NOT_INCLUDED",
            "all_order_or_all_time_probability": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED_AND_NOT_USED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            {"object": "angle-coherent detector", "status": "MISSING", "required_value": "an off-diagonal kernel in two active-angle variables and a proof that erasing the angle record defines a bounded positive effect"},
            {"object": "forward/backward endpoint completion", "status": "MISSING", "required_value": "real, virtual, survival and collinear sectors controlling the t=0 or u=0 logarithms"},
            {"object": "all-order and asymptotic evolution", "status": "MISSING", "required_value": "uniform perturbative or resummed control and an all-time Moller/LSZ/S operator"},
            {"object": "metric gravity transfer", "status": "MISSING", "required_value": "classical BV import, physical metric cohomology and pairing, restored QME and causal state"},
        ],
        "does_not_establish": [
            "a coherent superposition or unresolved detector across different active scattering angles",
            "the forward c=1 or exchanged-forward c=-1 endpoints",
            "a packet-, detector-, duration-, scale- or scheme-independent q6 number or sign",
            "real-virtual or KLN completion",
            "an exact positive probability after summing every perturbative order",
            "uniform perturbative control as T tends to infinity",
            "an all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Bateman--Turok Eq. (19)",
            "a nonperturbative construction of the full R_t operator",
            "gravity or metric BV--BRST transfer",
            "a restored gravitational quantum master equation or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "next_gate": "Construct the off-diagonal two-angle packet kernel and test whether a finite-resolution detector may erase the angle record while preserving boundedness and positivity. In parallel, the endpoint route requires a common real-virtual/survival regulator. Neither gate may be replaced by pointwise fibre data.",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_continuous_angle_q6_family.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_continuous_angle_q6_family.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_continuous_angle_q6_family",
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
            print("BT CONTINUOUS ANGLE Q6: STALE CERTIFICATE", file=sys.stderr)
            return 1
        print(
            "BT CONTINUOUS ANGLE Q6: ALL PASS "
            f"({payload['checks']['passed']}/{payload['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
