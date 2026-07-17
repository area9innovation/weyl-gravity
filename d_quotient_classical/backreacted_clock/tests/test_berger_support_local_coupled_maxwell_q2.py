import json
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.backreacted_clock import berger_support_local_coupled_maxwell_q2_export as result


class BergerSupportLocalCoupledMaxwellQ2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate, cls.payload = result.build()

    def test_complete_export_and_persisted_outputs(self):
        result.verify(self.certificate, self.payload)
        self.assertEqual(self.certificate["exact_diagnostics"]["arity_two_defect_term_counts"], [0] * 64)
        self.assertEqual(len(self.payload["rows"]), 64)
        self.assertEqual(self.certificate["classical_binary_q2"]["overlay_term_count"], 1954)
        self.assertEqual(self.certificate["classical_binary_q2"]["combined_term_count"], 152259)
        self.assertEqual(json.loads(result.CERTIFICATE_PATH.read_text()), self.certificate)
        self.assertEqual(json.loads(result.PAYLOAD_PATH.read_text()), self.payload)
        self.assertEqual(result.REPORT_PATH.read_text(), result._report(self.certificate))

    def test_clock_and_physical_regressions(self):
        diagnostics = self.certificate["exact_diagnostics"]
        self.assertEqual(diagnostics["Theta_source_term_count"], 108)
        self.assertEqual(self.payload["rows"][37]["terms"], [])
        self.assertNotEqual(self.payload["rows"][38]["terms"], [])
        physical = diagnostics["physical_regressions"]
        self.assertEqual(physical["standing_metric_source"], ["160/9", "0", "0", "0", "-160/9", "0", "0", "160/9", "0", "160/9"])
        self.assertTrue(physical["canonical_Maxwell_Euler_sign_recovered"])

    def test_frozen_generator_is_K_not_raw_D(self):
        action = self.certificate["frozen_K_action_Maxwell_rows"]
        self.assertEqual(action["generator"], "K_Berger=D-omega R")
        self.assertEqual(action["PBW_representation"], "e0 on the frozen dressed Maxwell rows")
        self.assertTrue(self.certificate["flags"]["K_BERGER_GENERATOR_SEMANTICS_IMPORTED"])
        self.assertTrue(
            self.certificate["flags"]["BERGER_LOCAL_K_ACTION_EQUIVARIANT_COUPLED_MAXWELL_ARITY_TWO"]
        )
        self.assertFalse(
            self.certificate["flags"]["BERGER_RAW_D_ACTION_EQUIVARIANT_COUPLED_MAXWELL_ARITY_TWO"]
        )
        self.assertFalse(self.certificate["flags"]["RAW_D_CARTAN_CERTIFIED"])

    def test_schemas_and_mutations(self):
        schema = json.loads(result.SCHEMA_PATH.read_text())
        payload_schema = json.loads(result.PAYLOAD_SCHEMA_PATH.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator.check_schema(payload_schema)
        Draft202012Validator(schema).validate(self.certificate)
        Draft202012Validator(payload_schema).validate(self.payload)
        mutant = deepcopy(self.certificate)
        mutant["flags"]["BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2"] = False
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)
        mutant = deepcopy(self.certificate)
        mutant["frozen_K_action_Maxwell_rows"]["generator"] = "D=e0"
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)
        mutant = deepcopy(self.payload)
        mutant["rows"][38]["terms"] = []
        with self.assertRaises(ValidationError):
            Draft202012Validator(payload_schema).validate(mutant)

    def test_downstream_promotions_rejected(self):
        for flag in (
            "BERGER_RAW_D_ACTION_EQUIVARIANT_COUPLED_MAXWELL_ARITY_TWO",
            "RAW_D_CARTAN_CERTIFIED",
            "BERGER_MAXWELL_UNARY_CONTRACTION",
            "BERGER_FIRST_GRAVITY_MAXWELL_TRANSFERRED_DRESSING",
            "BERGER_AXIAL_BACKGROUND_ADAPTER",
            "LORENTZIAN_CERTIFIED",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(self.certificate)
            mutant["flags"][flag] = True
            with self.assertRaises(AssertionError):
                result.verify(mutant, self.payload)


if __name__ == "__main__":
    unittest.main()
