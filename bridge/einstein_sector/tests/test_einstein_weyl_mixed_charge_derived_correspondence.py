import copy
import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_weyl_mixed_charge_derived_correspondence import DEFAULT_OUTPUT, build
from bridge.einstein_sector.verify_einstein_weyl_mixed_charge_derived_correspondence import verify_payload


class MixedChargeCorrespondenceTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(DEFAULT_OUTPUT.read_text())

    def test_exact_replay_and_independent_verifier(self):
        self.assertEqual(build(), self.payload)
        verify_payload(self.payload)

    def test_delete_transfer_coordinate_mutation(self):
        bad = copy.deepcopy(self.payload)
        bad["classification"]["anti_diagonal_homotopy_pullback"] = False
        with self.assertRaises(jsonschema.ValidationError):
            verify_payload(bad, False)

    def test_false_separate_neutral_projection_mutation(self):
        bad = copy.deepcopy(self.payload)
        bad["classification"]["separate_neutral_projection_exists"] = True
        with self.assertRaises(jsonschema.ValidationError):
            verify_payload(bad, False)

    def test_delete_koszul_half_mutation(self):
        bad = copy.deepcopy(self.payload)
        bad["derived_correspondence"]["balanced_fixture_tangent_complex"]["rank_d"] = 4
        with self.assertRaises(AssertionError):
            verify_payload(bad, False)

    def test_false_quotient_pairing_mutation(self):
        bad = copy.deepcopy(self.payload)
        bad["classification"]["Schur_form_is_derived_quotient_pairing"] = True
        with self.assertRaises(jsonschema.ValidationError):
            verify_payload(bad, False)

    def test_all_orders_promotion_mutation(self):
        bad = copy.deepcopy(self.payload)
        bad["classification"]["all_orders_kuranishi"] = True
        with self.assertRaises(jsonschema.ValidationError):
            verify_payload(bad, False)


if __name__ == "__main__":
    unittest.main()
