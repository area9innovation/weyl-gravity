#!/usr/bin/env python3
"""Build Gate-A v26 after the strict M1 typed-diagram preflight."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
PREVIOUS = HERE / "certificates/CLASSICAL_IMPORT_GATE_V25_RECONCILIATION.json"
PREFLIGHT = HERE / "certificates/STRICT_M1_COMMON_SNAPSHOT_PREFLIGHT_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V26_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V26.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    body = deepcopy(value)
    body.get("independent_checker", {}).pop("expected_digest", None)
    return hashlib.sha256(json.dumps(
        body, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode()).hexdigest()


def build() -> dict[str, Any]:
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V25_RECONCILIATION":
        raise ValueError("Gate V25 predecessor drift")
    if preflight.get("result_id") != "STRICT_M1_COMMON_SNAPSHOT_PREFLIGHT_V1":
        raise ValueError("M1 preflight unavailable")
    flags = preflight["claim_flags"]
    if (
        flags["M1_PREFLIGHT_COMPLETE"] is not True
        or flags["M1_TYPED_DIAGRAM_REQUIRED"] is not True
        or flags["M1_COMMON_STRICT_SNAPSHOT_COMPLETE"] is not False
        or flags["FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX"] is not False
    ):
        raise ValueError("M1 preflight firewall drift")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v26-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V26_RECONCILIATION",
        "result_state": "M1_PREFLIGHT_COMPLETE_THREE_CONSTRUCTION_PACKAGES_OPEN_GATE_FAIL_CLOSED",
        "created": "2026-08-16",
        "repository_base_commit": "89652649493e7a816aa43df642be878362f3b65b",
        "question": "Does M1 reduce to binding existing hashes, and what exact construction remains before Gate A can pass?",
        "answer": "No. The independent M1 preflight finds fourteen of twenty exports object-ready, two blocked by the missing explicit 386-row grading ledger and four blocked by the missing actual local-to-action-residual composite contraction. Four of seven hash objects are ready to bind, three remain blocked, and none of ten checks has run on final common bytes. M1 is therefore split into M1A typed ledger, M1B represented composite contraction and M1C immutable binding/replay. Gate A remains fail closed at one accepted hash.",
        "supersedes_for_current_status": previous["result_id"],
        "historical_certificate_preserved": True,
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V26.md",
    })
    value["minimal_missing_bundle"] = [{
        "id": "M1_COMMON_STRICT_SNAPSHOT",
        "object": "One content-addressed typed diagram binding the authoritative 386-row local source, endpoint and represented residual targets without identifying distinct carrier categories.",
        "work_packages": [row["id"] for row in preflight["m1_work_packages"]],
        "unlocks": ["all seven accepted top-level hashes", "independent common-domain replay"],
    }]
    counts = preflight["counts"]
    value["m1_common_snapshot_preflight_resolution"] = {
        "status": preflight["result_state"],
        "evidence": preflight["result_id"],
        "certificate_sha256": sha(PREFLIGHT),
        "snapshot_shape": preflight["authoritative_source_decision"]["snapshot_shape"],
        "authoritative_local_source": preflight["authoritative_source_decision"]["local_source"],
        "formal_8980_source_authoritative": preflight["authoritative_source_decision"]["formal_8980_source_authoritative"],
        "carrier_count": len(preflight["carrier_inventory"]),
        "typed_edge_count": len(preflight["cross_category_edges"]),
        "exports_total": counts["exports_total"],
        "exports_object_ready": counts["exports_common_object_ready"],
        "exports_blocked_typed_ledger": counts["exports_blocked_full_typed_ledger"],
        "exports_blocked_composite": counts["exports_blocked_composite_contraction"],
        "hashes_total": counts["hashes_total"],
        "hash_objects_ready": counts["hash_objects_ready_await_binding"],
        "hashes_blocked": counts["hashes_blocked_before_binding"],
        "freeze_checks_total": counts["freeze_checks_total"],
        "freeze_checks_common_snapshot_replayed": counts["freeze_checks_common_snapshot_replayed"],
        "missing_local_row_fields": preflight["local_row_ledger_audit"]["missing_explicit_fields"],
        "work_packages": preflight["m1_work_packages"],
        "accepted_common_snapshot_hashes_added": 0,
    }
    value["gate_disposition"].update({
        "gate_a_status": "FAIL_CLOSED",
        "claim_state": "CLASSICAL_IMPORT_M1_PREFLIGHT_COMPLETE_M1A_M1B_M1C_OPEN",
        "publishable_quantum_results_allowed_by_gate_a": False,
    })
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREVIOUS.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(PREVIOUS), "role": "immutable Gate V25 predecessor"},
        {"path": str(PREFLIGHT.relative_to(ROOT)), "result_or_artifact_id": preflight["result_id"], "sha256": sha(PREFLIGHT), "role": "independently checked M1 typed-diagram preflight"},
    ]
    value["claim_flags"].update({
        "M1_PREFLIGHT_COMPLETE": True,
        "M1_TYPED_DIAGRAM_REQUIRED": True,
        "M1_IS_CLERICAL_HASH_BUNDLE": False,
        "M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE": False,
        "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE": False,
        "M1C_COMMON_MANIFEST_REPLAY_COMPLETE": False,
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
        "M1A, M1B or M1C completion merely from the preflight inventory",
        "a passed Gate A, Hadamard state, renormalized products, QME restoration or residual quantum transfer",
    ]))
    value["next_gate"] = "Construct M1A from authoritative row semantics; construct and replay M1B on that typed diagram; only then bind all twenty exports and seven hashes and replay all ten checks as M1C."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v26_reconciliation.py",
        "checks": [
            "Gate V25 predecessor and M1 preflight content pins",
            "independent Gate V25 and preflight receiver replay",
            "unchanged twenty exports, ten checks and one accepted hash",
            "eight-carrier and seven-edge typed-diagram projection",
            "fourteen-ready/two-ledger/four-composite export partition",
            "four-ready/three-blocked hash-object partition",
            "M1A/M1B/M1C ordering and lifecycle",
            "formal-source/Gate-A/Hadamard/QME firewalls",
            "canonical reconciliation digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    resolution = value["m1_common_snapshot_preflight_resolution"]
    packages = "\n".join(
        f"{row['order']}. **{row['id']}** — `{row['status']}`: {row['deliverable']}"
        for row in resolution["work_packages"]
    )
    return f"""# Classical import Gate-A reconciliation v26

**Result:** `{value['result_id']}`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

**Gate A:** `FAIL_CLOSED`

The M1 preflight proves that the sole remaining package is mathematical work,
not a clerical hash sweep.  {resolution['exports_object_ready']} of
{resolution['exports_total']} exports are object-ready; two require the full
typed row ledger and four require the actual represented composite
contraction.  Four of seven hash objects are ready, while no final common
snapshot check has yet been replayed.

## Ordered construction

{packages}

The formal 8,980-coordinate comparison source remains non-authoritative.  No
new hash is accepted, and no Hadamard, renormalization, QME or residual-transfer
lifecycle state is promoted.
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return ((json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), report(value).encode())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("CLASSICAL_IMPORT_GATE_V26_RECONCILIATION: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V26_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
