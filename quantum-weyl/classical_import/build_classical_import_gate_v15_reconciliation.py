#!/usr/bin/env python3
"""Build Gate-A v15 after authoritative common q2/q3 source assembly."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
V14 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V14_RECONCILIATION.json"
Q2 = HERE / "certificates/STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.json"
Q3 = HERE / "certificates/STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1.json"
AUXILIARY = HERE / "certificates/STRICT_386_SHIFTED_MASS_BV_Q3_LIFT_V1.json"
QUARTIC = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V15_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V15.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "export_reconciliation", "freeze_check_reconciliation", "required_hash_disposition",
        "minimal_missing_bundle", "gate_disposition", "m2_minimal_resolution",
        "m2_shifted_cubic_inventory_resolution", "m2_diff_auxiliary_resolution",
        "m2_nonlinear_ghost_manifest_resolution", "m2_source_q2_assembly_resolution",
        "m2_source_q3_assembly_resolution", "transitive_provenance_drift",
    )
    payload = {key: value[key] for key in keys}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    previous, q2, q3, auxiliary, quartic = (json.loads(path.read_text()) for path in (V14, Q2, Q3, AUXILIARY, QUARTIC))
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V14_RECONCILIATION" or previous["gate_disposition"]["gate_a_status"] != "FAIL_CLOSED":
        raise ValueError("Gate V14 predecessor drift")
    if not q2["claim_flags"]["FULL_SHIFTED_SOURCE_Q2_COMMON_UNION_ASSEMBLED"]:
        raise ValueError("accepted common q2 unavailable")
    required_q3_flags = (
        "FULL_SHIFTED_SOURCE_Q3_COMMON_UNION_ASSEMBLED", "FULL_386_ARITY_THREE_IDENTITY_REPLAYED",
        "FULL_386_Q3_CYCLICITY_REPLAYED_MOD_D", "FULL_386_D_Q3_DERIVATION_REPLAYED",
        "FULL_SOURCE_Q3_ASSEMBLED",
    )
    if any(q3["claim_flags"].get(flag) is not True for flag in required_q3_flags):
        raise ValueError("authoritative common q3 snapshot unavailable")
    if auxiliary["exact_replay"]["cyclicity_defects"] or quartic["exact_replay"]["mixed_conformal_recursion_defects"]:
        raise ValueError("auxiliary q3 independent replay unavailable")
    if q3["source_q3_snapshot"]["accepted_q2_snapshot_sha256"] != q2["source_q2_snapshot"]["sha256"]:
        raise ValueError("q2/q3 common-byte link drift")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v15-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V15_RECONCILIATION",
        "result_state": "SOURCE_Q2_Q3_ACCEPTED_ARITY_THREE_ZERO_SIX_HASHES_AND_FINAL_FREEZE_OPEN_GATE_FAIL_CLOSED",
        "created": "2026-08-16",
        "question": "Does the authoritative common source q3 assembly close Gate A?",
        "answer": "It closes the nonlinear M2 source-operation obligation, not Gate A. The accepted q2 snapshot is now linked to a complete q3 snapshot containing the minimal Bach natural operator and 5,952 exact auxiliary coefficients. The complete arity-three identity, q3 cyclicity modulo horizontal boundary, and stationary D/q3 derivation have zero defects in split and graph coordinates. Six top-level hashes and the final common cyclic contraction remain open, so Gate A stays fail closed.",
        "supersedes_for_current_status": previous["result_id"],
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V15.md",
    })
    exports = {row["export_id"]: row for row in value["export_reconciliation"]}
    nonlinear = exports["support_local_classical_bv_q2"]
    nonlinear.update({
        "status": "RECEIVER_VERIFIED_SCOPED",
        "evidence": list(dict.fromkeys([*nonlinear["evidence"], q3["result_id"], auxiliary["result_id"], quartic["result_id"]])),
        "established": "The common nonlinear source snapshot now includes complete authoritative q2 and q3, exact graph transport, the full arity-three Taylor identity, q2/q3 cyclicity, and stationary D derivations.",
        "remaining_for_gate_a": "Reconcile the six unaccepted field/differential/D/residual/pairing/representative hashes and replay the final full cyclic contraction on one frozen manifest.",
        "boundary": "Local q2/q3 closure does not itself supply the residual payload, common freeze, Green compatibility, Hadamard data, or QME.",
    })
    value["minimal_missing_bundle"] = [item for item in value["minimal_missing_bundle"] if item["id"] != "M2_STRICT_Q2_D"]
    value["gate_disposition"].update({
        "claim_state": "CLASSICAL_IMPORT_SOURCE_Q2_Q3_ACCEPTED_SIX_HASHES_AND_FINAL_CONTRACTION_OPEN",
        "accepted_common_snapshot_hashes": 1,
        "gate_a_status": "FAIL_CLOSED",
        "publishable_quantum_results_allowed_by_gate_a": False,
    })
    value["m2_minimal_resolution"].update({
        "status": "CLOSED_AUTHORITATIVE_COMMON_Q2_Q3_ARITY_THREE",
        "remaining": "No source-operation Taylor coefficient remains at q2/q3. The six other top-level hashes and final common cyclic contraction are separate Gate-A obligations.",
        "boundary": "This local Taylor closure does not establish causal Green compatibility or an accepted freeze.",
    })
    value["m2_shifted_cubic_inventory_resolution"].update({
        "status": "SHIFTED_SOURCE_Q2_Q3_FAMILY_CENSUS_COMPLETE_AT_ARITY_THREE",
        "source_q3_family_count": q3["family_census"]["total_source_q3_families"],
        "auxiliary_ordered_q3_component_coefficients": q3["source_q3_snapshot"]["auxiliary_ordered_component_coefficients"],
        "complete_source_q2_q3_pullback_replayed": True,
    })
    value["m2_source_q2_assembly_resolution"]["full_source_q3_assembled"] = True
    value["m2_source_q3_assembly_resolution"] = {
        "status": "ACCEPTED_ARITY_THREE_COMMON_SNAPSHOT",
        "evidence": q3["result_id"],
        "accepted_q2_sha256": q2["source_q2_snapshot"]["sha256"],
        "accepted_q3_sha256": q3["source_q3_snapshot"]["sha256"],
        "minimal_natural_operator_components": q3["source_q3_snapshot"]["minimal_natural_operator_components"],
        "auxiliary_ordered_component_coefficients": q3["source_q3_snapshot"]["auxiliary_ordered_component_coefficients"],
        "source_q3_family_count": q3["family_census"]["total_source_q3_families"],
        "graph_block_quadruples": q3["graph_transport"]["graph_block_quadruples"],
        "arity_three_defects": q3["arity_three_replay"]["graph_386_arity_three_defects"],
        "cyclicity_defects_mod_d": q3["q3_cyclicity_replay"]["graph_386_q3_cyclicity_defects_mod_d"],
        "D_q3_defects": q3["D_q3_replay"]["graph_D_q3_derivation_defects"],
        "gate_a_status": "FAIL_CLOSED",
    }
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(V14.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(V14), "role": "immutable Gate-A V14 predecessor"},
        {"path": str(Q3.relative_to(ROOT)), "result_or_artifact_id": q3["result_id"], "sha256": sha(Q3), "role": "accepted common source-q3 snapshot and identities"},
        {"path": str(AUXILIARY.relative_to(ROOT)), "result_or_artifact_id": auxiliary["result_id"], "sha256": sha(AUXILIARY), "role": "independently replayed paired auxiliary q3 ledger"},
        {"path": str(QUARTIC.relative_to(ROOT)), "result_or_artifact_id": quartic["result_id"], "sha256": sha(QUARTIC), "role": "authoritative classical fourth variation and conformal Ward rail"},
    ]
    drift = []
    for source in previous["provenance"]["inputs"]:
        path = ROOT / source["path"]
        current = sha(path) if path.is_file() else None
        if current != source["sha256"]:
            drift.append({"path": source["path"], "historical_v14_sha256": source["sha256"], "current_worktree_sha256": current, "status": "RECORDED_NOT_SILENTLY_REBOUND"})
    value["transitive_provenance_drift"] = {
        "files_checked": len(previous["provenance"]["inputs"]), "drifted_files": len(drift),
        "status": "DRIFT_RECORDED_GATE_REMAINS_FAIL_CLOSED", "entries": drift,
    }
    value["claim_flags"].update({
        "STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q3": True,
        "STRICT_386_FULL_SOURCE_Q3_PULLBACK_REPLAYED": True,
        "STRICT_386_FULL_ARITY_THREE_IDENTITY_REPLAYED": True,
        "STRICT_386_FULL_Q3_CYCLICITY_REPLAYED_MOD_D": True,
        "STRICT_386_FULL_D_Q3_DERIVATION_REPLAYED": True,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "QME_RESTORED": False,
    })
    value["does_not_establish"] = [
        item for item in previous["does_not_establish"]
        if "metric-dependent auxiliary q3" not in item and "full source q3" not in item and "arity-three" not in item
    ]
    value["does_not_establish"] = list(dict.fromkeys([
        *value["does_not_establish"],
        "the six remaining top-level Gate-A hashes or the final common cyclic contraction",
        "q2/q3 compatibility with an advanced or retarded Green homotopy or causal lambda-squared closure",
        "Hadamard data, renormalized Lorentzian products, QME restoration, or residual transfer",
    ]))
    value["next_gate"] = "Build the common strict freeze manifest for the field dictionary, differential, D action, residual SDR, pairing, exact residual basis and centered representatives; accept the remaining six hashes and replay the final cyclic contraction before composing q2/q3 with Green homotopies."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v15_reconciliation.py",
        "checks": ["V14 and q2/q3 common-byte pins", "5,952-entry auxiliary q3 ledger", "two-family q3 census", "zero arity-three/cyclicity/D-q3 defects", "M2 removal", "six-hash and final-contraction firewalls"],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    q3 = value["m2_source_q3_assembly_resolution"]
    return f"""# Classical import Gate-A reconciliation v15

