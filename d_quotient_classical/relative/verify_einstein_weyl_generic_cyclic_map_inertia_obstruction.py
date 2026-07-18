#!/usr/bin/env python3
"""Independent matrix replay of the generic cyclic-map inertia obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_GENERIC_CYCLIC_MAP_INERTIA_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/einstein-weyl-generic-cyclic-map-inertia-obstruction-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    records = {}
    for name, record in value["dependency_refs"].items():
        path = ROOT / record["path"]
        if _sha(path) != record["sha256"]:
            raise ValueError(f"dependency digest drifted: {name}")
        payload = json.loads(path.read_text())
        if payload.get("result_id", payload.get("schema")) != record["artifact_id"]:
            raise ValueError(f"dependency identity drifted: {name}")
        records[name] = payload
    for relative, digest in value["provenance"]["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise ValueError(f"source digest drifted: {relative}")
    if records["axial_physical_ring"]["classification"]["Einstein_image_equals_complete_q_primary_summand_on_every_physical_fiber"] is not True:
        raise ValueError("axial q-primary completeness disappeared")
    if records["relative_dictionary"]["classification"]["generic_axial_and_polar_solution_cofibers_certified"] is not True:
        raise ValueError("generic solution cofibers disappeared")

    lam = sp.symbols("lambda", positive=True)
    expected = {
        "axial": (sp.diag(lam, 2), sp.Matrix([[1, 3], [sp.Rational(3, 2) * lam, 1]]), 2 * lam, -lam * (9 * lam - 2)),
        "polar": (sp.Matrix([[1, -2], [-2, 2 * lam]]), sp.Matrix([[1, -3 * lam], [-sp.Rational(3, 2), 1]]), 2 * (lam - 2), -(lam - 2) * (9 * lam - 2)),
    }
    for parity, (source, relative, det_source, det_target) in expected.items():
        target = source * relative
        if (
            target != target.T
            or sp.simplify(sp.factor(source.det()) - det_source) != 0
            or sp.simplify(sp.factor(target.det()) - det_target) != 0
        ):
            raise ValueError(f"independent {parity} inertia replay failed")
        row = value["exact_inertia_blocks"][parity]
        if row["Einstein_inertia_lambda_ge_6"] != [2, 0] or row["restricted_Weyl_inertia_lambda_ge_6"] != [1, 1]:
            raise ValueError(f"{parity} inertia ledger drifted")
    if value["shell_separation"]["same_label_frequency_collision"] is not False:
        raise ValueError("shell separation drifted")
    if value["classification"]["standard_pairing_all_sector_cyclic_triangle_possible"] is not False:
        raise ValueError("standard-pairing cyclic triangle was overpromoted")
    if value["classification"]["noncyclic_off_shell_relative_triangle_obstructed"] is not False:
        raise ValueError("noncyclic triangle was falsely obstructed")
    print("EINSTEIN_WEYL_GENERIC_CYCLIC_MAP_INERTIA_OBSTRUCTION_V1 independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
