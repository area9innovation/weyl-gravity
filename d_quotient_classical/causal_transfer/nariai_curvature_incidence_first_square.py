#!/usr/bin/env python3
"""Certify the canonical curvature-incidence form of the first Nariai BGG square."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_kostant_compression import (
    _adjoint_basis,
    _coordinate_map,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    NariaiBackground,
    ROOT,
    _sha256,
    _sparse,
    _sparse_table,
    candidate,
)


HERE = ROOT / "d_quotient_classical/causal_transfer"
STRICT = ROOT / "d_quotient_classical/certificates/NARIAI_FIRST_BGG_ZEROTH_ORDER_STRICTIFICATION_OBSTRUCTION_V1.json"
POINTWISE = ROOT / "d_quotient_classical/certificates/NARIAI_POINTWISE_BGG_CURVATURE_COMPRESSION_OBSTRUCTION_V1.json"
KOSTANT_CODE = ROOT / "covariant_completion/curved_operator/adjoint_tractor_kostant_compression.py"
STRICT_PRODUCER = HERE / "nariai_first_differential_bgg_correction.py"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_CURVATURE_INCIDENCE_FIRST_SQUARE_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-curvature-incidence-first-square.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-curvature-incidence-first-square-v1.schema.json"
VERIFIER = HERE / "verify_nariai_curvature_incidence_first_square.py"
TESTS = HERE / "tests/test_nariai_curvature_incidence_first_square.py"


def _nariai_weyl(a: int, b: int, c: int, d: int) -> sp.Expr:
    """All-lowered Weyl tensor of unit Nariai in the certified frame."""

    metric = NariaiBackground.metric
    same_factor = all(index < 2 for index in (a, b, c, d)) or all(
        index >= 2 for index in (a, b, c, d)
    )
    riemann = (
        metric[a, c] * metric[b, d] - metric[a, d] * metric[b, c]
        if same_factor
        else sp.Integer(0)
    )
    return sp.simplify(
        riemann
        - sp.Rational(1, 2)
        * (
            metric[a, c] * metric[d, b]
            - metric[a, d] * metric[c, b]
            - metric[b, c] * metric[d, a]
            + metric[b, d] * metric[c, a]
        )
        + sp.Rational(2, 3)
        * (metric[a, c] * metric[d, b] - metric[a, d] * metric[c, b])
    )


def curvature_incidence() -> dict[str, object]:
    """Return ``Omega_ab`` coordinates and ``(I_Omega xi)_a=Omega_ab xi^b``."""

    names, basis = _adjoint_basis()
    embedded, left_inverse = _coordinate_map(basis)
    metric = NariaiBackground.metric

    curvature: dict[tuple[int, int], sp.Matrix] = {}
    adjoint_blocks: list[sp.Matrix] = []
    incidence = sp.zeros(60, 4)
    for left in range(4):
        for right in range(left + 1, 4):
            standard = sp.zeros(6)
            for raised in range(4):
                for lowered in range(4):
                    standard[1 + raised, 1 + lowered] = sum(
                        metric[raised, contracted]
                        * _nariai_weyl(left, right, contracted, lowered)
                        for contracted in range(4)
                    )
            coordinates = left_inverse * standard.reshape(36, 1)
            if embedded * coordinates != standard.reshape(36, 1):
                raise AssertionError("normal tractor curvature escaped so(4,2)")
            curvature[(left, right)] = coordinates
            adjoint_blocks.append(
                sp.Matrix.hstack(
                    *(
                        left_inverse
                        * (standard * generator - generator * standard).reshape(36, 1)
                        for generator in basis
                    )
                )
            )
            incidence[15 * left : 15 * (left + 1), right] = coordinates
            incidence[15 * right : 15 * (right + 1), left] = -coordinates

    if tuple(names[4:10]) != ("M01", "M02", "M03", "M12", "M13", "M23"):
        raise AssertionError("Lorentz-generator support order drifted")
    return {
        "basis_names": names,
        "curvature": curvature,
        "adjoint_square": sp.Matrix.vstack(*adjoint_blocks),
        "incidence": incidence,
    }


def fixture() -> dict[str, object]:
    strict = candidate()
    geometry = curvature_incidence()
    residual = strict["corrected_defect"]
    if set(residual) != {()}:
        raise AssertionError("corrected first-square residue was not algebraic")
    incidence = geometry["incidence"]
    relative_defect = residual[()] - incidence
    wrong_sign_defect = residual[()] + incidence
    square = strict["normal_tractor_square"]
    if set(square) != {()}:
        raise AssertionError("normal tractor square was not algebraic")
    square_defect = square[()] - geometry["adjoint_square"]
    support = sorted({row % 15 for row, _ in residual[()].todok()})
    return {
        **geometry,
        "residual": residual,
        "relative_defect": relative_defect,
        "wrong_sign_defect": wrong_sign_defect,
        "square_defect": square_defect,
        "support": support,
    }


def build() -> dict[str, object]:
    strict = json.loads(STRICT.read_text())
    pointwise = json.loads(POINTWISE.read_text())
    if strict["flags"]["ZEROTH_ORDER_STRICTIFICATION_EXISTS"] is not False:
        raise ValueError("strictification dependency was overpromoted")
    if pointwise["flags"]["DERIVATIVE_BGG_CORRECTIONS_REQUIRED"] is not True:
        raise ValueError("pointwise curvature dependency is unavailable")
    value = fixture()
    incidence = value["incidence"]
    residual = value["residual"][()]
    relative = value["relative_defect"]
    wrong = value["wrong_sign_defect"]
    square_defect = value["square_defect"]
    sources = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (
            Path(__file__).resolve(),
            VERIFIER,
            TESTS,
            SCHEMA,
            KOSTANT_CODE,
            STRICT_PRODUCER,
        )
    }
    return {
        "schema": "pure-weyl-nariai-curvature-incidence-first-square-v1",
        "result_id": "NARIAI_CURVATURE_INCIDENCE_FIRST_SQUARE_V1",
        "result_state": "CANONICAL_CURVATURE_INCIDENCE_IDENTITY_EXACT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "strictification_screen": {
                "artifact_id": strict["result_id"],
                "path": str(STRICT.relative_to(ROOT)),
                "sha256": _sha256(STRICT),
            },
            "pointwise_curvature_gate": {
                "artifact_id": pointwise["result_id"],
                "path": str(POINTWISE.relative_to(ROOT)),
                "sha256": _sha256(POINTWISE),
            },
        },
        "conventions": {
            "background": "unit Nariai dS2 x S2 in the certified orthonormal frame",
            "adjoint_basis": list(value["basis_names"]),
            "curvature_coordinates": "Omega_ab is the normal standard-tractor curvature represented in the ordered adjoint basis",
            "incidence_map": "(I_Omega xi)_a=Omega_ab xi^b",
            "first_square": "d^D(L0+DeltaL0)-(L1+DeltaL1)K=I_Omega",
            "sign_anchor": "the output one-form index is the first curvature index; Omega_ab=-Omega_ba",
        },
        "exact_data": {
            "normal_tractor_curvature_coordinates": _sparse_table(value["curvature"]),
            "curvature_incidence": _sparse(incidence),
            "reconstructed_adjoint_curvature_square": _sparse(value["adjoint_square"]),
            "normal_tractor_square_defect": _sparse(square_defect),
            "corrected_first_square_residual": _sparse_table(value["residual"]),
            "relative_chain_defect": _sparse(relative),
            "wrong_sign_defect": _sparse(wrong),
        },
        "exact_checks": {
            "incidence_shape": [incidence.rows, incidence.cols],
            "incidence_rank": incidence.rank(),
            "incidence_nonzero_entries": sum(entry != 0 for entry in incidence),
            "residual_rank": residual.rank(),
            "residual_nonzero_entries": sum(entry != 0 for entry in residual),
            "residual_equals_incidence": residual == incidence,
            "adjoint_curvature_equals_normal_tractor_square": square_defect == sp.zeros(90, 15),
            "normal_tractor_square_defect_rank": square_defect.rank(),
            "normal_tractor_square_defect_nonzero_entries": sum(entry != 0 for entry in square_defect),
            "relative_defect_rank": relative.rank(),
            "relative_defect_nonzero_entries": sum(entry != 0 for entry in relative),
            "wrong_sign_defect_rank": wrong.rank(),
            "wrong_sign_defect_nonzero_entries": sum(entry != 0 for entry in wrong),
            "adjoint_support_indices": value["support"],
            "adjoint_support_names": [value["basis_names"][index] for index in value["support"]],
            "normalized_coefficient": "(3/2)*I_Omega[4,1]",
            "normalized_coefficient_value": str(sp.Rational(3, 2) * incidence[4, 1]),
        },
        "theorem": {
            "statement": "After the unique normalized zeroth-order correction of the first differential BGG lift, the complete remaining Nariai square defect is exactly the canonical curvature-incidence map I_Omega, coefficient by coefficient.",
            "interpretation": "The twelve-term residue is not unexplained cone cohomology and is not evidence for a missing algebraic endpoint potential. It is the curved-connection Lie-derivative incidence term. A strict square is therefore the wrong curved target; the next construction must retain this term in a homotopy-coherent or mapping-cone square and add its cyclic dual rows.",
            "strict_square_still_false": True,
        },
        "flags": {
            "NARIAI_CURVATURE_INCIDENCE_FIRST_SQUARE_V1": True,
            "CURVATURE_INCIDENCE_IDENTITY_EXACT": True,
            "RESIDUAL_IS_UNEXPLAINED_OBSTRUCTION": False,
            "STRICT_FIRST_BGG_SQUARE": False,
            "CYCLIC_CURVATURE_INCIDENCE_MAPPING_CONE": False,
            "NARIAI_CURVED_BGG_HPL_COMPRESSION": False,
            "NARIAI_GREEN_HOMOTOPY": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "C_G2_NARIAI_CYCLIC_CURVATURE_INCIDENCE_MAPPING_CONE",
        "claim_boundary": (
            "This exact coefficient calculation identifies the complete rank-four, twelve-entry algebraic residue of the corrected first Nariai BGG square with the canonical contraction of the normal tractor curvature, (I_Omega xi)_a=Omega_ab xi^b. The identity is local, tensorial and checked in the certified homogeneous Nariai frame; homogeneity globalizes that natural operator identity on unit Nariai. It proves the correct homotopy-coherent first-square incidence and reclassifies the previous residual as geometric curvature rather than an unexplained algebraic obstruction. It does not construct the cyclic mapping cone, the dual equation and identity incidence rows, the compressed Bach middle, any support or Green operator, an open background class, a nonlinear theorem, or a quantum result. The strict square remains false on non-flat Nariai curvature."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_curvature_incidence_first_square.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_curvature_incidence_first_square.py",
                "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_nariai_curvature_incidence_first_square",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-curvature-incidence-first-square-v1.schema.json -d d_quotient_classical/certificates/NARIAI_CURVATURE_INCIDENCE_FIRST_SQUARE_V1.json",
            ],
        },
    }


def render(value: dict[str, object]) -> str:
    checks = value["exact_checks"]
    return rf"""# Nariai curvature-incidence first-square identity

