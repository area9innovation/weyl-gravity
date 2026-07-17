import json
import unittest

import jsonschema

from d_quotient_classical.causal_transfer import abstract_cyclic_causal_transfer as theorem


class AbstractCyclicCausalTransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = theorem.build()

    def test_exact_fixture(self):
        fixture = self.payload["finite_exact_fixture"]
        self.assertTrue(all(value == 0 for value in fixture["identity_defects"].values()))

    def test_transfer_formula(self):
        self.assertEqual(
            self.payload["conclusions"]["SDR_transport_formula"],
            "Lambda_C,+/-=h+i Lambda_E,+/- p",
        )

    def test_cyclic_and_shear_closure(self):
        self.assertTrue(self.payload["flags"]["ABSTRACT_CYCLIC_ADJOINT_TRANSFER_CERTIFIED"])
        self.assertTrue(self.payload["flags"]["ABSTRACT_FINITE_CYCLIC_SHEAR_TRANSFER_CERTIFIED"])

    def test_berger_consumers(self):
        consumer = self.payload["berger_consumer"]
        self.assertTrue(consumer["all_rows_replayed"])
        self.assertIn("54=28", consumer["gravity_dimensions"])
        self.assertIn("64=28", consumer["coupled_dimensions"])

    def test_generality_is_fail_closed(self):
        self.assertFalse(self.payload["generality"]["G3_background_class_promoted"])
        self.assertFalse(self.payload["flags"]["SECOND_NONCYLINDER_DETOUR_CONSUMER"])
        self.assertFalse(self.payload["flags"]["HADAMARD_TRANSFER"])

    def test_raw_D_not_promoted(self):
        self.assertIn("raw D is affine", self.payload["berger_consumer"]["generator_scope"])

    def test_mutation_guard(self):
        mutant = json.loads(json.dumps(self.payload))
        mutant["flags"]["HADAMARD_TRANSFER"] = True
        with self.assertRaises((AssertionError, jsonschema.ValidationError)):
            theorem.verify(mutant)


if __name__ == "__main__":
    unittest.main()
