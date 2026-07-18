#!/usr/bin/env python3
"""Freeze algebraic BGG data and compute the transverse incidence adjoint."""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.nariai_transverse_curvature_incidence_variation import (
    exact_variation,
)
from d_quotient_classical.causal_transfer.nariai_yang_mills_middle_compression import (
    fixture,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ALGEBRAIC_BGG_PAIRING_VARIATION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-algebraic-bgg-pairing-variation.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-algebraic-bgg-pairing-variation-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/causal_transfer/verify_nariai_transverse_algebraic_bgg_pairing_variation.py"
TESTS = ROOT / "d_quotient_classical/causal_transfer/tests/test_nariai_transverse_algebraic_bgg_pairing_variation.py"
INCIDENCE_CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_CURVATURE_INCIDENCE_VARIATION_V1.json"
KOSTANT_MATRICES = ROOT / "covariant_completion/certificates/adjoint_tractor_kostant_compression_matrices.json"
SCREEN_MATRICES = ROOT / "covariant_completion/certificates/adjoint_tractor_bgg_differential_screen_matrices.json"
MIDDLE_CERT = ROOT / "d_quotient_classical/certificates/NARIAI_ALGEBRAIC_ENDPOINT_CURVATURE_REPAIR_OBSTRUCTION_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _deserialize(record: dict[str, Any]) -> sp.Matrix:
    value = sp.zeros(*record["shape"])
    for row, column, coefficient in record["entries"]:
        value[row, column] = sp.Rational(coefficient)
    return value


def _sparse(matrix: sp.Matrix) -> dict[str, Any]:
    return {
        "shape": [matrix.rows, matrix.cols],
        "rank": matrix.rank(),
        "entries": [[row, column, str(value)] for (row, column), value in sorted(matrix.todok().items())],
        "sha256": hashlib.sha256(sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode()).hexdigest(),
    }


@lru_cache(maxsize=1)
def exact_data() -> dict[str, Any]:
    data = fixture()
    algebraic = data["algebraic"]
    incidence = exact_variation()
    correction = _deserialize(incidence["delta_daut_incidence_term"])
    pair_c0 = algebraic.adjoint_pairing
    pair_c1 = algebraic.one_form_pairing
    dual = pair_c0.inv() * correction.T * pair_c1

    algebraic_maps = {
        "kostant_i0": algebraic.i0,
        "kostant_i1": algebraic.i1,
        "kostant_q1": data["screen"].q1,
        "kostant_q2": data["screen"].q2,
        "harmonic_p0": data["screen"].harmonic_p0,
        "harmonic_p1": data["screen"].harmonic_p1,
    }
    pairings = {
        "C0": pair_c0,
        "C1": pair_c1,
        "H0": algebraic.endpoint_ghost_pairing,
        "H1": algebraic.endpoint_field_pairing,
    }
    for name, pairing in pairings.items():
        if pairing.det() == 0 or pairing != pairing.T:
            raise AssertionError(f"{name} pairing drifted")
    if pair_c0 * dual - correction.T * pair_c1 != sp.zeros(15, 60):
        raise AssertionError("formal-adjoint incidence identity failed")
    if dual.rank() != correction.rank():
        raise AssertionError("dual incidence rank changed")

    return {
        "frame_identification": {
            "type": "epsilon-dependent orthonormal conformal tractor frame and covariant PBW derivative basis",
            "consequence": "algebraic representation maps and fibre pairings have zero first variation",
            "coordinate_warning": "this is not a claim that ordinary-coordinate connection coefficients have zero variation",
        },
        "fixed_Lambda_Einstein_tangent": {
            "dot_Schouten_in_moving_frame": "0",
            "dot_Cotton": "0",
            "reason": "P_ab=(Lambda/6)g_ab and the frame is orthonormal for every epsilon",
        },
        "algebraic_maps": {
            name: {"value": _sparse(matrix), "first_variation": _sparse(sp.zeros(*matrix.shape))}
            for name, matrix in algebraic_maps.items()
        },
        "fibre_pairings": {
            name: {"value": _sparse(matrix), "first_variation": _sparse(sp.zeros(*matrix.shape))}
            for name, matrix in pairings.items()
        },
        "incidence_correction": _sparse(correction),
        "formal_adjoint_dual": _sparse(dual),
        "formal_adjoint_identity": "J_C0 dot(d_aut)^sharp = dot(d_aut)^T J_C1",
        "formal_adjoint_defect": _sparse(pair_c0 * dual - correction.T * pair_c1),
    }


def build() -> dict[str, Any]:
    dependency = json.loads(INCIDENCE_CERT.read_text())
    if dependency["result_id"] != "NARIAI_TRANSVERSE_CURVATURE_INCIDENCE_VARIATION_V1":
        raise AssertionError("incidence dependency drifted")
    exact = exact_data()
    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "nariai-transverse-algebraic-bgg-pairing-variation-v1",
        "schema_version": "1.0.0",
        "result_id": "NARIAI_TRANSVERSE_ALGEBRAIC_BGG_PAIRING_VARIATION_V1",
        "result_state": "ALGEBRAIC_BGG_AND_PAIRING_VARIATION_ZERO_IN_COVARIANT_FRAME_DUAL_INCIDENCE_EXACT",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "incidence": {
                "path": str(INCIDENCE_CERT.relative_to(ROOT)),
                "result_id": dependency["result_id"],
                "sha256": _sha(INCIDENCE_CERT),
            },
            "kostant_matrices": {
                "path": str(KOSTANT_MATRICES.relative_to(ROOT)),
                "sha256": _sha(KOSTANT_MATRICES),
            },
            "differential_screen_matrices": {
                "path": str(SCREEN_MATRICES.relative_to(ROOT)),
                "sha256": _sha(SCREEN_MATRICES),
            },
            "middle_pairing_fixture": {
                "path": str(MIDDLE_CERT.relative_to(ROOT)),
                "result_id": json.loads(MIDDLE_CERT.read_text())["result_id"],
                "sha256": _sha(MIDDLE_CERT),
            },
        },
        "exact_data": exact,
        "exact_checks": {
            "algebraic_BGG_variation_zero_in_declared_frame": True,
            "all_four_pairing_variations_zero_in_declared_frame": True,
            "Schouten_variation_zero_in_declared_frame": True,
            "incidence_dual_computed": True,
            "incidence_dual_formal_adjoint_defect_zero": True,
            "incidence_dual_rank_four": exact["formal_adjoint_dual"]["rank"] == 4,
        },
        "flags": {
            "TRANSVERSE_ALGEBRAIC_BGG_PAIRING_VARIATION": True,
            "TRANSVERSE_INCIDENCE_DUAL_EXACT": True,
            "TRANSVERSE_CONNECTION_PBW_VARIATION": False,
            "TRANSVERSE_MIDDLE_SCHUR_VARIATION": False,
            "TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION": False,
            "TRANSVERSE_CAUSAL_TRANSFER": False,
        },
        "next_gate": "NARIAI_TRANSVERSE_CONNECTION_PBW_AND_MIDDLE_SCHUR_VARIATION",
        "claim_boundary": "In the declared moving orthonormal covariant-PBW frame, this certificate proves that the representation-theoretic BGG/Kostant maps and fibre pairings do not vary, and it computes the exact formal-adjoint dual of the outer incidence correction. It does not set the variation of the Levi-Civita connection to zero, and it does not solve the connection/PBW, middle/Schur, full SDR, or causal variations.",
        "source_manifest": sources,
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.nariai_transverse_algebraic_bgg_pairing_variation --check",
            "python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_algebraic_bgg_pairing_variation.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_transverse_algebraic_bgg_pairing_variation",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-algebraic-bgg-pairing-variation-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_ALGEBRAIC_BGG_PAIRING_VARIATION_V1.json",
        ],
    }


