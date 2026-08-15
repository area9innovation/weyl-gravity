#!/usr/bin/env python3
"""Build Gate-A v10 from the exact shifted-cubic inventory and vv BV lift."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
V9 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V9_RECONCILIATION.json"
CLASSICAL = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"
RECEIVER = HERE / "certificates/STRICT_386_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V10_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V10.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "standalone_history_replay", "status_vocabulary", "export_reconciliation",
        "freeze_check_reconciliation", "required_hash_disposition", "minimal_missing_bundle",
        "gate_disposition", "m3_scoped_resolution", "m2_minimal_resolution", "m2_d_resolution",
        "m2_stabilized_candidate_resolution", "m2_theory_identity_obstruction",
        "m2_quadratic_elimination_resolution", "m2_shifted_cubic_inventory_resolution",
        "m4_minimal_resolution", "transitive_provenance_drift",
    )
    payload = {key: value[key] for key in keys}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    previous, classical, receiver = (json.loads(path.read_text()) for path in (V9, CLASSICAL, RECEIVER))
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V9_RECONCILIATION" or previous.get("gate_disposition", {}).get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("V9 predecessor drift")
    if classical.get("claim_flags", {}).get("SHIFTED_MASS_H_F_HAT_F_HAT_COMPONENTS_SERIALIZED") is not True:
        raise ValueError("classical shifted-cubic inventory drift")
    flags = receiver.get("claim_flags", {})
    if (
        flags.get("KNOWN_REQUIRED_CUBIC_FAMILIES_ENUMERATED") is not True
        or flags.get("VV_BV_COTANGENT_LIFT_CANONICAL") is not True
        or flags.get("FULL_386_BV_COTANGENT_LIFT_SERIALIZED") is not False
        or flags.get("FULL_SOURCE_Q2_PULLBACK_REPLAYED") is not False
    ):
        raise ValueError("receiver shifted-cubic boundary drift")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v10-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V10_RECONCILIATION",
        "result_state": "SEVEN_REQUIRED_CUBIC_FAMILIES_ENUMERATED_VV_BV_LIFT_CANONICAL_HH_HV_GAUGE_COMPONENTS_OPEN_GATE_FAIL_CLOSED",
        "created": "2026-08-15",
        "repository_base_commit": "dab6c761997f09fad3ca1f9aa87b009ec98ec1ad",
        "question": "After exact component expansion of the shifted auxiliary interactions and the paired vv antifield map, how much of M2 is receiver-certified and does Gate A pass?",
        "answer": "Seven currently required cubic block families are enumerated. The shifted mass supplies 72 exact h-f_hat-f_hat coefficients, and the vv canonical transformation supplies 22 field-map plus 16 cotangent-partner coefficients with zero defect in all four pairing slices. This closes the vv BV-lift sub-obligation. Five known families remain component-open, and the source manifest is not exhaustive for nonlinear Weyl/boost ghost-antifield terms. The 72-to-zero h-f_hat-f_hat comparison proves that the vv shift alone is insufficient, but neither proves nor obstructs a further metric-dependent canonical or L-infinity normalization. Full q2/q3 pullback, Gate A, causal lambda-squared closure, Hadamard data and QME restoration remain fail closed.",
        "supersedes_for_current_status": previous["result_id"],
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V10.md",
    })

    exports = {row["export_id"]: row for row in value["export_reconciliation"]}
    checks = {row["check_id"]: row for row in value["freeze_check_reconciliation"]}
    q2_export = exports["support_local_classical_bv_q2"]
    q2_export.update({
        "evidence": list(dict.fromkeys([*q2_export["evidence"], classical["result_id"], receiver["result_id"]])),
        "established": "Seven known-required cubic families are enumerated; the 72-coefficient h-f_hat-f_hat vertex and the canonical vv field/cotangent sector are exact receiver imports.",
        "remaining_for_gate_a": "Derive hh and hv field/cotangent components, the three Diff auxiliary BV representation tables, and an exhaustive nonlinear Weyl/boost ghost-antifield manifest; then replay complete source q2/q3, cyclicity and D-equivariance.",
        "boundary": "The vv BV sector is component-complete and canonical. Five known families plus possible unmanifested ghost-antifield families remain; no full-carrier q2/q3 hash is accepted.",
    })
    for check_id in ("q1_q2_arity_two_nilpotency", "q2_cyclic_compatibility", "D_q2_derivation"):
        row = checks[check_id]
        row["evidence"] = list(dict.fromkeys([*row["evidence"], receiver["result_id"]]))
        row["remaining_for_gate_a"] = "Replay this identity after hh, hv, Diff and nonlinear Weyl/boost ghost-antifield components form a complete source-certified 386-row lift."
        row["boundary"] = "The vv canonicality slices vanish exactly; that scoped pairing result does not establish the complete source identity."

    value["required_hash_disposition"]["q2_hash"].update({
        "accepted": None,
        "candidate_scope": "SEVEN_REQUIRED_FAMILIES_ENUMERATED_VV_LIFT_CANONICAL_FULL_SOURCE_PULLBACK_OPEN",
    })
    for item in value["minimal_missing_bundle"]:
        if item["id"] == "M2_STRICT_Q2_D":
            item["object"] = "Complete the source-certified nonlinear BV equivalence: derive hh/hv field and cotangent components, three Diff auxiliary BV representation tables, and the nonlinear Weyl/boost ghost-antifield manifest; then replay full source q2/q3, cyclicity and D-equivariance."
            item["unlocks"] = [
                "authoritative source-equivalent full-carrier q2/q3",
                "authoritative D_q2 and D_q3 derivations",
                "accepted nonlinear common-snapshot hashes",
            ]
    value["gate_disposition"].update({
        "claim_state": "CLASSICAL_IMPORT_CUBIC_FAMILIES_ENUMERATED_VV_BV_LIFT_CANONICAL_FULL_PULLBACK_OPEN",
        "same_theory_receiver_verified_scoped": 11,
        "freeze_checks_receiver_verified_scoped": 8,
        "freeze_checks_supporting_evidence_only": 1,
        "freeze_checks_blocked": 1,
        "accepted_common_snapshot_hashes": 0,
    })
    value["m2_minimal_resolution"].update({
        "remaining": "The vv field/cotangent component is now exact and canonical. The hh/hv and Diff components, nonlinear Weyl/boost manifest, and complete q2/q3 pullback remain open.",
        "boundary": "A canonical component sector and seven-family lower-bound census do not constitute an exhaustive BV lift or cyclic L-infinity equivalence.",
    })

    complete = receiver["inventory_completeness"]
    lift = receiver["vv_BV_cotangent_lift"]
    comparison = receiver["candidate_comparison"]
    value["m2_shifted_cubic_inventory_resolution"] = {
        "status": "KNOWN_REQUIRED_FAMILIES_ENUMERATED_VV_BV_LIFT_CANONICAL_FULL_LIFT_OPEN",
        "classical_evidence": classical["result_id"],
        "receiver_evidence": receiver["result_id"],
        "carrier_rows": lift["carrier_rows"],
        "known_required_cubic_block_families": complete["known_required_cubic_block_families_enumerated"],
        "component_complete_families": complete["component_coefficient_complete_families"],
        "component_open_families": complete["component_coefficient_open_families"],
        "family_ids": [row["family_id"] for row in receiver["required_cubic_family_inventory"]],
        "h_f_hat_f_hat_source_coefficients": comparison["shifted_mass_h_f_hat_f_hat_source_nonzero_coefficients"],
        "h_f_hat_f_hat_candidate_coefficients": comparison["trivial_candidate_h_f_hat_f_hat_nonzero_coefficients"],
        "vv_field_map_coefficients": lift["field_map_nonzero_component_coefficients"],
        "vv_cotangent_partner_coefficients": lift["cotangent_partner_nonzero_component_coefficients"],
        "vv_canonicality_slices": len(lift["canonicality_slices"]),
        "vv_canonicality_defects": lift["canonicality_defects"],
        "quadratic_active_output_rows": lift["quadratic_active_output_rows"],
        "quadratic_zero_output_rows": lift["quadratic_zero_output_rows"],
        "hh_hv_component_complete": complete["hh_hv_BV_cotangent_lift_component_complete"],
        "diffeomorphism_representation_component_complete": complete["diffeomorphism_BV_representation_component_complete"],
        "exhaustive_full_nonlinear_BV_family_census": complete["exhaustive_full_nonlinear_BV_family_census"],
        "full_386_BV_cotangent_lift_serialized": complete["full_386_quadratic_BV_cotangent_lift_serialized"],
        "complete_source_q2_q3_pullback_replayed": complete["full_source_q2_q3_pullback_replayed"],
        "shift_alone_identifies_trivial_stabilization": False,
        "further_normalization_may_exist": comparison["further_metric_dependent_canonical_or_L_infinity_normalization_may_exist"],
        "full_nonlinear_equivalence_obstructed": comparison["full_nonlinear_equivalence_obstructed"],
    }

    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(V9.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(V9), "role": "immutable Gate-A V9 predecessor"},
        {"path": str(CLASSICAL.relative_to(ROOT)), "result_or_artifact_id": classical["result_id"], "sha256": sha(CLASSICAL), "role": "authoritative exact shifted-cubic inventory"},
        {"path": str(RECEIVER.relative_to(ROOT)), "result_or_artifact_id": receiver["result_id"], "sha256": sha(RECEIVER), "role": "independent 386-row cubic import and vv cotangent lift"},
    ]
    drift = []
    for source in previous["provenance"]["inputs"]:
        path = ROOT / source["path"]
        current = sha(path) if path.is_file() else None
        if current != source["sha256"]:
            drift.append({
                "path": source["path"],
                "historical_v9_sha256": source["sha256"],
                "current_worktree_sha256": current,
                "status": "RECORDED_NOT_SILENTLY_REBOUND",
                "disposition": "V9 remains content-pinned; current bytes are not substituted without successor replay.",
            })
    value["transitive_provenance_drift"] = {
        "files_checked": len(previous["provenance"]["inputs"]),
        "drifted_files": len(drift),
        "status": "DRIFT_RECORDED_GATE_REMAINS_FAIL_CLOSED",
        "entries": drift,
    }
    value["claim_flags"].update({
        "STRICT_386_KNOWN_REQUIRED_CUBIC_FAMILIES_ENUMERATED": True,
        "STRICT_386_SHIFTED_MASS_H_F_HAT_F_HAT_COMPONENTS_IMPORTED": True,
        "STRICT_386_VV_FIELD_MAP_COMPONENTS_IMPORTED": True,
        "STRICT_386_VV_COTANGENT_PARTNER_COMPONENTS_SERIALIZED": True,
        "STRICT_386_VV_BV_COTANGENT_LIFT_CANONICAL": True,
        "STRICT_386_EXHAUSTIVE_FULL_NONLINEAR_BV_FAMILY_CENSUS": False,
        "STRICT_386_HH_HV_BV_COTANGENT_LIFT_COMPONENT_COMPLETE": False,
        "STRICT_386_DIFF_BV_REPRESENTATION_COMPONENT_COMPLETE": False,
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
        "an exhaustive nonlinear BV family census or complete hh/hv, Diff, Weyl and boost component inventory",
        "that the 72 h-f_hat-f_hat source coefficients are an obstruction to a further metric-dependent canonical or L-infinity normalization",
        "a full 386-row BV cotangent lift, source q2/q3 pullback, causal lambda-squared closure, Hadamard state, or QME restoration",
    ]))
    value["next_gate"] = "Derive exact hh/hv field and cotangent tables and the three Diff auxiliary BV representation vertices; audit nonlinear Weyl/boost ghost-antifield families; then assemble and independently replay the complete 386-row source q2/q3 pullback. M1 and M3-M6 remain independent blockers."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v10_reconciliation.py",
        "checks": [
            "V9 predecessor and cubic-inventory pins",
            "twenty-export and ten-check preservation",
            "seven-family, 72, 22+16 and four-slice exact projection",
            "vv-sector promotion with exhaustive-census and full-lift firewalls",
            "zero accepted hashes and Gate-A lifecycle firewall",
            "transitive drift recorded without rebinding",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    p = value["m2_shifted_cubic_inventory_resolution"]
    return f"""# Classical import Gate-A reconciliation v10

