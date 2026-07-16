#!/usr/bin/env python3
"""Independent verifier for the extra-branch preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_extra_branch_preflight.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_extra_branch_preflight.schema.json"


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    for record in payload["provenance"]["inputs"].values():
        assert hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest() == record["sha256"]
    current = payload["provenance"]["current_engine"]
    assert hashlib.sha256((ROOT / current["path"]).read_bytes()).hexdigest() == current["sha256"]
    contract = payload["canonical_object_contract"]
    assert contract["definition_is_canonical_quotient_not_complement"] is True
    assert contract["symplectic_complement_is_not_the_definition"] is True
    assert set(payload["result_kind_separation"]) >= {"extra_solution_class", "adjoint_cokernel_class", "presymplectic_radical_class", "gauge_class"}
    assert len(payload["block_solve_ledger"]) == 4
    assert payload["block_solve_ledger"][0]["block"] == "generic axial"
    classification = payload["classification"]
    assert classification["any_extra_solution_class_certified"] is False
    assert classification["extra_branch_pairing_computed"] is False
    assert classification["lorentzian_causal_or_quantum_theorem"] is False
    return payload


if __name__ == "__main__":
    verify_certificate()
    print("EINSTEIN_MAXWELL_WEYL_EXTRA_BRANCH_PREFLIGHT independent verification: PASS")
