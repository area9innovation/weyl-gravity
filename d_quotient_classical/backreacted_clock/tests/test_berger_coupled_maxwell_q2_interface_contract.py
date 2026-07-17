import json
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.backreacted_clock import berger_coupled_maxwell_q2_interface_contract as result


class BergerCoupledMaxwellQ2InterfaceContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = result.build()

    def test_layout_cyclicity_and_persisted_outputs(self):
        result.verify(self.payload)
        interface = self.payload["combined_BV_interface"]
        self.assertEqual(interface["total_rows"], 64)
        self.assertEqual(interface["degree_ranks"], [6, 26, 26, 6])
        self.assertEqual(interface["row_layout"][54]["row_id"], "c_M")
        self.assertEqual(interface["row_layout"][63]["row_id"], "c_M_plus")
        cyclic = self.payload["standing_light_cyclic_regression"]
        self.assertEqual(cyclic["cyclic_residual"], "0")
        self.assertEqual(cyclic["action_residual"], "0")
        self.assertEqual(cyclic["direct_action_pairing"], "564428800/35920017")
        self.assertEqual(json.loads(result.CERTIFICATE_PATH.read_text()), self.payload)
        self.assertEqual(result.REPORT_PATH.read_text(), result._report(self.payload))

    def test_fail_closed_ledger(self):
        self.assertEqual(self.payload["full_export_acceptance_gate"]["status"], "INPUT_BLOCKED")
        statuses = {entry["block"]: entry["status"] for entry in self.payload["mixed_q2_block_ledger"]}
        self.assertIn("PHYSICAL_FIXTURE_CERTIFIED_SUPPORT_LOCAL_EXPORT_OPEN", statuses.values())
        self.assertIn("INPUT_BLOCKED", statuses.values())
        self.assertFalse(self.payload["background_partition"]["cross_substitution_allowed"])

    def test_schema_mutations(self):
        schema = json.loads(result.SCHEMA_PATH.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.payload)
        mutant = deepcopy(self.payload)
        mutant["standing_light_cyclic_regression"]["canonical_BV_Euler_Maxwell_q2_e023_cosine"] = mutant["standing_light_cyclic_regression"]["equation_form_Maxwell_q2_e023_cosine"]
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)
        mutant = deepcopy(self.payload)
        mutant["full_export_acceptance_gate"]["status"] = "READY"
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)
        mutant = deepcopy(self.payload)
        del mutant["flags"]["BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2"]
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)

    def test_forbidden_promotions(self):
        for flag in (
            "BERGER_FULL_SUPPORT_LOCAL_AA_TO_HPLUS",
            "BERGER_FULL_SUPPORT_LOCAL_HA_TO_APLUS",
            "BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2",
            "BERGER_MAXWELL_UNARY_CONTRACTION",
            "BERGER_FIRST_GRAVITY_MAXWELL_TRANSFERRED_DRESSING",
            "BERGER_AXIAL_BACKGROUND_ADAPTER",
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
