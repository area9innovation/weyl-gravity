#!/usr/bin/env python3
"""Independent exact verifier for the exceptional ell=1,k=0 solution cofiber."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_weyl_exceptional_ell1_solution_cofiber.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_weyl_exceptional_ell1_solution_cofiber.schema.json"


def main() -> None:
    value = json.loads(CERT.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(value)
    for record in value["provenance"]["inputs"].values():
        path = ROOT / record["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            raise AssertionError(f"stale exceptional input: {path}")
    x = sp.symbols("x")
    parse = lambda expression: sp.sympify(expression, locals={"x": x})
    projectors = value["explicit_projection"]
    roots = {"twist": 0, "extra": sp.Rational(4, 3), "standard": 4}
    for label, expression in projectors["axial"].items():
        polynomial = parse(expression)
        for root_label, root in roots.items():
            if sp.factor(polynomial.subs(x, root)) != int(label == root_label):
                raise AssertionError(f"axial {label} projector failed at {root_label}")
    for label, expression in projectors["polar"].items():
        polynomial = parse(expression)
        for root_label in ("extra", "standard"):
            if sp.factor(polynomial.subs(x, roots[root_label])) != int(label == root_label):
                raise AssertionError(f"polar {label} projector failed at {root_label}")
    pairing = value["action_derived_pairing"]
    if pairing["extra_Gram"] != [["16", "0"], ["0", "3"]] or pairing["standard_extra_mixed_pairing"] != ["0", "0"]:
        raise AssertionError("exceptional cofiber pairing changed")
    flags = value["classification"]
    if not flags["exceptional_solution_cofiber_certified"] or flags["exceptional_offshell_chain_map_certified"]:
        raise AssertionError("exceptional lifecycle drifted")
    if flags["nonzero_compact_momentum_exceptional_cofiber_certified"] or flags["final_residual_descent_certified"]:
        raise AssertionError("exceptional scope was over-promoted")
    print("EINSTEIN_WEYL_EXCEPTIONAL_ELL1_SOLUTION_COFIBER_V1 independent verification: PASS")


if __name__ == "__main__":
    main()
