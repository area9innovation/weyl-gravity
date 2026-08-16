#!/usr/bin/env python3
"""Build Gate-A v24 after represented M3RC action/support identification."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
PREVIOUS = HERE / "certificates/CLASSICAL_IMPORT_GATE_V23_RECONCILIATION.json"
ACTION_DUAL = HERE / "certificates/STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V24_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V24.md"


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
    action = json.loads(ACTION_DUAL.read_text(encoding="utf-8"))
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V23_RECONCILIATION":
        raise ValueError("Gate V23 predecessor drift")
    if action.get("result_id") != "STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1":
        raise ValueError("M3RC action/support comparison unavailable")
    flags = action["claim_flags"]
    if (
        flags["M3RC_B_REPRESENTED_ACTION_SUPPORT_DUAL_IDENTIFICATION_COMPLETE"] is not True
        or flags["ALL_470_FORMAL_DUALS_HAVE_COMPACT_SOURCE_REPRESENTATIVES"] is not True
        or flags["ACTION_PAIRING_EQUALS_CANONICAL_940_COTANGENT_PAIRING"] is not True
        or flags["M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE"] is not False
        or flags["FULL_ALL_ENERGY_CONTINUOUS_DUAL_IDENTIFIED"] is not False
    ):
        raise ValueError("M3RC-B scope firewall drift")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v24-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V24_RECONCILIATION",
        "result_state": "M3RC_ACTION_SUPPORT_DUAL_IDENTIFIED_ON_REPRESENTED_BLOCK_M4R_M1_OPEN_GATE_FAIL_CLOSED",
        "created": "2026-08-16",
        "repository_base_commit": "24a4d9458375e66706d234a92017035f050b044c",
        "question": "Does the imported causal/action pairing close M3RC-B, and what remains before Gate A can pass?",
        "answer": "M3RC-B closes on the declared represented energies two through six. The certified causal quasi-isomorphism Lambda: Gamma_c(C)[1] to Gamma_sc(C), its compact cutoff inverse, the action/Green current identity, and the all-energy +E,-A,-L harmonic normalization give every formal residual dual an explicit compact-source representative. The resulting action pairing equals the canonical rank-940 cotangent pairing with zero declared support, recovery, crosswalk or normalization defects. This does not identify the full continuous all-energy dual or make the formal 8,980-coordinate source authoritative. Gate A remains fail closed because M4R must now replay the residual cyclic contraction and M1 must bind all objects under one common snapshot.",
        "supersedes_for_current_status": previous["result_id"],
        "historical_certificate_preserved": True,
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V24.md",
    })
    value["minimal_missing_bundle"] = [
        next(item for item in previous["minimal_missing_bundle"] if item["id"] == "M4R_TYPED_RESIDUAL_CYCLICITY"),
        next(item for item in previous["minimal_missing_bundle"] if item["id"] == "M1_COMMON_STRICT_SNAPSHOT"),
    ]
    cyclic = one(value["export_reconciliation"], "export_id", "cyclic_pairing")
    cyclic.update({
        "status": "RECEIVER_VERIFIED_SCOPED",
        "evidence": list(dict.fromkeys([*cyclic["evidence"], action["result_id"]])),
        "established": "M4L closes the local action-derived pairing; M3RC-A constructs the formal cotangent SDR; M3RC-B identifies all 470 residual duals with compact-source causal classes and the action-derived Cauchy pairing at rank 940.",
        "remaining_for_gate_a": "Replay M4R residual cyclicity on the action-identified carrier, then bind every object under M1.",
        "boundary": "The represented finite action/support dual is complete; the full all-energy continuous dual and common all-object freeze are not claimed.",
    })
    cyclic_check = one(value["freeze_check_reconciliation"], "check_id", "cyclic_compatibility")
    cyclic_check.update({
        "status": "BLOCKED_MISSING_COMMON_SNAPSHOT",
        "evidence": list(dict.fromkeys([*cyclic_check["evidence"], action["result_id"]])),
        "established": "The formal cotangent comparison and its represented compact-source/action pairing identification are exact.",
        "remaining_for_gate_a": "M4R cyclic transfer side conditions and the M1 common freeze remain absent.",
        "boundary": "M3RC-B readiness is not itself the M4R receiver replay or the common frozen snapshot.",
    })
    value["residual_cyclic_carrier_obstruction_resolution"].update({
        "M3RC_CYCLIC_RESIDUAL_CARRIER_COMPLETION": "COMPLETE_ON_REPRESENTED_ACTION_SUPPORT_BLOCK",
        "M4R_TYPED_RESIDUAL_CYCLICITY": "READY",
    })
    value["m3rc_formal_cotangent_dual_resolution"].update({
        "M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION": "COMPLETE_ON_REPRESENTED_ENERGIES_2_THROUGH_6",
        "M4R_TYPED_RESIDUAL_CYCLICITY": "READY",
    })
    support = action["support_dual_identification"]
    pairing = action["action_pairing_identification"]
    value["m3rc_action_support_dual_resolution"] = {
        "status": action["result_state"],
        "evidence": action["result_id"],
        "certificate_sha256": sha(ACTION_DUAL),
        "represented_primal_modes": pairing["positive_frequency_dimension"],
        "compact_source_dual_classes": support["compact_source_representatives"],
        "phase_space_dimension": pairing["phase_space_dimension"],
        "action_pairing_rank": pairing["phase_pairing_rank"],
        "positive_krein_inertia": pairing["positive_krein_inertia"],
        "support_exact_sequence_defects": support["support_exact_sequence_defects"],
        "compact_source_support_defects": support["compact_source_support_defects"],
        "causal_recovery_defects": support["causal_recovery_defects"],
        "pairing_identification_defects": pairing["pairing_identification_defects"],
        "basis_crosswalk_defects": pairing["basis_crosswalk_defects"],
        "full_continuous_dual_claimed": support["full_continuous_dual_of_all_smooth_sections_claimed"],
        "M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION": "COMPLETE_ON_REPRESENTED_ENERGIES_2_THROUGH_6",
        "M4R_TYPED_RESIDUAL_CYCLICITY": "READY",
        "accepted_common_snapshot_hashes_added": 0,
    }
    value["gate_disposition"].update({
        "gate_a_status": "FAIL_CLOSED",
        "claim_state": "CLASSICAL_IMPORT_M3L_M3R_M3RC_A_M3RC_B_M4L_COMPLETE_M4R_M1_OPEN",
        "publishable_quantum_results_allowed_by_gate_a": False,
    })
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {
            "path": str(PREVIOUS.relative_to(ROOT)),
            "result_or_artifact_id": previous["result_id"],
            "sha256": sha(PREVIOUS),
            "role": "immutable Gate V23 predecessor",
        },
        {
            "path": str(ACTION_DUAL.relative_to(ROOT)),
            "result_or_artifact_id": action["result_id"],
            "sha256": sha(ACTION_DUAL),
            "role": "receiver-verified represented compact-source/action dual identification",
        },
    ]
    value["claim_flags"].update({
        "M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION_COMPLETE": True,
        "M3RC_B_REPRESENTED_ACTION_SUPPORT_DUAL_IDENTIFICATION_COMPLETE": True,
        "ALL_470_FORMAL_DUALS_HAVE_COMPACT_SOURCE_REPRESENTATIVES": True,
        "ACTION_PAIRING_EQUALS_CANONICAL_940_COTANGENT_PAIRING": True,
        "M3RC_DUAL_COMPARISON_MAPS_CONSTRUCTED": True,
        "M4R_TYPED_RESIDUAL_CYCLICITY_READY": True,
        "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE": False,
        "FORMAL_DUAL_IDENTIFIED_WITH_ACTION_SUPPORT_DUAL": False,
        "FULL_ALL_ENERGY_CONTINUOUS_DUAL_IDENTIFIED": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "QME_RESTORED": False,
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "the full continuous dual of every smooth or all-energy solution space",
        "that the 8,980-coordinate formal cotangent source is the unchanged authoritative classical BV source",
        "M4R, another accepted Gate-A hash, M1, Hadamard data, QME restoration or residual quantum transfer",
    ]))
    value["next_gate"] = "Replay M4R on the action-identified 940-coordinate residual carrier, including nondegeneracy, q_res cyclicity, p=iota-sharp, homotopy skew-adjointness and residual-transfer cyclic side conditions. Then bind M1 before any quantum promotion."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v24_reconciliation.py",
        "checks": [
            "Gate V23 predecessor and M3RC-B content pins",
            "independent M3RC-B receiver replay",
            "unchanged twenty exports, ten checks and one accepted hash",
            "M3RC-B removal and M4R/M1 dependency order",
            "470 compact-source representatives and exact rank-940 action pairing",
            "represented finite dual versus full continuous dual firewall",
            "M4R/Gate-A/Hadamard/QME/residual-transfer firewalls",
            "canonical reconciliation digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    resolution = value["m3rc_action_support_dual_resolution"]
    return f"""# Classical import Gate-A reconciliation v24

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
**Gate A:** `FAIL_CLOSED`

M3RC-B is complete on represented energies two through six.  The imported
causal cutoff theorem supplies {resolution['compact_source_dual_classes']}
compact-source dual classes for the {resolution['represented_primal_modes']}
positive-frequency E/A/L modes.  The Green pairing equals the action-derived
Cauchy pairing, and its suspended {resolution['phase_space_dimension']}-row
form has exact rank {resolution['action_pairing_rank']} with zero support,
recovery, crosswalk, or pairing-identification defects.

This is a finite represented subquotient result, not identification of the
full continuous dual of all smooth solutions.  M4R is now ready but has not
been replayed.  M1 remains last, no common snapshot hash was added, and Gate A
therefore remains fail closed.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v24_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v24_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v24_reconciliation.py
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
        print("CLASSICAL_IMPORT_GATE_V24_RECONCILIATION: generated artifacts current")
        return 0
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V24_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
