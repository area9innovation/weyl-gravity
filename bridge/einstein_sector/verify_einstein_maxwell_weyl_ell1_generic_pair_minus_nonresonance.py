#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_generic_pair_minus_nonresonance.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell1_generic_pair_minus_nonresonance.schema.json"


def verify() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for item in value["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]

    exceptional = 2 / sp.sqrt(3)
    assert sp.Rational(23, 20) < exceptional < sp.Rational(7, 6)
    for ell in range(2, 9):
        lam = ell * (ell + 1)
        branches = (
            sp.sqrt(lam - sp.sqrt(2 * lam)),
            sp.sqrt(sp.Rational(lam) - sp.Rational(2, 3)),
            sp.sqrt(lam + sp.sqrt(2 * lam)),
        )
        targets = []
        for output in (ell - 1, ell, ell + 1):
            if output >= 2:
                target_lam = output * (output + 1)
                targets.append(sp.sqrt(target_lam - sp.sqrt(2 * target_lam)))
        for branch in branches:
            for dipole in (exceptional, sp.Integer(2)):
                for candidate in (branch + dipole, abs(branch - dipole)):
                    assert all(sp.simplify(candidate - target) != 0 for target in targets)

    classification = value["classification"]
    assert classification["complete_k0_oscillator_pair_to_minus_census_closed"]
    assert not classification["quadratic_source_coefficients_computed"]


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_ELL1_GENERIC_PAIR_MINUS_NONRESONANCE independent verification: PASS")
