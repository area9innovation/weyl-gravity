#!/usr/bin/env python3
"""Independent verifier for the completed homogeneous/twist source matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_ell2_extra_resonance_matrix.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_homogeneous_twist_ell2_extra_resonance_matrix.schema.json"


def _matrix(rows: list[list[str]], time: sp.Symbol) -> sp.Matrix:
    return sp.Matrix([[sp.sympify(value, locals={"I": sp.I, "sqrt": sp.sqrt, "t": time}) for value in row] for row in rows])


def main() -> None:
    value = json.loads(CERT.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(value)
    provenance = value["provenance"]
    for key in ("generator", "direct_source"):
        path = ROOT / provenance[f"{key}_path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != provenance[f"{key}_sha256"]:
            raise AssertionError(f"stale source-matrix {key}: {path}")
    abd = value["homogeneous_abd_input"]
    if hashlib.sha256((ROOT / abd["path"]).read_bytes()).hexdigest() != abd["sha256"]:
        raise AssertionError("stale a,b,d matrix input")
    theorem = value["twist_projection_theorem"]
    time = sp.symbols("t", real=True)
    position = _matrix(theorem["position_matrix"], time)
    velocity = _matrix(theorem["velocity_matrix"], time)
    determinant = sp.factor(velocity.det(method="berkowitz"))
    expected = 4129056 * (72 * time**2 + 34 * sp.sqrt(3) * sp.I * time + 3)
    if position.rank() != 2 or sp.expand(determinant - expected) != 0:
        raise AssertionError("twist matrix rank or determinant changed")
    if clebsch_gordan(1, 2, 2, 1, 0, 1) != sp.sqrt(2) / 2:
        raise AssertionError("Clebsch-Gordan channel changed")
    flags = value["classification"]
    if not flags["complete_homogeneous_twist_bounded_resonance_matrix"]:
        raise AssertionError("complete resonance-matrix flag was lost")
    if flags["simultaneous_stabilizer_and_resonance_zero_locus_solved"] or flags["causal_retarded_sufficiency"]:
        raise AssertionError("tangent-cone lifecycle was over-promoted")
    print("EINSTEIN_MAXWELL_WEYL_HOMOGENEOUS_TWIST_ELL2_EXTRA_RESONANCE_MATRIX independent verification: PASS")


if __name__ == "__main__":
    main()
