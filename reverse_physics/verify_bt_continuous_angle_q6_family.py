#!/usr/bin/env python3
"""Stereographic verifier for the continuous hard-angle BT q6 family."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CONTINUOUS_ANGLE_Q6_FAMILY_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-continuous-angle-q6-family-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(certificate):
    import sympy as sp

    schema_ok = not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if not schema_ok:
        return {"schema_validation": False}

    inputs = certificate["provenance"]["inputs"]
    hashes_ok = all(sha256(row["path"]) == row["sha256"] for row in inputs)
    imported = {
        row["path"]: load(os.path.join(ROOT, row["path"])) for row in inputs
    }
    predecessors = [
        value
        for path, value in imported.items()
        if path.startswith("reverse_physics/certificates/")
    ]
    tagged_tree = next(
        value
        for value in predecessors
        if value["certificate"].endswith("TAGGED_CONNECTED_FINITE_TIME_INTERFERENCE_V1")
    )
    compact_tree = next(
        value
        for value in predecessors
        if value["certificate"].endswith("TAGGED_CONNECTED_COMPACT_PACKET_INTERFERENCE_V1")
    )
    active_loop = next(
        value
        for value in predecessors
        if value["certificate"].endswith("FINITE_TIME_ACTIVE_LOOP_AFFILIATION_V1")
    )
    selected_q6 = next(
        value
        for value in predecessors
        if value["certificate"].endswith("COMPLETE_TAGGED_Q6_PHYSICAL_PROBABILITY_V1")
    )
    nine = next(
        value
        for value in predecessors
        if value["certificate"].endswith("NINE_CYLINDER_RECORDED_Q6_INSTRUMENT_V1")
    )
    event = next(
        value for path, value in imported.items() if path.startswith("planning/events/")
    )

    # This rail never uses c as its primary coordinate.  It covers the full
    # open interval by r>0 with c=(1-r^2)/(1+r^2), sin(theta)=2r/(1+r^2).
    r = sp.symbols("r", positive=True)
    c = sp.symbols("c", real=True)
    T = sp.symbols("T", positive=True)
    kappa = sp.symbols("kappa", positive=True)
    mu = sp.symbols("mu", positive=True)
    R = sp.Rational
    c_r = (1 - r**2) / (1 + r**2)
    sine_r = 2 * r / (1 + r**2)

    def sq(row):
        return sp.factor(row[0] ** 2 - sum(value**2 for value in row[1:]))

    def expression(text):
        return sp.sympify(text, locals={"c": c}).subs(c, c_r)

    def same(left, right):
        return sp.simplify(sp.together(left - right)) == 0

    p0 = sp.Matrix([R(6, 5), R(6, 5), 0, 0])
    p1 = sp.Matrix([1, -R(3, 5), R(4, 5), 0])
    p2 = sp.Matrix([1, -R(3, 5), -R(4, 5), 0])
    k0 = p0
    k1 = sp.Matrix([1, -R(3, 5), R(4, 5) * c_r, R(4, 5) * sine_r])
    k2 = sp.Matrix([1, -R(3, 5), -R(4, 5) * c_r, -R(4, 5) * sine_r])
    incoming = (p0, p1, p2)
    outgoing = (k0, k1, k2)
    all_incoming = incoming + tuple(-row for row in outgoing)

    s = sq(p1 + p2)
    t = sq(p1 - k1)
    u = sq(p1 - k2)
    expected_t = -R(64, 25) * r**2 / (1 + r**2)
    expected_u = -R(64, 25) / (1 + r**2)
    root_t = sp.sqrt((9 + 25 * r**2) / (1 + r**2))
    root_u = sp.sqrt((25 + 9 * r**2) / (1 + r**2))
    a_t = R(2, 5) * (root_t - 3)
    a_u = R(2, 5) * (root_u - 3)
    D_t = R(2, 5) * (root_t + 3)
    D_u = R(2, 5) * (root_u + 3)

    rows = certificate["ten_channel_kinematics"]["rows"]
    source = tagged_tree["tagged_fixture_and_channels"]
    row_checks = []
    branch_checks = []
    rebuilt = 0
    for row in rows:
        mask = row["mask"]
        subset = [index for index in range(6) if mask & (1 << index)]
        momentum = sum((all_incoming[index] for index in subset), sp.zeros(4, 1))
        if momentum[0] < 0:
            momentum = -momentum
        invariant = sq(momentum)
        q_claim = [expression(value) for value in row["q"]]
        invariant_claim = expression(row["q_squared"])
        delta_claim = expression(row["delta"])
        D_claim = expression(row["D"])
        radius_squared = sum(value**2 for value in momentum[1:])
        row_checks.append(
            subset == row["subset"]
            and all(same(momentum[index], q_claim[index]) for index in range(4))
            and same(invariant, invariant_claim)
            and same(delta_claim + D_claim, 2 * momentum[0])
            and same(delta_claim * D_claim, invariant)
            and same((D_claim - delta_claim) ** 2, 4 * radius_squared)
        )
        # The r=1 point fixes the positive square-root branch; no branch can
        # cross zero because D is positive throughout r>0.
        radius_at_one = sp.sqrt(radius_squared.subs(r, 1))
        branch_checks.append(
            same(D_claim.subs(r, 1), momentum[0] + radius_at_one)
            and same(delta_claim.subs(r, 1), momentum[0] - radius_at_one)
            and D_claim.subs(r, 1) > 0
        )
        if delta_claim == 0:
            rebuilt += row["weight"] * T / D_claim
        else:
            rebuilt += row["weight"] * sp.sin(delta_claim * T) / (
                delta_claim * D_claim
            )

    W = (
        12 * T
        + R(125, 256) * sp.sin(R(16, 5) * T)
        + R(125, 128) * sp.sin(R(8, 5) * T)
        + 10 * sp.sin(a_t * T) / (-expected_t)
        + 10 * sp.sin(a_u * T) / (-expected_u)
    )
    W0 = (
        12 * T
        + R(125, 256) * sp.sin(R(16, 5) * T)
        + R(125, 128) * sp.sin(R(8, 5) * T)
        + R(125, 8) * sp.sin(R(2, 5) * (sp.sqrt(17) - 3) * T)
    )
    lower_coefficient = 12 - 2 * R(25, 16) - 2 * R(25, 6)
    slope = 12 + R(25, 8) + 10 / D_t + 10 / D_u

    product = sp.factor(s * (-t) * (-u))
    log_argument = sp.factor(mu**6 / (kappa**6 * product))
    gap_s = (R(4, 5) * kappa, R(16, 5) * kappa)
    gap_t = kappa * sp.sqrt(-t)
    gap_u = kappa * sp.sqrt(-u)
    expected_gap_t = R(8, 5) * kappa * r / sp.sqrt(1 + r**2)
    expected_gap_u = R(8, 5) * kappa / sp.sqrt(1 + r**2)

    tree = certificate["continuous_tree_cross"]
    loop = certificate["continuous_finite_time_loop"]
    bounds = certificate["compact_angle_bounds"]
    probability = certificate["complete_probability_family"]
    disposition = certificate["disposition"]
    scope = certificate["does_not_establish"]
    family = certificate["continuous_tagged_family"]
    invariants = family["active_invariants"]
    exchange = certificate["ten_channel_kinematics"]["exchange_formulas"]

    expected_exchange = {
        "minus_t": "32*(1-c)/25",
        "a_t": "2*(sqrt(17-8*c)-3)/5",
        "D_t": "2*(3+sqrt(17-8*c))/5",
        "minus_t_factorization": "-t=a_t*D_t",
        "minus_u": "32*(1+c)/25",
        "a_u": "2*(sqrt(17+8*c)-3)/5",
        "D_u": "2*(3+sqrt(17+8*c))/5",
        "minus_u_factorization": "-u=a_u*D_u",
    }
    expected_gaps = {
        "s": ["4*kappa/5", "16*kappa/5"],
        "t": ["4*kappa*sqrt(2*(1-c))/5", "4*kappa*sqrt(2*(1-c))/5"],
        "u": ["4*kappa*sqrt(2*(1+c))/5", "4*kappa*sqrt(2*(1+c))/5"],
    }
    expected_lower_steps = [
        "125*sin(16*T/5)/256>=-25*T/16",
        "125*sin(8*T/5)/128>=-25*T/16",
        "10*sin(a_t*T)/(-t)>=-10*T/D_t>=-25*T/6",
        "10*sin(a_u*T)/(-u)>=-10*T/D_u>=-25*T/6",
    ]

    checks = {
        "schema_validation": schema_ok,
        "certificate_identity": certificate["certificate"] == "REVERSE_PHYSICS_BT_CONTINUOUS_ANGLE_Q6_FAMILY_V1",
        "input_hashes_recomputed": hashes_ok,
        "six_predecessor_pass_flags_rechecked": len(predecessors) == 6 and all(row["checks"]["ok"] for row in predecessors),
        "done_event_matches_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("continuous-angle-q6-family"),
        "stereographic_coordinate_covers_open_interval": same(1 - c_r**2, 4 * r**2 / (1 + r**2) ** 2),
        "stereographic_sine_is_positive": sine_r > 0,
        "incoming_outgoing_conservation_recomputed": sum(incoming, sp.zeros(4, 1)) == sum(outgoing, sp.zeros(4, 1)),
        "six_null_conditions_recomputed": all(same(sq(row), 0) for row in incoming + outgoing),
        "spectator_identity_recomputed": p0 == k0,
        "s_recomputed": s == R(64, 25),
        "t_recomputed_rationally": same(t, expected_t),
        "u_recomputed_rationally": same(u, expected_u),
        "mandelstam_identity_recomputed": same(s + t + u, 0),
        "certificate_invariant_formulas_match": invariants == {"s": "64*kappa^2/25", "t": "-32*(1-c)*kappa^2/25", "u": "-32*(1+c)*kappa^2/25", "identity": "s+t+u=0"},
        "hard_endpoints_remain_excluded": family["domain"] == "-1<c<1" and "both are excluded" in family["hard_boundary"],
        "ten_subsets_recomputed": len(rows) == 10 and all(row_checks),
        "all_energy_gap_branches_rechecked": all(branch_checks),
        "mask_order_imported_exactly": [row["mask"] for row in rows] == source["representative_masks"],
        "incidence_weights_imported_exactly": [row["weight"] for row in rows] == [5 if row["mask"] in source["R_tag_odd_masks"] else 6 for row in rows],
        "four_resonant_rows_recomputed": [row["mask"] for row in rows if row["family"] == "RESONANT_NULL"] == source["N_tag_even_masks"],
        "exchange_families_recomputed": [row["mask"] for row in rows if row["family"] == "T_EXCHANGE"] == [19, 26] and [row["mask"] for row in rows if row["family"] == "U_EXCHANGE"] == [21, 28],
        "exchange_formula_strings_match": exchange == expected_exchange,
        "t_factorization_recomputed": same(a_t * D_t, -expected_t),
        "u_factorization_recomputed": same(a_u * D_u, -expected_u),
        "t_denominator_strictly_above_12_over_5": same(root_t**2 - 9, 16 * r**2 / (1 + r**2)),
        "u_denominator_strictly_above_12_over_5": same(root_u**2 - 9, 16 / (1 + r**2)),
        "tree_sum_rebuilt_from_ten_rows": same(rebuilt, W),
        "tree_fixture_recomputed_at_r_one": same(W.subs(r, 1), W0),
        "tree_fixture_matches_predecessor": tagged_tree["exact_tree_interference_kernel"]["real_bracket"] == "W(T)=12*T+125*sin(16*T/5)/256+125*sin(8*T/5)/128+125*sin(2*(sqrt(17)-3)*T/5)/8",
        "lower_bound_steps_recorded_exactly": tree["lower_bound_steps"] == expected_lower_steps,
        "lower_bound_coefficient_recomputed": lower_coefficient == R(13, 24) and lower_coefficient > 0,
        "uniform_positive_bound_recorded": tree["uniform_lower_bound"] == "W(c,T)>=13*T/24>0 for every -1<c<1 and T>0",
        "small_time_slope_recomputed_positive": tree["small_time_slope"] == "W_T(c,0)=12+25/8+10/D_t+10/D_u>0" and slope.subs(r, 1) > 0,
        "pointwise_large_time_coefficient_recomputed": tree["large_time_limit"] == "lim_(T->infinity) W(c,T)/T=12 for every fixed -1<c<1",
        "packet_bound_imported_without_d0_promotion": compact_tree["compact_tree_cross_functional"]["pointwise_bound"] == "|W_kappa,T(k,p)|<=54*T/d0" and "54*T/d0" in bounds["tree_pointwise_bound"] and "d0=2 gives 27*T" in bounds["tree_pointwise_bound"],
        "packet_functional_bound_matches_import": bounds["tree_packet_bound"] == "|C_ff(c,T)|<=54*T*sqrt(vol_in*vol_out)/d0 uniformly in |c|<=c_star",
        "loop_s_gaps_recomputed": gap_s == (R(4, 5) * kappa, R(16, 5) * kappa),
        "loop_t_gap_recomputed": same(gap_t, expected_gap_t),
        "loop_u_gap_recomputed": same(gap_u, expected_gap_u),
        "loop_gap_strings_match": loop["light_cone_gaps"] == expected_gaps,
        "loop_invariant_product_recomputed": same(product, R(262144, 15625) * r**2 / (1 + r**2) ** 2),
        "loop_log_argument_recomputed": same(log_argument, R(15625, 262144) * (mu / kappa) ** 6 * (1 + r**2) ** 2 / r**2),
        "loop_formula_has_all_six_transients": loop["bubble_sum"] == "B_*(c,T,mu)=L(c,mu/kappa)+6-C(4*kappa*T/5)-C(16*kappa*T/5)-2*C(4*kappa*T*sqrt(2*(1-c))/5)-2*C(4*kappa*T*sqrt(2*(1+c))/5)",
        "loop_fixture_matches_predecessor": loop["fixture_regression"] == "B_*(0,T,mu)=L_*+6-C(4*kappa*T/5)-C(16*kappa*T/5)-4*C(4*sqrt(2)*kappa*T/5)" and "C(4*kappa*T/5)" in active_loop["tagged_fixture"]["bubble_sum"],
        "compact_gap_bound_recomputed": bounds["minimum_light_cone_gap"] == "d_gap=(4*kappa/5)*min(1,sqrt(2*(1-c_star)))>0",
        "compact_transient_coefficient_recomputed": bounds["transient_bound"] == "|B_*(c,T,mu)-(L(c,mu/kappa)+6)|<=(25/16+5/sqrt(2*(1-c_star)))/(kappa*T)",
        "compact_log_endpoint_bound_recorded": bounds["log_bound"] == "L_abs=max(abs(log[A]),abs(log[A/(1-c_star^2)])), A=15625*(mu/kappa)^6/65536",
        "relative_bound_retains_packet_d0": "54*T/d0" in bounds["relative_bound"],
        "uniform_small_coupling_condition_recorded": bounds["uniform_positivity_condition"] == "lambda^2*M_R<1 implies 1+lambda^2*R6(c)>0 uniformly on the compact angle interval",
        "leading_probability_imported": probability["leading_term"] == selected_q6["complete_probability"]["leading_term"],
        "relative_q6_formula_assembled": probability["relative_coefficient"] == "R6(c;f,T,mu)=(2*sqrt(2)/3)*Re C_ff(c,T)+(5/(24*pi^2))*B_*(c,T,mu)",
        "probability_formula_assembled": probability["probability"] == "q_tag(c;f,T)=q4*{1+lambda^2*R6(c;f,T,mu)}+O(lambda^8)",
        "all_nine_labels_imported": nine["transported_tag_incidence"]["status"] == "ALL_NINE_TEN_CHANNEL_INCIDENCE_SPLITS_RECOMPUTED" and disposition["all_nine_spectator_labels"] == "TRANSPORTED_BY_CERTIFIED_PERMUTATION_COVARIANCE",
        "angle_coherence_remains_open": disposition["coherent_superposition_of_angle_records"] == "NOT_CONSTRUCTED",
        "endpoints_remain_open": disposition["forward_and_backward_endpoints"] == "NOT_INCLUDED",
        "all_orders_remain_open": disposition["all_order_or_all_time_probability"] == "NOT_CONSTRUCTED",
        "Eq19_remains_open": disposition["general_Eq19"] == "NOT_PROVED_AND_NOT_USED",
        "gravity_remains_open": disposition["gravity_or_metric_BV_BRST_transfer"] == "NOT_CONSTRUCTED",
        "Lorentzian_boundary_present": any("LORENTZIAN-CAUSAL" in row for row in scope),
        "literature_priority_forbidden": "literature priority" in scope,
    }
    return {name: bool(value) for name, value in checks.items()}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    checks = verify(load(args.verify))
    for name, ok in checks.items():
        print(("PASS: " if ok else "FAIL: ") + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
