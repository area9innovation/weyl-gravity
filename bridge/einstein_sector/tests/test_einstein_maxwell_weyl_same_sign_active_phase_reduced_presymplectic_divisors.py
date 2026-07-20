import copy
import json
import unittest

from jsonschema import ValidationError

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_active_phase_reduced_presymplectic_divisors import (
    OUTPUT,
    SCHEMA,
    build,
)


class ActivePhaseReducedPresymplecticDivisorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(OUTPUT.read_text())
        cls.schema = json.loads(SCHEMA.read_text())

    def test_certificate_rebuilds_exactly(self) -> None:
        self.assertEqual(self.payload, build())

    def test_common_node_phases_are_not_split_by_parity(self) -> None:
        row = self.payload["candidate17_20"]
        self.assertEqual(row["augmented_matrix"], "A_3=stack(J_T3_plus,J_T3_minus,C_minus,C_plus), shape 8x20")
        self.assertIn("not the product", row["important_nonfactorization"])
        self.assertEqual(row["horizontal_complex_dimension"], 12)

    def test_candidate17_20_witness_and_control_separate_the_divisor(self) -> None:
        row = self.payload["candidate17_20"]
        self.assertEqual(row["exact_bounded_witness"]["augmented_normal_rank"], 6)
        self.assertEqual(row["exact_bounded_witness"]["reduced_current_radical_complex_dimension"], 2)
        self.assertEqual(row["exact_nondegenerate_control"]["augmented_normal_rank"], 8)
        self.assertNotEqual(row["exact_nondegenerate_control"]["augmented_normal_determinant"], "0")

    def test_candidate18_spectators_and_all_product_charts_are_retained(self) -> None:
        row = self.payload["candidate18"]
        self.assertEqual(row["rank_one_chart_atlas"]["product_chart_count"], 100)
        self.assertIn("spectators", row["ambient_coordinate_order"])
        self.assertEqual(
            [branch["reduced_current_radical_complex_dimension"] for branch in row["aligned_central_angular_section"]["branch_rows"]],
            [4, 4],
        )
        self.assertEqual(
            [branch["linear_presymplectic_quotient_complex_dimension"] for branch in row["aligned_central_angular_section"]["branch_rows"]],
            [16, 16],
        )

    def test_fail_closed_flags_are_schema_enforced(self) -> None:
        mutated = copy.deepcopy(self.payload)
        mutated["classification"]["lifted_rotation_reduction_classified"] = True
        with self.assertRaises(ValidationError):
            __import__("jsonschema").validate(mutated, self.schema)
        self.assertFalse(self.payload["classification"]["occupation_strata_glued"])
        self.assertFalse(self.payload["classification"]["causal_residual_observational_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
