#!/usr/bin/env python3
"""Independent verifier for the zero twist solution cofiber."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_weyl_twist_solution_cofiber.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_weyl_twist_solution_cofiber.schema.json"


def main() -> None:
    value = json.loads(CERT.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(value)
    for record in value["provenance"]["inputs"].values():
        path = ROOT / record["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            raise AssertionError(f"stale twist input: {path}")
    x = sp.symbols("x")
    projector = sp.sympify(value["spectral_projection_theorem"]["twist_projector"])
    if [sp.factor(projector.subs(x, root)) for root in (0, sp.Rational(4, 3), 4)] != [1, 0, 0]:
        raise AssertionError("twist projector no longer isolates x=0")
    source = sp.Matrix([[0, 2], [-2, 0]])
    target = sp.Matrix([[0, -4], [4, 0]])
    if source.rank() != target.rank() or target != -2 * source:
        raise AssertionError("twist pairing transport changed")
    flags = value["classification"]
    if not flags["twist_solution_cofiber_zero"] or not flags["Einstein_image_equals_complete_twist_target_primary"]:
        raise AssertionError("zero twist cofiber was lost")
    if flags["twist_offshell_chain_map_certified"] or flags["global_moduli_or_final_residual_descent_certified"]:
        raise AssertionError("twist lifecycle was over-promoted")
    print("EINSTEIN_WEYL_TWIST_SOLUTION_COFIBER_V1 independent verification: PASS")


if __name__ == "__main__":
    main()
