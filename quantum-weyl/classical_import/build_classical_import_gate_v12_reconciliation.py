#!/usr/bin/env python3
"""Build Gate-A v12 after the three auxiliary Diff BV lifts."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
V11 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V11_RECONCILIATION.json"
CLASSICAL = ROOT / "d_quotient_classical/certificates/CLASSICAL_DIFF_AUXILIARY_BV_REPRESENTATION_V1.json"
RECEIVER = HERE / "certificates/STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V12_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V12.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "standalone_history_replay", "status_vocabulary", "export_reconciliation",
        "freeze_check_reconciliation", "required_hash_disposition", "minimal_missing_bundle",
        "gate_disposition", "m3_scoped_resolution", "m2_minimal_resolution", "m2_d_resolution",
        "m2_stabilized_candidate_resolution", "m2_theory_identity_obstruction",
        "m2_quadratic_elimination_resolution", "m2_shifted_cubic_inventory_resolution",
        "m2_hh_hv_cotangent_resolution", "m2_diff_auxiliary_resolution",
        "m4_minimal_resolution", "transitive_provenance_drift",
    )
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    previous, classical, receiver = (json.loads(path.read_text()) for path in (V11, CLASSICAL, RECEIVER))
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V11_RECONCILIATION" or previous.get("gate_disposition", {}).get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("V11 predecessor drift")
    cflags, rflags = classical.get("claim_flags", {}), receiver.get("claim_flags", {})
    if cflags.get("THREE_DIFF_AUXILIARY_FIELD_COMPONENT_TABLES_SERIALIZED") is not True:
        raise ValueError("classical Diff auxiliary export drift")
    if rflags.get("THREE_DIFF_AUXILIARY_BV_COTANGENT_LIFTS_SERIALIZED") is not True or rflags.get("SEVEN_KNOWN_REQUIRED_CUBIC_FAMILIES_COMPONENT_COMPLETE") is not True:
        raise ValueError("receiver Diff auxiliary lift drift")
    if rflags.get("EXHAUSTIVE_FULL_NONLINEAR_BV_FAMILY_CENSUS") is not False or rflags.get("FULL_SOURCE_Q2_PULLBACK_REPLAYED") is not False:
        raise ValueError("receiver fail-closed boundary drift")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v12-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V12_RECONCILIATION",
        "result_state": "SEVEN_KNOWN_CUBIC_FAMILIES_COMPONENT_COMPLETE_EXHAUSTIVE_GHOST_MANIFEST_AND_SOURCE_Q2_OPEN_GATE_FAIL_CLOSED",
        "created": "2026-08-15",
        "repository_base_commit": "95decea291a6a12c7f0cdab017d4bcd0da9aaf92",
        "question": "After importing all three auxiliary Diff representations and their cotangent/momentum-map rows, does the strict source q2 satisfy Gate A?",
        "answer": "All seven currently known required cubic families are now component-complete on the fixed 386-row carrier. The three source-forced Lie actions contain 168 ordered field coefficients; against the exact non-diagonal pairing they induce 264 master-density, 336 field-output, 632 antifield-output and 704 Diff momentum-map coefficients with zero formal-variational or Koszul defect. This closes the named Diff-family gap but not the exhaustive nonlinear BV census: an authoritative nonlinear Weyl/conformal-boost ghost-antifield manifest is still absent, and the complete source q2/q3 has not been assembled or replayed. No nonlinear hash is accepted and Gate A remains fail closed.",
        "supersedes_for_current_status": previous["result_id"],
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V12.md",
    })
    exports = {row["export_id"]: row for row in value["export_reconciliation"]}
    checks = {row["check_id"]: row for row in value["freeze_check_reconciliation"]}
    q2 = exports["support_local_classical_bv_q2"]
    q2.update({
        "evidence": list(dict.fromkeys([*q2["evidence"], classical["result_id"], receiver["result_id"]])),
        "established": "All seven currently known required cubic families have exact field/cotangent component tables, including the three Diff representations and their c-star momentum maps.",
        "remaining_for_gate_a": "Close the exhaustive nonlinear Weyl/conformal-boost ghost-antifield manifest, assemble the complete source q2/q3, and replay q1/q2, cyclicity and D identities on common bytes.",
        "boundary": "Completeness of the seven known families is not an exhaustive source-family census and does not itself provide an accepted full-carrier q2 hash.",
    })
    for check_id in ("q1_q2_arity_two_nilpotency", "q2_cyclic_compatibility", "D_q2_derivation"):
        row = checks[check_id]
        row["evidence"] = list(dict.fromkeys([*row["evidence"], receiver["result_id"]]))
        row["remaining_for_gate_a"] = "Replay this identity after the exhaustive nonlinear ghost manifest is source-pinned and the full 386-row q2 is assembled."
        row["boundary"] = "The isolated Diff master-density variations are exact; the full source q2 identity is not inferred from them."
    value["required_hash_disposition"]["q2_hash"].update({"accepted": None, "candidate_scope": "SEVEN_KNOWN_CUBIC_FAMILIES_COMPONENT_COMPLETE_EXHAUSTIVE_GHOST_MANIFEST_AND_FULL_Q2_OPEN"})
    for item in value["minimal_missing_bundle"]:
        if item["id"] == "M2_STRICT_Q2_D":
            item["object"] = "Derive an authoritative exhaustive nonlinear Weyl/conformal-boost ghost-antifield manifest; assemble the full source-certified 386-row q2/q3 and replay q1/q2, cyclicity and D-equivariance."
    value["gate_disposition"].update({
        "claim_state": "CLASSICAL_IMPORT_SEVEN_KNOWN_CUBIC_FAMILIES_COMPLETE_EXHAUSTIVE_GHOST_MANIFEST_OPEN",
        "same_theory_receiver_verified_scoped": 13,
        "accepted_common_snapshot_hashes": 0,
    })
    value["m2_minimal_resolution"].update({
        "remaining": "All seven known-required cubic families are component-complete. The exhaustive nonlinear ghost manifest and assembled source q2/q3 identity remain open.",
        "boundary": "Known-family completion cannot be promoted to exhaustive nonlinear equivalence or an accepted q2 hash.",
    })
    complete, summary = receiver["inventory_completeness"], receiver["component_summary"]
    inventory = value["m2_shifted_cubic_inventory_resolution"]
    inventory.update({
        "status": "SEVEN_KNOWN_REQUIRED_FAMILIES_COMPONENT_COMPLETE_EXHAUSTIVE_GHOST_CENSUS_OPEN",
        "classical_diff_evidence": classical["result_id"],
        "receiver_diff_evidence": receiver["result_id"],
        "component_complete_families": complete["component_coefficient_complete_families"],
        "component_open_families": complete["component_coefficient_open_families"],
        "diffeomorphism_representation_component_complete": True,
        "exhaustive_full_nonlinear_BV_family_census": False,
        "complete_source_q2_q3_pullback_replayed": False,
    })
    value["m2_diff_auxiliary_resolution"] = {
        "status": "THREE_DIFF_AUXILIARY_BV_REPRESENTATIONS_EXACT_ON_386_ROWS",
        "classical_evidence": classical["result_id"],
        "receiver_evidence": receiver["result_id"],
        **summary,
        "known_required_cubic_families": 7,
        "known_required_component_complete_families": 7,
        "exhaustive_full_nonlinear_BV_family_census": False,
        "full_source_q2_q3_pullback_replayed": False,
    }
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(V11.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(V11), "role": "immutable Gate-A V11 predecessor"},
        {"path": str(CLASSICAL.relative_to(ROOT)), "result_or_artifact_id": classical["result_id"], "sha256": sha(CLASSICAL), "role": "authoritative source-forced auxiliary Diff field actions"},
        {"path": str(RECEIVER.relative_to(ROOT)), "result_or_artifact_id": receiver["result_id"], "sha256": sha(RECEIVER), "role": "independent 386-row cotangent and Diff momentum-map lift"},
    ]
    drift = []
    for source in previous["provenance"]["inputs"]:
        path = ROOT / source["path"]
        current = sha(path) if path.is_file() else None
        if current != source["sha256"]:
            drift.append({"path": source["path"], "historical_v11_sha256": source["sha256"], "current_worktree_sha256": current, "status": "RECORDED_NOT_SILENTLY_REBOUND", "disposition": "V11 remains content-pinned; current bytes are not substituted without successor replay."})
    value["transitive_provenance_drift"] = {"files_checked": len(previous["provenance"]["inputs"]), "drifted_files": len(drift), "status": "DRIFT_RECORDED_GATE_REMAINS_FAIL_CLOSED", "entries": drift}
    value["claim_flags"].update({
        "STRICT_386_DIFF_BV_REPRESENTATION_COMPONENT_COMPLETE": True,
        "STRICT_386_SEVEN_KNOWN_REQUIRED_CUBIC_FAMILIES_COMPONENT_COMPLETE": True,
        "STRICT_386_EXHAUSTIVE_FULL_NONLINEAR_BV_FAMILY_CENSUS": False,
        "STRICT_386_FULL_SOURCE_Q2_PULLBACK_REPLAYED": False,
        "STRICT_386_FULL_SOURCE_Q3_PULLBACK_REPLAYED": False,
        "STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q2": False,
        "STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q3": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "QME_RESTORED": False,
    })
    value["does_not_establish"] = [item for item in previous["does_not_establish"] if "three Diff auxiliary" not in item]
    value["does_not_establish"] = list(dict.fromkeys([
        *value["does_not_establish"],
        "an exhaustive nonlinear Weyl/conformal-boost ghost-antifield manifest or proof that the seven known families are all families",
        "the assembled source q2/q3, full q1/q2 identity, accepted nonlinear hashes, cyclic L-infinity equivalence, or Gate A",
        "causal lambda-squared closure, a Hadamard state, renormalized Lorentzian products, QME restoration, or residual transfer",
    ]))
    value["next_gate"] = "Derive and independently audit the authoritative nonlinear Weyl/conformal-boost ghost-antifield manifest. Then assemble the complete 386-row source q2 and replay q1/q2, cyclicity and D-equivariance; M1 and M3-M6 remain independent blockers."
    value["independent_checker"] = {"path": "quantum-weyl/classical_import/check_classical_import_gate_v12_reconciliation.py", "checks": ["V11 predecessor and Diff source/receiver pins", "twenty-export and ten-check preservation", "168 source plus 264/336/632/704 receiver coefficient projection", "seven-known-family promotion with exhaustive-census firewall", "zero accepted hashes and Gate-A lifecycle firewall", "transitive drift recorded without rebinding"], "expected_digest": ""}
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    p = value["m2_diff_auxiliary_resolution"]
    return f"""# Classical import Gate-A reconciliation v12

**Result:** `{value['result_id']}`

**Dependency:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

**Gate A:** `{value['gate_disposition']['gate_a_status']}`

## Outcome

The three source-forced auxiliary Diff representations are exact on the fixed
386-row carrier.  Their {p['master_density_coefficients']} master-density
coefficients generate {p['field_output_coefficients']} field,
{p['antifield_output_coefficients']} antifield and
{p['c_star_output_coefficients']} `c_star` coefficients, with
{p['formal_variational_defects']} formal-variation and
{p['Koszul_symmetry_defects']} Koszul defects.

All seven currently known required cubic families are component-complete.  An
authoritative exhaustive nonlinear Weyl/conformal-boost ghost-antifield
manifest is still missing, so the complete source `q2/q3` is not assembled.
Gate A remains fail closed with
**{value['gate_disposition']['accepted_common_snapshot_hashes']}** accepted
top-level hashes.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v12_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v12_reconciliation.py
python3 quantum-weyl/classical_import/verify_classical_import_gate_v12_reconciliation.py
python3 -m unittest quantum-weyl.classical_import.tests.test_classical_import_gate_v12_reconciliation
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
        print("CLASSICAL_IMPORT_GATE_V12_RECONCILIATION: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V12_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
