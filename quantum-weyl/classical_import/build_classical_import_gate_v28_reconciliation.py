#!/usr/bin/env python3
"""Build Gate-A v28 after the complete M1A typed-diagram freeze."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
PREVIOUS = HERE / "certificates/CLASSICAL_IMPORT_GATE_V27_RECONCILIATION.json"
M1A3 = HERE / "certificates/STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1.json"
M1A4 = HERE / "certificates/STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V28_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V28.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    body = deepcopy(value)
    body.get("independent_checker", {}).pop("expected_digest", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    previous = json.loads(PREVIOUS.read_text())
    m1a3 = json.loads(M1A3.read_text())
    m1a4 = json.loads(M1A4.read_text())
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V27_RECONCILIATION":
        raise ValueError("Gate V27 predecessor drift")
    if (
        m1a3.get("result_id") != "STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1"
        or m1a3.get("claim_flags", {}).get("M1A3_REPRESENTED_CROSSWALK_COMPLETE") is not True
        or m1a4.get("result_id") != "STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1"
        or m1a4.get("claim_flags", {}).get("M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE") is not True
        or m1a4.get("claim_flags", {}).get("CLASSICAL_IMPORT_GATE_PASSED") is not False
    ):
        raise ValueError("M1A completion firewall drift")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v28-reconciliation-v1",
        "schema_path": "quantum-weyl/classical_import/schema/quantum-weyl-classical-import-gate-v28-reconciliation-v1.schema.json",
        "result_id": "CLASSICAL_IMPORT_GATE_V28_RECONCILIATION",
        "result_state": "M1A_TYPED_DIAGRAM_COMPLETE_M1B_COMPOSITE_OPEN_GATE_FAIL_CLOSED",
        "created": "2026-08-16",
        "repository_base_commit": "a03539c2d82920e945cb776186531b95e993a105",
        "question": "After M1A3 and the immutable M1A4 typed-diagram freeze, what remains before the strict classical import can pass?",
        "answer": "M1A is complete. The authoritative typed diagram content-addresses 17,779 rows across six distinct local, harmonic, residual, action-dual, zero-mode and centered carriers. The separate 410-row test fixture and formal 8,980-row cotangent comparison are explicitly excluded. Gate A remains fail closed because M1B has not yet materialized the composite inclusion, projection, homotopy and action pairing across those exact carriers, and M1C has not bound all twenty exports and seven hashes or replayed all ten checks on one immutable manifest.",
        "supersedes_for_current_status": previous["result_id"],
        "historical_certificate_preserved": True,
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V28.md",
    })
    resolution = value["m1_common_snapshot_preflight_resolution"]
    work = deepcopy(resolution["work_packages"])
    work[0].update({
        "status": "COMPLETE",
        "deliverable": "Complete: 17,779 authoritative rows are frozen across six typed carrier objects with 410 test and 8,980 formal comparison rows explicitly excluded.",
    })
    work[1].update({
        "status": "OPEN",
        "deliverable": "Materialize the exact represented composite inclusion, projection, homotopy and action pairing from the 386-row graph through the support-local endpoint and finite harmonic stages to the rank-940 action residual.",
    })
    work[2].update({"status": "OPEN_AFTER_M1B"})
    resolution.update({
        "work_packages": work,
        "m1a_represented_crosswalk_complete": True,
        "m1a_immutable_ledger_freeze_complete": True,
        "m1a_full_typed_carrier_ledger_complete": True,
        "m1b_represented_composite_contraction_complete": False,
        "accepted_common_snapshot_hashes_added": 0,
    })
    value["m1a_completion_resolution"] = {
        "represented_crosswalk_result_id": m1a3["result_id"],
        "represented_crosswalk_certificate_sha256": sha(M1A3),
        "typed_ledger_result_id": m1a4["result_id"],
        "typed_ledger_certificate_sha256": sha(M1A4),
        "represented_endpoint_rows": m1a3["counts"]["represented_endpoint_coordinates"],
        "test_nonminimal_rows_excluded": m1a3["counts"]["test_nonminimal_coordinates_excluded"],
        "test_nonminimal_doublets": m1a3["counts"]["test_nonminimal_doublets"],
        "action_residual_primal_rows": m1a3["counts"]["action_residual_primal_coordinates"],
        "action_residual_dual_rows": m1a3["counts"]["action_residual_dual_coordinates"],
        "authoritative_rows_total": m1a4["counts"]["authoritative_rows_total"],
        "authoritative_carrier_objects": m1a4["counts"]["authoritative_carrier_objects"],
        "untyped_authoritative_rows": m1a4["counts"]["untyped_authoritative_rows"],
        "category_identification_defects": m1a4["counts"]["category_identification_defects"],
        "q0_cross_partition_defects": m1a3["counts"]["q0_cross_partition_defects"],
        "q0_chain_degree_defects": m1a3["counts"]["q0_chain_degree_defects"],
        "residual_crosswalk_defects": m1a3["counts"]["residual_crosswalk_defects"],
        "typed_field_dictionary_candidate_sha256": m1a4["typed_field_dictionary"]["sha256"],
        "typed_diagram_candidate_sha256": m1a4["diagram_freeze"]["sha256"],
        "M1A_complete": True,
        "remaining_M1_packages": ["M1B_REPRESENTED_COMPOSITE_CONTRACTION", "M1C_COMMON_MANIFEST_REPLAY"],
    }
    for row in value["export_reconciliation"]:
        if row.get("export_id") in {"field_ghost_antifield_dictionary", "field_gradings"}:
            row.update({
                "m1_v28_status": "M1A_TYPED_DIAGRAM_FROZEN_AWAIT_M1C_COMMON_BINDING",
                "blocker": "M1C_COMMON_MANIFEST_REPLAY_AFTER_M1B",
                "m1a_typed_diagram_sha256": m1a4["diagram_freeze"]["sha256"],
            })
    value["required_hash_disposition"]["field_dictionary_hash"].update({
        "candidate": m1a4["typed_field_dictionary"]["sha256"],
        "candidate_scope": "M1A_COMPLETE_TYPED_DIAGRAM_CANDIDATE_AWAIT_M1B_AND_M1C_COMMON_BINDING",
    })
    value["minimal_missing_bundle"][0].update({
        "completed_work_packages": ["M1A_FULL_TYPED_CARRIER_LEDGER"],
        "remaining_work_packages": ["M1B_REPRESENTED_COMPOSITE_CONTRACTION", "M1C_COMMON_MANIFEST_REPLAY"],
    })
    value["gate_disposition"].update({
        "gate_a_status": "FAIL_CLOSED",
        "claim_state": "CLASSICAL_IMPORT_M1A_COMPLETE_M1B_COMPOSITE_OPEN",
        "publishable_quantum_results_allowed_by_gate_a": False,
    })
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREVIOUS.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(PREVIOUS), "role": "immutable Gate V27 predecessor"},
        {"path": str(M1A3.relative_to(ROOT)), "result_or_artifact_id": m1a3["result_id"], "sha256": sha(M1A3), "role": "independently checked represented and action-residual crosswalk"},
        {"path": str(M1A4.relative_to(ROOT)), "result_or_artifact_id": m1a4["result_id"], "sha256": sha(M1A4), "role": "independently checked immutable typed-diagram freeze"},
    ]
    value["claim_flags"].update({
        "M1A3_REPRESENTED_CROSSWALK_COMPLETE": True,
        "M1A4_LEDGER_FREEZE_COMPLETE": True,
        "M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE": True,
        "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE": False,
        "M1C_COMMON_MANIFEST_REPLAY_COMPLETE": False,
        "FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "QME_RESTORED": False,
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "M1B composite contraction or M1C common replay from the completed M1A typed ledger alone",
        "that the 410 test rows or formal 8,980 cotangent rows belong to the authoritative source",
        "a passed Gate A, Hadamard state, renormalized products, QME restoration or residual quantum transfer",
    ]))
    value["next_gate"] = "Construct M1B on the exact M1A typed diagram: compose the support-local 386-to-30 graph SDR with the represented harmonic analysis/synthesis and compact-source action-dual stages, serialize pi_cl, iota_cl, s_cl and the action pairing, and independently replay their typed identities before M1C."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v28_reconciliation.py",
        "checks": [
            "Gate V27 predecessor and M1A3/M1A4 content pins",
            "4,080/410/470+470 represented census and zero crosswalk defects",
            "17,779-row six-carrier typed-diagram freeze",
            "test/formal comparison exclusions",
            "M1A complete with M1B and M1C still open",
            "unchanged twenty exports, ten checks and one accepted hash",
            "formal-source/Gate-A/Hadamard/QME firewalls",
            "canonical reconciliation digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    resolution = value["m1a_completion_resolution"]
    return f"""# Classical import Gate-A reconciliation v28

