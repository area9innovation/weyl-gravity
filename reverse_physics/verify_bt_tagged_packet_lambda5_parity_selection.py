#!/usr/bin/env python3
"""Independent verifier for the tagged BT lambda-five parity selection."""
from __future__ import annotations

import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_PACKET_LAMBDA5_PARITY_SELECTION_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-tagged-packet-lambda5-parity-selection-v1.schema.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def matrix(rows):
    return sp.Matrix([[sp.Rational(value) for value in row] for row in rows])


def verify(certificate):
    inputs = certificate["provenance"]["inputs"]
    predecessors = [load(os.path.join(ROOT, row["path"])) for row in inputs if "/certificates/" in row["path"]]
    pred = {row["certificate"]: row for row in predecessors}
    compact = pred["REVERSE_PHYSICS_BT_TAGGED_CONNECTED_COMPACT_PACKET_INTERFERENCE_V1"]
    source = pred["REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_COMPACT_WAVEPACKET_V1"]
    signed = pred["REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1"]

    # Rebuild the two exact covariances without importing producer functions.
    lam, phi, X, Y = sp.symbols("lambda phi X Y")
    action = (X + lam * Y) ** 2
    action_flip = action.subs({X: -X, lam: -lam}, simultaneous=True)
    omega = sum(lam**n * phi ** (n + 1) / sp.factorial(n + 1) for n in range(8))
    omega_flip = omega.subs({lam: -lam, phi: -phi}, simultaneous=True)
    upsilon = sum((-lam * phi) ** n / sp.factorial(n) for n in range(8)) * (X + lam * Y)
    upsilon_flip = upsilon.subs({lam: -lam, phi: -phi, X: -X}, simultaneous=True)

    graph_count = 0
    graph_parity = True
    for v3 in range(9):
        for v4 in range(7):
            for internal in range(12):
                external = 3 * v3 + 4 * v4 - 2 * internal
                if external < 0:
                    continue
                graph_count += 1
                graph_parity &= external % 2 == (v3 + 2 * v4) % 2

    witness = certificate["finite_Krein_witness"]
    gram = matrix(witness["metric"])
    parity = matrix(witness["parity"])
    y2 = sp.Matrix([sp.Rational(value) for value in witness["y2"]])
    y3 = sp.Matrix([sp.Rational(value) for value in witness["y3"]])
    cross = 2 * (y2.T * gram * y3)[0]
    broken = gram.copy()
    broken[0, 2] = broken[2, 0] = 1
    broken_cross = 2 * (y2.T * broken * y3)[0]

    covariance = certificate["exact_covariance"]
    selection = certificate["tagged_output_selection"]
    interpretation = certificate["interpretation"]
    boundaries = certificate["does_not_establish"]
    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "all_input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in inputs),
        "six_predecessors_pass": len(predecessors) == 6 and all(row["checks"]["ok"] for row in predecessors),
        "dependency_boundary_is_exact": certificate["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_is_coefficient_computed": certificate["lifecycle_state"] == "COEFFICIENT_COMPUTED",
        "action_covariance_is_independently_rebuilt": sp.expand(action - action_flip) == 0,
        "Omega_covariance_is_independently_rebuilt": sp.expand(omega + omega_flip) == 0,
        "Upsilon_covariance_is_independently_rebuilt": sp.expand(upsilon + upsilon_flip) == 0,
        "covariance_is_total_Fock_not_ghost_parity": covariance["distinction"] == "Pi_F is not BT ghost parity kappa and is not the SO+(1,1) charge",
        "probability_evenness_is_recorded": covariance["probability"] == "q(lambda)=q(-lambda)",
        "larger_graph_enumeration_passes": graph_count > certificate["vertex_and_graph_selection"]["enumerated_fixture_count"] and graph_parity,
        "vertex_graph_identity_is_recorded": certificate["vertex_and_graph_selection"]["graph_identity"].startswith("3*V3+4*V4"),
        "source_is_three_particle_odd": "Upsilon^3" in source["positive_packet_frame"]["declared_source"] and "Omega^3" in source["positive_packet_frame"]["declared_source"],
        "order_lambda_map_has_cubic_lift": "cubic generator" in signed["answer"],
        "Krein_parity_is_selfadjoint": parity.T * gram == gram * parity,
        "Krein_metric_is_parity_invariant": parity.T * gram * parity == gram,
        "leading_output_is_odd": parity * y2 == -y2,
        "next_output_is_even": parity * y3 == y3,
        "lambda5_cross_is_independently_zero": cross == 0 == sp.Rational(witness["cross"]),
        "parity_breaking_mutation_is_nonzero": broken_cross == 20 == sp.Rational(witness["parity_breaking_cross"]),
        "complete_y3_ledger_is_recorded": all(term in selection["complete_next_output"] for term in ("A3 psi0", "A2 psi1", "detector correction")),
        "lambda5_coefficient_is_exactly_zero": selection["lambda5_coefficient"] == "q_tag^(5)=2*Re<y2,y3>_K=0" and interpretation["probability_order_lambda5"] == "EXACTLY_ZERO",
        "remainder_begins_at_lambda6": interpretation["tagged_probability_remainder_after_lambda4"] == "BEGINS_AT_LAMBDA6" and "O(lambda^8)" in selection["probability_series"],
        "known_lambda6_tree_cross_is_retained": compact["physical_interpretation"]["fixed_compact_packet_box_refinement"] == "FINITE_AND_GENERALLY_NONZERO" and interpretation["compact_packet_tree_cross_at_lambda6"] == "NONZERO_FUNCTIONAL",
        "complete_lambda6_is_not_promoted": interpretation["complete_order_lambda6_probability"] == "NOT_COMPUTED" and "the numerical value of the complete probability-order-lambda6 coefficient" in boundaries,
        "noncovariant_detector_boundary_is_explicit": any("held noncovariantly" in row for row in boundaries),
        "Eq19_gravity_Lorentzian_boundaries_remain_open": interpretation["general_Eq19"] == "NOT_PROVED" and interpretation["gravity_or_BV_BRST_transfer"] == "NOT_CONSTRUCTED" and interpretation["Lorentzian_causal_claim"] == "NOT_ESTABLISHED",
        "next_gate_is_complete_q6_ledger": "complete q6 object ledger" in certificate["next_gate"] and "active renormalized four-point one-loop" in certificate["next_gate"],
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
