import copy
import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_weyl_compact_cauchy_third_order_kuranishi_obstruction import DEFAULT_OUTPUT, build
from bridge.einstein_sector.verify_einstein_weyl_compact_cauchy_third_order_kuranishi_obstruction import verify_payload


class ThirdOrderKuranishiObstructionTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(DEFAULT_OUTPUT.read_text())

    def test_replay_and_independent_audit(self):
        self.assertEqual(build(), self.payload)
        verify_payload(self.payload)

    def test_false_D3_presence(self):
        bad = copy.deepcopy(self.payload)
        bad["classification"]["D3_constraint_tensor_present"] = True
        with self.assertRaises(jsonschema.ValidationError):
            verify_payload(bad, False)

    def test_false_balanced_evaluation(self):
        bad = copy.deepcopy(self.payload)
        bad["classification"]["balanced_cubic_class_evaluated"] = True
        with self.assertRaises(jsonschema.ValidationError):
            verify_payload(bad, False)

    def test_hide_correction_ambiguity(self):
        bad = copy.deepcopy(self.payload)
        bad["balanced_slice_ambiguity"]["rank"] = 0
        with self.assertRaises(AssertionError):
            verify_payload(bad, False)

    def test_omit_resonant_shell(self):
        bad = copy.deepcopy(self.payload)
        bad["resonance_closed_carrier"]["kinematic_shell_resonances"].pop()
        with self.assertRaises(AssertionError):
            verify_payload(bad, False)

    def test_false_gauge_independence(self):
        bad = copy.deepcopy(self.payload)
        bad["classification"]["gauge_representative_independence"] = True
        with self.assertRaises(jsonschema.ValidationError):
            verify_payload(bad, False)

    def test_false_third_order_sufficiency(self):
        bad = copy.deepcopy(self.payload)
        bad["classification"]["five_quadratic_Taub_charges_sufficient_through_order_three"] = True
        with self.assertRaises(jsonschema.ValidationError):
            verify_payload(bad, False)


if __name__ == "__main__":
    unittest.main()