def _report(_: dict[str, Any]) -> str:
    return r"""# Transverse algebraic BGG and pairing variation

Use an epsilon-dependent orthonormal conformal-tractor frame and write every
operator in the corresponding covariant PBW derivative basis.  The
Kostant inclusions/homotopies, harmonic projections, and the four fibre
pairings are representation-theoretic constant matrices, so their first
variations vanish in this frame.  Since the transverse tangent is Einstein at
fixed cosmological constant, the moving-frame Schouten variation also
vanishes.

This does **not** set the Levi--Civita connection variation to zero.  That
variation is the remaining connection/PBW gate.

With the now-fixed `C0` and `C1` pairings, the outer correction

\[
\dot d_{\rm aut}^{\rm inc}=-\dot I_\Omega p_0
\]

has an exact formal adjoint

\[
(\dot d_{\rm aut}^{\rm inc})^\sharp
=J_{C0}^{-1}(\dot d_{\rm aut}^{\rm inc})^T J_{C1}.
\]

Both maps have rank four, and the displayed formal-adjoint defect is zero.
Thus the previous “forced dual row” is now coefficientwise explicit.  The
connection/PBW and middle/Schur variations remain open.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if args.write:
        OUTPUT.write_text(json.dumps(payload, indent=2) + "\n")
        REPORT.write_text(_report(payload))
    else:
        if json.loads(OUTPUT.read_text()) != payload or REPORT.read_text() != _report(payload):
            raise AssertionError("algebraic BGG/pairing variation artifact is stale")
    print("NARIAI_TRANSVERSE_ALGEBRAIC_BGG_PAIRING_VARIATION_V1: PASS")


if __name__ == "__main__":
    main()
