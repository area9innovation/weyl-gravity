#!/usr/bin/env python3
"""Independent verifier for the minimal-BV WZ cotangent lift."""

from __future__ import annotations

from copy import deepcopy
import json

from jsonschema import Draft202012Validator

try:
    from .wess_zumino_minimal_bv_cotangent_lift import OUTPUT, SCHEMA, build, validate
except ImportError:
    from wess_zumino_minimal_bv_cotangent_lift import OUTPUT, SCHEMA, build, validate


def _multiply(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [
        [sum(left[i][k] * right[k][j] for k in range(4)) for j in range(4)]
        for i in range(4)
    ]


def verify() -> dict:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("minimal-BV WZ cotangent lift does not reproduce")
    quartet = value["contractible_quartet"]
    qh = _multiply(quartet["Q_W"], quartet["h"])
    hq = _multiply(quartet["h"], quartet["Q_W"])
    if (
        _multiply(quartet["Q_W"], quartet["Q_W"]) != quartet["QW_squared"]
        or [[qh[i][j] + hq[i][j] for j in range(4)] for i in range(4)]
        != quartet["number_operator"]
        or value["extended_rows"]["omega_star"]["delta"]["terms"][-1]
        != {"coefficient": 1, "factors": ["tau_star"]}
        or value["extended_rows"]["xi_star"]["delta"]["terms"][-1]
        != {"coefficient": 1, "factors": ["N_tau"]}
    ):
        raise ValueError("independent cotangent/quartet replay failed")
    mutant = deepcopy(value)
    mutant["extended_rows"]["omega_star"]["delta"]["terms"][-1]["coefficient"] = -1
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("wrong compensator cotangent sign was accepted")
    mutant = deepcopy(value)
    mutant["qme_lifecycle"]["full_extended_BV_QME"] = "RESTORED"
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("full extended QME over-promotion was accepted")
    return value


if __name__ == "__main__":
    verify()
    print("WZ minimal-BV cotangent lift independent verification: PASS")
