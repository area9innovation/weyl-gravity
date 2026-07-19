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

    def test_global_axial_all_m_bounded_cone_survives(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.global_axial_ell2_all_m_minus_extra_bounded_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertIn("wave-density", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
