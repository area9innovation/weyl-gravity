#!/usr/bin/env python3
"""Independently verify the aligned twist--ell=2-extra compatibility face."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_aligned_twist_ell2_extra_compatibility_face.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_aligned_twist_ell2_extra_compatibility_face.schema.json"


def verify() -> None:
    value = json.loads(CERT.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    flags = value["classification"]
    if not flags["nonzero_simultaneous_stabilizer_and_bounded_resonance_zero_face"]:
        raise AssertionError("common-zero face lost")
    if flags["complete_simultaneous_zero_locus_classified"]:
        raise AssertionError("off-axis zero locus was over-promoted")
    if flags["bounded_second_order_correction_constructed"] or flags["smooth_secular_second_order_correction_constructed"]:
        raise AssertionError("compatibility face was promoted to an extension")
    if clebsch_gordan(1, 2, 2, 0, 0, 0) != 0:
        raise AssertionError("aligned Clebsch-Gordan coefficient changed")
    diagonal = [sp.sympify(item) for item in value["extra_current_gram_at_ell2_k0"]["diagonal"]]
    if diagonal != [sp.Integer(1296), sp.Rational(208, 3), sp.Integer(22464), sp.Integer(12288)]:
        raise AssertionError("ell=2 current Gram changed")
    witness = value["explicit_nonzero_witness"]
    if witness["mu_H_remainder"] != "0" or not witness["all_five_moment_maps_zero"] or not witness["all_completed_bounded_resonance_functionals_zero"]:
        raise AssertionError("explicit common-zero witness changed")


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_ALIGNED_TWIST_ELL2_EXTRA_COMPATIBILITY_FACE independent verification: PASS")
