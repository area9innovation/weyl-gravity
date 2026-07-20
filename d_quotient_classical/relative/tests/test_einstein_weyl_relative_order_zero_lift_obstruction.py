from __future__ import annotations

import unittest

from d_quotient_classical.relative.einstein_weyl_relative_order_zero_lift_obstruction import build, validate


class OrderZeroLiftObstructionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = build()

    def test_schema_and_exact_rank(self):
        validate(self.value)
        system = self.value["exact_linear_system"]
        self.assertEqual((system["equations"], system["unknowns"]), (480, 310))
        self.assertEqual((system["rank_over_Q"], system["nullity"]), (305, 5))
        self.assertEqual(system["nonzero_entries"], 520)

    def test_kernel_is_only_Maxwell_de_rham_tails(self):
        kernel = self.value["kernel_classification"]
        self.assertTrue(kernel["all_A1_metric_equation_coefficients_zero"])
        self.assertEqual([item["generator"] for item in kernel["basis"]], ["H", "P_x", "J_1", "J_2", "J_3"])
        for item in kernel["basis"]:
            self.assertEqual(sum(term["map"] == "A1" for term in item["terms"]), 4)
            self.assertEqual(sum(term["map"] == "A2" for term in item["terms"]), 1)
            self.assertTrue(all("A_" in term["output"] or term["output"] == "lambda_cov_star" for term in item["terms"]))

    def test_normalized_metric_witness(self):
        witness = self.value["strict_incidence_obstruction"]["normalized_metric_witness"]
        self.assertEqual(witness["output_row"], 20)
        self.assertEqual(witness["coefficient"], "1/4")
        self.assertEqual(self.value["strict_incidence_obstruction"]["metric_order_four_delta2_terms"], 29628)

    def test_fail_closed_boundary(self):
        flags = self.value["classification"]
        self.assertFalse(flags["strict_order_zero_f2_zero_lift_exists"])
        for key in (
            "positive_order_lift_ruled_out",
            "nonzero_f2_ruled_out",
            "alternate_current_improvement_ruled_out",
            "relative_q2_repaired",
            "causal_observable_particle_or_quantum_claim",
        ):
            self.assertFalse(flags[key])


if __name__ == "__main__":
    unittest.main()
