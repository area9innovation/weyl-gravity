"""Complete invariant cubic gate for a lower-order auxiliary complement.

This is the first finite stage after the exact prenormal identity.  The
candidate complement is

``D=D_naive+X_1^mu nabla_mu+X_0``.

Both ``DP`` and ``PD`` are asked to admit products of two second-order
scalar-principal factors.  At derivative order three curvature commutators
cannot contribute, and the necessary equations are exactly

``X_1 P_2=q S_L`` and ``P_2 X_1=q S_R``.

Here every coefficient is taken in the *complete* parallel SO(3)-invariant
family.  The full quadratic/lower-order factor equations are deliberately
not inferred from this cubic solution family.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp
from sympy.polys.matrices import DomainMatrix

from .auxiliary_prenormal_symbol import AuxiliaryPrenormalSymbol
from .derivative_normal_form import ParallelCylinderNormalForm
from .invariant_pairings import (
    InvariantFibrePairingAnsatz,
    _rotation_generators,
)


def _field_first_order_invariance_matrix() -> sp.Matrix:
    """Infinitesimal holonomy equations for ``X^mu nabla_mu``.

    Column-major vectorization gives
    ``vec(TX-XT)=(I tensor T-T^T tensor I)vec(X)``.  The four derivative
    coefficients transform as one time scalar plus one spatial vector.
    """

    ansatz = InvariantFibrePairingAnsatz.build()
    identity = sp.eye(24)
    blocks = []
    for field_generator, covector_generator in zip(
        ansatz.field_generators, _rotation_generators(), strict=True
    ):
        commutator = (
            sp.kronecker_product(identity, field_generator)
            - sp.kronecker_product(field_generator.T, identity)
        )
        blocks.append(
            sp.kronecker_product(sp.eye(4), commutator)
            + sp.kronecker_product(covector_generator, sp.eye(24 * 24))
        )
    return sp.Matrix.vstack(*blocks)


def _coefficient_tuple(vector: sp.Matrix) -> tuple[sp.Matrix, ...]:
    return tuple(
        sp.Matrix(
            24,
            24,
            lambda row, column: vector[axis * 576 + column * 24 + row],
        )
        for axis in range(4)
    )


def _cubic_coefficient_vector(
    expression: sp.Matrix,
    covector: tuple[sp.Symbol, ...],
) -> sp.SparseMatrix:
    monomials = tuple(
        covector[a] * covector[b] * covector[c]
        for a in range(4)
        for b in range(a, 4)
        for c in range(b, 4)
    )
    values = []
    for row in range(24):
        for column in range(24):
            polynomial = sp.Poly(expression[row, column], *covector)
            values.extend(polynomial.coeff_monomial(item) for item in monomials)
    return sp.SparseMatrix(len(values), 1, values)


@dataclass(frozen=True)
class AuxiliaryLowerOrderFactorAnsatz:
    zeroth_invariant_parameters: int
    first_invariance_shape: tuple[int, int]
    first_invariance_rank: int
    first_invariant_parameters: int
    left_cubic_shape: tuple[int, int]
    left_cubic_rank: int
    left_cubic_solution_dimension: int
    left_correction_projection_rank: int
    simultaneous_cubic_shape: tuple[int, int]
    simultaneous_cubic_rank: int
    simultaneous_solution_dimension: int
    simultaneous_correction_projection_rank: int
    simultaneous_left_sum_projection_rank: int
    simultaneous_right_sum_projection_rank: int

    @staticmethod
    def build() -> "AuxiliaryLowerOrderFactorAnsatz":
        normal_form = ParallelCylinderNormalForm.build()
        normal_form.verify()
        invariance = _field_first_order_invariance_matrix()
        invariance_domain = DomainMatrix.from_Matrix(invariance)
        invariance_rank = invariance_domain.rank()
        basis = invariance_domain.nullspace().to_Matrix().T
        if basis.shape != (2304, 93):
            raise AssertionError("complete invariant first-order basis drifted")

        prenormal = AuxiliaryPrenormalSymbol.build()
        covector = prenormal.covector
        zeta = sp.Matrix(covector)
        principal = prenormal.field_principal_symbol
        q = prenormal.wave_quadratic

        left_columns = []
        right_columns = []
        scalar_columns = []
        for column in range(basis.cols):
            coefficients = _coefficient_tuple(basis[:, column])
            first_symbol = sum(
                (zeta[axis] * coefficients[axis] for axis in range(4)),
                sp.zeros(24),
            )
            left_columns.append(
                _cubic_coefficient_vector(
                    sp.Matrix(first_symbol * principal).applyfunc(sp.expand),
                    covector,
                )
            )
            right_columns.append(
                _cubic_coefficient_vector(
                    sp.Matrix(principal * first_symbol).applyfunc(sp.expand),
                    covector,
                )
            )
            scalar_columns.append(
                _cubic_coefficient_vector(
                    sp.Matrix(q * first_symbol).applyfunc(sp.expand), covector
                )
            )
        left = sp.SparseMatrix.hstack(*left_columns)
        right = sp.SparseMatrix.hstack(*right_columns)
        scalar = sp.SparseMatrix.hstack(*scalar_columns)
        zero = sp.zeros(left.rows, basis.cols)

        left_equations = left.row_join(-scalar)
        left_domain = DomainMatrix.from_Matrix(left_equations)
        left_rank = left_domain.rank()
        left_kernel = left_domain.nullspace().to_Matrix().T

        simultaneous = sp.Matrix.vstack(
            left.row_join(-scalar).row_join(zero),
            right.row_join(zero).row_join(-scalar),
        )
        simultaneous_domain = DomainMatrix.from_Matrix(simultaneous)
        simultaneous_rank = simultaneous_domain.rank()
        simultaneous_kernel = simultaneous_domain.nullspace().to_Matrix().T

        result = AuxiliaryLowerOrderFactorAnsatz(
            zeroth_invariant_parameters=38,
            first_invariance_shape=invariance.shape,
            first_invariance_rank=invariance_rank,
            first_invariant_parameters=basis.cols,
            left_cubic_shape=left_equations.shape,
            left_cubic_rank=left_rank,
            left_cubic_solution_dimension=left_equations.cols - left_rank,
            left_correction_projection_rank=DomainMatrix.from_Matrix(
                left_kernel[: basis.cols, :]
            ).rank(),
            simultaneous_cubic_shape=simultaneous.shape,
            simultaneous_cubic_rank=simultaneous_rank,
            simultaneous_solution_dimension=(
                simultaneous.cols - simultaneous_rank
            ),
            simultaneous_correction_projection_rank=DomainMatrix.from_Matrix(
                simultaneous_kernel[: basis.cols, :]
            ).rank(),
            simultaneous_left_sum_projection_rank=DomainMatrix.from_Matrix(
                simultaneous_kernel[basis.cols : 2 * basis.cols, :]
            ).rank(),
            simultaneous_right_sum_projection_rank=DomainMatrix.from_Matrix(
                simultaneous_kernel[2 * basis.cols :, :]
            ).rank(),
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.zeroth_invariant_parameters != 38:
            raise AssertionError("invariant endomorphism dimension drifted")
        if self.first_invariance_shape != (6912, 2304):
            raise AssertionError("first-order invariance ledger shape drifted")
        if (self.first_invariance_rank, self.first_invariant_parameters) != (
            2211,
            93,
        ):
            raise AssertionError("complete first-order invariant family drifted")
        if (
            self.left_cubic_shape,
            self.left_cubic_rank,
            self.left_cubic_solution_dimension,
            self.left_correction_projection_rank,
        ) != ((11520, 186), 121, 65, 65):
            raise AssertionError("left cubic divisibility solve drifted")
        if (
            self.simultaneous_cubic_shape,
            self.simultaneous_cubic_rank,
            self.simultaneous_solution_dimension,
            self.simultaneous_correction_projection_rank,
            self.simultaneous_left_sum_projection_rank,
            self.simultaneous_right_sum_projection_rank,
        ) != ((23040, 279), 234, 45, 45, 45, 45):
            raise AssertionError("simultaneous cubic divisibility solve drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-auxiliary-lower-order-factor-ansatz-v1",
            "ansatz_completeness": {
                "isotropy": "SO(3) holonomy of the cylinder",
                "field_decomposition": "5 V_0 + 3 V_1 + 2 V_2",
                "zeroth_order_dimension": self.zeroth_invariant_parameters,
                "zeroth_order_derivation": "5^2+3^2+2^2=38",
                "first_order_dimension": self.first_invariant_parameters,
                "first_order_derivation": (
                    "38 time intertwiners plus 55 spatial intertwiners; exact "
                    "infinitesimal constraint rank 2211 on 2304 coefficients"
                ),
                "first_order_constraint_shape": list(self.first_invariance_shape),
                "first_order_constraint_rank": self.first_invariance_rank,
                "parallel_globalization": True,
            },
            "candidate": {
                "complement": "D=D_naive+X_1^mu nabla_mu+X_0",
                "left_factorization": "DP=L_- L_+",
                "right_factorization": "PD=R_- R_+",
                "factor_principal_symbols": "q I_24",
                "factor_first_order_matrices_allowed": True,
            },
            "exact_cubic_gate": {
                "reason_curvature_does_not_enter": (
                    "commuting two derivatives lowers order by two on the "
                    "parallel-curvature cylinder, so order three is unchanged"
                ),
                "left_equation": "X_1 P_2=q S_L",
                "right_equation": "P_2 X_1=q S_R",
                "left_matrix_shape": list(self.left_cubic_shape),
                "left_rank": self.left_cubic_rank,
                "left_solution_dimension": self.left_cubic_solution_dimension,
                "simultaneous_matrix_shape": list(self.simultaneous_cubic_shape),
                "simultaneous_rank": self.simultaneous_cubic_rank,
                "simultaneous_solution_dimension": (
                    self.simultaneous_solution_dimension
                ),
                "projection_ranks_X1_SL_SR": [
                    self.simultaneous_correction_projection_rank,
                    self.simultaneous_left_sum_projection_rank,
                    self.simultaneous_right_sum_projection_rank,
                ],
                "cubic_obstruction": False,
            },
            "remaining_exact_solve": {
                "quadratic_factor_equations_assembled": False,
                "curvature_commutators_required": True,
                "zeroth_and_first_order_factor_coefficients_required": True,
                "nonlinear_terms": "products of the two factor first-order matrices",
                "full_lower_order_solution_found": False,
                "left_null_obstruction_found": False,
            },
            "outcome": {
                "complete_invariant_ansatz_declared": True,
                "simultaneous_cubic_solution_family_dimension": (
                    self.simultaneous_solution_dimension
                ),
                "mixed_order_factorization_proved": False,
                "mixed_order_green_realization": False,
                "flag_promoted": False,
            },
            "theorem_boundary": (
                "the complete invariant first-order family passes the exact "
                "simultaneous cubic divisibility gate with a 45-parameter family; "
                "the curvature-corrected nonlinear quadratic and lower equations "
                "remain unsolved, so no factorization or Green theorem follows"
            ),
        }
