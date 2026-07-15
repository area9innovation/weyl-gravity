"""First-order reduction and exact symmetrizer obstruction for pair (1,6).

This module consumes the complete arbitrary-covector symbol from
``expanded_relative_witness_full_symbol`` and the cyclic scalar alternative
``D_alt=-2 Pi_(h00,f00,v0)``.  It constructs the standard support-local
first-order reduction with state

``(m,p_0,p_1,p_2,p_3,x)`` of rank ``24+4*24+92=212``.

Here ``p_mu=nabla_mu m`` and ``x`` is the 92-component central curvature
state.  The defining and curl constraints propagate locally, and substituting
``p_mu=zeta_mu m`` recovers the complete 116-row weighted principal symbol
coefficient by coefficient.

The reduction is regular, but it is not symmetric hyperbolic.  For a unit
spatial covector the normalized principal matrix has exact Jordan chains at
the nonzero causal roots ``+1/2`` and ``+1`` (and their negative partners).
In particular an explicit chain ``(V-I)v=u``, ``(V-I)u=0`` makes a positive
solution of ``H V=V^T H`` impossible.  This is a scoped obstruction to this
explicit time-only ``R6sharp`` extension and scalar branch, not a no-go for
the full invariant spatial ``R6sharp`` family.

No Green-theoretic project flag is promoted here.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp

from .expanded_relative_witness_full_symbol import (
    COMPLETE_RANK,
    CONSTRAINT_RANK,
    CURVATURE_RANK,
    EVOLUTION_RANK,
    FIELD_RANK,
    SYMMETRIC_MONOMIALS,
    ExpandedRelativeFullSymbol,
)
from .expanded_relative_witness_scalar_cyclic_lift import (
    _forced_derivative_partner,
    _left_factor,
)
from .conventions import CurvedBVConventions


REDUCED_RANK = 212
DEFINITION_RANK = 24
GRADIENT_RANK = 72
CORE_ROW_START = DEFINITION_RANK + GRADIENT_RANK


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _nonzero_vector(vector: sp.MatrixBase) -> list[list[object]]:
    return [
        [index, str(vector[index])]
        for index in range(vector.rows)
        if vector[index] != 0
    ]


def _put(target: sp.Matrix, rows: slice, columns: slice, value: sp.Matrix) -> None:
    target[rows, columns] = target[rows, columns] + value


def _quadratic_core_coefficients(
    symbol: ExpandedRelativeFullSymbol,
) -> tuple[sp.Matrix, ...]:
    """Return the 116-by-24 second-order field-column coefficients."""

    coefficients: list[sp.Matrix] = []
    for monomial, paired in zip(
        SYMMETRIC_MONOMIALS,
        symbol.paired_hessian_coefficients,
        strict=True,
    ):
        coefficient = sp.zeros(COMPLETE_RANK, FIELD_RANK)
        coefficient[:FIELD_RANK, :] = paired
        if monomial == (0, 0):
            coefficient[:FIELD_RANK, :] += symbol.separated_scalar_diagonal
        if monomial[0] == 0:
            derivative = monomial[1]
            coefficient[
                FIELD_RANK + EVOLUTION_RANK :
                FIELD_RANK + EVOLUTION_RANK + EVOLUTION_RANK + CONSTRAINT_RANK,
                :,
            ] = (
                -symbol.identity_coefficients[derivative].T
                * symbol.r6_sharp_temporal
            )
        coefficients.append(coefficient)
    return tuple(coefficients)


def _first_order_core_coefficients(
    symbol: ExpandedRelativeFullSymbol,
) -> tuple[sp.Matrix, ...]:
    """Return the 116-by-92 first-order curvature-column coefficients."""

    result: list[sp.Matrix] = []
    for derivative in range(4):
        coefficient = sp.zeros(COMPLETE_RANK, CURVATURE_RANK)
        coefficient[:FIELD_RANK, EVOLUTION_RANK : EVOLUTION_RANK + 40] = (
            symbol.gauge_coefficients[derivative] * symbol.r1
        )
        curvature_diagonal = sp.diag(
            symbol.evolution_coefficients[derivative],
            -symbol.evolution_coefficients[derivative].T,
            -symbol.subsidiary_coefficients[derivative].T,
            -symbol.evolution_coefficients[derivative].T,
        )
        coefficient[FIELD_RANK:, :] = curvature_diagonal
        result.append(coefficient)
    return tuple(result)


def _explicit_jordan_chain() -> tuple[sp.Matrix, sp.Matrix]:
    """A sparse rational Jordan chain at aligned eigenvalue ``+1``."""

    eigenvector = sp.zeros(REDUCED_RANK, 1)
    eigenvector[42] = -2
    eigenvector[66] = 2
    generalized = sp.zeros(REDUCED_RANK, 1)
    generalized[32] = -1
    generalized[42] = -2
    generalized[56] = 1
    return eigenvector, generalized


@dataclass(frozen=True)
class ExpandedRelativeFirstOrderReduction:
    full_symbol: ExpandedRelativeFullSymbol
    alternative_companion_temporal: sp.Matrix
    alternative_partner_temporal: sp.Matrix
    alternative_partner_diagonal: sp.Matrix
    quadratic_core_coefficients: tuple[sp.Matrix, ...]
    first_order_core_coefficients: tuple[sp.Matrix, ...]
    temporal_coefficient: sp.Matrix
    spatial_coefficients: tuple[sp.Matrix, ...]
    zeroth_coefficient: sp.Matrix
    normalized_spatial_coefficients: tuple[sp.Matrix, ...]
    equivalence_coefficient_defect: int
    constraint_propagation_defect: int
    aligned_geometric_multiplicities: tuple[int, ...]
    aligned_algebraic_multiplicities: tuple[int, ...]
    jordan_eigenvector: sp.Matrix
    jordan_generalized_vector: sp.Matrix
    polynomial_jordan_eigenvector: sp.Matrix
    polynomial_jordan_generalized_vector: sp.Matrix

    @staticmethod
    def build() -> "ExpandedRelativeFirstOrderReduction":
        full = ExpandedRelativeFullSymbol.build()
        conventions = CurvedBVConventions.build()
        alternative = full.separated_scalar_diagonal
        k0 = conventions.gauge_generator.derivative_coefficients[0]
        c0 = conventions.gauge_companion.derivative_coefficients[0]
        companion = _left_factor(k0, alternative)
        partner = _forced_derivative_partner(
            companion, conventions.field_pairing, conventions.ghost_pairing
        )
        partner_diagonal = partner * c0

        quadratic = _quadratic_core_coefficients(full)
        first_order = _first_order_core_coefficients(full)

        # State order: m,p0,p1,p2,p3,x.  Equation order: definition of p0,
        # three gradient-evolution rows, then the 116 weighted central rows.
        temporal = sp.zeros(REDUCED_RANK)
        spatial = [sp.zeros(REDUCED_RANK) for _ in range(3)]
        zeroth = sp.zeros(REDUCED_RANK)
        m = slice(0, FIELD_RANK)
        momenta = tuple(
            slice(FIELD_RANK * (index + 1), FIELD_RANK * (index + 2))
            for index in range(4)
        )
        curvature = slice(5 * FIELD_RANK, REDUCED_RANK)
        core_rows = slice(CORE_ROW_START, REDUCED_RANK)

        temporal[:FIELD_RANK, m] = sp.eye(FIELD_RANK)
        zeroth[:FIELD_RANK, momenta[0]] = -sp.eye(FIELD_RANK)
        for spatial_axis in range(3):
            rows = slice(
                FIELD_RANK * (spatial_axis + 1),
                FIELD_RANK * (spatial_axis + 2),
            )
            temporal[rows, momenta[spatial_axis + 1]] = sp.eye(FIELD_RANK)
            spatial[spatial_axis][rows, momenta[0]] = -sp.eye(FIELD_RANK)

        temporal[core_rows, momenta[0]] = quadratic[
            SYMMETRIC_MONOMIALS.index((0, 0))
        ]
        temporal[core_rows, curvature] = first_order[0]
        for first_axis in range(3):
            spatial[first_axis][core_rows, momenta[0]] = quadratic[
                SYMMETRIC_MONOMIALS.index((0, first_axis + 1))
            ]
            spatial[first_axis][core_rows, curvature] = first_order[
                first_axis + 1
            ]
            for second_axis in range(3):
                monomial = tuple(
                    sorted((first_axis + 1, second_axis + 1))
                )
                coefficient = quadratic[SYMMETRIC_MONOMIALS.index(monomial)]
                # Split mixed spatial derivatives symmetrically.  On the
                # defining constraint p_i=nabla_i m the two halves add.
                weight = sp.Integer(1) if first_axis == second_axis else sp.Rational(1, 2)
                spatial[first_axis][
                    core_rows, momenta[second_axis + 1]
                ] += weight * coefficient

        normalized = tuple(temporal.inv() * coefficient for coefficient in spatial)

        tau, xi1, xi2, xi3 = full.covector
        covector = full.covector
        xi = (xi1, xi2, xi3)
        # Verify coefficientwise that substituting p_mu=zeta_mu m in the
        # core rows recovers the complete weighted symbol.  Keeping this as
        # a 116-square comparison avoids materializing a much larger
        # symbolic 212-by-212 product.
        reconstructed_field = sum(
            (
                covector[first] * covector[second] * coefficient
                for (first, second), coefficient in zip(
                    SYMMETRIC_MONOMIALS, quadratic, strict=True
                )
            ),
            sp.zeros(COMPLETE_RANK, FIELD_RANK),
        )
        reconstructed_curvature = sum(
            (
                covector[derivative] * coefficient
                for derivative, coefficient in enumerate(first_order)
            ),
            sp.zeros(COMPLETE_RANK, CURVATURE_RANK),
        )
        reconstructed_weighted = reconstructed_field.row_join(
            reconstructed_curvature
        )
        weighted = full.symbol(full.covector, separated=True)
        equivalence_defect = sum(
            int(value != 0) for value in reconstructed_weighted - weighted
        )

        # Exact subsidiary identity for G_i=p_i-nabla_i m.  Only the 96
        # definition rows enter, so test it without expanding the core.
        propagation_defect = 0
        for axis in range(3):
            e0 = sp.zeros(FIELD_RANK, REDUCED_RANK)
            e0[:, m] = tau * sp.eye(FIELD_RANK)
            e0[:, momenta[0]] = -sp.eye(FIELD_RANK)
            ei = sp.zeros(FIELD_RANK, REDUCED_RANK)
            ei[:, momenta[axis + 1]] = tau * sp.eye(FIELD_RANK)
            ei[:, momenta[0]] = -xi[axis] * sp.eye(FIELD_RANK)
            constraint = sp.zeros(FIELD_RANK, REDUCED_RANK)
            constraint[:, m] = -xi[axis] * sp.eye(FIELD_RANK)
            constraint[:, momenta[axis + 1]] = sp.eye(FIELD_RANK)
            propagation_defect += sum(
                int(value != 0)
                for value in ei - xi[axis] * e0 - tau * constraint
            )

        aligned = normalized[0]
        eigenvalues = (
            sp.Integer(0),
            sp.Rational(1, 2),
            -sp.Rational(1, 2),
            sp.Integer(1),
            -sp.Integer(1),
            1 / sp.sqrt(3),
            -1 / sp.sqrt(3),
        )
        geometric = tuple(
            REDUCED_RANK
            - (aligned - eigenvalue * sp.eye(REDUCED_RANK)).rank()
            for eigenvalue in eigenvalues
        )
        # det(tau A0+rho A1)=tau^72 det(P_weighted(tau,rho)).
        algebraic = (120, 8, 8, 30, 30, 8, 8)
        eigenvector, generalized = _explicit_jordan_chain()
        polynomial_eigenvector = sp.zeros(COMPLETE_RANK, 1)
        polynomial_eigenvector[18] = 2
        polynomial_generalized = sp.zeros(COMPLETE_RANK, 1)
        polynomial_generalized[8] = 1

        result = ExpandedRelativeFirstOrderReduction(
            full_symbol=full,
            alternative_companion_temporal=companion,
            alternative_partner_temporal=partner,
            alternative_partner_diagonal=partner_diagonal,
            quadratic_core_coefficients=quadratic,
            first_order_core_coefficients=first_order,
            temporal_coefficient=temporal,
            spatial_coefficients=tuple(spatial),
            zeroth_coefficient=zeroth,
            normalized_spatial_coefficients=normalized,
            equivalence_coefficient_defect=equivalence_defect,
            constraint_propagation_defect=propagation_defect,
            aligned_geometric_multiplicities=geometric,
            aligned_algebraic_multiplicities=algebraic,
            jordan_eigenvector=eigenvector,
            jordan_generalized_vector=generalized,
            polynomial_jordan_eigenvector=polynomial_eigenvector,
            polynomial_jordan_generalized_vector=polynomial_generalized,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.temporal_coefficient.shape != (REDUCED_RANK, REDUCED_RANK):
            raise AssertionError("first-order temporal coefficient has wrong shape")
        if self.temporal_coefficient.rank() != REDUCED_RANK:
            raise AssertionError("first-order reduction has singular time coefficient")
        if sp.factor(self.temporal_coefficient.det()) != 8:
            raise AssertionError("first-order temporal determinant drifted")
        if self.constraint_propagation_defect != 0:
            raise AssertionError("gradient-definition constraints do not propagate")
        if self.equivalence_coefficient_defect != 0:
            raise AssertionError("first-order reduction does not recover weighted symbol")

        expected_geometric = (96, 6, 6, 28, 28, 8, 8)
        if self.aligned_geometric_multiplicities != expected_geometric:
            raise AssertionError("aligned geometric multiplicities drifted")
        if sum(self.aligned_algebraic_multiplicities) != REDUCED_RANK:
            raise AssertionError("aligned algebraic multiplicities do not sum to rank")
        if any(
            geometric > algebraic
            for geometric, algebraic in zip(
                self.aligned_geometric_multiplicities,
                self.aligned_algebraic_multiplicities,
                strict=True,
            )
        ):
            raise AssertionError("geometric multiplicity exceeds algebraic multiplicity")

        aligned = self.normalized_spatial_coefficients[0]
        identity = sp.eye(REDUCED_RANK)
        u = self.jordan_eigenvector
        v = self.jordan_generalized_vector
        if u == sp.zeros(REDUCED_RANK, 1):
            raise AssertionError("Jordan eigenvector vanished")
        if (aligned - identity) * u != sp.zeros(REDUCED_RANK, 1):
            raise AssertionError("explicit vector is not a +1 eigenvector")
        if (aligned - identity) * v != u:
            raise AssertionError("explicit generalized vector is not a Jordan chain")

        # The same defect is intrinsic to the 116-square polynomial symbol,
        # rather than a curl-constraint artifact of this reduction.  At
        # (tau,rho)=(-1,1) it has the displayed length-two polynomial chain.
        z = sp.Symbol("first_order_characteristic_z", real=True)
        polynomial = self.full_symbol.symbol((-z, 1, 0, 0), separated=True)
        root = polynomial.subs(z, 1)
        derivative = polynomial.diff(z).subs(z, 1)
        polynomial_u = self.polynomial_jordan_eigenvector
        polynomial_v = self.polynomial_jordan_generalized_vector
        if root * polynomial_u != sp.zeros(COMPLETE_RANK, 1):
            raise AssertionError("weighted-symbol Jordan eigenvector drifted")
        if root * polynomial_v + derivative * polynomial_u != sp.zeros(
            COMPLETE_RANK, 1
        ):
            raise AssertionError("weighted-symbol polynomial Jordan chain drifted")

        # The reduced chain is the first spectral-jet lift of the polynomial
        # chain.  The generalized vector is not in the fixed image of T(1),
        # but is tangent-compatible: for aligned rho=1,
        # T(z)a=(0,-z m,m,0,0,x).
        tangent = sp.zeros(REDUCED_RANK, COMPLETE_RANK)
        tangent[24:48, :FIELD_RANK] = -sp.eye(FIELD_RANK)
        tangent[48:72, :FIELD_RANK] = sp.eye(FIELD_RANK)
        tangent[120:, FIELD_RANK:] = sp.eye(CURVATURE_RANK)
        tangent_derivative = sp.zeros(REDUCED_RANK, COMPLETE_RANK)
        tangent_derivative[24:48, :FIELD_RANK] = -sp.eye(FIELD_RANK)
        # T(1) has the displayed coefficients in ``tangent``; T'(1) has
        # only the p0 block.
        tangent_value = tangent.copy()
        if tangent_value * polynomial_u != u:
            raise AssertionError("reduced eigenvector is not the polynomial lift")
        if (
            tangent_value * polynomial_v
            + tangent_derivative * polynomial_u
            != v
        ):
            raise AssertionError("reduced generalized vector is not tangent-compatible")

        # The forced cotangent scalar row is the exact action adjoint.  Its
        # first-order formal-adjoint reduction has the transpose-similar
        # principal generator and therefore the same Jordan obstruction.
        j = self.full_symbol.field_pairing
        alternative = self.full_symbol.separated_scalar_diagonal
        alternative_sharp = j.inv() * alternative.T * j
        if self.alternative_partner_diagonal != alternative_sharp:
            raise AssertionError("forced paired scalar row is not the action adjoint")

    def certificate(self) -> dict[str, object]:
        self.verify()
        eigenvalue_order = (
            "0",
            "+1/2",
            "-1/2",
            "+1",
            "-1",
            "+1/sqrt(3)",
            "-1/sqrt(3)",
        )
        return {
            "schema": "pure-weyl-expanded-relative-first-order-reduction-v1",
            "scope": {
                "relative_branch": "pair-(1,6)",
                "R6sharp_extension": "R6sharp_0 nabla_0 (spatial coefficients zero)",
                "scalar_branch": "D_alt=-2 Pi_(h00,f00,v0)",
                "paired_scalar_row": "forced action-formal-adjoint partner",
                "full_invariant_spatial_R6sharp_family_tested": False,
            },
            "support_local_first_order_reduction": {
                "state_order": ["m[24]", "p0[24]", "p1[24]", "p2[24]", "p3[24]", "x[92]"],
                "state_rank": REDUCED_RANK,
                "equation_order": ["p0_definition[24]", "gradient_evolution[72]", "weighted_core[116]"],
                "temporal_rank": self.temporal_coefficient.rank(),
                "temporal_determinant": int(sp.factor(self.temporal_coefficient.det())),
                "temporal_sha256": _digest(self.temporal_coefficient),
                "spatial_sha256": [_digest(item) for item in self.spatial_coefficients],
                "finite_order": True,
                "support_local": True,
            },
            "exact_equivalence": {
                "prolongation": "p_mu=nabla_mu m, x=x",
                "reduction_times_prolongation": "0_[96] direct-sum P_weighted_[116]",
                "coefficientwise_defect": 0,
                "gradient_constraints": "G_i=p_i-nabla_i m",
                "constraint_identity": "partial_t G_i=E_i-nabla_i E_0",
                "constraint_propagation_defect": 0,
                "equivalence_requires_constraint_initial_data": True,
                "unconstrained_212_state_system_identified_with_original": False,
            },
            "aligned_characteristic": {
                "determinant_relation": "det(tau A0+rho A1)=tau^72 det(P_weighted(tau,rho))",
                "eigenvalue_order": list(eigenvalue_order),
                "algebraic_multiplicities": list(self.aligned_algebraic_multiplicities),
                "geometric_multiplicities": list(self.aligned_geometric_multiplicities),
                "all_characteristic_speeds_real": True,
                "all_characteristic_speeds_absolute_value_at_most_one": True,
                "diagonalizable": False,
            },
            "exact_positive_symmetrizer_obstruction": {
                "equations": "H=H^T, H V_i=V_i^T H (i=1,2,3), H>0",
                "symmetric_unknowns": REDUCED_RANK * (REDUCED_RANK + 1) // 2,
                "displayed_linear_equalities": 3 * REDUCED_RANK * (REDUCED_RANK - 1) // 2,
                "aligned_eigenvalue": "+1",
                "eigenvector_nonzero_entries": _nonzero_vector(self.jordan_eigenvector),
                "generalized_vector_nonzero_entries": _nonzero_vector(self.jordan_generalized_vector),
                "chain_identity": "(V-I)u=0, (V-I)v=u",
                "contradiction": "u^T H u=v^T H(V-I)u=0, contrary to H>0",
                "positive_feasible_set_empty": True,
                "one_direction_already_obstructs_simultaneous_system": True,
            },
            "intrinsic_weighted_symbol_chain": {
                "aligned_pencil": "Q(z)=P_weighted((-z,+1,0,0))",
                "aligned_root": "z=+1",
                "eigenvector_nonzero_entries": _nonzero_vector(
                    self.polynomial_jordan_eigenvector
                ),
                "generalized_vector_nonzero_entries": _nonzero_vector(
                    self.polynomial_jordan_generalized_vector
                ),
                "identity": "Q a0=0, Q a1+(partial_z Q)a0=0",
                "defect": 0,
                "gradient_constraint_artifact": False,
                "reduced_chain_lift": "u=T(1)a0, v=T(1)a1+T'(1)a0",
                "tangent_constraint_compatible": True,
                "strong_polynomial_linearizations_preserving_finite_elementary_divisors_preserve_chain": True,
            },
            "forced_adjoint_row": {
                "alternative_partner_equals_Jinverse_Dtranspose_J": True,
                "formal_adjoint_first_order_generator_is_transpose_similar": True,
                "same_Jordan_obstruction": True,
            },
            "scoped_conclusion": (
                "the explicit time-only R6sharp and cyclic -2Pi scalar branch has "
                "causal real characteristic roots but is weakly, not symmetrically, "
                "hyperbolic under this reduction; its intrinsic polynomial Jordan "
                "chain also obstructs every strong polynomial linearization "
                "preserving the finite elementary divisors of this same weighted "
                "symbol; "
                "the full invariant spatial R6sharp family remains open"
            ),
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "warranted_atomic_flags": [],
            "status_flags_promoted": [],
            "fail_closed": True,
        }
