"""Aggregate theorem: completion adds no centered residual cohomology."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from analytic_completion.fock.bosonic import BosonicKreinFock
from analytic_completion.fock.energy_blocks import TotalDegreeBlocks
from analytic_completion.ghosts.factor import ResidualGhostFactor
from analytic_completion.one_particle.generators import ClosedGeneratorCertificate
from analytic_completion.one_particle.krein import OneParticleKreinCompletion
from analytic_completion.residual.cartan import BoundedCartanContraction
from analytic_completion.residual.closed_brst import ClosedResidualBRST


ROOT = Path(__file__).resolve().parents[2]
ALGEBRAIC_CERTIFICATE = ROOT / "bridge" / "certificates" / "metric_to_residual.json"


@dataclass(frozen=True)
class CompletedResidualComplex:
    one_particle: OneParticleKreinCompletion
    fock: BosonicKreinFock
    ghosts: ResidualGhostFactor
    blocks: TotalDegreeBlocks
    cartan: BoundedCartanContraction

    @classmethod
    def build(cls) -> "CompletedResidualComplex":
        one_particle = OneParticleKreinCompletion()
        fock = BosonicKreinFock(one_particle)
        ghosts = ResidualGhostFactor.build()
        blocks = TotalDegreeBlocks(ghosts)
        cartan = BoundedCartanContraction(ClosedResidualBRST(blocks))
        return cls(one_particle, fock, ghosts, blocks, cartan)

    @staticmethod
    def algebraic_result() -> dict[str, object]:
        return json.loads(ALGEBRAIC_CERTIFICATE.read_text(encoding="utf-8"))

    def verify(self) -> None:
        self.one_particle.verify()
        ClosedGeneratorCertificate().verify()
        self.fock.verify()
        self.ghosts.verify()
        self.blocks.verify(verify_ghosts=False)
        self.cartan.brst.verify(verify_dependencies=False)
        self.cartan.verify(verify_dependencies=False)
        algebraic = self.algebraic_result()
        if algebraic["vacuum"]["h4"] != 0:
            raise AssertionError("vacuum centered cohomology changed")
        if algebraic["one_particle"]["h4"] != 0:
            raise AssertionError("one-particle centered cohomology changed")
        if algebraic["two_particle"]["h4"] != 2:
            raise AssertionError("two-particle centered cohomology is not two dimensional")
        if algebraic["two_particle"]["normalized_gram"] != [[1, 0], [0, 1]]:
            raise AssertionError("algebraic centered Gram is not I_2")
        algebraic_c4 = (
            algebraic["vacuum"]["cochain_dimensions"][1]
            + algebraic["one_particle"]["cochain_dimensions"][1]
            + algebraic["two_particle"]["cochain_dimensions"][0]
        )
        if self.blocks.centered_dimension_by_ghost_number()[4] != algebraic_c4:
            raise AssertionError("completed and algebraic centered ghost-number-four blocks differ")

    def certificate(self, verify: bool = True) -> dict[str, object]:
        if verify:
            self.verify()
        algebraic = self.algebraic_result()
        return {
            "schema": "pure-weyl-completed-residual-cohomology-v1",
            "theorem": "energy-mode Krein completion theorem",
            "selected_boundary_problem": "closed cylinder with all fifteen residual generators gauged",
            "completed_state_space": "Gamma_s(H_1) completed_tensor Lambda(so(4,2)^*)",
            "state_krein_symmetry": "Gamma_s(J_1) tensor identity",
            "residual_operator": "closed maximal total-degree block direct sum",
            "residual_operator_bounded": False,
            "range_closed": True,
            "range_proof": [
                "off center, ker Q = im Q by the bounded Cartan contraction",
                "off-center range equals the closed kernel",
                "the centered range is finite dimensional",
                "the orthogonal total-degree sum makes the total range closed",
            ],
            "ordinary_equals_reduced_cohomology": True,
            "cohomology_localizes_to_delta_zero": True,
            "completed_centered_equals_algebraic_centered": True,
            "centered": {
                "matter_energy_range": [0, 4],
                "total_dimension": self.blocks.dimension(0),
                "cochain_dimensions_ghost_3_4_5": [727, 3084, 8532],
                "vacuum_H4": algebraic["vacuum"]["h4"],
                "one_particle_H4": algebraic["one_particle"]["h4"],
                "two_particle_H4": algebraic["two_particle"]["h4"],
                "classes": ["W_+^2", "W_-^2"],
                "normalized_gram": algebraic["two_particle"]["normalized_gram"],
            },
            "interpretation": "two classical ghost-dressed weight-four vertex classes, not particles",
            "scope_guards": [
                "energy-mode completion only",
                "no covariant metric-field Sobolev theorem",
                "no distributional or Green-hyperbolic theorem",
                "no integrated SO(4,2) group representation",
                "no positive graviton Hilbert space",
                "no quantum or interacting unitarity claim",
            ],
        }
