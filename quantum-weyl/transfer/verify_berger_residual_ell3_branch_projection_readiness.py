#!/usr/bin/env python3
"""Independent verifier for residual mixed-ell3 branch-projection readiness."""

from __future__ import annotations

from copy import deepcopy
import json

from jsonschema import Draft202012Validator

from local_bv.schema_validation import validate_instance

from .berger_residual_ell3_branch_projection_readiness import (
    INPUT_SCHEMA,
    READINESS_SCHEMA,
    build,
)
from .berger_residual_ell3_branch_projection_readiness_certificate import OUTPUT


def _rejects_overclaim(value: dict) -> None:
    flags = value["claim_flags"]
    if (
        value["result_state"]
        != "CONSUMER_READY_RESIDUAL_BRANCH_BASIS_INPUT_NOT_SUPPLIED"
        or flags["RESIDUAL_BRANCH_BASIS_INPUT_AVAILABLE"]
        or flags["RESIDUAL_BRANCH_BASIS_ACCEPTED"]
        or flags["RESIDUAL_ELL3_BRANCH_PROJECTION_COMPUTED"]
        or flags["RESIDUAL_ELL3_MIXING_TABLE_COMPUTED"]
        or flags["DEFORMATION_VERTEX_PROJECTION_COMPUTED"]
        or flags["TOPOLOGICAL_DEFORMATION_DIRECTION_CLASSIFIED"]
        or flags["RESIDUAL_QUANTUM_TRANSFERRED"]
        or flags["QME_RESTORED"]
        or flags["QUANTUM_CLAIM"]
    ):
        raise ValueError("residual ell3 branch readiness was over-promoted")


def verify() -> dict:
    value = json.loads(OUTPUT.read_text())
    for path in (INPUT_SCHEMA, READINESS_SCHEMA):
        Draft202012Validator.check_schema(json.loads(path.read_text()))
    errors = validate_instance(value, json.loads(READINESS_SCHEMA.read_text()))
    if errors:
        raise ValueError("strict residual ell3 readiness schema failure: " + "; ".join(errors))
    if value != build():
        raise ValueError("residual ell3 branch readiness does not reproduce")
    _rejects_overclaim(value)
    for key in (
        "RESIDUAL_BRANCH_BASIS_INPUT_AVAILABLE",
        "RESIDUAL_BRANCH_BASIS_ACCEPTED",
        "RESIDUAL_ELL3_BRANCH_PROJECTION_COMPUTED",
        "RESIDUAL_ELL3_MIXING_TABLE_COMPUTED",
        "DEFORMATION_VERTEX_PROJECTION_COMPUTED",
        "TOPOLOGICAL_DEFORMATION_DIRECTION_CLASSIFIED",
        "RESIDUAL_QUANTUM_TRANSFERRED",
        "QME_RESTORED",
        "QUANTUM_CLAIM",
    ):
        mutant = deepcopy(value)
        mutant["claim_flags"][key] = True
        try:
            _rejects_overclaim(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"residual ell3 readiness overclaim escaped: {key}")
    return value


if __name__ == "__main__":
    verify()
    print("BERGER residual ell3 branch-projection readiness verifier: PASS")
