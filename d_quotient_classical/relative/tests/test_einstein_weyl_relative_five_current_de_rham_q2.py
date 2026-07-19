"""Scoped tests for the five-current de Rham arity-two interface."""

import hashlib
import json
import unittest

from d_quotient_classical.relative import einstein_weyl_relative_five_current_de_rham_q2 as producer


class FiveCurrentDeRhamQ2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = producer.build()

    def test_schema_and_exact_factorization(self) -> None:
        producer.validate(self.value)
        self.assertTrue(self.value["classification"]["all_five_hessian_pullback_factorizations_exact"])
        self.assertTrue(self.value["classification"]["current_interface_q1q2_identity_exact"])

    def test_complete_carrier_audit_is_scoped(self) -> None:
        self.assertTrue(self.value["classification"]["all_160_carrier_rows_audited"])
        self.assertEqual(self.value["operations"]["carrier_row_audit"]["active_orbit_rows"], 50)
        self.assertEqual(self.value["operations"]["carrier_row_audit"]["zero_q2_rows"], 110)
        self.assertFalse(self.value["classification"]["full_relative_238_row_arity_two_morphism_constructed"])
        self.assertFalse(self.value["classification"]["causal_green_homotopy_certified"])

    def test_generated_operation_hash(self) -> None:
        if producer.OUTPUT.exists() and producer.GENERATED.exists():
            generated = json.loads(producer.GENERATED.read_text())
            digest = hashlib.sha256((json.dumps(generated, indent=2, sort_keys=True) + "\n").encode()).hexdigest()
            self.assertEqual(digest, self.value["generated_operations"]["sha256"])


if __name__ == "__main__":
    unittest.main()
