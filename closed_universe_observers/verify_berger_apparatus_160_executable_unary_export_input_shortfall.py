#!/usr/bin/env python3
"""Independent verifier for executable 160-row unary input shortfall."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_APPARATUS_160_EXECUTABLE_UNARY_EXPORT_INPUT_SHORTFALL.json"
X = P / "certificates/BERGER_APPARATUS_160_EXECUTABLE_UNARY_EXPORT_INPUT_SHORTFALL_PAYLOAD.json"
SCHEMA = P / "schema/berger-apparatus-160-executable-unary-export-input-shortfall-v1.schema.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    cert, payload = json.loads(C.read_text()), json.loads(X.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(cert)
    assert sha256(X) == cert["payload_ref"]["sha256"]
    for ref in cert["dependency_refs"].values():
        path = ROOT / ref["path"]
        assert sha256(path) == ref["sha256"]
        assert json.loads(path.read_text())["result_id"] == ref["result_id"]
    replacement = json.loads((ROOT / cert["dependency_refs"]["replacement_payload"]["path"]).read_text())
    material = json.loads((ROOT / cert["dependency_refs"]["material_payload"]["path"]).read_text())
    assert "sparse_entries" not in replacement["complete_unary"]
    assert "coefficient_ring" not in replacement["complete_unary"]
    assert "q1_sparse_entries" not in material
    assert "pairing_sparse_entries" not in material
    assert set(payload["base_input_audit"]) == {"replacement_112", "material_parent_56"}
    assert set(payload["export_disposition"].values()) == {"NO_CERTIFIED_MAP"}
    assert payload["non_substitution_replay"]["old_108_block_count"] > 0
    assert cert["atlas_status"] == "NO_CERTIFIED_MAP"
    print("BERGER_APPARATUS_160_EXECUTABLE_UNARY_EXPORT_INPUT_SHORTFALL independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
