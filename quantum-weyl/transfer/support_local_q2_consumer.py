"""Independent consumer for a preflighted support-local q1/q2/D export.

The consumer validates the classical payload, parses every local expression
into the canonical AST, checks declared jet bounds, and dispatches to a
versioned evaluator.  The built-in evaluator is deliberately limited to the
identity-monomial fixture language; an unknown physical expression language
is rejected rather than guessed.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
import sys
from typing import Any


TRANSFER_ROOT = Path(__file__).resolve().parent
CLASSICAL_IMPORT_ROOT = TRANSFER_ROOT.parent / "classical_import"
for search_root in (TRANSFER_ROOT, CLASSICAL_IMPORT_ROOT):
    if str(search_root) not in sys.path:
        sys.path.insert(0, str(search_root))

try:
    from .arity_two_cartan import (
        ArityTwoComplex,
        BilinearOperator,
        LinearOperator,
    )
    from .local_expression_ast import (
        EXPRESSION_SCHEMA_VERSION,
        CanonicalExpressionComponent,
        canonical_expression_hash,
        parse_operator_components,
    )
except ImportError:  # direct script or path-loaded test execution
    from arity_two_cartan import ArityTwoComplex, BilinearOperator, LinearOperator
    from local_expression_ast import (
        EXPRESSION_SCHEMA_VERSION,
        CanonicalExpressionComponent,
        canonical_expression_hash,
        parse_operator_components,
    )

from verify_support_local_q2_export import validate_export


@dataclass(frozen=True)
class ParsedSupportLocalExport:
    classical_commit: str
    symbols: tuple[str, ...]
    ghost_numbers: tuple[int, ...]
    parities: tuple[int, ...]
    spacetime_dimension: int
    maximum_jet_order: int
    expression_schema_version: str
    q1_components: tuple[CanonicalExpressionComponent, ...]
    q2_components: tuple[CanonicalExpressionComponent, ...]
    D_components: tuple[CanonicalExpressionComponent, ...]
    canonical_expression_sha256: str


@dataclass(frozen=True)
class EvaluatedArityTwoExport:
    complex: ArityTwoComplex
    q2: BilinearOperator
    lie_D: LinearOperator
    source_commit: str
    canonical_expression_sha256: str


def _check_jet_bounds(
    components: tuple[CanonicalExpressionComponent, ...],
    *,
    maximum_jet_order: int,
) -> None:
    for component in components:
        for monomial, _coefficient in component.expression.terms:
            total = 0
            for position, multiindex in enumerate(monomial.input_jets):
                order = sum(multiindex)
                if order > component.max_jet_orders[position]:
                    raise ValueError(
                        f"{component.component_id}: expression exceeds its input jet bound"
                    )
                total += order
            if total > maximum_jet_order:
                raise ValueError(
                    f"{component.component_id}: expression exceeds the global jet bound"
                )


def parse_support_local_export(
    payload: dict[str, Any],
    *,
    repository_root: Path | None = None,
) -> ParsedSupportLocalExport:
    """Validate and canonicalize a support-local classical export."""

    validate_export(payload, repository_root=repository_root)
    version = payload["expression_schema_version"]
    if version != EXPRESSION_SCHEMA_VERSION:
        raise ValueError(f"no registered local-expression parser for {version}")
    support = payload["support_category"]
    dimension = support["spacetime_dimension"]
    q1_components = parse_operator_components(
        payload["q1"],
        spacetime_dimension=dimension,
    )
    q2_components = parse_operator_components(
        payload["q2"],
        spacetime_dimension=dimension,
    )
    D_components = parse_operator_components(
        payload["D_action"],
        spacetime_dimension=dimension,
    )
    maximum_jet_order = support["maximum_jet_order"]
    for components in (q1_components, q2_components, D_components):
        _check_jet_bounds(components, maximum_jet_order=maximum_jet_order)
    generators = payload["generators"]
    expressions = tuple(
        component.expression
        for components in (q1_components, q2_components, D_components)
        for component in components
    )
    return ParsedSupportLocalExport(
        classical_commit=payload["classical_commit"],
        symbols=tuple(generator["symbol"] for generator in generators),
        ghost_numbers=tuple(generator["ghost_number"] for generator in generators),
        parities=tuple(generator["Grassmann_parity"] for generator in generators),
        spacetime_dimension=dimension,
        maximum_jet_order=maximum_jet_order,
        expression_schema_version=version,
        q1_components=q1_components,
        q2_components=q2_components,
        D_components=D_components,
        canonical_expression_sha256=canonical_expression_hash(expressions),
    )


def _identity_coefficient(component: CanonicalExpressionComponent) -> Fraction:
    total = Fraction(0)
    for monomial, coefficient in component.expression.terms:
        if (
            monomial.operator_id != "scalar_identity"
            or any(any(order for order in multiindex) for multiindex in monomial.input_jets)
            or monomial.free_indices
            or monomial.contractions
        ):
            raise ValueError(
                f"{component.component_id}: the fixture evaluator only accepts scalar_identity"
            )
        total += coefficient
    return total


def evaluate_identity_fixture(parsed: ParsedSupportLocalExport) -> EvaluatedArityTwoExport:
    """Evaluate the registered scalar-identity fixture language exactly."""

    symbol_index = {symbol: index for index, symbol in enumerate(parsed.symbols)}
    dimension = len(parsed.symbols)
    q1_rows = [[Fraction(0) for _ in range(dimension)] for _ in range(dimension)]
    D_rows = [[Fraction(0) for _ in range(dimension)] for _ in range(dimension)]
    q2_entries = [
        [[Fraction(0) for _ in range(dimension)] for _ in range(dimension)]
        for _ in range(dimension)
    ]
    for component in parsed.q1_components:
        output = symbol_index[component.output]
        input_ = symbol_index[component.inputs[0]]
        q1_rows[output][input_] += _identity_coefficient(component)
    for component in parsed.D_components:
        output = symbol_index[component.output]
        input_ = symbol_index[component.inputs[0]]
        D_rows[output][input_] += _identity_coefficient(component)
    for component in parsed.q2_components:
        output = symbol_index[component.output]
        left = symbol_index[component.inputs[0]]
        right = symbol_index[component.inputs[1]]
        q2_entries[output][left][right] += _identity_coefficient(component)

    q1 = LinearOperator.from_rows("q1", 1, q1_rows)
    complex_ = ArityTwoComplex(parsed.ghost_numbers, parsed.parities, q1)
    q2 = BilinearOperator.from_entries("q2", 1, q2_entries)
    lie_D = LinearOperator.from_rows("L_D", 0, D_rows)
    complex_.validate_bilinear(q2)
    complex_.validate_linear(lie_D)
    if not complex_.linear_bracket(q1, q2, name="[q1,q2]").is_zero():
        raise ValueError("imported q1/q2 fail the arity-two nilpotency identity")
    return EvaluatedArityTwoExport(
        complex=complex_,
        q2=q2,
        lie_D=lie_D,
        source_commit=parsed.classical_commit,
        canonical_expression_sha256=parsed.canonical_expression_sha256,
    )
