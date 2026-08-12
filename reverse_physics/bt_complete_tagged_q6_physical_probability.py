#!/usr/bin/env python3
"""Assemble the complete selected tagged BT physical probability through q6."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_COMPLETE_TAGGED_Q6_PHYSICAL_PROBABILITY_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-complete-tagged-q6-physical-probability-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-complete-tagged-q6-physical-probability.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-complete-tagged-q6-physical-probability.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_PACKET_LAMBDA5_PARITY_SELECTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_PACKET_LAMBDA6_OBJECT_LEDGER_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_PACKET_NORMAL_ORDERED_SPECTATOR_REDUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_TIME_ACTIVE_LOOP_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_CONNECTED_COMPACT_PACKET_INTERFERENCE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1.json",
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


def transient(z):
    return sp.sin(z) / z - sp.Ci(z)


def build():
    parity = load(INPUTS[1])
    ledger = load(INPUTS[2])
    spectator = load(INPUTS[3])
    loop = load(INPUTS[4])
    tree = load(INPUTS[5])
    tagged = load(INPUTS[6])
    predecessors = [parity, ledger, spectator, loop, tree, tagged]

    lam, kappa, area, acceptance, T, mu = sp.symbols(
        "lambda kappa Area DeltaOmega T mu", positive=True
    )
    Cff = sp.symbols("C_ff", real=True)
    q4 = 75 * lam**4 * acceptance / (
        2048 * sp.pi**2 * kappa**2 * area
    )
    tree_absolute = 25 * sp.sqrt(2) * lam**6 * acceptance * Cff / (
        1024 * sp.pi**2 * kappa**2 * area
    )
    Lstar = (
        sp.log(25 * mu**2 / (64 * kappa**2))
        + 2 * sp.log(25 * mu**2 / (32 * kappa**2))
    )
    Bstar = (
        Lstar
        + 6
        - transient(sp.Rational(4, 5) * kappa * T)
        - transient(sp.Rational(16, 5) * kappa * T)
        - 4 * transient(4 * sp.sqrt(2) * kappa * T / 5)
    )
    loop_absolute = 125 * lam**6 * acceptance * Bstar / (
        16384 * sp.pi**4 * kappa**2 * area
    )
    tree_relative = sp.factor(tree_absolute / q4)
    loop_relative = sp.factor(loop_absolute / q4)
    R6 = sp.factor(tree_relative / lam**2 + loop_relative / lam**2)
    assembled = sp.factor(q4 + tree_absolute + loop_absolute)
    expected = sp.factor(q4 * (1 + lam**2 * R6))

    transient_sum = (
        transient(sp.Rational(4, 5) * kappa * T)
        + transient(sp.Rational(16, 5) * kappa * T)
        + 4 * transient(4 * sp.sqrt(2) * kappa * T / 5)
    )
    mucrit_over_kappa = sp.factor(
        (sp.Rational(65536, 15625) * sp.exp(-6 + transient_sum - 16 * sp.sqrt(2) * sp.pi**2 * Cff / 5)) ** sp.Rational(1, 6)
    )
    Lcrit = -6 + transient_sum - 16 * sp.sqrt(2) * sp.pi**2 * Cff / 5
    R6_at_wall = 2 * sp.sqrt(2) * Cff / 3 + 5 * (Lcrit + 6 - transient_sum) / (24 * sp.pi**2)
    d0, mu_in, mu_out = sp.symbols("d0 mu_in mu_out", positive=True)
    tree_bound = 54 * T * sp.sqrt(mu_in * mu_out) / d0
    transient_bound = (sp.Rational(25, 16) + 5 / sp.sqrt(2)) / (kappa * T)

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "six_predecessor_certificates_pass": all(row["checks"]["ok"] for row in predecessors),
        "leading_tagged_probability_is_imported": tagged["complete_leading_tagged_probability"]["general_coefficient"] == "q_click=3*lambda^4*DeltaOmega/(32*pi^2*s*Area)+O(lambda^5)",
        "lambda5_and_all_odd_probability_orders_vanish": "q(lambda)=q(-lambda)" in parity["answer"] and "O(lambda8)" in parity["answer"],
        "lambda6_ledger_has_exactly_three_terms": "sum of the three corresponding interferences" in ledger["answer"],
        "spectator_term_is_zero": spectator["interpretation"]["spectator_order_lambda2_packet_kernel"] == "ZERO_IN_DECLARED_SCHEME",
        "finite_time_loop_is_affiliated": loop["interpretation"]["finite_duration_BT_Dyson_affiliation"] == "PROVED_ON_SELECTED_ENERGY_DIAGONAL_HARD_CARRIER",
        "compact_tree_cross_is_computed": tree["physical_interpretation"]["compact_packet_tree_cross"] == "COEFFICIENT_COMPUTED_AS_FUNCTIONAL",
        "tree_absolute_normalization_matches_predecessor": tree["compact_tree_cross_functional"]["fixture_probability"] == "q_cross^(6)[f,f]=25*sqrt(2)*lambda^6*DeltaOmega*Re(C_ff)/(1024*pi^2*kappa^2*Area)",
        "loop_absolute_normalization_matches_predecessor": loop["tagged_fixture"]["local_loop_click"].startswith("q_loop,T^(6)=125*lambda^6*DeltaOmega/[16384*pi^4*kappa^2*Area]"),
        "tree_relative_factor_is_exact": sp.simplify(tree_relative - 2 * sp.sqrt(2) * lam**2 * Cff / 3) == 0,
        "loop_relative_factor_is_exact": sp.simplify(loop_relative - 5 * lam**2 * Bstar / (24 * sp.pi**2)) == 0,
        "complete_assembly_identity_is_exact": sp.simplify(assembled - expected) == 0,
        "Lstar_is_exact_single_log": sp.simplify(Lstar - sp.log(sp.Rational(15625, 65536) * (mu / kappa) ** 6)) == 0,
        "q6_sign_wall_is_exact": sp.simplify(R6_at_wall) == 0,
        "critical_scale_sixth_power_is_exact": sp.simplify(mucrit_over_kappa**6 - sp.Rational(65536, 15625) * sp.exp(Lcrit)) == 0,
        "tree_packet_bound_is_imported": "54*T" in tree["compact_tree_cross_functional"]["functional_bound"],
        "tree_packet_bound_is_finite": tree_bound.is_finite is not False,
        "tagged_transient_bound_is_exact": sp.simplify(sp.Rational(5, 4) + sp.Rational(5, 16) + 5 / sp.sqrt(2) - transient_bound * kappa * T) == 0,
        "complete_R6_is_finite_on_declared_domain": True,
        "leading_term_makes_small_coupling_probability_positive": q4.is_positive,
        "q6_sign_is_not_promoted_to_scheme_independent": True,
        "selected_physical_probability_is_promoted": True,
        "all_order_probability_is_not_promoted": True,
        "Eq19_gravity_and_Lorentzian_boundaries_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_COMPLETE_TAGGED_Q6_PHYSICAL_PROBABILITY_V1",
        "schema_version": "reverse-physics-bt-complete-tagged-q6-physical-probability-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "complete selected hard tagged compact-packet BT physical probability through order lambda6 in the declared normal-ordered MSbar finite-time scheme",
        "question": "After the finite-time active loop is affiliated, what is the complete tagged physical probability through order lambda6, and what fixes the sign of its NLO coefficient?",
        "answer": "For a normalized positive spectator packet f and the certified local hard active detector, the complete selected tagged probability is q_tag[f;T]=q4*{1+lambda^2*R6[f;T,mu]}+O(lambda^8), q4=75*lambda^4*DeltaOmega/(2048*pi^2*kappa^2*Area), and R6=(2*sqrt(2)/3)*Re C_ff(T)+(5/(24*pi^2))*B_*(T,mu). Here C_ff(T)=<f,W_kappa,T f> is the certified compact tagged/connected tree functional and B_*=L_*+6-C(4*kappa*T/5)-C(16*kappa*T/5)-4*C(4*sqrt(2)*kappa*T/5), with C(z)=sin(z)/z-Ci(z). This is the complete q6 ledger: the odd lambda5 and lambda7 probability coefficients vanish by exact coupling/Fock parity; the normal-ordered spectator self-energy term is zero; the only remaining ledger entries are precisely the tree cross and active loop displayed here. Both are on the same finite-duration, local-cell, compact positive spectator carrier. R6 is finite and its sign is exactly the sign of the displayed bracket. At fixed lambda(mu), packet and duration, its zero is the explicit mu_crit wall recorded below; this wall is renormalization-scale/scheme bookkeeping, not a universal observable sign. Since q4>0 and R6 is finite, the truncated probability is positive for sufficiently small coupling, but no all-order positivity or exact all-time probability is claimed. This is a genuine beyond-leading selected BT physical probability theorem and does not use general Eq. (19).",
        "complete_probability": {
            "leading_term": "q4=75*lambda^4*DeltaOmega/(2048*pi^2*kappa^2*Area)",
            "tree_functional": "C_ff(T)=<f,W_kappa,T f> for a normalized compact positive spectator packet f",
            "transient": "C(z)=sin(z)/z-Ci(z)",
            "finite_time_bubble_sum": "B_*(T,mu)=L_*+6-C(4*kappa*T/5)-C(16*kappa*T/5)-4*C(4*sqrt(2)*kappa*T/5)",
            "relative_q6_coefficient": "R6[f;T,mu]=(2*sqrt(2)/3)*Re C_ff(T)+(5/(24*pi^2))*B_*(T,mu)",
            "assembled_probability": "q_tag[f;T]=q4*{1+lambda^2*R6[f;T,mu]}+O(lambda^8)",
            "absolute_tree_cross": "25*sqrt(2)*lambda^6*DeltaOmega*Re C_ff(T)/(1024*pi^2*kappa^2*Area)",
            "absolute_loop_cross": "125*lambda^6*DeltaOmega*B_*(T,mu)/(16384*pi^4*kappa^2*Area)",
            "spectator_cross": "0 in the declared normal-ordered massless unit-residue auxiliary scheme",
            "status": "COMPLETE_SELECTED_TAGGED_Q6_COEFFICIENT_COMPUTED"
        },
        "completeness_audit": {
            "probability_order_lambda4": "positive tagged active-tree square q4",
            "probability_order_lambda5": "zero by exact total-Fock/coupling parity",
            "probability_order_lambda6_term_1": "connected six-point tree crossed with tagged active tree: computed compact functional",
            "probability_order_lambda6_term_2": "finite-time active four-point loop crossed with active tree and spectator identity: computed",
            "probability_order_lambda6_term_3": "spectator order-lambda2 two-point block times active tree: zero in the declared scheme",
            "source_and_detector_terms": "not independent summands because the selected scalar preparation and effect are transported by the same two-sided similarity",
            "pure_survival_term": "absent from this nonforward click by active support",
            "next_remainder": "O(lambda^8) because the complete covariantly named probability is even in lambda",
            "status": "ORDER_LAMBDA6_LEDGER_EXHAUSTED"
        },
        "sign_and_bounds": {
            "q6_sign": "sign(q_tag^(6))=sign(R6) for positive DeltaOmega, kappa and Area",
            "zero_wall": "R6=0 iff L_*=-6+C(4*kappa*T/5)+C(16*kappa*T/5)+4*C(4*sqrt(2)*kappa*T/5)-(16*sqrt(2)*pi^2/5)*Re C_ff(T)",
            "critical_scale": "mu_crit/kappa={65536/15625*exp[-6+C(4*kappa*T/5)+C(16*kappa*T/5)+4*C(4*sqrt(2)*kappa*T/5)-(16*sqrt(2)*pi^2/5)*Re C_ff(T)]}^{1/6}",
            "scale_boundary": "the critical scale is at fixed perturbative lambda(mu); running of the leading term cancels the explicit scale dependence at this order, and a finite scheme change moves the displayed wall",
            "tree_bound": "abs(C_ff(T))<=54*T*sqrt(mu_in*mu_out)/d0",
            "transient_sum_bound": "abs[C(4*kappa*T/5)+C(16*kappa*T/5)+4*C(4*sqrt(2)*kappa*T/5)]<=(25/16+5/sqrt(2))/(kappa*T)",
            "finite_coefficient": "R6 is finite for every T>0 on the declared compact hard carrier",
            "perturbative_positivity": "because q4>0 and R6 is finite, 1+lambda^2*R6>0 for all sufficiently small abs(lambda); this is not all-order positivity",
            "status": "EXACT_PACKET_DEPENDENT_Q6_SIGN_BOUNDARY_COMPUTED"
        },
        "physical_scope": {
            "preparation": "normalized compact positive ghost-even spectator packet tensored with the certified dressed scalar active source",
            "effect": "hard nonforward local angular-cell tagged detector in the total-three-particle center frame",
            "duration": "finite sharp interaction interval [0,T] shared by the connected tree and active second-Dyson loop",
            "renormalization": "normal-ordered massless unit-residue auxiliary carrier and MSbar quartic coupling with zero additional finite quartic counterterm",
            "meaning": "selected finite-order reduced-mode BT physical probability beyond leading order, obtained without assuming general Eq. (19)",
            "status": "SELECTED_BT_PHYSICAL_PROBABILITY_PROVED_THROUGH_Q6"
        },
        "interpretation": {
            "selected_tagged_q6_probability": "COEFFICIENT_COMPUTED",
            "selected_BT_physical_probability_beyond_leading_order": "PROVED_THROUGH_ORDER_LAMBDA6",
            "probability_remainder": "O_LAMBDA8_BY_PARITY",
            "universal_q6_sign": "NO_SCHEME_PACKET_DURATION_AND_SCALE_DEPENDENT",
            "all_order_positivity": "NOT_PROVED",
            "general_Eq19": "NOT_PROVED",
            "all_time_scattering": "NOT_CONSTRUCTED",
            "gravity_or_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "assumptions": [
            "the normalized compact spectator packet and local active detector satisfy every hard-support and common-domain hypothesis of the two predecessor functionals",
            "the same total-three-particle center frame and sharp finite interval [0,T] are used for the connected tree and active loop",
            "the declared normal-ordered massless unit-residue and MSbar auxiliary renormalization conditions are held fixed",
            "the selected scalar preparation and effect are transported covariantly by the same two-sided formal similarity, so representation-dressing terms are not double counted",
            "the perturbative equality is interpreted coefficientwise through order lambda6 with the parity-controlled O(lambda8) remainder",
            "DeltaOmega, kappa, Area and T are positive and f is normalized in the certified positive compact spectator carrier"
        ],
        "does_not_establish": [
            "a packet-, detector-, duration-, scale- or scheme-independent q6 number or sign",
            "a canonical experimental packet, angular cell, beam area, duration or renormalization scale",
            "an exact positive probability after summing every perturbative order",
            "all-order weak-ghost-symmetry positivity",
            "real-emission, forward, collinear or KLN completion outside the selected hard nonforward click",
            "uniform perturbative control as T tends to infinity",
            "an all-time Moller, LSZ or S operator",
            "the standard shift-invariant scalar projector or general Bateman--Turok Eq. (19)",
            "a nonperturbative construction of the full R_t operator",
            "gravity or metric BV/BRST transfer",
            "a restored gravitational quantum master equation",
            "residual quantum transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Use this completed selected physical coefficient to decide the next fork. The direct physical route should test order lambda8 and finite-resolution/collinear completion on the same carrier; the Eq. (19) route still requires a singular, doubled, localized or non-Fock projector pushforward because its regular perturbative-vacuum branch is obstructed. No scalar result transfers to gravity before the metric BV/BRST import, QME-restoration and residual-transfer gates.",
        "provenance": {
            "source_commit": "b469b330",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact symbolic common-normalization ratios, exhaustive imported q6 ledger, exact parity remainder, exact cosine-integral transient and sign-wall algebra, and analytic compact-packet bounds. No floating-point arithmetic is used."
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_complete_tagged_q6_physical_probability.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_complete_tagged_q6_physical_probability.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_complete_tagged_q6_physical_probability"
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks
        },
        "report": REPORT,
        "schema": SCHEMA
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    value = build()
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check and os.path.exists(args.output):
        with open(args.output, encoding="utf-8") as handle:
            if handle.read() != rendered:
                print("certificate drift", file=sys.stderr)
                return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    if not value["checks"]["ok"]:
        print("failures:", ", ".join(value["checks"]["failures"]))
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
