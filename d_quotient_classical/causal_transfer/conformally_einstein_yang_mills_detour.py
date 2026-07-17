#!/usr/bin/env python3
"""C-G2: curved Yang--Mills detour correction on the Nariai control."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/causal_transfer"
OBSTRUCTION = ROOT / "d_quotient_classical/certificates/CONFORMALLY_EINSTEIN_TRACTOR_CURVATURE_OBSTRUCTION_V1.json"
OUTPUT = ROOT / "d_quotient_classical/certificates/CONFORMALLY_EINSTEIN_YANG_MILLS_DETOUR_CORRECTION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/conformally-einstein-yang-mills-detour-correction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/conformally-einstein-yang-mills-detour-correction-v1.schema.json"
VERIFIER = HERE / "verify_conformally_einstein_yang_mills_detour.py"
TESTS = HERE / "tests/test_conformally_einstein_yang_mills_detour.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix(value: sp.Matrix) -> list[list[str]]:
    return [[str(entry) for entry in row] for row in value.tolist()]


def _fixture() -> dict[str, object]:
    """Exact constant-connection replay of both universal detour identities."""
    a = [sp.Matrix([[0, 1], [0, 0]]), sp.Matrix([[0, 0], [1, 0]])]
    zero = sp.zeros(2)
    curvature = [[a[i] * a[j] - a[j] * a[i] for j in range(2)] for i in range(2)]
    current = [
        -sum((a[i] * curvature[i][b] - curvature[i][b] * a[i] for i in range(2)), zero)
        for b in range(2)
    ]
    laplacian = sum((matrix * matrix for matrix in a), zero)

    corrected_blocks: list[list[sp.Matrix]] = []
    naive_blocks: list[list[sp.Matrix]] = []
    for b in range(2):
        corrected_row = []
        naive_row = []
        for source in range(2):
            base = (-laplacian if source == b else zero) + a[source] * a[b]
            naive_row.append(base)
            corrected_row.append(base - curvature[b][source])
        corrected_blocks.append(corrected_row)
        naive_blocks.append(naive_row)

    def block_matrix(blocks: list[list[sp.Matrix]]) -> sp.Matrix:
        return sp.Matrix.vstack(*(sp.Matrix.hstack(*row) for row in blocks))

    d = sp.Matrix.vstack(*a)
    delta = sp.Matrix.hstack(*(-matrix for matrix in a))
    epsilon_current = sp.Matrix.vstack(*current)
    minus_iota_current = sp.Matrix.hstack(*(-matrix for matrix in current))
    middle = block_matrix(corrected_blocks)
    naive_middle = block_matrix(naive_blocks)
    defects = {
        "M_d_minus_epsilon_deltaF": middle * d - epsilon_current,
        "delta_M_plus_iota_deltaF": delta * middle - minus_iota_current,
        "naive_M_d_minus_epsilon_deltaF": naive_middle * d - epsilon_current,
        "delta_naive_M_plus_iota_deltaF": delta * naive_middle - minus_iota_current,
    }
    if defects["M_d_minus_epsilon_deltaF"] != sp.zeros(4, 2):
        raise AssertionError("left Yang--Mills detour identity failed")
    if defects["delta_M_plus_iota_deltaF"] != sp.zeros(2, 4):
        raise AssertionError("right Yang--Mills detour identity failed")
    if defects["naive_M_d_minus_epsilon_deltaF"].rank() != 2:
        raise AssertionError("curvature correction necessity guard failed")
    if defects["delta_naive_M_plus_iota_deltaF"].rank() != 2:
        raise AssertionError("dual curvature correction necessity guard failed")
    return {
        "connection": a,
        "curvature": curvature,
        "current": current,
        "d": d,
        "delta": delta,
        "middle": middle,
        "naive_middle": naive_middle,
        "defects": defects,
    }


def build() -> dict:
    dependency = json.loads(OBSTRUCTION.read_text())
    if dependency["exact_checks"]["target_is_Bach_flat"] is not True:
        raise ValueError("Nariai Bach-flat control unavailable")
    fixture = _fixture()
    sources = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "pure-weyl-conformally-einstein-yang-mills-detour-correction-v1",
        "result_id": "CONFORMALLY_EINSTEIN_YANG_MILLS_DETOUR_CORRECTION_V1",
        "result_state": "CURVED_PARENT_DETOUR_CORRECTION_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_ref": {
            "artifact_id": dependency["result_id"],
            "path": str(OBSTRUCTION.relative_to(ROOT)),
            "sha256": _sha256(OBSTRUCTION),
        },
        "primary_source": {
            "title": "Yang-Mills detour complexes and conformal geometry",
            "authors": "A. Rod Gover, Petr Somberg, Vladimir Soucek",
            "arxiv": "math/0606401",
            "url": "https://arxiv.org/abs/math/0606401",
            "formula_scope": "Lemma 3.1 and the formally self-adjoint Yang-Mills detour complex",
        },
        "universal_parent": {
            "sequence": "Omega^0(V) --d^D--> Omega^1(V) --M^D--> Omega^1(V) --delta^D--> Omega^0(V)",
            "middle": "(M^D Psi)_b=-D^a D_a Psi_b+D^a D_b Psi_a-F_b^a Psi_a",
            "left_composition": "M^D d^D=epsilon(delta^D F)",
            "right_composition": "delta^D M^D=-iota(delta^D F)",
            "complex_condition": "delta^D F=0",
            "formal_self_adjointness": "if D preserves the fibre metric, the Yang-Mills detour complex is formally self-adjoint",
        },
        "nariai_application": {
            "normal_tractor_current": "in conformal dimension four the normal-tractor Yang-Mills current is the Bach tensor in the tractor slot",
            "bach_tensor": "0",
            "parent_complex": True,
            "curvature_action_nonzero": True,
            "flat_middle_is_invalid": True,
            "corrected_middle_is_valid": True,
        },
        "exact_matrix_fixture": {
            "connection_matrices": [_matrix(matrix) for matrix in fixture["connection"]],
            "curvature_matrices": [[_matrix(matrix) for matrix in row] for row in fixture["curvature"]],
            "yang_mills_current": [_matrix(matrix) for matrix in fixture["current"]],
            "d_matrix": _matrix(fixture["d"]),
            "delta_matrix": _matrix(fixture["delta"]),
            "corrected_middle_matrix": _matrix(fixture["middle"]),
            "corrected_left_defect_rank": fixture["defects"]["M_d_minus_epsilon_deltaF"].rank(),
            "corrected_right_defect_rank": fixture["defects"]["delta_M_plus_iota_deltaF"].rank(),
            "naive_left_defect_rank": fixture["defects"]["naive_M_d_minus_epsilon_deltaF"].rank(),
            "naive_right_defect_rank": fixture["defects"]["delta_naive_M_plus_iota_deltaF"].rank(),
        },
        "exact_checks": {
            "curvature_correction_sign_replayed": True,
            "left_composition_identity_exact": True,
            "right_composition_identity_exact": True,
            "naive_flat_middle_rejected": True,
            "Nariai_normal_tractor_is_Yang_Mills": True,
            "Nariai_curved_parent_complex_exists": True,
        },
        "flags": {
            "CONFORMALLY_EINSTEIN_YANG_MILLS_DETOUR_CORRECTION_V1": True,
            "NARIAI_CURVED_PARENT_DETOUR_COMPLEX": True,
            "NARIAI_CURVED_BGG_HPL_COMPRESSION": False,
            "NARIAI_PARENT_GREEN_HOMOTOPY": False,
            "NARIAI_METRIC_GREEN_HOMOTOPY": False,
            "G3_BACH_FLAT_OPEN_CLASS": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "C_G2_NARIAI_CURVED_BGG_HPL_COMPRESSION",
        "claim_boundary": (
            "This certificate identifies and sign-checks the universal curvature correction required after the zero-order flat-tractor conjugation fails. On the Bach-flat Nariai control, the normal tractor connection is Yang-Mills, so the corrected parent detour sequence is a formally self-adjoint differential complex. This is not yet the differential BGG/HPL compression to the metric Bach complex, a retarded or advanced Green construction, a support theorem, an open Bach-flat family, or a quantum statement. The exact matrix fixture independently rejects the naive flat middle but is a universal sign-and-composition replay, not a component expansion of the Nariai tractor bundle."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/conformally_einstein_yang_mills_detour.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_conformally_einstein_yang_mills_detour.py",
                "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_conformally_einstein_yang_mills_detour",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/conformally-einstein-yang-mills-detour-correction-v1.schema.json -d d_quotient_classical/certificates/CONFORMALLY_EINSTEIN_YANG_MILLS_DETOUR_CORRECTION_V1.json",
            ],
        },
    }


def _report(value: dict) -> str:
    f = value["exact_matrix_fixture"]
    return rf"""# Conformally Einstein Yang--Mills detour correction

