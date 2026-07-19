#!/usr/bin/env python3
"""Independent replay of the five-current de Rham carrier."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.relative import einstein_weyl_relative_five_current_de_rham_carrier as producer


def verify() -> dict[str, object]:
    value = json.loads(producer.OUTPUT.read_text())
    schema = json.loads(producer.SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for name, artifact in value["dependencies"].items():
        path = producer.ROOT / artifact["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != artifact["sha256"]:
            raise AssertionError(f"dependency drifted: {name}")
    for relative, digest in value["provenance"]["source_manifest"].items():
        if hashlib.sha256((producer.ROOT / relative).read_bytes()).hexdigest() != digest:
            raise AssertionError(f"source drifted: {relative}")

    zeta = sp.symbols("independent_zeta_0:4")
    d = [producer.exterior_symbol(p, zeta) for p in range(4)]
    for p in range(3):
        if d[p + 1] * d[p] != sp.zeros(d[p + 1].rows, d[p].cols):
            raise AssertionError(f"d squared failed at form degree {p}")
    for p in range(4):
        defect = d[p].T * producer.wedge_pairing(p + 1) + ((-1) ** (p + 1)) * producer.wedge_pairing(p) * d[3 - p]
        if defect != sp.zeros(defect.rows, defect.cols):
            raise AssertionError(f"Stokes identity failed at form degree {p}")
    fixture = {zeta[i]: value for i, value in enumerate((2, 3, 5, 7))}
    ranks = [int(matrix.subs(fixture).rank()) for matrix in d]
    if ranks != [1, 3, 3, 1]:
        raise AssertionError("independent nonzero-covector rank fixture failed")

    layout = json.loads(producer.GENERATED.read_text())
    rows = layout["rows"]
    if len(rows) != 160 or layout["degree_ranks_minus2_to3"] != [5, 25, 50, 50, 25, 5]:
        raise AssertionError("carrier layout changed")
    if any(rows[row["dual_row"]]["dual_row"] != row["index"] for row in rows):
        raise AssertionError("carrier duality is not involutive")
    pairing = {(term["left_row"], term["right_row"]): term["coefficient"] for term in layout["odd_pairing"]}
    if len(pairing) != 160 or any(pairing[(j, i)] != -coefficient for (i, j), coefficient in pairing.items()):
        raise AssertionError("odd pairing signs are not skew and nondegenerate")
    unary = layout["unary_terms"]
    if len(unary) != 320 or any(term["derivative"] not in producer.COORDINATES for term in unary):
        raise AssertionError("portable unary incidence is incomplete")
    records = layout["current_cone_embedding"]["records"]
    if len(records) != 50 or len({record["new_row"] for record in records}) != 50:
        raise AssertionError("old current cone did not embed")
    expected_hodge = {"current_H_t": 1, "current_H_x": -1, "current_H_theta": 1, "current_H_phi": -1}
    actual_hodge = {record["old_row_id"]: record["coefficient"] for record in records if record["old_row_id"] in expected_hodge}
    if actual_hodge != expected_hodge:
        raise AssertionError("vector-density to three-form Hodge signs changed")
    if value["classification"]["full_augmented_q2_identity_certified"]:
        raise AssertionError("q2 was promoted by the unary carrier")
    return {"status": "PASS", "rows": 160, "embedded_rows": 50, "generic_ranks": ranks}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
