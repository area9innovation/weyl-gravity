import copy
import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_weyl_compact_cauchy_cubic_constraint_tensor_export import DEFAULT_OUTPUT, build
from bridge.einstein_sector.verify_einstein_weyl_compact_cauchy_cubic_constraint_tensor_export import verify_payload


class CubicConstraintTensorExportTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(DEFAULT_OUTPUT.read_text())

    def test_replay_and_independent_audit(self):
        self.assertEqual(build(), self.payload)
        verify_payload(self.payload)

    def test_set_scale_to_one_mutation(self):
        bad = copy.deepcopy(self.payload)
        bad["classification"]["exact_action_to_canonical_normalization_present"] = True
        with self.assertRaises(jsonschema.ValidationError):
            verify_payload(bad, False)

    def test_zero_momenta_mutation(self):
        bad = copy.deepcopy(self.payload)
        bad["classification"]["covariant_to_canonical_correction_crosswalk_present"] = True
        with self.assertRaises(jsonschema.ValidationError):
            verify_payload(bad, False)

    def test_false_Hperp_export(self):
        bad = copy.deepcopy(self.payload)
        bad["classification"]["action_normalized_Hperp_D3_exported"] = True
        with self.assertRaises(jsonschema.ValidationError):
            verify_payload(bad, False)

    def test_scale_witness_mutation(self):
        bad = copy.deepcopy(self.payload)
        bad["normalization_witness"]["scale_2"] = "1/32"
        with self.assertRaises(AssertionError):
            verify_payload(bad, False)

    def test_false_noether_export(self):
        bad = copy.deepcopy(self.payload)
        bad["classification"]["arity_three_noether_exported"] = True
        with self.assertRaises(jsonschema.ValidationError):
            verify_payload(bad, False)

    def test_insert_zero_mutation(self):
        bad = copy.deepcopy(self.payload)
        bad["classification"]["absent_coefficient_inserted_as_zero"] = True
        with self.assertRaises(jsonschema.ValidationError):
            verify_payload(bad, False)


if __name__ == "__main__":
    unittest.main()
