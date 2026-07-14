"""Executable tangent of the curved completion-of-square transformation.

At the cylinder background the nonlinear field redefinition is

``phi_hat = phi - A_g^{-1} G^b(g,b)``.

This module evaluates ``S(h,v)=D[A_g^{-1}G^b]_(gbar,0)(h,v)`` in the exact
finite-jet algebra.  It is the shared local operator required by both the
curved Hessian congruence and the BV-canonical cotangent lift; keeping it
here prevents those workstreams from independently reconstructing signs and
curvature terms.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

import sympy as sp

from covariant_completion.auxiliary_witness import OrdinaryDerivativeWeylSystem
from covariant_completion.minimal_witness.cylinder_jets import (
    CylinderJetGeometry,
    Jet,
    _sum,
    _zero,
)
from covariant_completion.minimal_witness.linearized_bach import LinearizedBach


DIMENSION = 4
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


def _rank2_zero() -> list[list[Jet]]:
    return [[_zero() for _ in range(DIMENSION)] for _ in range(DIMENSION)]


def _exp_jet(linear: Jet, order: int) -> Jet:
    result = Jet.constant(1)
    power = Jet.constant(1)
    factorial = 1
    for degree in range(1, order + 1):
        power = power * linear
        factorial *= degree
        result += Fraction(1, factorial) * power
    return result


@dataclass(frozen=True)
class CurvedAuxiliaryTangentShift:
    """The finite-order local operator ``S:Dg+Db -> Dphi``."""

    geometry: CylinderJetGeometry
    linearized_geometry: LinearizedBach
    metric_principal_symbol: sp.Matrix
    vector_principal_symbol: sp.Matrix
    metric_flat_principal_defect: sp.Matrix
    vector_flat_principal_defect: sp.Matrix
    diffeomorphism_gauge_defect: sp.Matrix
    conformal_boost_gauge_defect: sp.Matrix
    weyl_gauge_defect: sp.Matrix

    @staticmethod
    def build(
        source_system: OrdinaryDerivativeWeylSystem | None = None,
    ) -> "CurvedAuxiliaryTangentShift":
        if source_system is None:
            source_system = OrdinaryDerivativeWeylSystem.build()
        linearized_geometry = LinearizedBach.build()
        provisional = CurvedAuxiliaryTangentShift(
            geometry=linearized_geometry.geometry,
            linearized_geometry=linearized_geometry,
            metric_principal_symbol=sp.zeros(10),
            vector_principal_symbol=sp.zeros(10, 4),
            metric_flat_principal_defect=sp.zeros(10),
            vector_flat_principal_defect=sp.zeros(10, 4),
            diffeomorphism_gauge_defect=sp.zeros(10, 4),
            conformal_boost_gauge_defect=sp.zeros(10, 4),
            weyl_gauge_defect=sp.zeros(10, 1),
        )
        metric_symbol, vector_symbol = provisional._compute_principal_symbol()
        equation = source_system.gauge_invariant_flat_hessian
        mass = equation[10:20, 10:20]
        expected_metric = -mass.inv() * equation[10:20, 0:10]
        expected_vector = -mass.inv() * equation[10:20, 20:24]
        substitution = {
            symbol: component
            for symbol, component in zip(
                sp.symbols("zeta_0:4", real=True),
                source_system.covector,
                strict=True,
            )
        }
        metric_defect = sp.simplify(
            metric_symbol.subs(substitution) - expected_metric
        )
        vector_defect = sp.simplify(
            vector_symbol.subs(substitution) - expected_vector
        )
        diffeomorphism, conformal_boost, weyl = provisional._compute_gauge_defects()
        result = CurvedAuxiliaryTangentShift(
            geometry=linearized_geometry.geometry,
            linearized_geometry=linearized_geometry,
            metric_principal_symbol=metric_symbol,
            vector_principal_symbol=vector_symbol,
            metric_flat_principal_defect=metric_defect,
            vector_flat_principal_defect=vector_defect,
            diffeomorphism_gauge_defect=diffeomorphism,
            conformal_boost_gauge_defect=conformal_boost,
            weyl_gauge_defect=weyl,
        )
        result.verify()
        return result

    def linearized_ricci(self, metric_variation) -> list[list[Jet]]:
        connection = self.linearized_geometry.connection_variation(
            metric_variation
        )
        derivative = self.linearized_geometry.covariant_derivative_connection_variation(
            connection
        )
        return [
            [
                _sum(
                    derivative[rho][rho][nu][sigma]
                    - derivative[nu][rho][rho][sigma]
                    for rho in range(DIMENSION)
                )
                for nu in range(DIMENSION)
            ]
            for sigma in range(DIMENSION)
        ]

    def apply(self, metric_variation, vector_variation) -> list[list[Jet]]:
        """Apply the exact tangent shift to arbitrary cylinder jets."""

        geometry = self.geometry
        ricci_one = self.linearized_ricci(metric_variation)
        raised_h_ricci = _sum(
            geometry.inverse_metric[a][left]
            * geometry.inverse_metric[b][right]
            * metric_variation[left][right]
            * geometry.ricci[a][b]
            for a in range(DIMENSION)
            for b in range(DIMENSION)
            for left in range(DIMENSION)
            for right in range(DIMENSION)
        )
        scalar_one = -raised_h_ricci + _sum(
            geometry.inverse_metric[a][b] * ricci_one[a][b]
            for a in range(DIMENSION)
            for b in range(DIMENSION)
        )
        derivative_v = geometry.covariant_derivative_covector(vector_variation)
        divergence_v = geometry.divergence_covector(vector_variation)
        dg = [
            [
                ricci_one[a][b]
                + Fraction(1, 2)
                * (derivative_v[a][b] + derivative_v[b][a])
                - 3 * metric_variation[a][b]
                - Fraction(1, 2) * geometry.metric[a][b] * scalar_one
                - geometry.metric[a][b] * divergence_v
                for b in range(DIMENSION)
            ]
            for a in range(DIMENSION)
        ]

        # Gbar is the cylinder Einstein tensor and tr(Gbar)=-6.  Differentiate
        # A_g^{-1}(G)=-2G+(2/3)g tr_g(G), including both metric variations in
        # the trace.  Omitting these terms is the common flat-covariantization
        # error this interface is designed to prevent.
        g_bar = [
            [
                geometry.ricci[a][b] - 3 * geometry.metric[a][b]
                for b in range(DIMENSION)
            ]
            for a in range(DIMENSION)
        ]
        raised_h_gbar = _sum(
            geometry.inverse_metric[a][left]
            * geometry.inverse_metric[b][right]
            * metric_variation[left][right]
            * g_bar[a][b]
            for a in range(DIMENSION)
            for b in range(DIMENSION)
            for left in range(DIMENSION)
            for right in range(DIMENSION)
        )
        trace_dg = _sum(
            geometry.inverse_metric[a][b] * dg[a][b]
            for a in range(DIMENSION)
            for b in range(DIMENSION)
        )
        trace_variation = -raised_h_gbar + trace_dg
        return [
            [
                -2 * dg[a][b]
                - 4 * metric_variation[a][b]
                + Fraction(2, 3)
                * geometry.metric[a][b]
                * trace_variation
                for b in range(DIMENSION)
            ]
            for a in range(DIMENSION)
        ]

    @staticmethod
    def _coordinates(tensor) -> sp.Matrix:
        return sp.Matrix(
            [tensor[a][b].value for a, b in SYMMETRIC_COORDINATES]
        )

    def _compute_principal_symbol(self) -> tuple[sp.Matrix, sp.Matrix]:

        zeta = sp.symbols("zeta_0:4", real=True)
        linear = _sum(
            Jet.monomial(tuple(1 if axis == mu else 0 for axis in range(4)))
            * zeta[mu]
            for mu in range(4)
        )
        metric_symbol = sp.zeros(10, 10)
        for column, (left, right) in enumerate(SYMMETRIC_COORDINATES):
            h = _rank2_zero()
            scalar = _exp_jet(linear, 2)
            h[left][right] = scalar
            h[right][left] = scalar
            value = self._coordinates(
                self.apply(h, self.geometry.zero_covector())
            )
            metric_symbol[:, column] = value
        # SymPy has no stable homogeneous_component method across supported
        # versions, so extract by a common scaling variable.
        scale = sp.symbols("tangent_symbol_scale")
        scaled = {zeta[mu]: scale * zeta[mu] for mu in range(4)}
        metric_symbol = metric_symbol.applyfunc(
            lambda entry: sp.expand(entry.subs(scaled)).coeff(scale, 2)
        )

        vector_symbol = sp.zeros(10, 4)
        for column in range(4):
            vector = self.geometry.zero_covector()
            vector[column] = _exp_jet(linear, 1)
            value = self._coordinates(self.apply(_rank2_zero(), vector))
            vector_symbol[:, column] = value
        vector_symbol = vector_symbol.applyfunc(
            lambda entry: sp.expand(entry.subs(scaled)).coeff(scale, 1)
        )
        return metric_symbol, vector_symbol

    def principal_symbol(self) -> tuple[sp.Matrix, sp.Matrix]:
        """Return the cached order-two ``h`` and order-one ``v`` symbols."""

        return self.metric_principal_symbol, self.vector_principal_symbol

    def _compute_gauge_defects(self) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
        """Evaluate ``delta phi-S(delta g,delta b)`` on generic gauge jets."""

        geometry = self.geometry
        zeta = sp.symbols("gauge_zeta_0:4", real=True)
        linear = _sum(
            Jet.monomial(tuple(1 if axis == mu else 0 for axis in range(4)))
            * zeta[mu]
            for mu in range(4)
        )
        diffeomorphism_scalar = _exp_jet(linear, 3)
        boost_scalar = _exp_jet(linear, 1)
        weyl_scalar = _exp_jet(linear, 2)
        zero_tensor = _rank2_zero()

        phi_bar = [
            [
                -2 * geometry.ricci[a][b] + 2 * geometry.metric[a][b]
                for b in range(DIMENSION)
            ]
            for a in range(DIMENSION)
        ]

        diffeomorphism = sp.zeros(10, 4)
        for column in range(DIMENSION):
            xi = geometry.zero_covector()
            xi[column] = diffeomorphism_scalar
            derivative = geometry.covariant_derivative_covector(xi)
            h = [
                [derivative[a][b] + derivative[b][a] for b in range(4)]
                for a in range(4)
            ]
            lie_phi = [
                [
                    _sum(
                        phi_bar[c][b]
                        * geometry.inverse_metric[c][d]
                        * derivative[a][d]
                        + phi_bar[a][c]
                        * geometry.inverse_metric[c][d]
                        * derivative[b][d]
                        for c in range(4)
                        for d in range(4)
                    )
                    for b in range(4)
                ]
                for a in range(4)
            ]
            shifted = self.apply(h, geometry.zero_covector())
            diffeomorphism[:, column] = self._coordinates(
                [
                    [lie_phi[a][b] - shifted[a][b] for b in range(4)]
                    for a in range(4)
                ]
            )

        conformal_boost = sp.zeros(10, 4)
        for column in range(DIMENSION):
            kappa = geometry.zero_covector()
            kappa[column] = boost_scalar
            derivative = geometry.covariant_derivative_covector(kappa)
            delta_phi = [
                [derivative[a][b] + derivative[b][a] for b in range(4)]
                for a in range(4)
            ]
            shifted = self.apply(zero_tensor, [-entry for entry in kappa])
            conformal_boost[:, column] = self._coordinates(
                [
                    [delta_phi[a][b] - shifted[a][b] for b in range(4)]
                    for a in range(4)
                ]
            )

        h_sigma = [
            [geometry.metric[a][b] * weyl_scalar for b in range(4)]
            for a in range(4)
        ]
        d_sigma = [weyl_scalar.derivative(a) for a in range(4)]
        weyl = -self._coordinates(self.apply(h_sigma, d_sigma))
        return (
            diffeomorphism.applyfunc(sp.expand),
            conformal_boost.applyfunc(sp.expand),
            weyl.applyfunc(sp.expand),
        )

    def verify(self) -> None:
        zero = _rank2_zero()
        if self._coordinates(self.apply(zero, self.geometry.zero_covector())) != sp.zeros(10, 1):
            raise AssertionError("the tangent shift is not linear")

        # Independent flat-principal regression against the action Hessian's
        # exact equation-of-motion shift.
        metric_symbol, vector_symbol = self.principal_symbol()
        if self.metric_flat_principal_defect != sp.zeros(10):
            raise AssertionError("the curved tangent shift has the wrong metric principal symbol")
        if self.vector_flat_principal_defect != sp.zeros(10, 4):
            raise AssertionError("the curved tangent shift has the wrong vector principal symbol")
        if self.diffeomorphism_gauge_defect != sp.zeros(10, 4):
            raise AssertionError("the shifted auxiliary tensor is not diffeomorphism invariant")
        if self.conformal_boost_gauge_defect != sp.zeros(10, 4):
            raise AssertionError("the shifted auxiliary tensor is not boost invariant")
        if self.weyl_gauge_defect != sp.zeros(10, 1):
            raise AssertionError("the shifted auxiliary tensor is not Weyl invariant")

    def certificate(self) -> dict[str, object]:
        self.verify()
        metric_symbol, vector_symbol = self.principal_symbol()
        return {
            "schema": "pure-weyl-curved-auxiliary-tangent-shift-v1",
            "operator": "S(h,v)=D[A_g^{-1}G^b]_(gbar,0)(h,v)",
            "executable_interface": (
                "CurvedAuxiliaryTangentShift.apply(metric_variation, vector_variation)"
            ),
            "input_orders": {"h": 2, "v": 1},
            "output": "symmetric covariant tensor",
            "includes": [
                "linearized Ricci curvature terms",
                "linearized scalar curvature terms",
                "variation of A_g^{-1} at nonzero cylinder Gbar",
                "symmetrized covariant derivative and divergence of v",
            ],
            "flat_principal_regression": {
                "metric_symbol_matches_exact_EOM_shift": True,
                "vector_symbol_matches_exact_EOM_shift": True,
                "metric_shape": list(metric_symbol.shape),
                "vector_shape": list(vector_symbol.shape),
            },
            "curved_gauge_regression": {
                "diffeomorphism_defect": "zero",
                "conformal_boost_defect": "zero",
                "Weyl_defect": "zero",
                "method": (
                    "generic exponential jets through operator order at one "
                    "cylinder point, including connection/curvature terms"
                ),
            },
            "finite_order_local": True,
        }
