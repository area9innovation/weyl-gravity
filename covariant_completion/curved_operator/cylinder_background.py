"""Exact algebraic curvature data for the unit Lorentzian cylinder.

All arrays are components in a normal orthonormal frame with index ``0`` in
the time direction.  The Riemann convention is

``R^a{}_{bcd} = d_c Gamma^a_{bd} - d_d Gamma^a_{bc} + ...``.

Only the spatial three-plane is curved.  This file is intentionally small:
it is the convention anchor used by the derivative normal-form engine and
the curved auxiliary-action certificate.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp


DIMENSION = 4


@dataclass(frozen=True)
class CylinderBackground:
    metric: sp.Matrix
    inverse_metric: sp.Matrix
    spatial: sp.Matrix
    riemann_covariant: sp.MutableDenseNDimArray
    ricci: sp.Matrix
    scalar_curvature: sp.Expr
    weyl_covariant: sp.MutableDenseNDimArray
    auxiliary_background: sp.Matrix

    @staticmethod
    def build() -> "CylinderBackground":
        metric = sp.diag(-1, 1, 1, 1)
        inverse_metric = metric.inv()
        spatial = sp.diag(0, 1, 1, 1)

        # R_abcd = s_ac s_bd-s_ad s_bc.
        riemann = sp.MutableDenseNDimArray.zeros(4, 4, 4, 4)
        for a in range(4):
            for b in range(4):
                for c in range(4):
                    for d in range(4):
                        riemann[a, b, c, d] = (
                            spatial[a, c] * spatial[b, d]
                            - spatial[a, d] * spatial[b, c]
                        )

        ricci = sp.zeros(4)
        for b in range(4):
            for d in range(4):
                ricci[b, d] = sp.simplify(
                    sum(
                        inverse_metric[a, c] * riemann[a, b, c, d]
                        for a in range(4)
                        for c in range(4)
                    )
                )
        scalar = sp.simplify(
            sum(inverse_metric[a, b] * ricci[a, b] for a in range(4) for b in range(4))
        )

        # Four-dimensional Weyl decomposition.
        weyl = sp.MutableDenseNDimArray.zeros(4, 4, 4, 4)
        for a in range(4):
            for b in range(4):
                for c in range(4):
                    for d in range(4):
                        ricci_part = sp.Rational(1, 2) * (
                            metric[a, c] * ricci[d, b]
                            - metric[a, d] * ricci[c, b]
                            - metric[b, c] * ricci[d, a]
                            + metric[b, d] * ricci[c, a]
                        )
                        scalar_part = sp.Rational(1, 6) * scalar * (
                            metric[a, c] * metric[d, b]
                            - metric[a, d] * metric[c, b]
                        )
                        weyl[a, b, c, d] = sp.simplify(
                            riemann[a, b, c, d] - ricci_part + scalar_part
                        )

        auxiliary = sp.simplify(-2 * ricci + sp.Rational(1, 3) * scalar * metric)
        result = CylinderBackground(
            metric=metric,
            inverse_metric=inverse_metric,
            spatial=spatial,
            riemann_covariant=riemann,
            ricci=ricci,
            scalar_curvature=scalar,
            weyl_covariant=weyl,
            auxiliary_background=auxiliary,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.ricci != sp.diag(0, 2, 2, 2):
            raise AssertionError("cylinder Ricci convention drifted")
        if self.scalar_curvature != 6:
            raise AssertionError("cylinder scalar curvature drifted")
        if self.auxiliary_background != sp.diag(-2, -2, -2, -2):
            raise AssertionError("wrong auxiliary background")

        for a in range(4):
            for b in range(4):
                for c in range(4):
                    for d in range(4):
                        r = self.riemann_covariant
                        if sp.simplify(r[a, b, c, d] + r[b, a, c, d]) != 0:
                            raise AssertionError("Riemann first-pair antisymmetry failed")
                        if sp.simplify(r[a, b, c, d] + r[a, b, d, c]) != 0:
                            raise AssertionError("Riemann second-pair antisymmetry failed")
                        if sp.simplify(r[a, b, c, d] - r[c, d, a, b]) != 0:
                            raise AssertionError("Riemann pair symmetry failed")
                        if sp.simplify(
                            r[a, b, c, d] + r[a, c, d, b] + r[a, d, b, c]
                        ) != 0:
                            raise AssertionError("algebraic Bianchi identity failed")
                        if self.weyl_covariant[a, b, c, d] != 0:
                            raise AssertionError("the conformal cylinder is not Weyl flat")

    def covector_commutator(self, a: int, b: int) -> sp.Matrix:
        """Matrix for ``[nabla_a,nabla_b]`` on covectors.

        With the convention above,

        ``[nabla_a,nabla_b] v_c = s_ca v_b-s_cb v_a``.
        """

        matrix = sp.zeros(4)
        for c in range(4):
            for d in range(4):
                matrix[c, d] = (
                    self.spatial[c, a] * int(d == b)
                    - self.spatial[c, b] * int(d == a)
                )
        return matrix

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-cylinder-curvature-normal-frame-v1",
            "dimension": 4,
            "signature": "(-,+,+,+)",
            "Ricci_covariant": [0, 2, 2, 2],
            "scalar_curvature": 6,
            "parallel_curvature": True,
            "Weyl_tensor": "zero",
            "auxiliary_background": [-2, -2, -2, -2],
            "auxiliary_formula": "phi_bar=-2 Ric+(R/3)g",
            "riemann_symmetries_verified": True,
            "algebraic_Bianchi_verified": True,
        }
