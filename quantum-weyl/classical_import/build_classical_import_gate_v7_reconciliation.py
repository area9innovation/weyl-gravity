#!/usr/bin/env python3
"""Build Gate-A v7 after the stabilized-q2 theory-identity preflight."""

from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
V6 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V6_RECONCILIATION.json"
PREFLIGHT = HERE / "certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V7_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V7.md"


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    payload = {
        key: value[key]
        for key in (
            "standalone_history_replay", "status_vocabulary", "export_reconciliation",
            "freeze_check_reconciliation", "required_hash_disposition", "minimal_missing_bundle",
            "gate_disposition", "m3_scoped_resolution", "m2_minimal_resolution",
            "m2_d_resolution", "m2_stabilized_candidate_resolution", "m4_minimal_resolution",
            "transitive_provenance_drift",
        )
    }
    return sha256(dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    previous, preflight = (loads(path.read_text()) for path in (V6, PREFLIGHT))
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V6_RECONCILIATION" or previous.get("gate_disposition", {}).get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("V6 predecessor drift")
    flags = preflight.get("claim_flags", {})
    if not all(flags.get(name) is True for name in (
        "STRICT_386_STABILIZED_Q2_CANDIDATE_CONSTRUCTED",
        "STRICT_386_STABILIZED_Q1_Q2_IDENTITY_VERIFIED",
        "STRICT_386_STABILIZED_Q2_CYCLICITY_VERIFIED",
        "STRICT_386_STABILIZED_D_Q2_DERIVATION_VERIFIED",
    )) or any(flags.get(name) is not False for name in (
        "STRICT_386_AUTHORITATIVE_FULL_Q2_IMPORTED",
        "STRICT_386_CANDIDATE_AUTHORITATIVE_EQUIVALENCE_CERTIFIED",
        "CLASSICAL_IMPORT_GATE_PASSED",
    )):
        raise ValueError("q2 preflight unavailable or over-promoted")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v7-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V7_RECONCILIATION",
        "result_state": "STABILIZED_Q2_CANDIDATE_CERTIFIED_AUTHORITATIVE_IDENTITY_OPEN",
        "created": "2026-08-15",
        "repository_base_commit": "2040f0c7964077686b7171b528be69cde62d4772",
        "question": "After constructing the exact cyclic trivial stabilization of minimal q2 on the 386-row graph carrier, which M2 obligations hold for that candidate, which authoritative import obligation remains, and does Gate A pass?",
        "answer": "The algebraic extension problem has a clean exact solution. In split coordinates the certified minimal q2 is extended by zero over the 356 contractible rows; the exact BV-canonical shear transports it to graph coordinates. The transported support envelope has 140 ordered-component channels, 68 distinct block triples, and 110 possible input and output rows. Direct-sum reasoning and exact conjugation preserve q1/q2, Koszul symmetry and cyclicity; stationary tensor naturality also proves the D/q2 derivation identity for this candidate. But the quantum receiver has constructed rather than imported this nonlinear extension. No authoritative classical 386-row q2 export or source-certified cyclic L-infinity equivalence identifies it with the intended nonminimal and generalized-auxiliary Weyl BV theory. Gate A therefore remains fail closed with zero accepted hashes. M2 is narrowed to a theory-identity/import obligation, while M1 and M3-M6 remain independently open.",
        "supersedes_for_current_status": previous["result_id"],
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V7.md",
    })

    exports = {row["export_id"]: row for row in value["export_reconciliation"]}
    checks = {row["check_id"]: row for row in value["freeze_check_reconciliation"]}
    exports["support_local_classical_bv_q2"].update({
        "evidence": [*exports["support_local_classical_bv_q2"]["evidence"], preflight["result_id"]],
        "established": "The six-row strict q2 and its exact 386-row cyclic trivial stabilization are receiver-verified as a construction. The graph transport has 140 ordered-component channels and 68 block triples.",
        "remaining_for_gate_a": "Import the authoritative full nonlinear classical q2 or a source-certified cyclic L-infinity equivalence identifying it with the stabilized candidate; then bind its hash to the common Gate-A manifest.",
        "boundary": "A mathematically valid receiver construction is not an authoritative classical import. The export remains scoped to the candidate until theory identity is source-certified.",
    })
    checks["q1_q2_arity_two_nilpotency"].update({
        "evidence": [*checks["q1_q2_arity_two_nilpotency"]["evidence"], preflight["result_id"]],
        "established": "The minimal 18-channel/51-path identity extends to the trivial stabilization and graph coordinates by endpoint/complement invariance and exact conjugation.",
        "remaining_for_gate_a": "Establish that the authoritative nonlinear classical extension is this candidate or transport the identity through a source-certified cyclic L-infinity equivalence.",
        "boundary": "The zero-defect identity is exact for the candidate, not yet an imported full-theory identity.",
    })
    checks["q2_cyclic_compatibility"].update({
        "evidence": [*checks["q2_cyclic_compatibility"]["evidence"], preflight["result_id"]],
        "established": "Minimal q2 cyclicity extends over the orthogonal contractible complement and is preserved by the exact BV-canonical graph shear.",
        "remaining_for_gate_a": "Supply authoritative theory identity and bind the resulting full-carrier q2 and pairing bytes to the common manifest.",
        "boundary": "Candidate cyclicity does not certify that the source classical programme chose the trivial nonlinear stabilization.",
    })
    checks["D_q2_derivation"].update({
        "status": "SUPPORTING_EVIDENCE_ONLY",
        "evidence": [preflight["result_id"]],
        "established": "For the stabilized candidate, T=Lie_partial_t is a derivation of all twelve stationary tensor-natural minimal q2 operators and commutes with both exact shear circuits; D/q2 has zero structural defects.",
        "remaining_for_gate_a": "Import authoritative full-theory q2 identity before treating this candidate derivation proof as a Gate-A freeze check.",
        "boundary": "This replaces the Berger control with a strict-carrier candidate, but the candidate is not yet an authoritative classical import.",
    })

    value["required_hash_disposition"]["q2_hash"].update({
        "accepted": None,
        "candidate": preflight["canonical_hashes"]["graph_transport_dag_sha256"],
        "candidate_scope": "STRICT_386_STABILIZED_CONSTRUCTION_NOT_AUTHORITATIVE_IMPORT",
    })
    for item in value["minimal_missing_bundle"]:
        if item["id"] == "M2_STRICT_Q2_D":
            item["object"] = "Resolve theory identity for the exact 386-row stabilized q2 candidate: import either the authoritative full nonlinear classical q2 ledger or a source-certified cyclic L-infinity equivalence to the trivial stabilization. The candidate q1q2, Koszul, cyclicity and D/q2 identities are no longer algebraically open."
            item["unlocks"] = ["authoritative full-carrier q2 export", "authoritative D_q2_derivation", "accepted q2 common-snapshot hash"]

    value["gate_disposition"].update({
        "claim_state": "CLASSICAL_IMPORT_Q2_STABILIZATION_CANDIDATE_CERTIFIED_THEORY_IDENTITY_OPEN",
        "same_theory_receiver_verified_scoped": 11,
        "different_theory_controls": 0,
        "freeze_checks_receiver_verified_scoped": 8,
        "freeze_checks_different_theory": 0,
        "freeze_checks_supporting_evidence_only": 1,
        "freeze_checks_blocked": 1,
        "accepted_common_snapshot_hashes": 0,
    })
    value["m2_minimal_resolution"].update({
        "remaining": "Minimal q2 and its exact cyclic 386-row stabilization now satisfy q1q2, Koszul, cyclicity and D/q2 as a receiver construction. Authoritative classical theory identity and an accepted common q2 hash remain open.",
        "boundary": "The receiver may classify and verify the candidate but may not manufacture the authoritative classical nonlinear extension required by the import gate.",
    })
    value["m2_stabilized_candidate_resolution"] = {
        "status": "CERTIFIED_CONSTRUCTION_NOT_AUTHORITATIVE_IMPORT",
        "evidence": preflight["result_id"],
        "carrier_rows": preflight["scope"]["carrier_rows"],
        "split_endpoint_rows": preflight["scope"]["endpoint_rows"],
        "split_contractible_rows": preflight["scope"]["split_contractible_rows"],
        "graph_input_row_envelope": preflight["graph_transport_dag"]["active_input_row_envelope"],
        "graph_output_row_envelope": preflight["graph_transport_dag"]["active_output_row_envelope"],
        "expanded_component_channels": preflight["graph_transport_dag"]["expanded_ordered_component_channels"],
        "unique_block_triples": preflight["graph_transport_dag"]["unique_block_triples"],
        "interaction_inert_rows": preflight["graph_transport_dag"]["interaction_inert_rows"],
        "q1_q2_defects": preflight["identity_transport"]["q1_q2_arity_two"]["defects"],
        "q2_cyclicity_defects": preflight["identity_transport"]["q2_cyclicity"]["defects"],
        "D_q2_derivation_defects": preflight["identity_transport"]["D_q2_derivation"]["derivation_defects"],
        "candidate_q2_sha256": preflight["canonical_hashes"]["graph_transport_dag_sha256"],
        "remaining": "Source-certify theory identity by a full nonlinear export or cyclic L-infinity equivalence; only then can the candidate hash be considered for Gate A.",
    }
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(V6.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": file_hash(V6), "role": "immutable Gate-A V6 predecessor"},
        {"path": str(PREFLIGHT.relative_to(ROOT)), "result_or_artifact_id": preflight["result_id"], "sha256": file_hash(PREFLIGHT), "role": "strict 386-row stabilized-q2 construction and theory-identity preflight"},
    ]
    drift = []
    for source in previous["provenance"]["inputs"]:
        path = ROOT / source["path"]
        current = file_hash(path) if path.is_file() else None
        if current != source["sha256"]:
            drift.append({
                "path": source["path"],
                "historical_v6_sha256": source["sha256"],
                "current_worktree_sha256": current,
                "status": "RECORDED_NOT_SILENTLY_REBOUND",
                "disposition": "V6 remains content-pinned; current bytes are not substituted without a successor replay.",
            })
    value["transitive_provenance_drift"] = {
        "files_checked": len(previous["provenance"]["inputs"]),
        "drifted_files": len(drift),
        "status": "DRIFT_RECORDED_GATE_REMAINS_FAIL_CLOSED",
        "entries": drift,
    }
    value["claim_flags"].update({
        "STRICT_386_STABILIZED_Q2_CANDIDATE": True,
        "STRICT_386_STABILIZED_Q1_Q2_IDENTITY": True,
        "STRICT_386_STABILIZED_Q2_CYCLICITY": True,
        "STRICT_386_STABILIZED_D_Q2_DERIVATION": True,
        "STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q2": False,
        "STRICT_386_AUTHORITATIVE_D_Q2_DERIVATION": False,
        "STRICT_386_CANDIDATE_THEORY_IDENTITY": False,
        "STRICT_386_FULL_CARRIER_Q2": False,
        "STRICT_386_D_Q2_DERIVATION": False,
    })
    value["does_not_establish"] = [
        *previous["does_not_establish"],
        "that the receiver-constructed cyclic trivial stabilization is the authoritative classical nonlinear q2",
        "a source-certified cyclic L-infinity equivalence between the intended classical extension and the stabilized candidate",
    ]
    value["next_gate"] = "Move the q2 decision to the authoritative classical programme. Export either the full nonlinear 386-row q2, including every intended nonminimal and generalized-auxiliary interaction, or a cyclic L-infinity equivalence identifying that extension with STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1. The quantum receiver must independently compare the export, preserve the candidate q1q2/cyclicity/Dq2 identities, and only then bind an authoritative q2 hash into the complete Gate-A manifest. M1 and M3-M6 remain independent blockers; no Hadamard or QME lifecycle promotion is authorized."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v7_reconciliation.py",
        "checks": [
            "V6 predecessor and q2-preflight pins", "twenty-export and ten-check order",
            "candidate q2 hash remains unaccepted", "candidate identities separated from authoritative import",
            "D/q2 reclassified from Berger control to strict supporting evidence", "theory-identity M2 frontier",
            "transitive drift recorded without rebinding", "zero accepted hashes", "Gate-A and quantum lifecycle firewall",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    candidate = value["m2_stabilized_candidate_resolution"]
    drift = value["transitive_provenance_drift"]
    return f"""# Classical import Gate-A reconciliation v7

**Result:** `{value['result_id']}`

**Lifecycle:** `{value['lifecycle']}`

**Gate A:** `{value['gate_disposition']['gate_a_status']}`

## Outcome

The strict minimal q2 has an exact cyclic trivial stabilization on the full
**{candidate['carrier_rows']}**-row carrier.  Its graph-coordinate action DAG
has **{candidate['expanded_component_channels']}** ordered-component channels,
**{candidate['unique_block_triples']}** block triples and
**{candidate['graph_input_row_envelope']} / {candidate['graph_output_row_envelope']}**
input/output row envelopes.  Candidate q1/q2, q2 cyclicity and D/q2 defects are
**{candidate['q1_q2_defects']} / {candidate['q2_cyclicity_defects']} / {candidate['D_q2_derivation_defects']}**.

## The remaining M2 obstruction

The construction is internally valid, but it was made by the quantum receiver.
No authoritative classical export or source-certified cyclic L-infinity
equivalence says that the intended nonminimal and generalized-auxiliary theory
is this trivial stabilization.  The candidate q2 hash is therefore recorded
but not accepted.

The old Berger D/q2 control is no longer the closest evidence.  It is replaced
by strict-carrier supporting evidence, still below a Gate-A freeze check because
the theory-identity link is missing.

## Gate verdict

Gate A remains fail closed with **{value['gate_disposition']['accepted_common_snapshot_hashes']}**
accepted hashes.  The export/check counts are unchanged at
**{value['gate_disposition']['same_theory_receiver_verified_scoped']} / {value['gate_disposition']['exports_total']}**
scoped exports and **{value['gate_disposition']['freeze_checks_receiver_verified_scoped']} / {value['gate_disposition']['freeze_checks_total']}**
scoped checks.  One check is supporting evidence and one remains blocked.
M1 and M3-M6 are independent blockers.

## Provenance drift

The V6 input ledger contains **{drift['files_checked']}** records; **{drift['drifted_files']}**
current files differ from those historical hashes.  Every difference is
recorded and none is silently rebound.

## Reproduction

```bash
python3 quantum-weyl/classical_import/build_classical_import_gate_v7_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v7_reconciliation.py
python3 quantum-weyl/classical_import/verify_classical_import_gate_v7_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v7_reconciliation.py
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), report(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("CLASSICAL_IMPORT_GATE_V7_RECONCILIATION: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V7_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
