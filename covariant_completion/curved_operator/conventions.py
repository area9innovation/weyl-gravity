"""Single-source conventions and exact first-order curved gauge data.

The curved auxiliary calculation previously obtained its metric, component
orders and fibre pairings indirectly from several modules.  This file makes
those choices one immutable object.  In particular it constructs the exact
linearized gauge generator on the cylinder as

``K = sum_mu K^mu nabla_mu + K^0``

and derives the modified de Donder companion from the formal-adjoint
identity

``Y_gh C = K^sharp J_aux``.

All coefficient matrices are normal-orthonormal-frame components of global
natural differential operators.  Their coefficients are parallel tensors,
so the table, together with ``nabla``, is an exact global definition rather
than a principal symbol.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import hashlib

import sympy as sp

from covariant_completion.auxiliary_witness import OrdinaryDerivativeWeylSystem

from .cylinder_background import CylinderBackground


SYMMETRIC_COORDINATES = (
    (0, 0),
    (0, 1),
    (0, 2),
    (0, 3),
    (1, 1),
    (1, 2),
    (1, 3),
    (2, 2),
    (2, 3),
    (3, 3),
)


def _digest_matrices(matrices: tuple[sp.Matrix, ...]) -> str:
    payload = "\n".join(
        sp.srepr(sp.ImmutableDenseMatrix(matrix)) for matrix in matrices
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@lru_cache(maxsize=1)
def _ordinary_system() -> OrdinaryDerivativeWeylSystem:
    """Build the expensive immutable flat normalization anchor once."""

    return OrdinaryDerivativeWeylSystem.build()


@dataclass(frozen=True)
class FirstOrderOperator:
    """A parallel-coefficient natural operator ``A^mu nabla_mu+A^0``."""

    derivative_coefficients: tuple[sp.Matrix, ...]
    zeroth_coefficient: sp.Matrix
    input_rank: int
    output_rank: int

    def symbol(self, covector: sp.Matrix) -> sp.Matrix:
        if covector.shape != (4, 1):
            raise ValueError("the symbol covector must have shape (4,1)")
        return sp.simplify(
            self.zeroth_coefficient
            + sum(
                (
                    covector[axis] * self.derivative_coefficients[axis]
                    for axis in range(4)
                ),
                sp.zeros(self.output_rank, self.input_rank),
            )
        )

    def verify(self) -> None:
        if len(self.derivative_coefficients) != 4:
            raise AssertionError("a four-dimensional operator needs four derivative tables")
        expected = (self.output_rank, self.input_rank)
        if self.zeroth_coefficient.shape != expected:
            raise AssertionError("wrong zeroth-order coefficient shape")
        if any(matrix.shape != expected for matrix in self.derivative_coefficients):
            raise AssertionError("wrong first-order coefficient shape")

    @property
    def coefficient_sha256(self) -> str:
        self.verify()
        return _digest_matrices(
            self.derivative_coefficients + (self.zeroth_coefficient,)
        )


@dataclass(frozen=True)
class CurvedBVConventions:
    """Convention anchor shared by the curved operator/retract/current work."""

    background: CylinderBackground
    field_order: tuple[str, ...]
    ghost_order: tuple[str, ...]
    tensor_coordinates: tuple[tuple[int, int], ...]
    field_pairing: sp.Matrix
    ghost_pairing: sp.Matrix
    gauge_generator: FirstOrderOperator
    gauge_companion: FirstOrderOperator

    @staticmethod
    def build() -> "CurvedBVConventions":
        background = CylinderBackground.build()
        source = _ordinary_system()

        derivative = tuple(sp.zeros(24, 9) for _ in range(4))
        derivative = tuple(matrix.copy() for matrix in derivative)
        zeroth = sp.zeros(24, 9)

        def tensor_coordinates(tensor: sp.Matrix) -> sp.Matrix:
            return sp.Matrix([tensor[a, b] for a, b in SYMMETRIC_COORDINATES])

        # Ghosts are covectors (xi_a,kappa_a) and a scalar sigma.  The
        # diffeomorphism action on the nonzero parallel auxiliary background
        # is retained in the f row.
        for axis in range(4):
            for column in range(4):
                xi = sp.zeros(4, 1)
                xi[column] = 1
                derivative[axis][:10, column] = tensor_coordinates(
                    sp.eye(4)[:, axis] * xi.T + xi * sp.eye(4)[axis, :]
                )

                xi_up = background.inverse_metric * xi
                background_xi = background.auxiliary_background * xi_up
                derivative[axis][10:20, column] = tensor_coordinates(
                    sp.eye(4)[:, axis] * background_xi.T
                    + background_xi * sp.eye(4)[axis, :]
                )

                kappa = sp.zeros(4, 1)
                kappa[column] = 1
                derivative[axis][10:20, 4 + column] = tensor_coordinates(
                    sp.eye(4)[:, axis] * kappa.T
                    + kappa * sp.eye(4)[axis, :]
                )

            derivative[axis][:10, 8] = sp.zeros(10, 1)
            derivative[axis][20:24, 8] = sp.eye(4)[:, axis]

        # Weyl scaling of the metric is algebraic; the conformal-boost
        # Stueckelberg transformation is algebraic in the vector row.
        zeroth[:10, 8] = tensor_coordinates(background.metric)
        zeroth[20:24, 4:8] = -sp.eye(4)

        generator = FirstOrderOperator(
            derivative_coefficients=derivative,
            zeroth_coefficient=zeroth,
            input_rank=9,
            output_rank=24,
        )

        # Compact-support formal adjoint: (A^mu nabla_mu)^sharp is
        # -A^{mu,T} nabla_mu because all coefficient tensors are parallel.
        # This is the unique companion in the fixed nondegenerate pairings.
        inverse_ghost_pairing = source.gauge_fixing_pairing.inv()
        companion_derivative = tuple(
            sp.simplify(
                -inverse_ghost_pairing * matrix.T * source.field_fibre_pairing
            )
            for matrix in derivative
        )
        companion_zeroth = sp.simplify(
            inverse_ghost_pairing
            * zeroth.T
            * source.field_fibre_pairing
        )
        companion = FirstOrderOperator(
            derivative_coefficients=companion_derivative,
            zeroth_coefficient=companion_zeroth,
            input_rank=24,
            output_rank=9,
        )

        result = CurvedBVConventions(
            background=background,
            field_order=("h[10]", "f[10]", "v[4]"),
            ghost_order=("xi[4]", "kappa[4]", "sigma[1]"),
            tensor_coordinates=SYMMETRIC_COORDINATES,
            field_pairing=source.field_fibre_pairing,
            ghost_pairing=source.gauge_fixing_pairing,
            gauge_generator=generator,
            gauge_companion=companion,
        )
        result.verify()
        return result

    def verify(self) -> None:
        self.background.verify()
        self.gauge_generator.verify()
        self.gauge_companion.verify()
        if self.field_pairing.shape != (24, 24) or self.field_pairing.rank() != 24:
            raise AssertionError("J_aux is not a nondegenerate 24-component pairing")
        if self.ghost_pairing.shape != (9, 9) or self.ghost_pairing.rank() != 9:
            raise AssertionError("Y_gh is not a nondegenerate 9-component pairing")

        # Coefficientwise proof of Y C=K^sharp J, including all lower-order
        # terms.  This is stronger than checking a polynomial principal symbol.
        for axis in range(4):
            defect = sp.simplify(
                self.ghost_pairing
                * self.gauge_companion.derivative_coefficients[axis]
                + self.gauge_generator.derivative_coefficients[axis].T
                * self.field_pairing
            )
            if defect != sp.zeros(9, 24):
                raise AssertionError("curved companion derivative-adjoint defect")
        zeroth_defect = sp.simplify(
            self.ghost_pairing * self.gauge_companion.zeroth_coefficient
            - self.gauge_generator.zeroth_coefficient.T * self.field_pairing
        )
        if zeroth_defect != sp.zeros(9, 24):
            raise AssertionError("curved companion zeroth-order adjoint defect")

        # Removing the cylinder auxiliary background must recover every
        # coefficient of the previously certified flat K and C operators.
        flat_derivative = list(self.gauge_generator.derivative_coefficients)
        flat_derivative = [matrix.copy() for matrix in flat_derivative]
        for matrix in flat_derivative:
            matrix[10:20, :4] = sp.zeros(10, 4)
        zeta = _ordinary_system().covector
        flat_generator_symbol = sp.simplify(
            self.gauge_generator.zeroth_coefficient
            + sum(
                (zeta[axis] * flat_derivative[axis] for axis in range(4)),
                sp.zeros(24, 9),
            )
        )
        source = _ordinary_system()
        if flat_generator_symbol != source.gauge_map:
            raise AssertionError("exact curved K has the wrong flat limit")
        flat_companion_symbol = sp.simplify(
            source.gauge_fixing_pairing.inv()
            * flat_generator_symbol.subs({entry: -entry for entry in zeta}).T
            * source.field_fibre_pairing
        )
        if flat_companion_symbol != source.gauge_condition:
            raise AssertionError("adjoint-derived curved C has the wrong flat limit")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-curved-bv-conventions-v1",
            "background": self.background.certificate(),
            "component_order": {
                "fields": list(self.field_order),
                "ghosts": list(self.ghost_order),
                "four_row_BV": ["G[9]", "M[24]", "E[24]", "I[9]"],
            },
            "pairings": {
                "J_aux_shape": list(self.field_pairing.shape),
                "J_aux_rank": self.field_pairing.rank(),
                "Y_gh_shape": list(self.ghost_pairing.shape),
                "Y_gh_rank": self.ghost_pairing.rank(),
                "metric_signature": "(-,+,+,+)",
            },
            "formal_adjoint": {
                "support": "compact spacetime support",
                "nabla_sharp": "-nabla",
                "parallel_coefficients": True,
                "identity": "Y_gh C_cyl=K_cyl^sharp J_aux",
                "derivative_coefficient_defects": [0, 0, 0, 0],
                "zeroth_coefficient_defect": 0,
            },
            "gauge_generator": {
                "order": 1,
                "shape": [24, 9],
                "global_natural_operator": True,
                "includes_Lie_xi_phi_bar": True,
                "coefficient_sha256": self.gauge_generator.coefficient_sha256,
                "flat_limit_exact": True,
            },
            "gauge_companion": {
                "order": 1,
                "shape": [9, 24],
                "generated_from_same_K_J_Y": True,
                "global_natural_operator": True,
                "coefficient_sha256": self.gauge_companion.coefficient_sha256,
                "flat_limit_exact": True,
                "expanded_all_coefficients": True,
            },
        }
