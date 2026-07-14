"""Explicit closed-universe residual BFV boundary policy.

This module does not claim that every quantization of the conformal cylinder
must gauge compact time translation.  It makes the boundary problem used by
Paper VII machine-readable: the Cauchy surface is the closed oriented
three-sphere, no surface-charge degrees of freedom are adjoined, and all
fifteen conformal reducibilities are represented by BFV constraints.
"""

from __future__ import annotations

from dataclasses import dataclass

from bridge.residual_bfv.conformal_ce import ConformalCE


@dataclass(frozen=True)
class ClosedUniverseBFVChoice:
    spatial_slice: str
    boundary_components: tuple[str, ...]
    residual_constraints: tuple[str, ...]
    compact_time_generator: str
    surface_charge_rank: int
    deparametrized: bool

    @classmethod
    def build(cls) -> "ClosedUniverseBFVChoice":
        ce = ConformalCE.build()
        result = cls(
            spatial_slice="S^3",
            boundary_components=(),
            residual_constraints=ce.names,
            compact_time_generator="D",
            surface_charge_rank=0,
            deparametrized=False,
        )
        result.verify()
        return result

    def verify(self) -> None:
        ce = ConformalCE.build()
        if self.boundary_components:
            raise AssertionError("closed-universe policy has a spatial boundary")
        if self.surface_charge_rank != 0:
            raise AssertionError("boundaryless policy contains a surface charge")
        if self.residual_constraints != ce.names:
            raise AssertionError("not every residual reducibility is constrained")
        if self.compact_time_generator not in self.residual_constraints:
            raise AssertionError("D is not included in the residual constraints")
        if self.deparametrized:
            raise AssertionError("closed-universe policy cannot be deparametrized")

    @property
    def cartan_contraction_allowed(self) -> bool:
        return (
            self.compact_time_generator in self.residual_constraints
            and self.surface_charge_rank == 0
            and not self.deparametrized
        )

    def retain_compact_time_as_charge(self) -> "ClosedUniverseBFVChoice":
        """Return the distinct boundary/deparametrized problem for guards."""

        return ClosedUniverseBFVChoice(
            spatial_slice=self.spatial_slice,
            boundary_components=("time-reference sector",),
            residual_constraints=tuple(
                name
                for name in self.residual_constraints
                if name != self.compact_time_generator
            ),
            compact_time_generator=self.compact_time_generator,
            surface_charge_rank=1,
            deparametrized=True,
        )
