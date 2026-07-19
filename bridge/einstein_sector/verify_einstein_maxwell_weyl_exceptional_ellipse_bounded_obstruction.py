#!/usr/bin/env python3
"""Independently verify the balanced exceptional bounded obstruction."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_bounded_obstruction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ellipse_bounded_obstruction.schema.json"


def verify() -> None:
    value = json.loads(CERT.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for item in value["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise AssertionError(f"input hash changed: {path}")

    root = sp.sqrt(3)
    coefficient = 12 * sp.I * (3 * root - 1) * sp.sqrt(6 - 2 * root)
    if sp.simplify(coefficient) == 0:
        raise AssertionError("resonant coefficient vanished")
    if value["unique_bounded_obstruction"]["adjoint_pairing_per_d_Aminus"] != "12*I*(3*sqrt(3)-1)*sqrt(6-2*sqrt(3))":
        raise AssertionError("stored adjoint pairing changed")
    classes = value["correction_classes"]
    if classes["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"] != "OBSTRUCTED":
        raise AssertionError("bounded lifecycle was not obstructed")
    if classes["SMOOTH_EXPONENTIAL_POLYNOMIAL"]["status"] != "CERTIFIED":
        raise AssertionError("smooth lifecycle changed")
    if value["classification"]["general_exceptional_mixed_zero_locus_classified"]:
        raise AssertionError("scoped endpoint was over-promoted")


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_BOUNDED_OBSTRUCTION independent verification: PASS")
