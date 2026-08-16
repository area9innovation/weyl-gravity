#!/usr/bin/env python3
"""Independent receiver for Gate-A reconciliation v26."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V26_RECONCILIATION.json"
PREVIOUS = HERE / "certificates/CLASSICAL_IMPORT_GATE_V25_RECONCILIATION.json"
PREFLIGHT = HERE / "certificates/STRICT_M1_COMMON_SNAPSHOT_PREFLIGHT_V1.json"
PREVIOUS_CHECKER = HERE / "check_classical_import_gate_v25_reconciliation.py"
PREFLIGHT_CHECKER = HERE / "check_strict_m1_common_snapshot_preflight.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    body = json.loads(json.dumps(value))
    body.get("independent_checker", {}).pop("expected_digest", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def load_checker(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text(encoding="utf-8")) if value is None else value
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    errors: list[str] = []

    def require(condition: object, message: str) -> None:
        if not condition:
            errors.append(message)

    require(value.get("result_id") == "CLASSICAL_IMPORT_GATE_V26_RECONCILIATION", "result identity drift")
    require(value.get("supersedes_for_current_status") == previous.get("result_id"), "predecessor drift")
    pins = {item.get("result_or_artifact_id"): item for item in value.get("provenance", {}).get("inputs", [])}
    for source, path in ((previous, PREVIOUS), (preflight, PREFLIGHT)):
        result_id = source["result_id"]
        require(pins.get(result_id, {}).get("path") == str(path.relative_to(ROOT)), f"path drift: {result_id}")
        require(pins.get(result_id, {}).get("sha256") == sha(path), f"hash drift: {result_id}")
    try:
        require(not load_checker(PREVIOUS_CHECKER, "gate_v25_for_v26").check(previous), "Gate V25 receiver replay")
        require(not load_checker(PREFLIGHT_CHECKER, "m1_preflight_for_v26").check(preflight), "M1 preflight receiver replay")
    except Exception as exc:
        errors.append(f"dependency checker exception: {exc}")

    require(len(value.get("export_reconciliation", [])) == len(previous["export_reconciliation"]) == 20, "export inventory drift")
    require(len(value.get("freeze_check_reconciliation", [])) == len(previous["freeze_check_reconciliation"]) == 10, "freeze-check inventory drift")
    disposition = value.get("gate_disposition", {})
    require(disposition.get("gate_a_status") == "FAIL_CLOSED", "Gate A promoted")
    require((disposition.get("accepted_common_snapshot_hashes"), disposition.get("same_theory_receiver_verified_scoped"), disposition.get("freeze_checks_receiver_verified_scoped"), disposition.get("freeze_checks_blocked")) == (1, 17, 9, 1), "gate census drift")
    missing = value.get("minimal_missing_bundle", [])
    require([item.get("id") for item in missing] == ["M1_COMMON_STRICT_SNAPSHOT"], "M1 sole-package frontier drift")
    require(missing and missing[0].get("work_packages") == ["M1A_FULL_TYPED_CARRIER_LEDGER", "M1B_REPRESENTED_COMPOSITE_CONTRACTION", "M1C_COMMON_MANIFEST_REPLAY"], "M1 work-package order drift")

    resolution = value.get("m1_common_snapshot_preflight_resolution", {})
    require(resolution.get("certificate_sha256") == sha(PREFLIGHT), "M1 preflight resolution hash drift")
    require((resolution.get("carrier_count"), resolution.get("typed_edge_count")) == (8, 7), "typed-diagram census drift")
    require((resolution.get("exports_total"), resolution.get("exports_object_ready"), resolution.get("exports_blocked_typed_ledger"), resolution.get("exports_blocked_composite")) == (20, 14, 2, 4), "export blocker partition drift")
    require((resolution.get("hashes_total"), resolution.get("hash_objects_ready"), resolution.get("hashes_blocked")) == (7, 4, 3), "hash blocker partition drift")
    require((resolution.get("freeze_checks_total"), resolution.get("freeze_checks_common_snapshot_replayed"), resolution.get("accepted_common_snapshot_hashes_added")) == (10, 0, 0), "replay/hash firewall drift")
    require(len(resolution.get("missing_local_row_fields", [])) == 8, "typed row-field blocker drift")
    require([row.get("status") for row in resolution.get("work_packages", [])] == ["OPEN", "OPEN_AFTER_M1A", "OPEN_AFTER_M1A_M1B"], "package lifecycle drift")
    require(resolution.get("formal_8980_source_authoritative") is False, "formal source promoted")

    flags = value.get("claim_flags", {})
    for key in ("M1_PREFLIGHT_COMPLETE", "M1_TYPED_DIAGRAM_REQUIRED"):
        require(flags.get(key) is True, f"positive flag missing: {key}")
    for key in (
        "M1_IS_CLERICAL_HASH_BUNDLE", "M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE",
        "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE", "M1C_COMMON_MANIFEST_REPLAY_COMPLETE",
        "M1_COMMON_STRICT_SNAPSHOT_COMPLETE", "FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX",
        "CLASSICAL_IMPORT_GATE_PASSED", "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A",
        "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ):
        require(flags.get(key) is False, f"firewall promoted: {key}")
    require(value.get("independent_checker", {}).get("expected_digest") == digest(value), "canonical reconciliation digest drift")
    return errors


def main() -> int:
    errors = check()
    print("CLASSICAL_IMPORT_GATE_V26_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - M1 classified as M1A typed ledger, M1B composite contraction and M1C final replay")
        print("  - Gate A remains fail closed at one of seven accepted hashes")
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
