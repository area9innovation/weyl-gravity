import copy
import json
import unittest

from d_quotient_classical.backreacted_clock import nonlinear_source_transfer_tangent_cone_dictionary as result


class NonlinearSourceTransferDictionaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(result.OUTPUT.read_text())

    def test_dictionary_and_exact_fixture(self):
        result.validate(self.value)
        self.assertEqual(result.exact_fixture()["original_obstruction"], "18*a**2")

    def test_fixture_mutation_fails(self):
        mutated = copy.deepcopy(self.value)
        mutated["exact_fixture"]["transformed_obstruction"] = "0"
        with self.assertRaisesRegex(ValueError, "fixture"):
            result.validate(mutated, verify_sources=False)


if __name__ == "__main__":
    unittest.main()
