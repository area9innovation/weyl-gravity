#!/usr/bin/env python3
"""Exact diagonal third variation of the pure-Weyl Euler density.

The established point evaluator works in ``Q[a,b]/(a^2,b^2)`` and therefore
extracts the polarized Hessian.  This receiver reuses its tensor geometry
without changing that certified implementation.  During one scoped call it
rebinds the evaluator's parameter algebra to ``Q[t]/(t^4)`` and extracts
``6 [t^3] E(g+t h)=D^3E_g(h,h,h)``.  The coordinate Taylor algebra remains
exact over :class:`fractions.Fraction`.

This is a receiver-side metric-sector witness.  It is not an authoritative
full-BV q3 export.
"""

from __future__ import annotations

from contextlib import contextmanager
from fractions import Fraction
from itertools import product
from typing import Iterable, Iterator, Mapping, Sequence

import cylinder_polarized_bach_evaluator as point


CoordinateJet = Mapping[tuple[int, int, int, int], Fraction | int]
MetricJets = Mapping[tuple[int, int], CoordinateJet]


class CubicJet(point.Jet):
    """Coordinate jet with one perturbation parameter truncated at degree 3."""

    @staticmethod
    def from_terms(
        order: int,
        terms: Iterable[tuple[int, int, Sequence[int], Fraction | int]],
    ) -> "CubicJet":
        if order < 0:
            return CubicJet(-1)
        combined: dict[
            tuple[int, int, tuple[int, int, int, int]], Fraction
        ] = {}
        for t_degree, dummy_degree, alpha, coefficient in terms:
            alpha = tuple(int(item) for item in alpha)
            if len(alpha) != point.DIMENSION or min(alpha) < 0:
                raise ValueError(
                    "coordinate multiindex must contain four nonnegative entries"
                )
            if not 0 <= t_degree <= 3 or dummy_degree != 0:
                continue
            if sum(alpha) > order:
                continue
            coefficient = (
                coefficient
                if isinstance(coefficient, Fraction)
                else Fraction(coefficient)
            )
            if coefficient:
                key = (t_degree, 0, alpha)
                combined[key] = combined.get(key, Fraction(0)) + coefficient
        return CubicJet(
            order,
            tuple((*key, value) for key, value in sorted(combined.items()) if value),
        )

    def __mul__(self, other: point.Jet) -> "CubicJet":
        order = min(self.order, other.order)
        terms = []
        for t1, dummy1, alpha1, value1 in self.terms:
            for t2, dummy2, alpha2, value2 in other.terms:
                t_degree = t1 + t2
                if t_degree > 3 or dummy1 or dummy2:
                    continue
                alpha = tuple(
                    alpha1[index] + alpha2[index]
                    for index in range(point.DIMENSION)
                )
                if sum(alpha) <= order:
                    terms.append((t_degree, 0, alpha, value1 * value2))
        return CubicJet.from_terms(order, terms)


@contextmanager
def _cubic_parameter_algebra() -> Iterator[None]:
    """Temporarily select the cubic parameter algebra used by point helpers."""

    original = point.Jet
    point.Jet = CubicJet
    try:
        yield
    finally:
        point.Jet = original


def _convert(value: point.Jet) -> CubicJet:
    return CubicJet.from_terms(value.order, value.terms)


def _component(jets: MetricJets, pair: tuple[int, int]) -> CoordinateJet:
    return jets.get(tuple(sorted(pair)), {})


def diagonal_cubic_bach_data(
    field: MetricJets,
    *,
    background: Mapping[tuple[int, int], point.Jet] | None = None,
    output_coordinate_order: int = 1,
) -> dict[str, object]:
    """Return ``q3(h,h,h)`` and its two linear Noether images.

    ``q3`` uses the repository's suspended factorial convention: it is the
    third Frechet derivative, not the raw coefficient of ``t^3``.  The
    Noether images apply the *background-linear* Diff and Weyl maps used by
    the strict minimal endpoint.
    """

    if output_coordinate_order < 1:
        raise ValueError("one output coordinate jet is required for Diff Noether")
    if background is None:
        background = point.flat_background(4 + output_coordinate_order)
    if min(value.order for value in background.values()) < 4 + output_coordinate_order:
        raise ValueError("background does not retain enough coordinate jets")

    with _cubic_parameter_algebra():
        cubic_background = {pair: _convert(value) for pair, value in background.items()}
        order = min(value.order for value in cubic_background.values())
        metric = {
            (a, b): cubic_background[(a, b)]
            + CubicJet.coordinate_series(order, _component(field, (a, b)), "a")
            for a, b in product(range(point.DIMENSION), repeat=2)
        }
        geometry = point._geometry(metric)
        inverse = geometry["inverse"]
        assert isinstance(inverse, Mapping)
        bach_action = {
            pair: value.scale(-2)
            for pair, value in point._bach_lower(geometry).items()
        }
        volume = (
            point.determinant(metric)
            .scale(-1)
            .sqrt()
            .truncate(output_coordinate_order)
        )
        density = {}
        for first, second in product(range(point.DIMENSION), repeat=2):
            density[(first, second)] = volume * point.sum_jets(
                (
                    inverse[(first, left)]
                    * inverse[(second, right)]
                    * bach_action[(left, right)]
                    for left, right in product(range(point.DIMENSION), repeat=2)
                ),
                order=output_coordinate_order,
            )

        q3 = {
            pair: [
                {
                    "multiindex": list(alpha),
                    "coefficient": str(6 * coefficient),
                }
                for t_degree, dummy, alpha, coefficient in density[pair].terms
                if t_degree == 3 and dummy == 0
            ]
            for pair in point.PAIRS
        }

        background_weyl_trace = point.sum_jets(
            (
                cubic_background[(a, b)] * density[(a, b)]
                for a, b in product(range(point.DIMENSION), repeat=2)
            ),
            order=0,
        )
        q1_weyl = 12 * background_weyl_trace.coefficient(3, 0)

        q1_diff: dict[int, Fraction] = {}
        for covector in range(point.DIMENSION):
            metric_derivative = point.sum_jets(
                (
                    density[(a, b)]
                    * cubic_background[(a, b)].derivative(covector)
                    for a, b in product(range(point.DIMENSION), repeat=2)
                ),
                order=0,
            )
            product_divergence = point.sum_jets(
                (
                    (
                        density[(a, b)]
                        * cubic_background[(covector, b)]
                    ).derivative(a)
                    for a, b in product(range(point.DIMENSION), repeat=2)
                ),
                order=0,
            )
            q1_diff[covector] = 6 * (
                metric_derivative - product_divergence.scale(2)
            ).coefficient(3, 0)

        nonlinear_trace = point.sum_jets(
            (
                metric[(a, b)] * density[(a, b)]
                for a, b in product(range(point.DIMENSION), repeat=2)
            ),
            order=0,
        ).coefficient(3, 0)

        return {
            "q3_metric_euler_density": q3,
            "q1_q3_diff_noether": {
                str(axis): str(value) for axis, value in q1_diff.items()
            },
            "q1_q3_weyl_noether": str(q1_weyl),
            "nonlinear_weyl_identity_t3": str(nonlinear_trace),
        }
