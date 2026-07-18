#!/usr/bin/env python3
"""Reducibility obstruction to the unmodified Nariai parent comparison.

Metric conformal reducibilities are infinitesimal Cartan automorphisms.  On a
curved conformal geometry they are not, in general, parallel sections of the
normal adjoint tractor connection.  Unit Nariai makes this distinction exact:
six independent product Killing fields lie in the metric ghost kernel, while
the common kernel of the normal-tractor curvature has dimension one.  Hence
the corrected Yang--Mills parent, and its contractible incidence cylinder,
cannot be quasi-isomorphic to the metric Bach complex without modifying the
ghost prolongation or adding noncontractible reducibility rows.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    ROOT,
    _sha256,
    _sparse,
)
from d_quotient_classical.causal_transfer.nariai_yang_mills_middle_compression import (
    fixture as middle_fixture,
)


HERE = ROOT / "d_quotient_classical/causal_transfer"
METRIC_COMPLEX = ROOT / "d_quotient_classical/certificates/NARIAI_METRIC_BACH_CYCLIC_BV_COMPLEX_V1.json"
CYLINDER = ROOT / "d_quotient_classical/certificates/NARIAI_CURVATURE_INCIDENCE_CYCLIC_MAPPING_CYLINDER_V1.json"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_PARENT_REDUCIBILITY_MISMATCH_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-parent-reducibility-mismatch.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-parent-reducibility-mismatch-v1.schema.json"
VERIFIER = HERE / "verify_nariai_parent_reducibility_mismatch.py"
TESTS = HERE / "tests/test_nariai_parent_reducibility_mismatch.py"
MIDDLE_PRODUCER = HERE / "nariai_yang_mills_middle_compression.py"
METRIC_PRODUCER = HERE / "nariai_metric_bach_cyclic_bv_complex.py"
CYLINDER_PRODUCER = HERE / "nariai_curvature_incidence_cyclic_mapping_cylinder.py"


def _matrix_digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode()
    ).hexdigest()


def _lie_derivative_metric(
    metric: sp.Matrix,
    coordinates: tuple[sp.Symbol, ...],
    vector: sp.Matrix,
) -> sp.Matrix:
    dimension = len(coordinates)
    output = sp.zeros(dimension)
    for a in range(dimension):
        for b in range(dimension):
            output[a, b] = sp.simplify(
                sum(
                    vector[c] * sp.diff(metric[a, b], coordinates[c])
                    + metric[c, b] * sp.diff(vector[c], coordinates[a])
                    + metric[a, c] * sp.diff(vector[c], coordinates[b])
                    for c in range(dimension)
                )
            )
    return output


def killing_fixture() -> dict[str, object]:
    t, chi, theta, phi = sp.symbols("t chi theta phi", real=True)
    coordinates = (t, chi, theta, phi)
    metric = sp.diag(-1, sp.cosh(t) ** 2, 1, sp.sin(theta) ** 2)
    vectors = (
        ("dS_rotation", sp.Matrix([0, 1, 0, 0])),
        (
            "dS_boost_cos",
            sp.Matrix([sp.cos(chi), -sp.tanh(t) * sp.sin(chi), 0, 0]),
        ),
        (
            "dS_boost_sin",
            sp.Matrix([sp.sin(chi), sp.tanh(t) * sp.cos(chi), 0, 0]),
        ),
        ("S2_rotation", sp.Matrix([0, 0, 0, 1])),
        (
            "S2_rotation_cos",
            sp.Matrix([0, 0, sp.cos(phi), -sp.cot(theta) * sp.sin(phi)]),
        ),
        (
            "S2_rotation_sin",
            sp.Matrix([0, 0, sp.sin(phi), sp.cot(theta) * sp.cos(phi)]),
        ),
    )
    defects = {
        name: _lie_derivative_metric(metric, coordinates, vector)
        for name, vector in vectors
    }
    if any(defect != sp.zeros(4) for defect in defects.values()):
        raise AssertionError("declared Nariai product generator is not Killing")
    basepoint = {t: 0, chi: 0, theta: sp.pi / 2, phi: 0}
    jets = []
    for _, vector in vectors:
        entries = [entry.subs(basepoint) for entry in vector]
        entries.extend(
            sp.diff(vector[component], coordinate).subs(basepoint)
            for component in range(4)
            for coordinate in coordinates
        )
        jets.append(sp.Matrix(entries))
    jet_matrix = sp.Matrix.hstack(*jets)
    if jet_matrix.rank() != 6:
        raise AssertionError("Nariai Killing generators lost independence")
    return {
        "coordinates": [str(value) for value in coordinates],
        "metric_diagonal": [str(metric[index, index]) for index in range(4)],
        "generators": [
            {"name": name, "components": [str(entry) for entry in vector]}
            for name, vector in vectors
        ],
        "Lie_derivative_defect_entries": sum(
            entry != 0 for defect in defects.values() for entry in defect
        ),
        "basepoint": ["0", "0", "pi/2", "0"],
        "value_and_first_partial_jet_rank": jet_matrix.rank(),
        "jet_sha256": _matrix_digest(jet_matrix),
    }


def build() -> dict[str, object]:
    metric = json.loads(METRIC_COMPLEX.read_text())
    cylinder = json.loads(CYLINDER.read_text())
    if metric["flags"]["NARIAI_METRIC_BACH_ENDPOINT_CHAIN_COMPLEX"] is not True:
        raise ValueError("metric Bach complex unavailable")
    if cylinder["flags"]["MAPPING_CYLINDER_SDR"] is not True:
        raise ValueError("parent-relative cylinder SDR unavailable")
    middle = middle_fixture()
    curvature = middle["normal_tractor_square"][()]
    kernel_vectors = curvature.nullspace()
    kernel = sp.Matrix.hstack(*kernel_vectors) if kernel_vectors else sp.zeros(15, 0)
    if curvature.shape != (90, 15) or curvature.rank() != 14:
        raise AssertionError("normal-tractor curvature kernel drifted")
    if kernel.shape != (15, 1) or curvature * kernel != sp.zeros(90, 1):
        raise AssertionError("normal-tractor common-kernel witness failed")
    killing = killing_fixture()
    missing_lower_bound = killing["value_and_first_partial_jet_rank"] - kernel.cols
    if missing_lower_bound != 5:
        raise AssertionError("reducibility mismatch lower bound drifted")

    sources = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (
            Path(__file__).resolve(),
            VERIFIER,
            TESTS,
            SCHEMA,
            MIDDLE_PRODUCER,
            METRIC_PRODUCER,
            CYLINDER_PRODUCER,
        )
    }
    return {
        "schema": "pure-weyl-nariai-parent-reducibility-mismatch-v1",
        "result_id": "NARIAI_PARENT_REDUCIBILITY_MISMATCH_V1",
        "result_state": "CURRENT_NORMAL_TRACTOR_PARENT_NOT_QUASI_ISOMORPHIC_TO_METRIC_COMPLEX",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "GLOBAL-SMOOTH"],
        "dependency_refs": {
            "metric_bach_complex": {
                "artifact_id": metric["result_id"],
                "path": str(METRIC_COMPLEX.relative_to(ROOT)),
                "sha256": _sha256(METRIC_COMPLEX),
            },
            "incidence_cylinder": {
                "artifact_id": cylinder["result_id"],
                "path": str(CYLINDER.relative_to(ROOT)),
                "sha256": _sha256(CYLINDER),
            },
        },
        "metric_reducibilities": {
            **killing,
            "global_Killing_dimension_lower_bound": 6,
            "metric_H_minus_1_dimension_lower_bound": 6,
        },
        "parent_reducibilities": {
            "normal_tractor_curvature_shape": list(curvature.shape),
            "normal_tractor_curvature_rank": curvature.rank(),
            "common_curvature_kernel_dimension": kernel.cols,
            "common_curvature_kernel": _sparse(kernel),
            "common_curvature_kernel_sha256": _matrix_digest(kernel),
            "parallel_section_evaluation_is_injective": True,
            "parent_H_minus_1_dimension_upper_bound": kernel.cols,
            "reason": "a normal-tractor parallel section is determined by its value, and its value is annihilated by every curvature block",
        },
        "obstruction": {
            "metric_H_minus_1_lower_bound": 6,
            "parent_H_minus_1_upper_bound": 1,
            "missing_reducibility_dimension_lower_bound": missing_lower_bound,
            "incidence_cylinder_H_minus_1_equals_parent": True,
            "direct_parent_metric_quasi_isomorphism_possible": False,
            "contractible_equation_identity_rows_sufficient": False,
            "normalized_witness": "6-1=5",
            "interpretation": "metric conformal reducibilities are infinitesimal Cartan automorphisms; the unmodified normal-tractor differential tests parallel adjoint tractors instead",
        },
        "required_repair": {
            "next_object": "curvature-corrected infinitesimal-automorphism prolongation",
            "schematic_equation": "nabla^D s + i_{p(s)} Omega = 0",
            "minimum_new_noncontractible_reducibility_directions": missing_lower_bound,
            "equation_only_contractible_extension_rejected": True,
        },
        "flags": {
            "NARIAI_PARENT_REDUCIBILITY_MISMATCH_V1": True,
            "CURRENT_NORMAL_TRACTOR_PARENT_METRIC_QUASI_ISOMORPHISM": False,
            "CURRENT_RELATIVE_EQUATION_CONE_ACYCLIC": False,
            "CURVATURE_CORRECTED_AUTOMORPHISM_PROLONGATION_REQUIRED": True,
            "NARIAI_GREEN_HOMOTOPY": False,
            "OPEN_BACKGROUND_CLASS": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "C_G2_NARIAI_CURVATURE_CORRECTED_AUTOMORPHISM_PROLONGATION",
        "claim_boundary": (
            "This theorem compares ghost-degree cohomology and proves that the current corrected Yang-Mills normal-tractor parent, together with its contractible curvature-incidence mapping cylinder, cannot be quasi-isomorphic to the exact metric Bach complex on unit Nariai. Six explicit global product Killing fields give metric ghost cohomology dimension at least six, while the stacked normal-tractor curvature has rank fourteen and bounds parallel adjoint-tractor ghosts by one dimension. Hence an equation/identity-only contractible completion cannot repair the comparison; at least five noncontractible reducibility directions, or equivalently the curvature-corrected infinitesimal-automorphism prolongation, are required. This does not rule out that corrected prolongation, a different parent complex, an independently constructed metric Green homotopy, an open-background theorem, nonlinear interactions, or a quantum theory."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_parent_reducibility_mismatch.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_parent_reducibility_mismatch.py",
                "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_nariai_parent_reducibility_mismatch",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-parent-reducibility-mismatch-v1.schema.json -d d_quotient_classical/certificates/NARIAI_PARENT_REDUCIBILITY_MISMATCH_V1.json",
            ],
        },
    }


def render(value: dict[str, object]) -> str:
    obstruction = value["obstruction"]
    return rf"""# Nariai parent reducibility mismatch

