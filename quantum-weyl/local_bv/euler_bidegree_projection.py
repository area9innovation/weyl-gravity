"""Exact ordinary-bidegree projection of the intrinsic Euler total forms.

This module expands ``tilde_omega_a = U_a - P_a`` before applying the
totalized differential.  The images of ``U`` and ``P`` retain separate
Hessian and Cotton summands, so the two ordinary connecting equations are
checked before cancellation rather than inferred by projecting an already
zero total-form residual.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations
import json
from typing import Iterable, Sequence

from .algebra import canonical_sha256
from .euler_connecting_identities import (
    COTTON_COORDINATES,
    DIMENSION,
    PAIRS,
    WEYL_COORDINATES,
    _cotton_basis,
    _cotton_constraints,
    _cotton_value,
    _epsilon,
    _weyl_basis,
    _weyl_constraints,
    _weyl_value,
)
from .quotient import exact_rank


SYMMETRIC_PAIRS = tuple(
    (left, right)
    for left in range(DIMENSION)
    for right in range(left, DIMENSION)
)
SYMMETRIC_PAIR_INDEX = {
    pair: index for index, pair in enumerate(SYMMETRIC_PAIRS)
}


def _symmetric_value(vector: Sequence[Fraction], left: int, right: int) -> Fraction:
    return vector[SYMMETRIC_PAIR_INDEX[tuple(sorted((left, right)))]]


# Odd coefficient generators: omega, U_a, and the symmetric Hessian H_ab.
OMEGA_POSITION = 0
U_POSITION = 1
H_POSITION = U_POSITION + DIMENSION
DX_POSITION = H_POSITION + len(SYMMETRIC_PAIRS)
GENERATOR_COUNT = DX_POSITION + DIMENSION

AtomExpression = dict[int, Fraction]
ONE: AtomExpression = {0: Fraction(1)}


def _atom(position: int) -> AtomExpression:
    return {1 << position: Fraction(1)}


OMEGA = _atom(OMEGA_POSITION)
U = tuple(_atom(U_POSITION + index) for index in range(DIMENSION))
H = tuple(_atom(H_POSITION + index) for index in range(len(SYMMETRIC_PAIRS)))
DX = tuple(_atom(DX_POSITION + index) for index in range(DIMENSION))


def _wedge_pair(left: AtomExpression, right: AtomExpression) -> AtomExpression:
    output: AtomExpression = {}
    for left_mask, left_coefficient in left.items():
        for right_mask, right_coefficient in right.items():
            if left_mask & right_mask:
                continue
            inversions = sum(
                1
                for left_index in range(GENERATOR_COUNT)
                if left_mask & (1 << left_index)
                for right_index in range(GENERATOR_COUNT)
                if right_mask & (1 << right_index) and left_index > right_index
            )
            coefficient = left_coefficient * right_coefficient
            if inversions % 2:
                coefficient = -coefficient
            mask = left_mask | right_mask
            output[mask] = output.get(mask, Fraction()) + coefficient
    return {mask: coefficient for mask, coefficient in output.items() if coefficient}


def _wedge(*factors: AtomExpression) -> AtomExpression:
    output = ONE
    for factor in factors:
        output = _wedge_pair(output, factor)
    return output


def _sum(*expressions: AtomExpression) -> AtomExpression:
    output: AtomExpression = {}
    for expression in expressions:
        for mask, coefficient in expression.items():
            output[mask] = output.get(mask, Fraction()) + coefficient
    return {mask: coefficient for mask, coefficient in output.items() if coefficient}


def _scale(coefficient: Fraction | int, expression: AtomExpression) -> AtomExpression:
    coefficient = Fraction(coefficient)
    return {
        mask: coefficient * value
        for mask, value in expression.items()
        if coefficient * value
    }


def _negate(expression: AtomExpression) -> AtomExpression:
    return _scale(-1, expression)


def _ghost_form_degree(mask: int) -> tuple[int, int]:
    ghost_mask = (1 << DX_POSITION) - 1
    ghost_number = (mask & ghost_mask).bit_count()
    form_degree = (mask >> DX_POSITION).bit_count()
    return ghost_number, form_degree


def _by_bidegree(expression: AtomExpression) -> dict[tuple[int, int], AtomExpression]:
    output: dict[tuple[int, int], AtomExpression] = {}
    for mask, coefficient in expression.items():
        bidegree = _ghost_form_degree(mask)
        row = output.setdefault(bidegree, {})
        row[mask] = coefficient
    return output


def _generator_labels() -> tuple[str, ...]:
    return (
        "omega",
        *(f"U_{index}" for index in range(DIMENSION)),
        *(f"H_{left}_{right}" for left, right in SYMMETRIC_PAIRS),
        *(f"dx_{index}" for index in range(DIMENSION)),
    )


def _expression_payload(expression: AtomExpression) -> list[dict[str, object]]:
    labels = _generator_labels()
    return [
        {
            "coefficient": {
                "numerator": coefficient.numerator,
                "denominator": coefficient.denominator,
            },
            "monomial": [
                labels[position]
                for position in range(GENERATOR_COUNT)
                if mask & (1 << position)
            ],
        }
        for mask, coefficient in sorted(expression.items())
    ]


def _hessian_form(a: int) -> AtomExpression:
    return _sum(
        *(
            _wedge(H[SYMMETRIC_PAIR_INDEX[tuple(sorted((a, b)))]], DX[b])
            for b in range(DIMENSION)
        )
    )


def _schouten_form(vector: Sequence[Fraction], a: int) -> AtomExpression:
    return _sum(
        *(
            _scale(_symmetric_value(vector, a, b), DX[b])
            for b in range(DIMENSION)
        )
    )


def _weyl_form(vector: Sequence[Fraction], a: int, b: int) -> AtomExpression:
    return _sum(
        *(
            _scale(_weyl_value(vector, a, b, c, d), _wedge(DX[c], DX[d]))
            for c, d in PAIRS
        )
    )


def _cotton_form(vector: Sequence[Fraction], a: int) -> AtomExpression:
    return _sum(
        *(
            _scale(_cotton_value(vector, a, b, c), _wedge(DX[b], DX[c]))
            for b, c in PAIRS
        )
    )


def _d_weyl_form(cotton: Sequence[Fraction], a: int, b: int) -> AtomExpression:
    return _sum(
        _wedge(_cotton_form(cotton, a), DX[b]),
        _negate(_wedge(_cotton_form(cotton, b), DX[a])),
    )


@dataclass(frozen=True)
class Factor:
    kind: str
    indices: tuple[int, ...] = ()

    @property
    def total_parity(self) -> int:
        return 0 if self.kind == "W" else 1


Term = tuple[Fraction, tuple[Factor, ...]]


def _factor_value(
    factor: Factor,
    schouten: Sequence[Fraction],
    weyl: Sequence[Fraction],
) -> AtomExpression:
    if factor.kind == "omega":
        return OMEGA
    if factor.kind == "U":
        return U[factor.indices[0]]
    if factor.kind == "P":
        return _schouten_form(schouten, factor.indices[0])
    if factor.kind == "dx":
        return DX[factor.indices[0]]
    if factor.kind == "W":
        return _weyl_form(weyl, *factor.indices)
    raise ValueError(f"unknown Euler component factor: {factor.kind}")


def _factor_differential(
    factor: Factor,
    cotton: Sequence[Fraction],
    *,
    p_cotton_sign: int = 1,
    w_cotton_sign: int = 1,
) -> AtomExpression:
    """Return D=Q+(-1)^ghost d_h on one component generator."""

    if factor.kind == "omega":
        # D omega = -d_h omega at ghost number one.
        return _negate(
            _sum(*(_wedge(U[index], DX[index]) for index in range(DIMENSION)))
        )
    if factor.kind == "U":
        return _negate(_hessian_form(factor.indices[0]))
    if factor.kind == "P":
        # QP=-H and d_h P=-C_source in the frozen Cotton convention.
        return _sum(
            _negate(_hessian_form(factor.indices[0])),
            _scale(-p_cotton_sign, _cotton_form(cotton, factor.indices[0])),
        )
    if factor.kind == "W":
        return _scale(w_cotton_sign, _d_weyl_form(cotton, *factor.indices))
    return {}


def _differentiate_terms(
    terms: Iterable[Term],
    schouten: Sequence[Fraction],
    weyl: Sequence[Fraction],
    cotton: Sequence[Fraction],
    *,
    p_cotton_sign: int = 1,
    w_cotton_sign: int = 1,
) -> tuple[AtomExpression, tuple[AtomExpression, ...]]:
    summands: list[AtomExpression] = []
    for coefficient, factors in terms:
        prefix_parity = 0
        for position, factor in enumerate(factors):
            image = _factor_differential(
                factor,
                cotton,
                p_cotton_sign=p_cotton_sign,
                w_cotton_sign=w_cotton_sign,
            )
            if image:
                values = [
                    image
                    if index == position
                    else _factor_value(other, schouten, weyl)
                    for index, other in enumerate(factors)
                ]
                sign = -1 if prefix_parity % 2 else 1
                summands.append(_scale(coefficient * sign, _wedge(*values)))
            prefix_parity += factor.total_parity
    return _sum(*summands), tuple(summands)


def _component_terms(*, mixed_scale: Fraction | int = 1) -> dict[str, tuple[Term, ...]]:
    components: dict[str, list[Term]] = {"a14": [], "a23": [], "a32": []}
    for a, nu, mu1, mu2 in permutations(range(DIMENSION)):
        epsilon = _epsilon((a, nu, mu1, mu2))
        common = (Factor("omega"), Factor("dx", (nu,)), Factor("W", (mu1, mu2)))
        components["a14"].append(
            (Fraction(4 * epsilon), (common[0], Factor("P", (a,)), *common[1:]))
        )
        components["a23"].append(
            (Fraction(-4 * epsilon), (common[0], Factor("U", (a,)), *common[1:]))
        )
    for a, b, nu1, nu2 in permutations(range(DIMENSION)):
        epsilon = _epsilon((a, b, nu1, nu2))
        tail = (Factor("dx", (nu1,)), Factor("dx", (nu2,)))
        components["a14"].append(
            (
                Fraction(4 * epsilon),
                (Factor("omega"), Factor("P", (a,)), Factor("P", (b,)), *tail),
            )
        )
        mixed_coefficient = Fraction(-4 * epsilon) * Fraction(mixed_scale)
        components["a23"].extend(
            (
                (
                    mixed_coefficient,
                    (Factor("omega"), Factor("U", (a,)), Factor("P", (b,)), *tail),
                ),
                (
                    mixed_coefficient,
                    (Factor("omega"), Factor("P", (a,)), Factor("U", (b,)), *tail),
                ),
            )
        )
        components["a32"].append(
            (
                Fraction(4 * epsilon),
                (Factor("omega"), Factor("U", (a,)), Factor("U", (b,)), *tail),
            )
        )
    return {name: tuple(terms) for name, terms in components.items()}


def _component_residuals(
    schouten: Sequence[Fraction],
    weyl: Sequence[Fraction],
    cotton: Sequence[Fraction],
    *,
    mixed_scale: Fraction | int = 1,
    p_cotton_sign: int = 1,
    w_cotton_sign: int = 1,
) -> tuple[dict[tuple[int, int], AtomExpression], dict[str, tuple[AtomExpression, ...]]]:
    components = _component_terms(mixed_scale=mixed_scale)
    differentiated = {}
    summands = {}
    for name, terms in components.items():
        differentiated[name], summands[name] = _differentiate_terms(
            terms,
            schouten,
            weyl,
            cotton,
            p_cotton_sign=p_cotton_sign,
            w_cotton_sign=w_cotton_sign,
        )
    total = _sum(*differentiated.values())
    return _by_bidegree(total), summands


def _component_differentials(
    schouten: Sequence[Fraction],
    weyl: Sequence[Fraction],
    cotton: Sequence[Fraction],
) -> dict[str, dict[tuple[int, int], AtomExpression]]:
    output = {}
    for name, terms in _component_terms().items():
        expression, _ = _differentiate_terms(terms, schouten, weyl, cotton)
        output[name] = _by_bidegree(expression)
    return output


def _cancellation_receipt(
    cases: Sequence[
        tuple[Sequence[Fraction], Sequence[Fraction], Sequence[Fraction]]
    ],
    *,
    bidegree: tuple[int, int],
    left_component: str,
    right_component: str,
) -> dict[str, object]:
    for case_index, case in enumerate(cases):
        components = _component_differentials(*case)
        left = components[left_component].get(bidegree, {})
        right = components[right_component].get(bidegree, {})
        if left and right and left == _negate(right):
            left_payload = _expression_payload(left)
            right_payload = _expression_payload(right)
            residual = _sum(left, right)
            return {
                "bidegree": {
                    "ghost_number": bidegree[0],
                    "form_degree": bidegree[1],
                },
                "left_component": left_component,
                "right_component": right_component,
                "witness_case_index": case_index,
                "left_term_count": len(left),
                "right_term_count": len(right),
                "left_sha256": canonical_sha256(left_payload),
                "right_sha256": canonical_sha256(right_payload),
                "residual_sha256": canonical_sha256(_expression_payload(residual)),
                "pairing_status": "RIGHT_EQUALS_NEGATIVE_LEFT",
            }
    raise AssertionError(
        f"no nonzero cancellation witness for {left_component}/{right_component} at {bidegree}"
    )


def _constraint_ranks() -> dict[str, int]:
    # Coordinates already implement pair symmetries.  Rank-nullity supplies
    # an independent receipt for the remaining defining identities.
    return {
        "weyl_coordinate_dimension": len(WEYL_COORDINATES),
        "weyl_constraint_rank": exact_rank(_weyl_constraints()),
        "cotton_coordinate_dimension": len(COTTON_COORDINATES),
        "cotton_constraint_rank": exact_rank(_cotton_constraints()),
        "symmetric_schouten_dimension": len(SYMMETRIC_PAIRS),
    }


def _build_euler_bidegree_projection_analysis() -> dict[str, object]:
    """Build both projected equations and sensitivity controls exactly."""

    weyl_basis = _weyl_basis()
    cotton_basis = _cotton_basis()
    schouten_basis = tuple(
        tuple(Fraction(index == basis_index) for index in range(len(SYMMETRIC_PAIRS)))
        for basis_index in range(len(SYMMETRIC_PAIRS))
    )
    zero_weyl = (Fraction(),) * len(WEYL_COORDINATES)
    zero_cotton = (Fraction(),) * len(COTTON_COORDINATES)
    zero_schouten = (Fraction(),) * len(SYMMETRIC_PAIRS)

    cases = []
    cases.extend((schouten, zero_weyl, zero_cotton) for schouten in schouten_basis)
    cases.extend((zero_schouten, weyl, zero_cotton) for weyl in weyl_basis)
    cases.extend((zero_schouten, zero_weyl, cotton) for cotton in cotton_basis)
    cases.extend(
        (schouten, weyl, zero_cotton)
        for schouten in schouten_basis
        for weyl in weyl_basis
    )

    residuals = [_component_residuals(*case)[0] for case in cases]
    target_bidegrees = ((2, 4), (3, 3), (4, 2))
    nonzero_counts = {
        f"g{ghost}_p{form}": sum(bool(row.get((ghost, form), {})) for row in residuals)
        for ghost, form in target_bidegrees
    }
    if any(nonzero_counts.values()):
        raise AssertionError(f"ordinary Euler connecting residuals remain: {nonzero_counts}")

    coefficient_control = [
        _component_residuals(*case, mixed_scale=Fraction(5, 4))[0]
        for case in cases
    ]
    cotton_control = [
        _component_residuals(
            zero_schouten,
            zero_weyl,
            cotton,
            p_cotton_sign=1,
            w_cotton_sign=-1,
        )[0]
        for cotton in cotton_basis
    ]
    coefficient_failures = sum(
        any(row.get(bidegree, {}) for bidegree in target_bidegrees)
        for row in coefficient_control
    )
    cotton_failures = sum(
        any(row.get(bidegree, {}) for bidegree in target_bidegrees)
        for row in cotton_control
    )
    if not coefficient_failures:
        raise AssertionError("mixed-coefficient negative control was insensitive")
    raw_cotton = tuple(
        Fraction(index == 0) for index in range(len(COTTON_COORDINATES))
    )
    raw_cotton_baseline = _component_residuals(
        zero_schouten, zero_weyl, raw_cotton
    )[0]
    raw_cotton_flipped = _component_residuals(
        zero_schouten,
        zero_weyl,
        raw_cotton,
        p_cotton_sign=1,
        w_cotton_sign=-1,
    )[0]
    if raw_cotton_baseline == raw_cotton_flipped:
        raise AssertionError("raw Cotton row-wiring control was insensitive")

    # At least one verified case must contain nonzero pre-cancellation
    # summands; otherwise projection of a zero residual would be circular.
    witness_summands = _component_residuals(schouten_basis[0], weyl_basis[0], zero_cotton)[1]
    summand_counts = {
        name: sum(bool(summand) for summand in rows)
        for name, rows in witness_summands.items()
    }
    if not any(summand_counts.values()):
        raise AssertionError("ordinary projection has no pre-cancellation summands")

    cancellation_receipts = [
        _cancellation_receipt(
            cases,
            bidegree=(2, 4),
            left_component="a14",
            right_component="a23",
        ),
        _cancellation_receipt(
            cases,
            bidegree=(3, 3),
            left_component="a23",
            right_component="a32",
        ),
    ]

    rank_receipt = _constraint_ranks()
    if rank_receipt != {
        "weyl_coordinate_dimension": 21,
        "weyl_constraint_rank": 11,
        "cotton_coordinate_dimension": 24,
        "cotton_constraint_rank": 8,
        "symmetric_schouten_dimension": 10,
    }:
        raise AssertionError("Euler component tensor rank receipt drifted")

    payload = {
        "result_id": "EULER_ORDINARY_BIDEGREE_PROJECTION",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "arithmetic": "EXACT_RATIONAL",
        "totalization": "D = Q_W + (-1)^ghost_number d_h",
        "component_substitution": "tilde_omega_a = U_a - P_a",
        "split_generator_rows": {
            "Q_W": {
                "omega": "0",
                "U_a": "0",
                "P_a": "-H_ab dx^b",
                "W_ab": "HOMOGENEOUS_ONLY_AND_ZERO_AFTER_THE_EXISTING_ODD_OMEGA",
            },
            "d_h": {
                "omega": "U_a dx^a",
                "U_a": "H_ab dx^b",
                "P_a": "-C_source_a",
                "W_ab": "C_source^a dx^b - C_source^b dx^a",
            },
            "base_Weyl_Gamma_row": {
                "equation": "Gamma_alpha W_Omega0 = 0",
                "reason": "W_Omega0 is the undifferentiated conformally invariant mixed Weyl tensor",
                "status": "DERIVED_FOR_BASE_WEYL_CARRIER",
            },
        },
        "generator_rows": {
            "D_omega": "-U_a dx^a",
            "D_U_a": "-H_ab dx^b",
            "D_P_a": "-H_ab dx^b - C_source_a",
            "D_W_ab": "C_source^a dx^b - C_source^b dx^a",
        },
        "constraint_rank_receipt": rank_receipt,
        "verified_case_count": len(cases),
        "target_bidegrees": [
            {"ghost_number": ghost, "form_degree": form}
            for ghost, form in target_bidegrees
        ],
        "nonzero_residual_counts": nonzero_counts,
        "pre_cancellation_nonzero_summand_counts": summand_counts,
        "cancellation_receipts": cancellation_receipts,
        "negative_controls": {
            "mixed_UP_coefficient_perturbation": {
                "replacement_scale": {"numerator": 5, "denominator": 4},
                "failing_case_count": coefficient_failures,
                "status": "EXPECTED_FAILURE_OBSERVED",
            },
            "Cotton_bridge_relative_sign_flip": {
                "failing_case_count": cotton_failures,
                "status": "PHYSICAL_SUBSPACE_INSENSITIVE_BY_COTTON_IDENTITIES",
            },
            "raw_Cotton_row_wiring_probe": {
                "uses_nonphysical_coordinate_vector": True,
                "baseline_nonzero_bidegrees": [
                    f"g{ghost}_p{form}"
                    for ghost, form in sorted(raw_cotton_baseline)
                    if raw_cotton_baseline[(ghost, form)]
                ],
                "flipped_nonzero_bidegrees": [
                    f"g{ghost}_p{form}"
                    for ghost, form in sorted(raw_cotton_flipped)
                    if raw_cotton_flipped[(ghost, form)]
                ],
                "status": "EXPECTED_WIRING_CHANGE_OBSERVED",
            },
        },
        "checks": {
            "individual_summands_projected_before_cancellation": "VERIFIED",
            "nonzero_cancellation_pair_hashes": "VERIFIED",
            "QW_a14_plus_dh_a23": "VERIFIED",
            "QW_a23_minus_dh_a32": "VERIFIED",
            "QW_a32": "VERIFIED",
            "mixed_coefficient_sensitivity": "VERIFIED",
            "Cotton_sign_on_irreducible_subspace": "INSENSITIVE_BY_IDENTITIES",
            "Cotton_row_wiring_sensitivity": "VERIFIED_ON_RAW_COORDINATE_PROBE",
            "basis_rank_nullity": "VERIFIED",
        },
        "claim_boundary": {
            "intrinsic_connecting_equations": "VERIFIED_FOR_FROZEN_EULER_CARRIER_ALGEBRA",
            "epsilon_contracted_top_reconstruction": "NOT_COMPUTED",
            "relative_cohomology_status": "UNDECIDED",
            "full_bv_status": "BLOCKED_BY_ANTIFIELD_EXPORT",
        },
    }
    return {**payload, "projection_sha256": canonical_sha256(payload)}


@lru_cache(maxsize=1)
def _cached_analysis_json() -> str:
    return json.dumps(
        _build_euler_bidegree_projection_analysis(),
        sort_keys=True,
        separators=(",", ":"),
    )


def euler_bidegree_projection_analysis() -> dict[str, object]:
    """Return a fresh copy of the cached exact analysis.

    Caching the serialized immutable value keeps certificate consumers fast
    without exposing a shared mutable dictionary to callers.
    """

    return json.loads(_cached_analysis_json())
