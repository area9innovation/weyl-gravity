from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
ATLAS = ROOT / "bridge/einstein_sector/atlas/einstein-compact-product-atlas-fragment.json"


class EinsteinAtlasFragmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(ATLAS.read_text(encoding="utf-8"))
        cls.entries = {entry["id"]: entry for entry in cls.value["entries"]}

    def test_stable_identifiers_are_unique(self) -> None:
        self.assertEqual(len(self.entries), len(self.value["entries"]))

    def test_twist_exceptional_is_independence_witness(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.twist_exceptional_independence"]
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")

    def test_exceptional_difference_frequency_census_is_fail_closed(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.exceptional_ell1_k0_difference_frequency_census"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("Twenty-seven exact resultant", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(entry["mode_data"]["second_order"]["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_causal_compact_product_claims_remain_fail_closed(self) -> None:
        for entry in self.value["entries"]:
            if "crosswalk" not in entry["id"]:
                self.assertIn(entry["mode_data"]["second_order"]["causal_retarded"]["status"], {"OPEN", "NO_CERTIFIED_MAP"})

    def test_bridge_one_is_linear_and_fail_closed_downstream(self) -> None:
        entry = self.entries["einstein.ph.bridge.relative_branch_dictionary_v1"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("NONCYCLIC_THREE_FORM_LINEAR_TRIANGLE_CERTIFIED", entry["claim_boundary"])
        self.assertIn("without harmonic selection", entry["claim_boundary"])
        self.assertIn("causal Green data and q2/q3 relative compatibility remain open", entry["claim_boundary"])
        self.assertEqual(entry["descriptions"]["observational"], "NO_CERTIFIED_MAP")
        self.assertEqual(entry["descriptions"]["quantum"], "NO_CERTIFIED_MAP")

    def test_nonzero_k_exceptional_cofiber_is_registered_without_bridge_promotion(self) -> None:
        entry = self.entries["einstein.ph.wm.extra.exceptional_ell1_nonzero_k"]
        self.assertEqual(entry["mode_data"]["dispersion"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["lee_wald"]["status"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(entry["mode_data"]["second_order"]["causal_retarded"]["status"], "OPEN")

    def test_nonzero_k_constant_twist_same_shell_is_sharp_but_not_sufficient(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.nonzero_k_constant_twist_same_shell"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("exactly m_A=0", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertIn("Opposite-momentum wave-wave terms", entry["claim_boundary"])
        self.assertEqual(entry["mode_data"]["second_order"]["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_twist_aligned_phase_divisor_requires_an_independent_functional(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.twist_aligned_opposite_momentum_resonance_gate"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("dynamical adjoint coefficient remains OPEN", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_twist_aligned_ell2_fixture_is_bounded_obstructed_only(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.twist_aligned_opposite_momentum_bounded_obstruction"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("one tuned ell=2", entry["claim_boundary"])

    def test_abd_matrix_is_input_not_full_nonlinear_theorem(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.abd_times_ell2_extra"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "OPEN")
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertIn("superseded", entry["claim_boundary"])

    def test_complete_homogeneous_twist_matrix_remains_precone(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.homogeneous_twist_times_ell2_extra"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "OPEN")
        self.assertEqual(entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "OPEN")

    def test_aligned_face_has_correction_class_split(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.aligned_twist_ell2_extra_compatibility_face"]
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["second_order"]["smooth_secular"]["status"], "CERTIFIED")
        self.assertIn("all 20 C4 extra/extra bilinear generators", entry["mode_data"]["second_order"]["smooth_secular"]["statement"])
        self.assertIn("no additional off-axis branch", entry["mode_data"]["resonance"]["statement"])

    def test_finite_generic_multi_momentum_cone_is_fail_closed_by_category(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.finite_generic_all_momenta_smooth_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second_order["causal_retarded"]["status"], "OPEN")
        self.assertIn("multiple |k| fibres", second_order["smooth_secular"]["statement"])
        self.assertIn("Exceptional/global input modes", entry["claim_boundary"])

    def test_complete_finite_harmonic_cone_includes_exceptional_global_inputs(self) -> None:
        entry = self.entries["einstein.ph.wm.complete_finite_harmonic_smooth_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("complete certified linear inventory", second_order["smooth_secular"]["statement"])
        self.assertIn("P_(j,r)", entry["mode_data"]["resonance"]["statement"])

    def test_standard_global_bounded_cone_is_complete_but_scoped(self) -> None:
        entry = self.entries["einstein.ph.wm.standard.global_bounded_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("{(c,d,W_x,A)}", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertIn("complete a/d polynomial maps", entry["claim_boundary"])
        self.assertIn("Q_e*a=0", entry["claim_boundary"])

    def test_complete_electric_wilson_transport_is_bounded_but_not_causal(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.electric_wilson_complete_oscillator_transport"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("Q_e*a=0", entry["claim_boundary"])
        self.assertIn("a/d polynomial maps", entry["claim_boundary"])

    def test_circumference_column_separates_resonance_from_polynomial_growth(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.circumference_complete_oscillator_column"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("R_(j,a), not P_(j,r)", entry["mode_data"]["resonance"]["statement"])

    def test_d_column_exposes_full_time_polynomial_repair(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.d_times_ell2_extra"]
        self.assertIn("d*z2=0", entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertIn("not a complete bounded d-column theorem", entry["claim_boundary"])
        abd = self.entries["einstein.ph.wm.interaction.abd_times_ell2_extra"]
        self.assertEqual(abd["mode_data"]["resonance"]["status"], "OPEN")
        self.assertIn("superseded", abd["claim_boundary"])

    def test_multi_ell_minus_pivots_remain_fixture_only(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.abd_times_generic_k0_einstein_minus_pivot_fixtures"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertIn("symbolic functional-form or degree bound", entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["statement"])

    def test_repaired_ad_polynomial_zero_locus_is_exact_but_pre_resonance(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ad_ell2_extra_polynomial_zero_locus"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("<a*z_ax1,a*z_ax2,a*z_pol1,a*z_pol2,d*z_pol2>", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "OPEN")

    def test_complete_global_ell2_extra_cone_collapses_to_standard_global(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.complete_global_ell2_extra_bounded_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertIn("{(c,d,W_x,A)}", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_aligned_global_minus_extra_bounded_cone_survives(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.aligned_global_axial_ell2_minus_extra_bounded_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertIn("x_minus=", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_global_axial_all_m_historical_cone_is_superseded(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.global_axial_ell2_all_m_minus_extra_bounded_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertIn("complete_global_twist", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertIn("SUPERSEDED BY", entry["claim_boundary"])
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_global_both_parity_ell2_historical_cone_is_superseded(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.global_ell2_all_m_both_parity_bounded_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertIn("historical aggregate", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("SUPERSEDED BY", entry["claim_boundary"])

    def test_complete_global_twist_ell2_cone_is_regenerated_after_projector_repair(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.complete_global_twist_ell2_bounded_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("c,W_x,A arbitrary", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertIn("REGENERATED", entry["claim_boundary"])

    def test_global_fixed_ell_k0_bounded_cone_is_registered(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.global_fixed_ell_k0_bounded_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertIn("c,W_x,A", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("historical A=0 restriction is superseded", entry["claim_boundary"])
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_fixed_ell_constant_twist_factorization_is_registered(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.fixed_ell_constant_twist_factorization"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("Q_(ell,+)=Q_(ell,-)=0", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertIn("bounded product cone", entry["claim_boundary"])
        self.assertEqual(entry["descriptions"]["causal"], "NO_CERTIFIED_MAP")

    def test_global_finite_harmonic_k0_bounded_cone_is_registered(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.global_finite_harmonic_k0_bounded_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertIn("c,W_x,A", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertIn("Infinite completion", entry["claim_boundary"])
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_exceptional_ad_pivots_keep_the_live_collision_open(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.exceptional_ell1_ad_resonance_pivots"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("a*t pivot", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertIn("exceptional-times-ell2-extra", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_exceptional_difference_matrix_is_sparse_and_fail_closed(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.exceptional_ell1_ell2_extra_difference_matrix"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("six adjoint projections vanish", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertIn("all-m tensor", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_exceptional_resonance_ellipse_requires_einstein_balance(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.exceptional_axisymmetric_resonance_ellipse"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "OBSTRUCTED")
        self.assertIn("strictly negative", entry["mode_data"]["taub_maps"]["statement"])
        self.assertIn("16*r_x^2+3*r_p^2=115*d^2", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_exceptional_ellipse_einstein_minus_frequency_gate_is_fail_closed(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.exceptional_ellipse_einstein_minus_frequency_gate"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertIn("Forty exact algebraic comparisons", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertIn("complete zero-frequency source cancels", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertIn("same-shell adjoint pairing", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_constant_twist_projector_repair_is_authoritative(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.constant_twist_ell2_projector_repair"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertIn("*dY_21", entry["mode_data"]["resonance"]["statement"])
        bounded = entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]
        self.assertEqual(bounded["status"], "CERTIFIED")
        self.assertIn("R_A^3", bounded["statement"])
        self.assertEqual(entry["descriptions"]["causal"], "NO_CERTIFIED_MAP")

    def test_mistyped_constant_twist_rows_are_superseded(self) -> None:
        identifiers = {
            "einstein.ph.wm.interaction.constant_twist_wave_counterexample",
            "einstein.ph.wm.interaction.constant_twist_ell2_extra_position_zero_locus",
            "einstein.ph.wm.interaction.constant_twist_ell2_einstein_position_zero_locus",
            "einstein.ph.wm.interaction.constant_twist_ell2_moment_resonance_cone",
            "einstein.ph.wm.mixed.constant_twist_ell2_complete_bounded_cone",
        }
        for identifier in identifiers:
            with self.subTest(identifier=identifier):
                entry = self.entries[identifier]
                self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
                self.assertEqual(entry["mode_data"]["resonance"]["status"], "OBSTRUCTED")
                self.assertIn("SUPERSEDED BY", entry["claim_boundary"])

    def test_projector_dependent_successors_are_regenerated(self) -> None:
        identifiers = {
            "einstein.ph.wm.mixed.twist_position_velocity_ell2_complete_bounded_cone",
            "einstein.ph.wm.mixed.twist_circumference_wilson_ell2_complete_bounded_cone",
            "einstein.ph.wm.mixed.d_twist_ell2_complete_bounded_cone",
            "einstein.ph.wm.mixed.complete_global_twist_ell2_bounded_cone",
        }
        for identifier in identifiers:
            with self.subTest(identifier=identifier):
                entry = self.entries[identifier]
                self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
                self.assertEqual(entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
                self.assertIn("REGENERATED", entry["claim_boundary"])

if __name__ == "__main__":
    unittest.main()
