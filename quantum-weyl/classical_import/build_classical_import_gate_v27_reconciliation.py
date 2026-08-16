#!/usr/bin/env python3
"""Build Gate-A v27 after the exact M1A local 386-row semantic extension."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
PREVIOUS = HERE / "certificates/CLASSICAL_IMPORT_GATE_V26_RECONCILIATION.json"
LOCAL = HERE / "certificates/STRICT_M1A_LOCAL_SEMANTIC_EXTENSION_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V27_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V27.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    body = deepcopy(value)
    body.get("independent_checker", {}).pop("expected_digest", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    previous = json.loads(PREVIOUS.read_text())
    local = json.loads(LOCAL.read_text())
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V26_RECONCILIATION":
        raise ValueError("Gate V26 predecessor drift")
    flags = local.get("claim_flags", {})
    if (
        local.get("result_id") != "STRICT_M1A_LOCAL_SEMANTIC_EXTENSION_V1"
        or flags.get("LOCAL_386_FULLY_TYPED") is not True
        or flags.get("M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE") is not False
        or flags.get("CLASSICAL_IMPORT_GATE_PASSED") is not False
    ):
        raise ValueError("M1A local semantic firewall drift")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v27-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V27_RECONCILIATION",
        "result_state": "M1A_LOCAL_386_TYPED_REPRESENTED_CROSSWALK_OPEN_GATE_FAIL_CLOSED",
        "created": "2026-08-16",
        "repository_base_commit": "f8709e9bee7e72b48a17b45f2b8666e97980029f",
        "question": "After the M1A local semantic extension, what remains before the full typed carrier ledger can be frozen?",
        "answer": "All 386 local graph rows are now fully namespaced. The 36 shifted auxiliary rows are action-derived; the 320 fixed-background mapping-cone rows are typed through the exact cone and engineering filtrations, with scalar nonlinear Weyl weight correctly marked not applicable because the Cotton slot obeys a triangular Weyl law. M1A remains open only at the represented crosswalk: 4,080 endpoint-harmonic coordinates, 410 scalar test-nonminimal coordinates, and the 470+470 action-residual carrier. Gate A remains fail closed at one accepted hash.",
        "supersedes_for_current_status": previous["result_id"],
        "historical_certificate_preserved": True,
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V27.md",
    })
    resolution = value["m1_common_snapshot_preflight_resolution"]
    work = deepcopy(resolution["work_packages"])
    work[0].update({
        "status": "LOCAL_386_COMPLETE_REPRESENTED_CROSSWALK_OPEN",
        "deliverable": "Crosswalk the 4,080 represented endpoint coordinates, isolate the 410 scalar test-nonminimal coordinates, type the 470+470 action-residual rows, and freeze their union with the completed local 386-row ledger.",
    })
    resolution.update({
        "work_packages": work,
        "missing_local_row_fields": [],
        "local_386_rows_fully_namespaced": 386,
        "local_386_rows_remaining_partial": 0,
        "m1a_represented_crosswalk_complete": False,
        "accepted_common_snapshot_hashes_added": 0,
    })
    value["m1a_local_semantic_resolution"] = {
        "result_id": local["result_id"],
        "status": local["result_state"],
        "certificate_sha256": sha(LOCAL),
        "extension_rows": local["counts"]["extension_rows"],
        "auxiliary_rows_fully_namespaced": local["counts"]["auxiliary_rows_fully_namespaced"],
        "mapping_cone_rows_fully_namespaced": local["counts"]["mapping_cone_rows_fully_namespaced"],
        "local_386_rows_fully_namespaced": local["counts"]["local_386_rows_fully_namespaced_after_this_result"],
        "unresolved_fields": local["counts"]["rows_with_unresolved_fields"],
        "cotton_weyl_component_checks": local["cotton_nonlinear_weyl_non_eigen_witness"]["component_checks"],
        "cotton_weyl_defects": local["cotton_nonlinear_weyl_non_eigen_witness"]["defects"],
        "scalar_nonlinear_weyl_weight_for_fixed_background_cone": "NOT_APPLICABLE",
        "M1A_complete": False,
        "remaining_M1A_package": "M1A3_REPRESENTED_CROSSWALK_AND_M1A4_LEDGER_FREEZE",
    }
    for row in value["export_reconciliation"]:
        if row.get("export_id") in {"field_ghost_antifield_dictionary", "field_gradings"}:
            row.update({
                "m1_v27_status": "LOCAL_386_READY_REPRESENTED_CROSSWALK_OPEN",
                "blocker": "M1A3_REPRESENTED_CROSSWALK_AND_M1A4_LEDGER_FREEZE",
            })
    value["gate_disposition"].update({
        "gate_a_status": "FAIL_CLOSED",
        "claim_state": "CLASSICAL_IMPORT_M1A_LOCAL_COMPLETE_REPRESENTED_CROSSWALK_OPEN",
        "publishable_quantum_results_allowed_by_gate_a": False,
    })
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREVIOUS.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(PREVIOUS), "role": "immutable Gate V26 predecessor"},
        {"path": str(LOCAL.relative_to(ROOT)), "result_or_artifact_id": local["result_id"], "sha256": sha(LOCAL), "role": "independently checked M1A local 386-row semantic extension"},
    ]
    value["claim_flags"].update({
        "M1A2_LOCAL_SEMANTIC_EXTENSION_COMPLETE": True,
        "LOCAL_386_FULLY_TYPED": True,
        "M1A3_REPRESENTED_CROSSWALK_COMPLETE": False,
        "M1A4_LEDGER_FREEZE_COMPLETE": False,
        "M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE": False,
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
        "M1A completion from the completed local 386-row ledger without the represented and action-residual crosswalk",
        "a nonlinear filtered Weyl action on the fixed-background contractible cone",
        "a passed Gate A, Hadamard state, renormalized products, QME restoration or residual quantum transfer",
    ]))
    value["next_gate"] = "Construct M1A3 on the 4,080 represented endpoint coordinates, classify the 410 scalar test-nonminimal coordinates by source or exclusion, type the 470+470 action residual, then freeze their union with the local 386 rows as M1A4."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v27_reconciliation.py",
        "checks": [
            "Gate V26 predecessor and M1A2 content pins",
            "386/386 local coverage and zero unresolved local fields",
            "2,560-component Cotton non-eigen witness with zero defects",
            "M1A3/M1A4 represented-crosswalk boundary",
            "unchanged twenty exports, ten checks and one accepted hash",
            "formal-source/Gate-A/Hadamard/QME firewalls",
            "canonical reconciliation digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    local = value["m1a_local_semantic_resolution"]
    return f"""# Classical import Gate-A reconciliation v27

