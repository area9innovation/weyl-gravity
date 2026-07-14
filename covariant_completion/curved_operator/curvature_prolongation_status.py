"""Fail-closed status for the curvature-prolonged causal BV theorem.

The exact null-symbol calculation identifies the physical helicity-two
quotient and proves that the reduced linearized-Weyl symbol is an
isomorphism.  It does *not* derive the curved Bianchi--Bach evolution or any
of the causal/homological statements below.  Each remaining theorem is kept
as an independent atomic flag so that principal-symbol evidence cannot
promote a full covariant claim.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Mapping

from .null_symbol_quotient import CurvedNullSymbolQuotient


OPEN_OBLIGATION_FIELDS = (
    "curved_EB_equations",
    "curved_EB_first_order_closure",
    "curved_EB_symmetric_hyperbolicity",
    "curved_sourced_constraint_identity",
    "curved_constraint_propagation",
    "EAL_curvature_spectrum_match",
    "support_local_prolongation_retract",
    "prolonged_BV_operator_identity",
    "prolonged_green_witness",
    "curvature_causal_green_operators",
    "causal_green_homotopy",
    "causal_quasi_isomorphism",
    "residual_endpoint_recovery",
    "SO42_equivariant_transport",
    "prolonged_current_comparison",
)


@dataclass(frozen=True)
class CurvatureProlongationStatus:
    quotient: CurvedNullSymbolQuotient
    curved_EB_equations: bool = False
    curved_EB_first_order_closure: bool = False
    curved_EB_symmetric_hyperbolicity: bool = False
    curved_sourced_constraint_identity: bool = False
    curved_constraint_propagation: bool = False
    EAL_curvature_spectrum_match: bool = False
    support_local_prolongation_retract: bool = False
    prolonged_BV_operator_identity: bool = False
    prolonged_green_witness: bool = False
    curvature_causal_green_operators: bool = False
    causal_green_homotopy: bool = False
    causal_quasi_isomorphism: bool = False
    residual_endpoint_recovery: bool = False
    SO42_equivariant_transport: bool = False
    prolonged_current_comparison: bool = False

    @staticmethod
    def build(
        quotient: CurvedNullSymbolQuotient | None = None,
        phase1_certificate: Mapping[str, object] | None = None,
        eal_certificate: Mapping[str, object] | None = None,
        hyperbolic_certificate: Mapping[str, object] | None = None,
        differential_ideal_certificate: Mapping[str, object] | None = None,
        formal_integrability_certificate: Mapping[str, object] | None = None,
        mapping_cylinder_certificate: Mapping[str, object] | None = None,
    ) -> "CurvatureProlongationStatus":
        phase1_flags = {
            "curved_EB_equations": False,
            "curved_EB_first_order_closure": False,
            "EAL_curvature_spectrum_match": False,
            "curved_EB_symmetric_hyperbolicity": False,
            "curved_sourced_constraint_identity": False,
            "curved_constraint_propagation": False,
            "support_local_prolongation_retract": False,
            "prolonged_BV_operator_identity": False,
        }
        if phase1_certificate is not None:
            if phase1_certificate.get("schema") != (
                "pure-weyl-cotton-curved-jet-comparison-v1"
            ):
                raise AssertionError("wrong curved Weyl/Cotton jet certificate schema")
            defects = (
                "algebraic_weyl_defects",
                "cotton_coordinate_defects",
                "cotton_reconstruction_defects",
                "bach_coordinate_defects",
            )
            exact = bool(phase1_certificate.get("coverage_complete")) and all(
                int(phase1_certificate.get(name, -1)) == 0 for name in defects
            )
            phase1_flags = {
                "curved_EB_equations": exact
                and bool(phase1_certificate.get("curved_EB_equations")),
                "curved_EB_first_order_closure": exact
                and bool(
                    phase1_certificate.get("curved_EB_first_order_closure")
                ),
                "EAL_curvature_spectrum_match": False,
                "curved_EB_symmetric_hyperbolicity": False,
                "curved_sourced_constraint_identity": False,
                "curved_constraint_propagation": False,
            }
        if eal_certificate is not None:
            if eal_certificate.get("schema") != (
                "pure-weyl-curvature-eal-spectrum-all-level-v1"
            ):
                raise AssertionError("wrong all-level curvature E/A/L schema")
            bridge = eal_certificate.get("equation_bridge", {})
            cotton = eal_certificate.get("cotton_prolongation", {})
            exhaustion = eal_certificate.get("global_exhaustion", {})
            character = eal_certificate.get("symbolic_character", {})
            eal_exact = all(
                (
                    bool(eal_certificate.get("all_level_not_finite_cutoff")),
                    bool(eal_certificate.get("EAL_curvature_spectrum_match")),
                    bool(bridge.get("exact_26_state_covariant_equivalence")),
                    int(bridge.get("operator_defects", -1)) == 0,
                    bool(cotton.get("cotton_unique_no_duplication")),
                    bool(exhaustion.get("global_BGG_exhaustion")),
                    bool(character.get("identity_all_coefficients")),
                    int(character.get("defect", -1)) == 0,
                )
            )
            phase1_flags["EAL_curvature_spectrum_match"] = (
                eal_exact
                and phase1_flags["curved_EB_equations"]
                and phase1_flags["curved_EB_first_order_closure"]
            )
        analytic_certificates = (
            hyperbolic_certificate,
            differential_ideal_certificate,
            formal_integrability_certificate,
        )
        if any(item is not None for item in analytic_certificates):
            if any(item is None for item in analytic_certificates):
                raise AssertionError(
                    "analytic promotion requires the PDE, differential-ideal, and formal-integrability certificates"
                )
            assert hyperbolic_certificate is not None
            assert differential_ideal_certificate is not None
            assert formal_integrability_certificate is not None
            if hyperbolic_certificate.get("schema") != (
                "pure-weyl-cotton-constraint-adjusted-hyperbolic-v1"
            ):
                raise AssertionError("wrong constraint-adjusted hyperbolic schema")
            if differential_ideal_certificate.get("schema") != (
                "pure-weyl-cotton-differential-ideal-audit-v1"
            ):
                raise AssertionError("wrong Weyl--Cotton differential-ideal schema")
            if formal_integrability_certificate.get("schema") != (
                "pure-weyl-cotton-formal-integrability-v1"
            ):
                raise AssertionError("wrong Weyl--Cotton formal-integrability schema")
            exact_equivalence = all(
                (
                    bool(
                        differential_ideal_certificate.get(
                            "covariant_and_adjusted_differential_ideals_equal"
                        )
                    ),
                    bool(
                        differential_ideal_certificate.get(
                            "covariant_and_adjusted_smooth_solution_spaces_equal"
                        )
                    ),
                    bool(
                        differential_ideal_certificate.get(
                            "source_compatibility_map_available"
                        )
                    ),
                    bool(
                        differential_ideal_certificate.get(
                            "sourced_subsidiary_identity_curvature_corrected"
                        )
                    ),
                )
            )
            hyperbolic_exact = all(
                (
                    bool(hyperbolic_certificate.get("evolution_symmetrizer_positive")),
                    bool(
                        hyperbolic_certificate.get(
                            "evolution_spatial_symbols_self_adjoint"
                        )
                    ),
                    bool(hyperbolic_certificate.get("all_characteristics_causal")),
                )
            )
            formal_integrability_exact = all(
                (
                    bool(
                        formal_integrability_certificate.get(
                            "formally_integrable_differential_ideals_equivalent"
                        )
                    ),
                    bool(
                        formal_integrability_certificate.get(
                            "exact_sourced_subsidiary_operator_identity"
                        )
                    ),
                    bool(
                        formal_integrability_certificate.get(
                            "compatible_sources_preserve_all_fourteen_constraints"
                        )
                    ),
                    bool(
                        formal_integrability_certificate.get(
                            "subsidiary_characteristics_causal"
                        )
                    ),
                )
            )
            sourced_exact = bool(
                hyperbolic_certificate.get(
                    "exact_sourced_subsidiary_operator_identity"
                )
            )
            propagation_exact = all(
                (
                    bool(hyperbolic_certificate.get("homogeneous_constraints_propagate")),
                    bool(hyperbolic_certificate.get("subsidiary_symmetrizer_positive")),
                    bool(
                        hyperbolic_certificate.get(
                            "subsidiary_spatial_symbols_self_adjoint"
                        )
                    ),
                )
            )
            prerequisites = (
                phase1_flags["curved_EB_equations"]
                and phase1_flags["curved_EB_first_order_closure"]
                and exact_equivalence
                and formal_integrability_exact
            )
            phase1_flags["curved_EB_symmetric_hyperbolicity"] = (
                prerequisites and hyperbolic_exact
            )
            phase1_flags["curved_sourced_constraint_identity"] = (
                prerequisites and sourced_exact
            )
            phase1_flags["curved_constraint_propagation"] = (
                prerequisites and sourced_exact and propagation_exact
            )
        if mapping_cylinder_certificate is not None:
            if mapping_cylinder_certificate.get("schema") != (
                "pure-weyl-curvature-mapping-cylinder-substitution-v1"
            ):
                raise AssertionError("wrong curvature mapping-cylinder schema")
            substitution = mapping_cylinder_certificate.get("substitution", {})
            kernel = mapping_cylinder_certificate.get("kernel", {})
            warranted = mapping_cylinder_certificate.get("warranted_atomic_flags")
            mapping_exact = all(
                (
                    bool(
                        mapping_cylinder_certificate.get(
                            "coefficientwise_complete_prolonged_Q"
                        )
                    ),
                    bool(mapping_cylinder_certificate.get("support_local")),
                    isinstance(substitution, Mapping),
                    bool(substitution.get("all_new_blocks_accounted_for")),
                    bool(substitution.get("formal_adjoint_tables_generated_from_primal_tables")),
                    bool(substitution.get("state_gauge_relation_exact")),
                    bool(substitution.get("first_chain_relation_exact")),
                    bool(substitution.get("second_chain_relation_exact")),
                    isinstance(kernel, Mapping),
                    kernel.get("Q_squared") == "zero",
                    int(kernel.get("BV_pairing_defect", -1)) == 0,
                    int(kernel.get("odd_BV_cyclicity_defect", -1)) == 0,
                    kernel.get("P_I") == "identity",
                    kernel.get("I_P_minus_identity") == "QH+HQ",
                    warranted
                    == [
                        "support_local_prolongation_retract",
                        "prolonged_BV_operator_identity",
                    ],
                )
            )
            phase1_flags["support_local_prolongation_retract"] = mapping_exact
            phase1_flags["prolonged_BV_operator_identity"] = mapping_exact
        result = CurvatureProlongationStatus(
            quotient if quotient is not None else CurvedNullSymbolQuotient.build(),
            **phase1_flags,
        )
        result.verify()
        return result

    @property
    def weyl_symbol_helicity_isomorphism(self) -> bool:
        return (
            self.quotient.quotient_dimension == 2
            and self.quotient.weyl_target_quotient_dimension == 2
            and self.quotient.induced_weyl_matrix.det() != 0
        )

    @property
    def curvature_prolonged_complex_exact(self) -> bool:
        return all(
            (
                self.curved_EB_equations,
                self.curved_EB_first_order_closure,
                self.curved_sourced_constraint_identity,
                self.curved_constraint_propagation,
                self.EAL_curvature_spectrum_match,
                self.support_local_prolongation_retract,
                self.prolonged_BV_operator_identity,
            )
        )

    @property
    def curvature_green_realization(self) -> bool:
        return all(
            (
                self.curvature_prolonged_complex_exact,
                self.curved_EB_symmetric_hyperbolicity,
                self.prolonged_green_witness,
                self.curvature_causal_green_operators,
                self.causal_green_homotopy,
            )
        )

    def _require(self, conclusion: str, *premises: str) -> None:
        if not getattr(self, conclusion):
            return
        missing = [name for name in premises if not getattr(self, name)]
        if missing:
            raise AssertionError(
                f"{conclusion} promoted before required theorem(s): "
                + ", ".join(missing)
            )

    def verify(self) -> None:
        self.quotient.verify()
        dataclass_names = {item.name for item in fields(self)}
        missing_fields = set(OPEN_OBLIGATION_FIELDS) - dataclass_names
        if missing_fields:
            raise AssertionError(
                "curvature obligation schema is incomplete: "
                + ", ".join(sorted(missing_fields))
            )

        self._require("curved_EB_first_order_closure", "curved_EB_equations")
        self._require(
            "curved_EB_symmetric_hyperbolicity",
            "curved_EB_equations",
            "curved_EB_first_order_closure",
        )
        self._require(
            "curved_sourced_constraint_identity",
            "curved_EB_equations",
            "curved_EB_first_order_closure",
        )
        self._require(
            "curved_constraint_propagation",
            "curved_EB_equations",
            "curved_EB_first_order_closure",
            "curved_sourced_constraint_identity",
        )
        self._require(
            "EAL_curvature_spectrum_match",
            "curved_EB_equations",
            "curved_EB_first_order_closure",
        )
        self._require(
            "support_local_prolongation_retract",
            "curved_EB_equations",
            "curved_EB_first_order_closure",
        )
        self._require(
            "prolonged_BV_operator_identity",
            "curved_EB_equations",
            "support_local_prolongation_retract",
        )
        self._require(
            "prolonged_green_witness",
            "prolonged_BV_operator_identity",
            "curved_EB_symmetric_hyperbolicity",
            "curved_sourced_constraint_identity",
        )
        self._require(
            "curvature_causal_green_operators",
            "prolonged_green_witness",
            "curved_EB_symmetric_hyperbolicity",
            "curved_sourced_constraint_identity",
            "curved_constraint_propagation",
        )
        self._require(
            "causal_green_homotopy",
            "prolonged_BV_operator_identity",
            "prolonged_green_witness",
            "curvature_causal_green_operators",
        )
        self._require("causal_quasi_isomorphism", "causal_green_homotopy")
        self._require(
            "residual_endpoint_recovery",
            "causal_quasi_isomorphism",
            "support_local_prolongation_retract",
        )
        self._require(
            "SO42_equivariant_transport",
            "causal_quasi_isomorphism",
            "EAL_curvature_spectrum_match",
        )
        self._require(
            "prolonged_current_comparison",
            "support_local_prolongation_retract",
            "prolonged_BV_operator_identity",
        )

        if self.curvature_prolonged_complex_exact and not (
            self.weyl_symbol_helicity_isomorphism
        ):
            raise AssertionError(
                "curvature prolongation promoted without the exact reduced "
                "Weyl-symbol isomorphism"
            )
        if self.curvature_green_realization and not (
            self.curvature_prolonged_complex_exact
            and self.weyl_symbol_helicity_isomorphism
        ):
            raise AssertionError(
                "curvature Green realization promoted without its prolonged complex"
            )

    def certificate(self) -> dict[str, object]:
        self.verify()
        obligations = {name: getattr(self, name) for name in OPEN_OBLIGATION_FIELDS}
        return {
            "schema": "pure-weyl-curvature-prolongation-status-v2",
            "exact_symbol_reduction": {
                "domain": "(F/ker N_2)/(N_2^{-1} im K_1/ker N_2)",
                "target": "im W_2/W_2(N_2^{-1} im K_1)",
                "domain_dimension": self.quotient.quotient_dimension,
                "target_dimension": self.quotient.weyl_target_quotient_dimension,
                "induced_matrix": [
                    [str(value) for value in row]
                    for row in self.quotient.induced_weyl_matrix.tolist()
                ],
                "isomorphism": self.weyl_symbol_helicity_isomorphism,
                "full_fibre_exact_sequence_guard": (
                    "ker(W_2) is larger than im(K_1) on the un-reduced 24-field "
                    "fibre; exactness is asserted only on the displayed Hessian "
                    "reduction"
                ),
                "full_fibre_ker_W_equals_im_K_claimed": False,
            },
            "weyl_symbol_helicity_isomorphism": (
                self.weyl_symbol_helicity_isomorphism
            ),
            **obligations,
            "atomic_open_obligations": obligations,
            "phase1_evidence": {
                "certificate": "curved_weyl_cotton_jet_comparison.json",
                "exhaustive_Weyl_two_jets": 150,
                "curved_equations_and_first_order_closure_promoted_from_certificate": (
                    self.curved_EB_equations
                    and self.curved_EB_first_order_closure
                ),
            },
            "all_level_spectrum_evidence": {
                "certificate": "curved_EAL_spectrum_all_level.json",
                "symbolic_not_finite_cutoff": self.EAL_curvature_spectrum_match,
                "cotton_no_duplication": self.EAL_curvature_spectrum_match,
                "global_BGG_exhaustion": self.EAL_curvature_spectrum_match,
            },
            "analytic_closure_evidence": {
                "hyperbolic_certificate": "curved_weyl_cotton_hyperbolic.json",
                "differential_ideal_certificate": (
                    "curved_weyl_cotton_differential_ideal.json"
                ),
                "formal_integrability_certificate": (
                    "curved_weyl_cotton_formal_integrability.json"
                ),
                "pointwise_row_defect_rank": 6,
                "defect_generated_by_secondary_constraints": (
                    self.curved_EB_symmetric_hyperbolicity
                ),
                "sourced_compatibility_exact": (
                    self.curved_sourced_constraint_identity
                ),
                "homogeneous_constraint_propagation_exact": (
                    self.curved_constraint_propagation
                ),
            },
            "mapping_cylinder_evidence": {
                "certificate": (
                    "curved_curvature_mapping_cylinder_substitution.json"
                ),
                "coefficientwise_complete": (
                    self.support_local_prolongation_retract
                    and self.prolonged_BV_operator_identity
                ),
                "support_local_prolongation_retract_promoted": (
                    self.support_local_prolongation_retract
                ),
                "prolonged_BV_operator_identity_promoted": (
                    self.prolonged_BV_operator_identity
                ),
            },
            "curvature_prolonged_complex_exact": (
                self.curvature_prolonged_complex_exact
            ),
            "curvature_green_realization": self.curvature_green_realization,
            "proof_boundary": {
                "principal_symbol_results_are_full_curved_equations": False,
                "homogeneous_constraint_symbol_is_sourced_identity": False,
                "symmetric_hyperbolicity_is_chain_green_homotopy": False,
                "finite_harmonic_checks_are_all_level_EAL_audit": False,
                "curvature_only_potential_reconstruction_is_support_local": False,
                "positive_PDE_symmetrizer_is_action_Krein_pairing": False,
            },
            "next_exact_step": (
                "construct the coefficientwise degree-minus-one prolonged Green "
                "witness and certify its support-local triangular Green blocks"
                if self.prolonged_BV_operator_identity
                else "insert the certified curvature equations, fourteen constraint "
                "rows, and their cotangent/identity partners into the support-local "
                "graph SDR and certify the complete prolonged BV differential"
                if self.curved_constraint_propagation
                else "construct and certify the constraint-adjusted symmetric-hyperbolic "
                "26-state Weyl--Cotton evolution and its sourced subsidiary identity"
                if self.curved_EB_equations and self.curved_EB_first_order_closure
                else "derive the complete 3+1 Bianchi--Bach equations and their "
                "minimal local first-order closure before promoting any analytic "
                "or causal flag"
            ),
            "fail_closed": True,
        }
