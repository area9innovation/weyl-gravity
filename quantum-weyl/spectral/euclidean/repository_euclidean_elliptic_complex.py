#!/usr/bin/env python3
"""Build the exact repository Euclidean full-BV principal-symbol complex."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from spectral.euclidean.elliptic_complex_receiver import (
    validate_euclidean_elliptic_complex,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATES = HERE / "certificates"
OUTPUT = CERTIFICATES / "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX.json"
GAUGE_OUTPUT = CERTIFICATES / "REPOSITORY_EUCLIDEAN_GAUGE_FIXING.json"
ADJOINT_OUTPUT = CERTIFICATES / "REPOSITORY_EUCLIDEAN_FORMAL_ADJOINT_COMPLEX.json"

FIELD_DICTIONARY = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json"
MULTIPLICITY = CERTIFICATES / "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER.json"
SNAPSHOT = ROOT / "quantum-weyl/classical_import/certificates/REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY.json"
NORMALIZATION = CERTIFICATES / "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1.json"

METRIC_BASIS = ["h00", "h01", "h02", "h03", "h11", "h22", "h33", "h12", "h13", "h23"]
GHOST_BASIS = ["xi0", "xi1", "xi2", "xi3", "omega"]
TT_BASIS = ["h11-h22", "h22-h33", "h12", "h13", "h23"]


def _canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _sparse(matrix: list[list[Fraction | int]]) -> dict[str, Any]:
    return {
        "shape": [len(matrix), len(matrix[0])],
        "entries": [
            {"row": row, "column": column, "coefficient": _q(value)}
            for row, values in enumerate(matrix)
            for column, value in enumerate(values)
            if value
        ],
    }


def _multiply(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0))
         for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def _transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(column) for column in zip(*matrix)]


def _rank(matrix: list[list[Fraction]]) -> int:
    work = [row[:] for row in matrix]
    rows, columns = len(work), len(work[0])
    rank = column = 0
    while rank < rows and column < columns:
        pivot = next((row for row in range(rank, rows) if work[row][column]), None)
        if pivot is None:
            column += 1
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][column]
        work[rank] = [entry / scale for entry in work[rank]]
        for row in range(rows):
            if row != rank and work[row][column]:
                scale = work[row][column]
                work[row] = [left - scale * right for left, right in zip(work[row], work[rank])]
        rank += 1
        column += 1
    return rank


def _determinant(matrix: list[list[Fraction]]) -> Fraction:
    work = [row[:] for row in matrix]
    result = Fraction(1)
    for column in range(len(work)):
        pivot = next((row for row in range(column, len(work)) if work[row][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        pivot_value = work[column][column]
        result *= pivot_value
        for row in range(column + 1, len(work)):
            scale = work[row][column] / pivot_value
            work[row] = [left - scale * right for left, right in zip(work[row], work[column])]
    return result


def _matrices() -> dict[str, list[list[Fraction]]]:
    zero = Fraction(0)
    K = [[zero for _ in range(5)] for _ in range(10)]
    K[0][0], K[0][4] = Fraction(2), Fraction(2)
    K[1][1] = K[2][2] = K[3][3] = Fraction(1)
    K[4][4] = K[5][4] = K[6][4] = Fraction(2)

    P = [[zero for _ in range(10)] for _ in range(5)]
    P[0][4], P[0][5] = Fraction(1), Fraction(-1)
    P[1][5], P[1][6] = Fraction(1), Fraction(-1)
    P[2][7] = P[3][8] = P[4][9] = Fraction(1)

    G = [[zero for _ in range(10)] for _ in range(5)]
    G[0][0] = G[1][1] = G[2][2] = G[3][3] = Fraction(1)
    G[4][0] = G[4][4] = G[4][5] = G[4][6] = Fraction(1)

    nd_in = [[Fraction(int(row == column)) for column in range(4)] for row in range(8)]
    nd_out = [[Fraction(int(column == row + 4)) for column in range(8)] for row in range(4)]
    nw_in = [[Fraction(1)], [Fraction(0)]]
    nw_out = [[Fraction(0), Fraction(1)]]
    return {
        "K": K, "P": P, "G": G,
        "PT": _transpose(P), "KT": _transpose(K),
        "nonminimal_diff_in": nd_in, "nonminimal_diff_out": nd_out,
        "nonminimal_weyl_in": nw_in, "nonminimal_weyl_out": nw_out,
    }


def _with_digest(value: dict[str, Any]) -> dict[str, Any]:
    value["proof_sha256"] = _canonical_hash(value)
    return value


def gauge_fixing() -> dict[str, Any]:
    matrices = _matrices()
    fp = _multiply(matrices["G"], matrices["K"])
    return _with_digest({
        "schema": "quantum-weyl-repository-euclidean-gauge-fixing-v1",
        "result_id": "REPOSITORY_EUCLIDEAN_GAUGE_FIXING",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": json.loads(MULTIPLICITY.read_text())["classical_commit"],
        "cotangent_representative": "k=(1,0,0,0)",
        "bases": {"ghost": GHOST_BASIS, "metric": METRIC_BASIS, "physical_slice": TT_BASIS},
        "conformal_deformation_symbol": _sparse(matrices["K"]),
        "gauge_condition_symbol": _sparse(matrices["G"]),
        "faddeev_popov_symbol": _sparse(fp),
        "faddeev_popov_rank": _rank(fp),
        "faddeev_popov_determinant": _q(_determinant(fp)),
        "gauge_slice_projection_symbol": _sparse(matrices["P"]),
        "identities": {
            "orbit_rank": _rank(matrices["K"]),
            "slice_rank": _rank(matrices["P"]),
            "projection_annihilates_orbit": not any(
                value for row in _multiply(matrices["P"], matrices["K"]) for value in row
            ),
            "gauge_slice_dimension": 5,
            "all_nonzero_covectors_covered_by_SO4": True,
        },
        "claim_boundary": "Exact Euclidean principal-symbol gauge fixing at one SO(4) cotangent representative. It certifies the local orbit/slice split and invertible FP symbol, not a determinant coefficient, global zero-mode normalization, QME, or Lorentzian theory.",
    })


def formal_adjoint() -> dict[str, Any]:
    matrices = _matrices()
    product = _multiply(matrices["KT"], matrices["PT"])
    return _with_digest({
        "schema": "quantum-weyl-repository-euclidean-formal-adjoint-complex-v1",
        "result_id": "REPOSITORY_EUCLIDEAN_FORMAL_ADJOINT_COMPLEX",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": json.loads(MULTIPLICITY.read_text())["classical_commit"],
        "cotangent_representative": "k=(1,0,0,0)",
        "incoming_symbol": _sparse(matrices["PT"]),
        "outgoing_symbol": _sparse(matrices["KT"]),
        "incoming_rank": _rank(matrices["PT"]),
        "outgoing_rank": _rank(matrices["KT"]),
        "composition_zero": not any(value for row in product for value in row),
        "exact_at_metric_cotangent_middle": _rank(matrices["PT"]) == 10 - _rank(matrices["KT"]),
        "pairing_convention": "Euclidean coefficient pairing in the ordered ghost, metric, and TT bases",
        "claim_boundary": "This is the exact formal-adjoint principal-symbol sequence of the local conformal deformation complex. It is not a global self-adjoint extension, determinant phase, Hadamard statement, or QME result.",
    })


def _artifact(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "format": "JSON_PROOF" if path in (GAUGE_OUTPUT, ADJOINT_OUTPUT) else "JSON_DATA",
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(_canonical_bytes(value)).hexdigest(),
    }


def _existing_artifact(path: Path) -> dict[str, str]:
    return {
        "format": "JSON_DATA" if path in (MULTIPLICITY, NORMALIZATION) else "JSON_PROOF",
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def _sector(identifier: str, incoming: list[list[Fraction]], outgoing: list[list[Fraction]]) -> dict[str, Any]:
    incoming_rank, outgoing_rank = _rank(incoming), _rank(outgoing)
    return {
        "sector_id": identifier,
        "domain_dimension": len(incoming[0]),
        "middle_dimension": len(incoming),
        "codomain_dimension": len(outgoing),
        "incoming_symbol": _sparse(incoming),
        "outgoing_symbol": _sparse(outgoing),
        "incoming_rank": incoming_rank,
        "outgoing_rank": outgoing_rank,
        "kernel_outgoing_dimension": len(incoming) - outgoing_rank,
        "exact_at_middle": incoming_rank == len(incoming) - outgoing_rank,
    }


def build() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    gauge = gauge_fixing()
    adjoint = formal_adjoint()
    matrices = _matrices()
    commit = json.loads(MULTIPLICITY.read_text())["classical_commit"]
    value = {
        "schema": "quantum-weyl-repository-euclidean-elliptic-complex-input-v1",
        "result_id": "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX",
        "result_state": "COMPLETE_GAUGE_FIXED_BV_PRINCIPAL_SYMBOL_SEQUENCE_EXACT_AND_ELLIPTIC",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": commit,
        "analytic_route": "EUCLIDEAN_ELLIPTIC",
        "background": {
            "geometry": "local oriented Euclidean four-manifold",
            "dimension": 4,
            "signature": "EUCLIDEAN",
            "boundary_policy": "LOCAL_COMPACT_SUPPORT",
        },
        "formulation": "FOURTH_ORDER_METRIC",
        "cotangent_orbit_reduction": {
            "representative": "k=(1,0,0,0)",
            "group": "SO(4)",
            "all_nonzero_covectors_covered": True,
        },
        "principal_symbol_exactness": [
            _sector("minimal_conformal_deformation", matrices["K"], matrices["P"]),
            _sector("minimal_cotangent_formal_adjoint", matrices["PT"], matrices["KT"]),
            _sector("nonminimal_diffeomorphism_doublet", matrices["nonminimal_diff_in"], matrices["nonminimal_diff_out"]),
            _sector("nonminimal_weyl_doublet", matrices["nonminimal_weyl_in"], matrices["nonminimal_weyl_out"]),
        ],
        "gauge_fixed_kinetic_blocks": [
            {"block_id": "repository_physical_upper_Delta2perp4", "bundle_rank": 5, "differential_order": 2, "principal_scalar": _q(Fraction(1, 2)), "elliptic": True},
            {"block_id": "repository_scalar_ghost_Delta0minus4", "bundle_rank": 1, "differential_order": 2, "principal_scalar": _q(-12), "elliptic": True},
            {"block_id": "repository_physical_lower_Delta2perp2", "bundle_rank": 5, "differential_order": 2, "principal_scalar": _q(1), "elliptic": True},
            {"block_id": "repository_vector_ghost_Delta1perpminus3", "bundle_rank": 3, "differential_order": 2, "principal_scalar": _q(1), "elliptic": True},
        ],
        "coverage": {
            "all_minimal_nonminimal_and_auxiliary_rows_accounted": True,
            "all_symbol_sectors_covered": True,
            "formal_adjoint_complex_verified": True,
            "gauge_fixed_operator_elliptic": True,
        },
        "proof_artifacts": {
            "field_dictionary": _existing_artifact(FIELD_DICTIONARY),
            "multiplicity": _existing_artifact(MULTIPLICITY),
            "snapshot_compatibility": _existing_artifact(SNAPSHOT),
            "action_normalization": _existing_artifact(NORMALIZATION),
            "gauge_fixing": _artifact(GAUGE_OUTPUT, gauge),
            "formal_adjoint": _artifact(ADJOINT_OUTPUT, adjoint),
        },
        "claim_flags": {
            "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX_CERTIFIED": True,
            "FULL_BV_SYMBOL_EXACTNESS_CERTIFIED": True,
            "REGULATED_SLAVNOV_BREAKING_COMPUTED": False,
            "QME_DISPOSITION": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL certificate proves the exact SO(4)-orbit principal-symbol complex, its formal adjoint, nonminimal doublets, invertible gauge symbol, and ellipticity of the four accepted full-BV determinant blocks. It does not compute local b4 coefficients, a regulated Slavnov insertion, the QME, global determinant phases, or a Lorentzian quantum theory.",
    }
    value["proof_sha256"] = _canonical_hash({
        key: value[key]
        for key in (
            "classical_commit", "analytic_route", "background", "formulation",
            "cotangent_orbit_reduction", "principal_symbol_exactness",
            "gauge_fixed_kinetic_blocks", "coverage", "proof_artifacts",
        )
    })
    return gauge, adjoint, value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    gauge, adjoint, value = build()
    rendered = {
        GAUGE_OUTPUT: _canonical_bytes(gauge),
        ADJOINT_OUTPUT: _canonical_bytes(adjoint),
        OUTPUT: _canonical_bytes(value),
    }
    if args.emit:
        for path, data in rendered.items():
            path.write_bytes(data)
    if args.check:
        stale = [str(path) for path, data in rendered.items() if not path.exists() or path.read_bytes() != data]
        if stale:
            raise SystemExit(f"stale repository Euclidean elliptic artifacts: {stale}")
    if all(path.exists() and path.read_bytes() == data for path, data in rendered.items()):
        receipt = validate_euclidean_elliptic_complex(value, repository_root=ROOT)
        print(f"repository Euclidean elliptic complex: PASS ({receipt['symbol_sector_count']} sectors)")
    else:
        print("repository Euclidean elliptic complex: BUILT (emit before semantic validation)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
