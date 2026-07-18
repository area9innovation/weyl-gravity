#!/usr/bin/env python3
"""Independent verifier for the compensator-extension preflight."""

from __future__ import annotations

from copy import deepcopy
import json

from jsonschema import Draft202012Validator

try:
    from .wess_zumino_extension_preflight import OUTPUT, SCHEMA, build, validate
except ImportError:
    from wess_zumino_extension_preflight import OUTPUT, SCHEMA, build, validate


def verify() -> dict:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("Wess-Zumino preflight does not reproduce")
    comparison = value["cohomology_comparison"]
    matrices = value["doublet_contraction"]["restricted_matrices"]
    if (
        comparison["extended_boundary_matrix"] != [[1, 0], [0, 1]]
        or comparison["extended_boundary_rank"] != 2
        or matrices["Q_squared"] != [[0 for _ in range(4)] for _ in range(4)]
        or matrices["anticommutator"] != matrices["N"]
        or matrices["Qh"] == matrices["hQ"]
        or value["extension"]["dressed_metric_Weyl_weights"]
        != {"exp_minus_2_tau": -2, "metric": 2, "sum": 0}
        or value["local_primitives"]["primitive_coordinates"]
        != value["local_primitives"]["image_coordinates"]
    ):
        raise ValueError("Wess-Zumino exactness replay failed")
    mutant = deepcopy(value)
    mutant["qme_lifecycle"]["full_extended_BV_QME"] = "RESTORED"
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("full-BV QME over-promotion was accepted")
    return value


if __name__ == "__main__":
    verify()
    print("Wess-Zumino extension preflight independent verification: PASS")
