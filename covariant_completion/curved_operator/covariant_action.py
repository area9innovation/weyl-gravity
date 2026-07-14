"""Exact covariant source data for the ordinary-derivative realization.

The action and gauge transformations are the nonlinear formulas of
Metsaev's ordinary-derivative four-dimensional Weyl gravity.  The purpose of
this module is narrower than a computer-algebra Hessian: it fixes the global
operator being differentiated and constructs its *exact linearized gauge
map* on the cylinder, including the background-auxiliary Lie derivative
which is absent in the flat symbol model.

An expanded 24-by-24 curved Hessian is deliberately not fabricated here.
Its absence is visible in :mod:`status` and keeps the theorem fail closed.
"""

from __future__ import annotations

from dataclasses import dataclass
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


def _digest(matrix: sp.MatrixBase) -> str:
    payload = sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class CovariantAuxiliaryAction:
    background: CylinderBackground
    covector: sp.Matrix
    cylinder_gauge_symbol: sp.Matrix
    flat_limit_gauge_symbol: sp.Matrix
    source_flat_gauge_symbol: sp.Matrix

    @staticmethod
    def build() -> "CovariantAuxiliaryAction":
        background = CylinderBackground.build()
        source = OrdinaryDerivativeWeylSystem.build()
        zeta = source.covector

        def tensor_coordinates(tensor: sp.Matrix) -> sp.Matrix:
            return sp.Matrix([tensor[a, b] for a, b in SYMMETRIC_COORDINATES])

        def gauge_symbol(auxiliary_background: sp.Matrix) -> sp.Matrix:
            # Ghosts are (xi, kappa, sigma); fields are (h,f,v).  At a normal
            # frame the diffeomorphism variation of the auxiliary tensor is
            # L_xi phi_bar.  This is the curvature-dependent term missed by
            # a naive covariantization of the flat symbol.
            result = sp.zeros(24, 9)
            for column in range(4):
                xi = sp.zeros(4, 1)
                xi[column] = 1
                result[:10, column] = tensor_coordinates(
                    zeta * xi.T + xi * zeta.T
                )

                # (L_xi phi)_ab = phi_cb nabla_a xi^c
                #                  +phi_ac nabla_b xi^c,
                # since nabla phi_bar=0 on the cylinder.
                xi_up = background.inverse_metric * xi
                lie_phi = (
                    zeta * (auxiliary_background * xi_up).T
                    + (auxiliary_background * xi_up) * zeta.T
                )
                result[10:20, column] = tensor_coordinates(lie_phi)

                kappa = sp.zeros(4, 1)
                kappa[column] = 1
                result[10:20, 4 + column] = tensor_coordinates(
                    zeta * kappa.T + kappa * zeta.T
                )
                result[20:24, 4 + column] = -kappa

            result[:10, 8] = tensor_coordinates(background.metric)
            result[20:24, 8] = zeta
            return result

        cylinder = gauge_symbol(background.auxiliary_background)
        flat = gauge_symbol(sp.zeros(4))
        result = CovariantAuxiliaryAction(
            background=background,
            covector=zeta,
            cylinder_gauge_symbol=cylinder,
            flat_limit_gauge_symbol=flat,
            source_flat_gauge_symbol=source.gauge_map,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.flat_limit_gauge_symbol != self.source_flat_gauge_symbol:
            raise AssertionError("the covariant gauge map has the wrong flat limit")
        if self.cylinder_gauge_symbol.shape != (24, 9):
            raise AssertionError("wrong curved auxiliary gauge-map shape")
        # b_bar=0 and phi_bar is parallel, so there are no zeroth-order
        # derivative-of-background terms in the normal-frame gauge symbol.
        if self.cylinder_gauge_symbol[20:24, :4] != sp.zeros(4, 4):
            raise AssertionError("diffeomorphisms unexpectedly move b_bar=0")
        if self.cylinder_gauge_symbol[10:20, :4] == sp.zeros(10, 4):
            raise AssertionError("the background-auxiliary Lie derivative was lost")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-covariant-auxiliary-action-definition-v1",
            "source": {
                "reference": "R.R. Metsaev, arXiv:0707.4437v3, Sec. 6",
                "density": (
                    "sqrt(-g)[-phi^{mu nu} G^b_(mu nu)-F(b)^2/4"
                    "-phi^{mu nu}phi_mu nu/4+(tr phi)^2/4]"
                ),
                "G_b": (
                    "Ric+sym(nabla b)/2+b tensor b/2"
                    "-g(R+2 div b-b^2/2)/2"
                ),
                "gauge_transformations": {
                    "diffeomorphism": "Lie derivative on g, phi, b",
                    "Weyl": "delta g=g sigma, delta b=d sigma, delta phi=0",
                    "conformal_boost": (
                        "delta b=-kappa; delta phi=sym(nabla kappa) at b_bar=0"
                    ),
                },
            },
            "cylinder_background": self.background.certificate(),
            "linearized_gauge_map": {
                "field_order": ["h[10]", "f[10]", "v[4]"],
                "ghost_order": ["xi[4]", "kappa[4]", "sigma[1]"],
                "shape": list(self.cylinder_gauge_symbol.shape),
                "includes_Lie_xi_phi_bar": True,
                "phi_bar_is_parallel": True,
                "flat_limit_equals_certified_K_aux": True,
                "sha256": _digest(self.cylinder_gauge_symbol),
                "flat_limit_sha256": _digest(self.flat_limit_gauge_symbol),
            },
            "exact_global_definition": True,
            "background_is_stationary_reason": (
                "the algebraic phi equation holds and elimination gives the Weyl "
                "action; the conformally flat cylinder has vanishing Bach tensor"
            ),
            "expanded_curved_hessian_emitted": False,
            "guard": (
                "an exact action-derived definition and exact gauge map do not replace "
                "the expanded Hessian, companion, witness, and exhaustive jet checks"
            ),
        }
