import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_L4_incidence_reduction.json"


class Candidate13L4IncidenceReductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERTIFICATE.read_text())

    def test_pencil_has_four_real_simple_roots(self) -> None:
        witnesses = self.value["exact_interval_witnesses"]
        for key in ("trace_square_pencil", "determinant_square_pencil", "discriminant_square_pencil"):
            self.assertEqual(witnesses[key]["sign"], "positive")
        self.assertIn("four distinct nonzero real", self.value["pencil_reduction"]["root_structure"])

    def test_generic_rank_witness_is_exact(self) -> None:
        generic = self.value["generic_open_stratum"]
        self.assertEqual(generic["rank_18_minor"], "-(lambda_1 - lambda_2)**4*(lambda_3 - lambda_4)**5")
        self.assertEqual(generic["linear_rank"], 18)
        self.assertEqual(generic["kernel_dimension"], 2)
        self.assertEqual(generic["incidence_dimension_over_C"], 22)

    def test_normal_form_keeps_both_octic_equations(self) -> None:
        equations = self.value["pencil_reduction"]["normal_form_equations"]
        self.assertEqual(len(equations), 2)
        self.assertTrue(all("Sym^8" in equation for equation in equations))
        self.assertTrue(self.value["classification"]["three_root_cancellation_witness_certified"])
        self.assertIn("three pencil eigenlines", self.value["mixed_root_cancellation_witness"]["nonfactorization"])

    def test_coordinate_boundary_is_strictly_lower_dimensional(self) -> None:
        boundary = self.value["coordinate_boundary_stratification"]
        self.assertEqual(boundary["representative_linear_ranks"], {"0": 0, "1": 5, "2": 10, "3": 15})
        self.assertEqual(boundary["maximum_boundary_incidence_dimension"], 20)
        self.assertTrue(self.value["classification"]["coordinate_boundary_dimension_20_certified"])
        self.assertIn("generic point lies in the torus", boundary["consequence"])

    def test_full_ideal_remains_open(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["complete_rank_stratification_certified"])
        self.assertFalse(classification["full_candidate_13_zero_variety_classified"])
        self.assertFalse(classification["taub_common_zero_intersection_classified"])
        self.assertFalse(classification["complete_two_fibre_tangent_cone_classified"])


if __name__ == "__main__":
    unittest.main()