The repaired first differential BGG square is not strict on unit Nariai.
Its complete residue is instead the canonical curvature insertion

\[
 d^D(L_0+\Delta L_0)-(L_1+\Delta L_1)K=I_\Omega,
 \qquad (I_\Omega\xi)_a=\Omega_{{ab}}\xi^b .
\]

The independently reconstructed incidence matrix has shape
`{checks['incidence_shape']}`, rank `{checks['incidence_rank']}`, and
`{checks['incidence_nonzero_entries']}` nonzero entries.  It agrees with the
previously certified residue coefficient by coefficient.  The difference has
rank `{checks['relative_defect_rank']}` and
`{checks['relative_defect_nonzero_entries']}` entries.  Reversing the incidence
sign leaves rank `{checks['wrong_sign_defect_rank']}` with
`{checks['wrong_sign_defect_nonzero_entries']}` entries, so the sign is fixed.

All nonzero coefficients lie in the Lorentz-generator support
`{checks['adjoint_support_names']}`.  The normalization anchor is
\((3/2)(I_\Omega)_{{4,1}}={checks['normalized_coefficient_value']}\).

## Meaning

The former twelve-term residue is the expected curved-connection term, not an
unclassified failure.  A strict BGG square is the wrong target on Nariai.  The
next gate is to retain this incidence in a cyclic mapping cone, including the
dual equation/identity rows, and only then recompress the Yang--Mills middle.

## Boundary

{value['claim_boundary']}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if args.guards:
        checks = value["exact_checks"]
        if checks["residual_equals_incidence"] is not True:
            raise AssertionError("curvature-incidence identity failed")
        if [checks["incidence_rank"], checks["incidence_nonzero_entries"]] != [4, 12]:
            raise AssertionError("curvature-incidence rank/support drifted")
        if checks["relative_defect_nonzero_entries"] != 0:
            raise AssertionError("relative square did not close")
        if checks["normal_tractor_square_defect_nonzero_entries"] != 0:
            raise AssertionError("incidence curvature differs from the normal tractor square")
        if checks["wrong_sign_defect_nonzero_entries"] != 12:
            raise AssertionError("incidence-sign mutation guard failed")
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    report = render(value)
    if args.check:
        if OUTPUT.read_text() != encoded or REPORT.read_text() != report:
            raise SystemExit("generated Nariai curvature-incidence artifacts drifted")
    else:
        OUTPUT.write_text(encoded)
        REPORT.write_text(report)


if __name__ == "__main__":
    main()
