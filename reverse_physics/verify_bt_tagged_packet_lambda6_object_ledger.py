#!/usr/bin/env python3
"""Independent verifier for the tagged compact-packet lambda-six ledger."""
from __future__ import annotations

import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_PACKET_LAMBDA6_OBJECT_LEDGER_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-tagged-packet-lambda6-object-ledger-v1.schema.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(certificate):
    inputs = certificate["provenance"]["inputs"]
    predecessors = [load(os.path.join(ROOT, row["path"])) for row in inputs if "/certificates/" in row["path"]]
    pred = {row["certificate"]: row for row in predecessors}
    tagged = pred["REVERSE_PHYSICS_BT_TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1"]
    cross = pred["REVERSE_PHYSICS_BT_TAGGED_CONNECTED_COMPACT_PACKET_INTERFERENCE_V1"]
    affiliation = pred["REVERSE_PHYSICS_BT_SCALAR_DRESSED_POSITIVE_SOURCE_AFFILIATION_V1"]

    lam = sp.symbols("lambda")
    T2, T3, C4, L4, D4 = sp.symbols("T2 T3 C4 L4 D4", real=True)
    amplitude = lam**2 * T2 + lam**3 * T3 + lam**4 * (C4 + L4 + D4)
    probability = sp.expand(amplitude**2)
    fixed_probability = sp.expand(probability.subs(T3, 0))

    # Rebuild the exact similarity with a different 3x3 Krein isometry.
    G = sp.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, 1]])
    R = sp.diag(2, sp.Rational(1, 2), 1)
    Rsharp = G.inv() * R.T * G
    P = sp.diag(1, 0, 1)
    E = sp.Matrix([[sp.Rational(1, 3), 2, 1], [4, sp.Rational(2, 7), 3], [2, 1, sp.Rational(5, 11)]])
    Pphi = Rsharp * P * R
    Ephi = R.inv() * E * R  # ordinary similarity replay for cyclic trace
    trace_equal = sp.trace(Pphi * Ephi) == sp.trace(P * E)

    kappa, mu_R = sp.symbols("kappa mu_R", positive=True)
    s = sp.Rational(64, 25) * kappa**2
    t = -sp.Rational(32, 25) * kappa**2
    log_sum = sp.log(mu_R**2 / s) + 2 * sp.log(mu_R**2 / (-t))
    expected_log_sum = sp.log(25 * mu_R**2 / (64 * kappa**2)) + 2 * sp.log(25 * mu_R**2 / (32 * kappa**2))
    two_plus_four_order_pairs = sorted(
        (2 * loop_2, 2 + 2 * loop_4)
        for loop_2 in range(3)
        for loop_4 in range(3)
        if 2 * loop_2 + 2 + 2 * loop_4 == 4
    )

    fixed = certificate["fixed_BT_expansion"]
    ledger = certificate["probability_ledger"]
    transfer = certificate["selected_scalar_transfer"]
    boundary = certificate["active_loop_boundary_condition"]
    interpretation = certificate["interpretation"]
    limits = certificate["does_not_establish"]
    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "all_input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in inputs),
        "seven_predecessors_pass": len(predecessors) == 7 and all(row["checks"]["ok"] for row in predecessors),
        "dependency_tags_are_exact": certificate["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_is_classified": certificate["lifecycle_state"] == "CLASSIFIED",
        "generic_q4_is_rebuilt": probability.coeff(lam, 4) == T2**2,
        "generic_q5_is_rebuilt": probability.coeff(lam, 5) == 2 * T2 * T3,
        "fixed_block_T3_zero_is_typed": fixed["order_three_block"] == "Pout*T3*Pin=0",
        "fixed_q5_is_zero": fixed_probability.coeff(lam, 5) == 0 and ledger["q5"] == "q_tag^(5)=0",
        "fixed_q6_is_three_crosses": sp.expand(fixed_probability.coeff(lam, 6) - 2*T2*C4 - 2*T2*L4 - 2*T2*D4) == 0,
        "recorded_q6_formula_is_exact": ledger["q6_formula"] == "q_tag^(6)=2*Re<T2,C4_tree>+2*Re<T2,I_spectator tensor L4_active_loop>+2*Re<T2,S2_spectator tensor A2_active_tree>",
        "tagged_support_import_has_two_partitions": len(tagged["partition_and_order_classification"]["supported_partitions"]) == 2,
        "order_four_support_has_all_three_terms": fixed["order_four_support"] == "T4=C4_tree+I_spectator tensor L4_active_loop+S2_spectator tensor A2_active_tree",
        "two_plus_four_order_split_is_independently_exhaustive": two_plus_four_order_pairs == [(0, 4), (2, 2)],
        "tree_cross_is_imported_as_nonzero_functional": cross["physical_interpretation"]["fixed_compact_packet_box_refinement"] == "FINITE_AND_GENERALLY_NONZERO" and ledger["tree_cross_status"] == "COEFFICIENT_COMPUTED_AS_COMPACT_PACKET_FUNCTIONAL",
        "active_loop_is_missing": ledger["active_loop_status"] == "MISSING_ON_THE_COMMON_FINITE_TIME_COMPACT_PACKET_CARRIER" and interpretation["active_four_point_one_loop_packet_kernel"] == "MISSING",
        "spectator_self_energy_cross_is_missing": ledger["spectator_self_energy_status"] == "MISSING_ON_THE_COMMON_FINITE_TIME_COMPACT_PACKET_CARRIER" and interpretation["spectator_self_energy_times_active_tree"] == "MISSING",
        "pure_survival_is_absent_but_dressed_spectator_remains": ledger["survival_term"].startswith("PURE_FORWARD_TERM_ABSENT") and "spectator self-energy" in ledger["survival_term"] and tagged["complete_leading_tagged_probability"]["forward_independence"].startswith("P_Y P_X=0"),
        "source_detector_are_not_double_counted": ledger["source_detector_terms"].startswith("NOT_SEPARATE_SUMMANDS") and "double count" in transfer["consequence"],
        "public_two_sided_identity_is_imported": affiliation["formal_Rt_affiliation"]["public_identity"].startswith("Rt^dagger*Rt=Rt*Rt^dagger=1") and transfer["two_sided_identity"].startswith("R_t^dagger*R_t=R_t*R_t^dagger=1"),
        "selected_trace_identity_is_imported": affiliation["transferred_scalar_detector_effect"]["finite_trace_identity"].startswith("tr(P_phi*E_phi)=") and transfer["trace_identity"].startswith("tr(P_phi*E_phi)="),
        "independent_similarity_replay_is_exact": Rsharp * R == sp.eye(3) and trace_equal,
        "hard_log_specialization_is_exact": sp.expand_log(log_sum, force=True) == sp.expand_log(expected_log_sum, force=True),
        "hard_log_is_only_boundary_data": boundary["status"] == "PARTIAL_BOUNDARY_DATA_ONLY" and "not a finite-time packet loop" in boundary["known_object"],
        "complete_q6_is_not_promoted": interpretation["complete_order_lambda6_probability"] == "NOT_COMPUTED" and "the numerical value or sign of the complete q6 coefficient" in limits,
        "general_Eq19_is_not_promoted": interpretation["general_Eq19"] == "NOT_PROVED" and "standard P_chi" in transfer["scope"],
        "gravity_Lorentzian_boundaries_are_exact": interpretation["gravity_or_BV_BRST_transfer"] == "NOT_CONSTRUCTED" and interpretation["Lorentzian_causal_claim"] == "NOT_ESTABLISHED",
        "next_gate_has_both_missing_packet_terms": "two missing renormalized order-four disconnected terms" in certificate["next_gate"] and "spectator order-two self-energy" in certificate["next_gate"],
    }
    return {name: bool(value) for name, value in checks.items()}


def main():
    checks = verify(load(CERT))
    failures = [name for name, ok in checks.items() if not ok]
    print("checks %d/%d" % (sum(checks.values()), len(checks)))
    print("RESULT:", "PASS" if not failures else "FAIL")
    if failures:
        print("failures:", ", ".join(failures))
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
