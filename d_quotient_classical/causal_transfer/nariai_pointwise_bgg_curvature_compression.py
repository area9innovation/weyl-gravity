#!/usr/bin/env python3
"""First Nariai curved-BGG gate: pointwise curvature compression defect."""

from __future__ import annotations

import argparse
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
HERE = ROOT / "d_quotient_classical/causal_transfer"
PARENT = ROOT / "d_quotient_classical/certificates/CONFORMALLY_EINSTEIN_YANG_MILLS_DETOUR_CORRECTION_V1.json"
KOSTANT = ROOT / "covariant_completion/certificates/adjoint_tractor_kostant_compression.json"
KOSTANT_MATRICES = ROOT / "covariant_completion/certificates/adjoint_tractor_kostant_compression_matrices.json"
KOSTANT_CODE = ROOT / "covariant_completion/curved_operator/adjoint_tractor_kostant_compression.py"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_POINTWISE_BGG_CURVATURE_COMPRESSION_OBSTRUCTION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-pointwise-bgg-curvature-compression-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-pointwise-bgg-curvature-compression-obstruction-v1.schema.json"
VERIFIER = HERE / "verify_nariai_pointwise_bgg_curvature_compression.py"
TESTS = HERE / "tests/test_nariai_pointwise_bgg_curvature_compression.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sparse(matrix: sp.Matrix) -> dict[str, object]:
    return {
        "shape": [matrix.rows, matrix.cols],
        "entries": [[row, column, str(matrix[row, column])] for row in range(matrix.rows) for column in range(matrix.cols) if matrix[row, column] != 0],
        "sha256": hashlib.sha256(sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode()).hexdigest(),
    }


def _nariai_weyl(a: int, b: int, c: int, d: int) -> sp.Rational:
    eta = sp.diag(-1, 1, 1, 1)
    g = lambda left, right: eta[left, right]
    one_factor = all(index < 2 for index in (a, b, c, d)) or all(index >= 2 for index in (a, b, c, d))
    riemann = g(a, c) * g(b, d) - g(a, d) * g(b, c) if one_factor else 0
    return sp.simplify(
        riemann
        - sp.Rational(1, 2) * (g(a, c) * g(d, b) - g(a, d) * g(c, b) - g(b, c) * g(d, a) + g(b, d) * g(c, a))
        + sp.Rational(2, 3) * (g(a, c) * g(d, b) - g(a, d) * g(c, b))
    )


def _fixture() -> dict[str, object]:
    eta = sp.diag(-1, 1, 1, 1)
    names, basis = _adjoint_basis()
    embedded, left_inverse = _coordinate_map(basis)

    def coordinates(matrix: sp.Matrix) -> sp.Matrix:
        result = left_inverse * matrix.reshape(36, 1)
        if embedded * result != matrix.reshape(36, 1):
            raise AssertionError("Nariai tractor curvature escaped so(4,2)")
        return result

    adjoint_curvature: list[list[sp.Matrix]] = []
    standard_curvature: list[list[sp.Matrix]] = []
    for left in range(4):
        standard_row = []
        adjoint_row = []
        for right in range(4):
            standard = sp.zeros(6)
            for raised in range(4):
                for lowered in range(4):
                    standard[1 + raised, 1 + lowered] = sum(
                        eta[raised, contracted] * _nariai_weyl(left, right, contracted, lowered)
                        for contracted in range(4)
                    )
            standard_row.append(standard)
            adjoint_row.append(sp.Matrix.hstack(*(coordinates(standard * generator - generator * standard) for generator in basis)))
        standard_curvature.append(standard_row)
        adjoint_curvature.append(adjoint_row)

    curvature_action = sp.Matrix.vstack(*(
        sp.Matrix.hstack(*(eta[source, source] * adjoint_curvature[target][source] for source in range(4)))
        for target in range(4)
    ))
    algebraic = AdjointTractorKostantCompression.build()
    compressed = sp.simplify(-algebraic.p1 * curvature_action * algebraic.i1)
    cyclic_defect = sp.simplify(algebraic.endpoint_field_pairing * compressed - compressed.T * algebraic.endpoint_field_pairing)
    if curvature_action.rank() != 54 or compressed.rank() != 9:
        raise AssertionError("Nariai curvature compression rank drifted")
    if cyclic_defect.rank() != 2 or cyclic_defect[1, 4] != 1:
        raise AssertionError("Nariai cyclic obstruction witness drifted")
    return {
        "basis_names": names,
        "standard_curvature": standard_curvature,
        "curvature_action": curvature_action,
        "compressed": compressed,
        "cyclic_defect": cyclic_defect,
        "pairing": algebraic.endpoint_field_pairing,
    }


