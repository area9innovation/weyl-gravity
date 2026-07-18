#!/usr/bin/env python3
"""Fast independent replay of the d-times-polar source fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_d_polar_ell2_extra_source_fixture.schema.json"


def parse(values: list[str]) -> sp.Matrix:
    return sp.Matrix([sp.sympify(value, locals={"I": sp.I, "sqrt": sp.sqrt}) for value in values])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=("e1", "e2"), required=True)
    args = parser.parse_args()
    path = ROOT / f"bridge/certificates/einstein_maxwell_weyl_d_polar_ell2_extra_{args.case}_source_fixture.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(value)
    expected = {
        "e1": sp.Matrix([0, -6 * sp.sqrt(3) * sp.I, 0, 0]),
        "e2": sp.Matrix([-376 * sp.sqrt(3) * sp.I, 0, -sp.Rational(632, 9) * sp.sqrt(3) * sp.I, 384 * sp.sqrt(3) * sp.I]),
    }
    if parse(value["bilinear_source_rows"]) != expected[args.case]:
        raise AssertionError("stored polar source changed")
    if args.case == "e2":
        components = value["e2_sparse_decomposition"]["component_sources"]
        rebuilt = -8 * parse(components["at"]) - 72 * parse(components["ct"]) + 48 * parse(components["u"])
        if rebuilt != expected["e2"]:
            raise AssertionError("sparse e2 decomposition failed")
    print(f"EINSTEIN_MAXWELL_WEYL_D_POLAR_ELL2_EXTRA_{args.case.upper()}_SOURCE_FIXTURE fast verification: PASS")


if __name__ == "__main__":
    main()
