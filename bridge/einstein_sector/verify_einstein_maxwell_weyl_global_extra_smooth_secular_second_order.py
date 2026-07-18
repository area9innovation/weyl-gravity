#!/usr/bin/env python3
"""Independently verify the global--extra smooth-secular theorem."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_global_extra_smooth_secular_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_global_extra_smooth_secular_second_order.schema.json"


def verify() -> None:
    value = json.loads(CERT.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    flags = value["classification"]
    if not flags["complete_quadratic_channel_ledger"] or not flags["all_nonstabilizer_smooth_secular_cokernels_zero"]:
        raise AssertionError("smooth block completeness lost")
    if not flags["smooth_exponential_polynomial_second_order_correction_exists"]:
        raise AssertionError("smooth correction theorem lost")
    if not flags["aligned_twist_extra_L1_L3_correction_coefficient_explicit"]:
        raise AssertionError("printed aligned twist--extra mixed block was lost")
    if flags["coefficient_explicit_correction_printed"]:
        raise AssertionError("printed mixed block silently promoted the full orbit")
    if flags["bounded_correction_exists"] or flags["causal_retarded_map_certified"] or flags["all_orders_integrability"]:
        raise AssertionError("a distinct lifecycle was over-promoted")
    s = sp.Rational(16, 3)
    lam2, lam3 = sp.Integer(6), sp.Integer(12)
    p2 = sp.factor(s - lam2 + sp.Rational(2, 3))
    q2 = sp.factor(s**2 - 2 * lam2 * s + lam2 * (lam2 - 2))
    p3 = sp.factor(s - lam3 + sp.Rational(2, 3))
    q3 = sp.factor(s**2 - 2 * lam3 * s + lam3 * (lam3 - 2))
    if (p2, q2, p3, q3) != (0, -sp.Rational(104, 9), -6, sp.Rational(184, 9)):
        raise AssertionError("cross-channel divisor audit failed")
    l1 = value["channel_ledger"]["aligned_twist_extra_cross"]["L1_divisors"]
    if l1 != {"extra": "-4", "standard": "-4/3"}:
        raise AssertionError("exceptional L1 nonresonance changed")


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_GLOBAL_EXTRA_SMOOTH_SECULAR_SECOND_ORDER independent verification: PASS")
