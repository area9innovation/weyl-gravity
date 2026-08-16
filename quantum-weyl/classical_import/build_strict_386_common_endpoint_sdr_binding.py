#!/usr/bin/env python3
"""Bind the exact graph endpoint SDR to the common strict nonlinear carrier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
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
RESULT = HERE / "certificates/STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1.json"
REPORT = HERE / "REPORT_STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def provenance_hash(value: dict[str, Any], result_id: str) -> str:
    for item in value.get("provenance", {}).get("inputs", []):
        if item.get("result_id", item.get("result_or_schema_id")) == result_id:
            return item["sha256"]
    raise ValueError(f"{value.get('result_id')} lacks provenance pin for {result_id}")


def dependency(path: Path, value: dict[str, Any], role: str) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)),
        "result_or_artifact_id": value["result_id"],
        "sha256": sha(path),
        "role": role,
    }


def build() -> dict[str, Any]:
    graph, unary, d_action, q2, q3, pairing, split_q1, shear, type_audit, gate = (
        load(path)
        for path in (GRAPH, UNARY, D_ACTION, Q2, Q3, PAIRING, SPLIT_Q1, SHEAR, TYPE_AUDIT, GATE)
    )
    expected = {
        graph.get("result_id"): "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1",
        unary.get("result_id"): "STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1",
        d_action.get("result_id"): "STRICT_386_FULL_D_ACTION_V1",
        q2.get("result_id"): "STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1",
        q3.get("result_id"): "STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1",
        pairing.get("result_id"): "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1",
        split_q1.get("result_id"): "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1",
        shear.get("result_id"): "STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1",
        type_audit.get("result_id"): "STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1",
        gate.get("result_id"): "CLASSICAL_IMPORT_GATE_V18_RECONCILIATION",
    }
    if any(actual != wanted for actual, wanted in expected.items()):
        raise ValueError("endpoint binding dependency identity drift")
    if gate["claim_flags"]["M3L_COMMON_ENDPOINT_SDR_BOUND"] is not False:
        raise ValueError("Gate V18 does not expose M3L as open")
    if type_audit["claim_flags"]["STRICT_386_GRAPH_ENDPOINT_SDR_SUPPORT_LOCAL"] is not True:
        raise ValueError("support-local graph endpoint SDR unavailable")

    graph_file_hash = sha(GRAPH)
    pairing_file_hash = sha(PAIRING)
    split_q1_file_hash = sha(SPLIT_Q1)
    shear_file_hash = sha(SHEAR)
    d_file_hash = sha(D_ACTION)
    q2_file_hash = sha(Q2)
    graph_snapshot = graph["graph_snapshot"]
    maps = graph["graph_sdr_component_maps"]

    compatibility_checks = {
        "unary_pins_graph_certificate": unary["common_snapshot"]["graph_dependency_sha256"] == graph_file_hash,
        "D_pins_graph_certificate": provenance_hash(d_action, graph["result_id"]) == graph_file_hash,
        "q2_pins_graph_certificate": provenance_hash(q2, graph["result_id"]) == graph_file_hash,
        "q2_and_q3_pin_same_split_q1": provenance_hash(q2, split_q1["result_id"]) == provenance_hash(q3, split_q1["result_id"]) == split_q1_file_hash,
        "graph_and_q2_pin_same_split_q1": provenance_hash(graph, split_q1["result_id"]) == split_q1_file_hash,
        "graph_q2_q3_pin_same_pairing": provenance_hash(graph, pairing["result_id"]) == provenance_hash(q2, pairing["result_id"]) == provenance_hash(q3, pairing["result_id"]) == pairing_file_hash,
        "graph_q2_q3_pin_same_shear": provenance_hash(graph, shear["result_id"]) == provenance_hash(q2, shear["result_id"]) == provenance_hash(q3, shear["result_id"]) == shear_file_hash,
        "q2_and_q3_pin_same_D": provenance_hash(q2, d_action["result_id"]) == provenance_hash(q3, d_action["result_id"]) == d_file_hash,
        "q3_pins_accepted_q2_certificate": provenance_hash(q3, q2["result_id"]) == q2_file_hash,
        "q3_pins_accepted_q2_object": q3["source_q3_snapshot"]["accepted_q2_snapshot_sha256"] == q2["source_q2_snapshot"]["sha256"],
        "graph_and_D_basis_hash_agree": graph_snapshot["basis_sha256"] == d_action["extended_common_snapshot"]["basis_sha256"] == pairing["canonical_hashes"]["component_basis_sha256"],
        "graph_and_D_pairing_hash_agree": graph_snapshot["pairing_sha256"] == d_action["extended_common_snapshot"]["pairing_sha256"] == pairing["canonical_hashes"]["pairing_serialization_sha256"],
        "graph_and_D_q1_hash_agree": graph_snapshot["graph_q1_sha256"] == d_action["extended_common_snapshot"]["graph_q1_sha256"],
        "q2_graph_DAG_exact": q2["graph_transport"]["exact_compositional_DAG_exported"] is True,
        "q3_graph_DAG_exact": q3["graph_transport"]["exact_compositional_DAG_exported"] is True,
    }
    if not all(compatibility_checks.values()):
        failed = [name for name, passed in compatibility_checks.items() if not passed]
        raise ValueError("common carrier compatibility failed: " + ", ".join(failed))

    object_hashes = {
        "component_basis_sha256": graph_snapshot["basis_sha256"],
        "odd_pairing_sha256": graph_snapshot["pairing_sha256"],
        "split_q1_snapshot_sha256": graph_snapshot["split_unary_snapshot_sha256"],
        "canonical_shear_snapshot_sha256": graph_snapshot["canonical_shear_snapshot_sha256"],
        "graph_q1_sha256": graph_snapshot["graph_q1_sha256"],
        "H_alg_graph_sha256": maps["H_alg_graph"]["sha256"],
        "i_end_graph_sha256": maps["i_end_graph"]["sha256"],
        "p_end_graph_sha256": maps["p_end_graph"]["sha256"],
        "P_end_graph_sha256": maps["P_end_graph"]["sha256"],
        "P_alg_graph_sha256": maps["P_alg_graph"]["sha256"],
        "R_graph_sha256": maps["R_graph"]["sha256"],
        "represented_green_common_snapshot_sha256": unary["common_snapshot"]["sha256"],
        "D_action_sha256": d_action["D_action"]["sha256"],
        "q2_source_snapshot_sha256": q2["source_q2_snapshot"]["sha256"],
        "q2_graph_transport_sha256": q2["canonical_hashes"]["graph_transport_sha256"],
        "q3_source_snapshot_sha256": q3["source_q3_snapshot"]["sha256"],
        "q3_graph_transport_sha256": q3["canonical_hashes"]["graph_transport_sha256"],
    }
    artifact_pins = [
        dependency(GRAPH, graph, "exact graph q1, endpoint SDR and transported suspension bytes"),
        dependency(UNARY, unary, "receiver-accepted represented unary-causal snapshot"),
        dependency(D_ACTION, d_action, "exact local cylinder-flow action on the graph carrier"),
        dependency(Q2, q2, "accepted source q2 and exact graph transport DAG"),
        dependency(Q3, q3, "accepted source q3 and exact graph transport DAG"),
        dependency(PAIRING, pairing, "fixed 386-row basis and odd pairing"),
        dependency(SPLIT_Q1, split_q1, "fixed split-coordinate unary table"),
        dependency(SHEAR, shear, "fixed BV-canonical split-to-graph transport"),
        dependency(TYPE_AUDIT, type_audit, "M3L/M3R type and locality decision"),
        dependency(GATE, gate, "open M3L Gate-A predecessor"),
    ]
    manifest_body = {
        "manifest_id": "STRICT_386_LOCAL_ENDPOINT_NONLINEAR_COMMON_MANIFEST_V1",
        "coordinate_presentation": "UNSHIFTED_CURVATURE_GRAPH_WITH_EXACT_SPLIT_SOURCE_DAGS",
        "carrier_rows": 386,
        "endpoint_rows": 30,
        "contracted_rows": 356,
        "artifact_pins": artifact_pins,
        "object_hashes": object_hashes,
    }
    common_manifest = {**manifest_body, "sha256": digest(manifest_body)}

    graph_replay = graph["exact_replay"]
    exact_replay = {
        "compatibility_links_checked": len(compatibility_checks),
        "compatibility_defects": sum(not passed for passed in compatibility_checks.values()),
        "qH_plus_Hq_defects": graph_replay["qH_plus_Hq_defects"],
        "p_i_identity_defects": graph_replay["p_graph_i_graph_identity_defects"],
        "i_p_projector_defects": graph_replay["i_graph_p_graph_equals_P_end_defects"],
        "normalized_side_condition_defects": sum(graph_replay[key] for key in (
            "H_squared_defects", "H_i_graph_defects", "p_graph_H_defects",
            "P_end_squared_defects", "P_alg_squared_defects", "P_end_P_alg_defects", "P_alg_P_end_defects",
        )),
        "endpoint_SDR_cyclicity_defects": graph_replay["H_alg_graph_cyclicity_defects"],
        "transported_suspension_PBW_reduced_cyclicity_defects": graph_replay["transported_R_PBW_reduced_cyclicity_defects"],
        "D_q1_commutator_defects": d_action["exact_replay"]["D_q1_commutator_defects"],
        "graph_q1_q2_defects": q2["q1_q2_replay"]["graph_386_q1_q2_defects"],
        "graph_q2_cyclicity_defects": q2["q2_cyclicity_replay"]["graph_386_q2_cyclicity_defects"],
        "graph_D_q2_derivation_defects": q2["D_q2_replay"]["graph_D_q2_derivation_defects"],
        "graph_arity_three_defects": q3["arity_three_replay"]["graph_386_arity_three_defects"],
        "graph_q3_cyclicity_defects_mod_d": q3["q3_cyclicity_replay"]["graph_386_q3_cyclicity_defects_mod_d"],
        "graph_D_q3_derivation_defects": q3["D_q3_replay"]["graph_D_q3_derivation_defects"],
    }
    if any(value for key, value in exact_replay.items() if key.endswith("defects")):
        raise ValueError("endpoint binding identity defect")

    result: dict[str, Any] = {
        "$schema": "../schema/strict-386-common-endpoint-sdr-binding-v1.schema.json",
        "schema": "strict-386-common-endpoint-sdr-binding-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-386-common-endpoint-sdr-binding-v1.schema.json",
        "result_id": "STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1",
        "result_kind": "CLASSICAL_IMPORT_COMMON_LOCAL_ENDPOINT_SDR_BINDING",
        "result_state": "M3L_COMMON_ENDPOINT_SDR_BOUND_M3R_AND_GATE_A_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-16",
        "repository_base_commit": "669895e3a9f75681f36de94f73a9b3b6039af8d7",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Do the exact graph endpoint SDR, q1, D, source q2/q3, transported suspension and represented Green names inhabit one content-addressed strict 386-row local carrier?",
        "answer": "Yes, in the declared local endpoint scope. A receiver manifest pins the same 386-row basis, odd pairing, split q1, canonical shear, graph q1, H_alg_graph, i_end_graph, p_end_graph, complementary projectors, transported suspension, represented Green names, D action and exact compositional graph q2/q3 DAGs. Fifteen independent provenance and internal-hash comparisons agree, and every previously receiver-replayed endpoint contraction, q1/q2/q3, cyclicity and stationary-D defect is zero on those pinned artifacts. This closes M3L only. It does not identify the endpoint with W+/W- residual coefficients, construct M3R, close residual cyclicity, accept a new Gate-A top-level hash, or reach Hadamard/QME stages.",
        "scope": {
            "theory": "strict pure-Weyl classical BV complex",
            "background": "unit conformal cylinder",
            "carrier": "386 local graph component species",
            "endpoint": "30 local field-component species",
            "coordinate_presentation": "unshifted curvature graph with exact split-source q2/q3 transport DAGs",
            "locality": "finite-order support-local SDR maps; represented Green names are separately analytic",
        },
        "common_manifest": common_manifest,
        "compatibility_checks": compatibility_checks,
        "exact_replay": exact_replay,
        "local_transfer_premise": {
            "i_end_graph_support_local": True,
            "p_end_graph_support_local": True,
            "H_alg_graph_support_local": True,
            "maximum_q1_differential_order": graph["support_and_foundations"]["maximum_differential_order"],
            "SDR_maps_use_Green_operator": False,
            "SDR_maps_add_choice_operation": False,
            "represented_green_names_bound": True,
            "endpoint_green_homotopy_identity_receiver_replayed": unary["receiver_replay"]["full_graph_homotopy_identity"],
            "nonlinear_green_compatibility_certified": False,
        },
        "foundational_strength": {
            "manifest_and_component_replay": "finite exact rational and hash computation formalizable in PRA for fixed serialized artifacts",
            "choice_dependency_added": "none",
            "analytic_dependency": "the represented Green-action names retain their smooth support-indexed LF and spectral completeness assumptions",
            "residual_dependency": "no harmonic or zero-mode projection enters M3L",
        },
        "gate_disposition": {
            "M3L_COMMON_ENDPOINT_SDR_BINDING": "COMPLETE",
            "M3R_TYPED_RESIDUAL_COMPARISON": "OPEN",
            "M4_FULL_CYCLIC_PAIRING": "OPEN",
            "M1_COMMON_STRICT_SNAPSHOT": "OPEN",
            "top_level_gate_a_hashes_accepted_by_this_result": 0,
            "classical_import_gate_a_status": "FAIL_CLOSED",
        },
        "provenance": {"inputs": artifact_pins},
        "claim_flags": {
            "STRICT_386_COMMON_ENDPOINT_SDR_MANIFEST_BOUND": True,
            "STRICT_386_COMMON_ENDPOINT_SDR_IDENTITIES_REPLAYED": True,
            "STRICT_386_Q1_D_Q2_Q3_SAME_LOCAL_CARRIER": True,
            "STRICT_386_GRAPH_ENDPOINT_SDR_SUPPORT_LOCAL": True,
            "M3L_COMMON_ENDPOINT_SDR_BOUND": True,
            "M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED": False,
            "FULL_RESIDUAL_CYCLIC_PAIRING_CERTIFIED": False,
            "NEW_GATE_A_TOP_LEVEL_HASH_ACCEPTED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "LORENTZIAN_Q2_Q3_GREEN_COMPATIBILITY_CERTIFIED": False,
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
        },
        "does_not_establish": [
            "an identification of the local endpoint with the 470-coordinate W+/W- residual carrier or the 15+15 symmetry-cotangent carrier",
            "a typed harmonic restriction or endpoint-to-residual spectral comparison",
            "support-locality of any nonzero global harmonic or zero-mode projector",
            "full residual cyclic pairing or cyclicity of M3R",
            "flattened graph-coordinate q2 or q3 tensors beyond the exact compositional transport DAGs",
            "nonlinear q2/q3 compatibility with the represented Green homotopies",
            "a new accepted Gate-A top-level hash, a passed classical import gate, Hadamard state, renormalized products, QME restoration or residual transfer",
        ],
        "next_gate": "Construct M3R as a typed endpoint-to-W+/W- harmonic comparison with explicit test/distribution domains and zero-mode policy. In parallel separate the already serialized full graph pairing from the still-open residual-comparison cyclicity, then freeze only after those typed obligations close.",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1.md",
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_386_common_endpoint_sdr_binding.py",
            "checks": [
                "all ten input content hashes and identities",
                "shared graph, q1, pairing, shear, D and q2 provenance pins",
                "basis/pairing/q1 internal hash agreement",
                "all fifteen cross-certificate compatibility links",
                "endpoint SDR and nonlinear exact defect projections",
                "manifest digest and every Gate/Hadamard/QME firewall",
            ],
            "expected_digest": "",
        },
    }
    projection = (
        "scope", "common_manifest", "compatibility_checks", "exact_replay",
        "local_transfer_premise", "foundational_strength", "gate_disposition",
        "claim_flags", "does_not_establish", "next_gate",
    )
    result["independent_checker"]["expected_digest"] = digest({key: result[key] for key in projection})
    return result


def report(value: dict[str, Any]) -> str:
    manifest = value["common_manifest"]
    replay = value["exact_replay"]
    return f"""# Strict 386-row common endpoint-SDR binding

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`
**Gate A:** `FAIL_CLOSED`

## Result

M3L is complete.  One content-addressed receiver manifest now binds the exact
386-row graph basis, pairing, q1, local endpoint inclusion, projection and
homotopy, complementary projectors, transported suspension, represented Green
names, cylinder-flow D action, and the exact graph-transport DAGs for source q2
and q3.

The manifest contains {len(manifest['object_hashes'])} canonical object hashes
and {len(manifest['artifact_pins'])} artifact pins.  All
{replay['compatibility_links_checked']} independent cross-certificate links
agree.  The endpoint contraction, normalized side conditions, endpoint SDR
cyclicity, q1/q2, q2 cyclicity, D/q2, arity three, q3 cyclicity and D/q3 defect
counts are zero on the pinned artifacts.

## What changed

No new homotopy was invented.  The result proves that the already exact local
graph SDR and the later q2/q3/D layers use the same basis, odd pairing, split
q1, canonical shear and graph q1 bytes.  This is the common binding requested
by `M3L_COMMON_ENDPOINT_SDR_BINDING`.

## Boundary

M3R remains open.  This manifest contains no harmonic restriction, W+/W-
projection or zero-mode projection, and it does not identify thirty endpoint
field species with any global coefficient carrier.  Full residual cyclicity,
nonlinear Green compatibility, Gate A, Hadamard, renormalized products, QME and
residual quantum transfer remain open.  No new Gate-A top-level hash is
accepted by this scoped binding.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_common_endpoint_sdr_binding.py --check
python3 quantum-weyl/classical_import/check_strict_386_common_endpoint_sdr_binding.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_common_endpoint_sdr_binding.py
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), report(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("STRICT_386_COMMON_ENDPOINT_SDR_BINDING: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_386_COMMON_ENDPOINT_SDR_BINDING: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
