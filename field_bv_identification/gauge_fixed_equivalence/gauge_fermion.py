"""A stationary, rotation-invariant Landau gauge fermion on the cylinder.

In trace-split variables the chosen fermion is

    Psi = integral sqrt(|gbar|) [bar_c_perp^mu nabla^nu h0_(mu nu)
                                + bar_omega tau].

It is local, has ghost number -1, is a weight-four scalar density, and
contains no multiplier-square term.  The latter is deliberate: a conformal
Landau gauge leaves every multiplier in an explicit nonminimal doublet
instead of eliminating it as a generalized auxiliary field.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from bridge.bv_complex.polynomial_bv import (
    PolynomialBVBlock,
    conformal_killing_matrix,
    tracefree_identity_matrix,
)
from field_bv_identification.gauge_fixed_equivalence.nonminimal_sector import (
    NonminimalBlock,
)


@dataclass(frozen=True)
class CylinderGaugeFermion:
    energy: int
    metric_to_vector_antighost_antifield: sp.SparseMatrix
    vector_antighost_to_equation: sp.SparseMatrix
    metric_trace_to_scalar_antighost_antifield: sp.SparseMatrix
    scalar_antighost_to_equation_trace: sp.SparseMatrix

    @classmethod
    def at_energy(cls, energy: int) -> "CylinderGaugeFermion":
        raw = PolynomialBVBlock.at_energy(energy)
        nonminimal = NonminimalBlock.at_energy(energy)
        metric = raw.slice("metric")
        equation = raw.slice("equation")
        scalar_metric = nonminimal.field("scalar_antighost_antifield").dimension
        scalar_equation = nonminimal.field("scalar_antighost").dimension
        metric_tf = metric.dimension - scalar_metric
        equation_tf = equation.dimension - scalar_equation

        # chi(h_0)=nabla^nu h^0_(mu nu).  In the polynomial realization this
        # is exactly the equation-side Noether map shifted by four units of
        # primary conformal weight.
        chi_vector = tracefree_identity_matrix(energy + 4)

        # Varying integral bar_c.div(h_0) with respect to a trace-free h_0
        # gives -K_0(bar_c)/2 in the K_0=2 symgrad-trace convention.
        vector_antighost = nonminimal.field("vector_antighost").dimension
        if vector_antighost:
            chi_vector_euler = -conformal_killing_matrix(energy - 4) / 2
        else:
            chi_vector_euler = sp.SparseMatrix(equation_tf, 0, {})

        result = cls(
            energy,
            sp.SparseMatrix(chi_vector),
            sp.SparseMatrix(chi_vector_euler),
            sp.SparseMatrix.eye(scalar_metric),
            sp.SparseMatrix.eye(scalar_equation),
        )
        result.verify(raw, nonminimal)
        return result

    def verify(self, raw: PolynomialBVBlock, nonminimal: NonminimalBlock) -> None:
        metric = raw.slice("metric")
        equation = raw.slice("equation")
        scalar_metric = nonminimal.field("scalar_antighost_antifield").dimension
        scalar_equation = nonminimal.field("scalar_antighost").dimension
        metric_tf = metric.dimension - scalar_metric
        equation_tf = equation.dimension - scalar_equation
        expected = (
            (
                self.metric_to_vector_antighost_antifield.shape,
                (
                    nonminimal.field("vector_antighost_antifield").dimension,
                    metric_tf,
                ),
            ),
            (
                self.vector_antighost_to_equation.shape,
                (equation_tf, nonminimal.field("vector_antighost").dimension),
            ),
            (
                self.metric_trace_to_scalar_antighost_antifield.shape,
                (scalar_metric, scalar_metric),
            ),
            (
                self.scalar_antighost_to_equation_trace.shape,
                (scalar_equation, scalar_equation),
            ),
        )
        if any(actual != wanted for actual, wanted in expected):
            raise AssertionError(f"gauge-fermion Hessian shape mismatch: {expected}")

    def summary(self) -> dict[str, object]:
        return {
            "formula": (
                "Psi=integral sqrt(|gbar|) [bar_c_perp^mu nabla^nu "
                "h0_(mu nu)+bar_omega tau]"
            ),
            "ghost_number": -1,
            "density_weight": 4,
            "compact_symmetry": "D x SO(4)",
            "multiplier_square": False,
            "metric_euler_derivative": "delta_Psi/delta_h0=-K0(bar_c)/2",
            "antighost_euler_derivative": "delta_Psi/delta_bar_c=div(h0)",
            "trace_euler_derivatives": (
                "delta_Psi/delta_tau=bar_omega; "
                "delta_Psi/delta_bar_omega=tau"
            ),
        }

