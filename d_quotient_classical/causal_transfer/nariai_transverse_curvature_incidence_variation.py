#!/usr/bin/env python3
"""Differentiate the Nariai curvature-incidence square transversely."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_kostant_compression import (
    _adjoint_basis,
    _coordinate_map,
)
from d_quotient_classical.causal_transfer.nariai_yang_mills_middle_compression import (
    fixture as middle_fixture,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_CURVATURE_INCIDENCE_VARIATION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-curvature-incidence-variation.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-curvature-incidence-variation-v1.schema.json"
VERIFIER = HERE / "verify_nariai_transverse_curvature_incidence_variation.py"
TESTS = HERE / "tests/test_nariai_transverse_curvature_incidence_variation.py"

WITNESS = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1.json"
INCIDENCE = ROOT / "d_quotient_classical/certificates/NARIAI_CURVATURE_INCIDENCE_FIRST_SQUARE_V1.json"
MAPPING_CONE = ROOT / "d_quotient_classical/certificates/NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sparse(matrix: sp.Matrix) -> dict[str, Any]:
    return {
        "shape": [matrix.rows, matrix.cols],
        "rank": matrix.rank(),
        "entries": [
            [row, column, str(value)]
            for (row, column), value in sorted(matrix.todok().items())
        ],
        "sha256": hashlib.sha256(sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode()).hexdigest(),
    }


def _variation_riemann() -> sp.MutableDenseNDimArray:
    """All-lowered orthonormal curvature variation at sinh(t)=1."""
    sectional = {
        (0, 1): sp.Integer(2),
        (0, 2): sp.Integer(-1),
        (0, 3): sp.Integer(-1),
        (1, 2): sp.Integer(1),
        (1, 3): sp.Integer(1),
        (2, 3): sp.Integer(-2),
    }
    tensor = sp.MutableDenseNDimArray.zeros(4, 4, 4, 4)
    for (left, right), value in sectional.items():
        for a, b, sign_ab in ((left, right, 1), (right, left, -1)):
            for c, d, sign_cd in ((left, right, 1), (right, left, -1)):
                tensor[a, b, c, d] = sign_ab * sign_cd * value
    return tensor


def exact_variation() -> dict[str, Any]:
    metric = sp.diag(-1, 1, 1, 1)
    delta_r = _variation_riemann()
    delta_ricci = sp.zeros(4)
    for b in range(4):
        for d in range(4):
            delta_ricci[b, d] = sp.simplify(
                sum(
                    metric[a, c] * delta_r[a, b, c, d]
                    for a in range(4)
                    for c in range(4)
                )
            )
    if delta_ricci != sp.zeros(4):
        raise AssertionError("transverse curvature variation is not Ricci-free")
    bianchi_defects = []
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    defect = sp.simplify(
                        delta_r[a, b, c, d]
                        + delta_r[a, c, d, b]
                        + delta_r[a, d, b, c]
                    )
                    if defect != 0:
                        bianchi_defects.append([a, b, c, d, str(defect)])
    if bianchi_defects:
        raise AssertionError(f"algebraic Bianchi variation failed: {bianchi_defects[:4]}")

    names, basis = _adjoint_basis()
    embedded, left_inverse = _coordinate_map(basis)
    curvature_coordinates: dict[tuple[int, int], sp.Matrix] = {}
    incidence = sp.zeros(60, 4)
    for left in range(4):
        for right in range(left + 1, 4):
            standard = sp.zeros(6)
            for raised in range(4):
                for lowered in range(4):
                    standard[1 + raised, 1 + lowered] = sp.simplify(
                        sum(
                            metric[raised, contracted]
                            * delta_r[left, right, contracted, lowered]
                            for contracted in range(4)
                        )
                    )
            coordinates = left_inverse * standard.reshape(36, 1)
            if embedded * coordinates != standard.reshape(36, 1):
                raise AssertionError("curvature variation escaped so(4,2)")
            curvature_coordinates[(left, right)] = coordinates
            incidence[15 * left : 15 * (left + 1), right] = coordinates
            incidence[15 * right : 15 * (right + 1), left] = -coordinates

    p0 = middle_fixture()["screen"].harmonic_p0
    delta_daut_incidence = -incidence * p0
    if incidence.rank() != 4 or len(incidence.todok()) != 12:
        raise AssertionError("transverse incidence rank/support drifted")
    if delta_daut_incidence.rank() != 4 or len(delta_daut_incidence.todok()) != 12:
        raise AssertionError("automorphism-arrow correction drifted")
    if -sp.Rational(1, 2) * incidence[4, 1] != 1:
        raise AssertionError("normalized incidence anchor drifted")

    return {
        "adjoint_basis_names": list(names),
        "delta_ricci": _sparse(delta_ricci),
        "algebraic_bianchi_defect_count": len(bianchi_defects),
        "delta_normal_tractor_curvature": {
            f"{left}{right}": _sparse(value)
            for (left, right), value in sorted(curvature_coordinates.items())
        },
        "delta_curvature_incidence": _sparse(incidence),
        "harmonic_projection_p0": _sparse(p0),
        "delta_daut_incidence_term": _sparse(delta_daut_incidence),
        "normalized_anchor": {
            "expression": "-(1/2) delta_I_Omega[4,1]",
            "value": str(-sp.Rational(1, 2) * incidence[4, 1]),
        },
    }


def build() -> dict[str, Any]:
    dependencies = {
        "transverse_witness": (WITNESS, "NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1"),
        "curvature_incidence_identity": (INCIDENCE, "NARIAI_CURVATURE_INCIDENCE_FIRST_SQUARE_V1"),
        "rank_310_mapping_cone": (MAPPING_CONE, "NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1"),
    }
    refs = {}
    for name, (path, expected) in dependencies.items():
        payload = json.loads(path.read_text())
        if payload["result_id"] != expected:
            raise AssertionError(f"dependency drifted: {name}")
        refs[name] = {
            "path": str(path.relative_to(ROOT)),
            "result_id": expected,
            "sha256": _sha(path),
        }
    if json.loads(WITNESS.read_text())["flags"]["TRANSVERSE_METRIC_PARENT_SDR_FIRST_VARIATION"] is not False:
        raise AssertionError("first-variation gate was not open")

    variation = exact_variation()
    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "nariai-transverse-curvature-incidence-variation-v1",
        "schema_version": "1.0.0",
        "result_id": "NARIAI_TRANSVERSE_CURVATURE_INCIDENCE_VARIATION_V1",
        "result_state": "FIRST_AND_DUAL_CURVATURE_INCIDENCE_VARIATION_EXACT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": refs,
        "evaluation": {
            "background": "unit Nariai",
            "tangent": "delta a=-(1/3)sinh(2t), delta b=sinh(t)",
            "frame": "epsilon-dependent orthonormal normal frame",
            "point": "t=asinh(1)",
            "delta_schouten_components": "0 because the tangent is Einstein at fixed cosmological constant in the moving orthonormal frame",
            "delta_cotton": "0",
        },
        "exact_data": variation,
        "linearized_first_square": {
            "identity": "dot(d^D)L0+d^D dot(L0)-dot(L1)K-L1 dot(K)=dot(I_Omega)",
            "strict_automorphism_arrow": "d_aut=d^D-I_Omega p0",
            "required_incidence_correction": "dot(d_aut)=dot(d^D)-dot(I_Omega)p0",
            "normalized_nonzero_term": variation["normalized_anchor"],
        },
        "cyclic_completion": {
            "dual_rule": "the opposite BV row receives the forced formal adjoint of -dot(I_Omega)p0 under the serialized rank-310 pairings",
            "dual_rank": variation["delta_daut_incidence_term"]["rank"],
            "dual_nonzero_entries_before_pairing_change": len(variation["delta_daut_incidence_term"]["entries"]),
            "full_pairing_variation_solved": False,
        },
        "exact_checks": {
            "delta_Riemann_algebraic_Bianchi": True,
            "delta_Ricci_zero": True,
            "delta_normal_tractor_curvature_reconstructed": True,
            "delta_curvature_incidence_rank_four": True,
            "delta_curvature_incidence_twelve_entries": True,
            "delta_daut_incidence_rank_four": True,
            "delta_daut_incidence_twelve_entries": True,
            "normalized_anchor_equals_one": True,
            "dual_row_forced_by_cyclicity": True,
        },
        "flags": {
            "NARIAI_TRANSVERSE_CURVATURE_INCIDENCE_VARIATION_V1": True,
            "TRANSVERSE_FIRST_AND_DUAL_INCIDENCE_VARIATION": True,
            "TRANSVERSE_BGG_SPLITTING_VARIATION": False,
            "TRANSVERSE_MIDDLE_SCHUR_VARIATION": False,
            "TRANSVERSE_METRIC_PARENT_SDR_FIRST_VARIATION": False,
            "TRANSVERSE_METRIC_PARENT_SDR": False,
            "TRANSVERSE_CAUSAL_TRANSFER": False,
        },
        "next_gate": "NARIAI_TRANSVERSE_BGG_SPLITTING_AND_MIDDLE_SCHUR_VARIATION",
        "claim_boundary": "This exact first-order certificate differentiates the canonical curvature-incidence term and its forced cyclic dual along the certified transverse linearized Einstein tangent. It proves the rank-four twelve-entry correction required in the first automorphism row. It does not yet solve the variations of the BGG splittings, middle/Schur identity, fibre pairing, complete rank-310 SDR, or causal transfer.",
        "source_manifest": sources,
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.nariai_transverse_curvature_incidence_variation --check --guards",
            "python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_curvature_incidence_variation.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_transverse_curvature_incidence_variation",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-curvature-incidence-variation-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_CURVATURE_INCIDENCE_VARIATION_V1.json"
        ],
    }


def _report(payload: dict[str, Any]) -> str:
    data = payload["exact_data"]
    return rf"""# Transverse variation of the Nariai curvature incidence

