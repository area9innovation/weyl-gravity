"""Promoted Cotton-constraint repair of the Weyl--Cotton evolution.

An independent row audit of the 26-state adjusted system finds

``R_x = U_x-2a`` and ``R_y = U_y-2c``,

where ``U_x,U_y`` are the exact vector Bach rows and

``a=div A+(1/2)curl y``, ``c=div C-(1/2)curl x``.

This module promotes ``a,c`` to independent vector variables.  The exact
vector Bach rows are retained as ``R_x+2a=0`` and ``R_y+2c=0``.  Formal
integrability gives

``a_t=q+(1/3)grad s-curl c`` and
``c_t=r+(1/3)grad t+curl a``.

Those literal rows are second order after substituting
``s=div x,t=div y``.  The square first-order system therefore subtracts the
retained differential constraints ``q+(1/3)grad s`` and
``r+(1/3)grad t`` and uses ``a_t+curl c=0``, ``c_t-curl a=0``.  The
certificate records this constraint subtraction explicitly.  Equivalence
to the complete covariant differential ideal is a separate row audit.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from .weyl_cotton_hyperbolic import (
    ConstraintAdjustedWeylCottonEvolution,
    STATE_SLICES,
    _block_slices,
    _put,
)


PROMOTED_STATE_DIMENSION = 32
PROMOTED_STATE_SLICES = _block_slices((5, 5, 5, 5, 3, 3, 3, 3))
PROMOTED_CONSTRAINT_DIMENSION = 14
PROMOTED_CONSTRAINT_SLICES = _block_slices((3, 3, 1, 1, 3, 3))


@dataclass(frozen=True)
class PromotedCottonConstraintEvolution:
    """First-order 32-state candidate with independent ``a,c`` variables."""

    base: ConstraintAdjustedWeylCottonEvolution
    spatial_coefficients: tuple[sp.Matrix, sp.Matrix, sp.Matrix]
    zeroth_coefficient: sp.Matrix
    symmetrizer: sp.Matrix
    constraint_spatial_coefficients: tuple[sp.Matrix, sp.Matrix, sp.Matrix]
    constraint_zeroth_coefficient: sp.Matrix
    representative_characteristic: sp.Expr
    literal_second_order_symbols: tuple[sp.Matrix, sp.Matrix]

    @staticmethod
    def build() -> "PromotedCottonConstraintEvolution":
        base = ConstraintAdjustedWeylCottonEvolution.build()

        spatial: list[sp.Matrix] = []
        for axis in range(3):
            coefficient = sp.zeros(PROMOTED_STATE_DIMENSION)
            coefficient[:26, :26] = base.evolution_spatial_coefficients[axis]
            vector_curl = base.vector_curl_coefficients[axis]
            _put(
                coefficient,
                PROMOTED_STATE_SLICES[6],
                PROMOTED_STATE_SLICES[7],
                vector_curl,
            )
            _put(
                coefficient,
                PROMOTED_STATE_SLICES[7],
                PROMOTED_STATE_SLICES[6],
                -vector_curl,
            )
            spatial.append(coefficient)

        zeroth = sp.zeros(PROMOTED_STATE_DIMENSION)
        zeroth[:26, :26] = base.evolution_zeroth_coefficient
        # Replace the noncovariant adjusted vector rows by the exact vector
        # Bach rows U_x=R_x+2a and U_y=R_y+2c.
        _put(
            zeroth,
            PROMOTED_STATE_SLICES[4],
            PROMOTED_STATE_SLICES[6],
            2 * sp.eye(3),
        )
        _put(
            zeroth,
            PROMOTED_STATE_SLICES[5],
            PROMOTED_STATE_SLICES[7],
            2 * sp.eye(3),
        )

        symmetrizer = sp.diag(
            base.evolution_symmetrizer,
            sp.eye(3),
            sp.eye(3),
        )

        # Retained constraints: q,r,s,t and the local definitions d_a,d_c.
        # q=x-div E, r=y-div B, s=div x, t=div y,
        # d_a=a-div A-(1/2)curl y,
        # d_c=c-div C+(1/2)curl x.
        constraints: list[sp.Matrix] = []
        for axis in range(3):
            coefficient = sp.zeros(
                PROMOTED_CONSTRAINT_DIMENSION, PROMOTED_STATE_DIMENSION
            )
            divergence = base.divergence_coefficients[axis]
            vector_curl = base.vector_curl_coefficients[axis]
            _put(
                coefficient,
                PROMOTED_CONSTRAINT_SLICES[0],
                PROMOTED_STATE_SLICES[0],
                -divergence,
            )
            _put(
                coefficient,
                PROMOTED_CONSTRAINT_SLICES[1],
                PROMOTED_STATE_SLICES[1],
                -divergence,
            )
            _put(
                coefficient,
                PROMOTED_CONSTRAINT_SLICES[2],
                PROMOTED_STATE_SLICES[4],
                sp.eye(3)[axis, :],
            )
            _put(
                coefficient,
                PROMOTED_CONSTRAINT_SLICES[3],
                PROMOTED_STATE_SLICES[5],
                sp.eye(3)[axis, :],
            )
            _put(
                coefficient,
                PROMOTED_CONSTRAINT_SLICES[4],
                PROMOTED_STATE_SLICES[2],
                -divergence,
            )
            _put(
                coefficient,
                PROMOTED_CONSTRAINT_SLICES[4],
                PROMOTED_STATE_SLICES[5],
                -sp.Rational(1, 2) * vector_curl,
            )
            _put(
                coefficient,
                PROMOTED_CONSTRAINT_SLICES[5],
                PROMOTED_STATE_SLICES[3],
                -divergence,
            )
            _put(
                coefficient,
                PROMOTED_CONSTRAINT_SLICES[5],
                PROMOTED_STATE_SLICES[4],
                sp.Rational(1, 2) * vector_curl,
            )
            constraints.append(coefficient)
        constraint_zeroth = sp.zeros(
            PROMOTED_CONSTRAINT_DIMENSION, PROMOTED_STATE_DIMENSION
        )
        _put(
            constraint_zeroth,
            PROMOTED_CONSTRAINT_SLICES[0],
            PROMOTED_STATE_SLICES[4],
            sp.eye(3),
        )
        _put(
            constraint_zeroth,
            PROMOTED_CONSTRAINT_SLICES[1],
            PROMOTED_STATE_SLICES[5],
            sp.eye(3),
        )
        _put(
            constraint_zeroth,
            PROMOTED_CONSTRAINT_SLICES[4],
            PROMOTED_STATE_SLICES[6],
            sp.eye(3),
        )
        _put(
            constraint_zeroth,
            PROMOTED_CONSTRAINT_SLICES[5],
            PROMOTED_STATE_SLICES[7],
            sp.eye(3),
        )

        lam = sp.Symbol("lambda")
        characteristic = sp.factor(spatial[0].charpoly(lam).as_expr())
        xi = sp.Matrix(sp.symbols("xi0:3"))
        second_order = sp.Rational(1, 3) * xi * xi.T

        result = PromotedCottonConstraintEvolution(
            base=base,
            spatial_coefficients=tuple(spatial),
            zeroth_coefficient=zeroth,
            symmetrizer=symmetrizer,
            constraint_spatial_coefficients=tuple(constraints),
            constraint_zeroth_coefficient=constraint_zeroth,
            representative_characteristic=characteristic,
            literal_second_order_symbols=(second_order, second_order.copy()),
        )
        result.verify()
        return result

    def verify(self) -> None:
        self.base.verify()
        if self.symmetrizer.shape != (32, 32):
            raise AssertionError("wrong promoted symmetrizer shape")
        if any(value <= 0 for value in self.symmetrizer.diagonal()):
            raise AssertionError("promoted symmetrizer is not positive")
        for coefficient in self.spatial_coefficients:
            weighted = self.symmetrizer * coefficient
            if weighted != weighted.T:
                raise AssertionError("promoted spatial symbol is not symmetrized")
        if self.constraint_zeroth_coefficient.shape != (14, 32):
            raise AssertionError("wrong promoted constraint table shape")
        if any(matrix.shape != (14, 32) for matrix in self.constraint_spatial_coefficients):
            raise AssertionError("wrong promoted constraint spatial shape")
        xi = sp.Matrix(sp.symbols("xi0:3"))
        expected_second_order = sp.Rational(1, 3) * xi * xi.T
        for symbol in self.literal_second_order_symbols:
            if symbol != expected_second_order or symbol.rank() != 1:
                raise AssertionError("literal promoted evolution second-order defect drifted")

        lam = sp.Symbol("lambda")
        expected = sp.factor(
            lam**8
            * (lam**2 - 1) ** 8
            * (4 * lam**2 - 1) ** 2
            * (3 * lam**2 - 1) ** 2
            / 144
        )
        if self.representative_characteristic != expected:
            raise AssertionError("promoted characteristic polynomial drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-cotton-promoted-constraint-candidate-v1",
            "state_order": [
                "E_STF[5]",
                "B_STF[5]",
                "A_STF[5]",
                "C_STF[5]",
                "x[3]",
                "y[3]",
                "a[3]",
                "c[3]",
            ],
            "state_rank": PROMOTED_STATE_DIMENSION,
            "exact_vector_Bach_rows": [
                "U_x=R_x+2a=x_t-div A+(1/2)curl y+2a",
                "U_y=R_y+2c=y_t-div C-(1/2)curl x+2c",
            ],
            "retained_constraints": [
                "q=x-div E",
                "r=y-div B",
                "s=div x",
                "t=div y",
                "d_a=a-div A-(1/2)curl y",
                "d_c=c-div C+(1/2)curl x",
            ],
            "constraint_rank": PROMOTED_CONSTRAINT_DIMENSION,
            "formal_integrability_rows": [
                "a_t=q+(1/3)grad s-curl c",
                "c_t=r+(1/3)grad t+curl a",
            ],
            "literal_formal_integrability_is_first_order": False,
            "literal_second_order_symbol": "(1/3) xi tensor xi in each sector",
            "literal_second_order_rank_at_nonzero_xi": 1,
            "first_order_constraint_subtraction": [
                "subtract q+(1/3)grad s and use a_t+curl c=0",
                "subtract r+(1/3)grad t and use c_t-curl a=0",
            ],
            "constraint_subtraction_is_support_local": True,
            "symmetrizer_positive": True,
            "spatial_symbols_self_adjoint": True,
            "representative_characteristic": str(
                self.representative_characteristic
            ),
            "characteristic_speeds": {
                "-1": 8,
                "-1/sqrt(3)": 2,
                "-1/2": 2,
                "0": 8,
                "+1/2": 2,
                "+1/sqrt(3)": 2,
                "+1": 8,
            },
            "all_characteristics_causal": True,
            "covariant_differential_ideal_equivalence_audited": False,
            "warranted_atomic_flags": [],
            "flags_promoted_here": [],
            "proof_boundary": (
                "the first-order rank-32 candidate is internally symmetric "
                "hyperbolic; equivalence of the constraint-subtracted a/c rows "
                "to the complete covariant differential ideal remains an "
                "independent exact row audit"
            ),
            "fail_closed": True,
        }
