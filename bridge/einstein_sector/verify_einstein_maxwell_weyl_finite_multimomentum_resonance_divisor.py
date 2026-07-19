#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_multimomentum_resonance_divisor.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_finite_multimomentum_resonance_divisor.schema.json"


def verify() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for item in value["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]

    rho, A, B, C = sp.symbols("rho A B C", real=True)
    n1, n2 = sp.symbols("n_1 n_2", integer=True, nonzero=True)
    D = C - A - B
    N = n1 + n2
    direct = sp.expand(4 * (n1**2 * rho + A) * (n2**2 * rho + B) - (N**2 * rho + C - n1**2 * rho - A - n2**2 * rho - B) ** 2)
    reduced = sp.expand(4 * (n1**2 * B + n2**2 * A - n1 * n2 * D) * rho + 4 * A * B - D**2)
    assert sp.expand(direct - reduced) == 0
    assert sp.Poly(reduced, rho).degree() <= 1

    numerator = sp.factor(D**2 - 4 * A * B)
    opposite = sp.factor(numerator / (4 * C))
    aligned = sp.factor(numerator / (4 * (2 * A + 2 * B - C)))
    reductions = value["certified_reductions"]
    assert reductions["opposite_equal_absolute_momentum"]["candidate_k_squared_n2rho"] == str(opposite)
    assert reductions["aligned_equal_absolute_momentum"]["candidate_k_squared_n2rho"] == str(aligned)
    classification = value["classification"]
    assert classification["finite_nonidentity_exceptional_circumference_set_certified"]
    assert classification["identity_resonant_channels_fail_closed"]
    assert not classification["quadratic_source_coefficients_computed"]
    assert not classification["complete_multifibre_tangent_cone_classified"]


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_FINITE_MULTIMOMENTUM_RESONANCE_DIVISOR independent verification: PASS")
