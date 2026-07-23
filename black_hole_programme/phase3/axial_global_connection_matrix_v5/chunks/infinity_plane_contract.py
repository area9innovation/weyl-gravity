"""Exact basis contract for the two finite axial infinity trace planes.

The radial factor rail uses the contiguous block order, whereas the
action-derived infinity initializer uses the standard realification of the
six complex formal traces.  This module freezes the two selectors and their
row crosswalk without performing any radial propagation.
"""
from __future__ import annotations

import itertools
from fractions import Fraction
from typing import Any

import sympy as sp

from .state_permutation import (
    STANDARD_REAL_ORDER,
    permutation_payload,
    verify_permutation,
)
from .verify_handoff import _require, canonical_sha256
from .verify_microfactor import BLOCK_ORDER


SCHEMA = "phase3-axial-infinity-physical-plane-contract-v1"
INFINITY_ORDER = ("XI0", "XI1", "XI2", "XI3", "EI0", "EI2")
IMINUS_SELECTOR = (0, 1, 4)
IPLUS_SELECTOR = (2, 3, 5)
COMPLEX_REAL_ROWS = (
    (0, 4),   # P
    (1, 5),   # P'
    (2, 6),   # Q
    (3, 7),   # Q'
    (8, 10),  # H1
    (9, 11),  # F
)
CHARTS = tuple(itertools.combinations(range(6), 3))


def _qmatrix(rows: int, cols: int) -> list[list[str]]:
    return [["0/1" for _ in range(cols)] for _ in range(rows)]


def standard_plane(selector: tuple[int, int, int]) -> list[list[str]]:
    """Realify a real complex 6x3 coordinate selector."""
    out = _qmatrix(12, 6)
    for column, row in enumerate(selector):
        out[row][column] = "1/1"
        out[row + 6][column + 3] = "1/1"
    return out


def _multiply(left: list[list[str]], right: list[list[str]]) -> list[list[str]]:
    a = sp.Matrix([[sp.Rational(value) for value in row] for row in left])
    b = sp.Matrix([[sp.Rational(value) for value in row] for row in right])
    c = a * b
    return [[str(c[i, j]) for j in range(c.cols)] for i in range(c.rows)]


def block_plane(selector: tuple[int, int, int]) -> list[list[str]]:
    permutation = permutation_payload()["standard_to_block_matrix"]
    return _multiply(permutation, standard_plane(selector))


def concatenated_standard_basis() -> list[list[str]]:
    minus = standard_plane(IMINUS_SELECTOR)
    plus = standard_plane(IPLUS_SELECTOR)
    return [minus[row] + plus[row] for row in range(12)]


def contract_payload() -> dict[str, Any]:
    concat = concatenated_standard_basis()
    determinant = sp.Matrix(
        [[sp.Rational(value) for value in row] for row in concat]
    ).det()
    permutation = permutation_payload()
    payload = {
        "schema": SCHEMA,
        "status": "CERTIFIED",
        "complex_infinity_order": list(INFINITY_ORDER),
        "selectors": {
            "Iminus": list(IMINUS_SELECTOR),
            "Iplus": list(IPLUS_SELECTOR),
        },
        "state_orders": {
            "standard": list(STANDARD_REAL_ORDER),
            "block": list(BLOCK_ORDER),
        },
        "standard_to_block_crosswalk_sha256": permutation[
            "crosswalk_sha256"
        ],
        "initial_planes": {
            "Iminus_standard_12_by_6": standard_plane(IMINUS_SELECTOR),
            "Iplus_standard_12_by_6": standard_plane(IPLUS_SELECTOR),
            "Iminus_block_12_by_6": block_plane(IMINUS_SELECTOR),
            "Iplus_block_12_by_6": block_plane(IPLUS_SELECTOR),
        },
        "combined_standard_basis": {
            "matrix_12_by_12": concat,
            "determinant": str(determinant),
            "rank": 12,
        },
        "grassmann_atlas": {
            "complex_plane_dimension": 3,
            "real_plane_dimension": 6,
            "ambient_complex_dimension": 6,
            "ambient_real_dimension": 12,
            "complex_state_real_rows": [list(rows) for rows in COMPLEX_REAL_ROWS],
            "charts": [list(chart) for chart in CHARTS],
            "chart_count": len(CHARTS),
            "state_factorization": "Y=G_chart(Z)*A",
        },
        "required_terminal_gate": {
            "separate_plane_rank": 6,
            "concatenated_endpoint_basis_rank": 12,
            "separate_plane_rank_does_not_imply_combined_rank": True,
        },
        "does_not_establish": [
            "a propagated plane at r=4",
            "rank of the concatenated propagated endpoint basis",
            "horizon-to-infinity matching",
            "endpoint flux, scattering, stability, CPT, or unitarity",
        ],
    }
    payload["payload_sha256"] = canonical_sha256(payload)
    return payload


def verify_contract(data: Any) -> bool:
    expected = contract_payload()
    _require(data == expected, "infinity plane contract: exact payload drift")
    verify_permutation(permutation_payload())
    minus = set(data["selectors"]["Iminus"])
    plus = set(data["selectors"]["Iplus"])
    _require(
        not minus.intersection(plus)
        and minus.union(plus) == set(range(6)),
        "infinity plane contract: selectors are not complementary",
    )
    combined = sp.Matrix([
        [sp.Rational(value) for value in row]
        for row in data["combined_standard_basis"]["matrix_12_by_12"]
    ])
    _require(
        combined.rank() == 12
        and combined.det() == sp.Rational(
            data["combined_standard_basis"]["determinant"]
        ),
        "infinity plane contract: combined basis is not invertible",
    )
    _require(
        data["grassmann_atlas"]["chart_count"] == 20
        and len(data["grassmann_atlas"]["charts"]) == 20,
        "infinity plane contract: chart atlas incomplete",
    )
    return True
