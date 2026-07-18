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

    def test_causal_compact_product_claims_remain_open(self) -> None:
        for entry in self.value["entries"]:
            if "crosswalk" not in entry["id"]:
                self.assertEqual(entry["mode_data"]["second_order"]["causal_retarded"]["status"], "OPEN")

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
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")

    def test_complete_homogeneous_twist_matrix_remains_precone(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.homogeneous_twist_times_ell2_extra"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
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


if __name__ == "__main__":
    unittest.main()
