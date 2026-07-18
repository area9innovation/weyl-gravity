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

    def test_full_noncyclic_triangle_promotes_only_linear_bridge(self) -> None:
        self.assertEqual(
            self.value["bridge"]["current_global_map_lifecycle"],
            "NONCYCLIC_THREE_FORM_LINEAR_TRIANGLE_CERTIFIED",
        )
        self.assertTrue(self.value["classification"]["bridge_1_activation_gate_satisfied"])
        self.assertFalse(self.value["relative_forms"]["identity_inclusion_symplectic"])

    def test_every_row_has_full_scope(self) -> None:
        required = {"theory", "background", "boundaries", "charge_sector", "carrier", "degree", "parity", "ell", "m", "k", "omega"}
        for row in self.value["branch_rows"]:
            self.assertEqual(set(row["scope"]), required)

    def test_no_cross_background_identity(self) -> None:
        self.assertFalse(self.value["classification"]["cross_background_mode_identification_made"])

    def test_generic_standard_pairing_cyclic_route_is_closed(self) -> None:
        self.assertTrue(self.value["classification"]["generic_standard_pairing_cyclic_maps_obstructed"])
        self.assertEqual(self.value["relative_forms"]["required_triangle_kind"], "NONCYCLIC_THREE_FORM")
        for identifier in ("ph.generic.axial.relative", "ph.generic.polar.relative"):
            row = next(item for item in self.value["branch_rows"] if item["id"] == identifier)
            self.assertIn("incompatible cohomology-form inertia", row["action_derived_pairing"]["standard_pairing_cyclic_map"])
            self.assertIn("nonlinear relative morphism", row["missing"])

    def test_exceptional_and_global_row_maps_are_no_longer_open(self) -> None:
        flags = self.value["classification"]
        self.assertTrue(flags["exceptional_and_global_harmonic_offshell_maps_certified"])
        self.assertTrue(flags["all_harmonic_sector_coefficient_maps_available"])
        self.assertTrue(flags["single_covariant_support_local_map_reconstructed"])
        rows = {row["id"]: row for row in self.value["branch_rows"]}
        self.assertEqual(rows["ph.exceptional.ell1.relative"]["map_lifecycle"], "DERIVED_COFIBER_TRIANGLE")
        self.assertEqual(rows["ph.exceptional.ell1.nonzero_k.relative"]["map_lifecycle"], "DERIVED_COFIBER_TRIANGLE")
        self.assertEqual(rows["ph.exceptional.ell1.nonzero_k.relative"]["projection_or_cofiber"]["status"], "CERTIFIED")
        self.assertEqual(rows["ph.global.homogeneous.relative"]["map_lifecycle"], "DERIVED_COFIBER_TRIANGLE")

    def test_aligned_common_zero_face_is_only_a_handoff(self) -> None:
        self.assertTrue(self.value["classification"]["aligned_nonzero_stabilizer_resonance_common_zero_face_imported"])
        self.assertTrue(self.value["classification"]["complete_declared_global_extra_common_zero_locus_imported"])
        self.assertTrue(self.value["classification"]["complete_global_extra_bounded_correction_obstruction_imported"])
        self.assertTrue(self.value["classification"]["complete_global_extra_smooth_secular_extension_imported"])
        self.assertTrue(self.value["classification"]["aligned_twist_extra_L1_L3_coefficient_correction_imported"])
        self.assertEqual(self.value["quadratic_handoff"]["status"], "PARTIAL_INPUT")
        self.assertTrue(self.value["classification"]["bridge_1_activation_gate_satisfied"])


if __name__ == "__main__":
    unittest.main()
