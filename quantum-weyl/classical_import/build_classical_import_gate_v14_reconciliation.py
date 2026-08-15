#!/usr/bin/env python3
"""Build Gate-A v14 after the common 386-row source-q2 assembly."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
V13 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V13_RECONCILIATION.json"
ASSEMBLY = HERE / "certificates/STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.json"
DIFF_V2 = HERE / "certificates/STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V2.json"
MASS = HERE / "certificates/STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V14_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V14.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = ("export_reconciliation", "freeze_check_reconciliation", "required_hash_disposition", "minimal_missing_bundle", "gate_disposition", "m2_minimal_resolution", "m2_shifted_cubic_inventory_resolution", "m2_diff_auxiliary_resolution", "m2_nonlinear_ghost_manifest_resolution", "m2_source_q2_assembly_resolution", "transitive_provenance_drift")
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    previous, assembly, diff, mass = (json.loads(path.read_text()) for path in (V13, ASSEMBLY, DIFF_V2, MASS))
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V13_RECONCILIATION" or previous["gate_disposition"]["gate_a_status"] != "FAIL_CLOSED":
        raise ValueError("Gate V13 predecessor drift")
    if assembly.get("result_id") != "STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1" or not assembly["claim_flags"]["FULL_SHIFTED_SOURCE_Q2_COMMON_UNION_ASSEMBLED"]:
        raise ValueError("common source-q2 assembly unavailable")
    if assembly["claim_flags"]["FULL_SOURCE_Q3_ASSEMBLED"] or assembly["q3_boundary"]["Gate_A_disposition"] != "FAIL_CLOSED":
        raise ValueError("source-q3 boundary drift")
    if diff["canonical_sign_repair"]["unrepaired_q1_q2_nonzero_coefficients"] != 336 or diff["canonical_sign_repair"]["repaired_q1_q2_nonzero_coefficients"] != 0:
        raise ValueError("auxiliary canonical sign repair unavailable")
    if mass["exact_replay"]["cyclicity_defects"] != 0:
        raise ValueError("shifted-mass q2 cyclicity unavailable")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v14-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V14_RECONCILIATION",
        "result_state": "SOURCE_Q2_COMMON_HASH_ACCEPTED_IDENTITIES_ZERO_AUXILIARY_Q3_AND_FREEZE_OBJECTS_OPEN_GATE_FAIL_CLOSED",
        "created": "2026-08-15",
        "question": "Does the common shifted-source q2 assembly close Gate A?",
        "answer": "It closes M2 at arity two, not Gate A. The 22 ordered minimal operations and 2,064 auxiliary component coefficients now form one content-addressed 386-row source-q2 snapshot. Exact replay gives zero q1/q2, cyclicity and stationary D/q2 defects in split and graph coordinates. Gate V14 accepts that q2 hash. The metric-dependent auxiliary q3 is not assembled, six other top-level hashes are still unaccepted, and the final common cyclic contraction remains blocked; Gate A therefore remains fail closed.",
        "supersedes_for_current_status": previous["result_id"],
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V14.md",
    })
    exports = {row["export_id"]: row for row in value["export_reconciliation"]}
    checks = {row["check_id"]: row for row in value["freeze_check_reconciliation"]}
    q2 = exports["support_local_classical_bv_q2"]
    q2.update({
        "status": "RECEIVER_VERIFIED_SCOPED",
        "evidence": list(dict.fromkeys([*q2["evidence"], diff["result_id"], mass["result_id"], assembly["result_id"]])),
        "established": "One authoritative shifted-source q2 snapshot now binds the complete minimal operation, four exhaustive shifted-source auxiliary families, zero extension on the receiver-added split cone, and exact BV-canonical graph transport.",
        "remaining_for_gate_a": "Assemble the metric-dependent auxiliary q3 and reconcile the remaining six top-level hashes and final cyclic contraction on one freeze snapshot.",
        "boundary": "A complete arity-two source q2 does not supply auxiliary q3, q2/Green compatibility, or a complete Gate-A freeze.",
    })
    descriptions = {
        "q1_q2_arity_two_nilpotency": "The minimal 18-channel/51-path theorem and all 926 auxiliary component channels combine with zero residual; exact shear conjugation gives zero graph-coordinate defects.",
        "q2_cyclic_compatibility": "Minimal cyclicity, 3,000 shifted-mass equalities and the translated 264-term auxiliary Diff Hamiltonian reconstruction combine with zero defects and are preserved by the BV-canonical shear.",
        "D_q2_derivation": "All sixteen shifted-source q2 families are stationary tensor-natural on the unit cylinder; the exact shear commutes with D, so the split and graph derivation defects vanish.",
    }
    for check_id, established in descriptions.items():
        row = checks[check_id]
        row.update({
            "status": "RECEIVER_VERIFIED_SCOPED",
            "evidence": list(dict.fromkeys([*row["evidence"], diff["result_id"], mass["result_id"], assembly["result_id"]])),
            "established": established,
            "remaining_for_gate_a": "This identity is closed for q2; auxiliary q3, the remaining common hashes and the final full cyclic contraction remain independent obligations.",
            "boundary": "An arity-two identity replay does not promote arity three, Green compatibility, Hadamard or QME.",
        })
    q2_hash = assembly["source_q2_snapshot"]["sha256"]
    value["required_hash_disposition"]["q2_hash"] = {"accepted": q2_hash, "candidate": q2_hash, "candidate_scope": "COMMON_386_SHIFTED_SOURCE_Q2_AND_EXACT_GRAPH_DAG"}
    for item in value["minimal_missing_bundle"]:
        if item["id"] == "M2_STRICT_Q2_D":
            item["object"] = "Lift the metric-dependent shifted auxiliary quartic vertex to q3, assemble it with minimal q3, and replay arity-three/cyclicity on the accepted q2 snapshot; then reconcile the six remaining top-level hashes."
    value["gate_disposition"].update({
        "claim_state": "CLASSICAL_IMPORT_SOURCE_Q2_ACCEPTED_AUXILIARY_Q3_AND_COMMON_FREEZE_OPEN",
        "same_theory_receiver_verified_scoped": previous["gate_disposition"]["same_theory_receiver_verified_scoped"] + 1,
        "freeze_checks_receiver_verified_scoped": previous["gate_disposition"]["freeze_checks_receiver_verified_scoped"] + 1,
        "freeze_checks_supporting_evidence_only": previous["gate_disposition"]["freeze_checks_supporting_evidence_only"] - 1,
        "accepted_common_snapshot_hashes": 1,
    })
    value["m2_minimal_resolution"].update({
        "status": "ARITY_TWO_COMMON_SOURCE_Q2_ACCEPTED_AUXILIARY_Q3_OPEN",
        "remaining": "The accepted q2 hash and all three q2 identities are closed. The metric-dependent auxiliary q3 and its arity-three/cyclicity replay remain open.",
        "boundary": "Arity-two completion does not authorize arity three, Green compatibility or the freeze gate.",
    })
    value["m2_shifted_cubic_inventory_resolution"].update({
        "status": "SHIFTED_SOURCE_Q2_FOUR_AUXILIARY_FAMILIES_ASSEMBLED_AUXILIARY_Q3_OPEN",
        "source_q2_family_count": 16,
        "shifted_source_auxiliary_q2_family_count": 4,
        "type_II_coordinate_map_families_not_source_q2": 3,
        "complete_source_q2_pullback_replayed": True,
        "complete_source_q2_q3_pullback_replayed": False,
    })
    value["m2_diff_auxiliary_resolution"].update({
        "status": "CANONICAL_C_STAR_V2_REPAIR_AND_COUPLED_Q1_Q2_REPLAYED",
        "receiver_evidence_v2": diff["result_id"],
        "translated_c_star_coefficients": 704,
        "unrepaired_q1_q2_defects": 336,
        "repaired_q1_q2_defects": 0,
    })
    value["m2_nonlinear_ghost_manifest_resolution"]["full_386_source_q2_assembled"] = True
    value["m2_source_q2_assembly_resolution"] = {
        "status": "ACCEPTED_ARITY_TWO_COMMON_SNAPSHOT",
        "evidence": assembly["result_id"],
        "accepted_q2_sha256": q2_hash,
        "minimal_ordered_symbolic_components": assembly["source_q2_snapshot"]["minimal_ordered_symbolic_components"],
        "auxiliary_ordered_component_coefficients": assembly["source_q2_snapshot"]["auxiliary_ordered_component_coefficients"],
        "graph_block_triples": assembly["graph_transport"]["graph_block_triples"],
        "q1_q2_defects": assembly["q1_q2_replay"]["graph_386_q1_q2_defects"],
        "cyclicity_defects": assembly["q2_cyclicity_replay"]["graph_386_q2_cyclicity_defects"],
        "D_q2_defects": assembly["D_q2_replay"]["graph_D_q2_derivation_defects"],
        "full_source_q3_assembled": False,
    }
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(V13.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(V13), "role": "immutable Gate-A V13 predecessor"},
        {"path": str(ASSEMBLY.relative_to(ROOT)), "result_or_artifact_id": assembly["result_id"], "sha256": sha(ASSEMBLY), "role": "accepted common source-q2 snapshot and identities"},
        {"path": str(DIFF_V2.relative_to(ROOT)), "result_or_artifact_id": diff["result_id"], "sha256": sha(DIFF_V2), "role": "append-only canonical c-star repair"},
        {"path": str(MASS.relative_to(ROOT)), "result_or_artifact_id": mass["result_id"], "sha256": sha(MASS), "role": "exact cyclic shifted-mass q2 lift"},
    ]
    drift = []
    for source in previous["provenance"]["inputs"]:
        path = ROOT / source["path"]
        current = sha(path) if path.is_file() else None
        if current != source["sha256"]:
            drift.append({"path": source["path"], "historical_v13_sha256": source["sha256"], "current_worktree_sha256": current, "status": "RECORDED_NOT_SILENTLY_REBOUND"})
    value["transitive_provenance_drift"] = {"files_checked": len(previous["provenance"]["inputs"]), "drifted_files": len(drift), "status": "DRIFT_RECORDED_GATE_REMAINS_FAIL_CLOSED", "entries": drift}
    value["claim_flags"].update({
        "STRICT_386_FULL_CARRIER_Q2": True,
        "STRICT_386_D_Q2_DERIVATION": True,
        "STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q2": True,
        "STRICT_386_AUTHORITATIVE_D_Q2_DERIVATION": True,
        "STRICT_386_FULL_SOURCE_Q2_ASSEMBLED": True,
        "STRICT_386_FULL_SOURCE_Q2_PULLBACK_REPLAYED": True,
        "STRICT_386_FULL_Q1_Q2_IDENTITY_REPLAYED": True,
        "STRICT_386_FULL_Q2_CYCLICITY_REPLAYED": True,
        "STRICT_386_FULL_D_Q2_DERIVATION_REPLAYED": True,
        "STRICT_386_FULL_SOURCE_Q3_PULLBACK_REPLAYED": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "QME_RESTORED": False,
    })
    value["does_not_establish"] = [item for item in previous["does_not_establish"] if "assembled source q2/q3" not in item and "full q1/q2 identity" not in item]
    value["does_not_establish"] = list(dict.fromkeys([*value["does_not_establish"], "the metric-dependent auxiliary q3, full source q3 assembly or arity-three replay", "the six remaining top-level Gate-A hashes or the final common cyclic contraction", "q2/Green compatibility, causal lambda-squared closure, Hadamard data, QME restoration, or residual transfer"]))
    value["next_gate"] = "Compute and pair-lift the exact h-h-f_hat-f_hat quartic auxiliary action coefficient to q3, assemble it with minimal q3 on the accepted q2 snapshot, and replay arity three plus cyclicity. The six remaining hashes and M1/M3-M6 remain independent Gate-A blockers."
    value["independent_checker"] = {"path": "quantum-weyl/classical_import/check_classical_import_gate_v14_reconciliation.py", "checks": ["V13 and q2 assembly pins", "twenty-export and ten-check preservation", "accepted common q2 hash", "zero q1/q2, cyclicity and D/q2 defects", "336-to-zero append-only sign repair", "auxiliary q3 and six-hash firewalls"], "expected_digest": ""}
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    q2 = value["m2_source_q2_assembly_resolution"]
    return f"""# Classical import Gate-A reconciliation v14

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`
**Gate A:** `{value['gate_disposition']['gate_a_status']}`

The arity-two source operation is now one accepted common object.  It binds
{q2['minimal_ordered_symbolic_components']} minimal operations and
**{q2['auxiliary_ordered_component_coefficients']} auxiliary component
coefficients**, then transports them through the exact canonical graph shear.
The accepted q2 hash is `{q2['accepted_q2_sha256']}`.

The graph-coordinate `q1/q2`, cyclicity and `D/q2` defect counts are
**{q2['q1_q2_defects']} / {q2['cyclicity_defects']} / {q2['D_q2_defects']}**.
The audit also retains the rejected convention: V1 left 336 exact defects;
the certified V2 `c_star` translation leaves zero.

Gate A remains fail closed.  Only one of seven top-level hashes is accepted,
the metric-dependent auxiliary `q3` is not assembled, and the final common
cyclic contraction is still blocked.  No causal Green, Hadamard or QME claim
is promoted.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v14_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v14_reconciliation.py
python3 quantum-weyl/classical_import/verify_classical_import_gate_v14_reconciliation.py
python3 -m unittest quantum-weyl.classical_import.tests.test_classical_import_gate_v14_reconciliation
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
        print("CLASSICAL_IMPORT_GATE_V14_RECONCILIATION: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V14_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
