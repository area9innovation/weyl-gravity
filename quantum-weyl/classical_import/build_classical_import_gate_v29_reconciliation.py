#!/usr/bin/env python3
"""Build Gate-A v29 after the exact M1B primal composite contraction."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
PREVIOUS = HERE / "certificates/CLASSICAL_IMPORT_GATE_V28_RECONCILIATION.json"
M1B_PRIMAL = HERE / "certificates/STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1.json"
SCHEMA = HERE / "schema/quantum-weyl-classical-import-gate-v29-reconciliation-v1.schema.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V29_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V29.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    body = deepcopy(value)
    body.get("independent_checker", {}).pop("expected_digest", None)
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def build() -> dict[str, Any]:
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    primal = json.loads(M1B_PRIMAL.read_text(encoding="utf-8"))
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V28_RECONCILIATION":
        raise ValueError("Gate V28 predecessor drift")
    flags = primal.get("claim_flags", {})
    if (
        primal.get("result_id") != "STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1"
        or flags.get("M1B_PRIMAL_COMPOSITE_CONTRACTION_COMPLETE") is not True
        or flags.get("M1B_ACTION_DUAL_LIFT_COMPLETE") is not False
        or flags.get("M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE") is not False
        or flags.get("CLASSICAL_IMPORT_GATE_PASSED") is not False
    ):
        raise ValueError("M1B primal lifecycle firewall drift")

    aggregate = primal["represented_contraction"]["aggregate"]
    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v29-reconciliation-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "result_id": "CLASSICAL_IMPORT_GATE_V29_RECONCILIATION",
        "result_state": "M1B_PRIMAL_COMPOSITE_COMPLETE_ACTION_DUAL_CYCLIC_AND_M1C_OPEN_GATE_FAIL_CLOSED",
        "created": "2026-08-16",
        "repository_base_commit": "0a17388b4837808fc3f0f2504114ac011e38a17f",
        "question": "What does the exact M1B primal composite settle, and what remains before Gate A can pass?",
        "answer": "The primal half of M1B is complete on the declared energy-2-through-6 D-finite domain. Exact removal of 205 isolated test doublets gives a 4,080-to-470 normalized endpoint contraction, and the standard composition lemma lifts it through the support-local 386-to-30 graph contraction as a typed operator DAG. This is not a 386-by-470 component matrix and not an arbitrary-smooth support-local contraction. The action-derived compact-source dual, rank-940 cyclic replay and M1C common manifest remain open, so Gate A stays fail closed at one of seven accepted hashes.",
        "supersedes_for_current_status": previous["result_id"],
        "historical_certificate_preserved": True,
        "human_report": str(REPORT.relative_to(ROOT)),
    })
    resolution = value["m1_common_snapshot_preflight_resolution"]
    work = deepcopy(resolution["work_packages"])
    work[1].update({
        "status": "PRIMAL_COMPLETE_ACTION_DUAL_AND_CYCLIC_OPEN",
        "deliverable": "Primal complete: exact 4,080-to-470 represented contraction and typed 386-through-30-to-470 composite DAG. Remaining: compact-source action-dual lift and rank-940 typed cyclic replay.",
    })
    work[2]["status"] = "OPEN_AFTER_M1B_ACTION_DUAL_AND_CYCLIC_REPLAY"
    resolution.update({
        "work_packages": work,
        "m1b_primal_composite_contraction_complete": True,
        "m1b_action_dual_lift_complete": False,
        "m1b_typed_cyclic_replay_complete": False,
        "m1b_represented_composite_contraction_complete": False,
        "accepted_common_snapshot_hashes_added": 0,
    })
    value["m1b_primal_completion_resolution"] = {
        "result_id": primal["result_id"],
        "certificate_sha256": sha(M1B_PRIMAL),
        "content_sha256": primal["content_sha256"],
        "domain": primal["scope"]["domain"],
        "energies": primal["scope"]["energies"],
        "represented_endpoint_rows": aggregate["represented_rows"],
        "primal_residual_rows": aggregate["residual_rows"],
        "q0_nonzero_entries": aggregate["q0_nonzero_entries"],
        "homotopy_nonzero_entries": aggregate["homotopy_nonzero_entries"],
        "inclusion_nonzero_entries": aggregate["iota_nonzero_entries"],
        "projection_nonzero_entries": aggregate["pi_nonzero_entries"],
        "represented_identity_defects": sum(primal["represented_contraction"]["exact_replay"].values()),
        "formal_composition_defects": sum(primal["formal_composition_replay"].values()),
        "graph_to_endpoint_support_local": flags["GRAPH_TO_ENDPOINT_FACTOR_SUPPORT_LOCAL"],
        "harmonic_restriction_support_local": flags["HARMONIC_RESTRICTION_SUPPORT_LOCAL"],
        "raw_386_by_470_component_matrix_constructed": flags["RAW_386_BY_470_COMPONENT_MATRIX_CONSTRUCTED"],
        "M1B_primal_complete": True,
        "M1B_complete": False,
        "remaining_M1B_packages": ["STRICT_M1B_ACTION_DUAL_LIFT", "STRICT_M1B_TYPED_CYCLIC_REPLAY"],
    }
    value["minimal_missing_bundle"][0].update({
        "completed_work_packages": ["M1A_FULL_TYPED_CARRIER_LEDGER", "M1B_PRIMAL_COMPOSITE_CONTRACTION"],
        "remaining_work_packages": ["M1B_ACTION_DUAL_LIFT", "M1B_TYPED_CYCLIC_REPLAY", "M1C_COMMON_MANIFEST_REPLAY"],
    })
    value["gate_disposition"].update({
        "gate_a_status": "FAIL_CLOSED",
        "claim_state": "CLASSICAL_IMPORT_M1A_AND_M1B_PRIMAL_COMPLETE_ACTION_DUAL_CYCLIC_AND_M1C_OPEN",
        "publishable_quantum_results_allowed_by_gate_a": False,
    })
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREVIOUS.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(PREVIOUS), "role": "immutable Gate V28 predecessor"},
        {"path": str(M1B_PRIMAL.relative_to(ROOT)), "result_or_artifact_id": primal["result_id"], "sha256": sha(M1B_PRIMAL), "role": "independently checked exact M1B primal composite contraction"},
    ]
    value["claim_flags"].update({
        "M1B_PRIMAL_COMPOSITE_CONTRACTION_COMPLETE": True,
        "M1B_ACTION_DUAL_LIFT_COMPLETE": False,
        "M1B_TYPED_CYCLIC_REPLAY_COMPLETE": False,
        "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE": False,
        "M1C_COMMON_MANIFEST_REPLAY_COMPLETE": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "QME_RESTORED": False,
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "the action-dual lift, rank-940 cyclic contraction, complete M1B package or M1C common replay",
        "a 386-by-470 component matrix or an arbitrary-smooth support-local harmonic contraction",
        "a passed Gate A, Hadamard state, renormalized products, QME restoration or residual quantum transfer",
    ]))
    value["next_gate"] = "Lift the frozen primal composite through the action-derived compact-source dual, then replay the rank-940 pairing, adjointness, skew-homotopy, inclusion-isometry and cyclic contraction identities on the same hashes."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v29_reconciliation.py",
        "checks": [
            "Gate V28 predecessor and M1B-primal content pins",
            "4,080-to-470 exact represented contraction census and zero defects",
            "typed local/represented category and support boundaries",
            "M1B primal complete with action-dual/cyclic/M1C open",
            "unchanged twenty exports, ten checks and one accepted hash",
            "Gate-A/Hadamard/QME firewalls and canonical digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    Draft202012Validator(load_schema()).validate(value)
    return value


def load_schema() -> dict[str, Any]:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return schema


def report(value: dict[str, Any]) -> str:
    result = value["m1b_primal_completion_resolution"]
    return f"""# Classical import Gate-A reconciliation v29

