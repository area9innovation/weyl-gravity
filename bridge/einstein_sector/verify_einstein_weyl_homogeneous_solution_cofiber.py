#!/usr/bin/env python3
"""Independent verifier for the zero homogeneous solution cofiber."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_weyl_homogeneous_solution_cofiber.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_weyl_homogeneous_solution_cofiber.schema.json"


def main() -> None:
    value = json.loads(CERT.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(value)
    for record in value["provenance"]["inputs"].values():
        path = ROOT / record["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            raise AssertionError(f"stale homogeneous input: {path}")
    theorem = value["polynomial_gauge_and_kernel_theorem"]
    matrix = sp.Matrix([[sp.Rational(entry) for entry in row] for row in theorem["source_to_target_metric_kernel"]])
    if matrix.det() != sp.Rational(1, 3):
        raise AssertionError("homogeneous coefficient dictionary lost invertibility")
    expected_inverse = sp.Matrix([[0, 0, 1, 0], [0, 0, 0, 3], [1, 0, 1, 0], [0, 1, 0, 3]])
    if matrix.inv() != expected_inverse:
        raise AssertionError("homogeneous inverse dictionary changed")
    flags = value["classification"]
    if not flags["homogeneous_solution_cofiber_zero"] or not flags["homogeneous_pairing_transport_certified"]:
        raise AssertionError("homogeneous solution-cofiber theorem was lost")
    if flags["homogeneous_offshell_chain_map_certified"] or flags["large_gauge_and_final_residual_descent_certified"]:
        raise AssertionError("homogeneous lifecycle was over-promoted")
    print("EINSTEIN_WEYL_HOMOGENEOUS_SOLUTION_COFIBER_V1 independent verification: PASS")


if __name__ == "__main__":
    main()
