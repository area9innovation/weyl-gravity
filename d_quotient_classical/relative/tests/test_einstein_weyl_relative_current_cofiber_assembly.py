"""Tests for the relative current/cofiber assembly."""

import unittest

from d_quotient_classical.relative import einstein_weyl_relative_current_cofiber_assembly as producer
from d_quotient_classical.relative.verify_einstein_weyl_relative_current_cofiber_assembly import verify


class RelativeCurrentCofiberAssemblyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = producer.build()

    def test_typed_unary_assembly(self) -> None:
        producer.validate(self.value)
        self.assertEqual(self.value["unary_assembly"]["assembled_rows"], 128)
        self.assertTrue(self.value["classification"]["assembled_unary_square_zero"])
        self.assertTrue(self.value["classification"]["assembled_support_local"])

    def test_charge_receiver_does_not_overpromote_f2(self) -> None:
        self.assertTrue(self.value["classification"]["five_charge_homotopy_moment_map_exact"])
        self.assertTrue(self.value["classification"]["direct_f2_obstruction_preserved"])
        self.assertFalse(self.value["classification"]["full_relative_arity_two_morphism_constructed"])
        self.assertFalse(self.value["classification"]["arity_three_authorized"])

    def test_independent_replay(self) -> None:
        if producer.OUTPUT.exists():
            self.assertEqual(verify()["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
