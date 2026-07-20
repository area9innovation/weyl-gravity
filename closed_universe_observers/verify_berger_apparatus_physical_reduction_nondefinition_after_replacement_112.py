#!/usr/bin/env python3
"""Independent structural verifier for the physical-reduction nondefinition."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_APPARATUS_PHYSICAL_REDUCTION_NONDEFINITION_AFTER_REPLACEMENT_112.json"
X = P / "certificates/BERGER_APPARATUS_PHYSICAL_REDUCTION_NONDEFINITION_AFTER_REPLACEMENT_112_PAYLOAD.json"
SCHEMA = P / "schema/berger-apparatus-physical-reduction-nondefinition-after-replacement-112-v1.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    cert, payload = json.loads(C.read_text()), json.loads(X.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(cert)
    assert sha(X) == cert["payload_ref"]["sha256"]
    for ref in cert["dependency_refs"].values():
        assert sha(ROOT / ref["path"]) == ref["sha256"]
    combined = json.loads((ROOT / cert["dependency_refs"]["combined_payload"]["path"]).read_text())
    replacement = json.loads((ROOT / cert["dependency_refs"]["replacement_payload"]["path"]).read_text())
    required = set(payload["executable_reduction_audit"]["required_operator_fields"])
    assert not required.intersection(combined["complete_q1"])
    assert not required.intersection(replacement["complete_unary"])
    assert combined["carrier"]["row_count"] == 160
    assert combined["carrier"]["pairing_rank"] == 160
    assert set(payload["downstream_nondefinition"].values()) == {"NO_CERTIFIED_MAP"}
    assert cert["atlas_status"] == "NO_CERTIFIED_MAP"
    print("BERGER_APPARATUS_PHYSICAL_REDUCTION_NONDEFINITION_AFTER_REPLACEMENT_112 independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
