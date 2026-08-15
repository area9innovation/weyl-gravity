#!/usr/bin/env python3
"""Build Gate-A v8 after the exact nonminimal theory-identity obstruction."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
V7 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V7_RECONCILIATION.json"
OBSTRUCTION = HERE / "certificates/STRICT_386_NONMINIMAL_THEORY_IDENTITY_OBSTRUCTION_V1.json"
CLASSICAL = ROOT / "d_quotient_classical/certificates/CLASSICAL_ORDINARY_DERIVATIVE_AUXILIARY_CUBIC_EXPORT_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V8_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V8.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "standalone_history_replay", "status_vocabulary", "export_reconciliation",
        "freeze_check_reconciliation", "required_hash_disposition", "minimal_missing_bundle",
        "gate_disposition", "m3_scoped_resolution", "m2_minimal_resolution", "m2_d_resolution",
        "m2_stabilized_candidate_resolution", "m2_theory_identity_obstruction", "m4_minimal_resolution",
        "transitive_provenance_drift",
    )
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    previous, obstruction, classical = (json.loads(path.read_text()) for path in (V7, OBSTRUCTION, CLASSICAL))
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V7_RECONCILIATION" or previous.get("gate_disposition", {}).get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("V7 predecessor drift")
    flags = obstruction.get("claim_flags", {})
    if flags.get("LITERAL_TRIVIAL_STABILIZATION_THEORY_IDENTITY_REFUTED") is not True or flags.get("NONLINEAR_CYCLIC_L_INFINITY_EQUIVALENCE_OBSTRUCTED") is not False:
        raise ValueError("identity-obstruction authority drift")
    if classical.get("result_id") != "CLASSICAL_ORDINARY_DERIVATIVE_AUXILIARY_CUBIC_EXPORT_V1":
        raise ValueError("classical cubic export drift")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v8-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V8_RECONCILIATION",
        "result_state": "LINEAR_THEORY_IDENTITY_REFUTED_NONLINEAR_EQUIVALENCE_REQUIRED_GATE_FAIL_CLOSED",
        "created": "2026-08-15",
        "repository_base_commit": "5013af08d48bf45d99d9b841a75244122e3822f9",
        "question": "Does the authoritative ordinary-derivative action identify with the exact trivial q2/q3 stabilization under the recorded linear coordinates, and what does the answer do to Gate A?",
        "answer": "No. The source cyclic form Omega(f_hat,q2(v,v)) is -1, while the trivial stabilization gives zero. Literal zero-extension and the recorded linear shear are therefore exactly ruled out as the authoritative nonlinear import. The candidate identities remain valid, and nonlinear equivalence is not ruled out. M2 is now a constructive obligation: import the quadratic auxiliary-elimination or cyclic L-infinity map, replay source q2/q3 pullback identities, and only then reconsider the q2/q3 hashes. Gate A remains fail closed with zero accepted hashes; M1 and M3-M6 remain independent blockers.",
        "supersedes_for_current_status": previous["result_id"],
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V8.md",
    })
    exports = {row["export_id"]: row for row in value["export_reconciliation"]}
    checks = {row["check_id"]: row for row in value["freeze_check_reconciliation"]}
    exports["support_local_classical_bv_q2"].update({
        "evidence": list(dict.fromkeys([*exports["support_local_classical_bv_q2"]["evidence"], classical["result_id"], obstruction["result_id"]])),
        "established": "The candidate q2 is exact and internally cyclic, but an authoritative source channel Omega(f_hat,q2(v,v))=-1 differs from candidate zero. Literal and linear-shear identity are refuted.",
        "remaining_for_gate_a": "Import the quadratic nonlinear auxiliary-elimination/cyclic L-infinity map and replay the complete source q2 pullback, or import the full authoritative q2 ledger directly.",
        "boundary": "The exact mismatch rejects the candidate as a literal source import; it does not reject nonlinear equivalence or invalidate the candidate algebra.",
    })
    for check_id in ("q1_q2_arity_two_nilpotency", "q2_cyclic_compatibility", "D_q2_derivation"):
        row = checks[check_id]
        row["evidence"] = list(dict.fromkeys([*row["evidence"], obstruction["result_id"]]))
        row["remaining_for_gate_a"] = "Transport and independently replay this identity under a source-certified nonlinear auxiliary-elimination/cyclic L-infinity map."
        row["boundary"] = "The candidate identity remains exact, but it is not an authoritative source-theory freeze check after the nonzero auxiliary cubic mismatch."
    value["required_hash_disposition"]["q2_hash"].update({
        "accepted": None,
        "candidate_scope": "LITERAL_SOURCE_IDENTITY_REFUTED_NONLINEAR_EQUIVALENCE_OPEN",
    })
    for item in value["minimal_missing_bundle"]:
        if item["id"] == "M2_STRICT_Q2_D":
            item["object"] = "Construct a source-certified nonlinear auxiliary-elimination or cyclic L-infinity map. Its first quadratic component must reproduce Omega(f_hat,q2(v,v))=-1; then replay full q2/q3 pullback, cyclicity and D-equivariance before accepting hashes."
            item["unlocks"] = ["authoritative source-equivalent full-carrier q2/q3", "authoritative D_q2 and D_q3 derivations", "accepted nonlinear common-snapshot hashes"]
    value["gate_disposition"].update({
        "claim_state": "CLASSICAL_IMPORT_LINEAR_THEORY_IDENTITY_REFUTED_NONLINEAR_EQUIVALENCE_OPEN",
        "same_theory_receiver_verified_scoped": 11,
        "freeze_checks_receiver_verified_scoped": 8,
        "freeze_checks_supporting_evidence_only": 1,
        "freeze_checks_blocked": 1,
        "accepted_common_snapshot_hashes": 0,
    })
    value["m2_minimal_resolution"].update({
        "remaining": "Minimal q2/q3 and their exact trivial 386-row stabilizations remain valid constructions. Literal source identity is refuted; a nonlinear auxiliary-elimination/cyclic L-infinity map and source pullback replay remain open.",
        "boundary": "A source/candidate mismatch in one auxiliary cubic channel prevents hash acceptance but does not constitute a no-go for nonlinear equivalence.",
    })
    comparison = obstruction["exact_channel_comparison"]
    disposition = obstruction["theory_identity_disposition"]
    value["m2_theory_identity_obstruction"] = {
        "status": "LITERAL_AND_LINEAR_IDENTITY_REFUTED_NONLINEAR_EQUIVALENCE_OPEN",
        "classical_evidence": classical["result_id"],
        "receiver_evidence": obstruction["result_id"],
        "carrier_rows": obstruction["scope"]["carrier_rows"],
        "cyclic_form_channel": comparison["cyclic_form_channel"],
        "source_value": comparison["source_ordinary_derivative_value"],
        "candidate_value": comparison["candidate_trivial_stabilization_value"],
        "defect": comparison["source_minus_candidate_defect"],
        "candidate_internal_identities_preserved": disposition["candidate_internal_q1_q2_and_cyclicity_certificates_preserved"],
        "nonlinear_equivalence_may_exist": disposition["nonlinear_canonical_or_L_infinity_equivalence_may_exist"],
        "nonlinear_equivalence_constructed": disposition["nonlinear_equivalence_constructed"],
        "nonlinear_equivalence_obstructed": False,
        "first_required_correction": disposition["first_required_correction"],
    }
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(V7.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(V7), "role": "immutable Gate-A V7 predecessor"},
        {"path": str(CLASSICAL.relative_to(ROOT)), "result_or_artifact_id": classical["result_id"], "sha256": sha(CLASSICAL), "role": "authoritative auxiliary cubic source export"},
        {"path": str(OBSTRUCTION.relative_to(ROOT)), "result_or_artifact_id": obstruction["result_id"], "sha256": sha(OBSTRUCTION), "role": "independent source/candidate theory-identity comparison"},
    ]
    drift = []
    for source in previous["provenance"]["inputs"]:
        path = ROOT / source["path"]
        current = sha(path) if path.is_file() else None
        if current != source["sha256"]:
            drift.append({"path": source["path"], "historical_v7_sha256": source["sha256"], "current_worktree_sha256": current, "status": "RECORDED_NOT_SILENTLY_REBOUND", "disposition": "V7 remains content-pinned; current bytes are not substituted without successor replay."})
    value["transitive_provenance_drift"] = {"files_checked": len(previous["provenance"]["inputs"]), "drifted_files": len(drift), "status": "DRIFT_RECORDED_GATE_REMAINS_FAIL_CLOSED", "entries": drift}
    value["claim_flags"].update({
        "STRICT_386_LITERAL_TRIVIAL_STABILIZATION_IDENTITY_REFUTED": True,
        "STRICT_386_LINEAR_SHEAR_THEORY_IDENTITY_REFUTED": True,
        "STRICT_386_CANDIDATE_INTERNAL_IDENTITIES_PRESERVED": True,
        "STRICT_386_NONLINEAR_EQUIVALENCE_MAY_EXIST": True,
        "STRICT_386_NONLINEAR_EQUIVALENCE_CONSTRUCTED": False,
        "STRICT_386_NONLINEAR_EQUIVALENCE_OBSTRUCTED": False,
        "STRICT_386_CANDIDATE_THEORY_IDENTITY": False,
        "STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q2": False,
        "STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q3": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([*previous["does_not_establish"], "nonexistence of a nonlinear auxiliary-elimination or cyclic L-infinity equivalence", "that the internally certified candidate q1/q2/q3 identities are false", "an authoritative full-carrier q2/q3 hash, causal lambda-squared source closure, Hadamard data, or QME restoration"]))
    value["next_gate"] = "Construct the quadratic auxiliary-elimination/cyclic L-infinity map demanded by the exact f_hat-v-v mismatch. Import it from the classical programme, independently replay its source q2/q3 pullback and cyclicity/D identities, and only then reconsider q2/q3 common-snapshot hashes. M1 and M3-M6 remain independent blockers."
    value["independent_checker"] = {"path": "quantum-weyl/classical_import/check_classical_import_gate_v8_reconciliation.py", "checks": ["V7 predecessor and exact obstruction pins", "twenty-export and ten-check preservation", "-1 versus 0 theory-identity witness", "candidate identities preserved", "nonlinear-equivalence no-go firewall", "zero accepted hashes and Gate-A lifecycle firewall", "transitive drift recorded without rebinding"], "expected_digest": ""}
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    p = value["m2_theory_identity_obstruction"]
    return f"""# Classical import Gate-A reconciliation v8