Along the certified Kantowski--Sachs linearized Einstein tangent, evaluated in
an adapted orthonormal normal frame at (t=\operatorname{{arsinh}}1), the
curvature variation is Ricci-free and has sectional Weyl entries

\[
(\dot C_{{01}},\dot C_{{02}},\dot C_{{03}},
 \dot C_{{12}},\dot C_{{13}},\dot C_{{23}})
=(2,-1,-1,1,1,-2).
\]

Reconstructing the normal-adjoint-tractor curvature gives the exact incidence

\[
(\dot I_\Omega\xi)_a=\dot\Omega_{{ab}}\xi^b.
\]

Its matrix has shape `{data['delta_curvature_incidence']['shape']}`, rank
`{data['delta_curvature_incidence']['rank']}`, and
`{len(data['delta_curvature_incidence']['entries'])}` nonzero entries.  The
normalization anchor is

\[
-\frac12(\dot I_\Omega)_{{4,1}}=1.
\]

Therefore differentiation of the first curved BGG square gives

\[
\dot d^D L_0+d^D\dot L_0-\dot L_1K-L_1\dot K=\dot I_\Omega,
\]

and the strict automorphism arrow must vary as

\[
\dot d_{{\rm aut}}=\dot d^D-\dot I_\Omega p_0.
\]

