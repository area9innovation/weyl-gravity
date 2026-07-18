import copy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.tangent_cone import plebanski_hacyan_homogeneous_twist_ell2_extra_cone as cone


class PlebanskiHacyanHomogeneousTwistEll2ExtraConeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = cone.build()
        cls.schema = json.loads(cone.SCHEMA.read_text(encoding="utf-8"))

    def test_generated_certificate_is_current(self):
        self.assertEqual(json.loads(cone.OUTPUT.read_text(encoding="utf-8")), self.value)
        Draft202012Validator(self.schema).validate(self.value)

    def test_exact_locus_and_fail_closed_sufficiency(self):
        flags = self.value["classification"]
        self.assertTrue(flags["complete_common_zero_locus_in_declared_nonzero_extra_carrier"])
        self.assertFalse(flags["off_axis_branch_exists"])
        self.assertTrue(flags["aligned_SO3_orbit_is_complete"])
        self.assertFalse(flags["bounded_second_order_right_inverse_constructed"])
        self.assertEqual(self.value["coefficient_elimination"]["b"]["verdict"], "b=0 for every nonzero extra amplitude")
        self.assertEqual(self.value["coefficient_elimination"]["a"]["verdict"], "a=0")
        self.assertEqual(self.value["coefficient_elimination"]["d"]["verdict"], "d=0")

    def test_off_axis_promotion_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.value)
        mutated["classification"]["off_axis_branch_exists"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(mutated)

    def test_bounded_sufficiency_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.value)
        mutated["classification"]["bounded_second_order_right_inverse_constructed"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(mutated)


if __name__ == "__main__":
    unittest.main()
