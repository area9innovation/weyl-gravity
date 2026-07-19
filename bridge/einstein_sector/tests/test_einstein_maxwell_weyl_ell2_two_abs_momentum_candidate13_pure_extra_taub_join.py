import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_pure_extra_taub_join.json"


class Candidate13PureExtraTaubJoinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERTIFICATE.read_text())

    def test_declared_carrier_is_pure_extra(self) -> None:
        self.assertIn("p-primary", self.value["real_tangent_domain"]["positive_frequency_coordinates"])
        self.assertIn("q-primary", self.value["real_tangent_domain"]["excluded"])

    def test_time_taub_form_is_negative_definite(self) -> None:
        taub = self.value["taub_restriction"]
        self.assertEqual(taub["axial_extra_Gram_inertia"], [2, 0])
        self.assertEqual(taub["polar_extra_Gram_inertia"], [2, 0])
        self.assertIn("mu_H(u)<0", taub["verdict"])

    def test_resonance_moment_common_zero_is_origin(self) -> None:
        theorem = self.value["common_zero_theorem"]
        self.assertEqual(theorem["equation"], "Z_res(candidate13) intersect {mu_H=0}={0}")
        self.assertFalse(theorem["same_fibre_sources_needed_for_no_go"])

    def test_correction_classes_are_typed(self) -> None:
        verdict = self.value["second_order_verdict"]
        self.assertTrue(verdict["bounded_or_finite_quasiperiodic"].startswith("OBSTRUCTED"))
        self.assertTrue(verdict["smooth_secular"].startswith("OBSTRUCTED"))
        self.assertEqual(verdict["causal_retarded"], "NO_CERTIFIED_MAP")

    def test_broader_mixed_cone_remains_open(self) -> None:
        flags = self.value["classification"]
        self.assertFalse(flags["candidate_13_same_fibre_source_matrices_classified"])
        self.assertFalse(flags["mixed_Einstein_extra_two_fibre_cone_classified"])


if __name__ == "__main__":
    unittest.main()
