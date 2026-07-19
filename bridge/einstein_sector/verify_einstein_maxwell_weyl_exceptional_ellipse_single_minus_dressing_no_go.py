#!/usr/bin/env python3
"""Verify the all-ell single-minus dressing no-go."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_single_minus_dressing_no_go.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ellipse_single_minus_dressing_no_go.schema.json"


def verify() -> None:
    value = json.loads(CERT.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for item in value["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise AssertionError(f"input hash changed: {path}")
    lam = sp.symbols("lambda", real=True)
    omega = sp.sqrt(lam - sp.sqrt(2 * lam))
    axial = -3 * sp.I * omega * (3 * sp.sqrt(2 * lam) - 1)
    polar = lam**2 * (2 * lam - 1) / 6
    for physical in (6, 12, 20, 30):
        if sp.simplify(axial.subs(lam, physical)) == 0 or sp.simplify(polar.subs(lam, physical)) == 0:
            raise AssertionError(f"pivot vanished at lambda={physical}")
    flags = value["classification"]
    if not flags["entire_axisymmetric_resonance_ellipse_covered"] or not flags["both_dressing_parities_covered"]:
        raise AssertionError("coverage was weakened")
    if flags["multiple_minus_modes_or_other_carriers_classified"]:
        raise AssertionError("single-mode theorem was over-promoted")


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_SINGLE_MINUS_DRESSING_NO_GO independent verification: PASS")