def build() -> dict:
    parent = json.loads(PARENT.read_text())
    kostant = json.loads(KOSTANT.read_text())
    if parent["flags"]["NARIAI_CURVED_PARENT_DETOUR_COMPLEX"] is not True:
        raise ValueError("curved Nariai parent unavailable")
    if kostant["theorem_boundary"]["pointwise_kostant_sdr_exact"] is not True:
        raise ValueError("pointwise Kostant compression unavailable")
    fixture = _fixture()
    sources = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA, KOSTANT_CODE)
    }
    return {
        "schema": "pure-weyl-nariai-pointwise-bgg-curvature-compression-obstruction-v1",
        "result_id": "NARIAI_POINTWISE_BGG_CURVATURE_COMPRESSION_OBSTRUCTION_V1",
        "result_state": "POINTWISE_CURVATURE_COMPRESSION_NONCYCLIC",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "curved_parent": {"artifact_id": parent["result_id"], "path": str(PARENT.relative_to(ROOT)), "sha256": _sha256(PARENT)},
            "kostant_sdr": {"artifact_id": "ADJOINT_TRACTOR_KOSTANT_COMPRESSION", "path": str(KOSTANT.relative_to(ROOT)), "sha256": _sha256(KOSTANT)},
            "kostant_matrices": {"artifact_id": "ADJOINT_TRACTOR_KOSTANT_COMPRESSION_MATRICES", "path": str(KOSTANT_MATRICES.relative_to(ROOT)), "sha256": _sha256(KOSTANT_MATRICES)},
        },
        "construction": {
            "standard_tractor_curvature": "Omega_ab has only the Weyl tangent block on Einstein Nariai because Cotton=0",
            "adjoint_action": "Omega_ad X=[Omega_standard,X] on the 15-dimensional adjoint tractor",
            "one_form_curvature_action": "(F dot Psi)_b=F_b^a Psi_a on the 60-dimensional parent middle row",
            "pointwise_compression": "Q_F=-p1 (F dot) i1",
            "omitted_terms": "derivative-dependent BGG splitting/HPL corrections",
        },
        "exact_matrices": {
            "curvature_action": _sparse(fixture["curvature_action"]),
            "pointwise_compressed_curvature": _sparse(fixture["compressed"]),
            "cyclic_defect": _sparse(fixture["cyclic_defect"]),
            "endpoint_pairing": _sparse(fixture["pairing"]),
        },
        "exact_checks": {
            "curvature_action_rank": fixture["curvature_action"].rank(),
            "curvature_action_nonzero_entries": sum(value != 0 for value in fixture["curvature_action"]),
            "compressed_rank": fixture["compressed"].rank(),
            "compressed_nonzero_entries": sum(value != 0 for value in fixture["compressed"]),
            "compressed_characteristic_polynomial": str(sp.factor(fixture["compressed"].charpoly().as_expr())),
            "cyclic_defect_rank": fixture["cyclic_defect"].rank(),
            "cyclic_defect_nonzero_entries": sum(value != 0 for value in fixture["cyclic_defect"]),
            "normalized_witness": "(J Q_F-Q_F^T J)[1,4]",
            "normalized_witness_value": str(fixture["cyclic_defect"][1, 4]),
        },
        "obstruction": {
            "failed_candidate": "the raw pointwise curvature compression -p1(F dot)i1 used as the complete curved endpoint correction",
            "reason": "it is not self-adjoint for the certified endpoint pairing",
            "conclusion": "derivative-dependent curved BGG splitting/HPL corrections are necessary",
            "not_a_global_no_go": True,
        },
        "flags": {
            "NARIAI_POINTWISE_BGG_CURVATURE_COMPRESSION_OBSTRUCTION_V1": True,
            "POINTWISE_CURVATURE_COMPRESSION_IS_CYCLIC": False,
            "DERIVATIVE_BGG_CORRECTIONS_REQUIRED": True,
            "NARIAI_CURVED_BGG_HPL_COMPRESSION": False,
            "NARIAI_GREEN_HOMOTOPY": False,
            "ALL_CURVED_COMPRESSIONS_OBSTRUCTED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "C_G2_NARIAI_FIRST_DIFFERENTIAL_BGG_CORRECTION",
        "claim_boundary": (
            "This exact calculation inserts the Nariai Weyl curvature into the standard and adjoint tractor representations, applies the certified pointwise Kostant inclusion and projection, and proves that the raw compressed curvature action has a rank-two cyclic-adjoint defect with normalized witness one. It establishes that the pointwise term alone cannot be the curved endpoint correction. It does not obstruct the general Bach-flat deformation detour complex or a full differential BGG/HPL compression; on the contrary it identifies the omitted derivative splitting terms as mandatory. No endpoint equality, support, Green, causal, open-family, or quantum claim is made."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_pointwise_bgg_curvature_compression.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_pointwise_bgg_curvature_compression.py",
                "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_nariai_pointwise_bgg_curvature_compression",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-pointwise-bgg-curvature-compression-obstruction-v1.schema.json -d d_quotient_classical/certificates/NARIAI_POINTWISE_BGG_CURVATURE_COMPRESSION_OBSTRUCTION_V1.json",
            ],
        },
    }


def _report(value: dict) -> str:
    checks = value["exact_checks"]
    return rf"""# Nariai pointwise BGG curvature-compression obstruction

The exact Nariai Weyl tensor was inserted into the standard tractor curvature,
lifted by commutator to the 15-dimensional adjoint tractor, and then to the
60-dimensional one-form row.  Its raw pointwise Kostant compression is

\[
Q_F=-p_1(F\!\cdot)i_1.
\]

The parent curvature action has rank `{checks['curvature_action_rank']}` and
the compressed \(9\times9\) term has rank `{checks['compressed_rank']}`.  But

\[
JQ_F-Q_F^TJ
\]

has rank `{checks['cyclic_defect_rank']}`, with the normalized exact witness

\[
(JQ_F-Q_F^TJ)_{{1,4}}={checks['normalized_witness_value']}.
\]

Therefore the pointwise curvature action alone cannot be the curved metric
endpoint correction.  The derivative-dependent BGG splitting/HPL terms are
necessary.  This is a scoped candidate obstruction, not a no-go theorem for
the Bach-flat detour complex or its full differential compression.
"""


def verify(value: dict) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("certificate drifted from exact reconstruction")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.guards:
        checks = value["exact_checks"]
        if [checks["curvature_action_rank"], checks["compressed_rank"], checks["cyclic_defect_rank"]] != [54, 9, 2]:
            raise AssertionError("rank guard failed")
        if checks["normalized_witness_value"] != "1":
            raise AssertionError("normalized witness guard failed")
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(_report(value))
    if args.check:
        verify(json.loads(OUTPUT.read_text()))
    print(f"{value['result_id']}: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
