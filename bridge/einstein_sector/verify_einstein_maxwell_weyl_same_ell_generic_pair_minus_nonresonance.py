#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_ell_generic_pair_minus_nonresonance.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_ell_generic_pair_minus_nonresonance.schema.json"


def verify() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for item in value["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]

    def frequencies(ell: int) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
        lam = ell * (ell + 1)
        return (
            sp.sqrt(lam - sp.sqrt(2 * lam)),
            sp.sqrt(sp.Rational(lam) - sp.Rational(2, 3)),
            sp.sqrt(lam + sp.sqrt(2 * lam)),
        )

    for ell in range(2, 13):
        branches = frequencies(ell)
        targets = [frequencies(output)[0] for output in range(2, 2 * ell + 1)]
        for first_index, first in enumerate(branches):
            for second in branches[first_index:]:
                for candidate in (first + second, abs(first - second)):
                    assert all(sp.simplify(candidate - target) != 0 for target in targets)

    classification = value["classification"]
    assert classification["combined_all_generic_input_ell_pairs_minus_nonresonant"]
    assert not classification["exceptional_ell1_times_generic_pairs_classified"]
    assert not classification["quadratic_source_coefficients_computed"]


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_SAME_ELL_GENERIC_PAIR_MINUS_NONRESONANCE independent verification: PASS")
