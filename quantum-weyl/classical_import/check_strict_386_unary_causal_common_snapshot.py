#!/usr/bin/env python3
"""Independent checker for the scoped strict unary-causal snapshot."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1.json"
GRAPH = HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
GREEN = HERE / "certificates/STRICT_386_GRAPH_GREEN_ACTION_NAME_V1.json"
GATE = HERE / "certificates/CLASSICAL_IMPORT_GATE_V5_RECONCILIATION.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text()) if value is None else value
    graph, green, gate = (json.loads(path.read_text()) for path in (GRAPH, GREEN, GATE))
    errors: list[str] = []
    if value.get("result_id") != "STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("identity/lifecycle")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency tags")
    scope = value.get("scope", {})
    if scope.get("carrier_rows") != 386 or scope.get("endpoint_rows") != 30 or scope.get("contracted_rows") != 356 or scope.get("accepted_hashes") != 13:
        errors.append("scope")

    maps = graph["graph_sdr_component_maps"]
    expected = {
        "component_basis_sha256": graph["graph_snapshot"]["basis_sha256"],
        "odd_pairing_sha256": graph["graph_snapshot"]["pairing_sha256"],
        "graph_q1_sha256": graph["graph_snapshot"]["graph_q1_sha256"],
        "H_alg_graph_sha256": maps["H_alg_graph"]["sha256"],
        "i_end_graph_sha256": maps["i_end_graph"]["sha256"],
        "p_end_graph_sha256": maps["p_end_graph"]["sha256"],
        "P_end_graph_sha256": maps["P_end_graph"]["sha256"],
        "P_alg_graph_sha256": maps["P_alg_graph"]["sha256"],
        "R_graph_sha256": maps["R_graph"]["sha256"],
        "plus_green_name_sha256": green["canonical_hashes"]["plus_action_name_sha256"],
        "minus_green_name_sha256": green["canonical_hashes"]["minus_action_name_sha256"],
        "represented_spaces_sha256": green["canonical_hashes"]["represented_spaces_sha256"],
        "transport_contract_sha256": green["canonical_hashes"]["transport_contract_sha256"],
    }
    if value.get("accepted_objects") != expected:
        errors.append("accepted-object projection")
    common = value.get("common_snapshot", {})
    if common.get("sha256") != digest(expected) or common.get("graph_dependency_sha256") != sha(GRAPH) or common.get("green_dependency_sha256") != sha(GREEN):
        errors.append("common snapshot hash")
    if common.get("receiver_status") != "ACCEPTED_SCOPED" or not all(common.get(key) is True for key in ("all_objects_share_carrier", "all_objects_share_pairing_and_suspension_convention", "both_causal_orientations_present")):
        errors.append("common snapshot disposition")

    green_graph = next((item for item in green["provenance"]["inputs"] if item.get("path") == str(GRAPH.relative_to(ROOT))), None)
    if green_graph is None or green_graph.get("sha256") != sha(GRAPH):
        errors.append("graph-to-Green transitive pin")
    replay = value.get("receiver_replay", {})
    if len(replay) != 10 or not all(item is True for item in replay.values()):
        errors.append("receiver replay")

    reconciled = value.get("gate_v5_reconciliation", {})
    if reconciled.get("authoritative_sha256") != sha(GATE) or reconciled.get("exports_required") != 20 or reconciled.get("freeze_checks_required") != 10 or reconciled.get("top_level_hashes_required") != 7:
        errors.append("Gate V5 projection")
    if reconciled.get("top_level_hashes_accepted_before") != 0 or reconciled.get("top_level_hashes_accepted_by_this_scoped_result") != 0 or reconciled.get("gate_a_status") != "FAIL_CLOSED":
        errors.append("Gate V5 promotion")
    expected_missing = [item["id"] for item in gate["minimal_missing_bundle"]]
    if [item.get("id") for item in reconciled.get("missing_bundle", [])] != expected_missing or expected_missing != ["M1_COMMON_STRICT_SNAPSHOT", "M2_STRICT_Q2_D", "M3_RESIDUAL_SDR", "M4_FULL_CYCLIC_PAIRING", "M5_RESIDUAL_EXACT_PAYLOAD", "M6_CENTERED_REPRESENTATIVES"]:
        errors.append("missing bundle")

    flags = value.get("claim_flags", {})
    for key in ("STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_ACCEPTED", "STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("STRICT_386_FULL_Q2_D_COMMON_SNAPSHOT", "STRICT_386_RESIDUAL_SDR_COMMON_SNAPSHOT", "CLASSICAL_IMPORT_GATE_PASSED", "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A", "HADAMARD_STATE_CONSTRUCTED", "RENORMALIZED_LORENTZIAN_PRODUCTS", "QME_RESTORED", "RESIDUAL_TRANSFERRED", "LORENTZIAN_QUANTUM_THEORY"):
        if flags.get(key) is not False:
            errors.append("claim promotion " + key)

    provenance = value.get("provenance", {}).get("inputs", [])
    for item, path in zip(provenance, (GRAPH, GREEN, GATE)):
        if item.get("path") != str(path.relative_to(ROOT)) or item.get("sha256") != sha(path):
            errors.append("provenance " + str(path.relative_to(ROOT)))
    keys = (
        "scope", "accepted_objects", "common_snapshot", "receiver_replay",
        "gate_v5_reconciliation", "foundational_strength", "claim_flags",
        "does_not_establish", "next_gate",
    )
    if value.get("independent_checker", {}).get("expected_digest") != digest({key: value[key] for key in keys}):
        errors.append("canonical projection digest")
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    if not errors:
        print("  - thirteen unary-causal hashes accepted on one 386-row snapshot")
        print("  - Gate V5 remains fail closed with all six missing bundles preserved")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
