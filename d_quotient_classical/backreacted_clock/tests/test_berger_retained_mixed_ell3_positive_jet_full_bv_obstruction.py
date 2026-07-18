import copy
import json
import unittest

from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_positive_jet_full_bv_obstruction as result,
)


class PositiveJetFullBVObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(result.OUTPUT.read_text())

    def test_certificate_validates_and_pairs_to_one(self):
        result.validate(self.value)
        self.assertEqual(result.target_pairing(self.value), 1)

    def test_weight_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.value)
        for record in mutated["obstruction_witness"]["weights"]:
            if record["page"] == 1:
                record["coefficient"] = "0"
        with self.assertRaisesRegex(ValueError, "pairing"):
            result.validate(mutated, verify_sources=False)

    def test_fail_closed_claim_boundary(self):
        self.assertFalse(self.value["claim_flags"]["RESIDUAL_COHOMOLOGY_OPERATION_NONZERO"])
        self.assertFalse(self.value["claim_flags"]["BRANCH_PROJECTION_DECIDED"])
        self.assertEqual(self.value["lifecycle_status"], "OBSTRUCTED")


if __name__ == "__main__":
    unittest.main()
