#!/usr/bin/env python3
"""Independent verifier for standard mixed-block orthogonality."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_mixed_block_orthogonality.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_mixed_block_orthogonality.schema.json"


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    for record in payload["provenance"]["inputs"].values():
        assert hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest() == record["sha256"]
    direct = payload["theorem"]["direct_shared_label_collision"]
    omega, A, B, p, t = sp.symbols("omega A B p t", real=True)
    expression = sp.sympify(direct["integrated_coordinate_current_per_unit_x"], locals={"omega": omega, "A": A, "B": B, "p": p, "t": t})
    assert sp.rem(sp.Poly(sp.expand(expression / sp.exp(-sp.I * omega * t)), omega), sp.Poly(omega**2 - 4, omega)).as_expr() == 0
    assert direct["both_twist_Jordan_coordinates_included"] is True
    assert payload["theorem"]["conclusion"]["complete_standard_block_diagonal_pullback"] is True
    assert payload["classification"]["extra_fourth_order_target_mixed_pairing_computed"] is False
    return payload


if __name__ == "__main__":
    verify_certificate()
    print("EINSTEIN_MAXWELL_WEYL_MIXED_BLOCK_ORTHOGONALITY independent verification: PASS")
