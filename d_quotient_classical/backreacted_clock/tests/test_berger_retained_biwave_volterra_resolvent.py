import hashlib
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.backreacted_clock import berger_retained_biwave_volterra_resolvent as theorem


class BergerRetainedBiwaveVolterraResolventTest(unittest.TestCase):
    def test_typed_resolvents_and_adjoint(self):
        payload, _ = theorem.build()
        theorem.verify(payload)
        self.assertTrue(payload["flags"]["BERGER_RETAINED_METRIC_GREEN_OPERATORS"])
        self.assertTrue(payload["typed_resolvents"]["R_sol_advanced"].endswith("X_s(I)->X_s(I)"))
        self.assertTrue(payload["typed_resolvents"]["R_src_advanced"].endswith("Y_s(I)->Y_s(I)"))
        self.assertEqual(payload["typed_resolvents"]["support_convention"]["advanced"], "J^-(source)")
        self.assertEqual(payload["adjoint_theorem"]["identity"], "(G_A,advanced)^sharp=G_(A^sharp),retarded")
        self.assertFalse(payload["adjoint_theorem"]["A_self_adjoint_used"])

    def test_strict_schema_and_artifacts(self):
        payload = json.loads(theorem.CERTIFICATE_PATH.read_text())
        schema = json.loads(theorem.SCHEMA_PATH.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(payload)
        mutant = dict(payload)
        mutant["unexpected"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)
        for record in payload["analytic_proof_artifacts"].values():
            path = theorem.ROOT / record["path"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record["sha256"])

    def test_persisted_outputs_and_manifest(self):
        payload, bodies = theorem.build()
        theorem._check_outputs(payload, bodies)
        manifest = json.loads(theorem.MANIFEST_PATH.read_text())
        self.assertEqual(manifest["target_result_id"], payload["result_id"])


if __name__ == "__main__":
    unittest.main()
