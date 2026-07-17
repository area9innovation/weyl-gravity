import json
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.backreacted_clock import berger_maxwell_bv_semidirect_preflight as result


class BergerMaxwellBVSemidirectPreflightTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = result.build()

    def test_exact_gauge_algebra_and_outputs(self):
        result.verify(self.payload)
        exact = self.payload["semidirect_q2_gauge_sector"]["exact_checks"]
        self.assertEqual(exact["action_commutator_residual"], ["0"] * 4)
        self.assertEqual(exact["semidirect_jacobi_vector_residual"], ["0"] * 4)
        self.assertEqual(exact["semidirect_jacobi_u1_residual"], "0")
        self.assertEqual(exact["field_strength_gauge_residual"], {})
        self.assertEqual(exact["field_strength_covariance_residual"], {})
        self.assertEqual(json.loads(result.CERTIFICATE_PATH.read_text()), self.payload)
        self.assertEqual(result.REPORT_PATH.read_text(), result._report(self.payload))

    def test_row_layout_and_fail_closed_inputs(self):
        self.assertEqual(sum(row["multiplicity"] for row in self.payload["maxwell_bv_complex"]["row_layout"]), 10)
        self.assertEqual(self.payload["maxwell_bv_complex"]["combined_gravity_clock_maxwell_rows"], 64)
        self.assertEqual(self.payload["dynamical_mixed_q2_ledger"]["status"], "INPUT_BLOCKED")
        self.assertEqual(self.payload["relational_apparatus_contract"]["status"], "CONTRACT_COMPLETE_EXACT_FIXTURE_INPUT_BLOCKED")

    def test_schema_and_mutations(self):
        schema = json.loads(result.SCHEMA_PATH.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.payload)
        mutant = deepcopy(self.payload)
        del mutant["flags"]["BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2"]
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)
        mutant = deepcopy(self.payload)
        mutant["dynamical_mixed_q2_ledger"]["status"] = "READY"
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)
        mutant = deepcopy(self.payload)
        mutant["semidirect_q2_gauge_sector"]["exact_checks"]["field_strength_gauge_residual"] = {"01": "1"}
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)

    def test_forbidden_promotions(self):
        for flag in (
            "BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2",
            "BERGER_FIRST_GRAVITY_MAXWELL_TRANSFERRED_DRESSING",
            "BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE",
            "BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL",
            "BERGER_MAXWELL_BACKREACTION",
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
