"""Exact Schouten-zero image of the certified four-dimensional quotient."""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache

from .four_dimensional import four_dimensional_schouten_analysis
from .quotient import RelationQuotient, exact_nullspace, exact_rank
from .six_derivative import six_derivative_curvature_analysis
from .specialization import WEYL
from .tensors import TensorExpression, TensorMonomial
from .weyl_decomposition import (
    hodge_dualize_weyl_factor,
    riemann_to_schouten_zero_weyl,
)


def _deduplicate(
    expressions: list[TensorExpression],
) -> tuple[TensorExpression, ...]:
    unique = {
        expression.canonical_hash(): expression
        for expression in expressions
        if expression
    }
    return tuple(unique[digest] for digest in sorted(unique))


def _matrix_columns_to_rows(
    columns: list[tuple[Fraction, ...]], row_count: int
) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(
        tuple(column[row] for column in columns) for row in range(row_count)
    )


def _source_kernel_expressions(
    source: RelationQuotient,
    kernel: tuple[tuple[Fraction, ...], ...],
) -> tuple[TensorExpression, ...]:
    return tuple(
        TensorExpression(
            {
                source.basis[column]: coefficient
                for column, coefficient in zip(source.free_columns, vector)
                if coefficient
            }
        )
        for vector in kernel
    )


@lru_cache(maxsize=1)
def schouten_zero_weyl_image_analysis() -> dict[str, object]:
    """Compute the induced exact map after ``P`` and all ``nabla^k P`` vanish.

    This is a restriction theorem for Schouten-flat jets.  It is deliberately
    not named the unrestricted Weyl-jet quotient: the mapped differential
    Bianchi rows also set Cotton to zero.
    """

    dimensional = four_dimensional_schouten_analysis()
    source = dimensional["tower"].current.quotient
    source_basis_images = tuple(
        riemann_to_schouten_zero_weyl(
            TensorExpression.monomial(monomial)
        )
        for monomial in source.basis
    )
    target_basis = tuple(
        sorted(
            {
                monomial
                for expression in source_basis_images
                for monomial in expression.terms
            },
            key=TensorMonomial.sort_key,
        )
    )

    mapped_families: dict[str, tuple[TensorExpression, ...]] = {}
    all_mapped: list[TensorExpression] = []
    for family in dimensional["tower"].current.families:
        mapped = _deduplicate(
            [
                riemann_to_schouten_zero_weyl(relation)
                for relation in family.relations
            ]
        )
        mapped_families[family.name] = mapped
        all_mapped.extend(mapped)
    mapped_relations = _deduplicate(all_mapped)
    target = RelationQuotient(target_basis, mapped_relations)

    source_columns = [
        target.free_coordinates(source_basis_images[column])
        for column in source.free_columns
    ]
    induced_map = _matrix_columns_to_rows(
        source_columns, target.quotient_dimension
    )
    induced_rank = exact_rank(induced_map)
    kernel = exact_nullspace(
        induced_map, column_count=source.quotient_dimension
    )
    kernel_expressions = _source_kernel_expressions(source, kernel)
    for expression in kernel_expressions:
        image = riemann_to_schouten_zero_weyl(expression)
        if any(target.free_coordinates(image)):
            raise AssertionError("induced Weyl-image kernel witness is nonzero")

    six_derivative = six_derivative_curvature_analysis()
    sector_image_ranks = {
        name: target.rank_of_classes(
            source_basis_images[source.position[monomial]]
            for monomial in basis
            if source_basis_images[source.position[monomial]]
        )
        for name, basis in six_derivative["sector_bases"].items()
    }
    sector_nonzero_ambient_images = {
        name: sum(
            bool(source_basis_images[source.position[monomial]])
            for monomial in basis
        )
        for name, basis in six_derivative["sector_bases"].items()
    }

    cumulative = []
    accumulated: list[TensorExpression] = []
    for name, relations in mapped_families.items():
        accumulated.extend(relations)
        quotient = RelationQuotient(target_basis, accumulated)
        cumulative.append(
            {
                "family": name,
                "mapped_relation_count": len(relations),
                "cumulative_relation_rank": quotient.relation_rank,
                "cumulative_quotient_dimension": quotient.quotient_dimension,
            }
        )

    if target.quotient_dimension != 1:
        raise AssertionError("Schouten-zero Weyl image dimension drifted")
    representative = target.basis[target.free_columns[0]]
    weyl_factor = next(
        index
        for index, factor in enumerate(representative.factors)
        if factor.spec == WEYL
    )
    odd_companion = hodge_dualize_weyl_factor(
        representative, weyl_factor
    )
    if not odd_companion or {
        monomial.spacetime_parity() for monomial in odd_companion.terms
    } != {1}:
        raise AssertionError("odd Hodge companion was not constructed")

    return {
        "source_quotient": source,
        "target_quotient": target,
        "source_basis_images": source_basis_images,
        "mapped_families": mapped_families,
        "mapped_relations": mapped_relations,
        "source_dimension": source.quotient_dimension,
        "target_ambient_dimension": len(target_basis),
        "target_relation_rank": target.relation_rank,
        "target_dimension": target.quotient_dimension,
        "induced_map": induced_map,
        "induced_map_rank": induced_rank,
        "kernel": kernel,
        "kernel_dimension": len(kernel),
        "kernel_expressions": kernel_expressions,
        "sector_image_ranks": sector_image_ranks,
        "sector_nonzero_ambient_images": sector_nonzero_ambient_images,
        "mapped_relation_count": len(mapped_relations),
        "cumulative_reduction": tuple(cumulative),
        "representative": representative,
        "odd_companion": odd_companion,
    }
