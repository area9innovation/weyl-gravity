import json
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.backreacted_clock import berger_dynamical_maxwell_redshift as result


class BergerDynamicalMaxwellRedshiftTest(unittest.TestCase):
    def test_exact_mode_and_persisted_outputs(self):
        payload = result.build()
        result.verify(payload)
        self.assertEqual(payload["rational_fixture"]["results"]["one_plus_z"], "2")
        self.assertEqual(payload["health_and_pairing"]["energy_signature"], [2, 0, 0])
        self.assertEqual(json.loads(result.CERTIFICATE_PATH.read_text()), payload)
        self.assertEqual(result.REPORT_PATH.read_text(), result._report(payload))

    def test_schema_and_required_mutations(self):
        schema = json.loads(result.SCHEMA_PATH.read_text())
        payload = result.build()
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(payload)
        mutant = deepcopy(payload)
        del mutant["flags"]["BERGER_GRAVITY_MAXWELL_Q2_DRESSING"]
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)
        mutant = deepcopy(payload)
        mutant["health_and_pairing"]["energy_signature"] = [1, 1, 0]
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)

    def test_fail_closed_promotions(self):
        payload = result.build()
        for flag in (
            "BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE",
            "BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL",
            "BERGER_GRAVITY_MAXWELL_Q2_DRESSING",
            "BERGER_MAXWELL_BACKREACTION",
            "BERGER_G1_COMPLETE_SIGNAL_SECTOR",
            "BERGER_REDSHIFT_PHENOMENOLOGY",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(payload)
            mutant["flags"][flag] = True
            with self.assertRaises(AssertionError):
                result.verify(mutant)


if __name__ == "__main__":
    unittest.main()
