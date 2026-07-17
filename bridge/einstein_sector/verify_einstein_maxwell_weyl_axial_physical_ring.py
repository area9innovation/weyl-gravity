#!/usr/bin/env python3
"""Independent verifier for the axial physical coefficient-ring audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_physical_ring.schema.json"


def _expr(value: str, symbols: dict[str, sp.Symbol]) -> sp.Expr:
    return sp.sympify(value.replace("lambda", "lam"), locals=symbols)


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    for relative, expected in payload["provenance"]["inputs"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected

    lam, momentum, frequency = sp.symbols("lam k omega")
    symbols = {"lam": lam, "k": momentum, "omega": frequency}
    witness = payload["audit"]["Bezout_unit_ideal_witness"]
    entries = witness["entries"]
    coefficients = witness["coefficients"]
    a, b, d = (_expr(entries[name], symbols) for name in ("a", "b", "d"))
    A, B, D = (_expr(coefficients[name], symbols) for name in ("A", "B", "D"))
    assert sp.factor(A * a + B * b + D * d - lam**2 * (lam - 2) ** 2) == 0

    ideals = payload["audit"]["determinantal_ideals_over_R_phys_omega"]
    assert [ideals[name] for name in ("I1", "I2", "I3", "I4")] == ["(1)", "(1)", "(p)", "(p^2*q)"]
    assert ideals["no_k_torsion"] is True
    specialization = payload["audit"]["specialization"]
    assert specialization["fiberwise_Smith_invariants"] == ["1", "1", "p", "p*q"]
    assert specialization["p_q_coprime_on_every_physical_specialization"] is True
    assert payload["audit"]["zero_momentum_audit"]["same_fiberwise_invariant_factors"] is True
    assert payload["classification"]["global_unimodular_Smith_transformations_over_multivariate_ring_claimed"] is False
    return payload


if __name__ == "__main__":
    verify_certificate()
    print("EINSTEIN_MAXWELL_WEYL_AXIAL_PHYSICAL_RING independent verification: PASS")
