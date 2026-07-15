"""Complete rotation-equivariant first-order family for ``R6sharp``.

The pair-(1,6) relative saddle contains a first-order map

``R6sharp: M_aux[24] -> X_Id_sharp[14]``.

The earlier temporal calculation fixed only its ``nabla_0`` coefficient.
This module constructs the complete coefficient family in the actual
component bases.  A time coefficient is an ordinary ``SO(3)`` intertwiner,
whereas the three spatial coefficients form a vector intertwiner.  Thus the
equations solved here are

``G_t T_0-T_0 G_s=0``

and

``G_t T_a-T_a G_s=sum_b (J_i)_{ba} T_b``.

They are exact rational equations made from the certified infinitesimal
rotation generators.  No multiplicity-only dimension count is used as a
substitute for solving them.  The result is a 22-parameter temporal family
and a 46-parameter spatial family.  Fixing the already certified temporal
normalization therefore leaves all 46 spatial parameters free.

This is an ansatz-completeness certificate.  The separate first-order
reduction search must still decide semisimplicity and positivity; no Green
flag follows from the family dimension alone.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
import hashlib

import sympy as sp
from sympy.polys.matrices import DomainMatrix

from .expanded_relative_witness_commutant import (
    _block_generators,
    _commutant_matrix,
)
from .expanded_relative_witness_full_symbol import (
    COMPLETE_RANK,
    EVOLUTION_RANK,
    FIELD_RANK,
    SYMMETRIC_MONOMIALS,
    _gauge_derivative_coefficients,
    _relative_coefficients,
)
from .expanded_relative_witness_first_order_reduction import (
    CORE_ROW_START,
    REDUCED_RANK,
    ExpandedRelativeFirstOrderReduction,
)
from .invariant_pairings import _rotation_generators


TARGET_RANK = 14
SOURCE_RANK = 24
SPATIAL_DIMENSION = 3
TEMPORAL_PARAMETER_COUNT = 22
SPATIAL_PARAMETER_COUNT = 46
TOTAL_PARAMETER_COUNT = TEMPORAL_PARAMETER_COUNT + SPATIAL_PARAMETER_COUNT


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _primitive(vector: sp.MatrixBase) -> sp.Matrix:
    """Return a deterministic primitive integral representative."""

    denominators = [sp.denom(value) for value in vector if value]
    common = reduce(sp.ilcm, denominators, 1)
    integral = sp.Matrix(vector) * common
    numerators = [abs(int(value)) for value in integral if value]
    divisor = reduce(sp.igcd, numerators, 0) or 1
    integral = integral / divisor
    first = next((value for value in integral if value), sp.Integer(1))
    if first < 0:
        integral = -integral
    return sp.Matrix(integral)


def _spatial_covariance_matrix() -> sp.SparseMatrix:
    target = _block_generators()[10]
    source = _block_generators()[1]
    rotations = tuple(
        generator[1:, 1:] for generator in _rotation_generators()
    )

    def variable(axis: int, output: int, input_: int) -> int:
        return (axis * TARGET_RANK + output) * SOURCE_RANK + input_

    entries: dict[tuple[int, int], sp.Expr] = {}
    equation = 0
    for target_generator, source_generator, rotation in zip(
        target, source, rotations, strict=True
    ):
        for axis in range(SPATIAL_DIMENSION):
            for output in range(TARGET_RANK):
                for input_ in range(SOURCE_RANK):
                    for middle in range(TARGET_RANK):
                        value = target_generator[output, middle]
                        if value:
                            key = (equation, variable(axis, middle, input_))
                            entries[key] = entries.get(key, 0) + value
                    for middle in range(SOURCE_RANK):
                        value = -source_generator[middle, input_]
                        if value:
                            key = (equation, variable(axis, output, middle))
                            entries[key] = entries.get(key, 0) + value
                    for image_axis in range(SPATIAL_DIMENSION):
                        value = -rotation[image_axis, axis]
                        if value:
                            key = (
                                equation,
                                variable(image_axis, output, input_),
                            )
                            entries[key] = entries.get(key, 0) + value
                    equation += 1
    return sp.SparseMatrix(
        equation,
        SPATIAL_DIMENSION * TARGET_RANK * SOURCE_RANK,
        {key: sp.expand(value) for key, value in entries.items() if value},
    )


def _spatial_triple(vector: sp.MatrixBase) -> tuple[sp.Matrix, ...]:
    return tuple(
        sp.Matrix(
            TARGET_RANK,
            SOURCE_RANK,
            lambda output, input_, axis=axis: vector[
                (axis * TARGET_RANK + output) * SOURCE_RANK + input_
            ],
        )
        for axis in range(SPATIAL_DIMENSION)
    )


def _coefficient_defect(
    triple: tuple[sp.Matrix, ...],
) -> tuple[sp.Matrix, ...]:
    target = _block_generators()[10]
    source = _block_generators()[1]
    rotations = tuple(
        generator[1:, 1:] for generator in _rotation_generators()
    )
    defects: list[sp.Matrix] = []
    for target_generator, source_generator, rotation in zip(
        target, source, rotations, strict=True
    ):
        for axis in range(SPATIAL_DIMENSION):
            right = sum(
                (
                    rotation[image_axis, axis] * triple[image_axis]
                    for image_axis in range(SPATIAL_DIMENSION)
                ),
                sp.zeros(TARGET_RANK, SOURCE_RANK),
            )
            defects.append(
                target_generator * triple[axis]
                - triple[axis] * source_generator
                - right
            )
    return tuple(defects)


@dataclass(frozen=True)
class ExpandedRelativeR6Family:
    temporal_equations: sp.SparseMatrix
    spatial_equations: sp.SparseMatrix
    temporal_rank: int
    spatial_rank: int
    temporal_basis: tuple[sp.Matrix, ...]
    spatial_basis_vectors: tuple[sp.Matrix, ...]
    spatial_basis: tuple[tuple[sp.Matrix, ...], ...]
    certified_temporal_coefficient: sp.Matrix
    certified_temporal_coordinates: sp.Matrix

    @staticmethod
    def build() -> "ExpandedRelativeR6Family":
        generators = _block_generators()
        temporal_equations = _commutant_matrix(
            generators[10], generators[1]
        )
        spatial_equations = _spatial_covariance_matrix()
        temporal_rank = DomainMatrix.from_Matrix(temporal_equations).rank()
        spatial_rank = DomainMatrix.from_Matrix(spatial_equations).rank()
        temporal_vectors = tuple(
            _primitive(vector) for vector in temporal_equations.nullspace()
        )
        spatial_vectors = tuple(
            _primitive(vector) for vector in spatial_equations.nullspace()
        )
        temporal_basis = tuple(
            sp.Matrix(
                TARGET_RANK,
                SOURCE_RANK,
                lambda output, input_, vector=vector: vector[
                    input_ * TARGET_RANK + output
                ],
            )
            for vector in temporal_vectors
        )
        spatial_basis = tuple(_spatial_triple(vector) for vector in spatial_vectors)

        _, temporal = _relative_coefficients(_gauge_derivative_coefficients())
        basis_matrix = sp.Matrix.hstack(
            *(sp.Matrix(
                [
                    item[output, input_]
                    for input_ in range(SOURCE_RANK)
                    for output in range(TARGET_RANK)
                ]
            )
              for item in temporal_basis)
        )
        vector = sp.Matrix(
            [
                temporal[output, input_]
                for input_ in range(SOURCE_RANK)
                for output in range(TARGET_RANK)
            ]
        )
        coordinates, residual = basis_matrix.gauss_jordan_solve(vector)
        if residual.rows:
            # There are no free coordinate parameters because the basis has
            # independent columns.  SymPy represents that by a 0-row matrix.
            raise AssertionError("temporal basis coordinates are not unique")

        result = ExpandedRelativeR6Family(
            temporal_equations=temporal_equations,
            spatial_equations=spatial_equations,
            temporal_rank=temporal_rank,
            spatial_rank=spatial_rank,
            temporal_basis=temporal_basis,
            spatial_basis_vectors=spatial_vectors,
            spatial_basis=spatial_basis,
            certified_temporal_coefficient=temporal,
            certified_temporal_coordinates=coordinates,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.temporal_equations.shape != (1008, 336):
            raise AssertionError("temporal intertwiner equation shape drifted")
        if self.spatial_equations.shape != (3024, 1008):
            raise AssertionError("spatial covariance equation shape drifted")
        if self.temporal_rank != 314:
            raise AssertionError("temporal intertwiner rank drifted")
        if self.spatial_rank != 962:
            raise AssertionError("spatial covariance rank drifted")
        if len(self.temporal_basis) != TEMPORAL_PARAMETER_COUNT:
            raise AssertionError("temporal family dimension drifted")
        if len(self.spatial_basis) != SPATIAL_PARAMETER_COUNT:
            raise AssertionError("spatial family dimension drifted")
        if any(
            defect != sp.zeros(TARGET_RANK, SOURCE_RANK)
            for triple in self.spatial_basis
            for defect in _coefficient_defect(triple)
        ):
            raise AssertionError("a spatial family basis vector is not equivariant")
        reconstructed = sum(
            (
                coordinate * basis
                for coordinate, basis in zip(
                    self.certified_temporal_coordinates,
                    self.temporal_basis,
                    strict=True,
                )
            ),
            sp.zeros(TARGET_RANK, SOURCE_RANK),
        )
        if reconstructed != self.certified_temporal_coefficient:
            raise AssertionError("certified temporal coefficient left the family")

    def spatial_coefficients(
        self, parameters: tuple[sp.Expr, ...]
    ) -> tuple[sp.Matrix, ...]:
        if len(parameters) != SPATIAL_PARAMETER_COUNT:
            raise ValueError("the spatial family has 46 parameters")
        return tuple(
            sum(
                (
                    parameter * basis[axis]
                    for parameter, basis in zip(
                        parameters, self.spatial_basis, strict=True
                    )
                ),
                sp.zeros(TARGET_RANK, SOURCE_RANK),
            )
            for axis in range(SPATIAL_DIMENSION)
        )

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-expanded-relative-r6-family-v1",
            "map": "R6sharp: M_aux[24] -> X_Id_sharp[14]",
            "actual_rotation_generators": {
                "target_block": 10,
                "source_block": 1,
                "generator_count": 3,
                "coordinate_basis_exact": True,
            },
            "temporal_family": {
                "equations_shape": list(self.temporal_equations.shape),
                "equations_nonzero_entries": len(self.temporal_equations.todok()),
                "equations_sha256": _digest(self.temporal_equations),
                "rank": self.temporal_rank,
                "nullity": len(self.temporal_basis),
                "basis_sha256": [_digest(item) for item in self.temporal_basis],
                "certified_coefficient_sha256": _digest(
                    self.certified_temporal_coefficient
                ),
                "certified_coefficient_coordinates": [
                    str(value) for value in self.certified_temporal_coordinates
                ],
                "certified_normalization_is_member": True,
            },
            "spatial_family": {
                "covariance_equation": (
                    "G_target T_a-T_a G_source=sum_b J_(b,a) T_b"
                ),
                "equations_shape": list(self.spatial_equations.shape),
                "equations_nonzero_entries": len(self.spatial_equations.todok()),
                "equations_sha256": _digest(self.spatial_equations),
                "rank": self.spatial_rank,
                "nullity": len(self.spatial_basis),
                "basis_triple_sha256": [
                    [_digest(coefficient) for coefficient in triple]
                    for triple in self.spatial_basis
                ],
                "all_basis_covariance_defects": 0,
            },
            "complete_first_order_family": {
                "unfixed_parameter_count": TOTAL_PARAMETER_COUNT,
                "temporal_parameter_count": TEMPORAL_PARAMETER_COUNT,
                "spatial_parameter_count": SPATIAL_PARAMETER_COUNT,
                "after_certified_temporal_normalization": SPATIAL_PARAMETER_COUNT,
                "complete_under_SO3_equivariance": True,
            },
            "search_boundary": {
                "aligned_212_first_order_reduction_tested_here": False,
                "semisimple_solution_certified_here": False,
                "positive_symmetrizer_certified_here": False,
            },
            "prolonged_green_witness": False,
            "warranted_atomic_flags": ["fixed_temporal_16_family_complete"],
            "status_flags_promoted": ["fixed_temporal_16_family_complete"],
            "fail_closed": True,
        }


def _quadratic_identity_delta(
    identity: tuple[sp.Matrix, ...],
    spatial: tuple[sp.Matrix, ...],
) -> tuple[sp.Matrix, ...]:
    """Coefficients of ``-N(zeta)^T deltaR(zeta)``.

    The output is the 40-by-24 equation-dual/field block in the project's
    symmetric-monomial order.  This makes the corrected first-order formal
    adjoint sign explicit rather than hiding it in a sampled symbol.
    """

    relative = (sp.zeros(TARGET_RANK, SOURCE_RANK), *spatial)
    result: list[sp.Matrix] = []
    for first, second in SYMMETRIC_MONOMIALS:
        coefficient = -identity[first].T * relative[second]
        if first != second:
            coefficient -= identity[second].T * relative[first]
        result.append(coefficient)
    return tuple(result)


def _aligned_reduction_delta(
    coefficients: tuple[sp.Matrix, ...],
) -> sp.SparseMatrix:
    """Affine variation of the aligned 212-state spatial matrix."""

    entries: dict[tuple[int, int], sp.Expr] = {}
    equation_dual_start = CORE_ROW_START + FIELD_RANK + EVOLUTION_RANK
    mixed = coefficients[SYMMETRIC_MONOMIALS.index((0, 1))]
    spatial = coefficients[SYMMETRIC_MONOMIALS.index((1, 1))]
    for row in range(mixed.rows):
        for column in range(mixed.cols):
            if mixed[row, column]:
                entries[(equation_dual_start + row, FIELD_RANK + column)] = (
                    mixed[row, column]
                )
            if spatial[row, column]:
                entries[(
                    equation_dual_start + row,
                    2 * FIELD_RANK + column,
                )] = spatial[row, column]
    return sp.SparseMatrix(REDUCED_RANK, REDUCED_RANK, entries)


@dataclass(frozen=True)
class ExpandedRelativeR6FirstOrderNoGo:
    """Parameter-uniform intrinsic and first-order Jordan obstruction.

    The 212-state reduction has a parameter-independent Jordan chain, but
    that chain violates its gradient constraint.  The decisive calculation
    is therefore performed independently on the regular 116-square Douglis
    polynomial.  The polynomial chain

    ``a0=2 e_18, a1=e_8``

    obeys ``Q(1)a0=0`` and ``Q(1)a1+Q'(1)a0=0`` for
    ``Q(z)=P_weighted((-z,1))``.  Every one of the 46 spatial R6 parameter
    directions annihilates both identities coefficientwise.  Hence the
    elementary divisor at the characteristic root is defective throughout
    the complete family.  A faithful strong first-order linearization must
    preserve that polynomial Jordan structure, so it cannot have a positive
    symmetrizer.
    """

    family: ExpandedRelativeR6Family
    reduction: ExpandedRelativeFirstOrderReduction
    quadratic_identity_deltas: tuple[tuple[sp.Matrix, ...], ...]
    aligned_reduction_deltas: tuple[sp.SparseMatrix, ...]
    eigenvector_delta_actions: tuple[sp.Matrix, ...]
    generalized_delta_actions: tuple[sp.Matrix, ...]
    intrinsic_base_eigen_defect: sp.Matrix
    intrinsic_base_chain_defect: sp.Matrix
    intrinsic_eigen_delta_actions: tuple[sp.Matrix, ...]
    intrinsic_chain_delta_actions: tuple[sp.Matrix, ...]
    eigenvector_constraint: sp.Matrix
    generalized_constraint: sp.Matrix

    @staticmethod
    def build() -> "ExpandedRelativeR6FirstOrderNoGo":
        family = ExpandedRelativeR6Family.build()
        reduction = ExpandedRelativeFirstOrderReduction.build()
        identity = reduction.full_symbol.identity_coefficients
        quadratic = tuple(
            _quadratic_identity_delta(identity, spatial)
            for spatial in family.spatial_basis
        )
        aligned = tuple(
            _aligned_reduction_delta(coefficients)
            for coefficients in quadratic
        )
        u = reduction.jordan_eigenvector
        v = reduction.jordan_generalized_vector
        actions_u = tuple(delta * u for delta in aligned)
        actions_v = tuple(delta * v for delta in aligned)

        # Intrinsic polynomial chain in the weighted 116-square pencil.
        z = sp.Symbol("expanded_relative_r6_chain_z")
        polynomial = reduction.full_symbol.symbol(
            (-z, sp.Integer(1), sp.Integer(0), sp.Integer(0)),
            separated=True,
        )
        a0 = sp.zeros(COMPLETE_RANK, 1)
        a1 = sp.zeros(COMPLETE_RANK, 1)
        a0[18] = 2
        a1[8] = 1
        base_eigen = polynomial.subs(z, 1) * a0
        base_chain = (
            polynomial.subs(z, 1) * a1
            + polynomial.diff(z).subs(z, 1) * a0
        )
        intrinsic_eigen_actions: list[sp.Matrix] = []
        intrinsic_chain_actions: list[sp.Matrix] = []
        for spatial in family.spatial_basis:
            r1_aligned = spatial[0]
            delta = sp.zeros(COMPLETE_RANK)
            delta_prime = sp.zeros(COMPLETE_RANK)
            # zeta=(-z,1,0,0), Nsharp=-N^T and deltaR=R_1.
            delta[
                FIELD_RANK + EVOLUTION_RANK :
                FIELD_RANK + EVOLUTION_RANK + 40,
                :FIELD_RANK,
            ] = (
                reduction.full_symbol.identity_coefficients[0].T * r1_aligned
                - reduction.full_symbol.identity_coefficients[1].T * r1_aligned
            )
            delta_prime[
                FIELD_RANK + EVOLUTION_RANK :
                FIELD_RANK + EVOLUTION_RANK + 40,
                :FIELD_RANK,
            ] = reduction.full_symbol.identity_coefficients[0].T * r1_aligned
            intrinsic_eigen_actions.append(delta * a0)
            intrinsic_chain_actions.append(delta * a1 + delta_prime * a0)

        # Aligned unit spatial covector: G_1=p_1-m.  The other two gradient
        # constraints vanish on the sparse chain but G_1 does not.
        constraint = sp.zeros(3 * FIELD_RANK, REDUCED_RANK)
        constraint[:FIELD_RANK, :FIELD_RANK] = -sp.eye(FIELD_RANK)
        constraint[:FIELD_RANK, 2 * FIELD_RANK : 3 * FIELD_RANK] = sp.eye(
            FIELD_RANK
        )
        constraint[
            FIELD_RANK : 2 * FIELD_RANK,
            3 * FIELD_RANK : 4 * FIELD_RANK,
        ] = sp.eye(FIELD_RANK)
        constraint[
            2 * FIELD_RANK : 3 * FIELD_RANK,
            4 * FIELD_RANK : 5 * FIELD_RANK,
        ] = sp.eye(FIELD_RANK)

        result = ExpandedRelativeR6FirstOrderNoGo(
            family=family,
            reduction=reduction,
            quadratic_identity_deltas=quadratic,
            aligned_reduction_deltas=aligned,
            eigenvector_delta_actions=actions_u,
            generalized_delta_actions=actions_v,
            intrinsic_base_eigen_defect=base_eigen,
            intrinsic_base_chain_defect=base_chain,
            intrinsic_eigen_delta_actions=tuple(intrinsic_eigen_actions),
            intrinsic_chain_delta_actions=tuple(intrinsic_chain_actions),
            eigenvector_constraint=constraint * u,
            generalized_constraint=constraint * v,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if len(self.aligned_reduction_deltas) != SPATIAL_PARAMETER_COUNT:
            raise AssertionError("not every spatial R6 parameter was tested")
        zero = sp.zeros(REDUCED_RANK, 1)
        if any(action != zero for action in self.eigenvector_delta_actions):
            raise AssertionError("an R6 parameter moves the Jordan eigenvector")
        if any(action != zero for action in self.generalized_delta_actions):
            raise AssertionError("an R6 parameter moves the generalized vector")

        intrinsic_zero = sp.zeros(COMPLETE_RANK, 1)
        if self.intrinsic_base_eigen_defect != intrinsic_zero:
            raise AssertionError("intrinsic polynomial eigenvector identity failed")
        if self.intrinsic_base_chain_defect != intrinsic_zero:
            raise AssertionError("intrinsic polynomial Jordan-chain identity failed")
        if any(
            action != intrinsic_zero
            for action in self.intrinsic_eigen_delta_actions
        ):
            raise AssertionError("an R6 parameter moves the intrinsic eigenvector")
        if any(
            action != intrinsic_zero
            for action in self.intrinsic_chain_delta_actions
        ):
            raise AssertionError("an R6 parameter breaks the intrinsic chain")

        reduction = self.reduction
        generator = reduction.normalized_spatial_coefficients[0]
        identity = sp.eye(REDUCED_RANK)
        u = reduction.jordan_eigenvector
        v = reduction.jordan_generalized_vector
        if (generator - identity) * u != zero:
            raise AssertionError("base +1 eigenvector identity drifted")
        if (generator - identity) * v != u:
            raise AssertionError("base +1 Jordan-chain identity drifted")
        if self.eigenvector_constraint == sp.zeros(3 * FIELD_RANK, 1):
            raise AssertionError("the scoped chain unexpectedly became constrained")
        if self.generalized_constraint == sp.zeros(3 * FIELD_RANK, 1):
            raise AssertionError("the generalized vector unexpectedly became constrained")

        # Coefficientwise binding to the corrected N#=-N^T convention.
        for spatial, coefficients in zip(
            self.family.spatial_basis,
            self.quadratic_identity_deltas,
            strict=True,
        ):
            expected = _quadratic_identity_delta(
                self.reduction.full_symbol.identity_coefficients, spatial
            )
            if coefficients != expected:
                raise AssertionError("R6 quadratic identity coefficient drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        reduction = self.reduction
        u = reduction.jordan_eigenvector
        v = reduction.jordan_generalized_vector
        return {
            "schema": "pure-weyl-expanded-relative-r6-first-order-no-go-v1",
            "family_cross_certificate": (
                "curved_expanded_relative_witness_r6_family.json"
            ),
            "complete_aligned_Douglis_family": {
                "block_shape": [COMPLETE_RANK, COMPLETE_RANK],
                "scalar_branch": "cyclic D_alt=-2 Pi_(h00,f00,v0)",
                "formal_adjoint_identity": "Nsharp(zeta)=-N(zeta)^T",
                "variable_lower_left_block": (
                    "-N(zeta)^T (sum_a xi_a R6sharp_a)"
                ),
                "quadratic_monomial_count": len(SYMMETRIC_MONOMIALS),
                "parameter_count": len(self.quadratic_identity_deltas),
                "quadratic_basis_sha256": [
                    [_digest(coefficient) for coefficient in basis]
                    for basis in self.quadratic_identity_deltas
                ],
                "coefficientwise_exact": True,
            },
            "standard_first_order_reduction": {
                "state_rank": REDUCED_RANK,
                "state_order": [
                    "m[24]",
                    "p0[24]",
                    "p1[24]",
                    "p2[24]",
                    "p3[24]",
                    "x[92]",
                ],
                "temporal_coefficient_unchanged_by_spatial_family": True,
                "temporal_rank": reduction.temporal_coefficient.rank(),
                "temporal_determinant": int(
                    sp.factor(reduction.temporal_coefficient.det())
                ),
                "aligned_affine_delta_sha256": [
                    _digest(delta) for delta in self.aligned_reduction_deltas
                ],
            },
            "parameter_uniform_Jordan_chain": {
                "eigenvalue": "+1",
                "eigenvector_nonzero_entries": [
                    [index, str(u[index])]
                    for index in range(u.rows)
                    if u[index]
                ],
                "generalized_vector_nonzero_entries": [
                    [index, str(v[index])]
                    for index in range(v.rows)
                    if v[index]
                ],
                "base_chain": "(V-I)u=0, (V-I)v=u",
                "delta_A1_u_rank_over_all_parameters": sp.Matrix.hstack(
                    *self.eigenvector_delta_actions
                ).rank(),
                "delta_A1_v_rank_over_all_parameters": sp.Matrix.hstack(
                    *self.generalized_delta_actions
                ).rank(),
                "coefficientwise_actions_zero": True,
                "holds_for_all_46_spatial_parameters": True,
                "semisimple_standard_generator_exists_in_family": False,
            },
            "intrinsic_polynomial_Jordan_chain": {
                "pencil": "Q(z)=P_weighted((-z,1,0,0))",
                "characteristic_root": "z=1",
                "a0": "2 e_18 in M_aux[24]",
                "a1": "e_8 in M_aux[24]",
                "base_identities": [
                    "Q(1)a0=0",
                    "Q(1)a1+Q'(1)a0=0",
                ],
                "base_identity_defects": [0, 0],
                "delta_Q1_a0_rank_over_all_parameters": sp.Matrix.hstack(
                    *self.intrinsic_eigen_delta_actions
                ).rank(),
                "delta_Q1_a1_plus_delta_Qprime1_a0_rank": sp.Matrix.hstack(
                    *self.intrinsic_chain_delta_actions
                ).rank(),
                "all_46_parameter_directions_preserve_both_identities": True,
                "polynomial_elementary_divisor_semisimple": False,
                "regular_member_conclusion": (
                    "every regular family member has a nonsemisimple "
                    "elementary divisor at z=1"
                ),
                "irregular_member_conclusion": (
                    "an irregular square polynomial cannot be the principal "
                    "polynomial of an invertible-temporal symmetric-hyperbolic "
                    "strong linearization"
                ),
                "semisimple_faithful_strong_linearization_exists": False,
            },
            "positive_symmetrizer_obstruction": {
                "argument": (
                    "a positive symmetrizer makes every spatial principal "
                    "generator diagonalizable, while every faithful strong "
                    "linearization preserves the displayed intrinsic "
                    "polynomial Jordan chain"
                ),
                "positive_H_exists_for_any_faithful_strong_linearization": False,
                "parameter_uniform": True,
            },
            "constraint_scope": {
                "gradient_constraint": "G_i=p_i-xi_i m",
                "eigenvector_constraint_nonzero_entries": [
                    [index, str(self.eigenvector_constraint[index])]
                    for index in range(self.eigenvector_constraint.rows)
                    if self.eigenvector_constraint[index]
                ],
                "generalized_constraint_nonzero_entries": [
                    [index, str(self.generalized_constraint[index])]
                    for index in range(self.generalized_constraint.rows)
                    if self.generalized_constraint[index]
                ],
                "Jordan_chain_lies_in_constraint_subspace": False,
                "intrinsic_116_polynomial_chain_independently_certified": True,
                "scope_not_based_on_constraint_violating_chain": True,
            },
            "scoped_conclusion": (
                "the complete 46-parameter spatial R6sharp family preserves "
                "an intrinsic Jordan chain of the regular aligned 116-square "
                "Douglis polynomial.  Therefore no family member admits a "
                "semisimple faithful strong linearization or positive "
                "symmetrizer.  This does not rule out changing the relative "
                "witness incidence, temporal normalization, scalar branch, or "
                "enlarging the prolonged system"
            ),
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "warranted_atomic_flags": [
                "fixed_temporal_16_family_complete",
                "intrinsic_sensitivity_matrix_zero",
                "parameter_uniform_Jordan_chain",
                "strong_hyperbolicity_in_16_family=false",
                "symmetric_hyperbolicity_in_16_family=false",
                "fixed_temporal_16_no_go",
            ],
            "status_flags_promoted": [
                "fixed_temporal_16_family_complete",
                "intrinsic_sensitivity_matrix_zero",
                "parameter_uniform_Jordan_chain",
                "fixed_temporal_16_no_go",
            ],
            "fail_closed": True,
        }
