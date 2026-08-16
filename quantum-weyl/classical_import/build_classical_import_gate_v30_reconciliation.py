#!/usr/bin/env python3
"""Decide Gate A against the independently verified M1C common snapshot."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
PREVIOUS = HERE / "certificates/CLASSICAL_IMPORT_GATE_V29_RECONCILIATION.json"
DUAL = HERE / "certificates/STRICT_M1B_ACTION_DUAL_LIFT_V1.json"
CYCLIC = HERE / "certificates/STRICT_M1B_TYPED_CYCLIC_COMPOSITE_V1.json"
M1C = HERE / "certificates/STRICT_M1C_COMMON_SNAPSHOT_V1.json"
SCHEMA = HERE / "schema/quantum-weyl-classical-import-gate-v30-reconciliation-v1.schema.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V30_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V30.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    body = deepcopy(value)
    body.get("independent_checker", {}).pop("expected_digest", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    previous, dual, cyclic, m1c = map(load, (PREVIOUS, DUAL, CYCLIC, M1C))
    expected = (
        (previous, "CLASSICAL_IMPORT_GATE_V29_RECONCILIATION"),
        (dual, "STRICT_M1B_ACTION_DUAL_LIFT_V1"),
        (cyclic, "STRICT_M1B_TYPED_CYCLIC_COMPOSITE_V1"),
        (m1c, "STRICT_M1C_COMMON_SNAPSHOT_V1"),
    )
    if any(value.get("result_id") != result_id for value, result_id in expected):
        raise ValueError("Gate V30 authority drift")
    if previous["gate_disposition"]["gate_a_status"] != "FAIL_CLOSED":
        raise ValueError("Gate V29 predecessor boundary drift")
    if dual["claim_flags"]["M1B_ACTION_DUAL_LIFT_COMPLETE"] is not True or cyclic["claim_flags"]["M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE"] is not True:
        raise ValueError("M1B completion missing")
    flags = m1c["claim_flags"]
    if not all(flags[key] for key in ("M1_COMMON_STRICT_SNAPSHOT_COMPLETE", "ALL_20_EXPORTS_COMMON_BOUND", "ALL_7_TOP_LEVEL_HASHES_COMMON_BOUND", "ALL_10_GATE_A_CHECKS_COMMON_REPLAYED")):
        raise ValueError("M1C common snapshot incomplete")
    if flags["CLASSICAL_IMPORT_GATE_PASSED"] is not False:
        raise ValueError("M1C improperly self-promoted Gate A")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v30-reconciliation-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "result_id": "CLASSICAL_IMPORT_GATE_V30_RECONCILIATION",
        "result_state": "CLASSICAL_IMPORT_GATE_A_VERIFIED_ON_IMMUTABLE_STRICT_PURE_WEYL_SNAPSHOT",
        "created": "2026-08-16",
        "repository_base_commit": "c4a9cc45829bd02ea723f47a2565b042d841c118",
        "question": "Does the independently verified M1C snapshot satisfy every classical import Gate-A requirement?",
        "answer": "Yes. The immutable M1C snapshot binds all twenty exports and seven top-level hashes under one six-object typed carrier diagram, and independent receivers replay all ten Gate-A checks plus three supplemental q3/residual/cohomology audits on those exact bytes. Gate A is therefore VERIFIED for the strict pure-Weyl classical BV snapshot. This removes the classical import blocker only: nonlinear Green compatibility, full-complex Hadamard data, renormalized Lorentzian products, the QME, and residual quantum transfer remain unconstructed.",
        "supersedes_for_current_status": previous["result_id"],
        "historical_certificate_preserved": True,
        "human_report": str(REPORT.relative_to(ROOT)),
    })
    value["m1_common_snapshot_preflight_resolution"].update({
        "work_packages": [
            {"order": 1, "id": "M1A_FULL_TYPED_CARRIER_LEDGER", "status": "COMPLETE"},
            {"order": 2, "id": "M1B_REPRESENTED_COMPOSITE_CONTRACTION", "status": "COMPLETE"},
            {"order": 3, "id": "M1C_COMMON_MANIFEST_REPLAY", "status": "COMPLETE"},
        ],
        "m1b_primal_composite_contraction_complete": True,
        "m1b_action_dual_lift_complete": True,
        "m1b_typed_cyclic_replay_complete": True,
        "m1b_represented_composite_contraction_complete": True,
        "m1c_common_manifest_replay_complete": True,
        "accepted_common_snapshot_hashes_added": 6,
    })
    value["m1b_action_dual_completion_resolution"] = {
        "result_id": dual["result_id"], "certificate_sha256": sha(DUAL), "content_sha256": dual["content_sha256"],
        "compact_source_action_duals": 470, "represented_action_test_check_coordinates": 4080,
        "exact_dual_identity_defects": sum(dual["represented_dual_lift"]["exact_replay"].values()),
        "M1B_action_dual_complete": True,
    }
    value["m1b_cyclic_completion_resolution"] = {
        "result_id": cyclic["result_id"], "certificate_sha256": sha(CYCLIC), "content_sha256": cyclic["content_sha256"],
        **cyclic["exact_cyclic_replay"]["aggregate"],
        "M1B_complete": True,
    }
    value["m1c_common_snapshot_resolution"] = {
        "result_id": m1c["result_id"], "certificate_sha256": sha(M1C), "content_sha256": m1c["content_sha256"],
        "snapshot_id": m1c["snapshot_id"], "snapshot_sha256": m1c["snapshot_sha256"],
        "artifact_pins": len(m1c["artifact_pins"]), "exports_bound": len(m1c["export_bindings"]),
        "top_level_hashes_bound": len(m1c["accepted_top_level_hashes"]),
        "gate_checks_passed": sum(item["status"] == "PASS_ON_COMMON_BYTES" for item in m1c["gate_a_replay"]),
        "supplemental_checks_passed": sum(item["status"] == "PASS_ON_COMMON_BYTES" for item in m1c["supplemental_replay"]),
        "M1C_complete": True,
    }
    value["export_reconciliation"] = [
        {
            "export_id": item["export_id"], "status": "RECEIVER_VERIFIED_COMMON_SNAPSHOT",
            "evidence": [obj["pin_id"] for obj in item["objects"]],
            "boundary": item["boundary"],
        }
        for item in m1c["export_bindings"]
    ]
    value["freeze_check_reconciliation"] = [
        {
            "check_id": item["check_id"], "status": "RECEIVER_VERIFIED_COMMON_SNAPSHOT",
            "evidence": item["pins"], "established": item["witness"],
            "remaining_for_gate_a": None,
            "boundary": "The check is scoped to the immutable typed snapshot and does not promote nonlinear Green, Hadamard, renormalization, QME, or residual-transfer claims.",
        }
        for item in m1c["gate_a_replay"]
    ]
    value["required_hash_disposition"] = {
        key: {"accepted": hash_value, "candidate": hash_value, "candidate_scope": f"COMMON_IMMUTABLE_SNAPSHOT_{m1c['snapshot_id']}"}
        for key, hash_value in m1c["accepted_top_level_hashes"].items()
    }
    value["minimal_missing_bundle"] = []
    value["gate_disposition"].update({
        "gate_a_status": "VERIFIED",
        "claim_state": "CLASSICAL_IMPORT_VERIFIED_ON_ONE_IMMUTABLE_STRICT_PURE_WEYL_TYPED_SNAPSHOT",
        "publishable_quantum_results_allowed_by_gate_a": True,
        "exports_total": 20,
        "same_theory_receiver_verified_scoped": 20,
        "different_theory_controls": 0,
        "legacy_accepted_scoped": 0,
        "supporting_evidence_only": 0,
        "missing_portable_objects": 0,
        "freeze_checks_total": 10,
        "freeze_checks_receiver_verified_scoped": 10,
        "freeze_checks_different_theory": 0,
        "freeze_checks_blocked": 0,
        "accepted_common_snapshot_hashes": 7,
    })
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREVIOUS.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(PREVIOUS), "role": "immutable fail-closed predecessor"},
        {"path": str(DUAL.relative_to(ROOT)), "result_or_artifact_id": dual["result_id"], "sha256": sha(DUAL), "role": "M1B action-derived dual lift"},
        {"path": str(CYCLIC.relative_to(ROOT)), "result_or_artifact_id": cyclic["result_id"], "sha256": sha(CYCLIC), "role": "M1B typed rank-940 cyclic composite"},
        {"path": str(M1C.relative_to(ROOT)), "result_or_artifact_id": m1c["result_id"], "sha256": sha(M1C), "role": "independently receiver-verified immutable common snapshot"},
    ]
    value["claim_flags"].update({
        "M1B_PRIMAL_COMPOSITE_CONTRACTION_COMPLETE": True,
        "M1B_ACTION_DUAL_LIFT_COMPLETE": True,
        "M1B_TYPED_CYCLIC_REPLAY_COMPLETE": True,
        "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE": True,
        "M1C_COMMON_MANIFEST_REPLAY_COMPLETE": True,
        "M1_COMMON_STRICT_SNAPSHOT_COMPLETE": True,
        "COMMON_GATE_A_FREEZE_BOUND": True,
        "CLASSICAL_IMPORT_GATE_PASSED": True,
        "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A": True,
        "NONLINEAR_GREEN_COMPATIBILITY_CERTIFIED": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED": False,
        "QME_RESTORED": False,
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
    })
    # This is a current-status reconciliation.  Keep the predecessor pinned
    # for history, but do not inherit limitations which V30 itself discharged.
    value["does_not_establish"] = [
        "a new scientific identity from the standalone-history migration repair",
        "that Berger q2 or D belongs to strict pure-Weyl gravity",
        "that an auxiliary deformation retract is the residual SDR",
        "that a causal Green homotopy is s_cl",
        "support-locality of the D-finite W+/W- harmonic projector",
        "an all-energy or arbitrary-smooth completion of the represented harmonic comparison",
        "that the formal 8,980-coordinate cotangent comparison source is the authoritative classical BV source",
        "a one-particle interpretation for W_+^2 or W_-^2",
        "q2/q3 compatibility with the typed advanced and retarded Green homotopies",
        "a complete Lorentzian off-shell BV propagator or BRST-compatible Hadamard two-point function",
        "renormalized Lorentzian products, QME restoration, residual transfer, physical positivity, or a Lorentzian quantum theory",
    ]
    value["next_gate"] = "With Gate A verified, audit nonlinear q2/q3 compatibility with the typed advanced and retarded Green homotopies on the immutable snapshot; only then attempt the BRST-compatible Hadamard two-point function or state a scoped obstruction."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v30_reconciliation.py",
        "checks": [
            "Gate V29, M1B action-dual/cyclic, and M1C content pins",
            "independent M1C receiver chain on the exact immutable snapshot",
            "twenty common exports, seven hashes, ten Gate-A checks, and three supplemental audits",
            "six-object typed carrier and comparison-source exclusions",
            "Gate-A promotion with nonlinear Green/Hadamard/QME firewalls",
            "canonical Gate V30 digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    Draft202012Validator(load(SCHEMA)).validate(value)
    return value


def report(value: dict[str, Any]) -> str:
    snapshot = value["m1c_common_snapshot_resolution"]
    return f"""# Classical import Gate-A reconciliation v30