**Result:** `{value['result_id']}`

**Lifecycle:** `{value['lifecycle']}`

**Gate A:** `{value['gate_disposition']['gate_a_status']}`

## Outcome

The literal theory-identity question is decided.  In `{p['cyclic_form_channel']}`
the authoritative source gives **{p['source_value']}**, the trivial stabilization
gives **{p['candidate_value']}**, and the defect is **{p['defect']}**.

This rejects zero-extension plus the recorded linear shear as an authoritative
nonlinear import.  It preserves the candidate identities and does not obstruct
nonlinear equivalence.  The next M2 object is the quadratic auxiliary-elimination
or cyclic L-infinity map whose pullback supplies the missing channel.

Gate A remains fail closed with **{value['gate_disposition']['accepted_common_snapshot_hashes']}**
accepted hashes.  M1 and M3--M6 remain independent blockers.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v8_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v8_reconciliation.py
python3 quantum-weyl/classical_import/verify_classical_import_gate_v8_reconciliation.py
python3 -m unittest quantum-weyl.classical_import.tests.test_classical_import_gate_v8_reconciliation
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("CLASSICAL_IMPORT_GATE_V8_RECONCILIATION: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale))); return bool(stale)
    for path, content in outputs: path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V8_RECONCILIATION: wrote certificate and report"); return 0


if __name__ == "__main__": raise SystemExit(main())
