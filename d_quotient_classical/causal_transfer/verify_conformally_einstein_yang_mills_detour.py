#!/usr/bin/env python3
"""Independent verifier for the curved Yang--Mills detour correction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/CONFORMALLY_EINSTEIN_YANG_MILLS_DETOUR_CORRECTION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/conformally-einstein-yang-mills-detour-correction-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for relative, digest in value["provenance"]["source_manifest"].items():
        if _sha256(ROOT / relative) != digest:
            raise ValueError(f"source digest drifted: {relative}")
    dep = value["dependency_ref"]
    if _sha256(ROOT / dep["path"]) != dep["sha256"]:
        raise ValueError("Nariai obstruction dependency drifted")

    # Independent block-operator construction.
    a0 = sp.Matrix([[0, 1], [0, 0]])
    a1 = sp.Matrix([[0, 0], [1, 0]])
    connection = [a0, a1]
    curvature = [[connection[a] * connection[b] - connection[b] * connection[a] for b in range(2)] for a in range(2)]
    current = [-sum((connection[a] * curvature[a][b] - curvature[a][b] * connection[a] for a in range(2)), sp.zeros(2)) for b in range(2)]
    laplacian = sum((matrix * matrix for matrix in connection), sp.zeros(2))
    rows = []
    naive_rows = []
    for b in range(2):
        row = []
        naive_row = []
        for a in range(2):
            base = (-laplacian if a == b else sp.zeros(2)) + connection[a] * connection[b]
            row.append(base - curvature[b][a])
            naive_row.append(base)
        rows.append(sp.Matrix.hstack(*row))
        naive_rows.append(sp.Matrix.hstack(*naive_row))
    middle = sp.Matrix.vstack(*rows)
    naive = sp.Matrix.vstack(*naive_rows)
    d = sp.Matrix.vstack(*connection)
    delta = sp.Matrix.hstack(*(-matrix for matrix in connection))
    epsilon = sp.Matrix.vstack(*current)
    minus_iota = sp.Matrix.hstack(*(-matrix for matrix in current))
    ranks = {
        "corrected_left_defect_rank": (middle * d - epsilon).rank(),
        "corrected_right_defect_rank": (delta * middle - minus_iota).rank(),
        "naive_left_defect_rank": (naive * d - epsilon).rank(),
        "naive_right_defect_rank": (delta * naive - minus_iota).rank(),
    }
    for name, rank in ranks.items():
        if value["exact_matrix_fixture"][name] != rank:
            raise ValueError(f"independent detour rank drifted: {name}")
    if list(ranks.values()) != [0, 0, 2, 2]:
        raise ValueError("universal detour identity failed")
    if value["flags"]["NARIAI_CURVED_BGG_HPL_COMPRESSION"] is not False:
        raise ValueError("BGG compression overpromoted")
    print("CONFORMALLY_EINSTEIN_YANG_MILLS_DETOUR_CORRECTION_V1 independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
