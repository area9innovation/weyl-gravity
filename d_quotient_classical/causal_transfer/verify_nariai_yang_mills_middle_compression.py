#!/usr/bin/env python3
"""Independent consumer of the Nariai algebraic endpoint obstruction."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.nariai_yang_mills_middle_compression import (
    ROOT,
    OUTPUT,
    SCHEMA,
)
from d_quotient_classical.causal_transfer.verify_nariai_first_differential_bgg_correction import (
    _matrix,
    _table,
)


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict[str, object]:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for relative, digest in value["provenance"]["source_manifest"].items():
        if _sha256(ROOT / relative) != digest:
            raise ValueError(f"source digest drifted: {relative}")
    for name, dependency in value["dependency_refs"].items():
        if _sha256(ROOT / dependency["path"]) != dependency["sha256"]:
            raise ValueError(f"dependency drifted: {name}")

    data = value["exact_data"]
    k = _table(data["first_bgg_operator"])
    gauge = _table(data["naive_gauge_defect"])
    correction = _matrix(data["unique_endpoint_correction"])
    pairing = _matrix(data["endpoint_pairing"])
    cyclic = _matrix(data["endpoint_cyclic_defect"])
    repaired = _table(data["repaired_gauge_defect"])
    if repaired:
        raise ValueError("serialized repaired gauge defect is nonzero")

    k_stack = sp.Matrix.hstack(*(k[(axis,)] for axis in range(4)))
    gauge_stack = sp.Matrix.hstack(*(gauge[(axis,)] for axis in range(4)))
    if k_stack.rank() != 9:
        raise ValueError("conformal-Killing symbol stack lost full row rank")
    if correction * k_stack + gauge_stack != sp.zeros(9, 16):
        raise ValueError("exported algebraic repair does not cancel the gauge defect")
    independent = sp.zeros(9)
    for row in range(9):
        solution, parameters = k_stack.T.gauss_jordan_solve(
            -gauge_stack[row, :].T
        )
        if parameters.rows:
            raise ValueError("algebraic repair ceased to be unique")
        independent[row, :] = solution.T
    if independent != correction:
        raise ValueError("independent algebraic solve disagrees with export")
    actual_cyclic = pairing * correction - correction.T * pairing
    if actual_cyclic != cyclic or cyclic.rank() != 2:
        raise ValueError("cyclic obstruction drifted")
    if -cyclic[1, 4] / 3 != 1:
        raise ValueError("normalized cyclic witness drifted")
    if value["flags"]["NARIAI_CURVED_BGG_HPL_COMPRESSION"] is not False:
        raise ValueError("full curved compression was overpromoted")
    print("NARIAI_ALGEBRAIC_ENDPOINT_CURVATURE_REPAIR_OBSTRUCTION_V1 independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
