"""Causal solution theorem for the constrained Weyl--Cotton PDE.

This module applies the standard global well-posedness and finite-propagation
theorem for linear symmetric-hyperbolic systems to the exact rank-26
constraint-adjusted Weyl--Cotton operator on ``R x S3``.

There are two different operators which must not be conflated:

* ``G_unconstrained^+/-`` solves the square rank-26 hyperbolic equation for
  every compactly supported rank-26 source;
* ``G_constrained^+/-`` is its restriction to the kernel of the exact
  source-compatibility operator.  The sourced subsidiary identity proves
  that this restriction lands in the fourteen-constraint kernel.

The result is a curvature-block causal PDE theorem.  It does not construct a
BV Green witness, a degree-minus-one chain homotopy, or Green operators for
the complete prolonged BV complex.
"""

from __future__ import annotations

from dataclasses import dataclass

from .weyl_cotton_differential_ideal import (
    WeylCottonDifferentialIdealAudit,
)
from .weyl_cotton_hyperbolic import ConstraintAdjustedWeylCottonEvolution


@dataclass(frozen=True)
class CausalWeylCottonPDE:
    """Prerequisites and conclusions of the curvature causal theorem."""

    evolution: ConstraintAdjustedWeylCottonEvolution
    differential_ideal: WeylCottonDifferentialIdealAudit
    background_globally_hyperbolic: bool
    cauchy_surfaces_compact: bool
    coefficients_global_smooth: bool
    temporal_principal_matrix_positive: bool
    characteristic_cone_inside_metric_cone: bool
    symmetric_hyperbolic_green_theorem: str

    @staticmethod
    def build() -> "CausalWeylCottonPDE":
        result = CausalWeylCottonPDE(
            evolution=ConstraintAdjustedWeylCottonEvolution.build(),
            differential_ideal=WeylCottonDifferentialIdealAudit.build(),
            background_globally_hyperbolic=True,
            cauchy_surfaces_compact=True,
            coefficients_global_smooth=True,
            temporal_principal_matrix_positive=True,
            characteristic_cone_inside_metric_cone=True,
            symmetric_hyperbolic_green_theorem=(
                "global existence, uniqueness and finite propagation for linear "
                "symmetric-hyperbolic systems on globally hyperbolic spacetimes; "
                "equivalently the symmetric-hyperbolic case of Bär, "
                "Green-hyperbolic operators on globally hyperbolic spacetimes, "
                "Commun. Math. Phys. 333 (2015) 1585-1615"
            ),
        )
        result.verify()
        return result

    def verify(self) -> None:
        self.evolution.verify()
        self.differential_ideal.verify()
        if not self.background_globally_hyperbolic:
            raise AssertionError("the causal PDE theorem needs global hyperbolicity")
        if not self.cauchy_surfaces_compact:
            raise AssertionError("the recorded cylinder support statement drifted")
        if not self.coefficients_global_smooth:
            raise AssertionError("the hyperbolic coefficients are not global smooth")
        if not self.temporal_principal_matrix_positive:
            raise AssertionError("the temporal symmetric-hyperbolic form is not positive")
        if not self.characteristic_cone_inside_metric_cone:
            raise AssertionError("the PDE cone is not contained in the metric cone")
        evolution_certificate = self.evolution.certificate()
        if not evolution_certificate["evolution_symmetrizer_positive"]:
            raise AssertionError("positive evolution symmetrizer regressed")
        if not evolution_certificate["evolution_spatial_symbols_self_adjoint"]:
            raise AssertionError("symmetric-hyperbolic spatial symbols regressed")
        if not evolution_certificate["all_characteristics_causal"]:
            raise AssertionError("a superluminal curvature characteristic appeared")
        if not evolution_certificate["exact_sourced_subsidiary_operator_identity"]:
            raise AssertionError("sourced subsidiary identity regressed")
        if not evolution_certificate["subsidiary_symmetrizer_positive"]:
            raise AssertionError("subsidiary uniqueness theorem is unavailable")
        ideal_certificate = self.differential_ideal.certificate()
        if not ideal_certificate[
            "sourced_subsidiary_identity_curvature_corrected"
        ]:
            raise AssertionError("unit-S3 source identity lost its curvature correction")
        if not ideal_certificate[
            "covariant_and_adjusted_differential_ideals_equal"
        ]:
            raise AssertionError("adjusted solutions are not exact curvature solutions")
        if not ideal_certificate["source_compatibility_map_available"]:
            raise AssertionError("compatible curvature sources are not identified")

    def certificate(self) -> dict[str, object]:
        self.verify()
        evolution_certificate = self.evolution.certificate()
        ideal_certificate = self.differential_ideal.certificate()
        return {
            "schema": "pure-weyl-cotton-causal-pde-v1",
            "background": {
                "spacetime": "R x unit S3",
                "metric": "-dt^2+dOmega_3^2",
                "globally_hyperbolic": self.background_globally_hyperbolic,
                "cauchy_surfaces": "Sigma_t={t} x S3",
                "cauchy_surfaces_compact": self.cauchy_surfaces_compact,
                "time_function": "t",
                "lapse": 1,
                "shift": 0,
            },
            "operator": {
                "name": "L_WC",
                "bundle_rank": 26,
                "state": "E[5]+B[5]+A[5]+C[5]+x[3]+y[3]",
                "coefficients_global_smooth": self.coefficients_global_smooth,
                "temporal_principal_matrix": "I_26",
                "positive_symmetrizer": True,
                "spatial_symbols_symmetrized_self_adjoint": True,
                "characteristic_speeds": evolution_certificate[
                    "characteristic_speeds"
                ],
                "characteristic_cone_inside_metric_cone": (
                    self.characteristic_cone_inside_metric_cone
                ),
                "lower_order_terms_do_not_change_characteristic_cone": True,
            },
            "analytic_input": {
                "theorem": self.symmetric_hyperbolic_green_theorem,
                "application": (
                    "for f in Gamma_c(F), choose a Cauchy slice strictly to the "
                    "past (respectively future) of supp(f), solve L_WC u=f with "
                    "zero Cauchy data there, and use uniqueness to make the "
                    "result independent of the chosen slice"
                ),
                "finite_propagation": (
                    "the symmetric-hyperbolic domain of dependence is contained "
                    "in the metric causal domain because every characteristic "
                    "speed has absolute value at most one"
                ),
            },
            "unconstrained_green_operators": {
                "notation": ["G_un^+", "G_un^-"],
                "domain": "Gamma_c(F_WC)",
                "codomain": "Gamma(F_WC)",
                "left_inverse": "L_WC G_un^+/- f=f",
                "right_inverse": "G_un^+/- L_WC u=u for u in Gamma_c(F_WC)",
                "retarded_support": "supp(G_un^+ f) subset J^+(supp f)",
                "advanced_support": "supp(G_un^- f) subset J^-(supp f)",
                "unique": True,
                "exists_for_every_compact_source": True,
                "preserves_constraints_for_arbitrary_source": False,
            },
            "constraint_operator": {
                "notation": "K_WC",
                "rank": 14,
                "constraint_state": "q[3]+r[3]+a[3]+c[3]+s[1]+t[1]",
                "constrained_fields": "ker K_WC",
                "subsidiary_operator": "L_K",
                "subsidiary_symmetric_hyperbolic": True,
                "subsidiary_characteristic": evolution_certificate[
                    "subsidiary_characteristic"
                ],
                "subsidiary_characteristics_causal": True,
            },
            "source_compatibility": {
                "notation": "K_src",
                "compatible_sources": "Gamma_c^comp(F_WC)=ker K_src",
                "rows": ideal_certificate["source_compatibility_rows"],
                "exact_operator_identity": "L_K K_WC=K_src L_WC",
                "unit_S3_curvature_correction_included": True,
                "K_src_is_finite_order_differential": True,
                "K_src_preserves_compact_support": True,
            },
            "compatible_source_restriction": {
                "definition": "G_con^+/-=G_un^+/- restricted to ker K_src",
                "domain": "Gamma_c^comp(F_WC)",
                "codomain": "ker K_WC",
                "constraint_proof": (
                    "for K_src f=0, C=K_WC G_un^+/- f solves L_K C=0; "
                    "retarded/advanced zero data and subsidiary uniqueness give C=0"
                ),
                "left_inverse": "L_WC G_con^+/- f=f for compatible f",
                "right_inverse": (
                    "G_con^+/- L_WC u=u for compact u in ker K_WC; "
                    "the identity makes L_WC u source-compatible"
                ),
                "retarded_support": "supp(G_con^+ f) subset J^+(supp f)",
                "advanced_support": "supp(G_con^- f) subset J^-(supp f)",
                "unique": True,
                "restriction_does_not_use_a_projector_onto_ker_K_src": True,
            },
            "exact_covariant_curvature_system": {
                "adjusted_and_covariant_differential_ideals_equal": True,
                "smooth_solution_spaces_equal": True,
                "therefore_constrained_solutions_satisfy_all_34_covariant_rows": True,
                "pointwise_row_modules_equal": False,
                "pointwise_rank_six_boundary_retained": True,
            },
            "curvature_block_causal_solution_operators": True,
            "unconstrained_operator_is_constrained_operator": False,
            "compatible_source_restriction_is_ordinary_full_bundle_green_operator": False,
            "warranted_integration_claim": (
                "the exact constrained Weyl--Cotton curvature block has unique "
                "advanced/retarded compatible-source solution operators with "
                "metric-causal support"
            ),
            "flags_promoted_here": [],
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "prolonged_green_witness": False,
            "prerequisites_for_repository_flag": [
                "embed L_WC and K_src in every degree of the prolonged BV operator",
                "construct the remaining ghost, identity, antifield and contractible Green blocks",
                "assemble a degreewise block-triangular prolonged Green operator",
                "verify Q_prol commutes with those advanced/retarded operators",
            ],
            "proof_boundary": (
                "causal PDE theorem for the exact constrained curvature block; "
                "no BV witness W_prol, no QG=GQ theorem, no Lambda^+/- chain "
                "homotopy, and no compact-to-spacelike-compact quasi-isomorphism"
            ),
            "fail_closed": True,
        }