**Result:** `{value['result_id']}`

**Dependencies:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

**Gate A:** `{value['gate_disposition']['gate_a_status']}`

The nonlinear source-operation obligation M2 is now closed through arity
three.  The accepted q3 snapshot `{q3['accepted_q3_sha256']}` contains the
minimal Bach natural operator and **{q3['auxiliary_ordered_component_coefficients']}**
ordered auxiliary coefficients in {q3['source_q3_family_count']} exhaustive
source families.  Its graph envelope has {q3['graph_block_quadruples']} block
quadruples.

The graph-coordinate arity-three, q3 cyclicity modulo horizontal boundary,
and `D/q3` defect counts are **{q3['arity_three_defects']} /
{q3['cyclicity_defects_mod_d']} / {q3['D_q3_defects']}**.  The q3 snapshot is
content-linked to the already accepted q2 snapshot; M2 is therefore removed
from the current missing bundle.

Gate A remains fail closed.  Only one of seven top-level hashes is accepted;
the other six and the final common cyclic contraction still need one frozen
strict snapshot.  No Green, Hadamard, renormalization, or QME claim is
promoted.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v15_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v15_reconciliation.py
python3 quantum-weyl/classical_import/verify_classical_import_gate_v15_reconciliation.py
python3 -m unittest quantum-weyl.classical_import.tests.test_classical_import_gate_v15_reconciliation
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("CLASSICAL_IMPORT_GATE_V15_RECONCILIATION: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V15_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
