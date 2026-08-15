#!/usr/bin/env python3
"""Build Gate-A v11 after the exact curved hh/hv quadratic BV lift."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
V10 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V10_RECONCILIATION.json"
CLASSICAL = ROOT / "d_quotient_classical/certificates/CLASSICAL_HH_HV_AUXILIARY_SHIFT_V1.json"
RECEIVER = HERE / "certificates/STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V11_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V11.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "standalone_history_replay", "status_vocabulary", "export_reconciliation",
        "freeze_check_reconciliation", "required_hash_disposition", "minimal_missing_bundle",
        "gate_disposition", "m3_scoped_resolution", "m2_minimal_resolution", "m2_d_resolution",
        "m2_stabilized_candidate_resolution", "m2_theory_identity_obstruction",
        "m2_quadratic_elimination_resolution", "m2_shifted_cubic_inventory_resolution",
        "m2_hh_hv_cotangent_resolution", "m4_minimal_resolution", "transitive_provenance_drift",
    )
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    previous, classical, receiver = (json.loads(path.read_text()) for path in (V10, CLASSICAL, RECEIVER))
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V10_RECONCILIATION" or previous.get("gate_disposition", {}).get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("V10 predecessor drift")
    cflags, rflags = classical.get("claim_flags", {}), receiver.get("claim_flags", {})
    if cflags.get("HH_SECOND_FRECHET_COMPONENT_JETS_SERIALIZED") is not True or cflags.get("HV_SECOND_FRECHET_COMPONENT_JETS_SERIALIZED") is not True:
        raise ValueError("classical hh/hv export drift")
    if rflags.get("FULL_386_QUADRATIC_BV_COTANGENT_LIFT_SERIALIZED") is not True or rflags.get("DIFF_AUXILIARY_BV_REPRESENTATION_COMPLETE") is not False or rflags.get("FULL_SOURCE_Q2_PULLBACK_REPLAYED") is not False:
        raise ValueError("receiver hh/hv boundary drift")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v11-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V11_RECONCILIATION",
        "result_state": "CURVED_HH_HV_VV_QUADRATIC_BV_LIFT_COMPONENT_COMPLETE_DIFF_AND_GHOST_CENSUS_OPEN_GATE_FAIL_CLOSED",
        "created": "2026-08-15",
        "repository_base_commit": "229fd0f2147e8ed611c5147328459f7678b1f605",
        "question": "After curved hh/hv second-Frechet export and formal-adjoint receiver lift, how much of M2 is component-complete and does Gate A pass?",
        "answer": "The complete quadratic auxiliary field/cotangent transformation is now serialized on the declared 386-row cylinder carrier: 1392 hh, 76 hv and 22 vv field coefficients induce 3907 collected cotangent coefficients, with zero defect over 150 declared metric-jet and four vector variational slices. Four of seven currently required cubic families are component-complete. The remaining three are the Diff auxiliary BV representation vertices, and the nonlinear Weyl/boost ghost-antifield census is still not exhaustive. The complete source q2/q3 pullback has not been replayed, so no q2 or q3 hash is accepted and Gate A remains fail closed.",
        "supersedes_for_current_status": previous["result_id"],
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V11.md",
    })
    exports = {row["export_id"]: row for row in value["export_reconciliation"]}
    checks = {row["check_id"]: row for row in value["freeze_check_reconciliation"]}
    q2 = exports["support_local_classical_bv_q2"]
    q2.update({
        "evidence": list(dict.fromkeys([*q2["evidence"], classical["result_id"], receiver["result_id"]])),
        "established": "The curved hh/hv/vv quadratic field transformation and all paired h-star/v-star cotangent terms are exact on the declared 386-row carrier; four of seven known-required cubic families are component-complete.",
        "remaining_for_gate_a": "Derive the three Diff auxiliary BV representation tables, close the nonlinear Weyl/boost ghost-antifield census, and replay the complete source q2/q3, cyclicity and D identities.",
        "boundary": "A complete quadratic canonical transformation does not by itself establish the full interacting BV pullback or an accepted q2/q3 hash.",
    })
    for check_id in ("q1_q2_arity_two_nilpotency", "q2_cyclic_compatibility", "D_q2_derivation"):
        row = checks[check_id]
        row["evidence"] = list(dict.fromkeys([*row["evidence"], receiver["result_id"]]))
        row["remaining_for_gate_a"] = "Replay this identity only after the Diff and nonlinear Weyl/boost families complete the source-certified 386-row q2/q3 pullback."
        row["boundary"] = "The quadratic field/cotangent canonicality replay has zero defect; it is not the complete source q2/q3 identity."
    value["required_hash_disposition"]["q2_hash"].update({"accepted": None, "candidate_scope": "FULL_QUADRATIC_AUXILIARY_CANONICAL_LIFT_DIFF_AND_NONLINEAR_GHOST_FAMILIES_OPEN"})
    for item in value["minimal_missing_bundle"]:
        if item["id"] == "M2_STRICT_Q2_D":
            item["object"] = "Complete the three Diff auxiliary BV representation families and exhaustive nonlinear Weyl/boost ghost-antifield manifest; then assemble and replay the full source-certified 386-row q2/q3 pullback, cyclicity and D-equivariance."
    value["gate_disposition"].update({
        "claim_state": "CLASSICAL_IMPORT_QUADRATIC_AUXILIARY_BV_LIFT_COMPLETE_DIFF_AND_GHOST_FAMILIES_OPEN",
        "same_theory_receiver_verified_scoped": 12,
        "accepted_common_snapshot_hashes": 0,
    })
    value["m2_minimal_resolution"].update({
        "remaining": "The full quadratic auxiliary field/cotangent lift is exact. Three Diff auxiliary representation families, the exhaustive nonlinear Weyl/boost manifest, and complete source q2/q3 pullback remain open.",
        "boundary": "Quadratic canonicality is necessary but does not establish the interacting cyclic L-infinity equivalence or source master-action pullback.",
    })
    lift, complete = receiver["quadratic_BV_cotangent_lift"], receiver["inventory_completeness"]
    old = value["m2_shifted_cubic_inventory_resolution"]
    old.update({
        "status": "FOUR_OF_SEVEN_FAMILIES_COMPLETE_FULL_QUADRATIC_BV_LIFT_SERIALIZED_DIFF_AND_GHOST_CENSUS_OPEN",
        "classical_hh_hv_evidence": classical["result_id"],
        "receiver_hh_hv_evidence": receiver["result_id"],
        "component_complete_families": complete["component_coefficient_complete_families"],
        "component_open_families": complete["component_coefficient_open_families"],
        "hh_field_coefficients": lift["field_second_Frechet_component_counts"]["hh"],
        "hv_field_coefficients": lift["field_second_Frechet_component_counts"]["hv"],
        "combined_cotangent_coefficients": lift["cotangent_component_counts_after_collection"]["combined"],
        "quadratic_active_output_rows": lift["quadratic_active_output_rows"],
        "quadratic_zero_output_rows": lift["quadratic_zero_output_rows"],
        "hh_hv_component_complete": True,
        "full_386_BV_cotangent_lift_serialized": True,
        "diffeomorphism_representation_component_complete": False,
        "exhaustive_full_nonlinear_BV_family_census": False,
        "complete_source_q2_q3_pullback_replayed": False,
    })
    counts = lift["cotangent_component_counts_after_collection"]
    value["m2_hh_hv_cotangent_resolution"] = {
        "status": "CURVED_HH_HV_FIELD_AND_COTANGENT_COMPONENT_JETS_EXACT",
        "classical_evidence": classical["result_id"],
        "receiver_evidence": receiver["result_id"],
        "carrier_rows": lift["carrier_rows"],
        "hh_field_coefficients": lift["field_second_Frechet_component_counts"]["hh"],
        "hv_field_coefficients": lift["field_second_Frechet_component_counts"]["hv"],
        "vv_field_coefficients": lift["field_second_Frechet_component_counts"]["vv"],
        "hh_to_h_star_coefficients": counts["hh_to_h_star"],
        "hv_to_h_star_coefficients": counts["hv_to_h_star"],
        "hv_to_v_star_coefficients": counts["hv_to_v_star"],
        "vv_to_v_star_coefficients": counts["vv_to_v_star"],
        "combined_cotangent_coefficients": counts["combined"],
        "metric_variation_slices_declared": lift["formal_adjoint_replay"]["metric_variation_jet_slices_declared"],
        "vector_variation_slices": lift["formal_adjoint_replay"]["vector_variation_slices"],
        "formal_adjoint_defects": lift["formal_adjoint_replay"]["coefficient_defects"],
        "full_quadratic_BV_cotangent_lift_serialized": True,
        "full_source_q2_q3_pullback_replayed": False,
    }
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(V10.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(V10), "role": "immutable Gate-A V10 predecessor"},
        {"path": str(CLASSICAL.relative_to(ROOT)), "result_or_artifact_id": classical["result_id"], "sha256": sha(CLASSICAL), "role": "authoritative curved hh/hv second-Frechet field jets"},
        {"path": str(RECEIVER.relative_to(ROOT)), "result_or_artifact_id": receiver["result_id"], "sha256": sha(RECEIVER), "role": "independent 386-row formal-adjoint cotangent lift"},
    ]
    drift = []
    for source in previous["provenance"]["inputs"]:
        path = ROOT / source["path"]
        current = sha(path) if path.is_file() else None
        if current != source["sha256"]:
            drift.append({"path": source["path"], "historical_v10_sha256": source["sha256"], "current_worktree_sha256": current, "status": "RECORDED_NOT_SILENTLY_REBOUND", "disposition": "V10 remains content-pinned; current bytes are not substituted without successor replay."})
    value["transitive_provenance_drift"] = {"files_checked": len(previous["provenance"]["inputs"]), "drifted_files": len(drift), "status": "DRIFT_RECORDED_GATE_REMAINS_FAIL_CLOSED", "entries": drift}
    value["claim_flags"].update({
        "STRICT_386_HH_HV_FIELD_COMPONENT_JETS_IMPORTED": True,
        "STRICT_386_HH_HV_BV_COTANGENT_LIFT_COMPONENT_COMPLETE": True,
        "STRICT_386_FULL_BV_COTANGENT_LIFT_SERIALIZED": True,
        "STRICT_386_FULL_QUADRATIC_BV_COTANGENT_LIFT_SERIALIZED": True,
        "STRICT_386_DIFF_BV_REPRESENTATION_COMPONENT_COMPLETE": False,
        "STRICT_386_EXHAUSTIVE_FULL_NONLINEAR_BV_FAMILY_CENSUS": False,
        "STRICT_386_FULL_SOURCE_Q2_PULLBACK_REPLAYED": False,
        "STRICT_386_FULL_SOURCE_Q3_PULLBACK_REPLAYED": False,
        "STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q2": False,
        "STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q3": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "QME_RESTORED": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "the three Diff auxiliary BV representation component tables or an exhaustive nonlinear Weyl/boost ghost-antifield family census",
        "the complete source q2/q3 pullback, accepted nonlinear hashes, cyclic L-infinity equivalence, or Gate A",
        "causal lambda-squared closure, a Hadamard state, renormalized Lorentzian products, QME restoration, or residual transfer",
    ]))
    value["next_gate"] = "Derive the three Diff auxiliary BV representation component tables and close the nonlinear Weyl/boost ghost-antifield census; then assemble and independently replay the complete 386-row source q2/q3 pullback. M1 and M3-M6 remain independent blockers."
    value["independent_checker"] = {"path": "quantum-weyl/classical_import/check_classical_import_gate_v11_reconciliation.py", "checks": ["V10 predecessor and hh/hv source/receiver pins", "twenty-export and ten-check preservation", "1392+76+22 field and 3907 cotangent coefficient projection", "quadratic-lift promotion with Diff/full-source firewalls", "zero accepted hashes and Gate-A lifecycle firewall", "transitive drift recorded without rebinding"], "expected_digest": ""}
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    p = value["m2_hh_hv_cotangent_resolution"]
    return f"""# Classical import Gate-A reconciliation v11

