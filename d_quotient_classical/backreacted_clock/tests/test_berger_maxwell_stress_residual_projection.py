import json
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.backreacted_clock import berger_maxwell_stress_residual_projection as result


class BergerMaxwellStressResidualProjectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = result.build()

    def test_exact_obstruction_and_persisted_outputs(self):
        result.verify(self.payload)
        exact = self.payload["physical_mode_block"]["exact_data"]
        self.assertEqual(exact["q1_closure_residual"], ["0", "0", "0"])
        self.assertEqual(exact["constant_hessian_rank"], 7)
        self.assertEqual(exact["augmented_rank"], 8)
        self.assertEqual(exact["dual_witness_source_pairing"], "1")
        self.assertEqual(exact["stress_covariant_divergence"], ["0"] * 4)
        self.assertEqual(json.loads(result.CERTIFICATE_PATH.read_text()), self.payload)
        self.assertEqual(result.REPORT_PATH.read_text(), result._report(self.payload))

    def test_source_shape_and_diagonal_primitive(self):
        exact = self.payload["physical_mode_block"]["exact_data"]
        self.assertEqual(
            exact["nonzero_retained_rows"],
            [
                {"row_id": "h_hat_star_00", "coefficient": "80/9"},
                {"row_id": "h_hat_star_03", "coefficient": "-160/9"},
                {"row_id": "h_hat_star_33", "coefficient": "80/9"},
            ],
        )
        self.assertTrue(all(value == "0" for value in exact["diagonal_primitive_residual"]))
        self.assertEqual(self.payload["physical_mode_block"]["D_weight"], "0")

    def test_schema_mutations(self):
        schema = json.loads(result.SCHEMA_PATH.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.payload)
        mutant = deepcopy(self.payload)
        mutant["projection_and_verdict"]["binary_verdict"] = "EXACT"
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)
        mutant = deepcopy(self.payload)
        mutant["physical_mode_block"]["exact_data"]["dual_witness_source_pairing"] = "0"
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)
        mutant = deepcopy(self.payload)
        del mutant["flags"]["BERGER_FULL_SUPPORT_LOCAL_MAXWELL_Q2"]
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)

    def test_fail_closed_promotions(self):
        for flag in (
            "BERGER_FULL_SUPPORT_LOCAL_MAXWELL_Q2",
            "BERGER_FULL_RESIDUAL_GRAVITY_MAXWELL_BRACKET",
            "BERGER_EINSTEIN_EXTRA_WEYL_BRANCH_MIXING",
            "BERGER_MAXWELL_BACKREACTED_SOLUTION",
            "NEGATIVE_PHYSICAL_DIRECTION_INTRODUCED",
            "LORENTZIAN_CERTIFIED",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(self.payload)
            mutant["flags"][flag] = True
            with self.assertRaises(AssertionError):
                result.verify(mutant)


if __name__ == "__main__":
    unittest.main()
