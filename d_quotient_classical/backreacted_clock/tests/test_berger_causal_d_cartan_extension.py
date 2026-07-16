import json
import unittest

from d_quotient_classical.backreacted_clock import berger_causal_d_cartan_extension as theorem


class BergerCausalDCartanExtensionTest(unittest.TestCase):
    def test_cyclic_causal_arity_two(self):
        payload = theorem.build()
        theorem.verify(payload)
        self.assertTrue(payload["flags"]["BERGER_CAUSAL_D_CARTAN_EXTENSION"])
        self.assertTrue(payload["support_scope"]["cyclic_Cartan_primitives_are_two_sided_causal"])
        self.assertFalse(payload["flags"]["QUANTUM_CLAIM"])

    def test_persisted_certificate(self):
        self.assertEqual(json.loads(theorem.CERTIFICATE_PATH.read_text()), theorem.build())


if __name__ == "__main__":
    unittest.main()
