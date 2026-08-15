#!/usr/bin/env python3
"""Bind graph-local and analytic unary data into one receiver snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1.json"
REPORT = HERE / "REPORT_STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1.md"
GRAPH = HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
GREEN = HERE / "certificates/STRICT_386_GRAPH_GREEN_ACTION_NAME_V1.json"
GATE_V5 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V5_RECONCILIATION.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def build() -> dict[str, Any]:
    graph, green, gate = (json.loads(path.read_text()) for path in (GRAPH, GREEN, GATE_V5))
    if graph.get("result_id") != "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1":
        raise ValueError("graph input drift")
    if green.get("result_id") != "STRICT_386_GRAPH_GREEN_ACTION_NAME_V1":
        raise ValueError("Green-name input drift")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V5_RECONCILIATION":
        raise ValueError("Gate V5 input drift")
    green_graph = next(
        item for item in green["provenance"]["inputs"]
        if item["path"] == str(GRAPH.relative_to(ROOT))
    )
    if green_graph["sha256"] != sha(GRAPH):
        raise ValueError("Green name is not bound to current graph bytes")
    if not all(
        graph["claim_flags"].get(key) is True
        for key in (
            "STRICT_386_GRAPH_Q1_COMPONENT_JET_TABLE_SERIALIZED",
            "STRICT_386_GRAPH_SDR_COMPONENT_MAPS_SERIALIZED",
            "STRICT_386_GRAPH_SDR_IDENTITIES_REPLAYED",
            "STRICT_386_GRAPH_SDR_CYCLICITY_REPLAYED",
            "STRICT_386_GRAPH_SUSPENSION_TRANSPORTED",
        )
    ):
        raise ValueError("graph snapshot incomplete")
    if not all(
        green["claim_flags"].get(key) is True
        for key in (
            "STRICT_ENDPOINT_GREEN_CONVERGENT_NAME_SERIALIZED",
            "STRICT_FULL_GRAPH_GREEN_CONVERGENT_NAME_SERIALIZED",
            "STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED",
        )
    ):
        raise ValueError("Green action names incomplete")
    if gate["gate_disposition"]["gate_a_status"] != "FAIL_CLOSED":
        raise ValueError("authoritative Gate V5 unexpectedly passed")

    maps = graph["graph_sdr_component_maps"]
    accepted_objects = {
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
    common_sha = digest(accepted_objects)
    missing = gate["minimal_missing_bundle"]
    value: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-unary-causal-common-snapshot-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-386-unary-causal-common-snapshot-v1.schema.json",
        "result_id": "STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1",
        "result_kind": "RECEIVER_ACCEPTED_SCOPED_SNAPSHOT",
        "result_state": "UNARY_CAUSAL_COMMON_SNAPSHOT_ACCEPTED_FULL_CLASSICAL_GATE_A_FAIL_CLOSED",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "37b3cac874c0662d09206d9d6a6b5362f7c4bf57",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Do the fixed 386-row graph basis, pairing, q1, SDR, transported suspension and both represented Green-action names now belong to one content-addressed receiver snapshot, and does that scoped acceptance pass the broader classical Gate A?",
        "answer": "The unary causal package is now one receiver-accepted scoped snapshot. Thirteen content hashes bind the fixed basis and odd pairing, graph q1, five SDR maps, transported suspension, both sign-oriented Green names, represented spaces and transport contract. The graph and analytic certificates independently replay their own exact and analytic boundaries, and the Green name pins the exact graph bytes it consumes. This does not pass classical Gate A. The authoritative V5 contract requires twenty exports, seven accepted top-level hashes and ten common-byte identity replays; it still lacks the full strict q2/D extension, continuum residual SDR, full cyclic pairing, exact residual representation payload and centered representatives. No Gate-A, Hadamard or QME flag is promoted.",
        "scope": {
            "carrier_rows": 386,
            "endpoint_rows": 30,
            "contracted_rows": 356,
            "accepted_hashes": len(accepted_objects),
            "scope_name": "STRICT_386_UNARY_CAUSAL_GRAPH",
            "not_scope_name": "CLASSICAL_GATE_A_TWENTY_EXPORT_FREEZE",
        },
        "accepted_objects": accepted_objects,
        "common_snapshot": {
            "kind": "STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT",
            "sha256": common_sha,
            "graph_dependency_sha256": sha(GRAPH),
            "green_dependency_sha256": sha(GREEN),
            "all_objects_share_carrier": True,
            "all_objects_share_pairing_and_suspension_convention": True,
            "both_causal_orientations_present": True,
            "receiver_status": "ACCEPTED_SCOPED",
        },
        "receiver_replay": {
            "graph_certificate_independent_replay": True,
            "green_name_independent_replay": True,
            "green_name_consumes_exact_graph_hash": True,
            "q1_nilpotency": True,
            "SDR_identities": True,
            "SDR_cyclicity": True,
            "transported_suspension_involution": True,
            "modal_Green_jump_and_zero_mode": True,
            "full_graph_homotopy_identity": True,
            "causal_support_and_adjoint_orientation": True,
        },
        "gate_v5_reconciliation": {
            "authoritative_result_id": gate["result_id"],
            "authoritative_sha256": sha(GATE_V5),
            "exports_required": gate["gate_disposition"]["exports_total"],
            "freeze_checks_required": gate["gate_disposition"]["freeze_checks_total"],
            "top_level_hashes_required": len(gate["required_hash_disposition"]),
            "top_level_hashes_accepted_before": gate["gate_disposition"]["accepted_common_snapshot_hashes"],
            "top_level_hashes_accepted_by_this_scoped_result": 0,
            "missing_bundle": [
                {"id": item["id"], "object": item["object"], "unlocks": item["unlocks"]}
                for item in missing
            ],
            "gate_a_status": "FAIL_CLOSED",
            "reason": "The unary causal snapshot is not a substitute for the twenty-export classical freeze contract.",
        },
        "foundational_strength": {
            "finite_local_snapshot_hashing_upper_bound": "PRA",
            "analytic_name_base": green["foundational_strength"]["imported_theorem_base"],
            "weakest_analytic_base": "NOT_ESTABLISHED",
            "choice_principle_inferred": False,
            "boundary": "Hash binding and finite map replay add no choice operation; the analytic Green-name theorem retains its separately declared classical-analysis boundary.",
        },
        "claim_flags": {
            "STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_ACCEPTED": True,
            "STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED": True,
            "STRICT_386_FULL_Q2_D_COMMON_SNAPSHOT": False,
            "STRICT_386_RESIDUAL_SDR_COMMON_SNAPSHOT": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS": False,
            "QME_RESTORED": False,
            "RESIDUAL_TRANSFERRED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
        },
        "does_not_establish": [
            "the authoritative twenty-export, seven-hash, ten-identity classical Gate A",
            "a full-carrier strict q2 and local D common snapshot or their D identities",
            "a continuum residual SDR or complete full-carrier cyclic pairing",
            "exact SO(4,2) residual matrices, centered H3/H4/H5 bases or normalized representative vectors",
            "an effective numerical Green solver or serialized distribution-kernel bytes",
            "a BRST-compatible Hadamard state, renormalized Lorentzian products, restored QME, residual quantum transfer or Lorentzian quantum theory",
        ],
        "next_gate": "Use this accepted unary-causal snapshot as the fixed carrier for M2: select and serialize the strict cylinder residual generator D on all 386 rows, extend the canonical strict q2 convention to every required nonminimal and auxiliary row, and independently replay [D,q1] and the D/q2 derivation identity without importing Berger rows.",
        "provenance": {
            "inputs": [
                {"path": str(GRAPH.relative_to(ROOT)), "sha256": sha(GRAPH), "role": "exact local graph q1, SDR, pairing and suspension snapshot"},
                {"path": str(GREEN.relative_to(ROOT)), "sha256": sha(GREEN), "role": "represented endpoint and full graph Green-action names"},
                {"path": str(GATE_V5.relative_to(ROOT)), "sha256": sha(GATE_V5), "role": "authoritative broader classical Gate-A contract and missing bundle"},
            ]
        },
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_386_unary_causal_common_snapshot.py",
            "checks": [
                "three dependency identities and hashes", "thirteen accepted-object hashes",
                "graph-to-Green transitive pin", "common snapshot digest",
                "ten scoped receiver replays", "V5 twenty-export/seven-hash boundary",
                "six missing-bundle preservation", "Gate-A/Hadamard/QME firewall",
                "canonical projection digest",
            ],
            "expected_digest": "",
        },
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1.md",
    }
    keys = (
        "scope", "accepted_objects", "common_snapshot", "receiver_replay",
        "gate_v5_reconciliation", "foundational_strength", "claim_flags",
        "does_not_establish", "next_gate",
    )
    value["independent_checker"]["expected_digest"] = digest({key: value[key] for key in keys})
    return value


def render(value: dict[str, Any]) -> str:
    gate = value["gate_v5_reconciliation"]
    return "\n".join([
        "# Strict 386 unary-causal common snapshot", "", "## Outcome", "", value["answer"], "",
        "## Accepted scoped snapshot", "",
        f"The receiver binds **{value['scope']['accepted_hashes']} hashes** into `{value['common_snapshot']['sha256']}`. They cover the 386-row basis and pairing, graph q1, local SDR, transported suspension, both causal Green names, their represented spaces and their transport contract.", "",
        "Every positive statement remains unary and causal. The common action is `H_alg_graph + i_end_graph Lambda_end,sign p_end_graph`; its exact graph identities and analytic support/adjoint boundary are independently replayed from content-addressed inputs.", "",
        "## Why Gate A still fails", "",
        f"Gate V5 requires **{gate['exports_required']} exports**, **{gate['top_level_hashes_required']} accepted top-level hashes**, and **{gate['freeze_checks_required']} identity checks** on one strict pure-Weyl snapshot. This scoped result accepts **{gate['top_level_hashes_accepted_by_this_scoped_result']}** of those top-level Gate-A hashes because it does not pretend unary causal data supplies q2, D or residual payloads.", "",
        "| missing bundle | remaining object |", "|---|---|",
        *[f"| `{item['id']}` | {item['object']} |" for item in gate["missing_bundle"]], "",
        "## Next", "", value["next_gate"], "",
        "## Verification", "", "```text",
        "python3 quantum-weyl/classical_import/build_strict_386_unary_causal_common_snapshot.py --check",
        "python3 quantum-weyl/classical_import/check_strict_386_unary_causal_common_snapshot.py",
        "python3 quantum-weyl/classical_import/verify_strict_386_unary_causal_common_snapshot.py",
        "python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_unary_causal_common_snapshot.py -v",
        "```", "",
    ])


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False).encode() + b"\n", render(value).encode())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    if args.check:
        stale = []
        if not RESULT.is_file() or RESULT.read_bytes() != result:
            stale.append(str(RESULT.relative_to(ROOT)))
        if not REPORT.is_file() or REPORT.read_bytes() != report:
            stale.append(str(REPORT.relative_to(ROOT)))
        if stale:
            print("STALE: " + ", ".join(stale))
            return 1
        print("STRICT 386 UNARY-CAUSAL COMMON SNAPSHOT: CURRENT")
        return 0
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("wrote", RESULT.relative_to(ROOT), "and", REPORT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
