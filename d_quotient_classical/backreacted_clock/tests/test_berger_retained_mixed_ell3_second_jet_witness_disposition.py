import copy
import json
import unittest

from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_second_jet_witness_disposition as result,
)
from d_quotient_classical.backreacted_clock.verify_berger_retained_mixed_ell3_second_jet_witness_disposition import (
    replay,
    verify,
)


class SecondJetWitnessDispositionTests(unittest.TestCase):
    def test_generated_outputs_are_current(self):
        value = result.build()
        result.validate(value)
        self.assertEqual(json.loads(result.OUTPUT.read_text()), value)

    def test_independent_native_replay(self):
        self.assertEqual(replay((1, 1)), (5, 252, result.sp.Rational(755, 9)))
        self.assertEqual(replay((0, 0))[2], 0)
        self.assertEqual(verify()["result_state"], "ORDER_TWO_OBSTRUCTION_WITHDRAWN_COMPLETE_BOUNDED_CYCLIC_CLASS_OPEN")

    def test_fail_closed_mutations(self):
        value = result.build()
        for name, expected in value["claim_flags"].items():
            mutant = copy.deepcopy(value)
            mutant["claim_flags"][name] = not expected
            with self.assertRaises(Exception, msg=name):
                result.validate(mutant)

    def test_no_branch_or_full_class_promotion(self):
        value = result.build()
        self.assertEqual(value["branch_repair_disposition"]["status"], "NO_CERTIFIED_MAP")
        self.assertEqual(value["full_class_disposition"]["complete_order_two_bounded_cyclic_complex"], "OPEN")
        self.assertEqual(value["full_class_disposition"]["complete_trivializing_cochain"], "NOT_CONSTRUCTED")


if __name__ == "__main__":
    unittest.main()