**Result:** `{value['result_id']}`
**Dependency:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`
**Gate A:** `{value['gate_disposition']['gate_a_status']}`

## Outcome

The receiver now knows **{p['known_required_cubic_block_families']}** required
cubic block families.  The exact tables contain **{p['h_f_hat_f_hat_source_coefficients']}**
nonzero `h-f_hat-f_hat` source coefficients, **{p['vv_field_map_coefficients']}**
vv field-map coefficients and **{p['vv_cotangent_partner_coefficients']}**
cotangent-partner coefficients.  All **{p['vv_canonicality_slices']}** vv
canonicality slices have **{p['vv_canonicality_defects']}** defects.

This closes the vv BV-lift sector.  The hh/hv and three Diff component families
remain open, and the nonlinear Weyl/boost ghost-antifield manifest is not yet
exhaustive.  The 72-to-zero shifted-mass comparison proves that the vv shift
alone is insufficient; it does not obstruct a further normalization.

Gate A remains fail closed with **{value['gate_disposition']['accepted_common_snapshot_hashes']}**
accepted hashes.  M1 and M3--M6 remain independent blockers.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v10_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v10_reconciliation.py
python3 quantum-weyl/classical_import/verify_classical_import_gate_v10_reconciliation.py
python3 -m unittest quantum-weyl.classical_import.tests.test_classical_import_gate_v10_reconciliation
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
        print("CLASSICAL_IMPORT_GATE_V10_RECONCILIATION: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V10_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
