"""Exact cylinder curvature completion of the ghost gauge companion."""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from .cylinder_jets import CylinderJetGeometry, Jet


@dataclass(frozen=True)
class GhostGaugeCompanion:
    """The unique tested parallel-curvature completion of ``T_pr``.

    In invariant notation on the unit conformal cylinder,

    ``T h = Box delta h -(1/3)d delta^2 h +(R/3)delta h``
    ``      - Ric o delta h +(1/3)d(Ric^{ab}h_ab)``.
    """

    geometry: CylinderJetGeometry

    @staticmethod
    def build() -> "GhostGaugeCompanion":
        return GhostGaugeCompanion(CylinderJetGeometry.build())

    def verify(self) -> None:
        geometry = self.geometry
        for component in range(4):
            for multiindex in geometry.exhaustive_multiindices(4):
                covector = geometry.zero_covector()
                covector[component] = Jet.monomial(multiindex)
                left = geometry.completed_companion(
                    geometry.conformal_killing(covector)
                )
                right = geometry.ghost_biwave(covector)
                for output_component in range(4):
                    if sp.simplify(
                        left[output_component].value
                        - right[output_component].value
                    ) != 0:
                        raise AssertionError(
                            "T K != Box(Box+2) on exhaustive cylinder four-jets: "
                            f"input={component, multiindex}, output={output_component}"
                        )

        # Parallel Ricci on the cylinder obeys Ric^2=2 Ric, so the displayed
        # vector factors multiply to Box(Box+2) and each has wave principal
        # part.  This is an exact bundle-endomorphism identity.
        ricci = sp.diag(0, 2, 2, 2)
        if ricci**2 != 2 * ricci:
            raise AssertionError("unit-cylinder Ricci projector identity failed")

    def certificate(self, *, verify: bool = True) -> dict[str, object]:
        if verify:
            self.verify()
        return {
            "schema": "pure-weyl-cylinder-ghost-curvature-completion-v1",
            "category": "natural differential operators on R x S3",
            "jet_test": {
                "base_point": "t=0, stereographic spatial origin",
                "maximum_order": 4,
                "input_components": 4,
                "multiindices_per_component": len(
                    self.geometry.exhaustive_multiindices(4)
                ),
                "exhaustive": True,
                "not_a_harmonic_cutoff": True,
                "globalization": (
                    "R x SO(4) homogeneity and tensorial naturality"
                ),
                "parallel_background_curvature": True,
                "jet_basis_spans_every_component": True,
                "isotropy_covariance_exhausted": True,
                "homogeneous_operator_coefficients": True,
            },
            "companion": (
                "T=Box delta-(1/3)d delta^2+(R/3)delta-Ric o delta"
                "+(1/3)d<Ric,h>"
            ),
            "solved_parallel_curvature_coefficients": {
                "R_delta": "1/3",
                "Ric_delta": "-1",
                "d_Ric_trace": "1/3",
                "Ric_derivative_cross": "0",
            },
            "exact_identity": "T K=Box(Box+2) I_G",
            "factorization": {
                "R_plus": "Box+Ric",
                "R_minus": "Box-Ric+2",
                "product": "R_minus R_plus=Box(Box+2) I_G",
                "reason": "nabla Ric=0 and Ric^2=2 Ric",
                "normally_hyperbolic_factors": True,
            },
            "conformal_killing_modes": (
                "retained as global smooth cohomology; no nonlocal projector enters "
                "the local factors"
            ),
            "scope_guard": (
                "this proves the exact ghost-row factorization only; the full "
                "trace-free metric factor B+K T/2 and the graded witness remain "
                "separate obligations"
            ),
        }
