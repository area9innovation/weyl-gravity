import json
import sys
import unittest

from d_quotient_classical.backreacted_clock import berger_26_row_causal_green_homotopy as theorem


class Berger26RowCausalGreenHomotopyTest(unittest.TestCase):
    def test_build_and_quantum_consumer_contract(self):
        payload, proof = theorem.build()
        theorem.verify(payload, proof)
        sys.path.insert(0, str(theorem.ROOT / "quantum-weyl"))
        from lorentzian.green_endpoint_contract import validate_green_endpoint_export
        summary = validate_green_endpoint_export(payload, repository_root=theorem.ROOT)
        self.assertEqual(summary["green_status"], "CERTIFIED")
        self.assertEqual(summary["hadamard_status"], "NOT_CONSTRUCTED")

    def test_persisted_outputs(self):
        payload, proof = theorem.build()
        self.assertEqual(json.loads(theorem.CERTIFICATE_PATH.read_text()), payload)
        self.assertEqual(json.loads(theorem.PROOF_PATH.read_text()), proof)


if __name__ == "__main__":
    unittest.main()
