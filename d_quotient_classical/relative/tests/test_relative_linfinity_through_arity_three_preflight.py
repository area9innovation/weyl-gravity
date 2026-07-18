import copy
import unittest

from d_quotient_classical.relative import relative_linfinity_through_arity_three_preflight as result


class RelativeLinfinityPreflightTests(unittest.TestCase):
    def test_current_gate_is_input_blocked(self):
        value = result.build()
        self.assertTrue(all(status == "MISSING" for status in value["input_status"].values()))
        self.assertNotIn("relative_branch_dictionary", value["dependency_refs"])
        self.assertFalse(value["scope_guard"]["berger_tensors_eligible"])
        self.assertFalse(value["claim_flags"]["Q4_AUTHORIZED"])

    def test_synthetic_product_payload_validates(self):
        value = result.synthetic_taylor("WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1", "Weyl-Maxwell")
        result.validate_taylor(value, expected_result_id=value["result_id"], expected_theory="Weyl-Maxwell", verify_artifacts=False)

    def test_berger_payload_is_rejected(self):
        value = result.synthetic_taylor("WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1", "Weyl-Maxwell")
        value["background_id"] = "fixed_rational_positive_Berger_clock"
        with self.assertRaises(Exception):
            result.validate_taylor(value, expected_result_id=value["result_id"], expected_theory="Weyl-Maxwell", verify_artifacts=False)

    def test_missing_arity_three_identity_is_rejected(self):
        value = copy.deepcopy(result.synthetic_taylor("EINSTEIN_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1", "Einstein-Maxwell"))
        value["acceptance_flags"]["ARITY_THREE_IDENTITY_VERIFIED"] = False
        with self.assertRaises(Exception):
            result.validate_taylor(value, expected_result_id=value["result_id"], expected_theory="Einstein-Maxwell", verify_artifacts=False)

    def test_triangle_background_is_explicit(self):
        value = result.synthetic_triangle()
        result.validate_triangle(value)
        value["background_id"] = "fixed_rational_positive_Berger_clock"
        with self.assertRaises(Exception):
            result.validate_triangle(value)

    def test_missing_inputs_cannot_claim_ready(self):
        value = result.build()
        value["result_state"] = "INPUTS_IMPORTED_RELATIVE_MORPHISM_SOLVE_READY"
        with self.assertRaises(Exception):
            result.verify(value)


if __name__ == "__main__":
    unittest.main()
