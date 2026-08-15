#!/usr/bin/env python3
"""Independent exact semantics for the classical pure-Weyl minimal-BV q3 AST.

The parameter algebra is the square-free ring
``Q[a,b,c]/(a^2,b^2,c^2)``.  A three-input evaluation therefore extracts
the coefficient of ``a*b*c`` in one geometry pass; no polarization by
floating point or finite differences is used.  Coordinate Taylor jets are
still exact :class:`fractions.Fraction` values.
"""

from __future__ import annotations

from contextlib import contextmanager
from fractions import Fraction
from itertools import product
from typing import Iterable, Iterator, Mapping, Sequence

try:
    from . import bach_natural_operator_ast as quadratic
    from . import cylinder_polarized_bach_evaluator as point
except ImportError:  # direct path execution
    import bach_natural_operator_ast as quadratic
    import cylinder_polarized_bach_evaluator as point


DIMENSION = 4
FULL_MASK = 0b111
CoordinateJet = Mapping[tuple[int, int, int, int], Fraction | int]
MetricJets = Mapping[tuple[int, int], CoordinateJet]


class CubicNaturalOperatorError(ValueError):
    """Raised when the imported classical q3 AST is not executable."""


class TrivariateJet(point.Jet):
    """Coordinate jet over three independent square-free parameters.

    The inherited first parameter-degree slot stores a three-bit mask and the
    inherited second slot is fixed to zero.  This keeps every tensor routine
    in the independently established exact point evaluator reusable while
    changing only the coefficient algebra.
    """

    @staticmethod
    def from_terms(
        order: int,
        terms: Iterable[tuple[int, int, Sequence[int], Fraction | int]],
    ) -> "TrivariateJet":
        if order < 0:
            return TrivariateJet(-1)
        combined: dict[tuple[int, int, tuple[int, int, int, int]], Fraction] = {}
        for mask, dummy, alpha, coefficient in terms:
            alpha = tuple(int(item) for item in alpha)
            if len(alpha) != DIMENSION or min(alpha) < 0:
                raise ValueError("coordinate multiindex must contain four nonnegative entries")
            if not isinstance(mask, int) or not 0 <= mask <= FULL_MASK or dummy != 0:
                continue
            if sum(alpha) > order:
                continue
            coefficient = coefficient if isinstance(coefficient, Fraction) else Fraction(coefficient)
            if coefficient:
                key = (mask, 0, alpha)
                combined[key] = combined.get(key, Fraction(0)) + coefficient
        return TrivariateJet(
            order,
            tuple((*key, value) for key, value in sorted(combined.items()) if value),
        )

    def __mul__(self, other: point.Jet) -> "TrivariateJet":
        order = min(self.order, other.order)
        terms = []
        for mask1, dummy1, alpha1, value1 in self.terms:
            for mask2, dummy2, alpha2, value2 in other.terms:
                if dummy1 or dummy2 or mask1 & mask2:
                    continue
                alpha = tuple(alpha1[index] + alpha2[index] for index in range(DIMENSION))
                if sum(alpha) <= order:
                    terms.append((mask1 | mask2, 0, alpha, value1 * value2))
        return TrivariateJet.from_terms(order, terms)


@contextmanager
def _trivariate_parameter_algebra() -> Iterator[None]:
    original = point.Jet
    point.Jet = TrivariateJet
    try:
        yield
    finally:
        point.Jet = original


def _convert(value: point.Jet) -> TrivariateJet:
    return TrivariateJet.from_terms(value.order, value.terms)


def _component(jets: MetricJets, pair: tuple[int, int]) -> CoordinateJet:
    return jets.get(tuple(sorted(pair)), {})


