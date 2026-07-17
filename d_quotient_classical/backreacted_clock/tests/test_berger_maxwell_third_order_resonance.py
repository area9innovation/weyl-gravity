import json
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.backreacted_clock import berger_maxwell_third_order_resonance as result


class BergerMaxwellThirdOrderResonanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = result.build()

    def test_full_unary_lift_and_persisted_outputs(self):
        result.verify(self.payload)
        lift = self.payload["full_54_row_lift"]
        self.assertEqual(lift["homotopy_source_nonzero_rows"], [])
        self.assertFalse(lift["nonminimal_components_induced"])
        self.assertTrue(all(value == "0" for value in lift["source_q1_closure_residual"]))
        self.assertTrue(all(value == "0" for value in lift["full_Maurer_Cartan_residual"]))
        self.assertTrue(all(value == "0" for value in lift["projection_residual"]))
        self.assertEqual(json.loads(result.CERTIFICATE_PATH.read_text()), self.payload)
        self.assertEqual(result.REPORT_PATH.read_text(), result._report(self.payload))

    def test_resonance_and_frequency_continuation(self):
        mixed = self.payload["physical_mixed_q2_block"]
        self.assertEqual(mixed["relative_dispersion_variation"], "-7055360/3991113")
        self.assertEqual(mixed["resonant_harmonic_source"], ["564428800/35920017", "0"])
        self.assertEqual(mixed["normalized_dual_witness"], ["35920017/564428800", "0"])
        self.assertEqual(mixed["dual_witness_source_pairing"], "1")
        self.assertEqual(mixed["fixed_frequency_verdict"], "OBSTRUCTION")
        self.assertEqual(mixed["frequency_renormalized_residual"], "0")

    def test_schema_mutations(self):
        schema = json.loads(result.SCHEMA_PATH.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.payload)
        mutant = deepcopy(self.payload)
        mutant["binary_verdict"]["fixed_frequency_periodic_primitive"] = "EXACT_PRIMITIVE"
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)
        mutant = deepcopy(self.payload)
        mutant["physical_mixed_q2_block"]["dual_witness_source_pairing"] = "0"
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)
        mutant = deepcopy(self.payload)
        del mutant["flags"]["BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2"]
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)

    def test_fail_closed_promotions(self):
        for flag in (
            "BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2",
            "BERGER_ALL_ORDERS_BACKREACTED_SOLUTION",
            "BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE",
            "BERGER_RADIATIVE_BRANCH_COUPLING_CLASSIFIED",
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
