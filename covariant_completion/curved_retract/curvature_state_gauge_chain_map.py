"""Exact degree-minus-one curvature graph chain square.

The curvature state map is ``T_state=(C1,div C1)`` and depends only on the
metric component of the 24-field auxiliary bundle.  The auxiliary gauge map
has nine inputs: four diffeomorphisms, four conformal-boost/Stueckelberg
directions with zero metric component, and one Weyl scalar.  This module
checks ``C1 K_aux=0`` on the complete relevant jet fibres.  Since the first
component vanishes as a global natural operator, its covariant divergence
vanishes as well, proving ``T_state K_aux=0`` without a redundant fourth-jet
test of the zero tensor.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from covariant_completion.curved_operator.conventions import (
    CurvedBVConventions,
    SYMMETRIC_COORDINATES,
)
from covariant_completion.minimal_witness.cylinder_jets import Jet
from covariant_completion.minimal_witness.linearized_bach import LinearizedBach


def _weyl_value_defects(weyl: list) -> int:
    return sum(
        int(sp.expand(weyl[a][b][c][d].value) != 0)
        for a in range(4)
        for b in range(4)
        for c in range(4)
        for d in range(4)
    )


@dataclass(frozen=True)
class CurvatureStateGaugeChainMap:
    """Exhaustive certificate data for ``T_state K_aux=0``."""

    diffeomorphism_jet_count: int
    weyl_scalar_jet_count: int
    boost_components: int
    diffeomorphism_defects: int
    weyl_scalar_defects: int
    auxiliary_metric_block_defects: int

    @staticmethod
    def build() -> "CurvatureStateGaugeChainMap":
        bach = LinearizedBach.build()
        geometry = bach.geometry
        conventions = CurvedBVConventions.build()

        diffeomorphism_defects = 0
        diffeomorphism_jet_count = 0
        for component in range(4):
            for multiindex in geometry.exhaustive_multiindices(3):
                covector = geometry.zero_covector()
                covector[component] = Jet.monomial(multiindex)
                diffeomorphism_defects += _weyl_value_defects(
                    bach.linearized_weyl(geometry.conformal_killing(covector))
                )
                diffeomorphism_jet_count += 1

        weyl_scalar_defects = 0
        weyl_scalar_jet_count = 0
        for multiindex in geometry.exhaustive_multiindices(2):
            scalar = Jet.monomial(multiindex)
            conformal_metric = [
                [geometry.metric[a][b] * scalar for b in range(4)]
                for a in range(4)
            ]
            weyl_scalar_defects += _weyl_value_defects(
                bach.linearized_weyl(conformal_metric)
            )
            weyl_scalar_jet_count += 1

        generator = conventions.gauge_generator
        metric_block_defects = 0
        for coefficient in generator.derivative_coefficients:
            metric_block_defects += sum(
                int(coefficient[row, column] != 0)
                for row in range(10)
                for column in range(4, 9)
            )
        metric_block_defects += sum(
            int(generator.zeroth_coefficient[row, column] != 0)
            for row in range(10)
            for column in range(4, 8)
        )
        metric_coordinates = sp.Matrix(
            [geometry.metric[a][b].value for a, b in SYMMETRIC_COORDINATES]
        )
        metric_block_defects += sum(
            int(value != 0)
            for value in (
                generator.zeroth_coefficient[:10, 8] - metric_coordinates
            )
        )

        result = CurvatureStateGaugeChainMap(
            diffeomorphism_jet_count=diffeomorphism_jet_count,
            weyl_scalar_jet_count=weyl_scalar_jet_count,
            boost_components=4,
            diffeomorphism_defects=diffeomorphism_defects,
            weyl_scalar_defects=weyl_scalar_defects,
            auxiliary_metric_block_defects=metric_block_defects,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.diffeomorphism_jet_count != 4 * 35:
            raise AssertionError("diffeomorphism third-jet coverage drifted")
        if self.weyl_scalar_jet_count != 15:
            raise AssertionError("Weyl-scalar second-jet coverage drifted")
        if self.boost_components != 4:
            raise AssertionError("conformal-boost ghost coverage drifted")
        if self.diffeomorphism_defects:
            raise AssertionError("C1 K_diffeomorphism is nonzero")
        if self.weyl_scalar_defects:
            raise AssertionError("C1 K_Weyl is nonzero")
        if self.auxiliary_metric_block_defects:
            raise AssertionError("the auxiliary metric gauge block drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-curvature-state-gauge-chain-map-v1",
            "auxiliary_ghost_order": [
                "diffeomorphism[4]",
                "conformal_boost[4]",
                "Weyl_scalar[1]",
            ],
            "T_state": "(C1,div C1)",
            "metric_gauge_components": {
                "diffeomorphism": "K_met xi",
                "conformal_boost": "zero",
                "Weyl_scalar": "g sigma",
            },
            "exhaustive_jet_certificate": {
                "diffeomorphism_composition_order": 3,
                "diffeomorphism_jets": self.diffeomorphism_jet_count,
                "Weyl_scalar_composition_order": 2,
                "Weyl_scalar_jets": self.weyl_scalar_jet_count,
                "boost_components": self.boost_components,
                "diffeomorphism_defects": self.diffeomorphism_defects,
                "Weyl_scalar_defects": self.weyl_scalar_defects,
                "auxiliary_metric_block_defects": (
                    self.auxiliary_metric_block_defects
                ),
            },
            "C1_K_aux": "zero",
            "div_C1_K_aux": "zero as the covariant derivative of the exact zero natural operator",
            "T_state_K_aux": "zero",
            "T_state_K_aux_exact": True,
            "globalization": "R x SO(4) homogeneity of natural operators",
            "support_local": True,
            "fail_closed": True,
        }
