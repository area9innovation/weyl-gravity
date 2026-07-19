#!/usr/bin/env python3
"""Independently verify the Einstein-minus balance and frequency gate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_einstein_minus_frequency_gate.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ellipse_einstein_minus_frequency_gate.schema.json"


def verify() -> None:
    value = json.loads(CERT.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)

    for item in value["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise AssertionError(f"stale input hash: {path}")

    d = sp.symbols("d", positive=True)
    rx2 = sp.Rational(115, 16) * d**2
    y1sq = rx2**2 / (243 * d**2)
    y2sq = sp.Rational(75, 746496) * d**2
    control = sp.factor(22464 * y1sq + 12288 * y2sq)
    deficit = sp.factor(sp.Rational(1, 4) * sp.Rational(4, 3) * 16 * rx2 + sp.Rational(1, 4) * sp.Rational(16, 3) * control)
    kappa = sp.Rational(1, 4) * (6 - 2 * sp.sqrt(3)) * (3 * sp.sqrt(3) - 1)
    occupation = sp.radsimp(deficit / kappa)
    expected = sp.Rational(1, 9477) * (9342240 + 7785200 * sp.sqrt(3)) * d**2
    if control != sp.Rational(1547725, 324) * d**2:
        raise AssertionError("ell=2 control occupation changed")
    if deficit != sp.Rational(1557040, 243) * d**2:
        raise AssertionError("Hamiltonian deficit changed")
    if sp.simplify(occupation - expected) != 0:
        raise AssertionError("Einstein-minus balancing occupation changed")

    records = value["frequency_census"]["records"]
    if len(records) != 40 or any(record["collision"] for record in records):
        raise AssertionError("frequency census is incomplete or resonant")
    for record in records:
        if record["L"] != 0 and sp.sympify(record["residual_minpoly_constant"]) == 0:
            raise AssertionError("a recorded algebraic residual can vanish")

    flags = value["classification"]
    if not flags["mu_H_mu_Px_mu_Ji_all_zero_on_balanced_axisymmetric_fixture"]:
        raise AssertionError("stabilizer balance was lost")
    if flags["complete_quadratic_source_solved"] or flags["bounded_second_order_extension_certified"]:
        raise AssertionError("source-level theorem was over-promoted")


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_EINSTEIN_MINUS_FREQUENCY_GATE independent verification: PASS")
