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

    def test_bridge_one_is_fail_closed(self) -> None:
        entry = self.entries["einstein.ph.bridge.relative_branch_dictionary_v1"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "OPEN")
        self.assertEqual(entry["descriptions"]["observational"], "NO_CERTIFIED_MAP")
        self.assertEqual(entry["descriptions"]["quantum"], "NO_CERTIFIED_MAP")

    def test_abd_matrix_is_input_not_full_nonlinear_theorem(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.abd_times_ell2_extra"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")

    def test_complete_homogeneous_twist_matrix_remains_precone(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.homogeneous_twist_times_ell2_extra"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "OPEN")

    def test_aligned_face_is_compatibility_not_extension(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.aligned_twist_ell2_extra_compatibility_face"]
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(entry["mode_data"]["second_order"]["smooth_secular"]["status"], "OPEN")


if __name__ == "__main__":
    unittest.main()
