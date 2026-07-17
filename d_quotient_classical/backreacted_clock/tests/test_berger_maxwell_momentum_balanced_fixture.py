import json
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.backreacted_clock import berger_maxwell_momentum_balanced_fixture as result


class BergerMaxwellMomentumBalancedFixtureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = result.build()

    def test_normalization_balance_and_persisted_outputs(self):
        result.verify(self.payload)
        exact = self.payload["balanced_Maxwell_fixture"]["exact_data"]
        self.assertTrue(all(value == "0" for value in exact["normalization_residual"]))
        self.assertEqual(exact["Hopf_flux_standing"], "0")
        self.assertEqual(exact["normalized_single_beam_witness_pairing"], "0")
        self.assertEqual(exact["constant_hessian_rank"], exact["augmented_rank"])
        self.assertEqual(json.loads(result.CERTIFICATE_PATH.read_text()), self.payload)
        self.assertEqual(result.REPORT_PATH.read_text(), result._report(self.payload))

    def test_second_order_correction_and_health(self):
        exact = self.payload["balanced_Maxwell_fixture"]["exact_data"]
        self.assertTrue(all(value == "0" for value in exact["second_order_Maurer_Cartan_residual"]))
        self.assertEqual(exact["symplectic_pairing"], "-64*pi**2")
        self.assertEqual(exact["positive_energy_coefficient"], "64*sqrt(10)*pi**2/3")
        self.assertEqual(self.payload["branch_and_health"]["energy_signature"], [2, 0, 0])

    def test_schema_mutations(self):
        schema = json.loads(result.SCHEMA_PATH.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.payload)
        mutant = deepcopy(self.payload)
        mutant["projection_and_solution"]["binary_verdict"] = "OBSTRUCTION"
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)
        mutant = deepcopy(self.payload)
        mutant["balanced_Maxwell_fixture"]["exact_data"]["Hopf_flux_standing"] = "1"
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)
        mutant = deepcopy(self.payload)
        del mutant["flags"]["BERGER_FULL_SUPPORT_LOCAL_MAXWELL_Q2"]
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)

    def test_fail_closed_promotions(self):
        for flag in (
            "BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE",
            "BERGER_FULL_SUPPORT_LOCAL_MAXWELL_Q2",
            "BERGER_RADIATIVE_BRANCH_COUPLING_CLASSIFIED",
            "BERGER_FULL_BACKREACTED_SOLUTION",
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
