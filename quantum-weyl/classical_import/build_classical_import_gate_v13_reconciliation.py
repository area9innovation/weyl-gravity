#!/usr/bin/env python3
"""Build Gate-A v13 after the exhaustive scoped Weyl/boost ghost manifest."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
V12 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V12_RECONCILIATION.json"
MANIFEST = ROOT / "d_quotient_classical/certificates/CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V13_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V13.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "export_reconciliation", "freeze_check_reconciliation", "required_hash_disposition",
        "minimal_missing_bundle", "gate_disposition", "m2_minimal_resolution",
        "m2_shifted_cubic_inventory_resolution", "m2_diff_auxiliary_resolution",
        "m2_nonlinear_ghost_manifest_resolution", "transitive_provenance_drift",
    )
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    previous, manifest = (json.loads(path.read_text()) for path in (V12, MANIFEST))
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V12_RECONCILIATION" or previous.get("gate_disposition", {}).get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("V12 predecessor drift")
    flags = manifest.get("claim_flags", {})
    if flags.get("EXHAUSTIVE_NONLINEAR_WEYL_BOOST_GHOST_ANTIFIELD_MANIFEST") is not True:
        raise ValueError("source ghost manifest is not exhaustive in scope")
    if flags.get("ADDITIONAL_AUXILIARY_GHOST_ANTIFIELD_FAMILIES_REQUIRED") is not False or flags.get("FULL_386_SOURCE_Q2_ASSEMBLED") is not False:
        raise ValueError("manifest boundary drift")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v13-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V13_RECONCILIATION",
        "result_state": "AUXILIARY_FAMILY_CENSUS_EXHAUSTIVE_SOURCE_Q2_ASSEMBLY_AND_IDENTITIES_OPEN_GATE_FAIL_CLOSED",
        "created": "2026-08-15",
        "question": "Does the primary-source-complete nonlinear Weyl/boost ghost manifest close Gate A?",
        "answer": "No. Metsaev's full nonlinear boost law makes the Weyl/boost internal algebra Abelian and the shifted auxiliary tensor invariant. The exhaustive scoped ghost manifest therefore adds no new auxiliary families: the seven already serialized families are the exhaustive auxiliary cubic family census. This removes the census uncertainty, but it does not assemble those component tables with the minimal q2/q3 on one 386-row payload or replay q1/q2, cyclicity and D-equivariance. Gate A still accepts zero common hashes and remains fail closed.",
        "supersedes_for_current_status": previous["result_id"],
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V13.md",
    })
    exports = {row["export_id"]: row for row in value["export_reconciliation"]}
    checks = {row["check_id"]: row for row in value["freeze_check_reconciliation"]}
    q2 = exports["support_local_classical_bv_q2"]
    q2.update({
        "evidence": list(dict.fromkeys([*q2["evidence"], manifest["result_id"]])),
        "established": "The nonlinear Weyl/boost ghost-antifield manifest is exhaustive in its declared source scope, requires zero additional auxiliary families, and makes the seven serialized auxiliary families an exhaustive family census.",
        "remaining_for_gate_a": "Assemble the minimal and seven auxiliary families as one source-certified 386-row q2/q3 payload and replay q1/q2, cyclicity and D-equivariance on those common bytes.",
        "boundary": "An exhaustive family list is not an assembled operator payload, an accepted q2 hash, or an identity replay.",
    })
    for check_id in ("q1_q2_arity_two_nilpotency", "q2_cyclic_compatibility", "D_q2_derivation"):
        row = checks[check_id]
        row["evidence"] = list(dict.fromkeys([*row["evidence"], manifest["result_id"]]))
        row["remaining_for_gate_a"] = "Replay this identity only after all minimal and auxiliary q2 components are assembled on the common 386-row payload."
        row["boundary"] = "The complete source family census supplies the domain of the test, not its result."
    value["required_hash_disposition"]["q2_hash"].update({"accepted": None, "candidate_scope": "EXHAUSTIVE_AUXILIARY_FAMILY_CENSUS_SOURCE_Q2_ASSEMBLY_OPEN"})
    for item in value["minimal_missing_bundle"]:
        if item["id"] == "M2_STRICT_Q2_D":
            item["object"] = "Assemble the minimal and seven exhaustive auxiliary cubic families into the source-certified 386-row q2/q3 payload; independently replay q1/q2, cyclicity and D-equivariance."
    value["gate_disposition"].update({
        "claim_state": "CLASSICAL_IMPORT_AUXILIARY_FAMILY_CENSUS_EXHAUSTIVE_SOURCE_Q2_ASSEMBLY_OPEN",
        "accepted_common_snapshot_hashes": 0,
    })
    value["m2_minimal_resolution"].update({
        "remaining": "The auxiliary family census is exhaustive. The single common source q2/q3 payload and its full-carrier identities remain open.",
        "boundary": "Census completion does not promote any component collection to an accepted operator hash.",
    })
    inventory = value["m2_shifted_cubic_inventory_resolution"]
    inventory.update({
        "status": "SEVEN_AUXILIARY_FAMILIES_COMPONENT_COMPLETE_AND_EXHAUSTIVE_SOURCE_Q2_ASSEMBLY_OPEN",
        "ghost_manifest_evidence": manifest["result_id"],
        "component_complete_families": 7,
        "component_open_families": 0,
        "exhaustive_full_nonlinear_BV_family_census": True,
        "complete_source_q2_q3_pullback_replayed": False,
    })
    value["m2_nonlinear_ghost_manifest_resolution"] = {
        "status": "PRIMARY_SOURCE_IMPORTED_AND_INDEPENDENTLY_REPLAYED",
        "evidence": manifest["result_id"],
        **manifest["manifest_summary"],
        "Weyl_boost_internal_algebra_abelian": True,
        "shifted_f_hat_internal_invariant": True,
        "exhaustive_in_declared_scope": True,
        "full_386_source_q2_assembled": False,
    }
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(V12.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(V12), "role": "immutable Gate-A V12 predecessor"},
        {"path": str(MANIFEST.relative_to(ROOT)), "result_or_artifact_id": manifest["result_id"], "sha256": sha(MANIFEST), "role": "primary-source-complete nonlinear Weyl/boost ghost manifest"},
    ]
    drift = []
    for source in previous["provenance"]["inputs"]:
        path = ROOT / source["path"]
        current = sha(path) if path.is_file() else None
        if current != source["sha256"]:
            drift.append({"path": source["path"], "historical_v12_sha256": source["sha256"], "current_worktree_sha256": current, "status": "RECORDED_NOT_SILENTLY_REBOUND"})
    value["transitive_provenance_drift"] = {"files_checked": len(previous["provenance"]["inputs"]), "drifted_files": len(drift), "status": "DRIFT_RECORDED_GATE_REMAINS_FAIL_CLOSED", "entries": drift}
    value["claim_flags"].update({
        "STRICT_386_EXHAUSTIVE_FULL_NONLINEAR_BV_FAMILY_CENSUS": True,
        "STRICT_386_SEVEN_AUXILIARY_CUBIC_FAMILIES_COMPONENT_COMPLETE": True,
        "STRICT_386_FULL_SOURCE_Q2_ASSEMBLED": False,
        "STRICT_386_FULL_SOURCE_Q2_PULLBACK_REPLAYED": False,
        "STRICT_386_FULL_SOURCE_Q3_PULLBACK_REPLAYED": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "QME_RESTORED": False,
    })
    value["does_not_establish"] = [item for item in previous["does_not_establish"] if "exhaustive nonlinear Weyl/conformal-boost" not in item]
    value["does_not_establish"] = list(dict.fromkeys([
        *value["does_not_establish"],
        "the assembled source q2/q3 or a common full-carrier nonlinear operator hash",
        "the full q1/q2 identity, cyclicity, D-equivariance, Gate A, causal lambda-squared closure, Hadamard data, QME restoration, or residual transfer",
    ]))
    value["next_gate"] = "Assemble the minimal and seven exhaustive auxiliary cubic families as one source-certified 386-row q2/q3 payload, then independently replay q1/q2, cyclicity and D-equivariance. M1 and M3-M6 remain independent Gate-A blockers."
    value["independent_checker"] = {"path": "quantum-weyl/classical_import/check_classical_import_gate_v13_reconciliation.py", "checks": ["V12 and manifest pins", "twenty-export and ten-check preservation", "three nonzero and four certified-zero ghost-family projection", "seven-family exhaustive promotion", "source-q2 assembly and identity firewalls", "zero accepted hashes and lifecycle firewalls"], "expected_digest": ""}
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    p = value["m2_nonlinear_ghost_manifest_resolution"]
    return f"""# Classical import Gate-A reconciliation v13

**Result:** `{value['result_id']}`

**Dependency:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

**Gate A:** `{value['gate_disposition']['gate_a_status']}`

The primary source supplies the previously omitted nonlinear boost terms.
Exact replay shows that the Weyl/boost internal algebra is Abelian and the
shifted auxiliary tensor is invariant.  The scoped manifest has
{p['nonzero_ghost_antifield_families']} nonzero ghost-antifield families and
{p['additional_nonlinear_Weyl_boost_ghost_antifield_families']} additional
Weyl/boost families.  Consequently the seven serialized auxiliary cubic
families are now an exhaustive family census.

Gate A remains fail closed with
**{value['gate_disposition']['accepted_common_snapshot_hashes']}** accepted
common hashes.  Census completion is not source-q2 assembly: the combined
386-row payload and its `q1/q2`, cyclicity and `D` identities remain open.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v13_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v13_reconciliation.py
python3 quantum-weyl/classical_import/verify_classical_import_gate_v13_reconciliation.py
python3 -m unittest quantum-weyl.classical_import.tests.test_classical_import_gate_v13_reconciliation
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
        print("CLASSICAL_IMPORT_GATE_V13_RECONCILIATION: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V13_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
