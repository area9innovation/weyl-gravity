#!/usr/bin/env python3
"""Independent receiver for Gate-A reconciliation v23."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V23_RECONCILIATION.json"
PREVIOUS = HERE / "certificates/CLASSICAL_IMPORT_GATE_V22_RECONCILIATION.json"
DUAL = HERE / "certificates/STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1.json"
DUAL_CHECKER = HERE / "check_strict_dfinite_cotangent_dual_comparison.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    body = json.loads(json.dumps(value))
    body.get("independent_checker", {}).pop("expected_digest", None)
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def load_dual_checker():
    spec = importlib.util.spec_from_file_location("strict_dfinite_cotangent_dual_gate_receiver", DUAL_CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load formal cotangent-dual checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text(encoding="utf-8")) if value is None else value
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    dual = json.loads(DUAL.read_text(encoding="utf-8"))
    errors: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    require(value.get("result_id") == "CLASSICAL_IMPORT_GATE_V23_RECONCILIATION", "result identity drift")
    require(value.get("supersedes_for_current_status") == previous.get("result_id"), "predecessor identity drift")
    pins = {item["result_or_artifact_id"]: item for item in value.get("provenance", {}).get("inputs", [])}
    for result_id, path in ((previous["result_id"], PREVIOUS), (dual["result_id"], DUAL)):
        require(result_id in pins, f"missing pin {result_id}")
        if result_id in pins:
            require(pins[result_id]["path"] == str(path.relative_to(ROOT)), f"path drift for {result_id}")
            require(pins[result_id]["sha256"] == sha(path), f"hash drift for {result_id}")
    try:
        dual_errors = load_dual_checker().check(dual)
    except Exception as exc:  # fail closed on receiver failure
        dual_errors = [f"formal-dual checker exception: {exc}"]
    require(not dual_errors, "formal cotangent-dual checker failed: " + "; ".join(dual_errors))

    require(len(value.get("export_reconciliation", [])) == len(previous["export_reconciliation"]) == 20, "export inventory drift")
    require(len(value.get("freeze_check_reconciliation", [])) == len(previous["freeze_check_reconciliation"]) == 10, "freeze-check inventory drift")
    disposition = value.get("gate_disposition", {})
    require(disposition.get("gate_a_status") == "FAIL_CLOSED", "Gate A promoted")
    require(disposition.get("accepted_common_snapshot_hashes") == 1, "accepted hash count drift")
    require(disposition.get("same_theory_receiver_verified_scoped") == 17, "verified export count drift")
    require(disposition.get("freeze_checks_receiver_verified_scoped") == 9, "verified check count drift")
    require(disposition.get("freeze_checks_blocked") == 1, "blocked check count drift")
    require(
        [item["id"] for item in value.get("minimal_missing_bundle", [])]
        == ["M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION", "M4R_TYPED_RESIDUAL_CYCLICITY", "M1_COMMON_STRICT_SNAPSHOT"],
        "minimal missing bundle/order drift",
    )

    resolution = value.get("m3rc_formal_cotangent_dual_resolution", {})
    require(resolution.get("certificate_sha256") == sha(DUAL), "formal-dual resolution hash drift")
    require((resolution.get("original_source_full_dimension"), resolution.get("original_source_H0_dimension"), resolution.get("original_source_H1_dimension")) == (4490, 470, 0), "original source cohomology projection drift")
    require(resolution.get("same_source_retract_to_940_possible") is False, "same-source obstruction promoted")
    require((resolution.get("formal_cotangent_source_dimension"), resolution.get("formal_cotangent_residual_dimension")) == (8980, 940), "formal cotangent dimension projection drift")
    require((resolution.get("formal_full_pairing_rank"), resolution.get("formal_residual_pairing_rank"), resolution.get("formal_identity_defects")) == (8980, 940, 0), "formal pairing/identity projection drift")
    require(resolution.get("M3RC_A_FORMAL_COTANGENT_DUAL_COMPARISON") == "COMPLETE", "M3RC-A not complete")
    require(resolution.get("M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION") == "OPEN", "M3RC-B promoted")
    require(resolution.get("M4R_TYPED_RESIDUAL_CYCLICITY") == "BLOCKED_BY_M3RC_B", "M4R dependency drift")
    require(resolution.get("accepted_common_snapshot_hashes_added") == 0, "new hash silently accepted")

    flags = value.get("claim_flags", {})
    for key in (
        "ORIGINAL_DFINITE_H1_ZERO",
        "M3RC_A_FORMAL_COTANGENT_DUAL_COMPARISON_COMPLETE",
        "FORMAL_8980_COTANGENT_SOURCE_CONSTRUCTED",
        "FORMAL_940_COTANGENT_RESIDUAL_COMPARISON_CONSTRUCTED",
        "FORMAL_COTANGENT_PAIRING_NONDEGENERATE",
        "FORMAL_COTANGENT_SDR_CYCLIC",
    ):
        require(flags.get(key) is True, f"missing positive flag {key}")
    for key in (
        "UNCHANGED_4490_SOURCE_CAN_RETRACT_TO_940_RESIDUAL",
        "M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION_COMPLETE",
        "FORMAL_DUAL_IDENTIFIED_WITH_ACTION_SUPPORT_DUAL",
        "M3RC_DUAL_COMPARISON_MAPS_CONSTRUCTED",
        "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE",
        "CLASSICAL_IMPORT_GATE_PASSED",
        "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A",
        "HADAMARD_STATE_CONSTRUCTED",
        "QME_RESTORED",
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ):
        require(flags.get(key) is False, f"firewall promoted: {key}")

    require(value.get("independent_checker", {}).get("expected_digest") == digest(value), "canonical reconciliation digest drift")
    return errors


def main() -> int:
    errors = check()
    print("CLASSICAL_IMPORT_GATE_V23_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - M3RC-A formal cotangent comparison is exact")
        print("  - M3RC-B action/support identification remains open before M4R")
        print("  - Gate A remains fail closed at one of seven accepted hashes")
    for error in errors:
        print("  - " + error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
