"""Full trace-free metric gauge completion on the conformal cylinder.

The operator is defined on the complete trace-free bundle by

``H=B_lin+(1/2)K T``.

Here ``B_lin`` is reconstructed from the full linearized Weyl tensor, not by
extending a transverse formula away from its gauge slice.  The detour identity
and exact ghost factor imply

``H K = (1/2) K Box(Box+2)``.

Consequently ``B := H-(1/2)K T`` has the exact local Ward identity ``BK=0``.
The module does *not* yet claim that ``H`` has been factored into normally
hyperbolic operators on the full trace-free bundle.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

import sympy as sp

from .cylinder_jets import CylinderJetGeometry, Jet, _sum, _zero


def _tensor_add(*tensors):
    return [
        [
            _sum(tensor[mu][nu] for tensor in tensors)
            for nu in range(4)
        ]
        for mu in range(4)
    ]


def _tensor_scale(scalar, tensor):
    return [
        [scalar * tensor[mu][nu] for nu in range(4)] for mu in range(4)
    ]


@dataclass(frozen=True)
class GaugeFixedMetricBiwave:
    geometry: CylinderJetGeometry

    @staticmethod
    def build() -> "GaugeFixedMetricBiwave":
        return GaugeFixedMetricBiwave(CylinderJetGeometry.build())

    def tracefree_section(self, component: int, multiindex: tuple[int, ...]):
        """One exhaustive local basis jet of ``S^2_0 T*``.

        The nine independent components are ``00,01,02,03,11,12,13,22,23``;
        ``33`` is fixed by the trace constraint throughout the coordinate jet.
        """

        pairs = (
            (0, 0),
            (0, 1),
            (0, 2),
            (0, 3),
            (1, 1),
            (1, 2),
            (1, 3),
            (2, 2),
            (2, 3),
        )
        tensor = [[_zero() for _ in range(4)] for _ in range(4)]
        value = Jet.monomial(multiindex)
        mu, nu = pairs[component]
        tensor[mu][nu] = value
        tensor[nu][mu] = value
        # g^{ij}=Omega^{-2}delta^{ij}; hence h_33=Omega^2 h_00-h_11-h_22.
        spatial_metric = self.geometry.metric[1][1]
        tensor[3][3] = (
            spatial_metric * tensor[0][0] - tensor[1][1] - tensor[2][2]
        )
        return tensor

    def operator(self, tensor):
        # Import locally to avoid a module cycle while constructing B from C_1.
        from .linearized_bach import LinearizedBach

        bach = LinearizedBach.build().action_normalized_bach(tensor)
        gauge = self.geometry.conformal_killing(
            self.geometry.completed_companion(tensor)
        )
        return _tensor_add(bach, _tensor_scale(Fraction(1, 2), gauge))

    def conformal_killing_of_covector(self, covector):
        return self.geometry.conformal_killing(covector)

    def half_k_ghost_biwave(self, covector):
        return _tensor_scale(
            Fraction(1, 2),
            self.geometry.conformal_killing(
                self.geometry.ghost_biwave(covector)
            ),
        )

    def verify_intertwiner(self) -> None:
        # The two exact local identities are certified exhaustively in their
        # minimal differential orders.  Their composition is the fifth-order
        # intertwiner without requiring a redundant fifth-jet Bach expansion.
        from .curvature_completion import GhostGaugeCompanion
        from .linearized_bach import LinearizedBach

        LinearizedBach.build().verify()
        GhostGaugeCompanion(self.geometry).verify()

    def certificate(self, *, verify: bool = True) -> dict[str, object]:
        if verify:
            self.verify_intertwiner()
        return {
            "schema": "pure-weyl-cylinder-full-metric-biwave-v1",
            "category": "trace-free metric jets on R x S3",
            "operator_origin": "H=B_lin+(1/2)K T on the full trace-free bundle",
            "operator": "H=B_lin+(1/2)K T",
            "witness_field_block": "2H=2B_lin+K T",
            "exact_intertwiner": "H K=(1/2)K Box(Box+2)",
            "proof_decomposition": [
                "C_1 K=0 on exhaustive local third jets, hence B_lin K=0",
                "T K=Box(Box+2) on exhaustive local fourth jets",
            ],
            "derived_detour_operator": "B=H-(1/2)K T",
            "ward_identity": "B K=0",
            "physical_restriction": (
                "on ker(T), H=B; the certified TT and transverse-vector "
                "physical restrictions retain their earlier Green factors"
            ),
            "scope_guard": (
                "the exact local second-order factorization or equivalent "
                "hyperbolic auxiliary system for H is not asserted by this "
                "intertwiner certificate"
            ),
            "globalization": {
                "equivariance": "R x SO(4)",
                "parallel_background_curvature": True,
                "exhaustive_fibre_and_jet_components": True,
                "not_a_finite_harmonic_test": True,
            },
        }
