"""Fast tests for the fixed-carrier cyclic rank obstruction."""

import unittest

from d_quotient_classical.relative import einstein_weyl_relative_238_cyclic_rank_obstruction as producer
from d_quotient_classical.relative.verify_einstein_weyl_relative_238_cyclic_rank_obstruction import verify


class Relative238CyclicRankObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = producer.build()

    def test_exact_rank_lower_bound(self) -> None:
        producer.validate(self.value)
        self.assertEqual(self.value["rank_audit"]["combined_ranks"], [10,45,78,69,31,5])
        self.assertEqual(self.value["classification"]["minimum_additional_row_lower_bound"], 28)

    def test_fail_closed_scope(self) -> None:
        flags = self.value["classification"]
        self.assertFalse(flags["fixed_238_row_cyclic_bv_complex_possible"])
        self.assertFalse(flags["noncyclic_238_row_q1q2_complex_obstructed"])
        self.assertFalse(flags["larger_cyclic_mixed_bundle_carrier_obstructed"])

    def test_independent_replay(self) -> None:
        if producer.OUTPUT.exists():
            self.assertEqual(verify()["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
