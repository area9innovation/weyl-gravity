"""All-level E/A/L spectrum of the curvature-prolonged equations.

This module composes four exact results which were previously certified in
separate workstreams:

* the exhaustive curved two-jet comparison between the 26-state
  Weyl--Cotton system and the covariant Bach/dual-Bach equations;
* the symbolic all-energy metric preimages of every E/A/L curvature block;
* the global flat-BGG exactness theorem on ``R x S3``; and
* the exact split BGG rank formulas.

The resulting proof is symbolic in the compact energy ``n``.  The displayed
levels two through six are regressions only, not a cutoff definition of the
module.  No metric reconstruction from arbitrary curvature is used: the
harmonic right inverse occurs only in the already-certified D-finite block
comparison.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import sympy as sp

from bridge.bgg_operators import CylinderBGGBlock, symbolic_dimensions
from bridge.metric_preimages.all_energy import BRANCH_MINIMUM, block_dimension

from .weyl_3plus1 import (
    COTTON_DIMENSION,
    WEYL_DIMENSION,
    WeylCottonBachFirstOrder,
)


N = sp.symbols("n", integer=True, positive=True)
R = sp.symbols("r", positive=True, real=True)
Q = sp.symbols("q")


def _parse(expression: object) -> sp.Expr:
    return sp.sympify(expression, locals={"n": N, "r": R, "pi": sp.pi})


def _branch_dimension(family: str) -> sp.Expr:
    return sp.expand(block_dimension(family, N))


def _expected_pivot_square(family: str) -> sp.Expr:
    z = 1 + R**2
    return {
        "E": N * (N - 1) * (N + 1) / (256 * sp.pi**2 * z**4),
        "A": N * (N - 2) * (N - 1) / (1024 * sp.pi**2 * (N + 2) * z**2),
        "L": N * (N - 3) * (N - 1) / (256 * sp.pi**2 * z**4),
    }[family]


@dataclass(frozen=True)
class AllLevelCurvatureEALSpectrum:
    """Exact composition proof for the parity-complete E/A/L spectrum."""

    jet_certificate: Mapping[str, object]
    preimage_certificate: Mapping[str, object]
    bgg_certificate: Mapping[str, object]
    first_order: WeylCottonBachFirstOrder
    prolongation_symbol: sp.Matrix
    prolongation_inclusion: sp.Matrix
    prolongation_projection: sp.Matrix
    defining_operator: sp.Matrix
    defining_retraction: sp.Matrix
    stable_eal_dimension: sp.Expr
    stable_bgg_physical_dimension: sp.Expr
    bgg_joint_equation_rank: sp.Expr
    character_resolution: sp.Expr
    character_eal: sp.Expr
    low_level_dimensions: tuple[int, ...]
    low_level_joint_equation_ranks: tuple[int, ...]

    @staticmethod
    def build(
        *,
        jet_certificate: Mapping[str, object],
        preimage_certificate: Mapping[str, object],
        bgg_certificate: Mapping[str, object],
    ) -> "AllLevelCurvatureEALSpectrum":
        first_order = WeylCottonBachFirstOrder.build()

        # At an arbitrary normal-frame covector, c=L(zeta)u is the exact
        # symbol of the covariant first-divergence definition.  These matrices
        # prove that adjoining c creates a graph, not a second solution copy.
        zeta = sp.symbols("eal_zeta_0:4", real=True)
        prolongation_symbol = sum(
            (
                zeta[axis]
                * first_order.decomposition.cotton_divergence_coefficients[axis]
                for axis in range(4)
            ),
            sp.zeros(COTTON_DIMENSION, WEYL_DIMENSION),
        )
        inclusion = sp.eye(WEYL_DIMENSION).col_join(prolongation_symbol)
        projection = sp.eye(WEYL_DIMENSION).row_join(
            sp.zeros(WEYL_DIMENSION, COTTON_DIMENSION)
        )
        defining = (-prolongation_symbol).row_join(sp.eye(COTTON_DIMENSION))
        retraction = sp.zeros(WEYL_DIMENSION, COTTON_DIMENSION).col_join(
            sp.eye(COTTON_DIMENSION)
        )

        one_chirality = sum(
            (_branch_dimension(family) for family in ("E", "A", "L")),
            sp.Integer(0),
        )
        stable_eal = sp.expand(2 * one_chirality)
        dimensions = symbolic_dimensions(N)
        stable_bgg = sp.expand(dimensions.curvature - 2 * dimensions.equation)
        joint_rank = sp.expand(2 * dimensions.equation)

        character_resolution = sp.factor(
            (5 * Q**2 - 9 * Q**4 + 4 * Q**5) / (1 - Q) ** 4
        )
        e_character = Q**2 * (5 - 3 * Q) / (1 - Q) ** 3
        a_character = Q**3 * (8 - 9 * Q + 3 * Q**2) / (1 - Q) ** 3
        l_character = Q**4 * (5 - 3 * Q) / (1 - Q) ** 3
        character_eal = sp.factor(e_character + a_character + l_character)

        low_dimensions: list[int] = []
        low_joint_ranks: list[int] = []
        for energy in range(2, 7):
            block = CylinderBGGBlock.at_energy(energy)
            block.verify()
            low_dimensions.append(block.dimensions.physical)
            low_joint_ranks.append(2 * block.dimensions.equation)

        result = AllLevelCurvatureEALSpectrum(
            jet_certificate=jet_certificate,
            preimage_certificate=preimage_certificate,
            bgg_certificate=bgg_certificate,
            first_order=first_order,
            prolongation_symbol=prolongation_symbol,
            prolongation_inclusion=inclusion,
            prolongation_projection=projection,
            defining_operator=defining,
            defining_retraction=retraction,
            stable_eal_dimension=stable_eal,
            stable_bgg_physical_dimension=stable_bgg,
            bgg_joint_equation_rank=joint_rank,
            character_resolution=character_resolution,
            character_eal=character_eal,
            low_level_dimensions=tuple(low_dimensions),
            low_level_joint_equation_ranks=tuple(low_joint_ranks),
        )
        result.verify()
        return result

    def _verify_jet_dependency(self) -> None:
        certificate = self.jet_certificate
        if certificate.get("schema") != "pure-weyl-cotton-curved-jet-comparison-v1":
            raise AssertionError("wrong curved Weyl/Cotton jet certificate")
        if not certificate.get("coverage_complete"):
            raise AssertionError("curved Weyl/Cotton jet comparison is not exhaustive")
        if (certificate.get("tested_two_jets"), certificate.get("expected_two_jets")) != (
            150,
            150,
        ):
            raise AssertionError("curved Weyl/Cotton two-jet count drifted")
        for defect in (
            "algebraic_weyl_defects",
            "cotton_coordinate_defects",
            "cotton_reconstruction_defects",
            "bach_coordinate_defects",
        ):
            if certificate.get(defect) != 0:
                raise AssertionError(f"nonzero curved operator defect: {defect}")
        if not (
            certificate.get("curved_EB_equations")
            and certificate.get("curved_EB_first_order_closure")
            and certificate.get("covariant_first_divergence_matches_3plus1_table")
            and certificate.get("covariant_Bach_matches_first_order_table")
        ):
            raise AssertionError("26-state/covariant equation equivalence is incomplete")

    def _verify_preimage_dependency(self) -> None:
        certificate = self.preimage_certificate
        if certificate.get("schema") != "pure-weyl-cylinder-preimages-v1":
            raise AssertionError("wrong all-energy metric-preimage certificate")
        if certificate.get("right_inverse_identity") != (
            "C1 R_n=id on E/A/L curvature image blocks"
        ):
            raise AssertionError("all-energy curvature right inverse is missing")
        parity = certificate.get("parity_completion", {})
        if parity.get("orientation") != -1 or parity.get("hodge_eigenvalues") != {
            "+": "-I",
            "-": "+I",
        }:
            raise AssertionError("parity/Hodge completion convention drifted")

        records = {
            str(record.get("family")): record
            for record in certificate.get("records", ())
        }
        if set(records) != {"E", "A", "L"}:
            raise AssertionError("all-energy preimage families are incomplete")
        expected_irreps = {
            "E": (N / 2 + 1, N / 2 - 1),
            "A": (N / 2, N / 2 - 1),
            "L": (N / 2, N / 2 - 2),
        }
        for family, record in records.items():
            if record.get("energy") != "n":
                raise AssertionError(f"{family} preimage is not symbolic in n")
            if record.get("minimum_energy") != BRANCH_MINIMUM[family]:
                raise AssertionError(f"{family} low-energy boundary drifted")
            if sp.expand(_parse(record.get("dimension")) - _branch_dimension(family)) != 0:
                raise AssertionError(f"{family} irrep dimension drifted")
            irrep = tuple(_parse(value) for value in record.get("irrep", ()))
            if irrep != expected_irreps[family]:
                raise AssertionError(f"{family} SO(4) irrep drifted")
            pivot = _parse(record.get("curvature_pivot"))
            if sp.factor(pivot**2 - _expected_pivot_square(family)) != 0:
                raise AssertionError(f"{family} curvature pivot normalization drifted")
            if sp.simplify(
                pivot.subs({N: BRANCH_MINIMUM[family], R: sp.Integer(1)})
            ) == 0:
                raise AssertionError(f"{family} curvature pivot vanishes at its boundary")
            if record.get("hodge_eigenvalue") != "-I":
                raise AssertionError(f"{family} positive-chirality Hodge sign drifted")

    def _verify_bgg_dependency(self) -> None:
        certificate = self.bgg_certificate
        if certificate.get("schema") != "pure-weyl-cylinder-bgg-normal-form-v1":
            raise AssertionError("wrong all-energy BGG certificate")
        required = {
            "C K=0",
            "D2 C=C^sharp star C=0",
            "B=C^sharp C",
            "ker C=im K",
            "ker D2=im C",
            "ker B/im K=W+ direct-sum W-",
        }
        if not required.issubset(set(certificate.get("identities", ()))):
            raise AssertionError("all-energy BGG identities are incomplete")
        if certificate.get("external_theorem_dependency") != (
            "smooth flat-BGG exactness on R x S3"
        ):
            raise AssertionError("global BGG exactness input is missing")

    def verify(self) -> None:
        self._verify_jet_dependency()
        self._verify_preimage_dependency()
        self._verify_bgg_dependency()
        self.first_order.verify()

        identity_10 = sp.eye(WEYL_DIMENSION)
        identity_26 = sp.eye(WEYL_DIMENSION + COTTON_DIMENSION)
        if self.prolongation_projection * self.prolongation_inclusion != identity_10:
            raise AssertionError("Weyl--Cotton projection/inclusion is not inverse")
        if self.defining_operator * self.prolongation_inclusion != sp.zeros(
            COTTON_DIMENSION, WEYL_DIMENSION
        ):
            raise AssertionError("prolonged inclusion violates the Cotton definition")
        if self.prolongation_inclusion * self.prolongation_projection - identity_26 != (
            -self.defining_retraction * self.defining_operator
        ):
            raise AssertionError("Cotton defining row does not remove the duplicate slot")

        if sp.expand(
            self.stable_eal_dimension - self.stable_bgg_physical_dimension
        ) != 0:
            raise AssertionError("stable all-energy E/A/L dimension mismatch")
        if self.stable_eal_dimension != 2 * (3 * N**2 - 7):
            raise AssertionError("stable parity-complete E/A/L formula drifted")
        dimensions = symbolic_dimensions(N)
        if sp.expand(
            dimensions.curvature
            - self.bgg_joint_equation_rank
            - self.stable_bgg_physical_dimension
        ) != 0:
            raise AssertionError("BGG curvature rank exhaustion failed")
        if sp.simplify(self.character_resolution - self.character_eal) != 0:
            raise AssertionError("symbolic E/A/L character identity failed")
        if self.low_level_dimensions != (10, 40, 82, 136, 202):
            raise AssertionError("low-level E/A/L regression drifted")
        if self.low_level_joint_equation_ranks != (0, 0, 18, 64, 148):
            raise AssertionError("low-level BGG joint equation ranks drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        dimensions = symbolic_dimensions(N)
        records = self.preimage_certificate["records"]
        return {
            "schema": "pure-weyl-curvature-eal-spectrum-all-level-v1",
            "proof_kind": "symbolic all-energy composition theorem",
            "all_level_not_finite_cutoff": True,
            "compact_energy_variable": "n",
            "equation_bridge": {
                "state": "u=(E_STF[5],B_STF[5]), c=(X_sl3[8],Y_sl3[8])",
                "state_dimension": WEYL_DIMENSION + COTTON_DIMENSION,
                "covariant_target": (
                    "c=div(Psi), C1^sharp Psi=0, C1^sharp star Psi=0"
                ),
                "exhaustive_Weyl_two_jets": 150,
                "operator_defects": 0,
                "exact_26_state_covariant_equivalence": True,
            },
            "cotton_prolongation": {
                "definition": "c=L^alpha nabla_alpha u",
                "algebraic_c_coefficient": "I_16",
                "projection_times_inclusion": "I_10",
                "inclusion_projection_minus_identity": "-R(c-L nabla u)",
                "cotton_unique_no_duplication": True,
                "metric_reconstruction_used": False,
            },
            "global_exhaustion": {
                "theorem_input": "smooth flat-BGG exactness on R x S3",
                "isomorphism": (
                    "ker(B_lin)/im(K0) = ker(C1^sharp) intersection "
                    "ker(C1^sharp star)"
                ),
                "SO42_equivariant": True,
                "curvature_dimension": str(dimensions.curvature),
                "rank_C1sharp": str(dimensions.equation),
                "rank_C1sharp_star": str(dimensions.equation),
                "joint_equation_rank": str(self.bgg_joint_equation_rank),
                "physical_kernel_dimension": str(
                    self.stable_bgg_physical_dimension
                ),
                "global_BGG_exhaustion": True,
            },
            "branches": [
                {
                    "family": record["family"],
                    "minimum_energy": record["minimum_energy"],
                    "frequency": "n",
                    "positive_chirality_irrep": record["irrep"],
                    "one_chirality_dimension": record["dimension"],
                    "curvature_pivot": record["curvature_pivot"],
                    "positive_hodge_eigenvalue": "-I",
                    "negative_hodge_eigenvalue": "+I",
                }
                for record in records
            ],
            "chirality": {
                "positive": "(jL,jR), star=-I",
                "negative": "(jR,jL), star=+I",
                "parity_map": "alpha<->gamma",
                "both_chiralities": True,
            },
            "symbolic_character": {
                "BGG_resolution": str(self.character_resolution),
                "E_plus_A_plus_L": str(self.character_eal),
                "defect": 0,
                "identity_all_coefficients": True,
            },
            "low_level_regression": {
                "energies": [2, 3, 4, 5, 6],
                "physical_dimensions": list(self.low_level_dimensions),
                "joint_equation_ranks": list(self.low_level_joint_equation_ranks),
                "role": "regression only; not the proof of the all-level result",
            },
            "EAL_curvature_spectrum_match": True,
            "status_ledger_modified": False,
            "promotion_boundary": (
                "this producer proves the all-level solution-module spectrum; "
                "the fail-closed status ledger may additionally require sourced "
                "constraint propagation before consuming it"
            ),
            "not_proved_here": [
                "constraint-adjusted symmetric hyperbolicity",
                "sourced subsidiary identity",
                "constraint propagation",
                "causal Green operators or BV Green homotopy",
                "support-local reconstruction of a metric from curvature",
            ],
            "fail_closed": True,
        }