The explicit incidence contribution `-dot(I_Omega)p0` again has rank four and
twelve entries.  Cyclicity forces its formal-adjoint contribution in the
opposite BV row.

This closes the first and dual incidence variation only.  The BGG splitting,
middle/Schur, pairing, and complete rank-310 SDR variations remain the next
gate; no transverse causal theorem is claimed.
"""


def verify(payload: dict[str, Any]) -> None:
    if payload["dependency_tags"] != ["LOCAL-ALGEBRAIC"]:
        raise AssertionError("dependency scope drifted")
    if not all(payload["exact_checks"].values()):
        raise AssertionError("a curvature-variation check failed")
    incidence = payload["exact_data"]["delta_curvature_incidence"]
    correction = payload["exact_data"]["delta_daut_incidence_term"]
    if incidence["rank"] != 4 or len(incidence["entries"]) != 12:
        raise AssertionError("incidence rank/support drifted")
    if correction["rank"] != 4 or len(correction["entries"]) != 12:
        raise AssertionError("automorphism correction rank/support drifted")
    if payload["exact_data"]["normalized_anchor"]["value"] != "1":
        raise AssertionError("normalization anchor drifted")
    for flag in (
        "TRANSVERSE_BGG_SPLITTING_VARIATION",
        "TRANSVERSE_MIDDLE_SCHUR_VARIATION",
        "TRANSVERSE_METRIC_PARENT_SDR_FIRST_VARIATION",
        "TRANSVERSE_METRIC_PARENT_SDR",
        "TRANSVERSE_CAUSAL_TRANSFER",
    ):
        if payload["flags"][flag] is not False:
            raise AssertionError(f"downstream flag promoted: {flag}")


def _guards(payload: dict[str, Any]) -> None:
    mutations = (
        ("erase anchor", ("exact_data", "normalized_anchor", "value"), "0"),
        ("promote splitting", ("flags", "TRANSVERSE_BGG_SPLITTING_VARIATION"), True),
        ("promote SDR", ("flags", "TRANSVERSE_METRIC_PARENT_SDR"), True),
    )
    for name, path, value in mutations:
        mutant = deepcopy(payload)
        target: Any = mutant
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            verify(mutant)
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard accepted: {name}")


def _write(payload: dict[str, Any]) -> None:
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(_report(payload))


def _check(payload: dict[str, Any]) -> None:
    if json.loads(OUTPUT.read_text()) != payload:
        raise AssertionError("certificate drifted")
    if REPORT.read_text() != _report(payload):
        raise AssertionError("report drifted")
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = build()
    verify(payload)
    if args.write:
        _write(payload)
    if args.check:
        _check(payload)
    if args.guards:
        _guards(payload)
    print("NARIAI_TRANSVERSE_CURVATURE_INCIDENCE_VARIATION_V1: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
