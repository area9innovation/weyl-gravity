from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ATLAS = ROOT / "d_quotient_classical/atlas/classical-causal-atlas-fragment.json"


class ClassicalAtlasFragmentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(ATLAS.read_text())
        cls.entries = {entry["id"]: entry for entry in cls.value["entries"]}

    def test_required_backgrounds(self) -> None:
        ids = set(self.entries)
        self.assertTrue(any("vacuum_cylinder" in value for value in ids))
        self.assertTrue(any("berger" in value for value in ids))
        self.assertTrue(any("nariai" in value for value in ids))
        self.assertIn("classical.bach_flat.open_parent_detour", ids)

    def test_W_squares_are_not_particles(self) -> None:
        for name in ("plus", "minus"):
            carrier = self.entries[f"classical.vacuum_cylinder.deformation.w_{name}_squared"]["scope"]["carrier"]
            self.assertIn("not a one-particle mode", carrier)

    def test_wess_zumino_d_cartan_is_a_local_nonmode_entry(self) -> None:
        entry = self.entries[
            "classical.vacuum_cylinder.local_bv.wz_tau_adic_d_cartan"
        ]
        self.assertIn("not a mode or particle carrier", entry["scope"]["carrier"])
        self.assertEqual(entry["descriptions"]["symplectic"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["causal"], "NOT_APPLICABLE")
        self.assertEqual(entry["descriptions"]["quantum"], "OPEN")
        self.assertIn(
            "WESS_ZUMINO_D_CARTAN_CONTRACTION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "Minkowski D_M projection is explicitly not exported",
            entry["claim_boundary"],
        )

    def test_wess_zumino_causal_trace_obstruction_is_fail_closed(self) -> None:
        entry = self.entries[
            "classical.vacuum_cylinder.local_bv."
            "wz_tau_adic_causal_trace_obstruction"
        ]
        self.assertEqual(entry["descriptions"]["causal"], "OBSTRUCTED")
        self.assertEqual(entry["descriptions"]["symplectic"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["quantum"], "OPEN")
        self.assertIn("not a mode or particle carrier", entry["scope"]["carrier"])
        self.assertIn(
            "TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn("not a finite zero mode", entry["claim_boundary"])
        self.assertIn(
            "No full tau-adic Hadamard kernel", entry["claim_boundary"]
        )

    def test_complex_compensator_action_preflight_is_local_and_fail_closed(self) -> None:
        entry = self.entries[
            "classical.complex_compensator.local_bv.action_quartet_preflight"
        ]
        self.assertEqual(entry["descriptions"]["causal"], "NOT_APPLICABLE")
        self.assertEqual(entry["descriptions"]["symplectic"], "CERTIFIED")
        self.assertEqual(
            entry["descriptions"]["observational"], "NO_CERTIFIED_MAP"
        )
        self.assertEqual(entry["descriptions"]["quantum"], "OPEN")
        self.assertIn("not a mode or particle carrier", entry["scope"]["carrier"])
        self.assertIn(
            "COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "kappa_r=kappa_theta is sign-obstructed",
            entry["claim_boundary"],
        )
        self.assertIn(
            "f is introduced rather than generated",
            entry["claim_boundary"],
        )
        self.assertIn(
            "No background, causal Green, Hadamard",
            entry["claim_boundary"],
        )

    def test_changed_action_compensator_causal_parent_is_scoped(self) -> None:
        entry = self.entries[
            "classical.complex_compensator.vacuum_cylinder."
            "changed_action_causal_parent"
        ]
        self.assertEqual(entry["descriptions"]["causal"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["symplectic"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(
            entry["descriptions"]["observational"], "NO_CERTIFIED_MAP"
        )
        self.assertEqual(entry["descriptions"]["quantum"], "OPEN")
        self.assertIn(
            "not a mode or particle identification",
            entry["scope"]["carrier"],
        )
        evidence = {item["result_id"] for item in entry["evidence"]}
        self.assertIn(
            "COMPLEX_COMPENSATOR_VACUUM_CYLINDER_CAUSAL_PARENT_V1",
            evidence,
        )
        self.assertIn(
            "TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1",
            evidence,
        )
        self.assertIn("changes the classical theory", entry["claim_boundary"])
        self.assertIn(
            "not certified stable or positive", entry["claim_boundary"]
        )
        self.assertIn(
            "No residual-mode crosswalk", entry["claim_boundary"]
        )
        self.assertIn("Hadamard/Feynman state", entry["claim_boundary"])

    def test_sharp_green_transfer_crosswalk_has_no_mode_identification(self) -> None:
        theorem_id = "GREEN_HYPERBOLIC_CYCLIC_TRANSFER_THEOREM_V1"
        for chirality in ("plus", "minus"):
            entry = self.entries[
                f"classical.vacuum_cylinder.deformation.w_{chirality}_squared"
            ]
            self.assertIn(
                theorem_id,
                {item["result_id"] for item in entry["evidence"]},
            )
        nariai = self.entries[
            "classical.nariai.conformal_orbit.rank310_metric"
        ]
        self.assertIn(
            theorem_id,
            {item["result_id"] for item in nariai["evidence"]},
        )
        self.assertIn(
            "does not identify it with the conformal-cylinder modes",
            nariai["claim_boundary"],
        )

    def test_weak_background_causal_and_d_verdicts_are_separate(self) -> None:
        entry = self.entries[
            "classical.crosswalk.weak_background_causal_vs_residual_d"
        ]
        self.assertEqual(entry["descriptions"]["causal"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["symplectic"], "NO_CERTIFIED_MAP")
        self.assertIn(
            "WEAK_BACKGROUND_CAUSAL_VS_D_STABILITY_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "Causal stability and residual-D stability are separate",
            entry["claim_boundary"],
        )
        self.assertIn("Hadamard and quantum claims remain open", entry["claim_boundary"])

    def test_correction_classes_are_separate(self) -> None:
        for entry in self.entries.values():
            second = entry["mode_data"]["second_order"]
            self.assertIn("bounded_or_finite_quasiperiodic", second)
            self.assertIn("smooth_secular", second)
            self.assertIn("causal_retarded", second)

    def test_transverse_nariai_parent_is_scoped(self) -> None:
        entry = self.entries["classical.nariai.transverse_kantowski_sachs_tangent"]
        ids = {item["result_id"] for item in entry["evidence"]}
        self.assertIn("NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1", ids)
        self.assertIn("NARIAI_TRANSVERSE_FIRST_ORDER_SCHUR_SOLVE_V1", ids)
        self.assertIn("NARIAI_TRANSVERSE_PHI_ONLY_SHIFTED_CHAIN_OBSTRUCTION_V1", ids)
        self.assertIn("NARIAI_TRANSVERSE_INCIDENCE_L1_RIGIDITY_V1", ids)
        self.assertIn("NARIAI_TRANSVERSE_NORMALIZED_L0_COUPLED_OBSTRUCTION_V1", ids)
        self.assertIn("NARIAI_TRANSVERSE_K_SENSITIVITY_ADMISSIBILITY_V1", ids)
        self.assertIn("NARIAI_TRANSVERSE_PHI_SECOND_ORDER_OBSTRUCTION_V1", ids)
        self.assertIn("NARIAI_TRANSVERSE_LINEARIZED_PBW_ASSOCIATIVITY_GATE_V1", ids)
        self.assertIn("NARIAI_TRANSVERSE_ASSOCIATIVE_MIDDLE_SHIFTED_CHAIN_REPLAY_V1", ids)
        self.assertIn("NARIAI_TRANSVERSE_FACTORIZED_HOM_SCHUR_REPLAY_V1", ids)
        self.assertIn("NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_V1", ids)
        self.assertIn("NARIAI_TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION_V1", ids)
        self.assertEqual(entry["descriptions"]["causal"], "CERTIFIED")
        self.assertIn("factorized adjunction before PBW normal ordering", entry["claim_boundary"])
        self.assertIn("upper relative-saddle chain closes", entry["claim_boundary"])
        self.assertIn("unique 15-term algebraic cyclic completion", entry["claim_boundary"])
        self.assertIn("direct action-leading coefficients plus Noether uniqueness", entry["claim_boundary"])
        self.assertIn("all twenty-one differentiated ten-block SDR identities vanish", entry["claim_boundary"])
        self.assertIn(
            "tangent theorem at epsilon=0",
            entry["claim_boundary"],
        )
        self.assertIn(
            "NARIAI_TRANSVERSE_FORMAL_METRIC_GREEN_VARIATION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "NARIAI_TRANSVERSE_GLOBAL_HPL_RANK310_CAUSAL_VARIATION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )

    def test_berger_bridge_one_remains_fail_closed(self) -> None:
        entry = self.entries["classical.berger.crosswalk.retained36_to_einstein_extra"]
        self.assertEqual(set(entry["descriptions"].values()), {"NO_CERTIFIED_MAP"})
        self.assertIn("Bridge 1 is not activated", entry["claim_boundary"])
        self.assertIn("relative cofiber", entry["claim_boundary"])
        self.assertIn(
            "BERGER_BRIDGE1_ADMISSIBLE_CARRIER_DISPOSITION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )

    def test_berger_frozen_cauchy_graph_is_obstructed_not_quantized(self) -> None:
        entry = self.entries[
            "classical.berger.crosswalk.retained26_to_frozen104_cauchy_bv"
        ]
        self.assertEqual(entry["descriptions"]["causal"], "OBSTRUCTED")
        self.assertEqual(entry["descriptions"]["quantum"], "NO_CERTIFIED_MAP")
        self.assertIn("at least 104 added rows", entry["claim_boundary"])
        self.assertIn(
            "doubled-cone strictification is nilpotent",
            entry["claim_boundary"],
        )
        self.assertIn("208 added, 312 total", entry["claim_boundary"])
        self.assertIn(
            "cone cohomology (13,57,57,13)",
            entry["claim_boundary"],
        )
        self.assertIn(
            "retained q26 cohomology (1,1,1,1)",
            entry["claim_boundary"],
        )
        self.assertIn("ranks (23,56,23)", entry["claim_boundary"])
        self.assertIn(
            "not a PBW operator extension",
            entry["claim_boundary"],
        )
        self.assertIn(
            "every non-cone 104-row factorization",
            entry["claim_boundary"],
        )
        self.assertIn("Changed companions", entry["claim_boundary"])
        self.assertIn(
            "BERGER_Q26_CAUCHY_BV_CARRIER_OBSTRUCTION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "BERGER_Q26_MINIMAL_SIX_ROW_CYCLIC_OBSTRUCTION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "BERGER_Q26_FINITE_ROW_MODULE_CLOSURE_LOWER_BOUND_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "BERGER_Q26_104_ROW_CANONICAL_CONE_LIFT_OBSTRUCTION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "BERGER_Q26_104_ROW_CONE_NEXT_DEFECT_MODULE_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "BERGER_Q26_104_ROW_FULLY_MIXED_CONE_SDR_OBSTRUCTION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "BERGER_Q26_104_ROW_NONCONE_RATIONAL_NILPOTENCE_FEASIBILITY_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "BERGER_Q26_104_ROW_NONCONE_EVOLUTION_EXTENSION_OBSTRUCTION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )

    def test_berger_bikernel_support_gate_is_fail_closed(self) -> None:
        entry = self.entries[
            "classical.berger.retained_gravity_clock_maxwell"
        ]
        self.assertIn(
            "BERGER_26_ROW_SMOOTH_BIKERNEL_HOMOTOPY_SUPPORT_GATE_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "cutoff-escape continuity obstruction",
            entry["claim_boundary"],
        )
        self.assertIn(
            "no one-sided support profile",
            entry["claim_boundary"],
        )
        self.assertEqual(entry["descriptions"]["quantum"], "OPEN")

    def test_nariai_incidence_cylinder_is_not_the_metric_bridge(self) -> None:
        entry = self.entries["classical.nariai.crosswalk.normal_tractor_cylinder_to_metric"]
        self.assertEqual(set(entry["descriptions"].values()), {"NO_CERTIFIED_MAP"})
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "OBSTRUCTED")
        self.assertIn("rank-310", entry["claim_boundary"])
        self.assertIn(
            "NARIAI_CURVATURE_METRIC_BRIDGE_DISPOSITION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )

    def test_bach_flat_class_has_metric_and_rank310_causal_transfer(self) -> None:
        entry = self.entries["classical.bach_flat.open_parent_detour"]
        self.assertEqual(entry["descriptions"]["causal"], "CERTIFIED")
        ids = {item["result_id"] for item in entry["evidence"]}
        self.assertIn("BACH_FLAT_RANK310_NATURAL_SDR_V1", ids)
        self.assertIn("BACH_FLAT_METRIC_BIWAVE_GREEN_HOMOTOPY_V1", ids)
        self.assertIn("BACH_FLAT_RANK310_CAUSAL_TRANSFER_V1", ids)
        self.assertIn("pure normal-tractor-parent-to-metric crosswalk remains fail-closed", entry["claim_boundary"])

    def test_candidate13_reduced_source_is_not_promoted_to_local_bv(self) -> None:
        entry = self.entries["classical.crosswalk.candidate13_reduced_source_to_local_bv"]
        self.assertEqual(entry["descriptions"]["causal"], "NO_CERTIFIED_MAP")
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["second_order"]["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("new local equation-level cofiber", entry["claim_boundary"])
        self.assertIn(
            "CANDIDATE13_REDUCED_SOURCE_SUPPORT_LOCAL_UPGRADE_OBSTRUCTION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )

    def test_five_current_de_rham_carrier_has_scoped_q2_only(self) -> None:
        entry = self.entries["classical.crosswalk.compact_product_five_current_de_rham_carrier"]
        self.assertEqual(entry["descriptions"]["symplectic"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["causal"], "NO_CERTIFIED_MAP")
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertIn("full 238-row relative mapping-cofiber morphism remains open", entry["mode_data"]["taub_maps"]["statement"])
        self.assertIn("eighteen spectral resonance", entry["claim_boundary"])
        self.assertIn(
            "EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_CARRIER_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_Q2_V1",
            {item["result_id"] for item in entry["evidence"]},
        )

    def test_fixed_238_row_cyclic_completion_is_rank_obstructed(self) -> None:
        entry = self.entries["classical.crosswalk.compact_product_relative_238_cyclic_completion"]
        self.assertEqual(entry["descriptions"]["symplectic"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "OBSTRUCTED")
        self.assertEqual(entry["descriptions"]["causal"], "NO_CERTIFIED_MAP")
        self.assertIn("at least 28 rows", entry["claim_boundary"])
        self.assertIn("necessary rather than sufficient", entry["claim_boundary"])
        self.assertIn("larger mixed-bundle cyclic carriers remain open", entry["claim_boundary"])
        self.assertIn(
            "EINSTEIN_WEYL_RELATIVE_238_ROW_CYCLIC_RANK_OBSTRUCTION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )

    def test_316_row_cotangent_carrier_is_unary_only(self) -> None:
        entry = self.entries["classical.crosswalk.compact_product_relative_316_cotangent_carrier"]
        self.assertEqual(entry["descriptions"]["symplectic"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertEqual(entry["descriptions"]["causal"], "NO_CERTIFIED_MAP")
        self.assertIn("not either standard action-derived form", entry["claim_boundary"])
        self.assertIn("full-domain q2 is obstructed", entry["claim_boundary"])
        self.assertIn("derived Taub-zero homotopy pullback", entry["claim_boundary"])
        self.assertIn(
            "EINSTEIN_WEYL_RELATIVE_316_ROW_COTANGENT_COMPLETION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "EINSTEIN_WEYL_RELATIVE_316_BLOCK_DIAGONAL_Q2_OBSTRUCTION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )

    def test_derived_taub_zero_pullback_is_quadratic_and_open(self) -> None:
        entry = self.entries["classical.crosswalk.compact_product_derived_taub_zero_pullback"]
        self.assertEqual(entry["descriptions"]["causal"], "NO_CERTIFIED_MAP")
        self.assertEqual(entry["descriptions"]["symplectic"], "OPEN")
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertIn("does not restrict the unary tangent complex", entry["claim_boundary"])
        self.assertIn(
            "EINSTEIN_WEYL_RELATIVE_DERIVED_TAUB_ZERO_PULLBACK_PREFLIGHT_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertEqual(entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(entry["mode_data"]["second_order"]["smooth_secular"]["status"], "CERTIFIED")
        self.assertIn("not a serialized all-mode PBW matrix", entry["claim_boundary"])
        self.assertIn(
            "EINSTEIN_WEYL_RELATIVE_REDUCED_TAUB_FACTORIZATION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "EINSTEIN_WEYL_RELATIVE_SHIFTED_CURRENT_CONE_PREFLIGHT_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn("degree-zero chain map A:K_P->C_W", entry["claim_boundary"])
        self.assertIn("not the existing block-diagonal 316 profile", entry["claim_boundary"])
        self.assertIn(
            "EINSTEIN_WEYL_RELATIVE_FULL_FIVE_CURRENT_PBW_EXPORT_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn("30,494 canonical terms", entry["claim_boundary"])
        self.assertIn("V1 current table", entry["claim_boundary"])
        self.assertIn(
            "EINSTEIN_WEYL_RELATIVE_ORDER_ZERO_LIFT_OBSTRUCTION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn("rank 305", entry["claim_boundary"])
        self.assertIn("Order two", entry["claim_boundary"])
        self.assertIn(
            "EINSTEIN_WEYL_RELATIVE_ENDPOINT_NORMALIZATION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn("A2(P_X^4)=X^mu c_mu_star", entry["claim_boundary"])
        self.assertIn(
            "EINSTEIN_WEYL_RELATIVE_ORDER_ONE_INVARIANT_ANSATZ_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn("406 unknowns", entry["claim_boundary"])
        self.assertIn("complete through coefficient-jet order two", entry["claim_boundary"])
        self.assertIn(
            "EINSTEIN_WEYL_RELATIVE_HESSIAN_SECOND_CURRENT_INPUT_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "EINSTEIN_WEYL_RELATIVE_FULL_FIVE_CURRENT_SECOND_JET_EXPORT_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn("36,539 canonical terms", entry["claim_boundary"])
        self.assertIn("twenty independently hashed chunks", entry["claim_boundary"])
        self.assertIn(
            "EINSTEIN_WEYL_RELATIVE_ORDER_ONE_CHAIN_OBSTRUCTION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn("rank 398 and augmented rank 399", entry["claim_boundary"])
        self.assertIn("before f2 can be tested", entry["claim_boundary"])
        self.assertIn(
            "EINSTEIN_WEYL_RELATIVE_ORDER_TWO_OBSTRUCTION_SENSITIVITY_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "626-dimensional invariant A1 order-two symbol space",
            entry["claim_boundary"],
        )
        self.assertIn(
            "sensitivity has rank one and is surjective",
            entry["claim_boundary"],
        )
        self.assertIn(
            "EINSTEIN_WEYL_RELATIVE_ORDER_TWO_TOP_DESCENT_OBSTRUCTION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn("1056-by-712 matrix", entry["claim_boundary"])
        self.assertIn("kernel dimension 196", entry["claim_boundary"])
        self.assertIn("four-row exact rowspace witness", entry["claim_boundary"])
        self.assertIn(
            "complete endpoint-normalized chain map is obstructed through order two",
            entry["claim_boundary"],
        )
        self.assertIn(
            "EINSTEIN_WEYL_RELATIVE_ORDER_THREE_DESCENT_OBSTRUCTION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn("all 5,600 raw cubic A1 coefficients", entry["claim_boundary"])
        self.assertIn(
            "complete endpoint-normalized chain map is obstructed through order three",
            entry["claim_boundary"],
        )
        self.assertIn(
            "EINSTEIN_WEYL_RELATIVE_ALL_ORDER_ENDPOINT_PAIRING_OBSTRUCTION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "EINSTEIN_WEYL_RELATIVE_COMPENSATED_ENDPOINT_CHAIN_OBSTRUCTION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "fixed diffeomorphism-only endpoint is obstructed at every finite differential order",
            entry["claim_boundary"],
        )
        self.assertIn("corrected endpoint A2_comp", entry["claim_boundary"])
        self.assertIn(
            "rank 3 and augmented rank 4",
            entry["claim_boundary"],
        )
        self.assertIn(
            "xi has nonzero normal form modulo (tau,xi^2)",
            entry["claim_boundary"],
        )
        self.assertIn(
            "minimal GL(4)-covariant tensor-symbol repair adjoins Lambda^2(T^*M)",
            entry["claim_boundary"],
        )
        self.assertIn(
            "full chain map are absent",
            entry["claim_boundary"],
        )
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "OBSTRUCTED")

    def test_transverse_exact_einstein_branch_is_slabwise_only(self) -> None:
        entry = self.entries["classical.nariai.transverse_kantowski_sachs_exact_branch"]
        self.assertEqual(entry["descriptions"]["causal"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["second_order"]["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("not a no-go for other non-Einstein Bach-flat", entry["claim_boundary"])
        self.assertIn(
            "NARIAI_TRANSVERSE_KANTOWSKI_SACHS_GLOBAL_OBSTRUCTION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "NARIAI_KS_FOUR_BLOCK_INCIDENCE_OBSTRUCTION_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "NARIAI_RANK310_SIX_BLOCK_FINITE_HPL_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "NARIAI_KS_COMMON_SLAB_CAUSAL_DOMAIN_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "EINSTEIN_METRIC_BIWAVE_GREEN_HOMOTOPY_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn(
            "NARIAI_KS_RANK310_COMMON_SLAB_GREEN_TRANSFER_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn("two forced quadratic metric cross terms", entry["claim_boundary"])
        self.assertIn("complete four-row metric endpoint", entry["claim_boundary"])
        self.assertIn("exact rank-310 advanced/retarded homotopies", entry["claim_boundary"])
        self.assertIn("not a whole-cylinder theorem", entry["claim_boundary"])

    def test_transverse_finite_hpl_is_evidence_not_geometric_promotion(self) -> None:
        entry = self.entries["classical.nariai.transverse_kantowski_sachs_tangent"]
        self.assertIn(
            "NARIAI_RANK310_FINITE_HPL_INCIDENCE_THEOREM_V1",
            {item["result_id"] for item in entry["evidence"]},
        )
        self.assertIn("nonlocal-denominator", entry["claim_boundary"])
        self.assertIn("separate exact-branch atlas row", entry["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
