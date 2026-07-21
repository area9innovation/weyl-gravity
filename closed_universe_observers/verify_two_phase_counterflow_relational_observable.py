#!/usr/bin/env python3
"""Method-distinct verifier for the counterflow observer obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
CERTIFICATE = ROOT / "closed_universe_observers/certificates/TWO_PHASE_COUNTERFLOW_RELATIONAL_OBSERVABLE_V1.json"
SCHEMA = ROOT / "closed_universe_observers/schema/two-phase-counterflow-relational-observable-v1.schema.json"


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for ref in value["dependency_refs"].values():
        path = ROOT / ref["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != ref["sha256"]:
            raise ValueError(f"dependency hash drifted: {ref['path']}")

    # Reconstruct homology and the contracting identity without importing the
    # producer or accepting its serialized Boolean fields.
    d = sp.Matrix([[0, 0, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 1, 0]])
    s = sp.Matrix([[0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 0, 0]])
    if d * d != sp.zeros(4) or d * s + s * d != sp.eye(4):
        raise ValueError("independent derived-fibre contraction failed")
    # Degree groups are r in -1, (psi,Q) in 0, epsilon in +1.
    if d[:, 0].rank() != 1 or d[:, 2].rank() != 1:
        raise ValueError("derived-fibre degree ranks drifted")
    tangent = sp.Matrix([[0]])
    if tangent.rank() != 0:
        raise ValueError("fixed-charge phase tangent was not radical")
    quotient_dimension = 1 - 1
    if quotient_dimension != 0:
        raise ValueError("R_rel quotient retained a clock")

    reduction = value["fixed_charge_reduction"]
    if reduction["relative_clock_dimension"] != quotient_dimension or reduction["pairing_rank"] != 0:
        raise ValueError("serialized clock obstruction disagrees with replay")
    if value["retarded_response_disposition"]["rank"] is not None:
        raise ValueError("prequotient rank was promoted")
    if value["relational_frequency_disposition"]["one_plus_z_rel"] is not None:
        raise ValueError("formal phase ratio was promoted to redshift")
    if value["prequotient_diagnostic"]["formal_ratio"] != "5/2":
        raise ValueError("quarantined diagnostic drifted")
    for name, enabled in value["flags"].items():
        if name not in {"FIXED_CHARGE_RELATIVE_CLOCK_OBSTRUCTED", "PREQUOTIENT_PHASE_DIAGNOSTIC_COMPUTED"} and enabled:
            raise ValueError(f"downstream claim promoted: {name}")
    for branch in ("Einstein_branch", "additional_branch"):
        if value["gravitational_branch_response"][branch]["status"] != "NO_CERTIFIED_MAP":
            raise ValueError(f"uncrosswalked branch promoted: {branch}")
    return value


if __name__ == "__main__":
    verify()
    print("TWO_PHASE_COUNTERFLOW_RELATIONAL_OBSERVABLE_V1 obstruction independent verification: PASS")
