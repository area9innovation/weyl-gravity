#!/usr/bin/env python3
"""Build Gate-A v6 after strict full-D and D/q1 certification."""

from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
V5 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V5_RECONCILIATION.json"
FULL_D = HERE / "certificates/STRICT_386_FULL_D_ACTION_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V6_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V6.md"


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    payload = {
        key: value[key]
        for key in (
            "standalone_history_replay", "status_vocabulary", "export_reconciliation",
            "freeze_check_reconciliation", "required_hash_disposition", "minimal_missing_bundle",
            "gate_disposition", "m3_scoped_resolution", "m2_minimal_resolution",
            "m2_d_resolution", "m4_minimal_resolution", "transitive_provenance_drift",
        )
    }
    return sha256(dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    previous, full_d = (loads(path.read_text()) for path in (V5, FULL_D))
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V5_RECONCILIATION" or previous.get("gate_disposition", {}).get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("V5 predecessor drift")
    flags = full_d.get("claim_flags", {})
    if not all(flags.get(name) is True for name in (
        "STRICT_386_FULL_LOCAL_D_ACTION_CERTIFIED", "STRICT_386_D_Q1_COMMUTATOR_REPLAYED",
        "STRICT_386_D_FORMAL_SKEW_ADJOINT_REPLAYED", "STRICT_386_UNARY_CAUSAL_D_SCOPED_SNAPSHOT_ACCEPTED",
    )) or flags.get("CLASSICAL_IMPORT_GATE_PASSED") is not False:
        raise ValueError("strict D certificate unavailable or over-promoted")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v6-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V6_RECONCILIATION",
        "result_state": "FULL_D_AND_D_Q1_SCOPED_CERTIFIED_FULL_CARRIER_Q2_OPEN",
        "created": "2026-08-15",
        "repository_base_commit": "3fa9c8cc37040960afbc5f6de7a0260389c2bd66",
        "question": "After serializing the real compact-cylinder flow on every row of the accepted strict 386-row unary-causal graph carrier and independently replaying its q1 commutator and formal skew adjoint, which Gate-A M2 obligations are now receiver-verified, what remains for q2, and does Gate A pass?",
        "answer": "The D half of M2 is now exact on the same strict 386-row graph carrier as q1, the local SDR, transported suspension and represented Green actions. The selected real generator is T=Lie_{partial_t}; the compact Hermitian convention is D=iT after complexification. A 386-entry first-order rational component table covers all twenty-two blocks and every degree. Independent left and right sparse compositions inspect all twenty-seven graph-q1 tables, seventy combined derivative multiindices and 4,374 rational coefficients and find [T,q1]=0 with no defects. Formal skew-adjointness is replayed against all 410 ordered odd-pairing entries. Therefore local_D_action_on_bv_generators and D_q1_commutator_zero become RECEIVER_VERIFIED_SCOPED for the strict theory; the Berger rows remain only historical controls. Gate A nevertheless remains FAIL_CLOSED. The full-carrier strict q2 extension and D/q2 derivation identity are absent, so M2 is narrowed rather than closed. The new D hash is a scoped candidate bound to the fourteen-object unary-causal-D snapshot, not an accepted Gate-A top-level hash. M1, M3, M4, M5 and M6 also remain unresolved. No Hadamard, renormalized-product, QME, residual-transfer or Lorentzian quantum lifecycle state is promoted.",
        "supersedes_for_current_status": previous["result_id"],
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V6.md",
    })

    exports = {row["export_id"]: row for row in value["export_reconciliation"]}
    checks = {row["check_id"]: row for row in value["freeze_check_reconciliation"]}
    exports["local_D_action_on_bv_generators"].update({
        "status": "RECEIVER_VERIFIED_SCOPED",
        "evidence": [full_d["result_id"]],
        "established": "The real cylinder flow T=Lie_partial_t is serialized as 386 exact first-order diagonal entries on all strict graph rows and is formally skew against the complete 410-entry odd pairing.",
        "remaining_for_gate_a": "Bind the full-carrier strict q2 extension and D/q2 derivation replay to this fourteen-object unary-causal-D snapshot, then include it in the complete twenty-export Gate-A manifest.",
        "boundary": "A local D action and unary equivariance do not construct q2, a D-Cartan homotopy, a physical D quotient, or an accepted Gate-A top-level hash.",
    })
    exports["support_local_classical_bv_q2"].update({
        "remaining_for_gate_a": "Extend translated q2 to every retained nonminimal, generalized-auxiliary and graph interaction row, bind it to the certified full D action on one carrier, and replay D/q2.",
        "boundary": "The complete support-local q2 export remains open because the portable six-row minimal result has not been extended to all 386 graph rows.",
    })
    checks["D_q1_commutator_zero"].update({
        "status": "RECEIVER_VERIFIED_SCOPED",
        "evidence": [full_d["result_id"]],
        "established": "Independent left/right temporal-index compositions agree for all 4,374 graph-q1 rational coefficients, so [T,q1]=0 on every one of the 386 strict rows.",
        "remaining_for_gate_a": "Retain this exact replay while binding full-carrier q2, residual maps and all seven top-level hashes into the complete Gate-A snapshot.",
        "boundary": "Unary cylinder-flow equivariance does not imply the nonlinear D/q2 derivation identity or decide whether the residual D symmetry is proper gauge.",
    })
    checks["q1_q2_arity_two_nilpotency"].update({
        "boundary": "The scoped minimal q1/q2 theorem and the full-carrier D/q1 theorem inhabit compatible strict conventions, but the q2 payload itself is not yet extended to every graph row.",
    })

    hashes = value["required_hash_disposition"]
    hashes["D_action_hash"].update({
        "accepted": None,
        "candidate": full_d["canonical_hashes"]["D_action_sha256"],
        "candidate_scope": "STRICT_386_UNARY_CAUSAL_D_SCOPED_NOT_GATE_A_COMMON_MANIFEST",
    })
    for item in value["minimal_missing_bundle"]:
        if item["id"] == "M2_STRICT_Q2_D":
            item["object"] = "Extend the canonically translated strict q2 payload to every required nonminimal, generalized-auxiliary and graph row on the certified 386-row unary-causal-D snapshot; then replay D/q2 and full-carrier q2 cyclicity. The full D action and [D,q1] are no longer missing."
            item["unlocks"] = ["full-carrier support-local q2 export", "D_q2_derivation", "full-carrier q2 cyclicity"]

    value["gate_disposition"].update({
        "claim_state": "CLASSICAL_IMPORT_STRICT_FULL_D_AND_D_Q1_SCOPED_CERTIFIED_FULL_Q2_OPEN",
        "same_theory_receiver_verified_scoped": 11,
        "different_theory_controls": 0,
        "freeze_checks_receiver_verified_scoped": 8,
        "freeze_checks_different_theory": 1,
        "accepted_common_snapshot_hashes": 0,
    })
    value["m2_minimal_resolution"].update({
        "remaining": "The minimal q1/q2 and cyclic convention are certified, and full-carrier D/[D,q1] are separately certified on the compatible strict graph snapshot. Full-carrier q2, D/q2 and accepted Gate hashes remain open.",
        "boundary": "The minimal q2 theorem and full-carrier unary D theorem do not compose into a full M2 result until q2 is extended to the same 386 rows and the nonlinear identity is replayed.",
    })
    value["m2_d_resolution"] = {
        "status": "STRICT_386_FULL_D_AND_D_Q1_RECEIVER_VERIFIED_SCOPED",
        "evidence": full_d["result_id"],
        "carrier_rows": full_d["scope"]["carrier_rows"],
        "component_blocks": full_d["scope"]["component_blocks"],
        "D_component_coefficients": full_d["D_action"]["nonzero_coefficients"],
        "q1_operator_tables_checked": full_d["exact_replay"]["q1_operator_tables_checked"],
        "q1_rational_coefficients_checked": full_d["exact_replay"]["q1_rational_coefficients_checked"],
        "D_q1_commutator_defects": full_d["exact_replay"]["D_q1_commutator_defects"],
        "pairing_entries_checked": full_d["exact_replay"]["formal_skew_adjoint_pairing_entries_checked"],
        "scoped_snapshot_hashes": full_d["extended_common_snapshot"]["accepted_object_hashes"],
        "D_action_sha256": full_d["canonical_hashes"]["D_action_sha256"],
        "remaining": "Extend q2 to all required 386-row sectors and replay D/q2 plus full-carrier q2 cyclicity on this exact snapshot.",
        "boundary": "This is a support-local unary equivariance result. It is neither a D-Cartan homotopy nor a physical charge/quotient decision and accepts no Gate-A top-level hash.",
    }
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(V5.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": file_hash(V5), "role": "immutable Gate-A V5 predecessor"},
        {"path": str(FULL_D.relative_to(ROOT)), "result_or_artifact_id": full_d["result_id"], "sha256": file_hash(FULL_D), "role": "strict 386-row full D action and D/q1 receiver replay"},
    ]
    drift = []
    for source in previous["provenance"]["inputs"]:
        path = ROOT / source["path"]
        current = file_hash(path) if path.is_file() else None
        if current != source["sha256"]:
            drift.append({
                "path": source["path"],
                "historical_v5_sha256": source["sha256"],
                "current_worktree_sha256": current,
                "status": "RECORDED_NOT_SILENTLY_REBOUND",
                "disposition": "V5 remains the content-pinned authority for its historical claim; the changed current file is not substituted without an independent successor replay.",
            })
    value["transitive_provenance_drift"] = {
        "files_checked": len(previous["provenance"]["inputs"]),
        "drifted_files": len(drift),
        "status": "DRIFT_RECORDED_GATE_REMAINS_FAIL_CLOSED",
        "entries": drift,
    }
    value["claim_flags"].update({
        "STRICT_386_FULL_LOCAL_D_ACTION_SCOPED_REPLAY": True,
        "STRICT_386_D_Q1_COMMUTATOR_SCOPED_REPLAY": True,
        "STRICT_386_D_FORMAL_SKEW_ADJOINT_SCOPED_REPLAY": True,
        "STRICT_386_FULL_CARRIER_Q2": False,
        "STRICT_386_D_Q2_DERIVATION": False,
    })
    value["does_not_establish"] = [
        *previous["does_not_establish"],
        "that the strict full-carrier q2 or D/q2 identity follows from the unary D/q1 replay",
        "that the cylinder generator D is proper gauge rather than charged or sector-dependent",
    ]
    value["next_gate"] = "Use STRICT_386_FULL_D_ACTION_V1 as the fixed local cylinder-flow action on the accepted unary-causal graph snapshot. Transport or extend the canonical strict six-row q2 convention to every required nonminimal, generalized-auxiliary and graph row without importing Berger interactions. Independently replay q1q2, D/q2, Koszul symmetry, row completeness and q2 cyclicity on those exact 386-row bytes. Only then may M2 or the D_action/q2 candidate hashes be reconsidered for the complete twenty-export Gate-A manifest. M1, M3, M4, M5 and M6 remain independent and must still close before Gate A can pass; no causal quantum or QME lifecycle promotion is authorized."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v6_reconciliation.py",
        "checks": [
            "V5 predecessor and strict-D pins", "twenty-export and ten-check order",
            "single strict D export scoped promotion", "single D/q1 check scoped promotion",
            "386-row/4,374-coefficient crosswalk", "D candidate hash remains unaccepted",
            "M2 narrowed only to full-carrier q2 and D/q2", "all other missing families preserved",
            "transitive predecessor drift recorded without rebinding", "zero accepted common hashes",
            "Gate-A fail-closed counts", "quantum lifecycle firewall",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    m2 = value["m2_d_resolution"]
    drift = value["transitive_provenance_drift"]
    d_export = next(row for row in value["export_reconciliation"] if row["export_id"] == "local_D_action_on_bv_generators")
    d_check = next(row for row in value["freeze_check_reconciliation"] if row["check_id"] == "D_q1_commutator_zero")
    return f"""# Classical import Gate-A reconciliation v6

**Result:** `{value['result_id']}`

**Lifecycle:** `{value['lifecycle']}`

**Gate A:** `{value['gate_disposition']['gate_a_status']}`

## Outcome

The real cylinder flow `T=Lie_partial_t` is now exact on all
**{m2['carrier_rows']}** rows of the strict graph carrier.  The compact
Hermitian convention is `D=iT`; no Berger helical generator or finite mode
matrix is imported.  The component table has **{m2['D_component_coefficients']}**
first-order entries across **{m2['component_blocks']}** blocks.

## Scoped promotions

| Obligation | Status | Established | Still required |
|---|---|---|---|
| `local_D_action_on_bv_generators` | `{d_export['status']}` | {d_export['established']} | {d_export['remaining_for_gate_a']} |
| `D_q1_commutator_zero` | `{d_check['status']}` | {d_check['established']} | {d_check['remaining_for_gate_a']} |

The receiver checked **{m2['q1_operator_tables_checked']}** graph-q1 tables and
**{m2['q1_rational_coefficients_checked']}** rational coefficients, finding
**{m2['D_q1_commutator_defects']}** commutator defects.  It also checked
**{m2['pairing_entries_checked']}** ordered pairing entries.  The extended
scoped snapshot now binds **{m2['scoped_snapshot_hashes']}** object hashes.

## What remains

M2 is narrowed, not closed.  The full D action and `[D,q1]` are no longer
missing; full-carrier strict `q2`, `D/q2`, and full-carrier q2 cyclicity are.
The D hash is recorded as a scoped candidate but remains unaccepted because
the complete twenty-export Gate-A manifest does not yet exist.  M1, M3, M4,
M5 and M6 remain independent blockers.

## Provenance drift

The V5 predecessor remains content-pinned.  A current-worktree audit found
**{drift['drifted_files']}** changed files among its **{drift['files_checked']}**
transitive provenance records.  Their historical and current hashes are
recorded in the machine certificate; none is silently rebound or treated as
an independent replay.

## Gate verdict

Gate A remains fail closed with zero accepted common snapshot hashes.  This
result does not construct a D-Cartan homotopy, decide the physical D charge,
or authorize Hadamard, renormalized-product, QME, residual-transfer or
Lorentzian quantum claims.

## Reproduction

```bash
python3 quantum-weyl/classical_import/build_classical_import_gate_v6_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v6_reconciliation.py
python3 quantum-weyl/classical_import/verify_classical_import_gate_v6_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v6_reconciliation.py
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
        print("CLASSICAL_IMPORT_GATE_V6_RECONCILIATION: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V6_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
