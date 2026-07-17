#!/usr/bin/env python3
"""Independent replay of the Nariai pointwise BGG curvature defect."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_kostant_compression import (
    AdjointTractorKostantCompression,
    _adjoint_basis,
    _coordinate_map,
)


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/NARIAI_POINTWISE_BGG_CURVATURE_COMPRESSION_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-pointwise-bgg-curvature-compression-obstruction-v1.schema.json"


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
    for name, dep in value["dependency_refs"].items():
        if _sha256(ROOT / dep["path"]) != dep["sha256"]:
            raise ValueError(f"dependency drifted: {name}")

    eta = sp.diag(-1, 1, 1, 1)
    names, basis = _adjoint_basis()
    embedded, left = _coordinate_map(basis)

    def g(a: int, b: int) -> sp.Expr:
        return eta[a, b]

    def weyl(a: int, b: int, c: int, d: int) -> sp.Expr:
        same = all(index < 2 for index in (a, b, c, d)) or all(index >= 2 for index in (a, b, c, d))
        riemann = g(a, c) * g(b, d) - g(a, d) * g(b, c) if same else 0
        wedge = g(a, c) * g(d, b) - g(a, d) * g(c, b)
        return sp.simplify(riemann - wedge + sp.Rational(2, 3) * wedge)

    curvature = []
    for a in range(4):
        row = []
        for b in range(4):
            standard = sp.zeros(6)
            for c in range(4):
                for d in range(4):
                    standard[1 + c, 1 + d] = sum(eta[c, e] * weyl(a, b, e, d) for e in range(4))
            row.append(sp.Matrix.hstack(*(left * (standard * x - x * standard).reshape(36, 1) for x in basis)))
        curvature.append(row)
    action = sp.Matrix.vstack(*(sp.Matrix.hstack(*(eta[a, a] * curvature[b][a] for a in range(4))) for b in range(4)))
    algebraic = AdjointTractorKostantCompression.build()
    compressed = -algebraic.p1 * action * algebraic.i1
    defect = algebraic.endpoint_field_pairing * compressed - compressed.T * algebraic.endpoint_field_pairing
    checks = value["exact_checks"]
    actual = {
        "curvature_action_rank": action.rank(),
        "compressed_rank": compressed.rank(),
        "cyclic_defect_rank": defect.rank(),
        "normalized_witness_value": str(defect[1, 4]),
    }
    if any(checks[name] != result for name, result in actual.items()):
        raise ValueError(f"independent pointwise compression drifted: {actual}")
    if value["flags"]["NARIAI_CURVED_BGG_HPL_COMPRESSION"] is not False:
        raise ValueError("full HPL was overpromoted")
    print("NARIAI_POINTWISE_BGG_CURVATURE_COMPRESSION_OBSTRUCTION_V1 independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
