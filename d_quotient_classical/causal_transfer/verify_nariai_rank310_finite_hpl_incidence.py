#!/usr/bin/env python3
"""Independent replay of the finite rank-310 HPL incidence theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

import d_quotient_classical.causal_transfer.nariai_parent_detour_mapping_cone_repair as repair
from d_quotient_classical.causal_transfer.nariai_transverse_rank310_dual_sdr import abstract_fixture, matrix_defects


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/NARIAI_RANK310_FINITE_HPL_INCIDENCE_THEOREM_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-rank310-finite-hpl-incidence-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for name, ref in value["dependency_refs"].items():
        path = ROOT / ref["path"]
        payload = json.loads(path.read_text())
        if _sha(path) != ref["sha256"] or payload["result_id"] != ref["artifact_id"]:
            raise ValueError(f"dependency drifted: {name}")
    for relative, digest in value["provenance"]["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise ValueError(f"source drifted: {relative}")

    fixture = abstract_fixture()
    h = fixture["base"]["homotopy"]
    delta = fixture["dotted"]["q_dot"]
    hd = repair._multiply(h, delta)
    dh = repair._multiply(delta, h)
    independent = {
        "Q_Delta_plus_Delta_Q": repair._add(
            repair._multiply(fixture["base"]["q"], delta),
            repair._multiply(delta, fixture["base"]["q"]),
        ),
        "Delta_squared": repair._multiply(delta, delta),
        "H_Delta_squared": repair._multiply(hd, hd),
        "Delta_H_squared": repair._multiply(dh, dh),
        "HPL_inverse_left": repair._add(
            repair._multiply(
                repair._add(repair._identity(len(h)), hd),
                repair._add(repair._identity(len(h)), repair._scale(hd, -1)),
            ),
            repair._scale(repair._identity(len(h)), -1),
        ),
        "HPL_inverse_right": repair._add(
            repair._multiply(
                repair._add(repair._identity(len(h)), dh),
                repair._add(repair._identity(len(h)), repair._scale(dh, -1)),
            ),
            repair._scale(repair._identity(len(h)), -1),
        ),
    }
    if any(matrix_defects(matrix) for matrix in independent.values()):
        raise ValueError("independent finite-incidence replay failed")
    if value["exact_fixture"]["inverse_series_length"] != 2:
        raise ValueError("HPL series no longer terminates after one correction")
    if value["analytic_consequence"]["nonlocal_HPL_inverse_required"]:
        raise ValueError("a nonlocal inverse was introduced")
    if value["flags"]["TRANSVERSE_EXACT_GEOMETRIC_RANK310_FAMILY"]:
        raise ValueError("the missing finite geometry was overclaimed")
    print("NARIAI_RANK310_FINITE_HPL_INCIDENCE_THEOREM_V1 independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
