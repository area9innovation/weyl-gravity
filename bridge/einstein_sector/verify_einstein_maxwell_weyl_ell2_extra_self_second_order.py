#!/usr/bin/env python3
"""Independent verifier for the complete C4 extra-self correction ledger."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_extra_self_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_extra_self_second_order.schema.json"


def main() -> None:
    payload = json.loads(CERT.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = payload["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()

    beta, Q_e, X = sp.symbols("beta Q_e X", real=True)
    combined = beta**2 - Q_e**2 / 2 - sp.Rational(2, 3) * X
    assert sp.factor(combined.subs(beta**2, Q_e**2 / 2 + sp.Rational(2, 3) * X)) == 0
    ledger = payload["bilinear_correction_ledger"]
    assert len(ledger) == 20
    for entry in ledger.values():
        for block in entry["blocks"].values():
            assert all(sp.sympify(value) == 0 for value in block["remainder"])
        if "remainder" in entry.get("homogeneous_L0", {}):
            assert all(sp.sympify(value) == 0 for value in entry["homogeneous_L0"]["remainder"])
    flags = payload["classification"]
    assert flags["complete_C4_extra_self_source_coefficient_explicit"] is True
    assert flags["arbitrary_relative_phases_covered"] is True
    assert flags["causal_retarded_or_all_orders_claim"] is False


if __name__ == "__main__":
    main()
