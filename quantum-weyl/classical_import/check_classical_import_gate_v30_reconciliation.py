#!/usr/bin/env python3
"""Independent receiver for the strict pure-Weyl Gate-A decision."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V30_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V30.md"
SCHEMA = HERE / "schema/quantum-weyl-classical-import-gate-v30-reconciliation-v1.schema.json"
PREVIOUS = HERE / "certificates/CLASSICAL_IMPORT_GATE_V29_RECONCILIATION.json"
DUAL = HERE / "certificates/STRICT_M1B_ACTION_DUAL_LIFT_V1.json"
CYCLIC = HERE / "certificates/STRICT_M1B_TYPED_CYCLIC_COMPOSITE_V1.json"
M1C = HERE / "certificates/STRICT_M1C_COMMON_SNAPSHOT_V1.json"
M1C_CHECKER = HERE / "check_strict_m1c_common_snapshot.py"


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


def check(value: dict[str, Any], run_receivers: bool = False) -> list[str]:
    errors: list[str] = []
    previous, dual, cyclic, m1c = map(load, (PREVIOUS, DUAL, CYCLIC, M1C))
    schema = load(SCHEMA)
    try:
        Draft202012Validator.check_schema(schema)
        errors.extend(
            f"schema:{'/'.join(map(str, error.absolute_path)) or '<root>'}:{error.message}"
            for error in Draft202012Validator(schema).iter_errors(value)
        )
    except Exception as exc:
        errors.append(f"schema:{exc}")

    if value.get("result_id") != "CLASSICAL_IMPORT_GATE_V30_RECONCILIATION":
        errors.append("identity")
    if value.get("lifecycle") != "CLASSIFIED":
        errors.append("lifecycle")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency tags")
    if value.get("supersedes_for_current_status") != previous["result_id"] or value.get("historical_certificate_preserved") is not True:
        errors.append("predecessor disposition")
    if previous.get("gate_disposition", {}).get("gate_a_status") != "FAIL_CLOSED":
        errors.append("predecessor boundary")

    provenance = {row.get("path"): row for row in value.get("provenance", {}).get("inputs", [])}
    for path, authority, role in (
        (PREVIOUS, previous, "immutable fail-closed predecessor"),
        (DUAL, dual, "M1B action-derived dual lift"),
        (CYCLIC, cyclic, "M1B typed rank-940 cyclic composite"),
        (M1C, m1c, "independently receiver-verified immutable common snapshot"),
    ):
        row = provenance.get(str(path.relative_to(ROOT)), {})
        if row.get("sha256") != sha(path) or row.get("result_or_artifact_id") != authority["result_id"] or row.get("role") != role:
            errors.append(f"provenance {path.name}")

    dual_resolution = value.get("m1b_action_dual_completion_resolution", {})
    dual_defects = sum(dual["represented_dual_lift"]["exact_replay"].values())
    if (
        dual_resolution.get("result_id") != dual["result_id"]
        or dual_resolution.get("certificate_sha256") != sha(DUAL)
        or dual_resolution.get("content_sha256") != dual["content_sha256"]
        or dual_resolution.get("compact_source_action_duals") != 470
        or dual_resolution.get("represented_action_test_check_coordinates") != 4080
        or dual_resolution.get("exact_dual_identity_defects") != dual_defects
        or dual_resolution.get("M1B_action_dual_complete") is not True
        or dual_defects != 0
    ):
        errors.append("M1B action-dual resolution")

    cyclic_resolution = value.get("m1b_cyclic_completion_resolution", {})
    aggregate = cyclic["exact_cyclic_replay"]["aggregate"]
    if (
        cyclic_resolution.get("result_id") != cyclic["result_id"]
        or cyclic_resolution.get("certificate_sha256") != sha(CYCLIC)
        or cyclic_resolution.get("content_sha256") != cyclic["content_sha256"]
        or any(cyclic_resolution.get(key) != expected for key, expected in aggregate.items())
        or cyclic_resolution.get("M1B_complete") is not True
        or sum(cyclic["exact_cyclic_replay"]["identity_totals"].values()) != 0
    ):
        errors.append("M1B cyclic resolution")

    snapshot = value.get("m1c_common_snapshot_resolution", {})
    expected_snapshot = {
        "result_id": m1c["result_id"],
        "certificate_sha256": sha(M1C),
        "content_sha256": m1c["content_sha256"],
        "snapshot_id": m1c["snapshot_id"],
        "snapshot_sha256": m1c["snapshot_sha256"],
        "artifact_pins": 16,
        "exports_bound": 20,
        "top_level_hashes_bound": 7,
        "gate_checks_passed": 10,
        "supplemental_checks_passed": 3,
        "M1C_complete": True,
    }
    if snapshot != expected_snapshot:
        errors.append("M1C snapshot resolution")

    exports = value.get("export_reconciliation", [])
    if (
        len(exports) != 20
        or {row.get("export_id") for row in exports} != {row["export_id"] for row in m1c["export_bindings"]}
        or any(row.get("status") != "RECEIVER_VERIFIED_COMMON_SNAPSHOT" for row in exports)
    ):
        errors.append("common export decision")
    checks = value.get("freeze_check_reconciliation", [])
    if (
        len(checks) != 10
        or {row.get("check_id") for row in checks} != {row["check_id"] for row in m1c["gate_a_replay"]}
        or any(row.get("status") != "RECEIVER_VERIFIED_COMMON_SNAPSHOT" or row.get("remaining_for_gate_a") is not None for row in checks)
    ):
        errors.append("common freeze-check decision")
    hashes = value.get("required_hash_disposition", {})
    if set(hashes) != set(m1c["accepted_top_level_hashes"]) or any(
        hashes.get(key, {}).get("accepted") != hash_value or hashes.get(key, {}).get("candidate") != hash_value
        for key, hash_value in m1c["accepted_top_level_hashes"].items()
    ):
        errors.append("common hash decision")

    disposition = value.get("gate_disposition", {})
    expected_disposition = {
        "gate_a_status": "VERIFIED",
        "publishable_quantum_results_allowed_by_gate_a": True,
        "exports_total": 20,
        "same_theory_receiver_verified_scoped": 20,
        "missing_portable_objects": 0,
        "freeze_checks_total": 10,
        "freeze_checks_receiver_verified_scoped": 10,
        "freeze_checks_blocked": 0,
        "accepted_common_snapshot_hashes": 7,
    }
    if any(disposition.get(key) != expected for key, expected in expected_disposition.items()) or value.get("minimal_missing_bundle") != []:
        errors.append("Gate-A disposition")

    flags = value.get("claim_flags", {})
    for flag in (
        "M1B_PRIMAL_COMPOSITE_CONTRACTION_COMPLETE", "M1B_ACTION_DUAL_LIFT_COMPLETE",
        "M1B_TYPED_CYCLIC_REPLAY_COMPLETE", "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE",
        "M1C_COMMON_MANIFEST_REPLAY_COMPLETE", "M1_COMMON_STRICT_SNAPSHOT_COMPLETE",
        "COMMON_GATE_A_FREEZE_BOUND",
        "CLASSICAL_IMPORT_GATE_PASSED", "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A",
    ):
        if flags.get(flag) is not True:
            errors.append(f"required flag {flag}")
    for flag in (
        "NONLINEAR_GREEN_COMPATIBILITY_CERTIFIED", "HADAMARD_STATE_CONSTRUCTED",
        "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED", "QME_RESTORED",
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ):
        if flags.get(flag) is not False:
            errors.append(f"quantum firewall {flag}")

    nonclaims = value.get("does_not_establish", [])
    stale_nonclaims = {
        "a passed classical freeze gate",
        "the six remaining top-level Gate-A hashes or the final common cyclic contraction",
        "acceptance of the residual zero-mode candidate hash in a common full Gate-A freeze",
        "acceptance of the centered representative candidate hash in a common full Gate-A freeze",
    }
    if stale_nonclaims.intersection(nonclaims):
        errors.append("stale pre-V30 nonclaim")
    for boundary in (
        "q2/q3 compatibility with the typed advanced and retarded Green homotopies",
        "a complete Lorentzian off-shell BV propagator or BRST-compatible Hadamard two-point function",
        "that the formal 8,980-coordinate cotangent comparison source is the authoritative classical BV source",
    ):
        if boundary not in nonclaims:
            errors.append(f"missing current boundary {boundary}")

    checker = value.get("independent_checker", {})
    if checker.get("path") != str(Path(__file__).relative_to(ROOT)):
        errors.append("checker path")
    if checker.get("expected_digest") != digest(value):
        errors.append("canonical Gate digest")
    report = REPORT.read_text(encoding="utf-8") if REPORT.is_file() else ""
    for token in ("Gate A passes", "20 exports", "7", "10", "classical import decision", "does not itself create a quantum result", "Hadamard", "QME"):
        if token not in report:
            errors.append(f"report token {token}")
    if run_receivers:
        completed = subprocess.run([sys.executable, str(M1C_CHECKER)], cwd=ROOT, text=True, capture_output=True)
        if completed.returncode:
            errors.append("independent M1C receiver chain")
    return sorted(set(errors))


def main() -> int:
    errors = check(load(RESULT), run_receivers=True)
    if errors:
        print("CLASSICAL_IMPORT_GATE_V30_RECONCILIATION: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("CLASSICAL_IMPORT_GATE_V30_RECONCILIATION: PASS")
    print("  - independently replayed the exact M1C receiver chain")
    print("  - Gate A verified on 20 exports, 7 hashes and 10 required checks")
    print("  - nonlinear Green, Hadamard, renormalization and QME claims remain false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