## Result

The Nariai Weyl curvature obstructs the flat, zero-order tractor conjugation,
but it does not obstruct the curved parent detour complex.  The required
middle operator is

\[
(M^D\Psi)_b=-D^aD_a\Psi_b+D^aD_b\Psi_a-F_b{{}}^a\Psi_a.
\]

Its universal compositions are

\[
M^Dd^D=\varepsilon(\delta^DF),\qquad
\delta^DM^D=-\iota(\delta^DF).
\]

In four conformal dimensions the normal-tractor Yang--Mills current is the
Bach tensor in the relevant tractor slot.  Unit Nariai is Einstein and
Bach-flat, so the corrected sequence is a formally self-adjoint complex.

## Exact sign replay

For an independent rational noncommuting constant-connection fixture, the
corrected left and right defect ranks are respectively
`{f['corrected_left_defect_rank']}` and `{f['corrected_right_defect_rank']}`.
Dropping the curvature action raises both ranks to
`{f['naive_left_defect_rank']}` and `{f['naive_right_defect_rank']}`.  Thus
the sign and placement of \(-F\!\cdot\) are detected rather than ceremonial.

## Remaining gate

The next task is the actual curved differential BGG/HPL compression from this
parent to the Nariai metric Bach complex.  No Green or causal claim is made
here.
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
        fixture = value["exact_matrix_fixture"]
        if [fixture["corrected_left_defect_rank"], fixture["corrected_right_defect_rank"]] != [0, 0]:
            raise AssertionError("corrected detour guard failed")
        if [fixture["naive_left_defect_rank"], fixture["naive_right_defect_rank"]] != [2, 2]:
            raise AssertionError("flat-middle rejection guard failed")
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(_report(value))
    if args.check:
        verify(json.loads(OUTPUT.read_text()))
    print(f"{value['result_id']}: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
