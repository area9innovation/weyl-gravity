#!/usr/bin/env python3
"""Independently verify the balanced exceptional zero-frequency source."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_zero_frequency_source.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ellipse_zero_frequency_source.schema.json"


def verify() -> None:
    value = json.loads(CERT.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for item in value["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise AssertionError(f"input hash changed: {path}")

    d = sp.symbols("d", nonzero=True, real=True)
    root = sp.sqrt(3)
    rx2 = sp.Rational(115, 16) * d**2
    y1sq = rx2**2 / (243 * d**2)
    y2sq = sp.Rational(75, 746496) * d**2
    direct_minus2 = sp.Rational(60125, 17496) * (6 + 5 * root) * d**2
    total = (
        -sp.Rational(16, 9) * rx2
        - sp.Rational(29952, 5) * y1sq
        - sp.Rational(12, 5) * sp.Rational(4096, 3) * y2sq
        + sp.Rational(48, 5) * (-6 + 5 * root) * direct_minus2
    )
    if sp.factor(total) != 0:
        raise AssertionError("independent E00 cancellation failed")
    flags = value["classification"]
    if not flags["complete_zero_frequency_source_solved"]:
        raise AssertionError("zero-frequency theorem was lost")
    if flags["complete_nonzero_frequency_polynomial_source_solved"] or flags["bounded_second_order_extension_certified"]:
        raise AssertionError("bounded theorem was over-promoted")


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_ZERO_FREQUENCY_SOURCE independent verification: PASS")
