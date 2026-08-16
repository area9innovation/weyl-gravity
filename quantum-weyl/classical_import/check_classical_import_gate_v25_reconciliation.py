#!/usr/bin/env python3
"""Independent receiver for Gate-A reconciliation v25."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V25_RECONCILIATION.json"
PREVIOUS = HERE / "certificates/CLASSICAL_IMPORT_GATE_V24_RECONCILIATION.json"
M4R = HERE / "certificates/STRICT_TYPED_RESIDUAL_CYCLICITY_V1.json"
M4R_CHECKER = HERE / "check_strict_typed_residual_cyclicity.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    body = json.loads(json.dumps(value))
    body.get("independent_checker", {}).pop("expected_digest", None)
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def load_m4r_checker():
    spec = importlib.util.spec_from_file_location("strict_m4r_gate_receiver", M4R_CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load M4R checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text(encoding="utf-8")) if value is None else value
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    m4r = json.loads(M4R.read_text(encoding="utf-8"))
    errors: list[str] = []

    def require(condition: object, message: str) -> None:
        if not condition:
            errors.append(message)

    require(value.get("result_id") == "CLASSICAL_IMPORT_GATE_V25_RECONCILIATION", "result identity drift")
    require(value.get("supersedes_for_current_status") == previous.get("result_id"), "predecessor drift")
    pins = {item["result_or_artifact_id"]: item for item in value.get("provenance", {}).get("inputs", [])}
    for result_id, path in ((previous["result_id"], PREVIOUS), (m4r["result_id"], M4R)):
        require(result_id in pins, f"missing pin {result_id}")
        if result_id in pins:
            require(pins[result_id].get("path") == str(path.relative_to(ROOT)), f"path drift for {result_id}")
            require(pins[result_id].get("sha256") == sha(path), f"hash drift for {result_id}")
    try:
        m4r_errors = load_m4r_checker().check(m4r)
    except Exception as exc:
        m4r_errors = [f"M4R checker exception: {exc}"]
    require(not m4r_errors, "M4R checker failed: " + "; ".join(m4r_errors))

    require(len(value.get("export_reconciliation", [])) == len(previous["export_reconciliation"]) == 20, "export inventory drift")
    require(len(value.get("freeze_check_reconciliation", [])) == len(previous["freeze_check_reconciliation"]) == 10, "check inventory drift")
    disposition = value.get("gate_disposition", {})
    require(disposition.get("gate_a_status") == "FAIL_CLOSED", "Gate A promoted")
    require((disposition.get("accepted_common_snapshot_hashes"), disposition.get("same_theory_receiver_verified_scoped"), disposition.get("freeze_checks_receiver_verified_scoped"), disposition.get("freeze_checks_blocked")) == (1, 17, 9, 1), "gate census drift")
    require([item.get("id") for item in value.get("minimal_missing_bundle", [])] == ["M1_COMMON_STRICT_SNAPSHOT"], "M1 is not the sole missing package")

    resolution = value.get("m4r_typed_residual_cyclicity_resolution", {})
    require(resolution.get("certificate_sha256") == sha(M4R), "M4R resolution hash drift")
    require((resolution.get("formal_comparison_source_dimension"), resolution.get("action_identified_residual_dimension"), resolution.get("residual_pairing_rank"), resolution.get("energy_blocks_replayed")) == (8980, 940, 940, 5), "M4R dimension/rank projection drift")
    for key in ("all_identity_defects", "action_pairing_identification_defects", "accepted_common_snapshot_hashes_added"):
        require(resolution.get(key) == 0, f"nonzero M4R resolution field: {key}")
    for key in ("q_res_cyclic", "projection_equals_inclusion_sharp", "homotopy_skew_adjoint"):
        require(resolution.get(key) is True, f"M4R identity projection missing: {key}")
    require(resolution.get("formal_source_authoritative") is False, "formal source authority promoted")
    require(resolution.get("M1_COMMON_STRICT_SNAPSHOT") == "SOLE_MINIMAL_MISSING_PACKAGE", "M1 disposition drift")

    flags = value.get("claim_flags", {})
    for key in (
        "M3RC_B_REPRESENTED_ACTION_SUPPORT_DUAL_IDENTIFICATION_COMPLETE",
        "M4R_TYPED_RESIDUAL_CYCLICITY_READY",
        "M4R_REPRESENTED_Q_RES_CYCLIC",
        "M4R_REPRESENTED_PROJECTION_EQUALS_INCLUSION_SHARP",
        "M4R_REPRESENTED_HOMOTOPY_SKEW_ADJOINT",
        "M4R_REPRESENTED_NORMALIZED_CYCLIC_CONTRACTION_COMPLETE",
        "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE",
    ):
        require(flags.get(key) is True, f"missing positive flag: {key}")
    for key in (
        "M1_COMMON_STRICT_SNAPSHOT_COMPLETE",
        "FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX",
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
    print("CLASSICAL_IMPORT_GATE_V25_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - represented M4R cyclic contraction closes with zero exact defects")
        print("  - M1 is the sole minimal missing classical import package")
        print("  - Gate A remains fail closed at one of seven accepted hashes")
    for error in errors:
        print("  - " + error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
