"""Exact dual-endpoint cokernel for the pure-Weyl zero-mode block.

The tangent detour chain has endpoint arrow ``K^sharp:E -> I`` and gauge
arrow ``K:G -> M``.  With nondegenerate cyclic coordinate pairings,

    K^sharp = J_GI^{-1} K^T J_ME.

The fifteen-dimensional gauge kernel ``Z=ker K`` therefore pairs
canonically with ``coker K^sharp``.  This module instantiates that elementary
adjoint-linear-algebra theorem in the exact 65-by-50 polynomial chart that
already certifies all conformal-Killing reducibilities.

The quotient is the obstruction/constraint codomain.  It is deliberately
not called the BFV ghost-momentum space; those momenta are newly adjoined
cotangent variables in :mod:`residual_roles`.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import factorial

import sympy as sp

from bridge.bv_complex.conformal_polynomials import SYMMETRIC_PAIRS
from bridge.zero_modes import conformal_killing_projector
from field_bv_identification.gauge_fixed_equivalence.contraction import (
    ZeroModePreservation,
)


def _metric_fischer_gram() -> sp.Matrix:
    """Compact ``SO(4)`` Fischer form on the 50 low metric coefficients."""

    exponents = tuple(
        exponent
        for degree in range(2)
        for exponent in product(range(degree + 1), repeat=4)
        if sum(exponent) == degree
    )
    weights: list[sp.Expr] = []
    for first, second in SYMMETRIC_PAIRS:
        tensor_weight = 1 if first == second else 2
        for exponent in exponents:
            monomial_weight = sp.prod(factorial(power) for power in exponent)
            weights.append(sp.Integer(tensor_weight) * monomial_weight)
    if len(weights) != 50:
        raise AssertionError("unexpected low metric coefficient count")
    return sp.diag(*weights)


@dataclass(frozen=True)
class DualEndpointCokernel:
    """Exact realization of ``coker K^sharp ~= (ker K)^*``."""

    gauge_map: sp.Matrix
    adjoint_map: sp.Matrix
    gauge_endpoint_pairing: sp.Matrix
    metric_equation_pairing: sp.Matrix
    zero_basis: sp.Matrix
    quotient_map: sp.Matrix
    quotient_section: sp.Matrix
    obstruction_projector: sp.Matrix
    exact_endpoint_projector: sp.Matrix
    labels: tuple[str, ...]
    generator_compact_degrees: tuple[int, ...]
    dual_compact_degrees: tuple[int, ...]

    @classmethod
    def build(cls) -> "DualEndpointCokernel":
        ckv = conformal_killing_projector()
        compact = ZeroModePreservation.build()
        gauge_map = sp.Matrix(ckv.gauge_map)
        gauge_endpoint_pairing = sp.Matrix(compact.compact_gram)
        metric_equation_pairing = _metric_fischer_gram()

        # This is the exact coordinate form of cyclic adjointness:
        # J_GI K^sharp = K^T J_ME.
        adjoint_map = sp.simplify(
            gauge_endpoint_pairing.inv()
            * gauge_map.T
            * metric_equation_pairing
        )
        zero_basis = sp.Matrix(ckv.basis)

        # Phi([u])(z_a)=<z_a,u>.  Its rows are the fifteen dual coordinates.
        quotient_map = sp.simplify(zero_basis.T * gauge_endpoint_pairing)
        zero_gram = sp.simplify(
            zero_basis.T * gauge_endpoint_pairing * zero_basis
        )
        quotient_section = sp.simplify(zero_basis * zero_gram.inv())
        obstruction_projector = sp.simplify(quotient_section * quotient_map)
        exact_endpoint_projector = sp.eye(65) - obstruction_projector

        result = cls(
            gauge_map=gauge_map,
            adjoint_map=sp.Matrix(adjoint_map),
            gauge_endpoint_pairing=gauge_endpoint_pairing,
            metric_equation_pairing=metric_equation_pairing,
            zero_basis=zero_basis,
            quotient_map=sp.Matrix(quotient_map),
            quotient_section=sp.Matrix(quotient_section),
            obstruction_projector=sp.Matrix(obstruction_projector),
            exact_endpoint_projector=sp.Matrix(exact_endpoint_projector),
            labels=ckv.labels,
            generator_compact_degrees=ckv.compact_degrees,
            dual_compact_degrees=tuple(-degree for degree in ckv.compact_degrees),
        )
        result.verify()
        return result

    @property
    def zero_dimension(self) -> int:
        return self.zero_basis.cols

    @property
    def endpoint_dimension(self) -> int:
        return self.adjoint_map.rows

    @property
    def obstruction_dimension(self) -> int:
        return self.quotient_map.rank()

    @property
    def exact_endpoint_dimension(self) -> int:
        return self.adjoint_map.rank()

    def verify(self) -> None:
        if self.gauge_map.shape != (50, 65):
            raise AssertionError("unexpected zero-mode gauge-map shape")
        if self.adjoint_map.shape != (65, 50):
            raise AssertionError("unexpected endpoint adjoint-map shape")
        if self.gauge_endpoint_pairing.det() == 0:
            raise AssertionError("G-I pairing is degenerate")
        if self.metric_equation_pairing.det() == 0:
            raise AssertionError("M-E pairing is degenerate")
        if (
            self.gauge_endpoint_pairing * self.adjoint_map
            != self.gauge_map.T * self.metric_equation_pairing
        ):
            raise AssertionError("K^sharp is not the cyclic adjoint of K")
        if self.gauge_map * self.zero_basis != sp.zeros(50, 15):
            raise AssertionError("displayed Z is not ker K")
        if self.gauge_map.rank() != 50 or self.zero_basis.rank() != 15:
            raise AssertionError("the 50+15 gauge decomposition failed")

        # Well-definedness on the cokernel and an explicit inverse on the
        # chosen quotient representatives.
        if self.quotient_map * self.adjoint_map != sp.zeros(15, 50):
            raise AssertionError("Phi does not annihilate im K^sharp")
        if self.quotient_map * self.quotient_section != sp.eye(15):
            raise AssertionError("Phi has no exact quotient section")
        if self.quotient_map.rank() != 15:
            raise AssertionError("Phi is not onto Z^*")
        if self.adjoint_map.rank() != 50:
            raise AssertionError("coker K^sharp is not fifteen dimensional")

        if (
            self.obstruction_projector * self.obstruction_projector
            != self.obstruction_projector
        ):
            raise AssertionError("obstruction representative map is not a projector")
        if self.obstruction_projector * self.adjoint_map != sp.zeros(65, 50):
            raise AssertionError("obstruction representatives overlap im K^sharp")
        if self.exact_endpoint_projector.rank() != 50:
            raise AssertionError("exact endpoint projector has the wrong rank")
        if self.quotient_map * self.exact_endpoint_projector != sp.zeros(15, 65):
            raise AssertionError("exact endpoint coordinates survive in the quotient")
        if sp.Matrix.hstack(self.adjoint_map, self.quotient_section).rank() != 65:
            raise AssertionError("I != im K^sharp direct-sum Z_ob")

        if self.generator_compact_degrees != (-1,) * 4 + (0,) * 7 + (1,) * 4:
            raise AssertionError("Z lost its 4+7+4 compact grading")
        if self.dual_compact_degrees != (1,) * 4 + (0,) * 7 + (-1,) * 4:
            raise AssertionError("Z^* has the wrong dual compact grading")
