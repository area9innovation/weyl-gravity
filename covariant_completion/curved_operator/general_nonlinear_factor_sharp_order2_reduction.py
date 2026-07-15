"""Exact polynomial reduction of the sharp order-two factor constraints.

The sharp Schur gate emits 179 normalized polynomials in the 21 cubic and
93 first-order split variables.  This module computes *all affine-linear
consequences in their rational vector-space span*: it takes the exact left
kernel of the quadratic-coefficient matrix, row-reduces the resulting
affine equations, substitutes every pivot variable, and canonicalizes the
residual quadratic system.

This is stronger than merely selecting constraints which happen to be
linear as written.  It remains weaker than a full nonlinear ideal solve;
the certificate states that boundary explicitly.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import hashlib
from typing import Mapping

import sympy as sp
from sympy.polys.matrices import DomainMatrix

from .general_nonlinear_factor_sharp_order2 import (
    GeneralNonlinearFactorSharpOrderTwo,
)
from .general_nonlinear_factor_system import (
    Monomial,
    Polynomial,
    _clean_polynomial,
    _normalized_polynomial_bytes,
    _polynomial_bytes,
)


SPLIT_VARIABLE_COUNT = 114


def _normalize(polynomial: Mapping[Monomial, sp.Expr]) -> Polynomial:
    clean = _clean_polynomial(polynomial)
    if not clean:
        return {}
    first = clean[min(clean)]
    return {
        monomial: sp.cancel(coefficient / first)
        for monomial, coefficient in clean.items()
    }


def _substitute_polynomial(
    polynomial: Mapping[Monomial, sp.Expr],
    affine: tuple[Polynomial, ...],
) -> Polynomial:
    result: dict[Monomial, sp.Expr] = defaultdict(lambda: sp.Integer(0))
    for monomial, coefficient in polynomial.items():
        if not monomial:
            result[()] += coefficient
        elif len(monomial) == 1:
            for changed, value in affine[monomial[0]].items():
                result[changed] += coefficient * value
        elif len(monomial) == 2:
            for left, left_value in affine[monomial[0]].items():
                for right, right_value in affine[monomial[1]].items():
                    result[tuple(sorted(left + right))] += (
                        coefficient * left_value * right_value
                    )
        else:
            raise AssertionError("sharp order-two constraint ceased to be quadratic")
    return _clean_polynomial(result)


@dataclass(frozen=True)
class GeneralNonlinearFactorSharpOrderTwoReduction:
    input_constraint_count: int
    input_degree_classification: tuple[int, ...]
    quadratic_monomial_count: int
    quadratic_coefficient_rank: int
    affine_consequence_count: int
    affine_system_shape: tuple[int, int]
    affine_rank: int
    affine_augmented_rank: int
    affine_pivot_variables: tuple[int, ...]
    affine_free_variables: tuple[int, ...]
    affine_rref_sha256: str
    residual_constraint_count: int
    residual_unique_constraint_count: int
    residual_degree_classification: tuple[int, ...]
    residual_term_count: int
    residual_sha256: str
    residual_constant_obstruction: bool
    zero_free_assignment_solution: bool
    zero_free_assignment_nonzero_coordinates: tuple[tuple[int, str], ...]

    @staticmethod
    def build() -> "GeneralNonlinearFactorSharpOrderTwoReduction":
        gate = GeneralNonlinearFactorSharpOrderTwo.build()
        constraints = gate.projected_constraints
        if len(constraints) != 179:
            raise AssertionError("sharp projected constraint input drifted")

        degree_classification = tuple(
            sum(max(map(len, polynomial), default=0) == degree for polynomial in constraints)
            for degree in range(3)
        )
        quadratic_monomials = tuple(
            sorted(
                {
                    monomial
                    for polynomial in constraints
                    for monomial in polynomial
                    if len(monomial) == 2
                }
            )
        )
        quadratic_index = {
            monomial: column for column, monomial in enumerate(quadratic_monomials)
        }
        quadratic_entries = {
            (row, quadratic_index[monomial]): coefficient
            for row, polynomial in enumerate(constraints)
            for monomial, coefficient in polynomial.items()
            if len(monomial) == 2
        }
        quadratic = sp.SparseMatrix(
            len(constraints), len(quadratic_monomials), quadratic_entries
        )
        quadratic_rank = DomainMatrix.from_Matrix(quadratic).rank()
        left_kernel = (
            DomainMatrix.from_Matrix(quadratic.T).nullspace().to_Matrix().T
        )
        if left_kernel.shape[0] != len(constraints):
            raise AssertionError("quadratic left-kernel orientation drifted")

        affine_entries = {}
        for row, polynomial in enumerate(constraints):
            affine_entries[(row, SPLIT_VARIABLE_COUNT)] = polynomial.get((), 0)
            for variable in range(SPLIT_VARIABLE_COUNT):
                value = polynomial.get((variable,), 0)
                if value != 0:
                    affine_entries[(row, variable)] = value
        affine_parts = sp.SparseMatrix(
            len(constraints), SPLIT_VARIABLE_COUNT + 1, affine_entries
        )
        consequences = sp.Matrix(left_kernel.T * affine_parts).applyfunc(sp.expand)
        # Remove zero consequences before rank and RREF calculations.
        nonzero_rows = tuple(
            row
            for row in range(consequences.rows)
            if consequences[row, :] != sp.zeros(1, consequences.cols)
        )
        affine_system = consequences[list(nonzero_rows), :] if nonzero_rows else sp.zeros(0, SPLIT_VARIABLE_COUNT + 1)
        coefficients = affine_system[:, :SPLIT_VARIABLE_COUNT]
        rhs = -affine_system[:, SPLIT_VARIABLE_COUNT:]
        coefficient_rank = DomainMatrix.from_Matrix(coefficients).rank()
        augmented_rank = DomainMatrix.from_Matrix(coefficients.row_join(rhs)).rank()

        pivot_variables: tuple[int, ...] = ()
        free_variables: tuple[int, ...] = tuple(range(SPLIT_VARIABLE_COUNT))
        affine: list[Polynomial] = [
            {(variable,): sp.Integer(1)} for variable in range(SPLIT_VARIABLE_COUNT)
        ]
        rref_hash = hashlib.sha256(b"").hexdigest()
        if coefficient_rank == augmented_rank:
            rref, pivots = coefficients.row_join(rhs).rref()
            pivot_variables = tuple(
                int(pivot) for pivot in pivots if pivot < SPLIT_VARIABLE_COUNT
            )
            free_variables = tuple(
                variable
                for variable in range(SPLIT_VARIABLE_COUNT)
                if variable not in set(pivot_variables)
            )
            digest = hashlib.sha256()
            for row in range(coefficient_rank):
                digest.update(
                    ("|".join(sp.srepr(value) for value in rref[row, :]) + "\n").encode()
                )
                pivot = pivot_variables[row]
                expression: dict[Monomial, sp.Expr] = {
                    (): rref[row, SPLIT_VARIABLE_COUNT]
                }
                for variable in free_variables:
                    if rref[row, variable] != 0:
                        expression[(variable,)] = -rref[row, variable]
                affine[pivot] = _clean_polynomial(expression)
            rref_hash = digest.hexdigest()

        residual_by_normalized: dict[bytes, Polynomial] = {}
        residual_constant = coefficient_rank < augmented_rank
        if not residual_constant:
            for polynomial in constraints:
                changed = _substitute_polynomial(polynomial, tuple(affine))
                if not changed:
                    continue
                if set(changed) == {()}:
                    residual_constant = True
                normalized = _normalize(changed)
                residual_by_normalized[
                    _normalized_polynomial_bytes(normalized)
                ] = normalized
        residuals = tuple(
            residual_by_normalized[key] for key in sorted(residual_by_normalized)
        )
        residual_degree_classification = tuple(
            sum(max(map(len, polynomial), default=0) == degree for polynomial in residuals)
            for degree in range(3)
        )
        residual_digest = hashlib.sha256()
        for index, polynomial in enumerate(residuals):
            residual_digest.update(f"constraint={index}\n".encode())
            residual_digest.update(_polynomial_bytes(polynomial))

        zero_assignment_solution = False
        nonzero_coordinates: tuple[tuple[int, str], ...] = ()
        if coefficient_rank == augmented_rank and not residual_constant:
            values = []
            for variable in range(SPLIT_VARIABLE_COUNT):
                value = affine[variable].get((), 0)
                values.append(sp.expand(value))
            zero_assignment_solution = all(
                sp.expand(
                    sum(
                        coefficient
                        * sp.prod(values[variable] for variable in monomial)
                        for monomial, coefficient in polynomial.items()
                    )
                )
                == 0
                for polynomial in constraints
            )
            if zero_assignment_solution:
                nonzero_coordinates = tuple(
                    (variable, str(value))
                    for variable, value in enumerate(values)
                    if value != 0
                )

        result = GeneralNonlinearFactorSharpOrderTwoReduction(
            input_constraint_count=len(constraints),
            input_degree_classification=degree_classification,
            quadratic_monomial_count=len(quadratic_monomials),
            quadratic_coefficient_rank=quadratic_rank,
            affine_consequence_count=len(nonzero_rows),
            affine_system_shape=affine_system.shape,
            affine_rank=coefficient_rank,
            affine_augmented_rank=augmented_rank,
            affine_pivot_variables=pivot_variables,
            affine_free_variables=free_variables,
            affine_rref_sha256=rref_hash,
            residual_constraint_count=len(residuals),
            residual_unique_constraint_count=len(residual_by_normalized),
            residual_degree_classification=residual_degree_classification,
            residual_term_count=sum(len(polynomial) for polynomial in residuals),
            residual_sha256=residual_digest.hexdigest(),
            residual_constant_obstruction=residual_constant,
            zero_free_assignment_solution=zero_assignment_solution,
            zero_free_assignment_nonzero_coordinates=nonzero_coordinates,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if (
            self.input_constraint_count,
            self.input_degree_classification,
            self.quadratic_monomial_count,
            self.quadratic_coefficient_rank,
        ) != (179, (0, 0, 179), 1497, 124):
            raise AssertionError("sharp polynomial input classification drifted")
        if (
            self.affine_consequence_count,
            self.affine_system_shape,
            self.affine_rank,
            self.affine_augmented_rank,
            self.affine_pivot_variables,
            self.affine_free_variables,
            self.affine_rref_sha256,
        ) != (
            0,
            (0, 115),
            0,
            0,
            (),
            tuple(range(114)),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        ):
            raise AssertionError("sharp affine consequence solve drifted")
        if (
            self.residual_constraint_count,
            self.residual_unique_constraint_count,
            self.residual_degree_classification,
            self.residual_term_count,
            self.residual_sha256,
            self.residual_constant_obstruction,
            self.zero_free_assignment_solution,
            self.zero_free_assignment_nonzero_coordinates,
        ) != (
            179,
            179,
            (0, 0, 179),
            4664,
            "646c0f5c75a90e05f3aa09918078e107e81d3646f19a8c09eca76916427cdd53",
            False,
            False,
            (),
        ):
            raise AssertionError("sharp residual quadratic ledger drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-general-nonlinear-factor-sharp-order2-reduction-v1",
            "input": {
                "certificate": "curved_general_nonlinear_factor_sharp_order2.json",
                "unique_projected_constraints": self.input_constraint_count,
                "classification_by_maximal_degree_0_to_2": list(
                    self.input_degree_classification
                ),
                "quadratic_monomial_count": self.quadratic_monomial_count,
                "quadratic_coefficient_rank": self.quadratic_coefficient_rank,
            },
            "all_affine_linear_consequences": {
                "method": "exact left kernel of the quadratic-coefficient matrix",
                "nonzero_consequences": self.affine_consequence_count,
                "system_shape_including_constant": list(self.affine_system_shape),
                "coefficient_rank": self.affine_rank,
                "augmented_rank": self.affine_augmented_rank,
                "consistent": self.affine_rank == self.affine_augmented_rank,
                "pivot_variables": list(self.affine_pivot_variables),
                "eliminated_variables": len(self.affine_pivot_variables),
                "free_variables": len(self.affine_free_variables),
                "rref_sha256": self.affine_rref_sha256,
            },
            "residual_quadratic_system": {
                "constraint_count": self.residual_constraint_count,
                "unique_constraint_count": self.residual_unique_constraint_count,
                "classification_by_maximal_degree_0_to_2": list(
                    self.residual_degree_classification
                ),
                "term_count": self.residual_term_count,
                "content_sha256": self.residual_sha256,
                "constant_contradiction_after_affine_elimination": (
                    self.residual_constant_obstruction
                ),
                "zero_free_assignment_is_exact_solution": (
                    self.zero_free_assignment_solution
                ),
                "zero_free_assignment_nonzero_coordinates": [
                    {"variable": variable, "value": value}
                    for variable, value in self.zero_free_assignment_nonzero_coordinates
                ],
                "degree_one_multiplier_left_ideal_test_completed": False,
                "exact_left_ideal_contradiction_found": False,
            },
            "outcome": {
                "all_vector_space_linear_consequences_solved": True,
                "exact_rational_order_two_solution_found": (
                    self.zero_free_assignment_solution
                ),
                "exact_affine_span_obstruction_found": (
                    self.residual_constant_obstruction
                ),
                "full_quadratic_ideal_solved": False,
                "orders_one_and_zero_solved": False,
                "general_factorization_proved": False,
                "general_factorization_disproved": False,
                "green_realization_proved": False,
                "flag_promoted": False,
            },
            "theorem_boundary": (
                "all affine-linear consequences in the exact rational span of "
                "the 179 order-two Schur polynomials are solved and substituted. "
                "Unless an explicit rational point or constant contradiction is "
                "reported, the residual quadratic ideal remains undecided.  Orders "
                "one and zero and every Green-theoretic flag remain open"
            ),
        }
