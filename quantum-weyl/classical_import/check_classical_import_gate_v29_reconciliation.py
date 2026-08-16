#!/usr/bin/env python3
"""Independent receiver for classical-import Gate-A reconciliation v29."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V29_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V29.md"
SCHEMA = HERE / "schema/quantum-weyl-classical-import-gate-v29-reconciliation-v1.schema.json"
PREVIOUS = HERE / "certificates/CLASSICAL_IMPORT_GATE_V28_RECONCILIATION.json"
PRIMAL = HERE / "certificates/STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    body = deepcopy(value)
    body.get("independent_checker", {}).pop("expected_digest", None)
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    previous = load(PREVIOUS)
    primal = load(PRIMAL)
    schema = load(SCHEMA)
    for error in Draft202012Validator(schema).iter_errors(value):
        errors.append(f"schema:{'/'.join(map(str, error.absolute_path)) or '<root>'}:{error.message}")
    if value.get("result_id") != "CLASSICAL_IMPORT_GATE_V29_RECONCILIATION" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("identity/lifecycle")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency tags")
    if value.get("supersedes_for_current_status") != previous["result_id"] or value.get("historical_certificate_preserved") is not True:
        errors.append("predecessor disposition")

    provenance = {row.get("path"): row for row in value.get("provenance", {}).get("inputs", [])}
    for path, result_id in ((PREVIOUS, previous["result_id"]), (PRIMAL, primal["result_id"])):
        relative = str(path.relative_to(ROOT))
        row = provenance.get(relative, {})
        if row.get("sha256") != sha(path) or row.get("result_or_artifact_id") != result_id:
            errors.append(f"provenance {relative}")

    aggregate = primal["represented_contraction"]["aggregate"]
    flags = primal["claim_flags"]
    expected_resolution = {
        "result_id": primal["result_id"],
        "certificate_sha256": sha(PRIMAL),
        "content_sha256": primal["content_sha256"],
        "domain": primal["scope"]["domain"],
        "energies": [2, 3, 4, 5, 6],
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
    if value.get("m1b_primal_completion_resolution") != expected_resolution:
        errors.append("M1B primal resolution")
    if expected_resolution["represented_identity_defects"] or expected_resolution["formal_composition_defects"]:
        errors.append("M1B primal defects")

    current_m1 = value.get("m1_common_snapshot_preflight_resolution", {})
    prior_m1 = previous["m1_common_snapshot_preflight_resolution"]
    for key in ("exports_total", "exports_object_ready", "candidate_hash_objects_ready", "required_hash_objects", "required_freeze_checks"):
        if current_m1.get(key) != prior_m1.get(key):
            errors.append(f"M1 census drift {key}")
    work = current_m1.get("work_packages", [])
    if len(work) != 3 or work[0].get("status") != "COMPLETE" or work[1].get("status") != "PRIMAL_COMPLETE_ACTION_DUAL_AND_CYCLIC_OPEN" or work[2].get("status") != "OPEN_AFTER_M1B_ACTION_DUAL_AND_CYCLIC_REPLAY":
        errors.append("M1 package lifecycle")
    if (
        current_m1.get("m1b_primal_composite_contraction_complete") is not True
        or current_m1.get("m1b_action_dual_lift_complete") is not False
        or current_m1.get("m1b_typed_cyclic_replay_complete") is not False
        or current_m1.get("m1b_represented_composite_contraction_complete") is not False
    ):
        errors.append("M1B sublayer boundary")

    for key in ("export_reconciliation", "required_hash_disposition", "required_freeze_checks"):
        if value.get(key) != previous.get(key):
            errors.append(f"inherited Gate-A surface drift {key}")
    disposition = value.get("gate_disposition", {})
    if (
        disposition.get("gate_a_status") != "FAIL_CLOSED"
        or disposition.get("accepted_common_snapshot_hashes") != 1
        or disposition.get("same_theory_receiver_verified_scoped") != previous["gate_disposition"]["same_theory_receiver_verified_scoped"]
        or disposition.get("freeze_checks_receiver_verified_scoped") != previous["gate_disposition"]["freeze_checks_receiver_verified_scoped"]
        or disposition.get("publishable_quantum_results_allowed_by_gate_a") is not False
    ):
        errors.append("Gate-A disposition")

    claim_flags = value.get("claim_flags", {})
    if claim_flags.get("M1B_PRIMAL_COMPOSITE_CONTRACTION_COMPLETE") is not True:
        errors.append("M1B primal flag")
    for flag in (
        "M1B_ACTION_DUAL_LIFT_COMPLETE", "M1B_TYPED_CYCLIC_REPLAY_COMPLETE",
        "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE",
        "M1C_COMMON_MANIFEST_REPLAY_COMPLETE", "CLASSICAL_IMPORT_GATE_PASSED",
        "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A", "HADAMARD_STATE_CONSTRUCTED",
        "QME_RESTORED", "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ):
        if claim_flags.get(flag) is not False:
            errors.append(f"fail-closed flag {flag}")
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("canonical reconciliation digest")
    if value.get("independent_checker", {}).get("path") != str(Path(__file__).relative_to(ROOT)):
        errors.append("checker path")
    if value.get("human_report") != str(REPORT.relative_to(ROOT)) or not REPORT.is_file():
        errors.append("report path")
    else:
        report = REPORT.read_text(encoding="utf-8")
        for token in ("4,080-to-470", "typed operator", "support-expanding", "action-derived", "rank-940", "one of", "Hadamard", "QME"):
            if token not in report:
                errors.append(f"report token {token}")
    return errors


def main() -> int:
    errors = check(load(RESULT))
    if errors:
        print("CLASSICAL_IMPORT_GATE_V29_RECONCILIATION: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("CLASSICAL_IMPORT_GATE_V29_RECONCILIATION: PASS")
    print("  - M1B primal complete on the declared D-finite domain")
    print("  - action dual, cyclic replay and M1C remain open")
    print("  - Gate A remains fail closed at one of seven hashes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
