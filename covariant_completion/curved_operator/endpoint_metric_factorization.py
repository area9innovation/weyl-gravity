"""Exact projector-free factorization screen for the metric endpoint block.

The coefficient-complete endpoint witness leaves the field operator

``D_M = P_tr + H_end,TF``

on symmetric two-tensors.  This module tests the strongest natural local
factorization which would make that block Green hyperbolic without a TT,
helicity, inverse-curl, or inverse-Laplacian projector:

``D_M = L_- L_+``

with

``L_+/- = P_tr + Box P_TF + A_+/-^mu nabla_mu + B_+/-``.

The coefficients ``A`` and ``B`` range over the *complete* parallel
``SO(3)``-invariant families which vanish on the trace line and preserve the
trace-free bundle.  Their dimensions are respectively nine and three.  The
product is formed by the repository's exact symmetrized covariant-jet/PBW
composer, so the order-two and order-zero equations include all cylinder
curvature commutators.

The public builder is intentionally fail closed.  It records the exact
staged polynomial system and either an exact solution or a scoped algebraic
obstruction.  It never promotes a Green claim from a partial solve.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import hashlib
from itertools import combinations_with_replacement
import json
from pathlib import Path
from typing import Iterable, Mapping

import sympy as sp
from sympy.polys.matrices import DomainMatrix

from .conventions import SYMMETRIC_COORDINATES, _ordinary_system
from .derivative_normal_form import ParallelCylinderNormalForm
from .invariant_pairings import _rotation_generators, _tensor_representation
from .parallel_operator_composition import ParallelFieldOperatorComposer
from .symmetrized_pbw_composition import SymmetrizedPBWComposer


Word = tuple[int, ...]
Table = dict[Word, sp.Matrix]


def _trace_projectors() -> tuple[sp.Matrix, sp.Matrix]:
    metric = _ordinary_system().metric
    metric_vector = sp.Matrix(
        [metric[a, b] for a, b in SYMMETRIC_COORDINATES]
    )
    trace_covector = metric_vector.T
    if trace_covector * metric_vector != sp.Matrix([[4]]):
        raise AssertionError("symmetric-tensor trace normalization drifted")
    trace = metric_vector * trace_covector / 4
    tracefree = sp.eye(10) - trace
    if trace * trace != trace or tracefree * tracefree != tracefree:
        raise AssertionError("trace projectors ceased to be idempotent")
    return trace, tracefree


def _matrix10(vector: sp.Matrix) -> sp.Matrix:
    """Column-major vectorization inverse used by Kronecker constraints."""

    if vector.shape != (100, 1):
        raise ValueError("a ten-tensor endomorphism needs 100 coordinates")
    return sp.Matrix(10, 10, lambda row, column: vector[column * 10 + row])


def _first_coefficients(vector: sp.Matrix) -> tuple[sp.Matrix, ...]:
    if vector.shape != (400, 1):
        raise ValueError("a first-order ten-tensor operator needs 400 coordinates")
    return tuple(_matrix10(vector[100 * axis : 100 * (axis + 1), :]) for axis in range(4))


def _invariant_bases() -> tuple[tuple[tuple[sp.Matrix, ...], ...], tuple[sp.Matrix, ...]]:
    """Return complete 9-dimensional first and 3-dimensional zeroth bases."""

    _, tracefree = _trace_projectors()
    identity10 = sp.eye(10)
    # vec(P X P)=(P^T tensor P)vec(X), with column-major vec.
    tracefree_constraint = sp.eye(100) - sp.kronecker_product(
        tracefree.T, tracefree
    )
    tensor_generators = tuple(
        _tensor_representation(rotation) for rotation in _rotation_generators()
    )

    zeroth_blocks = [tracefree_constraint]
    for generator in tensor_generators:
        zeroth_blocks.append(
            sp.kronecker_product(identity10, generator)
            - sp.kronecker_product(generator.T, identity10)
        )
    zeroth_constraints = sp.Matrix.vstack(*zeroth_blocks)
    zeroth_kernel = (
        DomainMatrix.from_Matrix(zeroth_constraints).nullspace().to_Matrix().T
    )
    if zeroth_kernel.shape != (100, 3):
        raise AssertionError("complete invariant algebraic family is not rank three")

    first_blocks = [
        sp.kronecker_product(sp.eye(4), tracefree_constraint)
    ]
    for field_generator, covector_generator in zip(
        tensor_generators, _rotation_generators(), strict=True
    ):
        commutator = (
            sp.kronecker_product(identity10, field_generator)
            - sp.kronecker_product(field_generator.T, identity10)
        )
        first_blocks.append(
            sp.kronecker_product(sp.eye(4), commutator)
            + sp.kronecker_product(covector_generator, sp.eye(100))
        )
    first_constraints = sp.Matrix.vstack(*first_blocks)
    first_kernel = (
        DomainMatrix.from_Matrix(first_constraints).nullspace().to_Matrix().T
    )
    if first_kernel.shape != (400, 9):
        raise AssertionError("complete invariant first-order family is not rank nine")

    first = tuple(
        _first_coefficients(first_kernel[:, column])
        for column in range(first_kernel.cols)
    )
    zeroth = tuple(
        _matrix10(zeroth_kernel[:, column])
        for column in range(zeroth_kernel.cols)
    )
    for coefficients in first:
        for coefficient in coefficients:
            if coefficient != tracefree * coefficient * tracefree:
                raise AssertionError("first-order basis escaped the trace-free block")
    for coefficient in zeroth:
        if coefficient != tracefree * coefficient * tracefree:
            raise AssertionError("algebraic basis escaped the trace-free block")
    return first, zeroth


def _embed10(matrix: sp.Matrix) -> sp.Matrix:
    if matrix.shape != (10, 10):
        raise ValueError("only the symmetric-tensor block can be embedded")
    result = sp.zeros(24)
    result[:10, :10] = matrix
    return result


def _factor_table(
    first_basis: tuple[tuple[sp.Matrix, ...], ...],
    zeroth_basis: tuple[sp.Matrix, ...],
    first_parameters: tuple[sp.Expr, ...],
    zeroth_parameters: tuple[sp.Expr, ...],
) -> Table:
    if len(first_parameters) != 9 or len(zeroth_parameters) != 3:
        raise ValueError("factor parameter ledger drifted")
    trace, tracefree = _trace_projectors()
    metric = _ordinary_system().metric
    output: dict[Word, sp.Matrix] = defaultdict(lambda: sp.zeros(24))
    output[()] = _embed10(
        trace
        + sum(
            (parameter * basis for parameter, basis in zip(
                zeroth_parameters, zeroth_basis, strict=True
            )),
            sp.zeros(10),
        )
    )
    for axis in range(4):
        output[(axis, axis)] += metric[axis, axis] * _embed10(tracefree)
        output[(axis,)] += _embed10(
            sum(
                (
                    parameter * basis[axis]
                    for parameter, basis in zip(
                        first_parameters, first_basis, strict=True
                    )
                ),
                sp.zeros(10),
            )
        )
    return {
        word: matrix.applyfunc(sp.expand)
        for word, matrix in output.items()
        if matrix != sp.zeros(24)
    }


def _target_table(payload: Mapping[str, object]) -> Table:
    if payload.get("schema") != (
        "pure-weyl-prolonged-metric-endpoint-backward-witness-coefficients-v2"
    ):
        raise AssertionError("wrong endpoint backward-witness coefficient schema")
    d_end = payload.get("D_end")
    if not isinstance(d_end, Mapping):
        raise AssertionError("missing endpoint D_end tables")
    field = d_end.get("D_M")
    if not isinstance(field, Mapping) or field.get("shape") != [10, 10]:
        raise AssertionError("missing 10 by 10 endpoint field block")
    coefficients = field.get("coefficients")
    if not isinstance(coefficients, list):
        raise AssertionError("malformed endpoint field coefficients")
    trace, tracefree = _trace_projectors()
    output: Table = {}
    for item in coefficients:
        if not isinstance(item, Mapping):
            raise AssertionError("malformed endpoint field coefficient item")
        multiindex = item.get("multiindex")
        entries = item.get("entries")
        if not isinstance(multiindex, list) or not isinstance(entries, list):
            raise AssertionError("malformed endpoint field sparse item")
        word = tuple(
            axis
            for axis, multiplicity in enumerate(multiindex)
            for _ in range(int(multiplicity))
        )
        matrix = sp.zeros(10)
        for row, column, value in entries:
            matrix[int(row), int(column)] = sp.Rational(value)
        # The exact endpoint filtration has already isolated the lower-left
        # trace coupling.  Its Green inverse is obtained by the certified
        # triangular formula after this rank-nine problem is solved.  The
        # same-bundle factor target is therefore the block diagonal carrier
        # P_tr + P_TF D_M P_TF, not the unreduced triangular D_M.
        reduced = (tracefree * matrix * tracefree).applyfunc(sp.expand)
        if not word:
            reduced += trace
        output[word] = _embed10(reduced)
    return output


def _defect_by_order(left: Mapping[Word, sp.Matrix], right: Mapping[Word, sp.Matrix]) -> dict[int, tuple[sp.Expr, ...]]:
    result: dict[int, list[sp.Expr]] = defaultdict(list)
    for word in sorted(set(left) | set(right), key=lambda item: (len(item), item)):
        defect = sp.Matrix(
            left.get(word, sp.zeros(24)) - right.get(word, sp.zeros(24))
        ).applyfunc(sp.expand)
        # Only the actual 10 by 10 endpoint block is part of the solve.
        for value in defect[:10, :10]:
            if value != 0:
                result[len(word)].append(value)
        if any(value != 0 for value in defect[10:, :]) or any(
            value != 0 for value in defect[:10, 10:]
        ):
            raise AssertionError("factor product escaped the embedded metric block")
    return {
        order: tuple(dict.fromkeys(sp.expand(value) for value in values))
        for order, values in result.items()
    }


def _coefficient_hash(table: Mapping[Word, sp.Matrix]) -> str:
    serial = []
    for word in sorted(table, key=lambda item: (len(item), item)):
        serial.append(
            [
                list(word),
                [
                    [row, column, str(value)]
                    for (row, column), value in sorted(
                        table[word].todok().items()
                    )
                ],
            ]
        )
    return hashlib.sha256(
        json.dumps(serial, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class EndpointMetricFactorizationSystem:
    """The exact staged polynomial system for ``D_M=L_-L_+``."""

    target: Table
    product: Table
    equations: Mapping[int, tuple[sp.Expr, ...]]
    parameters: tuple[sp.Symbol, ...]
    first_basis: tuple[tuple[sp.Matrix, ...], ...]
    zeroth_basis: tuple[sp.Matrix, ...]

    @staticmethod
    def build(payload: Mapping[str, object]) -> "EndpointMetricFactorizationSystem":
        first_basis, zeroth_basis = _invariant_bases()
        a_minus = sp.symbols("am0:9")
        a_plus = sp.symbols("ap0:9")
        b_minus = sp.symbols("bm0:3")
        b_plus = sp.symbols("bp0:3")
        normal_form = ParallelCylinderNormalForm.build()
        pbw = SymmetrizedPBWComposer(
            ParallelFieldOperatorComposer(normal_form)
        )
        minus = _factor_table(
            first_basis, zeroth_basis, a_minus, b_minus
        )
        plus = _factor_table(first_basis, zeroth_basis, a_plus, b_plus)
        product = pbw.compose(minus, plus)
        target = _target_table(payload)
        equations = _defect_by_order(product, target)
        result = EndpointMetricFactorizationSystem(
            target=target,
            product=product,
            equations=equations,
            parameters=tuple(a_minus + a_plus + b_minus + b_plus),
            first_basis=first_basis,
            zeroth_basis=zeroth_basis,
        )
        result.verify_kinematics()
        return result

    def verify_kinematics(self) -> None:
        if (len(self.first_basis), len(self.zeroth_basis)) != (9, 3):
            raise AssertionError("complete invariant factor family drifted")
        orders = sorted(
            set(map(len, self.target)) | set(map(len, self.product))
        )
        if orders != [0, 1, 2, 3, 4]:
            raise AssertionError("factorization derivative-order ledger drifted")
        # The principal symbol is fixed before solving lower orders.
        if self.equations.get(4, ()):
            raise AssertionError("scalar fourth-order principal symbols disagree")

    def system_payload(self) -> dict[str, object]:
        self.verify_kinematics()
        return {
            "schema": "pure-weyl-endpoint-metric-factorization-system-v1",
            "dependency_tag": "LORENTZIAN-CAUSAL",
            "target": "D_M=P_tr+H_end,TF",
            "candidate": (
                "L_-/+ = P_tr+Box P_TF+A_-/+^mu nabla_mu+B_-/+"
            ),
            "ansatz_completeness": {
                "isotropy": "SO(3) holonomy of R x S3",
                "tracefree_representation": "V_0+V_1+V_2",
                "zeroth_order_dimension": len(self.zeroth_basis),
                "zeroth_order_derivation": "sum_l 1^2=3",
                "first_order_dimension": len(self.first_basis),
                "first_order_derivation": (
                    "3 temporal intertwiners plus 6 spatial Clebsch-Gordan "
                    "intertwiners"
                ),
                "parallel_globalization": True,
                "tracefree_preserving": True,
                "principal_normalization_WLOG": (
                    "For general invariant leading maps q H_minus and q H_plus, "
                    "the scalar target forces H_minus H_plus=I.  Both are "
                    "invertible and parallel, and the exact redistribution "
                    "L_minus H_plus, H_plus^{-1} L_plus has scalar qI principal "
                    "symbols, the same product, and remains inside the complete "
                    "9+3 lower-order families."
                ),
            },
            "normal_form": (
                "exact symmetrized covariant derivatives with all unit-S3 "
                "curvature commutators"
            ),
            "parameter_count": len(self.parameters),
            "parameter_names": [str(value) for value in self.parameters],
            "equation_counts_by_derivative_order": {
                str(order): len(self.equations.get(order, ()))
                for order in (4, 3, 2, 1, 0)
            },
            "target_sha256": _coefficient_hash(self.target),
            "product_sha256": _coefficient_hash(self.product),
            "full_factorization_proved": False,
            "full_factorization_disproved_in_complete_ansatz": False,
            "green_claim_promoted": False,
            "fail_closed": True,
        }


def load_system(path: Path) -> EndpointMetricFactorizationSystem:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise AssertionError("endpoint backward-witness payload is not an object")
    return EndpointMetricFactorizationSystem.build(payload)


def _unique_nonzero(expressions: Iterable[sp.Expr]) -> tuple[sp.Expr, ...]:
    return tuple(
        dict.fromkeys(
            value
            for expression in expressions
            if (value := sp.factor(expression)) != 0
        )
    )


def _independent_rows(matrix: sp.Matrix, target_rank: int) -> tuple[int, ...]:
    rows: list[int] = []
    rank = 0
    for row in range(matrix.rows):
        candidate = matrix[rows + [row], :]
        changed = DomainMatrix.from_Matrix(candidate).rank()
        if changed > rank:
            rows.append(row)
            rank = changed
        if rank == target_rank:
            break
    if rank != target_rank:
        raise AssertionError("could not extract the required independent rows")
    return tuple(rows)


def _multiplier_monomials(
    variables: tuple[sp.Symbol, ...], maximum_degree: int
) -> tuple[sp.Expr, ...]:
    output = [sp.Integer(1)]
    for degree in range(1, maximum_degree + 1):
        output.extend(
            sp.prod(variables[index] for index in indices)
            for indices in combinations_with_replacement(
                range(len(variables)), degree
            )
        )
    return tuple(output)


def _polynomial_ideal_certificate(
    constraints: tuple[sp.Expr, ...],
    variables: tuple[sp.Symbol, ...],
) -> tuple[
    tuple[sp.Expr, ...],
    tuple[tuple[int, sp.Expr], ...],
    int,
    tuple[sp.Symbol, ...],
]:
    """Find a low-degree rational Nullstellensatz certificate.

    The rows are ``m f_i`` for every multiplier monomial ``m`` through a
    staged degree.  Solving the exact transposed Macaulay system for the
    constant polynomial retains the multipliers themselves, unlike a bare
    Groebner ``[1]`` result.
    """

    for multiplier_degree in range(0, 4):
        multipliers = _multiplier_monomials(variables, multiplier_degree)
        rows = tuple(
            (constraint_index, multiplier)
            for constraint_index in range(len(constraints))
            for multiplier in multipliers
        )
        products = tuple(
            sp.Poly(
                multiplier * constraints[constraint_index],
                *variables,
                domain=sp.QQ,
            )
            for constraint_index, multiplier in rows
        )
        monomials = {tuple([0] * len(variables))}
        for polynomial in products:
            monomials.update(polynomial.monoms())
        ordered_monomials = tuple(
            sorted(monomials, key=lambda item: (sum(item), item))
        )
        coefficient_matrix = sp.MutableSparseMatrix(
            len(products), len(ordered_monomials), {}
        )
        monomial_columns = {
            monomial: column for column, monomial in enumerate(ordered_monomials)
        }
        for row, polynomial in enumerate(products):
            for monomial, coefficient in polynomial.terms():
                coefficient_matrix[row, monomial_columns[monomial]] = coefficient
        target = sp.zeros(len(ordered_monomials), 1)
        target[monomial_columns[tuple([0] * len(variables))], 0] = 1
        augmented = DomainMatrix.from_Matrix(
            coefficient_matrix.T.row_join(target)
        )
        reduced_domain, pivots = augmented.rref()
        reduced = reduced_domain.to_Matrix()
        last_column = coefficient_matrix.rows
        if last_column in pivots:
            continue
        # Set every free multiplier coefficient to zero.  RREF then reads a
        # deterministic particular solution directly from its last column.
        solution = sp.zeros(coefficient_matrix.rows, 1)
        for row, pivot in enumerate(pivots):
            if pivot < coefficient_matrix.rows:
                solution[pivot, 0] = reduced[row, -1]
        free_symbols: tuple[sp.Symbol, ...] = ()
        weights_by_constraint: dict[int, sp.Expr] = defaultdict(
            lambda: sp.Integer(0)
        )
        for row, value in enumerate(solution):
            if value != 0:
                constraint_index, multiplier = rows[row]
                weights_by_constraint[constraint_index] += value * multiplier
        weights = tuple(
            (index, sp.factor(value))
            for index, value in sorted(weights_by_constraint.items())
            if value != 0
        )
        defect = sp.expand(
            sum(
                (value * constraints[index] for index, value in weights),
                sp.Integer(0),
            )
            - 1
        )
        if defect != 0:
            raise AssertionError("order-two polynomial ideal certificate failed")
        monomial_expressions = tuple(
            sp.prod(
                variable**power
                for variable, power in zip(
                    variables, monomial, strict=True
                )
            )
            for monomial in ordered_monomials
        )
        return (
            monomial_expressions,
            weights,
            multiplier_degree,
            free_symbols,
        )
    raise AssertionError("no degree-at-most-three ideal certificate was found")


@dataclass(frozen=True)
class EndpointMetricFactorizationNoGo:
    """Exact order-two obstruction in the complete scalar-principal family."""

    system: EndpointMetricFactorizationSystem
    order3_rank: int
    order3_augmented_rank: int
    order2_sum_rank: int
    order2_sum_rows: tuple[int, ...]
    order2_sum_solution: tuple[sp.Expr, ...]
    order2_constraints: tuple[sp.Expr, ...]
    order2_monomials: tuple[sp.Expr, ...]
    constant_weights: tuple[tuple[int, sp.Expr], ...]
    certificate_multiplier_degree: int
    constant_certificate_free_symbols: tuple[sp.Symbol, ...]

    @staticmethod
    def build(system: EndpointMetricFactorizationSystem) -> "EndpointMetricFactorizationNoGo":
        parameters = system.parameters
        a_minus = parameters[:9]
        a_plus = parameters[9:18]
        b_minus = parameters[18:21]
        b_plus = parameters[21:24]

        cubic = system.equations.get(3, ())
        cubic_matrix, cubic_rhs = sp.linear_eq_to_matrix(
            cubic, a_minus + a_plus
        )
        cubic_rank = DomainMatrix.from_Matrix(cubic_matrix).rank()
        cubic_augmented_rank = DomainMatrix.from_Matrix(
            cubic_matrix.row_join(cubic_rhs)
        ).rank()
        if (cubic_rank, cubic_augmented_rank) != (9, 9):
            raise AssertionError("endpoint cubic factor gate drifted")
        cubic_substitution = {
            a_plus[index]: -a_minus[index] for index in range(9)
        }
        if any(sp.expand(value.subs(cubic_substitution)) != 0 for value in cubic):
            raise AssertionError("cubic gate is not exactly A_plus=-A_minus")

        sums = sp.symbols("s0:3")
        order2_substitution = dict(cubic_substitution)
        order2_substitution.update(
            {
                b_plus[index]: sums[index] - b_minus[index]
                for index in range(3)
            }
        )
        quadratic = _unique_nonzero(
            value.subs(order2_substitution)
            for value in system.equations.get(2, ())
        )
        sum_matrix, sum_rhs = sp.linear_eq_to_matrix(quadratic, sums)
        sum_rank = DomainMatrix.from_Matrix(sum_matrix).rank()
        if sum_rank != 3:
            raise AssertionError("order-two algebraic-sum gate is not full rank")
        rows = _independent_rows(sum_matrix, 3)
        sum_solution = tuple(
            sp.factor(value)
            for value in sum_matrix[list(rows), :].inv() * sum_rhs[list(rows), :]
        )
        sum_substitution = {
            sums[index]: sum_solution[index] for index in range(3)
        }
        constraints = _unique_nonzero(
            value.subs(sum_substitution) for value in quadratic
        )
        monomials, weights, multiplier_degree, free_symbols = _polynomial_ideal_certificate(
            constraints, tuple(a_minus)
        )
        result = EndpointMetricFactorizationNoGo(
            system=system,
            order3_rank=cubic_rank,
            order3_augmented_rank=cubic_augmented_rank,
            order2_sum_rank=sum_rank,
            order2_sum_rows=rows,
            order2_sum_solution=sum_solution,
            order2_constraints=constraints,
            order2_monomials=monomials,
            constant_weights=weights,
            certificate_multiplier_degree=multiplier_degree,
            constant_certificate_free_symbols=free_symbols,
        )
        result.verify()
        return result

    def verify(self) -> None:
        self.system.verify_kinematics()
        if (self.order3_rank, self.order3_augmented_rank) != (9, 9):
            raise AssertionError("order-three solve is not exact")
        if self.order2_sum_rank != 3:
            raise AssertionError("order-two B-sum solve is not exact")
        if len(self.order2_sum_solution) != 3:
            raise AssertionError("order-two B-sum solution ledger drifted")
        if not self.constant_weights:
            raise AssertionError("order-two no-go lacks an exact certificate")
        a_minus = self.system.parameters[:9]
        defect = sp.expand(
            sum(
                (
                    weight * self.order2_constraints[index]
                    for index, weight in self.constant_weights
                ),
                sp.Integer(0),
            )
            - 1
        )
        if defect != 0 or any(
            variable not in a_minus
            for constraint in self.order2_constraints
            for variable in constraint.free_symbols
        ):
            raise AssertionError("order-two obstruction is not a rational identity")

    def certificate(self, *, dependency_sha256: str) -> dict[str, object]:
        self.verify()
        base = self.system.system_payload()
        return {
            "schema": "pure-weyl-endpoint-metric-scalar-factorization-no-go-v1",
            "dependency_tag": "LORENTZIAN-CAUSAL",
            "endpoint_backward_witness_coefficients_sha256": dependency_sha256,
            "target": base["target"],
            "candidate": base["candidate"],
            "ansatz_completeness": base["ansatz_completeness"],
            "normal_form": base["normal_form"],
            "staged_solve": {
                "order4": {
                    "defects": len(self.system.equations.get(4, ())),
                    "result": "scalar biwave symbols agree",
                },
                "order3": {
                    "equations": len(self.system.equations.get(3, ())),
                    "coefficient_rank": self.order3_rank,
                    "augmented_rank": self.order3_augmented_rank,
                    "solution": "A_plus=-A_minus",
                },
                "order2": {
                    "equations": len(self.system.equations.get(2, ())),
                    "B_minus_plus_B_plus_rank": self.order2_sum_rank,
                    "B_sum_pivot_equation_indices": list(self.order2_sum_rows),
                    "B_sum_solution": [str(value) for value in self.order2_sum_solution],
                    "residual_quadratics": len(self.order2_constraints),
                    "residual_monomials": len(self.order2_monomials),
                    "polynomial_nullstellensatz_nonzero_multipliers": len(
                        self.constant_weights
                    ),
                    "certificate_multiplier_degree": self.certificate_multiplier_degree,
                    "polynomial_nullstellensatz_certificate": [
                        {
                            "constraint_index": index,
                            "weight": str(weight),
                            "constraint": str(self.order2_constraints[index]),
                        }
                        for index, weight in self.constant_weights
                    ],
                    "identity": "sum_i weight_i constraint_i=1",
                    "defect": 0,
                },
                "order1": "not reached: exact order-two ideal is the unit ideal",
                "order0": "not reached: exact order-two ideal is the unit ideal",
            },
            "outcome": {
                "full_factorization_proved": False,
                "scalar_principal_factorization_disproved_in_complete_ansatz": True,
                "normally_hyperbolic_same_bundle_factor_pair_disproved_in_this_ansatz": True,
                "complete_parallel_invariant_wave_leading_fibre_family_covered": True,
                "general_green_hyperbolicity_disproved": False,
                "curvature_metric_lift_disproved": False,
                "green_claim_promoted": False,
            },
            "scope": (
                "The no-go exhausts two second-order factors with trace identity, "
                "scalar Box principal symbol on S2_0, and every parallel SO(3)-"
                "invariant tracefree-preserving first- and zeroth-order term. "
                "The scalar-principal normalization is without loss for any "
                "parallel invariant nondegenerate leading pair whose product "
                "is the scalar target.  The no-go does not exclude enlarged "
                "or mixed-order systems, triangular Green extensions, or the "
                "equation-cone curvature-to-metric route."
            ),
            "status_flags_promoted": [],
            "fail_closed": True,
        }
