#!/usr/bin/env python3
"""Independent verifier for repaired-apparatus Z2 and memory nondefinition."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_APPARATUS_Z2_MEMORY_NONDEFINITION_AFTER_REPAIRED_REDUCTION.json"
X = P / "certificates/BERGER_APPARATUS_Z2_MEMORY_NONDEFINITION_AFTER_REPAIRED_REDUCTION_PAYLOAD.json"
SCHEMA = P / "schema/berger-apparatus-z2-memory-nondefinition-after-repaired-reduction-v1.schema.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    cert = json.loads(C.read_text())
    payload = json.loads(X.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(cert)
    assert sha256(X) == cert["payload_ref"]["sha256"]
    for ref in cert["dependency_refs"].values():
        path = ROOT / ref["path"]
        assert sha256(path) == ref["sha256"]
        assert json.loads(path.read_text())["result_id"] == ref["result_id"]

    combined = json.loads((ROOT / cert["dependency_refs"]["combined_payload"]["path"]).read_text())
    physical = json.loads((ROOT / cert["dependency_refs"]["physical_reduction"]["path"]).read_text())
    physical_payload = json.loads((ROOT / cert["dependency_refs"]["physical_reduction_payload"]["path"]).read_text())
    required = set(physical_payload["executable_reduction_audit"]["required_operator_fields"])
    assert not required.intersection(combined["complete_q1"])
    assert physical["atlas_status"] == "NO_CERTIFIED_MAP"
    assert set(physical["reduction_disposition"].values()) == {"NO_CERTIFIED_MAP"}
    assert set(payload["undefined_receiver_chain"].values()) == {"NO_CERTIFIED_MAP"}
    assert set(payload["correction_class_disposition"].values()) == {"NO_CERTIFIED_MAP"}
    assert payload["operational_disposition"]["leading_coordinate_rank_two"].endswith("ONLY")
    assert cert["atlas_status"] == "NO_CERTIFIED_MAP"
    print("BERGER_APPARATUS_Z2_MEMORY_NONDEFINITION_AFTER_REPAIRED_REDUCTION independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
