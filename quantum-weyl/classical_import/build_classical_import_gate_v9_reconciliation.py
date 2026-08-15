#!/usr/bin/env python3
"""Build Gate-A v9 after importing the first nonlinear auxiliary correction."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
V8 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V8_RECONCILIATION.json"
CLASSICAL_MAP = ROOT / "d_quotient_classical/certificates/CLASSICAL_QUADRATIC_AUXILIARY_ELIMINATION_MAP_V1.json"
CHANNEL = HERE / "certificates/STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V9_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V9.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "standalone_history_replay", "status_vocabulary", "export_reconciliation",
        "freeze_check_reconciliation", "required_hash_disposition", "minimal_missing_bundle",
        "gate_disposition", "m3_scoped_resolution", "m2_minimal_resolution", "m2_d_resolution",
        "m2_stabilized_candidate_resolution", "m2_theory_identity_obstruction",
        "m2_quadratic_elimination_resolution", "m4_minimal_resolution", "transitive_provenance_drift",
    )
    return hashlib.sha256(
        json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def build() -> dict[str, Any]:
    previous, classical_map, channel = (
        json.loads(path.read_text()) for path in (V8, CLASSICAL_MAP, CHANNEL)
    )
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V8_RECONCILIATION" or previous.get("gate_disposition", {}).get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("V8 predecessor drift")
    if classical_map.get("claim_flags", {}).get("F_HAT_V_V_CHANNEL_CANCELED_BY_PULLBACK") is not True:
        raise ValueError("authoritative quadratic map drift")
    channel_flags = channel.get("claim_flags", {})
    if (
        channel_flags.get("FIRST_NONLINEAR_EQUIVALENCE_COMPONENT_CONSTRUCTED") is not True
        or channel_flags.get("FULL_SOURCE_Q2_PULLBACK_REPLAYED") is not False
        or channel_flags.get("CLASSICAL_IMPORT_GATE_PASSED") is not False
    ):
        raise ValueError("receiver channel boundary drift")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v9-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V9_RECONCILIATION",
        "result_state": "FIRST_NONLINEAR_COMPONENT_IMPORTED_ONE_CHANNEL_CLOSED_FULL_PULLBACK_OPEN_GATE_FAIL_CLOSED",
        "created": "2026-08-15",
        "repository_base_commit": "a004672f18a9011ff65b7e79b498d4a3f7985bec",
        "question": "After importing the exact quadratic auxiliary-elimination map and independently replaying its first induced cubic cancellation, which M2 obligation closes and does Gate A pass?",
        "answer": "The first constructive nonlinear-equivalence obligation closes. The exact source-to-split map has F_(2)(v)=v tensor v-(1/2)g v^2; its inverse-shift mass cross term contributes +1 to the source Omega(f_hat,q2(v,v))=-1 channel, giving transformed source 0, equal to the trivial-stabilization candidate. This removes the V8 mismatch as an obstruction and constructs the first required nonlinear component. It does not establish the complete 386-row BV cotangent lift or the full source q2/q3 pullback: metric-dependent h-f_hat-f_hat and ghost/antifield channels remain. Gate A therefore remains fail closed with zero accepted hashes, and M1 plus M3-M6 remain independent blockers.",
        "supersedes_for_current_status": previous["result_id"],
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V9.md",
    })
    exports = {row["export_id"]: row for row in value["export_reconciliation"]}
    checks = {row["check_id"]: row for row in value["freeze_check_reconciliation"]}
    q2_export = exports["support_local_classical_bv_q2"]
    q2_export.update({
        "evidence": list(dict.fromkeys([*q2_export["evidence"], classical_map["result_id"], channel["result_id"]])),
        "established": "The exact quadratic source-to-split auxiliary map is imported and independently cancels the formerly mismatched f_hat-v-v cubic channel. This constructs the first nonlinear equivalence component on the 386-row carrier.",
        "remaining_for_gate_a": "Serialize the full 386-row BV cotangent lift, enumerate every metric-dependent auxiliary and ghost/antifield cubic channel, and independently replay the complete source q2/q3 pullback, cyclicity and D-equivariance.",
        "boundary": "One exact induced channel is closed. No authoritative full-carrier q2/q3 hash is accepted until every pullback channel is receiver-replayed.",
    })
    for check_id in ("q1_q2_arity_two_nilpotency", "q2_cyclic_compatibility", "D_q2_derivation"):
        row = checks[check_id]
        row["evidence"] = list(dict.fromkeys([*row["evidence"], channel["result_id"]]))
        row["remaining_for_gate_a"] = "Replay this identity under the complete source-certified nonlinear BV cotangent lift after all induced q2/q3 channels are serialized."
        row["boundary"] = "The first nonlinear field-map component agrees in one exact channel; the complete source-theory identity remains open."
    value["required_hash_disposition"]["q2_hash"].update({
        "accepted": None,
        "candidate_scope": "FIRST_NONLINEAR_COMPONENT_CLOSED_FULL_SOURCE_PULLBACK_OPEN",
    })
    for item in value["minimal_missing_bundle"]:
        if item["id"] == "M2_STRICT_Q2_D":
            item["object"] = "Complete the source-certified nonlinear BV equivalence: serialize its componentwise 386-row cotangent lift and enumerate all induced cubic channels, beginning with h-f_hat-f_hat and ghost/antifield families; then replay full q2/q3, cyclicity and D-equivariance."
            item["unlocks"] = [
                "authoritative source-equivalent full-carrier q2/q3",
                "authoritative D_q2 and D_q3 derivations",
                "accepted nonlinear common-snapshot hashes",
            ]
    value["gate_disposition"].update({
        "claim_state": "CLASSICAL_IMPORT_FIRST_NONLINEAR_COMPONENT_CONSTRUCTED_FULL_PULLBACK_OPEN",
        "same_theory_receiver_verified_scoped": 11,
        "freeze_checks_receiver_verified_scoped": 8,
        "freeze_checks_supporting_evidence_only": 1,
        "freeze_checks_blocked": 1,
        "accepted_common_snapshot_hashes": 0,
    })
    value["m2_minimal_resolution"].update({
        "remaining": "Minimal q2/q3 and their exact 386-row stabilization remain valid. The first nonlinear auxiliary-elimination component closes the f_hat-v-v mismatch, but the componentwise BV cotangent lift and all remaining source q2/q3 pullback channels are open.",
        "boundary": "Closing one necessary cubic channel proves a first equivalence component, not a full cyclic L-infinity equivalence or authoritative q2/q3 hash.",
    })
    replay = channel["channel_pullback_replay"]
    boundary = channel["equivalence_boundary"]
    value["m2_quadratic_elimination_resolution"] = {
        "status": "FIRST_QUADRATIC_COMPONENT_IMPORTED_ONE_CUBIC_CHANNEL_CLOSED_FULL_PULLBACK_OPEN",
        "classical_evidence": classical_map["result_id"],
        "receiver_evidence": channel["result_id"],
        "carrier_rows": replay["carrier_rows"],
        "field_map_component": replay["source_to_split_homogeneous_quadratic_component"],
        "cyclic_form_channel": replay["cyclic_form_channel"],
        "source_before_correction": replay["pre_correction_source_value"],
        "inverse_shift_correction": replay["inverse_shift_mass_cross_correction"],
        "transformed_source": replay["transformed_source_value"],
        "candidate": replay["candidate_value"],
        "residual": replay["transformed_source_minus_candidate_residual"],
        "component_support_local": replay["support_local"],
        "component_uses_green_operator": replay["uses_green_operator"],
        "component_uses_choice_principle": replay["uses_choice_principle"],
        "source_local_BV_canonical_lift_available": boundary["source_certified_local_BV_canonical_lift_available"],
        "receiver_componentwise_386_cotangent_lift_serialized": boundary["receiver_componentwise_386_cotangent_lift_serialized"],
        "complete_source_q2_pullback_replayed": boundary["complete_source_q2_pullback_replayed"],
        "complete_source_q3_pullback_replayed": boundary["complete_source_q3_pullback_replayed"],
        "full_cyclic_L_infinity_equivalence_constructed": boundary["full_cyclic_L_infinity_equivalence_constructed"],
        "nonlinear_equivalence_obstructed": boundary["nonlinear_equivalence_obstructed"],
        "remaining_shifted_cubic_families": boundary["remaining_shifted_cubic_families"],
    }
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(V8.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(V8), "role": "immutable Gate-A V8 predecessor"},
        {"path": str(CLASSICAL_MAP.relative_to(ROOT)), "result_or_artifact_id": classical_map["result_id"], "sha256": sha(CLASSICAL_MAP), "role": "authoritative exact quadratic auxiliary map"},
        {"path": str(CHANNEL.relative_to(ROOT)), "result_or_artifact_id": channel["result_id"], "sha256": sha(CHANNEL), "role": "independent 386-row channel pullback replay"},
    ]
    drift = []
    for source in previous["provenance"]["inputs"]:
        path = ROOT / source["path"]
        current = sha(path) if path.is_file() else None
        if current != source["sha256"]:
            drift.append({
                "path": source["path"],
                "historical_v8_sha256": source["sha256"],
                "current_worktree_sha256": current,
                "status": "RECORDED_NOT_SILENTLY_REBOUND",
                "disposition": "V8 remains content-pinned; current bytes are not substituted without successor replay.",
            })
    value["transitive_provenance_drift"] = {
        "files_checked": len(previous["provenance"]["inputs"]),
        "drifted_files": len(drift),
        "status": "DRIFT_RECORDED_GATE_REMAINS_FAIL_CLOSED",
        "entries": drift,
    }
    value["claim_flags"].update({
        "STRICT_386_FIRST_NONLINEAR_EQUIVALENCE_COMPONENT_CONSTRUCTED": True,
        "STRICT_386_F_HAT_V_V_PULLBACK_CHANNEL_CLOSED": True,
        "STRICT_386_COMPONENT_SUPPORT_LOCAL": True,
        "STRICT_386_COMPONENT_USES_GREEN_OPERATOR": False,
        "STRICT_386_COMPONENT_USES_CHOICE_PRINCIPLE": False,
        "STRICT_386_FULL_BV_COTANGENT_LIFT_SERIALIZED": False,
        "STRICT_386_FULL_SOURCE_Q2_PULLBACK_REPLAYED": False,
        "STRICT_386_FULL_SOURCE_Q3_PULLBACK_REPLAYED": False,
        "STRICT_386_NONLINEAR_EQUIVALENCE_CONSTRUCTED": False,
        "STRICT_386_NONLINEAR_EQUIVALENCE_OBSTRUCTED": False,
        "STRICT_386_CANDIDATE_THEORY_IDENTITY": False,
        "STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q2": False,
        "STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q3": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "QME_RESTORED": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "a componentwise 386-row BV cotangent lift or complete source q2/q3 pullback",
        "elimination or agreement of the metric-dependent h-f_hat-f_hat and ghost/antifield channel families",
        "a full cyclic L-infinity equivalence, authoritative q2/q3 hash, causal lambda-squared source closure, Hadamard data, or QME restoration",
    ]))
    value["next_gate"] = "Enumerate every cubic channel induced by the exact nonlinear auxiliary shift and its BV cotangent lift, beginning with h-f_hat-f_hat and ghost/antifield families. Serialize the componentwise 386-row lift and independently replay full source q2/q3, cyclicity and D identities before accepting hashes. M1 and M3-M6 remain independent blockers."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v9_reconciliation.py",
        "checks": [
            "V8 predecessor and quadratic-map/channel pins",
            "twenty-export and ten-check preservation",
            "exact -1 + 1 = 0 channel ledger",
            "first-component promotion with full-pullback firewall",
            "zero accepted hashes and Gate-A lifecycle firewall",
            "transitive drift recorded without rebinding",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    p = value["m2_quadratic_elimination_resolution"]
    return f"""# Classical import Gate-A reconciliation v9

**Result:** `{value['result_id']}`

**Lifecycle:** `{value['lifecycle']}`

**Gate A:** `{value['gate_disposition']['gate_a_status']}`

## Outcome

The first nonlinear correction is now constructed.  The exact component
`{p['field_map_component']}` contributes **{p['inverse_shift_correction']}**
to the source value **{p['source_before_correction']}** in
`{p['cyclic_form_channel']}`.  The transformed source and candidate are both
**{p['candidate']}**, with residual **{p['residual']}**.

This closes one necessary channel.  It does not serialize the complete 386-row
BV cotangent lift or replay all source q2/q3 channels.  The metric-dependent
`h-f_hat-f_hat` and ghost/antifield families remain explicit obligations.

Gate A remains fail closed with **{value['gate_disposition']['accepted_common_snapshot_hashes']}**
accepted hashes.  M1 and M3--M6 remain independent blockers.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v9_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v9_reconciliation.py
python3 quantum-weyl/classical_import/verify_classical_import_gate_v9_reconciliation.py
python3 -m unittest quantum-weyl.classical_import.tests.test_classical_import_gate_v9_reconciliation
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
        print("CLASSICAL_IMPORT_GATE_V9_RECONCILIATION: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V9_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
