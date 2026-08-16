#!/usr/bin/env python3
"""Build Gate-A v25 after finite represented M4R residual cyclicity."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
PREVIOUS = HERE / "certificates/CLASSICAL_IMPORT_GATE_V24_RECONCILIATION.json"
M4R = HERE / "certificates/STRICT_TYPED_RESIDUAL_CYCLICITY_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V25_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V25.md"


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
    m4r = json.loads(M4R.read_text(encoding="utf-8"))
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V24_RECONCILIATION":
        raise ValueError("Gate V24 predecessor drift")
    if m4r.get("result_id") != "STRICT_TYPED_RESIDUAL_CYCLICITY_V1":
        raise ValueError("M4R result unavailable")
    flags = m4r["claim_flags"]
    if (
        flags["M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE"] is not True
        or flags["M4R_REPRESENTED_PROJECTION_EQUALS_INCLUSION_SHARP"] is not True
        or flags["M4R_REPRESENTED_HOMOTOPY_SKEW_ADJOINT"] is not True
        or flags["FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX"] is not False
        or flags["M1_COMMON_STRICT_SNAPSHOT_COMPLETE"] is not False
    ):
        raise ValueError("M4R/M1 scope firewall drift")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v25-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V25_RECONCILIATION",
        "result_state": "M4R_COMPLETE_ON_ACTION_IDENTIFIED_REPRESENTED_CARRIER_M1_ONLY_GATE_FAIL_CLOSED",
        "created": "2026-08-16",
        "repository_base_commit": "24a4d9458375e66706d234a92017035f050b044c",
        "question": "Does the exact finite cyclic contraction close M4R, and what remains before Gate A can pass?",
        "answer": "M4R closes on the action-identified residual carrier at represented energies two through six. The receiver reconstructs all five formal cotangent comparison blocks and verifies q_res cyclicity, projection equals inclusion-adjoint, homotopy skew-adjointness, inclusion isometry, contraction and normalized side conditions with zero defects. M3RC-B supplies the compact-source action meaning of the rank-940 residual form. This does not promote the formal 8,980-coordinate comparison source to the authoritative full BV source. M1 is now the sole minimal missing package: one common strict snapshot must bind every local, nonlinear, causal and residual object and allow receiver replay of all twenty exports, ten checks and seven hashes. Gate A remains fail closed at one accepted hash.",
        "supersedes_for_current_status": previous["result_id"],
        "historical_certificate_preserved": True,
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V25.md",
    })
    value["minimal_missing_bundle"] = [
        next(item for item in previous["minimal_missing_bundle"] if item["id"] == "M1_COMMON_STRICT_SNAPSHOT")
    ]
    cyclic = one(value["export_reconciliation"], "export_id", "cyclic_pairing")
    cyclic.update({
        "status": "RECEIVER_VERIFIED_SCOPED",
        "evidence": list(dict.fromkeys([*cyclic["evidence"], m4r["result_id"]])),
        "established": "M4L supplies the local action-derived cyclic structure; M3RC identifies the compact-source residual cotangent dual; M4R exactly replays the normalized cyclic contraction on all 940 represented residual coordinates.",
        "remaining_for_gate_a": "Bind the local and represented residual structures under the one M1 authoritative strict snapshot and accept the common pairing hash only after replay.",
        "boundary": "The M4R theorem is finite and represented; it does not make the 8,980-coordinate formal comparison source authoritative or identify an all-energy continuous dual.",
    })
    cyclic_check = one(value["freeze_check_reconciliation"], "check_id", "cyclic_compatibility")
    cyclic_check.update({
        "status": "BLOCKED_MISSING_COMMON_SNAPSHOT",
        "evidence": list(dict.fromkeys([*cyclic_check["evidence"], m4r["result_id"]])),
        "established": "Local M4L and represented residual M4R cyclicity both pass independently, including exact adjoint and normalized contraction side conditions.",
        "remaining_for_gate_a": "Replay the same typed identities after M1 binds all objects and bases to one authoritative source snapshot.",
        "boundary": "Two category-correct scoped theorems are not yet one common frozen-source theorem.",
    })
    value["residual_cyclic_carrier_obstruction_resolution"].update({
        "M4R_TYPED_RESIDUAL_CYCLICITY": "COMPLETE_ON_REPRESENTED_ACTION_IDENTIFIED_BLOCK",
    })
    value["m3rc_formal_cotangent_dual_resolution"].update({
        "M4R_TYPED_RESIDUAL_CYCLICITY": "COMPLETE_ON_REPRESENTED_ACTION_IDENTIFIED_BLOCK",
    })
    value["m3rc_action_support_dual_resolution"].update({
        "M4R_TYPED_RESIDUAL_CYCLICITY": "COMPLETE_ON_REPRESENTED_ACTION_IDENTIFIED_BLOCK",
    })
    replay = m4r["exact_cyclic_replay"]
    carrier = m4r["typed_carrier"]
    value["m4r_typed_residual_cyclicity_resolution"] = {
        "status": m4r["result_state"],
        "evidence": m4r["result_id"],
        "certificate_sha256": sha(M4R),
        "formal_comparison_source_dimension": replay["formal_source_dimension"],
        "action_identified_residual_dimension": replay["residual_dimension"],
        "residual_pairing_rank": replay["residual_pairing_rank"],
        "energy_blocks_replayed": len(replay["block_replays"]),
        "all_identity_defects": replay["all_identity_defects"],
        "action_pairing_identification_defects": carrier["action_pairing_identification_defects"],
        "q_res_cyclic": flags["M4R_REPRESENTED_Q_RES_CYCLIC"],
        "projection_equals_inclusion_sharp": flags["M4R_REPRESENTED_PROJECTION_EQUALS_INCLUSION_SHARP"],
        "homotopy_skew_adjoint": flags["M4R_REPRESENTED_HOMOTOPY_SKEW_ADJOINT"],
        "formal_source_authoritative": carrier["formal_source_is_authoritative_full_BV_source"],
        "M4R_TYPED_RESIDUAL_CYCLICITY": "COMPLETE_ON_REPRESENTED_ENERGIES_2_THROUGH_6",
        "M1_COMMON_STRICT_SNAPSHOT": "SOLE_MINIMAL_MISSING_PACKAGE",
        "accepted_common_snapshot_hashes_added": 0,
    }
    value["gate_disposition"].update({
        "gate_a_status": "FAIL_CLOSED",
        "claim_state": "CLASSICAL_IMPORT_M3L_M3R_M3RC_A_M3RC_B_M4L_M4R_COMPLETE_M1_OPEN",
        "publishable_quantum_results_allowed_by_gate_a": False,
    })
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {
            "path": str(PREVIOUS.relative_to(ROOT)),
            "result_or_artifact_id": previous["result_id"],
            "sha256": sha(PREVIOUS),
            "role": "immutable Gate V24 predecessor",
        },
        {
            "path": str(M4R.relative_to(ROOT)),
            "result_or_artifact_id": m4r["result_id"],
            "sha256": sha(M4R),
            "role": "receiver-verified finite represented typed residual cyclic contraction",
        },
    ]
    value["claim_flags"].update({
        "M4R_TYPED_RESIDUAL_CYCLICITY_READY": True,
        "M4R_REPRESENTED_Q_RES_CYCLIC": True,
        "M4R_REPRESENTED_PROJECTION_EQUALS_INCLUSION_SHARP": True,
        "M4R_REPRESENTED_HOMOTOPY_SKEW_ADJOINT": True,
        "M4R_REPRESENTED_NORMALIZED_CYCLIC_CONTRACTION_COMPLETE": True,
        "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE": True,
        "M1_COMMON_STRICT_SNAPSHOT_COMPLETE": False,
        "FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "QME_RESTORED": False,
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "that the formal 8,980-coordinate comparison source is the authoritative full classical BV source",
        "M1, another accepted Gate-A hash, a passed Gate A, Hadamard data, renormalized products, QME restoration or residual quantum transfer",
    ]))
    value["next_gate"] = "Construct M1 as one content-addressed strict source manifest binding all twenty exports, all local and residual maps, all seven required hashes and the M4R compact-source dual dictionary. Independently replay all ten checks on those exact bytes before passing Gate A."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v25_reconciliation.py",
        "checks": [
            "Gate V24 predecessor and M4R content pins",
            "independent M4R checker replay",
            "unchanged twenty exports, ten checks and one accepted hash",
            "M4R removal and sole M1 missing package",
            "exact 8,980-to-940 five-block cyclic contraction projection",
            "q_res cyclicity, projection adjoint and homotopy skewness",
            "formal comparison source versus authoritative full source firewall",
            "M1/Gate-A/Hadamard/QME/residual-transfer firewalls",
            "canonical reconciliation digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    resolution = value["m4r_typed_residual_cyclicity_resolution"]
    return f"""# Classical import Gate-A reconciliation v25

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
**Gate A:** `FAIL_CLOSED`

M4R is complete on represented energies two through six.  The receiver replays
{resolution['energy_blocks_replayed']} formal cotangent blocks from
{resolution['formal_comparison_source_dimension']} comparison coordinates to
{resolution['action_identified_residual_dimension']} action-identified residual
coordinates.  The residual odd pairing has exact rank
{resolution['residual_pairing_rank']}; q-res cyclicity, projection-adjointness,
homotopy skewness, contraction and normalized side conditions have
{resolution['all_identity_defects']} defects.

M1 is now the sole minimal missing package.  The formal comparison source is
not declared authoritative, no common snapshot hash is added, and Gate A
remains fail closed at one of seven hashes.  No Hadamard, renormalization, QME
or residual-transfer lifecycle state is promoted.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v25_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v25_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v25_reconciliation.py
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
        print("CLASSICAL_IMPORT_GATE_V25_RECONCILIATION: generated artifacts current")
        return 0
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V25_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
