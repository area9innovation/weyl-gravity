import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

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

    def test_triangle_artifact_hash_is_verified(self):
        value = result.synthetic_triangle()
        value["triangle_artifacts"]["inclusion"]["sha256"] = "0" * 64
        with self.assertRaises(Exception):
            result.validate_triangle(value)

    def test_fixed_identity_cyclic_obstruction_must_be_respected(self):
        value = result.synthetic_triangle()
        value["acceptance_flags"]["FIXED_IDENTITY_CYCLIC_OBSTRUCTION_RESPECTED"] = False
        with self.assertRaises(Exception):
            result.validate_triangle(value)

    def test_fixed_identity_cyclic_obstruction_requires_hashed_resolution(self):
        value = result.synthetic_triangle()
        del value["triangle_artifacts"]["cyclic_obstruction_resolution"]
        with self.assertRaises(Exception):
            result.validate_triangle(value)

    def test_fixed_identity_field_inclusion_cannot_be_silently_reused(self):
        value = result.synthetic_triangle()
        value["cyclic_obstruction_disposition"]["fixed_identity_field_inclusion_reused"] = True
        with self.assertRaises(Exception):
            result.validate_triangle(value)

    def test_missing_inputs_cannot_claim_ready(self):
        value = result.build()
        value["result_state"] = "INPUTS_IMPORTED_RELATIVE_MORPHISM_SOLVE_READY"
        with self.assertRaises(Exception):
            result.verify(value)

    def test_all_valid_inputs_activate_relative_morphism_solve(self):
        with tempfile.TemporaryDirectory(dir=result.ROOT) as temporary:
            directory = Path(temporary)
            triangle_path = directory / "triangle.json"
            einstein_path = directory / "einstein.json"
            weyl_path = directory / "weyl.json"
            triangle_path.write_text(json.dumps(result.synthetic_triangle()))
            einstein_path.write_text(json.dumps(result.synthetic_taylor(
                "EINSTEIN_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1",
                "Einstein-Maxwell",
            )))
            weyl_path.write_text(json.dumps(result.synthetic_taylor(
                "WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1",
                "Weyl-Maxwell",
            )))
            absent = directory / "absent.json"
            with (
                patch.object(result, "TRIANGLE_CANDIDATES", (triangle_path, absent)),
                patch.object(result, "EINSTEIN_CANDIDATES", (einstein_path, absent)),
                patch.object(result, "WEYL_CANDIDATES", (weyl_path, absent)),
            ):
                value = result.build()
        self.assertTrue(all(status == "IMPORTED" for status in value["input_status"].values()))
        self.assertTrue(value["claim_flags"]["ALL_SCIENTIFIC_INPUTS_IMPORTED"])
        self.assertEqual(value["result_state"], "INPUTS_IMPORTED_RELATIVE_MORPHISM_SOLVE_READY")
        self.assertEqual(value["next_gate"], "COMPUTE_RELATIVE_ARITY_TWO_AND_THREE_DEFECTS")


if __name__ == "__main__":
    unittest.main()
