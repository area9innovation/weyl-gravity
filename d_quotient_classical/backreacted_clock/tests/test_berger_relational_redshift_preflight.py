import json
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.backreacted_clock import berger_relational_redshift_preflight as preflight


class BergerRelationalRedshiftPreflightTest(unittest.TestCase):
    def test_exact_build_and_persisted_outputs(self):
        payload = preflight.build()
        preflight.verify(payload)
        self.assertEqual(payload["rational_fixture"]["results"]["one_plus_z"], "2")
        self.assertEqual(json.loads(preflight.CERTIFICATE_PATH.read_text()), payload)
        self.assertEqual(preflight.REPORT_PATH.read_text(), preflight._report(payload))

    def test_draft_2020_12_schema_and_required_mutation(self):
        schema = json.loads(preflight.SCHEMA_PATH.read_text())
        payload = preflight.build()
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(payload)
        mutant = deepcopy(payload)
        del mutant["flags"]["QUANTUM_CLAIM"]
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)
        mutant = deepcopy(payload)
        mutant["relational_geometry"]["physical_metric_weyl_invariant"] = False
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)

    def test_fail_closed_promotions_rejected(self):
        payload = preflight.build()
        for flag in (
            "BERGER_COMPLETE_RELATIONAL_OBSERVABLE",
            "BERGER_INTERACTING_SIGNAL_SOLUTION",
            "BERGER_SPATIALLY_DRESSED_ENDPOINT_ALGEBRA",
            "BERGER_REDSHIFT_PHENOMENOLOGY",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(payload)
            mutant["flags"][flag] = True
            with self.assertRaises(AssertionError):
                preflight.verify(mutant)


if __name__ == "__main__":
    unittest.main()