**Result:** `{value['result_id']}`
**Dependency:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`
**Gate A:** `{value['gate_disposition']['gate_a_status']}`

## Outcome

The curved quadratic auxiliary transformation now has
**{p['hh_field_coefficients']} hh**, **{p['hv_field_coefficients']} hv**, and
**{p['vv_field_coefficients']} vv** field coefficients.  Formal adjunction on
the 386-row pairing produces **{p['combined_cotangent_coefficients']}** collected
cotangent coefficients with **{p['formal_adjoint_defects']}** defects over
{p['metric_variation_slices_declared']} metric and {p['vector_variation_slices']}
vector variational slices.

This completes the quadratic BV cotangent lift, not the interacting import.
The three Diff auxiliary representation families and exhaustive nonlinear
Weyl/boost ghost-antifield census remain open.  No source q2/q3 hash is accepted,
and Gate A remains fail closed with
**{value['gate_disposition']['accepted_common_snapshot_hashes']}** accepted hashes.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v11_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v11_reconciliation.py
python3 quantum-weyl/classical_import/verify_classical_import_gate_v11_reconciliation.py
python3 -m unittest quantum-weyl.classical_import.tests.test_classical_import_gate_v11_reconciliation
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
        print("CLASSICAL_IMPORT_GATE_V11_RECONCILIATION: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V11_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