The exact metric Bach complex and the current normal-adjoint-tractor parent
do not have the same ghost cohomology on unit Nariai.

The six displayed product isometries are independent global Killing fields,
so

\[
\dim H^{{-1}}_{{\rm metric}}\geq 6.
\]

A parallel adjoint tractor must lie in the common kernel of every normal
tractor curvature block.  Their stacked (90\times15) matrix has rank
`{value['parent_reducibilities']['normal_tractor_curvature_rank']}`, hence

\[
\dim H^{{-1}}_{{\rm parent}}\leq 1.
\]

The certified incidence cylinder retracts to that parent and cannot change
this cohomology.  Consequently its direct cone with the metric complex cannot
be acyclic; adding only contractible equation and identity rows cannot repair
the mismatch.  The deficit is at least

\[
{obstruction['metric_H_minus_1_lower_bound']}
-{obstruction['parent_H_minus_1_upper_bound']}
={obstruction['missing_reducibility_dimension_lower_bound']}.
\]

The correct next object is the infinitesimal-automorphism prolongation,
schematically (\nabla^D s+i_{{p(s)}}\Omega=0), rather than the parallel
adjoint-tractor equation (\nabla^D s=0).

## Boundary

{value['claim_boundary']}
"""


def verify(value: dict[str, object]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("reducibility mismatch certificate drifted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.guards:
        flags = value["flags"]
        if flags["NARIAI_PARENT_REDUCIBILITY_MISMATCH_V1"] is not True:
            raise AssertionError("reducibility mismatch guard failed")
        if flags["CURRENT_RELATIVE_EQUATION_CONE_ACYCLIC"] is not False:
            raise AssertionError("relative cone was overpromoted")
        if flags["NARIAI_GREEN_HOMOTOPY"] is not False:
            raise AssertionError("Green homotopy was overpromoted")
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(render(value))
    if args.check:
        verify(json.loads(OUTPUT.read_text()))
    print(f"{value['result_id']}: PASS")


if __name__ == "__main__":
    main()