**Result:** `{value['result_id']}`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

**Gate A:** `FAIL_CLOSED`

All **{local['local_386_rows_fully_namespaced']} of 386** local graph rows are
now fully typed.  This includes 36 action-derived shifted auxiliary rows and
320 contractible mapping-cone rows.  The latter do not receive invented scalar
Weyl weights: an exact {local['cotton_weyl_component_checks']:,}-component
check gives zero defects for the triangular Cotton law
`delta V_abc=omega^p W_apbc`, so scalar nonlinear Weyl weight is
`NOT_APPLICABLE` on this fixed-background resolution carrier.

## Remaining M1A construction

M1A is not complete.  M1A3 must crosswalk 4,080 represented endpoint
coordinates, classify the 410 scalar test-nonminimal coordinates by an
authoritative source or explicit exclusion, and type the 470 primal plus 470
action-dual residual coordinates.  M1A4 must then freeze those rows together
with the completed local ledger.

M1B, M1C and all final common-snapshot checks remain downstream.  Gate A still
accepts one of seven hashes.  No Hadamard, renormalization, QME or
residual-transfer lifecycle state is promoted.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    outputs = {
        RESULT: json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        REPORT: report(value),
    }
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.exists() or path.read_text() != content]
        if stale:
            raise SystemExit("stale generated artifacts: " + ", ".join(stale))
        print("CLASSICAL_IMPORT_GATE_V27_RECONCILIATION: generated artifacts current")
        return 0
    for path, content in outputs.items():
        path.write_text(content)
    print("CLASSICAL_IMPORT_GATE_V27_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
