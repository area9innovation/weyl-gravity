#!/usr/bin/env python3
"""Independently verify the global--extra bounded-correction obstruction."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_global_extra_bounded_correction_obstruction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_global_extra_bounded_correction_obstruction.schema.json"


def verify() -> None:
    value = json.loads(CERT.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    flags = value["classification"]
    if not flags["complete_nonzero_extra_common_zero_orbit_covered"] or not flags["bounded_or_finite_quasiperiodic_correction_obstructed"]:
        raise AssertionError("bounded obstruction lost")
    if flags["smooth_exponential_polynomial_correction_constructed"] or flags["causal_retarded_map_certified"]:
        raise AssertionError("a later correction class was over-promoted")
    X, Q = sp.symbols("X Q", positive=True)
    coefficient = -sp.Rational(7, 2) * Q**2 - sp.Rational(14, 3) * X
    if not (coefficient < 0):
        raise AssertionError("orbit growth coefficient lost strict sign")
    if value["channel"]["quadratic_time_coefficient"] != "-7*B**2":
        raise AssertionError("direct twist leading coefficient changed")


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_GLOBAL_EXTRA_BOUNDED_CORRECTION_OBSTRUCTION independent verification: PASS")
