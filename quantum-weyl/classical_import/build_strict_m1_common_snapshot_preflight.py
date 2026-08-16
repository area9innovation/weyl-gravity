#!/usr/bin/env python3
"""Build the fail-closed M1 common-snapshot carrier and export preflight."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_M1_COMMON_SNAPSHOT_PREFLIGHT_V1.json"
REPORT = HERE / "REPORT_STRICT_M1_COMMON_SNAPSHOT_PREFLIGHT_V1.md"

INPUTS = {
    "bootstrap": HERE / "snapshots/bootstrap-v1.json",
    "gate_v25": HERE / "certificates/CLASSICAL_IMPORT_GATE_V25_RECONCILIATION.json",
    "component_pairing": HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json",
    "full_q1": HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json",
    "common_endpoint": HERE / "certificates/STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1.json",
    "source_q2": HERE / "certificates/STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.json",
    "source_q3": HERE / "certificates/STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1.json",
    "D_action": HERE / "certificates/STRICT_386_FULL_D_ACTION_V1.json",
    "dfinite": HERE / "certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json",
    "m3r": HERE / "certificates/STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.json",
    "m3rc_a": HERE / "certificates/STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1.json",
    "m3rc_b": HERE / "certificates/STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1.json",
    "m4r": HERE / "certificates/STRICT_TYPED_RESIDUAL_CYCLICITY_V1.json",
    "zero_modes": HERE / "certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json",
    "centered": HERE / "certificates/STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1.json",
}

EXPECTED_IDS = {
    "gate_v25": "CLASSICAL_IMPORT_GATE_V25_RECONCILIATION",
    "component_pairing": "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1",
    "full_q1": "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1",
    "common_endpoint": "STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1",
    "source_q2": "STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1",
    "source_q3": "STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1",
    "D_action": "STRICT_386_FULL_D_ACTION_V1",
    "dfinite": "STRICT_DFINITE_RESIDUAL_SDR_V1",
    "m3r": "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1",
    "m3rc_a": "STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1",
    "m3rc_b": "STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1",
    "m4r": "STRICT_TYPED_RESIDUAL_CYCLICITY_V1",
    "zero_modes": "STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1",
    "centered": "STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1",
}

LOCAL_ROW_REQUIRED_FIELDS = [
    "ghost_number",
    "antifield_number",
    "form_degree",
    "Grassmann_parity",
    "mass_dimension",
    "Weyl_weight",
    "compact_degree",
    "derivative_order_bound",
]

LEDGER_EXPORTS = {
    "field_ghost_antifield_dictionary",
    "field_gradings",
}
COMPOSITE_MAP_EXPORTS = {
    "classical_inclusion_iota_cl",
    "classical_projection_pi_cl",
    "classical_homotopy_s_cl",
}
COMPOSITE_PAIRING_EXPORTS = {"cyclic_pairing"}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def build() -> dict[str, Any]:
    source = {name: load(path) for name, path in INPUTS.items()}
    for name, result_id in EXPECTED_IDS.items():
        if source[name].get("result_id") != result_id:
            raise ValueError(f"authority drift: {name}")
    gate = source["gate_v25"]
    if (
        gate["gate_disposition"]["gate_a_status"] != "FAIL_CLOSED"
        or [item["id"] for item in gate["minimal_missing_bundle"]] != ["M1_COMMON_STRICT_SNAPSHOT"]
        or source["common_endpoint"]["claim_flags"]["M3L_COMMON_ENDPOINT_SDR_BOUND"] is not True
        or source["m3r"]["claim_flags"]["M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED"] is not True
        or source["m3rc_b"]["claim_flags"]["M3RC_B_REPRESENTED_ACTION_SUPPORT_DUAL_IDENTIFICATION_COMPLETE"] is not True
        or source["m4r"]["claim_flags"]["M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE"] is not True
    ):
        raise ValueError("M1 prerequisite firewall drift")

    local_rows = source["component_pairing"]["component_basis"]["rows"]
    present_fields = sorted({key for row in local_rows for key in row})
    missing_fields = [field for field in LOCAL_ROW_REQUIRED_FIELDS if field not in present_fields]
    export_inventory = []
    for item in gate["export_reconciliation"]:
        export_id = item["export_id"]
        if export_id in LEDGER_EXPORTS:
            status = "MISSING_FULL_TYPED_ROW_LEDGER"
            blocker = "M1A_FULL_TYPED_CARRIER_LEDGER"
        elif export_id in COMPOSITE_MAP_EXPORTS:
            status = "TYPED_STAGES_READY_COMPOSITE_MAP_MISSING"
            blocker = "M1B_REPRESENTED_COMPOSITE_CONTRACTION"
        elif export_id in COMPOSITE_PAIRING_EXPORTS:
            status = "LOCAL_AND_RESIDUAL_FORMS_READY_COMMON_COMPOSITE_MISSING"
            blocker = "M1B_REPRESENTED_COMPOSITE_CONTRACTION"
        else:
            status = "COMMON_OBJECT_READY_FOR_BINDING"
            blocker = None
        export_inventory.append({
            "export_id": export_id,
            "gate_v25_status": item["status"],
            "m1_preflight_status": status,
            "blocker": blocker,
            "evidence": item["evidence"],
            "boundary": item["boundary"],
        })

    hashes = gate["required_hash_disposition"]
    hash_inventory = [
        {
            "hash_id": "field_dictionary_hash",
            "status": "BLOCKED_M1A_FULL_TYPED_CARRIER_LEDGER",
            "candidate": hashes["field_dictionary_hash"]["candidate"],
            "candidate_scope": hashes["field_dictionary_hash"]["candidate_scope"],
        },
        {
            "hash_id": "differential_hash",
            "status": "LOCAL_OBJECT_READY_COMMON_HASH_BLOCKED_M1A",
            "candidate": source["common_endpoint"]["common_manifest"]["object_hashes"]["graph_q1_sha256"],
            "candidate_scope": "STRICT_386_GRAPH_Q1_READY_BUT_COMMON_TYPED_ROW_LEDGER_ABSENT",
        },
        *[
            {
                "hash_id": key,
                "status": "OBJECT_READY_AWAIT_M1C_COMMON_BINDING",
                "candidate": hashes[key]["candidate"],
                "candidate_scope": hashes[key]["candidate_scope"],
            }
            for key in ("q2_hash", "D_action_hash", "zero_mode_basis_hash", "representative_hash")
        ],
        {
            "hash_id": "pairing_hash",
            "status": "LOCAL_AND_RESIDUAL_OBJECTS_READY_COMPOSITE_HASH_BLOCKED_M1B",
            "candidate": digest({
                "local_pairing": source["component_pairing"]["canonical_hashes"]["pairing_serialization_sha256"],
                "represented_action_residual_pairing": source["m3rc_b"]["action_pairing_identification"]["dual_dictionary_sha256"],
                "represented_residual_rank": source["m4r"]["typed_carrier"]["action_pairing_rank"],
            }),
            "candidate_scope": "TYPED_PAIR_OF_LOCAL_AND_REPRESENTED_FORMS_NOT_A_COMMON_COMPOSITE_CONTRACTION",
        },
    ]
    hash_order = [
        "field_dictionary_hash", "differential_hash", "q2_hash", "D_action_hash",
        "zero_mode_basis_hash", "pairing_hash", "representative_hash",
    ]
    hash_inventory.sort(key=lambda row: hash_order.index(row["hash_id"]))

    carriers = [
        {
            "id": "LOCAL_GRAPH_BV_386",
            "category": "LOCAL_COMPONENT_JET",
            "dimension": 386,
            "authoritative_role": "actual strict local unary/nonlinear/causal BV carrier",
            "status": "AUTHORITATIVE_LOCAL_SOURCE",
        },
        {
            "id": "LOCAL_ENDPOINT_30",
            "category": "LOCAL_COMPONENT_JET",
            "dimension": 30,
            "authoritative_role": "support-local endpoint of the 386-row algebraic contraction",
            "status": "AUTHORITATIVE_LOCAL_ENDPOINT",
        },
        {
            "id": "REPRESENTED_ENDPOINT_DFINITE_4080",
            "category": "REDUCED_MODE_GLOBAL_HARMONIC",
            "dimension": source["m3r"]["comparison"]["source"]["total_dimension"],
            "authoritative_role": "energy-2-through-6 represented harmonic realization of the thirty endpoint species",
            "status": "AUTHORITATIVE_REPRESENTED_DOMAIN",
        },
        {
            "id": "DFINITE_COMPARISON_4490",
            "category": "REDUCED_MODE_GLOBAL_HARMONIC",
            "dimension": source["dfinite"]["global_direct_sum"]["full_dimension"],
            "authoritative_role": "finite harmonic SDR comparison including the test nonminimal doublet",
            "status": "SCOPED_COMPARISON_SOURCE",
        },
        {
            "id": "FORMAL_COTANGENT_COMPARISON_8980",
            "category": "FORMAL_SHIFTED_COTANGENT",
            "dimension": source["m3rc_a"]["formal_cotangent_completion"]["full_dimension"],
            "authoritative_role": "formal algebraic M3RC-A/M4R comparison source",
            "status": "NOT_AUTHORITATIVE_FULL_BV_SOURCE",
        },
        {
            "id": "ACTION_RESIDUAL_940",
            "category": "REDUCED_MODE_CAUSAL_COHOMOLOGY",
            "dimension": source["m4r"]["typed_carrier"]["total_residual_coordinates"],
            "authoritative_role": "represented primal plus compact-source action-dual residual target",
            "status": "AUTHORITATIVE_REPRESENTED_RESIDUAL_TARGET",
        },
        {
            "id": "ZERO_MODE_15_PLUS_15",
            "category": "RESIDUAL_ZERO_MODE",
            "dimension": 30,
            "authoritative_role": "separate conformal-Killing generator/cotangent payload at energies zero and one",
            "status": "AUTHORITATIVE_SCOPED_PAYLOAD",
        },
        {
            "id": "CENTERED_C3_C4_C5",
            "category": "RESIDUAL_COCHAIN",
            "dimension": 727 + 3084 + 8532,
            "authoritative_role": "centered cochain bases and normalized H4 representatives",
            "status": "AUTHORITATIVE_SCOPED_PAYLOAD",
        },
    ]

    edges = [
        {"id": "M3L_LOCAL_ENDPOINT_SDR", "source": "LOCAL_GRAPH_BV_386", "target": "LOCAL_ENDPOINT_30", "status": "EXACT_SUPPORT_LOCAL_COMPLETE"},
        {"id": "FINITE_HARMONIC_REALIZATION", "source": "LOCAL_ENDPOINT_30", "target": "REPRESENTED_ENDPOINT_DFINITE_4080", "status": "EXACT_GLOBAL_REPRESENTATION_FUNCTOR_NOT_POSITION_LOCAL"},
        {"id": "M3R_ANALYSIS_SYNTHESIS", "source": "REPRESENTED_ENDPOINT_DFINITE_4080", "target": "ACTION_RESIDUAL_940", "status": "PRIMAL_470_STAGE_COMPLETE_DUAL_STAGE_ACTION_IDENTIFIED"},
        {"id": "M3RCA_FORMAL_COTANGENT_SDR", "source": "FORMAL_COTANGENT_COMPARISON_8980", "target": "ACTION_RESIDUAL_940", "status": "EXACT_COMPARISON_ONLY_NOT_AUTHORITATIVE_SOURCE"},
        {"id": "M3RCB_COMPACT_SOURCE_DUAL", "source": "REPRESENTED_ENDPOINT_DFINITE_4080", "target": "ACTION_RESIDUAL_940", "status": "EXACT_ON_REPRESENTED_ACTION_DUAL"},
        {"id": "M4R_FORMAL_CYCLIC_CONTRACTION", "source": "FORMAL_COTANGENT_COMPARISON_8980", "target": "ACTION_RESIDUAL_940", "status": "EXACT_COMPARISON_ONLY"},
        {"id": "M1B_ACTUAL_REPRESENTED_COMPOSITE_CONTRACTION", "source": "LOCAL_GRAPH_BV_386", "target": "ACTION_RESIDUAL_940", "status": "MISSING_SERIALIZED_TYPED_COMPOSITE"},
    ]

    counts = {
        "exports_total": len(export_inventory),
        "exports_common_object_ready": sum(row["m1_preflight_status"] == "COMMON_OBJECT_READY_FOR_BINDING" for row in export_inventory),
        "exports_blocked_full_typed_ledger": sum(row["blocker"] == "M1A_FULL_TYPED_CARRIER_LEDGER" for row in export_inventory),
        "exports_blocked_composite_contraction": sum(row["blocker"] == "M1B_REPRESENTED_COMPOSITE_CONTRACTION" for row in export_inventory),
        "hashes_total": len(hash_inventory),
        "hash_objects_ready_await_binding": sum("READY" in row["status"] and "BLOCKED" not in row["status"] for row in hash_inventory),
        "hashes_blocked_before_binding": sum("BLOCKED" in row["status"] for row in hash_inventory),
        "freeze_checks_total": len(gate["freeze_check_reconciliation"]),
        "freeze_checks_common_snapshot_replayed": 0,
    }
    if counts != {
        "exports_total": 20,
        "exports_common_object_ready": 14,
        "exports_blocked_full_typed_ledger": 2,
        "exports_blocked_composite_contraction": 4,
        "hashes_total": 7,
        "hash_objects_ready_await_binding": 4,
        "hashes_blocked_before_binding": 3,
        "freeze_checks_total": 10,
        "freeze_checks_common_snapshot_replayed": 0,
    }:
        raise ValueError(f"M1 census drift: {counts}")

    value: dict[str, Any] = {
        "$schema": "../schema/strict-m1-common-snapshot-preflight-v1.schema.json",
        "schema": "strict-m1-common-snapshot-preflight-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-m1-common-snapshot-preflight-v1.schema.json",
        "result_id": "STRICT_M1_COMMON_SNAPSHOT_PREFLIGHT_V1",
        "result_kind": "CLASSICAL_IMPORT_COMMON_TYPED_DIAGRAM_PREFLIGHT",
        "result_state": "M1_SPLIT_INTO_TYPED_LEDGER_COMPOSITE_CONTRACTION_AND_FINAL_BINDING",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-16",
        "repository_base_commit": "89652649493e7a816aa43df642be878362f3b65b",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "question": "Can M1 be completed by hashing the existing objects, or does the common strict snapshot still require new typed mathematical data?",
        "answer": "M1 is not a clerical hash bundle. Fourteen of twenty exports are object-ready, but the full 386-row field/ghost/antifield grading ledger is absent and four residual-map/pairing exports exist only as separate local, D-finite, formal-cotangent and action-residual stages. The formal 8,980-coordinate cotangent comparison source cannot be declared the authoritative local BV source. M1 therefore splits into M1A, a full typed carrier ledger; M1B, an exact represented composite contraction from the actual 386-row graph architecture through the 30 endpoint species to the 940 action residual; and M1C, final seven-hash and ten-check binding. Gate A remains fail closed.",
        "authoritative_source_decision": {
            "local_source": "LOCAL_GRAPH_BV_386",
            "snapshot_shape": "CONTENT_ADDRESSED_TYPED_DIAGRAM_NOT_ONE_VECTOR_SPACE",
            "formal_8980_source_authoritative": False,
            "action_residual_940_is_target_not_local_source": True,
            "category_equalities_forbidden": [
                "LOCAL_GRAPH_BV_386=FORMAL_COTANGENT_COMPARISON_8980",
                "LOCAL_ENDPOINT_30=ZERO_MODE_15_PLUS_15",
                "LOCAL_ENDPOINT_30=ACTION_RESIDUAL_940",
            ],
        },
        "carrier_inventory": carriers,
        "cross_category_edges": edges,
        "local_row_ledger_audit": {
            "rows": len(local_rows),
            "serialized_fields": present_fields,
            "required_explicit_fields": LOCAL_ROW_REQUIRED_FIELDS,
            "missing_explicit_fields": missing_fields,
            "all_rows_have_required_explicit_fields": not missing_fields,
            "boundary": "Cohomological degree, block and row names do not by themselves certify antifield number, form degree, parity, mass dimension, Weyl weight, compact degree or derivative bounds.",
        },
        "export_inventory": export_inventory,
        "hash_inventory": hash_inventory,
        "freeze_check_inventory": [
            {
                "check_id": item["check_id"],
                "gate_v25_status": item["status"],
                "common_snapshot_replay_status": "WAITING_FOR_M1C_AFTER_M1A_M1B",
                "evidence": item["evidence"],
            }
            for item in gate["freeze_check_reconciliation"]
        ],
        "counts": counts,
        "m1_work_packages": [
            {
                "order": 1,
                "id": "M1A_FULL_TYPED_CARRIER_LEDGER",
                "status": "OPEN",
                "deliverable": "Serialize every local 386 row and every represented/residual row with explicit role and grading fields, preserving distinct local, harmonic, formal-dual, action-dual, zero-mode and centered categories.",
                "unlocks": ["field_ghost_antifield_dictionary", "field_gradings", "field_dictionary_hash", "differential_hash"],
            },
            {
                "order": 2,
                "id": "M1B_REPRESENTED_COMPOSITE_CONTRACTION",
                "status": "OPEN_AFTER_M1A",
                "deliverable": "Materialize and independently replay the represented composite inclusion, projection, homotopy and action pairing from the actual 386-row graph architecture through the 30 endpoint bundle and finite harmonic realization to the 940 action residual.",
                "unlocks": ["classical_inclusion_iota_cl", "classical_projection_pi_cl", "classical_homotopy_s_cl", "cyclic_pairing", "pairing_hash"],
            },
            {
                "order": 3,
                "id": "M1C_COMMON_MANIFEST_REPLAY",
                "status": "OPEN_AFTER_M1A_M1B",
                "deliverable": "Freeze the typed diagram at one commit, bind all twenty exports and seven hashes, and independently replay all ten Gate-A checks on exactly those bytes.",
                "unlocks": ["CLASSICAL_IMPORT_GATE_A_DECISION"],
            },
        ],
        "foundational_strength": {
            "exact_finite_inventory": "PRA-suitable hashing, counting and finite equality checks once authorities are supplied",
            "analytic_dependency": "M3RC-B imports the existing LORENTZIAN-CAUSAL compact-source/action-pairing theorem",
            "choice_principle_used_by_preflight": False,
            "weakest_foundation_proved": False,
        },
        "claim_flags": {
            "M1_PREFLIGHT_COMPLETE": True,
            "M1_IS_CLERICAL_HASH_BUNDLE": False,
            "M1_TYPED_DIAGRAM_REQUIRED": True,
            "M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE": False,
            "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE": False,
            "M1C_COMMON_MANIFEST_REPLAY_COMPLETE": False,
            "FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX": False,
            "M1_COMMON_STRICT_SNAPSHOT_COMPLETE": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
        },
        "does_not_establish": [
            "a full typed 386-row field, ghost, antifield and auxiliary grading ledger",
            "a represented composite contraction from the actual local graph BV carrier to the action residual",
            "that the formal 8,980-coordinate comparison source is the authoritative full classical BV source",
            "acceptance of any additional Gate-A hash",
            "a passed classical import gate",
            "a full-complex Hadamard state, renormalized Lorentzian products, QME restoration or residual quantum transfer",
        ],
        "next_gate": "Construct M1A from authoritative row semantics, not name inference; then build M1B on that typed carrier and only afterward attempt M1C hash acceptance and ten-check replay.",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_M1_COMMON_SNAPSHOT_PREFLIGHT_V1.md",
        "provenance": {
            "inputs": [
                {
                    "path": str(path.relative_to(ROOT)),
                    "result_or_artifact_id": source[name].get("result_id", source[name].get("snapshot_id", "CLASSICAL_IMPORT_BOOTSTRAP_V1")),
                    "sha256": sha(path),
                    "role": name,
                }
                for name, path in INPUTS.items()
            ]
        },
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_m1_common_snapshot_preflight.py",
            "checks": [
                "authority identities and content hashes",
                "twenty-export and seven-hash census",
                "386-row serialized versus required grading fields",
                "carrier dimensions and category inequalities",
                "M1A/M1B/M1C blocker partition",
                "formal-source, Gate-A, Hadamard and QME firewalls",
                "canonical preflight digest",
            ],
            "expected_digest": "",
        },
    }
    digest_keys = (
        "authoritative_source_decision", "carrier_inventory", "cross_category_edges",
        "local_row_ledger_audit", "export_inventory", "hash_inventory",
        "freeze_check_inventory", "counts", "m1_work_packages", "claim_flags",
    )
    value["independent_checker"]["expected_digest"] = digest({key: value[key] for key in digest_keys})
    return value


def report(value: dict[str, Any]) -> str:
    counts = value["counts"]
    packages = "\n".join(
        f"{row['order']}. **{row['id']}** — {row['deliverable']}" for row in value["m1_work_packages"]
    )
    return f"""# Strict M1 common-snapshot preflight v1

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
**Gate A:** `FAIL_CLOSED`

## Decision

M1 is not a clerical hash bundle.  The snapshot must be a content-addressed
typed diagram, because the 386-row local graph complex, the 30-row local
endpoint, the finite harmonic realization, the formal 8,980-coordinate
cotangent comparison, the 940-coordinate action residual, the zero modes and
the centered cochains are different mathematical objects.

Of {counts['exports_total']} required exports, {counts['exports_common_object_ready']}
are object-ready for common binding.  Two still lack a full explicit row and
grading ledger, and four have exact typed stages but no serialized composite
inclusion, projection, homotopy and pairing from the actual local architecture
to the action residual.  Four of seven hash objects are ready to bind; three
remain blocked.  None of the ten checks has yet been replayed on final M1
bytes.

## Work packages

{packages}

## Hard boundary

The formal 8,980-coordinate shifted-cotangent complex remains a comparison
source.  It is not the authoritative full BV source.  This preflight accepts
no new Gate-A hash and establishes no Hadamard, renormalized-product, QME or
residual-transfer lifecycle state.
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (
        (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(),
        report(value).encode(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("STRICT_M1_COMMON_SNAPSHOT_PREFLIGHT: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_M1_COMMON_SNAPSHOT_PREFLIGHT: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
