#!/usr/bin/env python3
"""Independent receiver for Gate-A reconciliation v24."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V24_RECONCILIATION.json"
PREVIOUS = HERE / "certificates/CLASSICAL_IMPORT_GATE_V23_RECONCILIATION.json"
ACTION_DUAL = HERE / "certificates/STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1.json"
ACTION_CHECKER = HERE / "check_strict_m3rc_action_support_dual_identification.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    body = json.loads(json.dumps(value))
    body.get("independent_checker", {}).pop("expected_digest", None)
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def load_action_checker():
    spec = importlib.util.spec_from_file_location("strict_m3rc_action_support_gate_receiver", ACTION_CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load M3RC action/support checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text(encoding="utf-8")) if value is None else value
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    action = json.loads(ACTION_DUAL.read_text(encoding="utf-8"))
    errors: list[str] = []

    def require(condition: object, message: str) -> None:
        if not condition:
            errors.append(message)

    require(value.get("result_id") == "CLASSICAL_IMPORT_GATE_V24_RECONCILIATION", "result identity drift")
    require(value.get("supersedes_for_current_status") == previous.get("result_id"), "predecessor identity drift")
    pins = {item["result_or_artifact_id"]: item for item in value.get("provenance", {}).get("inputs", [])}
    for result_id, path in ((previous["result_id"], PREVIOUS), (action["result_id"], ACTION_DUAL)):
        require(result_id in pins, f"missing pin {result_id}")
        if result_id in pins:
            require(pins[result_id]["path"] == str(path.relative_to(ROOT)), f"path drift for {result_id}")
            require(pins[result_id]["sha256"] == sha(path), f"hash drift for {result_id}")
    try:
        action_errors = load_action_checker().check(action)
    except Exception as exc:
        action_errors = [f"M3RC-B checker exception: {exc}"]
    require(not action_errors, "M3RC-B checker failed: " + "; ".join(action_errors))

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
        == ["M4R_TYPED_RESIDUAL_CYCLICITY", "M1_COMMON_STRICT_SNAPSHOT"],
        "minimal missing bundle/order drift",
    )

    resolution = value.get("m3rc_action_support_dual_resolution", {})
    require(resolution.get("certificate_sha256") == sha(ACTION_DUAL), "M3RC-B resolution hash drift")
    require((resolution.get("represented_primal_modes"), resolution.get("compact_source_dual_classes"), resolution.get("phase_space_dimension"), resolution.get("action_pairing_rank")) == (470, 470, 940, 940), "M3RC-B carrier/rank projection drift")
    require(resolution.get("positive_krein_inertia") == {"positive": 230, "negative": 240, "zero": 0}, "Krein inertia projection drift")
    for key in ("support_exact_sequence_defects", "compact_source_support_defects", "causal_recovery_defects", "pairing_identification_defects", "basis_crosswalk_defects", "accepted_common_snapshot_hashes_added"):
        require(resolution.get(key) == 0, f"nonzero M3RC-B resolution field: {key}")
    require(resolution.get("full_continuous_dual_claimed") is False, "full continuous dual promoted")
    require(resolution.get("M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION") == "COMPLETE_ON_REPRESENTED_ENERGIES_2_THROUGH_6", "M3RC-B disposition drift")
    require(resolution.get("M4R_TYPED_RESIDUAL_CYCLICITY") == "READY", "M4R readiness drift")

    flags = value.get("claim_flags", {})
    for key in (
        "M3RC_A_FORMAL_COTANGENT_DUAL_COMPARISON_COMPLETE",
        "M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION_COMPLETE",
        "M3RC_B_REPRESENTED_ACTION_SUPPORT_DUAL_IDENTIFICATION_COMPLETE",
        "ALL_470_FORMAL_DUALS_HAVE_COMPACT_SOURCE_REPRESENTATIVES",
        "ACTION_PAIRING_EQUALS_CANONICAL_940_COTANGENT_PAIRING",
        "M3RC_DUAL_COMPARISON_MAPS_CONSTRUCTED",
        "M4R_TYPED_RESIDUAL_CYCLICITY_READY",
    ):
        require(flags.get(key) is True, f"missing positive flag {key}")
    for key in (
        "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE",
        "FORMAL_DUAL_IDENTIFIED_WITH_ACTION_SUPPORT_DUAL",
        "FULL_ALL_ENERGY_CONTINUOUS_DUAL_IDENTIFIED",
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
    print("CLASSICAL_IMPORT_GATE_V24_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - M3RC-B closes on 470 compact-source/action dual classes")
        print("  - M4R is ready; M1 remains last")
        print("  - Gate A remains fail closed at one of seven accepted hashes")
    for error in errors:
        print("  - " + error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