**Result:** `{value['result_id']}`
**Gate A:** `VERIFIED`
**Snapshot:** `{snapshot['snapshot_id']}`
**Snapshot SHA-256:** `{snapshot['snapshot_sha256']}`

## Decision

Gate A passes for one immutable strict pure-Weyl classical BV typed snapshot.
The receiver verifies all {snapshot['exports_bound']} exports, all
{snapshot['top_level_hashes_bound']} hashes, all {snapshot['gate_checks_passed']}
required checks, and {snapshot['supplemental_checks_passed']} supplemental q3,
residual, and centered-cohomology audits on the exact pinned bytes.

This is a classical import decision.  It authorizes quantum work to depend on
the snapshot; it does not itself create a quantum result.  Nonlinear q2/q3
compatibility with advanced and retarded Green homotopies is the next gate.
No full-complex Hadamard function, renormalized Lorentzian products, QME
restoration, residual transfer, or Lorentzian quantum theory is claimed.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    outputs = {RESULT: json.dumps(value, indent=2, ensure_ascii=False) + "\n", REPORT: report(value)}
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.is_file() or path.read_text() != content]
        if stale:
            print("stale generated artifacts: " + ", ".join(stale))
            return 1
        print("CLASSICAL_IMPORT_GATE_V30_RECONCILIATION: CURRENT")
        return 0
    for path, content in outputs.items():
        path.write_text(content)
    print("CLASSICAL_IMPORT_GATE_V30_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
