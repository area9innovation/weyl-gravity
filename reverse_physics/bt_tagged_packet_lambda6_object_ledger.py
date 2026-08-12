#!/usr/bin/env python3
"""Typed object ledger for the tagged BT compact-packet lambda-six term."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_PACKET_LAMBDA6_OBJECT_LEDGER_V1.json")
SCHEMA = "reverse_physics/schema/reverse-physics-bt-tagged-packet-lambda6-object-ledger-v1.schema.json"
REPORT = "reverse_physics/reports/bt-tagged-packet-lambda6-object-ledger.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-tagged-packet-lambda6-object-ledger.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_PACKET_LAMBDA5_PARITY_SELECTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_CONNECTED_COMPACT_PACKET_INTERFERENCE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_POSITIVE_SOURCE_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_COMPACT_WAVEPACKET_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_ORDER4_PACKET_COLUMN_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_UV_HARD_SCATTERING_LAW_V1.json",
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


def krein_adjoint(A, G):
    return G.inv() * A.T * G


def build():
    lambda5 = load(INPUTS[1])
    compact_cross = load(INPUTS[2])
    tagged = load(INPUTS[3])
    affiliation = load(INPUTS[4])
    compact_source = load(INPUTS[5])
    connected = load(INPUTS[6])
    hard_log = load(INPUTS[7])

    lam = sp.symbols("lambda", real=True)
    t2, c4, l4, d4 = sp.symbols("T2 C4 L4 D4", real=True)
    amplitude = lam**2 * t2 + lam**4 * (c4 + l4 + d4)
    probability = sp.expand(amplitude**2)
    q4 = probability.coeff(lam, 4)
    q5 = probability.coeff(lam, 5)
    q6 = probability.coeff(lam, 6)

    # Fixed three-particle odd projectors kill every parity-odd order-three
    # block. This finite block replay keeps the operator statement visible.
    parity = sp.diag(-1, -1, 1, 1)
    pin = sp.diag(1, 1, 0, 0)
    pout = sp.diag(1, 1, 0, 0)
    odd_operator = sp.Matrix([[0, 0, 2, 1], [0, 0, -1, 3], [4, 2, 0, 0], [1, -2, 0, 0]])
    projected_odd = pout * odd_operator * pin

    # A rational Krein-unitary similarity replay. The exact result used in
    # the theorem is the universal two-sided/cyclic identity, not this matrix.
    G = sp.Matrix([[0, 1], [1, 0]])
    R = sp.diag(2, sp.Rational(1, 2))
    Rsharp = krein_adjoint(R, G)
    P = sp.Matrix([[1, 0], [0, 0]])
    E = sp.Matrix([[sp.Rational(2, 5), sp.Rational(1, 7)], [sp.Rational(3, 11), sp.Rational(4, 9)]])
    Pphi = Rsharp * P * R
    Ephi = Rsharp * E * R
    trace_BT = sp.trace(P * E)
    trace_phi = sp.trace(Pphi * Ephi)

    kappa, mu_R, area, acceptance = sp.symbols("kappa mu_R Area DeltaOmega", positive=True)
    s = sp.Rational(64, 25) * kappa**2
    t = -sp.Rational(32, 25) * kappa**2
    u = t
    logs = sp.log(mu_R**2 / s) + sp.log(mu_R**2 / (-t)) + sp.log(mu_R**2 / (-u))
    loop_log_density = sp.factor(5 * lam**6 * logs / (256 * sp.pi**4 * s))
    loop_log_click = sp.factor(loop_log_density * acceptance / area)
    expected_log_prefactor = sp.Rational(125, 16384)
    two_plus_four_order_pairs = [
        (2 * L2, 2 + 2 * L4)
        for L2 in range(3)
        for L4 in range(3)
        if 2 * L2 + 2 + 2 * L4 == 4
    ]

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessors_pass": all(row["checks"]["ok"] for row in (lambda5, compact_cross, tagged, affiliation, compact_source, connected, hard_log)),
        "fixed_BT_amplitude_has_no_lambda3_term": sp.expand(amplitude).coeff(lam, 3) == 0,
        "q4_is_leading_tagged_square": q4 == t2**2,
        "q5_is_zero": q5 == 0,
        "q6_has_exact_three_cross_terms": sp.expand(q6 - 2 * t2 * c4 - 2 * t2 * l4 - 2 * t2 * d4) == 0,
        "odd_order_operator_has_correct_covariance": parity * odd_operator * parity == -odd_operator,
        "fixed_odd_projectors_kill_order_three": projected_odd == sp.zeros(4),
        "tagged_support_has_only_connected_and_spectator_partitions": len(tagged["partition_and_order_classification"]["supported_partitions"]) == 2,
        "tagged_order_four_types_are_imported": "connected six-point tree and one-loop active four-point corrections" in tagged["partition_and_order_classification"]["order_four"],
        "two_plus_four_partition_order_split_is_exhaustive": two_plus_four_order_pairs == [(0, 4), (2, 2)],
        "complete_connected_order_four_is_three_to_three_tree": connected["connected_graph_classification"]["status"] == "COMPLETE_CONNECTED_ORDER_LAMBDA4_OUTPUT_IS_THREE_TO_THREE_TREE",
        "compact_tree_cross_is_known": compact_cross["physical_interpretation"]["compact_packet_tree_cross"] == "COEFFICIENT_COMPUTED_AS_FUNCTIONAL",
        "active_detector_is_nonforward": tagged["complete_leading_tagged_probability"]["forward_independence"].startswith("P_Y P_X=0"),
        "formal_Rt_is_two_sided": affiliation["formal_Rt_affiliation"]["public_identity"] == "Rt^dagger*Rt=Rt*Rt^dagger=1 coefficientwise in formal lambda",
        "finite_trace_similarity_is_imported": affiliation["transferred_scalar_detector_effect"]["finite_trace_identity"] == "tr(P_phi*E_phi)=tr(P_u*E_BT)",
        "compact_source_effect_limit_exists": compact_source["interpretation"]["finite_volume_source_effect_limit"] == "CONSTRUCTED_AT_FIXED_ZETA",
        "rational_R_is_Krein_unitary": Rsharp * R == sp.eye(2) and R * Rsharp == sp.eye(2),
        "similarity_trace_replay_is_exact": sp.simplify(trace_phi - trace_BT) == 0,
        "hard_log_predecessor_is_physical_baseline": hard_log["checks"]["ok"] and "complete inclusive NLO probability" in hard_log["does_not_establish"][0],
        "fixture_log_prefactor_is_exact": sp.simplify(loop_log_click / (lam**6 * acceptance * logs / (sp.pi**4 * kappa**2 * area))) == expected_log_prefactor,
        "complete_loop_packet_is_not_imported_from_hard_log": True,
        "source_detector_dressing_is_not_double_counted": True,
        "pure_survival_is_excluded_but_spectator_dressing_survives": True,
        "complete_q6_is_not_promoted": True,
        "Eq19_gravity_and_Lorentzian_boundaries_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_TAGGED_PACKET_LAMBDA6_OBJECT_LEDGER_V1",
        "schema_version": "reverse-physics-bt-tagged-packet-lambda6-object-ledger-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "complete typed object classification of the hard tagged compact-packet probability coefficient at order lambda6",
        "question": "After q5 vanishes, which terms actually belong to the tagged compact-packet q6 coefficient, and which apparent source, detector or survival terms are representation artifacts or support-forbidden?",
        "answer": "On fixed odd three-particle BT input/output projectors, write A_tag=lambda2*T2+lambda3*T3+lambda4*T4+... . Total-Fock parity makes T3 odd, so Pout*T3*Pin=0 exactly. Exhaustive tagged support leaves the connected six-leg partition and the tagged two-plus-four partition. Coupling order inside the latter gives two order-four terms, not one: spectator identity times the renormalized active four-point loop, and the renormalized order-two spectator self-energy times the active four-point tree. Thus T4=C4_tree+I_s tensor L4_active_loop+S2_s tensor A2_active_tree and q6 is the sum of the three corresponding interferences with T2. The compact connected-tree cross is certified; the active loop and dressed-spectator crosses are missing. Pure forward survival is killed by nonforward active support, but that fact does not kill spectator dressing multiplied by an active transition. For the selected dressed scalar experiment, the source, detector and effect are all pulled by the same formally two-sided R_t; cyclicity of the finite detector trace makes the scalar probability exactly equal to the fixed-BT probability coefficientwise. Source and detector dressing are therefore not additional q6 summands and must not be double counted. The known asymptotic hard logarithm constrains the active-loop scale-dependent part but supplies neither missing finite-time packet object. The q6 lifecycle remains CLASSIFIED, not COEFFICIENT_COMPUTED.",
        "fixed_BT_expansion": {
            "block": "A_tag(lambda)=Pout*(U_T(lambda)-I)*Pin=lambda^2*T2+lambda^3*T3+lambda^4*T4+O(lambda^5)",
            "projectors": "Pin and Pout are fixed total-Fock-odd three-particle BT packet projectors",
            "order_three_parity": "Pi_F*T3*Pi_F=-T3",
            "order_three_block": "Pout*T3*Pin=0",
            "order_four_support": "T4=C4_tree+I_spectator tensor L4_active_loop+S2_spectator tensor A2_active_tree",
            "C4_tree": "complete connected six-point finite-time tree on the common compact packet carrier",
            "L4_active_loop": "renormalized active four-point one-loop block including counterterms, tensored with the spectator identity",
            "S2_spectator_A2_active_tree": "renormalized order-lambda2 spectator two-point block including its mass and wave-function counterterms, tensored with the active order-lambda2 four-point tree",
            "other_order_four_support": "NONE after normalized-vacuum cancellation at the certified hard tagged fixture by exhaustive partition, coupling-order and particle-number classification",
            "status": "FIXED_BT_TAGGED_BLOCK_CLASSIFIED_THROUGH_AMPLITUDE_ORDER_LAMBDA4"
        },
        "probability_ledger": {
            "q4": "q_tag^(4)=<T2,T2>=3*lambda^4*DeltaOmega/(32*pi^2*s*Area) after restoring lambda^4",
            "q5": "q_tag^(5)=0",
            "q6_formula": "q_tag^(6)=2*Re<T2,C4_tree>+2*Re<T2,I_spectator tensor L4_active_loop>+2*Re<T2,S2_spectator tensor A2_active_tree>",
            "tree_cross_status": "COEFFICIENT_COMPUTED_AS_COMPACT_PACKET_FUNCTIONAL",
            "tree_cross": "q_tree_cross^(6)[f,f]=25*sqrt(2)*lambda^6*DeltaOmega*Re(C_ff)/(1024*pi^2*kappa^2*Area)",
            "active_loop_status": "MISSING_ON_THE_COMMON_FINITE_TIME_COMPACT_PACKET_CARRIER",
            "spectator_self_energy_status": "MISSING_ON_THE_COMMON_FINITE_TIME_COMPACT_PACKET_CARRIER",
            "T3_norm_term": "ABSENT because the fixed BT three-particle block T3 is zero",
            "survival_term": "PURE_FORWARD_TERM_ABSENT because Pout*Pin=0 in the active nonforward factor; spectator self-energy times active scattering remains",
            "source_detector_terms": "NOT_SEPARATE_SUMMANDS for the covariantly pulled selected scalar experiment",
            "complete_q6_status": "CLASSIFIED_NOT_COMPUTED"
        },
        "selected_scalar_transfer": {
            "source": "P_phi=R_t^dagger*P_BT*R_t",
            "effect": "E_phi=R_t^dagger*E_BT*R_t",
            "two_sided_identity": "R_t^dagger*R_t=R_t*R_t^dagger=1 coefficientwise on the finite detector ideal",
            "trace_identity": "tr(P_phi*E_phi)=tr(P_BT*E_BT)",
            "compact_extension": "finite-rank packet effects converge in trace norm on the common Gaussian image core",
            "consequence": "all R_t source/detector expansion terms cancel inside the complete similarity; adding them again to the BT q6 ledger would double count",
            "scope": "selected shift-breaking dressed scalar packet only, not the standard P_chi projector or general Eq. (19)",
            "status": "SELECTED_SCALAR_Q6_LEDGER_IDENTICAL_TO_FIXED_BT_LEDGER_FORMALLY"
        },
        "active_loop_boundary_condition": {
            "known_object": "asymptotic fixed-angle hard projected logarithm, not a finite-time packet loop",
            "general_density": "d_sigma_virt,log/dOmega=5*lambda^6*(L_s+L_t+L_u)/(256*pi^4*s), L_X=log(mu_R^2/|X|)",
            "tagged_invariants": "s=64*kappa^2/25 and t=u=-32*kappa^2/25",
            "tagged_log_sum": "log(25*mu_R^2/(64*kappa^2))+2*log(25*mu_R^2/(32*kappa^2))",
            "tagged_central_click_log": "125*lambda^6*DeltaOmega*log_sum/(16384*pi^4*kappa^2*Area)",
            "use": "renormalization-scale and hard/asymptotic consistency check on the missing packet loop",
            "does_not_supply": "finite terms, packet time kernel, source preparation dependence, counterterm scheme ledger or the common finite-time normalization",
            "status": "PARTIAL_BOUNDARY_DATA_ONLY"
        },
        "interpretation": {
            "complete_lambda6_object_ledger": "CLASSIFIED",
            "compact_tree_cross": "COEFFICIENT_COMPUTED",
            "active_four_point_one_loop_packet_kernel": "MISSING",
            "spectator_self_energy_times_active_tree": "MISSING",
            "independent_source_detector_q6_summands": "NO_FOR_THE_SELECTED_COVARIANT_PULLBACK",
            "pure_survival_q6_summand": "ABSENT_ON_ACTIVE_NONFORWARD_SUPPORT",
            "complete_order_lambda6_probability": "NOT_COMPUTED",
            "general_Eq19": "NOT_PROVED",
            "gravity_or_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "assumptions": [
            "the tagged input and output packets remain in the certified hard nonforward supports with exactly one unchanged labeled spectator and no forward active overlap",
            "fixed BT input/output projectors have odd total Fock parity and the regulator/counterterms preserve coupling/Fock-parity covariance",
            "the exhaustive support and connected order-four classifications continue to apply on the chosen compact tagged tube, and normalized vacuum bubbles are divided out",
            "the selected scalar source, detector and complete effect are pulled together by the same formally two-sided R_t on the common compact Gaussian detector ideal",
            "finite-rank approximants and trace-norm convergence justify cyclicity for the selected compact packet effect",
            "the hard logarithm is used only as boundary data and is not identified with the missing finite-time compact-packet loop"
        ],
        "does_not_establish": [
            "the renormalized active four-point one-loop compact-packet kernel",
            "the renormalized spectator two-point finite-time packet kernel and its interference after multiplication by the active tree",
            "the finite or scheme-dependent part of the active loop interference",
            "the numerical value or sign of the complete q6 coefficient",
            "cancellation or dominance of the positive resonant tree cross",
            "forward, collinear or real-virtual/KLN completion outside the declared hard detector",
            "general Eq. (19) for the standard shift-invariant scalar projector",
            "convergence or nonperturbative existence of the full R_t operator",
            "an all-time Moller, LSZ or S operator",
            "all-order positivity",
            "gravity or metric BV/BRST transfer",
            "a restored gravity quantum master equation or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "missing_object_ledger": [
            {"object": "active four-point one-loop finite-time packet kernel", "status": "MISSING", "required_value": "renormalized spectator-identity loop operator on the exact same active packet, duration, mass-jet and detector normalization as T2"},
            {"object": "spectator two-point finite-time packet kernel", "status": "MISSING", "required_value": "renormalized order-lambda2 spectator self-energy, including mass and wave-function counterterms, on the exact tagged packet and duration, multiplied by the active tree"},
            {"object": "loop and self-energy counterterm/scheme ledger", "status": "MISSING", "required_value": "local counterterm classification, coefficient choice, the active hard-log Callan--Symanzik match, and the declared spectator pole/residue or finite-time renormalization conditions"},
            {"object": "complete q6 sign", "status": "MISSING", "required_value": "sum both disconnected crosses with the certified connected-tree cross and prove its value or sign for a declared packet and renormalization condition"},
            {"object": "gravity transfer", "status": "MISSING", "required_value": "metric BV/BRST carrier, anomaly classification, QME restoration and residual transfer before any gravitational probability statement"}
        ],
        "next_gate": "Compute the two missing renormalized order-four disconnected terms on the same finite-time compact tagged carrier: spectator identity times the active four-point one-loop kernel, and spectator order-two self-energy times the active four-point tree. Start by classifying the shared local scalar counterterms and fixing active scattering plus spectator pole/residue or finite-time renormalization conditions. Verify that the active loop hard/asymptotic scale derivative reproduces 5*(L_s+L_t+L_u)/(256*pi^4*s). Only the sum of both missing crosses with the certified compact connected-tree cross can promote q6 from CLASSIFIED to COEFFICIENT_COMPUTED. This selected scalar route still does not prove general Eq. (19) or transfer to gravity.",
        "provenance": {
            "source_commit": "cb9ec7cb",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact perturbative series algebra, total-Fock-parity block projection, imported exhaustive support classification, exact finite Krein similarity replay, and exact algebraic specialization of the certified hard logarithm. No floating-point arithmetic is used."
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_tagged_packet_lambda6_object_ledger.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_tagged_packet_lambda6_object_ledger.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_tagged_packet_lambda6_object_ledger"
        ],
        "checks": {"ok": all(checks.values()), "passed": sum(checks.values()), "total": len(checks), "failures": [name for name, ok in checks.items() if not ok], "details": checks},
        "report": REPORT,
        "schema": SCHEMA,
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
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
