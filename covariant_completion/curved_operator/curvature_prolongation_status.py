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

from covariant_completion.green_homotopy.causal_transport import (
    SCHEMA as CAUSAL_TRANSPORT_SCHEMA,
    recognition_certificate_passes,
)
from covariant_completion.final_transport.equivariant_transport import (
    SCHEMA as SO42_TRANSPORT_SCHEMA,
    recognition_certificate_passes as so42_recognition_certificate_passes,
)

from .mixed_order_green_promotion import coefficient_certificate_passes
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
    mixed_order_promotion_theorem_exact: bool = False
    mixed_order_factorization_exact: bool = False
    causal_transport_recognition_exact: bool = False
    SO42_transport_recognition_exact: bool = False

    @staticmethod
    def build(
        quotient: CurvedNullSymbolQuotient | None = None,
        phase1_certificate: Mapping[str, object] | None = None,
        eal_certificate: Mapping[str, object] | None = None,
        hyperbolic_certificate: Mapping[str, object] | None = None,
        differential_ideal_certificate: Mapping[str, object] | None = None,
        formal_integrability_certificate: Mapping[str, object] | None = None,
        mapping_cylinder_certificate: Mapping[str, object] | None = None,
        prolonged_current_certificate: Mapping[str, object] | None = None,
        mixed_order_promotion_certificate: Mapping[str, object] | None = None,
        mixed_order_factorization_certificate: Mapping[str, object] | None = None,
        causal_transport_recognition_certificate: Mapping[str, object] | None = None,
        SO42_transport_recognition_certificate: Mapping[str, object] | None = None,
    ) -> "CurvatureProlongationStatus":
        formal_promotion_exact = False
        coefficient_exact = False
        transport_recognition_exact = False
        so42_recognition_exact = False
        phase1_flags = {
            "curved_EB_equations": False,
            "curved_EB_first_order_closure": False,
            "EAL_curvature_spectrum_match": False,
            "curved_EB_symmetric_hyperbolicity": False,
            "curved_sourced_constraint_identity": False,
            "curved_constraint_propagation": False,
            "support_local_prolongation_retract": False,
            "prolonged_BV_operator_identity": False,
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "causal_quasi_isomorphism": False,
            "residual_endpoint_recovery": False,
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
        if prolonged_current_certificate is not None:
            if prolonged_current_certificate.get("schema") != (
                "pure-weyl-prolonged-current-comparison-v1"
            ):
                raise AssertionError("wrong prolonged current comparison schema")
            exact = prolonged_current_certificate.get(
                "exact_matrix_identities", {}
            )
            transgression = prolonged_current_certificate.get(
                "variational_transgression", {}
            )
            rows = prolonged_current_certificate.get("all_row_ledger", {})
            support = prolonged_current_certificate.get("support", {})
            warranted = prolonged_current_certificate.get(
                "warranted_atomic_flags"
            )
            current_exact = all(
                (
                    isinstance(exact, Mapping),
                    exact.get("Isharp_Hprol_I_minus_Haux") == "zero",
                    exact.get("Qprol_squared") == "zero",
                    exact.get("Qprol_odd_cyclicity_defect") == "zero",
                    exact.get("canonical_master_action_congruence_defect")
                    == "zero",
                    isinstance(transgression, Mapping),
                    bool(transgression.get("off_shell")),
                    transgression.get("compatible_current_identity")
                    == "I^*omega_prol^comp-omega_aux=0",
                    isinstance(rows, Mapping),
                    int(rows.get("mapping_cylinder_blocks", -1)) == 16,
                    bool(rows.get("degree_ledger_complete")),
                    bool(rows.get("fields_and_curvature_fields")),
                    bool(rows.get("equation_and_identity_rows")),
                    bool(rows.get("antifield_and_identity_antifield_rows")),
                    bool(rows.get("trace_Weyl_and_nonminimal_rows")),
                    int(rows.get("silent_rows_dropped", -1)) == 0,
                    isinstance(support, Mapping),
                    bool(support.get("finite_differential_orders_only")),
                    support.get("inverse_Laplacian") is False,
                    support.get("inverse_curl") is False,
                    support.get("spectral_projector") is False,
                    support.get("Green_operator") is False,
                    prolonged_current_certificate.get(
                        "prolonged_current_comparison"
                    ) is True,
                    warranted == ["prolonged_current_comparison"],
                    phase1_flags.get(
                        "support_local_prolongation_retract", False
                    ),
                    phase1_flags.get("prolonged_BV_operator_identity", False),
                )
            )
            phase1_flags["prolonged_current_comparison"] = current_exact
        if (
            mixed_order_factorization_certificate is not None
            and mixed_order_promotion_certificate is None
        ):
            raise AssertionError(
                "mixed-order factorization cannot promote without the promotion theorem"
            )
        if mixed_order_promotion_certificate is not None:
            if mixed_order_promotion_certificate.get("schema") != (
                "pure-weyl-mixed-order-green-promotion-v1"
            ):
                raise AssertionError("wrong mixed-order Green promotion schema")
            formal = mixed_order_promotion_certificate.get(
                "exact_formal_construction", {}
            )
            causal = mixed_order_promotion_certificate.get("causal_support", {})
            adjoint = mixed_order_promotion_certificate.get(
                "formal_adjoint_handling", {}
            )
            insertion = mixed_order_promotion_certificate.get(
                "sixteen_block_insertion", {}
            )
            homological = mixed_order_promotion_certificate.get(
                "homological_consequence_if_coefficients_pass", {}
            )
            formal_promotion_exact = all(
                (
                    isinstance(formal, Mapping),
                    int(formal.get("right_inverse_defect", -1)) == 0,
                    int(formal.get("left_inverse_defect", -1)) == 0,
                    int(formal.get("formula_equality_defect", -1)) == 0,
                    bool(formal.get("two_sided")),
                    isinstance(causal, Mapping),
                    bool(causal.get("same_sided_factor_composition")),
                    bool(causal.get("D_does_not_enlarge_support")),
                    causal.get("retarded_intermediate_domains")
                    == "past-compact extensions",
                    causal.get("advanced_intermediate_domains")
                    == "future-compact extensions",
                    isinstance(adjoint, Mapping),
                    bool(adjoint.get("operator_order_reversal_checked")),
                    adjoint.get("mixed_block_rule")
                    == "(G_P_plus)^sharp=G_Psharp_minus",
                    isinstance(insertion, Mapping),
                    int(insertion.get("existing_green_blocks", -1)) == 14,
                    insertion.get("replaced_open_blocks")
                    == ["M_aux P", "Ebar_aux Psharp"],
                    bool(
                        insertion.get(
                            "conditional_all_16_blocks_two_sided_and_causal"
                        )
                    ),
                    bool(insertion.get("S_and_Sinverse_support_local")),
                    isinstance(homological, Mapping),
                    bool(homological.get("QG_equals_GQ")),
                    homological.get("Q_Lambda_plus_Lambda_Q") == "identity",
                )
            )
            coefficient_exact = (
                mixed_order_factorization_certificate is not None
                and coefficient_certificate_passes(
                    mixed_order_factorization_certificate
                )
            )
            green_prerequisites = all(
                (
                    phase1_flags["curved_EB_symmetric_hyperbolicity"],
                    phase1_flags["curved_sourced_constraint_identity"],
                    phase1_flags["curved_constraint_propagation"],
                    phase1_flags.get("support_local_prolongation_retract", False),
                    phase1_flags.get("prolonged_BV_operator_identity", False),
                )
            )
            green_exact = bool(
                formal_promotion_exact
                and coefficient_exact
                and green_prerequisites
            )
            phase1_flags["prolonged_green_witness"] = green_exact
            phase1_flags["curvature_causal_green_operators"] = green_exact
            phase1_flags["causal_green_homotopy"] = green_exact
        if causal_transport_recognition_certificate is not None:
            if causal_transport_recognition_certificate.get("schema") != (
                CAUSAL_TRANSPORT_SCHEMA
            ):
                raise AssertionError("wrong causal transport recognition schema")
            transport_recognition_exact = recognition_certificate_passes(
                causal_transport_recognition_certificate
            )
        transport_prerequisites = all(
            (
                phase1_flags.get("prolonged_green_witness", False),
                phase1_flags.get("curvature_causal_green_operators", False),
                phase1_flags.get("causal_green_homotopy", False),
                phase1_flags.get("support_local_prolongation_retract", False),
                phase1_flags.get("prolonged_BV_operator_identity", False),
            )
        )
        phase1_flags["causal_quasi_isomorphism"] = bool(
            transport_recognition_exact and transport_prerequisites
        )
        phase1_flags["residual_endpoint_recovery"] = bool(
            transport_recognition_exact
            and transport_prerequisites
            and phase1_flags["causal_quasi_isomorphism"]
        )
        if SO42_transport_recognition_certificate is not None:
            if SO42_transport_recognition_certificate.get("schema") != (
                SO42_TRANSPORT_SCHEMA
            ):
                raise AssertionError("wrong SO(4,2) transport recognition schema")
            so42_recognition_exact = so42_recognition_certificate_passes(
                SO42_transport_recognition_certificate
            )
        phase1_flags["SO42_equivariant_transport"] = bool(
            so42_recognition_exact
            and phase1_flags["causal_quasi_isomorphism"]
            and phase1_flags["residual_endpoint_recovery"]
            and phase1_flags["EAL_curvature_spectrum_match"]
            and phase1_flags["support_local_prolongation_retract"]
        )
        phase1_flags["mixed_order_promotion_theorem_exact"] = bool(
            formal_promotion_exact
        )
        phase1_flags["mixed_order_factorization_exact"] = bool(coefficient_exact)
        phase1_flags["causal_transport_recognition_exact"] = bool(
            transport_recognition_exact
        )
        phase1_flags["SO42_transport_recognition_exact"] = bool(
            so42_recognition_exact
        )
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
        if (
            self.mixed_order_factorization_exact
            and not self.mixed_order_promotion_theorem_exact
        ):
            raise AssertionError(
                "mixed-order coefficients accepted without the promotion theorem"
            )
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
        self._require(
            "causal_quasi_isomorphism",
            "prolonged_green_witness",
            "curvature_causal_green_operators",
            "causal_green_homotopy",
            "causal_transport_recognition_exact",
        )
        self._require(
            "residual_endpoint_recovery",
            "causal_quasi_isomorphism",
            "support_local_prolongation_retract",
            "causal_transport_recognition_exact",
        )
        self._require(
            "SO42_equivariant_transport",
            "causal_quasi_isomorphism",
            "residual_endpoint_recovery",
            "EAL_curvature_spectrum_match",
            "support_local_prolongation_retract",
            "SO42_transport_recognition_exact",
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
            "fixed_temporal_16_diagnostic_flags": {
                "fixed_temporal_16_family_complete": True,
                "intrinsic_sensitivity_matrix_zero": True,
                "parameter_uniform_Jordan_chain": True,
                "strong_hyperbolicity_in_16_family": False,
                "symmetric_hyperbolicity_in_16_family": False,
                "fixed_temporal_16_no_go": True,
                "aligned_physical_biwave_recursive_formula_exact": True,
                "aligned_physical_Jordan_extension_causal": True,
                "physical_biwave_block_green_hyperbolic": True,
                "physical_Jordan_extension_causal": True,
                "physical_green_flag_scope": (
                    "exact restricted TT plus shifted-auxiliary operator subcomplex"
                ),
                "alternative_17_27_intrinsic_sensitivity_nonzero": True,
                "alternative_17_27_minimal_regular_slices_semisimple": False,
                "alternative_17_27_full_family_no_go": False,
                "alternative_minimal_sensitivity_family_complete": True,
                "alternative_minimal_family_zero_root_no_go": True,
                "rank34_presented_rank12_submodule_green": True,
                "rank34_rank8_constraint_quotient_hyperbolic": True,
                "rank34_rank14_field_cokernel_green": False,
                "shifted_rank4_vector_block_contractible": True,
                "shifted_rank4_vector_replacement_Green_inverse": True,
                "shifted_rank4_vector_Green_homotopy": True,
                "all_row_Green_assembly_conditional_on_rank14": True,
                "rank14_Weyl_Cotton_input_manifest_complete": True,
                "rank14_principal_projector_free_presentation": True,
                "rank14_principal_green_algebra": True,
                "direct_rank14_curvature_retraction_no_go": True,
                "rank14_equation_SDR_required": True,
                "rank14_raw_curvature_image_rank": 5,
                "rank14_raw_curvature_kernel_rank": 9,
                "rank14_compatible_source_kernel_rank": 12,
                "rank14_raw_curvature_image_is_source_compatible": False,
                "rank14_generic_curvature_compatibility_defect_rank": 3,
                "rank14_fake_V7_quotient_defined": False,
                "rank14_equation_cone_exact": True,
                "rank14_null_B3_H2_quotient_distinguished_from_constraint_kernel": True,
                "rank14_witness_companion_cycle_gate_exact": True,
                "rank14_fake_state_SDR_rejected": True,
                "rank14_full_equation_cone_required": True,
                "rank14_ordinary_BV_Caux_layer_identified": True,
                "rank14_curved_Caux_Rees_layer_unresolved": True,
                "rank14_mixed_symbol_cone_rejected": True,
                "rank14_common_Douglis_filtration_required": True,
                "rank14_common_Douglis_weight_constraints_feasible": True,
                "rank14_full_symbol_cone_is_complex": False,
                "rank14_full_symbol_cone_cohomology_computed": False,
                "rank14_equation_SDR_constructed": False,
                "rank14_green_operators_constructed": False,
                "rank14_typed_incoming_map_ledger_complete": True,
                "rank14_plain_state_kernel_quotient_is_target": False,
                "rank14_principal_H7_contraction_certified": False,
                "rank14_corrected_equation_source_map_typed": True,
                "rank14_lower_order_PBW_may_resume": False,
            },
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
            "prolonged_current_evidence": {
                "certificate": "curved_prolonged_current_comparison.json",
                "all_row_cyclic_quadratic_parent": (
                    self.prolonged_current_comparison
                ),
                "off_shell_d_plus_Q_comparison": (
                    self.prolonged_current_comparison
                ),
                "Green_current_equality_is_separate": True,
            },
            "mixed_order_green_evidence": {
                "promotion_certificate": "curved_mixed_order_green_promotion.json",
                "general_system_certificate": (
                    "curved_general_nonlinear_factor_system.json"
                ),
                "adjoint_reduction_certificate": "general_adjoint_factor.json",
                "sharp_order_two_certificate": (
                    "curved_general_nonlinear_factor_sharp_order2.json"
                ),
                "sharp_order_two_reduction_certificate": (
                    "curved_general_nonlinear_factor_sharp_order2_reduction.json"
                ),
                "sharp_degree_one_macaulay_screen_certificate": (
                    "curved_general_nonlinear_factor_sharp_macaulay_screen.json"
                ),
                "repaired_channel_certificate": (
                    "quadratic_obstruction_channel.json"
                ),
                "fixed_repair_no_go_certificate": (
                    "quadratic_obstruction_channel_fixed_branch.json"
                ),
                "expanded_relative_certificate": (
                    "curved_expanded_relative_witness.json"
                ),
                "expanded_relative_commutant_certificate": (
                    "curved_expanded_relative_witness_commutant.json"
                ),
                "expanded_scalar_completion_certificate": (
                    "curved_expanded_relative_witness_scalar_completion.json"
                ),
                "expanded_temporal_douglis_certificate": (
                    "curved_expanded_relative_witness_douglis.json"
                ),
                "expanded_adjoint_sign_audit_certificate": (
                    "curved_expanded_relative_witness_adjoint_sign.json"
                ),
                "fixed_temporal_16_family_certificate": (
                    "curved_expanded_relative_witness_r6_family.json"
                ),
                "fixed_temporal_16_no_go_certificate": (
                    "curved_expanded_relative_witness_r6_first_order_no_go.json"
                ),
                "fixed_temporal_16_triangular_audit_certificate": (
                    "curved_expanded_relative_witness_triangular_green_audit.json"
                ),
                "fixed_temporal_16_jordan_homology_certificate": (
                    "curved_expanded_relative_witness_jordan_homology.json"
                ),
                "fixed_temporal_16_jordan_triangular_certificate": (
                    "curved_expanded_relative_witness_jordan_triangular.json"
                ),
                "shifted_physical_green_filtration_certificate": (
                    "curved_expanded_relative_witness_shifted_green_filtration.json"
                ),
                "rank34_differential_module_certificate": (
                    "curved_expanded_relative_witness_rank34_module.json"
                ),
                "shifted_rank4_vector_certificate": (
                    "curved_expanded_relative_witness_vector_contraction.json"
                ),
                "all_row_conditional_assembly_certificate": (
                    "curved_expanded_relative_witness_all_row_assembly.json"
                ),
                "rank14_Weyl_Cotton_input_manifest": (
                    "curved_rank14_weyl_cotton_input_manifest.json"
                ),
                "rank14_principal_curvature_presentation_certificate": (
                    "curved_expanded_relative_witness_rank14_curvature_presentation.json"
                ),
                "rank14_Weyl_Cotton_symbol_audit_certificate": (
                    "curved_rank14_weyl_cotton_symbol_audit.json"
                ),
                "rank14_equation_cycle_gate_certificate": (
                    "curved_rank14_equation_cycle_gate.json"
                ),
                "rank14_equation_SDR_boundary_certificate": (
                    "curved_rank14_equation_sdr_boundary.json"
                ),
                "rank14_full_cone_symbol_gate_certificate": (
                    "curved_rank14_full_cone_symbol_gate.json"
                ),
                "rank14_typed_incoming_map_ledger_certificate": (
                    "curved_rank14_weyl_cotton_incoming_map_ledger.json"
                ),
                "alternative_incidence_screen_certificate": (
                    "curved_expanded_relative_witness_incidence_screen.json"
                ),
                "alternative_semisimplicity_certificate": (
                    "curved_expanded_relative_witness_alternative_semisimplicity.json"
                ),
                "alternative_sensitivity_family_no_go_certificate": (
                    "curved_expanded_relative_witness_alternative_family_no_go.json"
                ),
                "factorization_certificate": (
                    "pure-weyl-mixed-order-factorization-v1 (not currently emitted)"
                ),
                "promotion_theorem_exact": (
                    self.mixed_order_promotion_theorem_exact
                ),
                "actual_factorization_exact": (
                    self.mixed_order_factorization_exact
                ),
                "three_flags_promote_together_only": True,
                "promoted": self.prolonged_green_witness,
            },
            "causal_transport_evidence": {
                "certificate": "curved_causal_transport_recognition.json",
                "conditional_recognition_exact": (
                    self.causal_transport_recognition_exact
                ),
                "requires_three_actual_Green_flags": True,
                "causal_quasi_isomorphism_promoted": (
                    self.causal_quasi_isomorphism
                ),
                "residual_endpoint_recovery_promoted": (
                    self.residual_endpoint_recovery
                ),
                "SO42_equivariant_transport_not_inferred": True,
                "prolonged_current_comparison_independent_of_Green": True,
            },
            "SO42_transport_evidence": {
                "certificate": "curved_SO42_causal_transport_recognition.json",
                "conditional_recognition_exact": (
                    self.SO42_transport_recognition_exact
                ),
                "cutoff_inverse_homotopy": "[kappa,rho]=[Q,[chi,rho]]",
                "requires_causal_quasi_isomorphism": True,
                "promoted": self.SO42_equivariant_transport,
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
                "extract every coefficient in the certified common Douglis/Rees "
                "filtration, especially lower A and weighted zeroth Weyl--Cotton "
                "blocks; verify all associated-graded cone squares before computing "
                "its causal-stratum cohomology or any Green homotopy"
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