**Result:** `{value['result_id']}`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

**Gate A:** `FAIL_CLOSED`

The primal half of M1B is complete on the declared energy-two-through-six
D-finite graph domain.  Exact restriction removes 205 isolated comparison
test doublets and leaves a **{result['represented_endpoint_rows']:,}-to-{result['primal_residual_rows']}**
normalized endpoint contraction.  It has {result['q0_nonzero_entries']:,} q0,
{result['homotopy_nonzero_entries']:,} homotopy and {result['inclusion_nonzero_entries']}
inclusion/projection entries, with zero represented identity defects.

The local 386-to-30 graph contraction and this finite represented contraction
compose by the normalized-contraction lemma.  The result is a typed operator
DAG, not a 386-by-470 component matrix.  The local graph factor is support-local;
the harmonic restriction is global and support-expanding.  No arbitrary-smooth
contraction is claimed.

## Remaining M1 construction

M1B still requires the action-derived compact-source dual lift and the rank-940
cyclic replay.  M1C must then bind all twenty exports and seven hashes and replay
all ten Gate-A checks on one immutable manifest.  Gate A still accepts one of
seven hashes.  No full-complex Hadamard state, renormalized Lorentzian products,
QME restoration or residual quantum transfer is promoted.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    outputs = {RESULT: json.dumps(value, indent=2, ensure_ascii=False) + "\n", REPORT: report(value)}
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit("stale generated artifacts: " + ", ".join(stale))
        print("CLASSICAL_IMPORT_GATE_V29_RECONCILIATION: generated artifacts current")
        return 0
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")
    print("CLASSICAL_IMPORT_GATE_V29_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