def validate_imported_ast(payload: object) -> Mapping[str, object]:
    """Validate the executable shape without regenerating the classical export."""

    if not isinstance(payload, dict):
        raise CubicNaturalOperatorError("q3 AST must be an object")
    if payload.get("schema") != "pure-weyl-minimal-bv-q3-natural-operator-ast-v1":
        raise CubicNaturalOperatorError("unsupported q3 AST schema")
    if payload.get("spacetime_dimension") != DIMENSION or payload.get("coefficient_field") != "Q":
        raise CubicNaturalOperatorError("q3 AST must be exact and four-dimensional")
    nodes = payload.get("nodes")
    if not isinstance(nodes, list) or len(nodes) != 10 or payload.get("root_node") != "q3_hstar_hhh":
        raise CubicNaturalOperatorError("q3 AST node count or root drift")
    expected = (
        "metric_three_parameter_family", "inverse_metric", "levi_civita_geometry",
        "schouten_and_weyl_4d", "cotton_4d", "bach_4d",
        "raise_symmetric_two_tensor", "absolute_metric_volume_density",
        "densitize_and_scale", "mixed_third_frechet_coefficient",
    )
    if tuple(item.get("operation") for item in nodes) != expected:
        raise CubicNaturalOperatorError("q3 AST operation inventory drift")
    seen: set[str] = set()
    for node in nodes:
        node_id = node.get("node_id")
        inputs = node.get("inputs")
        if not isinstance(node_id, str) or node_id in seen or not isinstance(inputs, list) or any(parent not in seen for parent in inputs):
            raise CubicNaturalOperatorError("q3 AST is duplicated or not topological")
        seen.add(node_id)
    root = nodes[-1]
    if root.get("node_id") != "q3_hstar_hhh" or root.get("parameters", {}).get("coefficient") != "[a*b*c]" or root.get("parameters", {}).get("hidden_factorial") is not False:
        raise CubicNaturalOperatorError("q3 Frechet extraction convention drift")
    if nodes[-2].get("parameters", {}).get("coefficient") != -2:
        raise CubicNaturalOperatorError("pure-Weyl Euler normalization drift")
    return payload


def _metric_family(
    background: Mapping[tuple[int, int], point.Jet],
    first: MetricJets,
    second: MetricJets,
    third: MetricJets,
) -> dict[tuple[int, int], TrivariateJet]:
    converted = {pair: _convert(value) for pair, value in background.items()}
    order = min(value.order for value in converted.values())
    return {
        (a, b): converted[(a, b)]
        + TrivariateJet.from_terms(order, ((1, 0, alpha, value) for alpha, value in _component(first, (a, b)).items()))
        + TrivariateJet.from_terms(order, ((2, 0, alpha, value) for alpha, value in _component(second, (a, b)).items()))
        + TrivariateJet.from_terms(order, ((4, 0, alpha, value) for alpha, value in _component(third, (a, b)).items()))
        for a, b in product(range(DIMENSION), repeat=2)
    }