**Result:** `{value['result_id']}`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

**Gate A:** `FAIL_CLOSED`

M1A is complete.  The immutable typed diagram binds **{resolution['authoritative_rows_total']:,}
authoritative rows** across **{resolution['authoritative_carrier_objects']} distinct carrier
objects**.  It includes 386 local graph rows, {resolution['represented_endpoint_rows']:,}
represented endpoint coordinates, {resolution['action_residual_primal_rows']} primal plus
{resolution['action_residual_dual_rows']} compact-source action-dual residual rows, thirty
zero-mode rows and 12,343 centered cochains.  Every authoritative row has a
materialization rule and there are zero category-identification defects.

The 410 historical test coordinates are exactly {resolution['test_nonminimal_doublets']}
scalar doublets and remain an excluded comparison fixture.  The formal 8,980-row
cotangent completion also remains comparison-only.  Neither is silently identified
with the strict local BV source.

## Remaining M1 construction

M1B must now materialize the represented composite `iota_cl`, `pi_cl`, `s_cl`
and action pairing across the frozen carriers.  M1C must then bind all twenty
exports and seven hashes and replay all ten Gate-A identities on one immutable
manifest.  The field-dictionary hash printed by M1A is a candidate, not an
accepted common-snapshot hash.

Gate A still accepts one of seven hashes and remains fail closed.  No
full-complex Hadamard state, renormalized Lorentzian products, QME restoration
or residual quantum transfer is promoted.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    outputs = {RESULT: json.dumps(value, indent=2, ensure_ascii=False) + "\n", REPORT: report(value)}
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.exists() or path.read_text() != content]
        if stale:
            raise SystemExit("stale generated artifacts: " + ", ".join(stale))
        print("CLASSICAL_IMPORT_GATE_V28_RECONCILIATION: generated artifacts current")
        return 0
    for path, content in outputs.items():
        path.write_text(content)
    print("CLASSICAL_IMPORT_GATE_V28_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
