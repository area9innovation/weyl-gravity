from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "bridge/certificates/einstein_weyl_relative_branch_dictionary.json"


class RelativeBranchDictionaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text(encoding="utf-8"))

    def test_sectoral_maps_do_not_promote_global_bridge(self) -> None:
        self.assertEqual(self.value["bridge"]["current_global_map_lifecycle"], "ONSHELL_MAP_ONLY")
        self.assertFalse(self.value["classification"]["bridge_1_activation_gate_satisfied"])

    def test_every_row_has_full_scope(self) -> None:
        required = {"theory", "background", "boundaries", "charge_sector", "carrier", "degree", "parity", "ell", "m", "k", "omega"}
        for row in self.value["branch_rows"]:
            self.assertEqual(set(row["scope"]), required)

    def test_no_cross_background_identity(self) -> None:
        self.assertFalse(self.value["classification"]["cross_background_mode_identification_made"])

    def test_aligned_common_zero_face_is_only_a_handoff(self) -> None:
        self.assertTrue(self.value["classification"]["aligned_nonzero_stabilizer_resonance_common_zero_face_imported"])
        self.assertTrue(self.value["classification"]["complete_declared_global_extra_common_zero_locus_imported"])
        self.assertTrue(self.value["classification"]["complete_global_extra_bounded_correction_obstruction_imported"])
        self.assertTrue(self.value["classification"]["complete_global_extra_smooth_secular_extension_imported"])
        self.assertTrue(self.value["classification"]["aligned_twist_extra_L1_L3_coefficient_correction_imported"])
        self.assertEqual(self.value["quadratic_handoff"]["status"], "PARTIAL_INPUT")
        self.assertFalse(self.value["classification"]["bridge_1_activation_gate_satisfied"])


if __name__ == "__main__":
    unittest.main()
