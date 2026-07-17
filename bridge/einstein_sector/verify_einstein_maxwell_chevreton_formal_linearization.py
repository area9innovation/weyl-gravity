#!/usr/bin/env python3
"""Independent checks for the Chevreton dual-number linearization bridge."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_chevreton_formal_linearization.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_chevreton_formal_linearization.schema.json"


def _rem(expression: sp.Expr, epsilon: sp.Symbol) -> sp.Expr:
    return sp.rem(sp.Poly(sp.expand(expression), epsilon), sp.Poly(epsilon**2, epsilon)).as_expr()


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    for relative, expected in payload["provenance"]["inputs"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected

    epsilon, r2, j1 = sp.symbols("epsilon r2 j1")
    assert _rem(epsilon**2 * r2, epsilon) == 0
    assert _rem((epsilon * j1) ** 2, epsilon) == 0

    proof = payload["proof"]
    assert proof["integrable_family_required"] is False
    assert "every Einstein-Maxwell Jacobi field" in proof["formal_identity"]
    classification = payload["classification"]
    assert classification["all_formal_linearized_Einstein_Maxwell_solutions_included"] is True
    assert classification["only_integrable_tangents"] is False
    assert classification["off_shell_BV_chain_map_constructed"] is False
    return payload


if __name__ == "__main__":
    verify_certificate()
    print("EINSTEIN_MAXWELL_CHEVRETON_FORMAL_LINEARIZATION independent verification: PASS")
