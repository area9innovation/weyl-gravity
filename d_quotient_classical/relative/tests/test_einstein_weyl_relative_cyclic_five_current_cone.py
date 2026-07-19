"""Fast tests for the cyclic five-current BV cone."""

import json
import unittest

from d_quotient_classical.relative import einstein_weyl_relative_cyclic_five_current_cone as producer
from d_quotient_classical.relative.verify_einstein_weyl_relative_cyclic_five_current_cone import verify


class CyclicFiveCurrentConeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = producer.build()

    def test_schema_and_rows(self) -> None:
        producer.validate(self.value)
        self.assertEqual(self.value["generated_layout"]["degree_ranks"], [5, 20, 20, 5])
        self.assertTrue(self.value["classification"]["cyclic_dual_bv_rows_certified"])

    def test_fail_closed(self) -> None:
        self.assertFalse(self.value["classification"]["global_improvement_smoothness_certified"])
        self.assertFalse(self.value["classification"]["slice_integral_matches_complete_five_charge_q2"])

    def test_independent_replay(self) -> None:
        if producer.OUTPUT.exists() and producer.GENERATED.exists():
            self.assertEqual(verify()["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