def evaluate_ast(
    payload: Mapping[str, object],
    first: MetricJets,
    second: MetricJets,
    third: MetricJets,
    *,
    background: Mapping[tuple[int, int], point.Jet] | None = None,
    output_coordinate_order: int = 0,
) -> dict[tuple[int, int], dict[tuple[int, int, int, int], Fraction]]:
    """Execute the imported AST and return exact q3 output coordinate jets."""

    validate_imported_ast(payload)
    if output_coordinate_order < 0:
        raise ValueError("output coordinate order must be nonnegative")
    background = point.cylinder_background(4 + output_coordinate_order) if background is None else background
    required_background_order = 4 + output_coordinate_order
    if min(value.order for value in background.values()) < required_background_order:
        raise CubicNaturalOperatorError("background does not retain enough coordinate jets")
    # Extra coordinate jets are irrelevant to the requested local output but
    # enlarge the exact trivariate algebra combinatorially.  Truncate at the
    # mathematically sufficient fourth-order operator margin before executing.
    background = {
        pair: value.truncate(required_background_order)
        for pair, value in background.items()
    }

    with _trivariate_parameter_algebra():
        values: dict[str, object] = {}
        for node in payload["nodes"]:
            operation = node["operation"]
            inputs = [values[parent] for parent in node["inputs"]]
            if operation == "metric_three_parameter_family":
                result = _metric_family(background, first, second, third)
            elif operation == "inverse_metric":
                result = point.inverse_matrix(inputs[0])
            elif operation == "levi_civita_geometry":
                result = point._geometry(inputs[0])
                if result["inverse"] != inputs[1]:
                    raise CubicNaturalOperatorError("independent inverse nodes disagree")
            elif operation == "schouten_and_weyl_4d":
                result = point._schouten_and_weyl(inputs[0])
            elif operation == "cotton_4d":
                result = quadratic._cotton(inputs[0], inputs[1][0])
            elif operation == "bach_4d":
                result = quadratic._bach(inputs[0], inputs[1][0], inputs[1][1], inputs[2])
            elif operation == "raise_symmetric_two_tensor":
                inverse, lower = inputs
                order = min(value.order for value in lower.values())
                result = {
                    (a, b): point.sum_jets(
                        (inverse[(a, c)] * inverse[(b, d)] * lower[(c, d)] for c, d in product(range(DIMENSION), repeat=2)),
                        order=order,
                    )
                    for a, b in product(range(DIMENSION), repeat=2)
                }
            elif operation == "absolute_metric_volume_density":
                result = point.determinant(inputs[0]).scale(-1).sqrt().truncate(output_coordinate_order)
            elif operation == "densitize_and_scale":
                volume, raised = inputs
                result = {pair: volume * item.scale(-2) for pair, item in raised.items()}
            elif operation == "mixed_third_frechet_coefficient":
                result = {
                    pair: {
                        alpha: coefficient
                        for mask, dummy, alpha, coefficient in inputs[0][pair].terms
                        if mask == FULL_MASK and dummy == 0
                    }
                    for pair in point.PAIRS
                }
            else:  # protected by validation
                raise CubicNaturalOperatorError(f"unknown q3 AST operation: {operation}")
            values[node["node_id"]] = result
        root = values[payload["root_node"]]
        assert isinstance(root, dict)
        return root


def evaluate_point(
    payload: Mapping[str, object],
    first: MetricJets,
    second: MetricJets,
    third: MetricJets,
    *,
    background: Mapping[tuple[int, int], point.Jet] | None = None,
) -> dict[tuple[int, int], Fraction]:
    jets = evaluate_ast(payload, first, second, third, background=background)
    return {pair: jets[pair].get(point.ZERO_MULTIINDEX, Fraction(0)) for pair in point.PAIRS}


def transform_output_density_jets(
    values: Mapping[tuple[int, int], CoordinateJet],
    permutation: Sequence[int],
    signs: Sequence[int],
) -> dict[tuple[int, int], dict[tuple[int, int, int, int], Fraction]]:
    """Pull back a contravariant absolute weight-one density jet."""

    if sorted(permutation) != list(range(DIMENSION)) or len(signs) != DIMENSION or any(sign not in (-1, 1) for sign in signs):
        raise ValueError("expected a signed coordinate permutation")
    output: dict[tuple[int, int], dict[tuple[int, int, int, int], Fraction]] = {}
    for i, j in point.PAIRS:
        old_pair = tuple(sorted((permutation[i], permutation[j])))
        row: dict[tuple[int, int, int, int], Fraction] = {}
        for old_word, coefficient in values.get(old_pair, {}).items():
            new_word = tuple(old_word[permutation[index]] for index in range(DIMENSION))
            sign = signs[i] * signs[j]
            for axis in range(DIMENSION):
                sign *= quadratic.product_sign(signs[axis], new_word[axis])
            row[new_word] = row.get(new_word, Fraction(0)) + Fraction(coefficient) * sign
        output[(i, j)] = {word: value for word, value in row.items() if value}
    return output
