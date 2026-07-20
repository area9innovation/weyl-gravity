#!/usr/bin/env python3
"""Independent raw-record replay of the fully mixed cone SDR obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_Q26_104_ROW_FULLY_MIXED_CONE_SDR_OBSTRUCTION_V1.json"
)
PAYLOAD = (
    ROOT
    / "d_quotient_classical/generated/"
    "berger_q26_104_row_fully_mixed_cone_sdr_obstruction_v1/"
    "rational_cohomology_witness.json"
)
Q104 = (
    ROOT
    / "quantum-weyl/lorentzian/generated/"
    "berger_canonical_graph_q_cauchy_obstruction/"
    "rejected_candidate_q_Cauchy_104.json"
)
RETAINED = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_RETAINED_MINIMAL_OPERATOR.json"
)
DEGREES_104 = tuple(
    [-1] * 6 + [0] * 20 + [1] * 20 + [2] * 6
) * 2


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _constant_matrix(record: dict, shape: tuple[int, int]) -> sp.Matrix:
    result = sp.zeros(*shape)
    symbols = {
        "alpha_B": sp.Rational(2),
        "u": sp.Rational(1),
        "v": sp.Rational(3),
    }
    for row, column, terms in record["entries"]:
        for exponents, coefficient in terms:
            if not any(exponents):
                result[row, column] += sp.sympify(
                    coefficient, locals=symbols
                )
    return result


def _block_rank(
    matrix: sp.Matrix,
    degrees: tuple[int, ...],
    degree: int,
) -> int:
    columns = [
        index for index, value in enumerate(degrees) if value == degree
    ]
    rows = [
        index
        for index, value in enumerate(degrees)
        if value == degree + 1
    ]
    return int(matrix.extract(rows, columns).rank()) if rows else 0


def verify() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    if (
        certificate["result_id"]
        != "BERGER_Q26_104_ROW_FULLY_MIXED_CONE_SDR_OBSTRUCTION_V1"
    ):
        raise AssertionError("certificate identity drifted")
    for item in certificate["pinned_inputs"].values():
        if _sha(ROOT / item["path"]) != item["sha256"]:
            raise AssertionError(f"pinned input drifted: {item['path']}")
    exact = certificate["sdr_obstruction"]["exact_payload"]
    if _sha(ROOT / exact["path"]) != exact["sha256"]:
        raise AssertionError("payload hash drifted")

    q104 = _constant_matrix(json.loads(Q104.read_text()), (104, 104))
    ranks104 = {
        degree: _block_rank(q104, DEGREES_104, degree)
        for degree in (-1, 0, 1, 2)
    }
    cone_dimensions = {-1: 24, 0: 80, 1: 80, 2: 24}
    cone_h = {
        degree: cone_dimensions[degree]
        - ranks104[degree]
        - ranks104.get(degree - 1, 0)
        for degree in (-1, 0, 1, 2)
    }

    retained = json.loads(RETAINED.read_text())
    q26 = sp.zeros(26)
    slots = (
        ("K_spatial", slice(3, 13), slice(0, 3)),
        ("H_retained", slice(13, 23), slice(3, 13)),
        ("minus_K_spatial_sharp", slice(23, 26), slice(13, 23)),
    )
    for name, rows, columns in slots:
        record = retained["q1_blocks"][name]
        q26[rows, columns] = _constant_matrix(
            record, tuple(record["shape"])
        )
    degrees26 = tuple([-1] * 3 + [0] * 10 + [1] * 10 + [2] * 3)
    ranks26 = {
        degree: _block_rank(q26, degrees26, degree)
        for degree in (-1, 0, 1, 2)
    }
    retained_dimensions = {-1: 3, 0: 10, 1: 10, 2: 3}
    retained_h = {
        degree: retained_dimensions[degree]
        - ranks26[degree]
        - ranks26.get(degree - 1, 0)
        for degree in (-1, 0, 1, 2)
    }
    if cone_h != {-1: 13, 0: 57, 1: 57, 2: 13}:
        raise AssertionError(f"cone cohomology drifted: {cone_h}")
    if retained_h != {-1: 1, 0: 1, 1: 1, 2: 1}:
        raise AssertionError(f"retained cohomology drifted: {retained_h}")
    if payload["cone_homology_dimensions"] != {
        str(key): value for key, value in cone_h.items()
    }:
        raise AssertionError("payload cone dimensions drifted")
    if payload["retained_homology_dimensions"] != {
        str(key): value for key, value in retained_h.items()
    }:
        raise AssertionError("payload retained dimensions drifted")
    flags = certificate["classification"]
    if (
        not flags["fully_mixed_cone_evolution_lift_exists"]
        or flags["retained_q26_SDR_exists"]
        or flags["all_non_cone_104_row_completions_obstructed"]
    ):
        raise AssertionError("classification boundary drifted")
    print(
        "BERGER_Q26_104_ROW_FULLY_MIXED_CONE_SDR_OBSTRUCTION_V1: "
        f"PASS cone_h={list(cone_h.values())} "
        f"retained_h={list(retained_h.values())}"
    )


if __name__ == "__main__":
    verify()
