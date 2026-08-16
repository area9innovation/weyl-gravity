#!/usr/bin/env python3
"""Build Gate-A v23 after the formal cotangent-dual comparison."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
PREVIOUS = HERE / "certificates/CLASSICAL_IMPORT_GATE_V22_RECONCILIATION.json"
DUAL = HERE / "certificates/STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V23_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V23.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    body = deepcopy(value)
    body.get("independent_checker", {}).pop("expected_digest", None)
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def one(rows: list[dict[str, Any]], field: str, value: str) -> dict[str, Any]:
    matches = [row for row in rows if row[field] == value]
    if len(matches) != 1:
        raise ValueError(f"expected one {field}={value}, found {len(matches)}")
    return matches[0]


def build() -> dict[str, Any]:
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    dual = json.loads(DUAL.read_text(encoding="utf-8"))
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V22_RECONCILIATION":
        raise ValueError("Gate V22 predecessor drift")
    if dual.get("result_id") != "STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1":
        raise ValueError("formal cotangent-dual comparison unavailable")
    flags = dual["claim_flags"]
    if (
        flags["ORIGINAL_DFINITE_H1_ZERO"] is not True
        or flags["FORMAL_940_COTANGENT_RESIDUAL_COMPARISON_CONSTRUCTED"] is not True
        or flags["FORMAL_DUAL_IDENTIFIED_WITH_ACTION_SUPPORT_DUAL"] is not False
        or flags["M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE"] is not False
    ):
        raise ValueError("formal cotangent-dual firewall drift")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v23-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V23_RECONCILIATION",
        "result_state": "M3RC_FORMAL_DUAL_COMPLETE_ACTION_SUPPORT_IDENTIFICATION_M4R_M1_OPEN_GATE_FAIL_CLOSED",
        "created": "2026-08-16",
        "repository_base_commit": "4f054fc718f818b6603964fbe016429671f73443",
        "question": "Does the exact transposed SDR complete M3RC, and what remains before residual cyclicity can be claimed?",
        "answer": "It completes only M3RC-A, the finite formal cotangent-dual comparison. The unchanged 4,490-coordinate D-finite source has H0 dimension 470 and H1 dimension zero, so it cannot retract to a 940-coordinate residual carrier. Its explicit 8,980-coordinate shifted cotangent completion does retract exactly to the 940-coordinate cotangent residual carrier through q_dual=-q0^T, iota_dual=pi_cl^T, pi_dual=iota_cl^T and s_dual=-s_cl^T; the canonical odd pairing is nondegenerate and all declared cyclic SDR identities have zero defects. M3RC-B remains open because no support/topology class or harmonic integration theorem identifies that formal algebraic dual with the action-derived BV dual. Gate A therefore remains fail closed with M3RC-B, M4R and M1 open.",
        "supersedes_for_current_status": previous["result_id"],
        "historical_certificate_preserved": True,
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V23.md",
    })
    value["minimal_missing_bundle"] = [
        {
            "id": "M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION",
            "object": "Choose paired support/topology classes for the endpoint solution and source complexes, construct the harmonic integration comparison to the finite algebraic dual, and identify the action-derived BV pairing and adjoint maps with the formal cotangent comparison.",
            "unlocks": ["action-derived residual BV pairing", "well-typed M4R replay"],
        },
        next(item for item in previous["minimal_missing_bundle"] if item["id"] == "M4R_TYPED_RESIDUAL_CYCLICITY"),
        next(item for item in previous["minimal_missing_bundle"] if item["id"] == "M1_COMMON_STRICT_SNAPSHOT"),
    ]
    cyclic = one(value["export_reconciliation"], "export_id", "cyclic_pairing")
    cyclic.update({
        "status": "RECEIVER_VERIFIED_SCOPED",
        "evidence": list(dict.fromkeys([*cyclic["evidence"], dual["result_id"]])),
        "established": "M4L closes the local action-derived pairing, the one-sided M3R pullback is exactly rank-zero, and M3RC-A constructs an exact cyclic 8,980-to-940 formal cotangent SDR by transposing the certified finite comparison.",
        "remaining_for_gate_a": "Identify the formal algebraic dual with declared action/support dual classes (M3RC-B), then replay M4R and bind M1.",
        "boundary": "A canonical finite cotangent evaluation pairing is not automatically the integrated action-derived BV pairing on a selected topological support dual.",
    })
    cyclic_check = one(value["freeze_check_reconciliation"], "check_id", "cyclic_compatibility")
    cyclic_check.update({
        "status": "BLOCKED_MISSING_COMMON_SNAPSHOT",
        "evidence": list(dict.fromkeys([*cyclic_check["evidence"], dual["result_id"]])),
        "established": "The formal cotangent completion has exact nondegeneracy, q-cyclicity, homotopy skewness and inclusion isometry.",
        "remaining_for_gate_a": "M3RC-B action/support identification, M4R replay and the M1 common freeze remain absent.",
        "boundary": "Formal algebraic cyclicity cannot be promoted across an unconstructed action/support pairing comparison.",
    })
    value["residual_cyclic_carrier_obstruction_resolution"].update({
        "M3RC_CYCLIC_RESIDUAL_CARRIER_COMPLETION": "SPLIT_FORMAL_COMPLETE_ACTION_SUPPORT_OPEN",
        "M4R_TYPED_RESIDUAL_CYCLICITY": "BLOCKED_BY_M3RC_B",
    })
    value["m3rc_formal_cotangent_dual_resolution"] = {
        "status": dual["result_state"],
        "evidence": dual["result_id"],
        "certificate_sha256": sha(DUAL),
        "original_source_full_dimension": dual["same_source_impossibility"]["original_source_full_dimension"],
        "original_source_H0_dimension": dual["same_source_impossibility"]["original_source_degree_zero_cohomology_dimension"],
        "original_source_H1_dimension": dual["same_source_impossibility"]["original_source_degree_one_cohomology_dimension"],
        "same_source_retract_to_940_possible": dual["same_source_impossibility"]["same_source_deformation_retract_to_940_possible"],
        "formal_cotangent_source_dimension": dual["formal_cotangent_completion"]["full_dimension"],
        "formal_cotangent_residual_dimension": dual["formal_cotangent_completion"]["residual_dimension"],
        "formal_full_pairing_rank": dual["formal_cotangent_completion"]["full_pairing_rank"],
        "formal_residual_pairing_rank": dual["formal_cotangent_completion"]["residual_pairing_rank"],
        "formal_identity_defects": dual["formal_cotangent_completion"]["all_declared_identity_defects"],
        "M3RC_A_FORMAL_COTANGENT_DUAL_COMPARISON": "COMPLETE",
        "M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION": "OPEN",
        "M4R_TYPED_RESIDUAL_CYCLICITY": "BLOCKED_BY_M3RC_B",
        "accepted_common_snapshot_hashes_added": 0,
    }
    value["gate_disposition"].update({
        "gate_a_status": "FAIL_CLOSED",
        "claim_state": "CLASSICAL_IMPORT_M3L_M3R_PRIMAL_M3RC_A_M4L_COMPLETE_M3RC_B_M4R_M1_OPEN",
        "publishable_quantum_results_allowed_by_gate_a": False,
    })
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {
            "path": str(PREVIOUS.relative_to(ROOT)),
            "result_or_artifact_id": previous["result_id"],
            "sha256": sha(PREVIOUS),
            "role": "immutable Gate V22 predecessor",
        },
        {
            "path": str(DUAL.relative_to(ROOT)),
            "result_or_artifact_id": dual["result_id"],
            "sha256": sha(DUAL),
            "role": "receiver-verified same-source cohomology obstruction and formal cotangent-dual SDR",
        },
    ]
    value["claim_flags"].update({
        "ORIGINAL_DFINITE_H1_ZERO": True,
        "UNCHANGED_4490_SOURCE_CAN_RETRACT_TO_940_RESIDUAL": False,
        "M3RC_A_FORMAL_COTANGENT_DUAL_COMPARISON_COMPLETE": True,
        "M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION_COMPLETE": False,
        "FORMAL_8980_COTANGENT_SOURCE_CONSTRUCTED": True,
        "FORMAL_940_COTANGENT_RESIDUAL_COMPARISON_CONSTRUCTED": True,
        "FORMAL_COTANGENT_PAIRING_NONDEGENERATE": True,
        "FORMAL_COTANGENT_SDR_CYCLIC": True,
        "FORMAL_DUAL_IDENTIFIED_WITH_ACTION_SUPPORT_DUAL": False,
        "M3RC_DUAL_COMPARISON_MAPS_CONSTRUCTED": False,
        "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "QME_RESTORED": False,
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "that the 8,980-coordinate formal cotangent completion is the unchanged authoritative D-finite BV source",
        "a selected continuous action/support dual or harmonic integration identification",
        "M3RC-B, M4R, another accepted Gate-A hash, M1, Hadamard data, QME restoration or residual quantum transfer",
    ]))
    value["next_gate"] = "Construct M3RC-B by selecting paired support/topology classes and proving that harmonic integration identifies the action-derived BV pairing and adjoint maps with the exact formal cotangent comparison. Only then replay M4R and bind M1."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v23_reconciliation.py",
        "checks": [
            "Gate V22 predecessor and formal-dual content pins",
            "independent formal cotangent-dual checker replay",
            "unchanged twenty exports, ten checks and one accepted hash",
            "M3RC-A removal and M3RC-B/M4R/M1 dependency order",
            "same-source 4490-to-940 cohomology obstruction",
            "formal cyclicity versus action/support identification firewall",
            "Gate-A/Hadamard/QME/residual-transfer firewalls",
            "canonical reconciliation digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    resolution = value["m3rc_formal_cotangent_dual_resolution"]
    return f"""# Classical import Gate-A reconciliation v23

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
**Gate A:** `FAIL_CLOSED`

The unchanged {resolution['original_source_full_dimension']}-coordinate
D-finite source has H0 dimension {resolution['original_source_H0_dimension']}
and H1 dimension {resolution['original_source_H1_dimension']}; it cannot
retract to a 940-coordinate residual carrier.

M3RC-A is nevertheless exact after a declared formal cotangent completion.
The {resolution['formal_cotangent_source_dimension']}-coordinate doubled source
retracts onto {resolution['formal_cotangent_residual_dimension']} residual
coordinates, with full and residual odd-pairing ranks
{resolution['formal_full_pairing_rank']} and
{resolution['formal_residual_pairing_rank']} and zero declared defects.

M3RC-B remains open: no support/topology choice or harmonic integration theorem
identifies this algebraic dual with the action-derived BV dual.  M4R therefore
remains blocked, M1 remains last, and no new top-level hash is accepted.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v23_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v23_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v23_reconciliation.py
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (
        (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(),
        report(value).encode(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.exists() or path.read_bytes() != content]
    if args.check:
        if stale:
            raise SystemExit("stale generated artifacts: " + ", ".join(stale))
        print("CLASSICAL_IMPORT_GATE_V23_RECONCILIATION: generated artifacts current")
        return 0
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V23_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
