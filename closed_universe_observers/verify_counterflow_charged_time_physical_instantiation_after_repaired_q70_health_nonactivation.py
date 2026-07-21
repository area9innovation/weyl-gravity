#!/usr/bin/env python3
"""Independent verifier for repaired-q70-health receiver nonactivation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/COUNTERFLOW_CHARGED_TIME_PHYSICAL_INSTANTIATION_AFTER_REPAIRED_Q70_HEALTH_NOT_ACTIVATED_V1.json"
Q = P / "certificates/COUNTERFLOW_CHARGED_TIME_PHYSICAL_INSTANTIATION_AFTER_REPAIRED_Q70_HEALTH_NOT_ACTIVATED_V1_PAYLOAD.json"
S = P / "schema/counterflow-charged-time-physical-instantiation-after-repaired-q70-health-not-activated-v1.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(cert: dict[str, Any], payload: dict[str, Any], health: dict[str, Any], hp: dict[str, Any]) -> None:
    Draft202012Validator(json.loads(S.read_text())).validate(cert)
    blocks = hp["certified_block_ledger"]
    assert [block["two_j"] for block in blocks] == [0, 1, 2]
    assert all(block["pairing_radical_dimension"] == 0 for block in blocks)
    assert all("OBSTRUCTED" in block["unrestricted_status"] for block in blocks)
    assert all("OBSTRUCTED" in block["fixed_Q_rel_status"] for block in blocks)
    assert health["remaining_carrier"]["physical_quotient_status"] == "NO_CERTIFIED_MAP"
    assert health["remaining_carrier"]["pairing_inertia_status"] == "NO_CERTIFIED_MAP"
    assert "removed" in health["branch_verdicts"]["fixed_Q_rel"]["global_relative_clock"]
    assert len(payload["thirteen_field_interface"]) == 13
    assert all(field["status"] == "NO_CERTIFIED_MAP" for field in payload["thirteen_field_interface"].values())
    ratio = payload["frequency_ratio_partial_function"]
    assert ratio["domain"] == [] and ratio["domain_cardinality"] == 0
    assert ratio["value"] == "UNDEFINED" and ratio["redshift"] == "NO_CERTIFIED_MAP"
    assert ratio["coordinate_ratio_promoted"] is False and ratio["independent_methods_run"] == 0
    assert all(value == "REJECT" for value in payload["mutations"].values())
    assert all(payload["exact_checks"].values())


def main() -> int:
    cert, payload = json.loads(C.read_text()), json.loads(Q.read_text())
    assert sha(Q) == cert["payload_ref"]["sha256"]
    for ref in cert["dependency_refs"].values():
        assert sha(ROOT / ref["path"]) == ref["sha256"]
    health = json.loads((ROOT / cert["dependency_refs"]["health_assembly"]["path"]).read_text())
    hp = json.loads((ROOT / cert["dependency_refs"]["health_assembly_payload"]["path"]).read_text())
    for role, ref in health["imports"].items():
        assert sha(ROOT / ref["path"]) == ref["sha256"], role
        assert payload["health_transitive_imports"][role]["sha256"] == ref["sha256"]
    verify(cert, payload, health, hp)
    print("COUNTERFLOW_CHARGED_TIME_PHYSICAL_INSTANTIATION_AFTER_REPAIRED_Q70_HEALTH_NOT_ACTIVATED_V1 independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
