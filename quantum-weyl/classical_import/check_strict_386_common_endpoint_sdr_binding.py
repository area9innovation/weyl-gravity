#!/usr/bin/env python3
"""Independently check the strict common endpoint-SDR binding."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1.json"
GRAPH = HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
UNARY = HERE / "certificates/STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1.json"
D_ACTION = HERE / "certificates/STRICT_386_FULL_D_ACTION_V1.json"
Q2 = HERE / "certificates/STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.json"
Q3 = HERE / "certificates/STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
SPLIT_Q1 = HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
SHEAR = HERE / "certificates/STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1.json"
TYPE_AUDIT = HERE / "certificates/STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1.json"
GATE = HERE / "certificates/CLASSICAL_IMPORT_GATE_V18_RECONCILIATION.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def pin(value: dict[str, Any], result_id: str) -> str | None:
    matches = [
        item.get("sha256")
        for item in value.get("provenance", {}).get("inputs", [])
        if item.get("result_id", item.get("result_or_schema_id")) == result_id
    ]
    return matches[0] if len(matches) == 1 else None


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = load(RESULT) if value is None else value
    paths = (GRAPH, UNARY, D_ACTION, Q2, Q3, PAIRING, SPLIT_Q1, SHEAR, TYPE_AUDIT, GATE)
    graph, unary, d_action, q2, q3, pairing, split_q1, shear, type_audit, gate = (
        load(path) for path in paths
    )
    errors: list[str] = []
    if (
        value.get("result_id") != "STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1"
        or value.get("result_state") != "M3L_COMMON_ENDPOINT_SDR_BOUND_M3R_AND_GATE_A_OPEN"
        or value.get("lifecycle") != "CLASSIFIED"
        or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
    ):
        errors.append("identity/lifecycle/tags")

    identities = [
        graph.get("result_id"), unary.get("result_id"), d_action.get("result_id"),
        q2.get("result_id"), q3.get("result_id"), pairing.get("result_id"),
        split_q1.get("result_id"), shear.get("result_id"), type_audit.get("result_id"), gate.get("result_id"),
    ]
    expected_identities = [
        "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1", "STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1",
        "STRICT_386_FULL_D_ACTION_V1", "STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1",
        "STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1", "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1",
        "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1", "STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1",
        "STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1", "CLASSICAL_IMPORT_GATE_V18_RECONCILIATION",
    ]
    if identities != expected_identities:
        errors.append("input identity inventory")

    expected_provenance = [
        {
            "path": str(path.relative_to(ROOT)),
            "result_or_artifact_id": source["result_id"],
            "sha256": sha(path),
        }
        for path, source in zip(paths, (graph, unary, d_action, q2, q3, pairing, split_q1, shear, type_audit, gate), strict=True)
    ]
    actual_provenance = value.get("provenance", {}).get("inputs", [])
    if len(actual_provenance) != 10:
        errors.append("provenance cardinality")
    for actual, expected in zip(actual_provenance, expected_provenance, strict=False):
        if any(actual.get(key) != wanted for key, wanted in expected.items()) or not actual.get("role"):
            errors.append("provenance pin " + expected["result_or_artifact_id"])

    graph_file = sha(GRAPH)
    pairing_file = sha(PAIRING)
    q1_file = sha(SPLIT_Q1)
    shear_file = sha(SHEAR)
    d_file = sha(D_ACTION)
    q2_file = sha(Q2)
    graph_snapshot = graph.get("graph_snapshot", {})
    compatibility = {
        "unary_pins_graph_certificate": unary.get("common_snapshot", {}).get("graph_dependency_sha256") == graph_file,
        "D_pins_graph_certificate": pin(d_action, graph["result_id"]) == graph_file,
        "q2_pins_graph_certificate": pin(q2, graph["result_id"]) == graph_file,
        "q2_and_q3_pin_same_split_q1": pin(q2, split_q1["result_id"]) == pin(q3, split_q1["result_id"]) == q1_file,
        "graph_and_q2_pin_same_split_q1": pin(graph, split_q1["result_id"]) == q1_file,
        "graph_q2_q3_pin_same_pairing": pin(graph, pairing["result_id"]) == pin(q2, pairing["result_id"]) == pin(q3, pairing["result_id"]) == pairing_file,
        "graph_q2_q3_pin_same_shear": pin(graph, shear["result_id"]) == pin(q2, shear["result_id"]) == pin(q3, shear["result_id"]) == shear_file,
        "q2_and_q3_pin_same_D": pin(q2, d_action["result_id"]) == pin(q3, d_action["result_id"]) == d_file,
        "q3_pins_accepted_q2_certificate": pin(q3, q2["result_id"]) == q2_file,
        "q3_pins_accepted_q2_object": q3.get("source_q3_snapshot", {}).get("accepted_q2_snapshot_sha256") == q2.get("source_q2_snapshot", {}).get("sha256"),
        "graph_and_D_basis_hash_agree": graph_snapshot.get("basis_sha256") == d_action.get("extended_common_snapshot", {}).get("basis_sha256") == pairing.get("canonical_hashes", {}).get("component_basis_sha256"),
        "graph_and_D_pairing_hash_agree": graph_snapshot.get("pairing_sha256") == d_action.get("extended_common_snapshot", {}).get("pairing_sha256") == pairing.get("canonical_hashes", {}).get("pairing_serialization_sha256"),
        "graph_and_D_q1_hash_agree": graph_snapshot.get("graph_q1_sha256") == d_action.get("extended_common_snapshot", {}).get("graph_q1_sha256"),
        "q2_graph_DAG_exact": q2.get("graph_transport", {}).get("exact_compositional_DAG_exported") is True,
        "q3_graph_DAG_exact": q3.get("graph_transport", {}).get("exact_compositional_DAG_exported") is True,
    }
    if compatibility != value.get("compatibility_checks") or not all(compatibility.values()):
        errors.append("independent cross-certificate compatibility")

    graph_maps = graph.get("graph_sdr_component_maps", {})
    object_hashes = {
        "component_basis_sha256": graph_snapshot.get("basis_sha256"),
        "odd_pairing_sha256": graph_snapshot.get("pairing_sha256"),
        "split_q1_snapshot_sha256": graph_snapshot.get("split_unary_snapshot_sha256"),
        "canonical_shear_snapshot_sha256": graph_snapshot.get("canonical_shear_snapshot_sha256"),
        "graph_q1_sha256": graph_snapshot.get("graph_q1_sha256"),
        "H_alg_graph_sha256": graph_maps.get("H_alg_graph", {}).get("sha256"),
        "i_end_graph_sha256": graph_maps.get("i_end_graph", {}).get("sha256"),
        "p_end_graph_sha256": graph_maps.get("p_end_graph", {}).get("sha256"),
        "P_end_graph_sha256": graph_maps.get("P_end_graph", {}).get("sha256"),
        "P_alg_graph_sha256": graph_maps.get("P_alg_graph", {}).get("sha256"),
        "R_graph_sha256": graph_maps.get("R_graph", {}).get("sha256"),
        "represented_green_common_snapshot_sha256": unary.get("common_snapshot", {}).get("sha256"),
        "D_action_sha256": d_action.get("D_action", {}).get("sha256"),
        "q2_source_snapshot_sha256": q2.get("source_q2_snapshot", {}).get("sha256"),
        "q2_graph_transport_sha256": q2.get("canonical_hashes", {}).get("graph_transport_sha256"),
        "q3_source_snapshot_sha256": q3.get("source_q3_snapshot", {}).get("sha256"),
        "q3_graph_transport_sha256": q3.get("canonical_hashes", {}).get("graph_transport_sha256"),
    }
    manifest = value.get("common_manifest", {})
    if (
        manifest.get("manifest_id") != "STRICT_386_LOCAL_ENDPOINT_NONLINEAR_COMMON_MANIFEST_V1"
        or manifest.get("coordinate_presentation") != "UNSHIFTED_CURVATURE_GRAPH_WITH_EXACT_SPLIT_SOURCE_DAGS"
        or (manifest.get("carrier_rows"), manifest.get("endpoint_rows"), manifest.get("contracted_rows")) != (386, 30, 356)
        or manifest.get("object_hashes") != object_hashes
        or manifest.get("artifact_pins") != actual_provenance
    ):
        errors.append("common manifest projection")
    manifest_body = {key: manifest.get(key) for key in (
        "manifest_id", "coordinate_presentation", "carrier_rows", "endpoint_rows",
        "contracted_rows", "artifact_pins", "object_hashes",
    )}
    if manifest.get("sha256") != digest(manifest_body):
        errors.append("common manifest digest")

    graph_replay = graph.get("exact_replay", {})
    expected_replay = {
        "compatibility_links_checked": len(compatibility),
        "compatibility_defects": sum(not passed for passed in compatibility.values()),
        "qH_plus_Hq_defects": graph_replay.get("qH_plus_Hq_defects"),
        "p_i_identity_defects": graph_replay.get("p_graph_i_graph_identity_defects"),
        "i_p_projector_defects": graph_replay.get("i_graph_p_graph_equals_P_end_defects"),
        "normalized_side_condition_defects": sum(graph_replay.get(key, -1000) for key in (
            "H_squared_defects", "H_i_graph_defects", "p_graph_H_defects",
            "P_end_squared_defects", "P_alg_squared_defects", "P_end_P_alg_defects", "P_alg_P_end_defects",
        )),
        "endpoint_SDR_cyclicity_defects": graph_replay.get("H_alg_graph_cyclicity_defects"),
        "transported_suspension_PBW_reduced_cyclicity_defects": graph_replay.get("transported_R_PBW_reduced_cyclicity_defects"),
        "D_q1_commutator_defects": d_action.get("exact_replay", {}).get("D_q1_commutator_defects"),
        "graph_q1_q2_defects": q2.get("q1_q2_replay", {}).get("graph_386_q1_q2_defects"),
        "graph_q2_cyclicity_defects": q2.get("q2_cyclicity_replay", {}).get("graph_386_q2_cyclicity_defects"),
        "graph_D_q2_derivation_defects": q2.get("D_q2_replay", {}).get("graph_D_q2_derivation_defects"),
        "graph_arity_three_defects": q3.get("arity_three_replay", {}).get("graph_386_arity_three_defects"),
        "graph_q3_cyclicity_defects_mod_d": q3.get("q3_cyclicity_replay", {}).get("graph_386_q3_cyclicity_defects_mod_d"),
        "graph_D_q3_derivation_defects": q3.get("D_q3_replay", {}).get("graph_D_q3_derivation_defects"),
    }
    if value.get("exact_replay") != expected_replay or any(
        defect for key, defect in expected_replay.items() if key.endswith("defects")
    ):
        errors.append("exact replay projection")

    local = value.get("local_transfer_premise", {})
    if (
        any(local.get(key) is not True for key in (
            "i_end_graph_support_local", "p_end_graph_support_local", "H_alg_graph_support_local",
            "represented_green_names_bound", "endpoint_green_homotopy_identity_receiver_replayed",
        ))
        or local.get("maximum_q1_differential_order") != 4
        or local.get("SDR_maps_use_Green_operator") is not False
        or local.get("SDR_maps_add_choice_operation") is not False
        or local.get("nonlinear_green_compatibility_certified") is not False
    ):
        errors.append("local transfer premise/boundary")
    gate_disposition = value.get("gate_disposition", {})
    if gate_disposition != {
        "M3L_COMMON_ENDPOINT_SDR_BINDING": "COMPLETE",
        "M3R_TYPED_RESIDUAL_COMPARISON": "OPEN",
        "M4_FULL_CYCLIC_PAIRING": "OPEN",
        "M1_COMMON_STRICT_SNAPSHOT": "OPEN",
        "top_level_gate_a_hashes_accepted_by_this_result": 0,
        "classical_import_gate_a_status": "FAIL_CLOSED",
    }:
        errors.append("Gate disposition")

    flags = value.get("claim_flags", {})
    for key in (
        "STRICT_386_COMMON_ENDPOINT_SDR_MANIFEST_BOUND",
        "STRICT_386_COMMON_ENDPOINT_SDR_IDENTITIES_REPLAYED",
        "STRICT_386_Q1_D_Q2_Q3_SAME_LOCAL_CARRIER",
        "STRICT_386_GRAPH_ENDPOINT_SDR_SUPPORT_LOCAL",
        "M3L_COMMON_ENDPOINT_SDR_BOUND",
    ):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    for key in (
        "M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED", "FULL_RESIDUAL_CYCLIC_PAIRING_CERTIFIED",
        "NEW_GATE_A_TOP_LEVEL_HASH_ACCEPTED", "CLASSICAL_IMPORT_GATE_PASSED",
        "LORENTZIAN_Q2_Q3_GREEN_COMPATIBILITY_CERTIFIED", "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED",
        "QME_RESTORED", "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ):
        if flags.get(key) is not False:
            errors.append("claim promotion " + key)
    if len(value.get("does_not_establish", [])) < 7 or not value.get("next_gate"):
        errors.append("boundary ledger")

    projection = (
        "scope", "common_manifest", "compatibility_checks", "exact_replay",
        "local_transfer_premise", "foundational_strength", "gate_disposition",
        "claim_flags", "does_not_establish", "next_gate",
    )
    try:
        expected_digest = digest({key: value[key] for key in projection})
    except KeyError as error:
        errors.append("canonical projection missing " + str(error))
    else:
        if value.get("independent_checker", {}).get("expected_digest") != expected_digest:
            errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_COMMON_ENDPOINT_SDR_BINDING: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
