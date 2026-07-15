"""Exact Lorentzian epsilon reconstruction of the four-dimensional Euler head.

The direct Chern--Weil expression ``epsilon_abcd R^ab wedge R^cd`` is
compared with the independently sectorized Weyl--Schouten polynomial
``W^2 + 4 W X + 4 X^2``, where ``2X = g wedge P``.  The calculation uses the
frozen Lorentz signature and orientation, exact rational tensor bases, and
negative controls for orientation and the Schouten-square coefficient.  The
mixed epsilon sector is separately proved to vanish by Weyl tracefreeness.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations
import json
from typing import Iterable, Sequence

from .algebra import canonical_sha256
from .euler_connecting_identities import PAIRS, PAIR_INDEX, WEYL_COORDINATES
from .quotient import exact_nullspace, exact_rank


DIMENSION = 4
LORENTZ_SIGNATURE = (-1, 1, 1, 1)
SYMMETRIC_PAIRS = tuple(
    (left, right)
    for left in range(DIMENSION)
    for right in range(left, DIMENSION)
)
SYMMETRIC_PAIR_INDEX = {
    pair: index for index, pair in enumerate(SYMMETRIC_PAIRS)
}
WEYL_COORDINATE_INDEX = {
    coordinate: index for index, coordinate in enumerate(WEYL_COORDINATES)
}


def _epsilon(indices: Sequence[int]) -> int:
    if len(set(indices)) != DIMENSION:
        return 0
    inversions = sum(
        indices[left] > indices[right]
        for left in range(DIMENSION)
        for right in range(left + 1, DIMENSION)
    )
    return -1 if inversions % 2 else 1


def _oriented_pair(left: int, right: int) -> tuple[int | None, int]:
    if left == right:
        return None, 0
    if left < right:
        return PAIR_INDEX[(left, right)], 1
    return PAIR_INDEX[(right, left)], -1


def _weyl_constraint(
    terms: Iterable[tuple[int, tuple[int, int, int, int]]],
) -> tuple[Fraction, ...]:
    row = [Fraction() for _ in WEYL_COORDINATES]
    for coefficient, (a, b, c, d) in terms:
        left, left_sign = _oriented_pair(a, b)
        right, right_sign = _oriented_pair(c, d)
        if left is None or right is None:
            continue
        coordinate = tuple(sorted((left, right)))
        row[WEYL_COORDINATE_INDEX[coordinate]] += (
            coefficient * left_sign * right_sign
        )
    return tuple(row)


@lru_cache(maxsize=1)
def _lorentz_weyl_constraints() -> tuple[tuple[Fraction, ...], ...]:
    constraints = [
        _weyl_constraint(
            (
                (1, (0, 1, 2, 3)),
                (1, (0, 2, 3, 1)),
                (1, (0, 3, 1, 2)),
            )
        )
    ]
    constraints.extend(
        _weyl_constraint(
            (LORENTZ_SIGNATURE[a], (a, b, a, d))
            for a in range(DIMENSION)
        )
        for b in range(DIMENSION)
        for d in range(b, DIMENSION)
    )
    return tuple(constraints)


@lru_cache(maxsize=1)
def _lorentz_weyl_basis() -> tuple[tuple[Fraction, ...], ...]:
    basis = exact_nullspace(
        _lorentz_weyl_constraints(), column_count=len(WEYL_COORDINATES)
    )
    if len(basis) != 10:
        raise AssertionError("Lorentzian four-dimensional Weyl dimension drifted")
    return basis


def _weyl_value(
    vector: Sequence[Fraction], a: int, b: int, c: int, d: int
) -> Fraction:
    left, left_sign = _oriented_pair(a, b)
    right, right_sign = _oriented_pair(c, d)
    if left is None or right is None:
        return Fraction()
    coordinate = tuple(sorted((left, right)))
    return left_sign * right_sign * vector[WEYL_COORDINATE_INDEX[coordinate]]


def _schouten_value(vector: Sequence[Fraction], a: int, b: int) -> Fraction:
    return vector[SYMMETRIC_PAIR_INDEX[tuple(sorted((a, b)))]]


def _metric(a: int, b: int) -> Fraction:
    return Fraction(LORENTZ_SIGNATURE[a] if a == b else 0)


def _schouten_curvature_value(
    schouten: Sequence[Fraction], a: int, b: int, c: int, d: int
) -> Fraction:
    """Return ``(g wedge P)_abcd`` in the frozen Ricci decomposition."""

    return (
        _metric(a, c) * _schouten_value(schouten, b, d)
        - _metric(a, d) * _schouten_value(schouten, b, c)
        - _metric(b, c) * _schouten_value(schouten, a, d)
        + _metric(b, d) * _schouten_value(schouten, a, c)
    )


TwoForm = tuple[Fraction, ...]
CurvatureForms = dict[tuple[int, int], TwoForm]


def _raised_curvature_forms(
    weyl: Sequence[Fraction],
    schouten: Sequence[Fraction],
    *,
    sector: str,
) -> CurvatureForms:
    forms = {}
    for a, b in PAIRS:
        components = []
        for c, d in PAIRS:
            weyl_value = _weyl_value(weyl, a, b, c, d)
            schouten_value = _schouten_curvature_value(
                schouten, a, b, c, d
            )
            lower = (
                weyl_value
                if sector == "WEYL"
                else schouten_value
                if sector == "SCHOUTEN_CURVATURE"
                else weyl_value + schouten_value
                if sector == "RIEMANN"
                else None
            )
            if lower is None:
                raise ValueError(f"unknown Euler curvature sector: {sector}")
            components.append(
                Fraction(LORENTZ_SIGNATURE[a] * LORENTZ_SIGNATURE[b]) * lower
            )
        forms[(a, b)] = tuple(components)
    return forms


def _oriented_internal_form(
    forms: CurvatureForms, left: int, right: int
) -> TwoForm:
    pair, sign = _oriented_pair(left, right)
    if pair is None:
        return (Fraction(),) * len(PAIRS)
    canonical_pair = PAIRS[pair]
    return tuple(sign * value for value in forms[canonical_pair])


def _wedge_two_forms(left: TwoForm, right: TwoForm) -> Fraction:
    coefficient = Fraction()
    for left_index, (a, b) in enumerate(PAIRS):
        for right_index, (c, d) in enumerate(PAIRS):
            coefficient += (
                left[left_index]
                * right[right_index]
                * _epsilon((a, b, c, d))
            )
    return coefficient


def _epsilon_curvature_contraction(
    left: CurvatureForms,
    right: CurvatureForms,
    *,
    orientation: int = 1,
) -> Fraction:
    return Fraction(orientation) * sum(
        Fraction(_epsilon((a, b, c, d)))
        * _wedge_two_forms(
            _oriented_internal_form(left, a, b),
            _oriented_internal_form(right, c, d),
        )
        for a, b, c, d in permutations(range(DIMENSION))
    )


def _head_values(
    weyl: Sequence[Fraction],
    schouten: Sequence[Fraction],
    *,
    carrier_orientation: int = 1,
    mixed_scale: Fraction | int = 1,
    schouten_square_scale: Fraction | int = 1,
) -> dict[str, Fraction]:
    riemann = _raised_curvature_forms(weyl, schouten, sector="RIEMANN")
    weyl_forms = _raised_curvature_forms(weyl, schouten, sector="WEYL")
    schouten_forms = _raised_curvature_forms(
        weyl, schouten, sector="SCHOUTEN_CURVATURE"
    )
    direct = _epsilon_curvature_contraction(riemann, riemann)
    ww = _epsilon_curvature_contraction(
        weyl_forms, weyl_forms, orientation=carrier_orientation
    )
    wg = _epsilon_curvature_contraction(
        weyl_forms, schouten_forms, orientation=carrier_orientation
    )
    gw = _epsilon_curvature_contraction(
        schouten_forms, weyl_forms, orientation=carrier_orientation
    )
    gg = _epsilon_curvature_contraction(
        schouten_forms, schouten_forms, orientation=carrier_orientation
    )
    carrier = (
        ww
        + Fraction(mixed_scale) * (wg + gw)
        + Fraction(schouten_square_scale) * gg
    )
    return {
        "direct_E4": direct,
        "W_squared": ww,
        "four_WX": wg + gw,
        "four_X_squared": gg,
        "carrier_E4": carrier,
        "residual": direct - carrier,
    }


def _basis_sums(
    basis: Sequence[Sequence[Fraction]],
) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(
        tuple(left + right for left, right in zip(basis[i], basis[j]))
        for i in range(len(basis))
        for j in range(i, len(basis))
    )


def _build_analysis() -> dict[str, object]:
    weyl_basis = _lorentz_weyl_basis()
    schouten_basis = tuple(
        tuple(
            Fraction(index == basis_index)
            for index in range(len(SYMMETRIC_PAIRS))
        )
        for basis_index in range(len(SYMMETRIC_PAIRS))
    )
    zero_weyl = (Fraction(),) * len(WEYL_COORDINATES)
    zero_schouten = (Fraction(),) * len(SYMMETRIC_PAIRS)

    cases: list[tuple[str, tuple[Fraction, ...], tuple[Fraction, ...]]] = []
    cases.extend(
        ("WEYL_QUADRATIC", vector, zero_schouten)
        for vector in _basis_sums(weyl_basis)
    )
    cases.extend(
        ("SCHOUTEN_QUADRATIC", zero_weyl, vector)
        for vector in _basis_sums(schouten_basis)
    )
    cases.extend(
        ("WEYL_SCHOUTEN", weyl, schouten)
        for weyl in weyl_basis
        for schouten in schouten_basis
    )

    values = [_head_values(weyl, schouten) for _, weyl, schouten in cases]
    residual_count = sum(bool(row["residual"]) for row in values)
    if residual_count:
        raise AssertionError("epsilon-contracted Euler head reconstruction failed")

    orientation_controls = [
        _head_values(weyl, schouten, carrier_orientation=-1)
        for _, weyl, schouten in cases
    ]
    orientation_failure_count = sum(
        bool(row["residual"]) for row in orientation_controls
    )
    mixed_controls = [
        _head_values(weyl, schouten, mixed_scale=Fraction(5, 4))
        for sector, weyl, schouten in cases
        if sector == "WEYL_SCHOUTEN"
    ]
    mixed_failure_count = sum(bool(row["residual"]) for row in mixed_controls)
    schouten_square_controls = [
        _head_values(
            weyl,
            schouten,
            schouten_square_scale=Fraction(5, 4),
        )
        for sector, weyl, schouten in cases
        if sector == "SCHOUTEN_QUADRATIC"
    ]
    schouten_square_failure_count = sum(
        bool(row["residual"]) for row in schouten_square_controls
    )
    if not orientation_failure_count:
        raise AssertionError("Euler orientation negative control was insensitive")
    if mixed_failure_count:
        raise AssertionError("Weyl--Schouten epsilon cross term stopped vanishing")
    if not schouten_square_failure_count:
        raise AssertionError("Euler Schouten-square negative control was insensitive")

    sector_counts = {
        sector: sum(case_sector == sector for case_sector, _, _ in cases)
        for sector in ("WEYL_QUADRATIC", "SCHOUTEN_QUADRATIC", "WEYL_SCHOUTEN")
    }
    value_payload = [
        {
            "sector": sector,
            "direct_E4": {
                "numerator": row["direct_E4"].numerator,
                "denominator": row["direct_E4"].denominator,
            },
            "carrier_E4": {
                "numerator": row["carrier_E4"].numerator,
                "denominator": row["carrier_E4"].denominator,
            },
        }
        for (sector, _, _), row in zip(cases, values)
    ]
    payload = {
        "result_id": "EULER_EPSILON_HEAD_RECONSTRUCTION",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "arithmetic": "EXACT_RATIONAL",
        "spacetime_dimension": DIMENSION,
        "signature": "LORENTZIAN_MINUS_PLUS_PLUS_PLUS",
        "metric_diagonal": list(LORENTZ_SIGNATURE),
        "orientation": "epsilon_0123 = +1; dx0 wedge dx1 wedge dx2 wedge dx3 positive",
        "hodge_convention": "epsilon_abcd epsilon^cdef = -2 delta_ab^ef",
        "direct_head": "epsilon_abcd R^ab wedge R^cd",
        "carrier_head": "epsilon_abcd (W^ab W^cd + 4 W^ab X^cd + 4 X^ab X^cd)",
        "schouten_carrier": "2 X_ab = (g wedge P)_ab",
        "weyl_coordinate_dimension": len(WEYL_COORDINATES),
        "weyl_constraint_rank": exact_rank(_lorentz_weyl_constraints()),
        "weyl_basis_dimension": len(weyl_basis),
        "schouten_basis_dimension": len(schouten_basis),
        "case_counts": sector_counts,
        "verified_case_count": len(cases),
        "nonzero_residual_count": residual_count,
        "case_value_sha256": canonical_sha256(value_payload),
        "negative_controls": {
            "reverse_carrier_orientation": {
                "failing_case_count": orientation_failure_count,
                "status": "EXPECTED_FAILURE_OBSERVED",
            },
            "mixed_4WX_coefficient_times_5_over_4": {
                "failing_case_count": mixed_failure_count,
                "status": "INSENSITIVE_BY_WEYL_TRACEFREENESS",
            },
            "4X2_coefficient_times_5_over_4": {
                "failing_case_count": schouten_square_failure_count,
                "status": "EXPECTED_FAILURE_OBSERVED",
            },
        },
        "checks": {
            "Lorentz_signature_used": "VERIFIED",
            "frozen_orientation_used": "VERIFIED",
            "Weyl_rank_nullity": "VERIFIED_21_MINUS_11_EQUALS_10",
            "direct_RR_equals_W2_plus_4WX_plus_4X2": "VERIFIED",
            "orientation_sensitivity": "VERIFIED",
            "mixed_WX_sector": "STRUCTURALLY_ZERO_BY_WEYL_TRACEFREENESS",
            "Schouten_square_coefficient_sensitivity": "VERIFIED",
        },
        "claim_boundary": {
            "Euler_head_tensor_reconstruction": "VERIFIED",
            "intrinsic_carrier_tower_status": "COMPLETE",
            "relative_cohomology_status": "UNDECIDED",
            "full_BV_status": "BLOCKED_BY_ANTIFIELD_EXPORT",
            "Berger_clock_dependency": "NONE_UNTIL_A_SEPARATE_BACKGROUND_IMPORT_IS_FROZEN",
        },
    }
    return {**payload, "reconstruction_sha256": canonical_sha256(payload)}


@lru_cache(maxsize=1)
def _cached_analysis_json() -> str:
    return json.dumps(_build_analysis(), sort_keys=True, separators=(",", ":"))


def euler_head_reconstruction_analysis() -> dict[str, object]:
    """Return a fresh copy of the cached exact head reconstruction."""

    return json.loads(_cached_analysis_json())
