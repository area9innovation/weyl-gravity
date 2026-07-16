from copy import deepcopy
import unittest

from d_quotient_classical.backreacted_clock.berger_unary_d_cartan_obstruction import (
    BergerUnaryDCartanObstruction,
)


class BergerUnaryDCartanObstructionTests(unittest.TestCase):
    def test_normalized_symbol_class(self) -> None:
        payload = BergerUnaryDCartanObstruction.build().payload
        self.assertEqual(
            payload["douglis_symbol_fixture"]["cohomology_dimensions"],
            [0, 6, 6, 0],
        )
        self.assertEqual(payload["normalized_field_class"]["dual_on_representative"], "1")

    def test_positive_unary_flag_is_rejected(self) -> None:
        payload = deepcopy(BergerUnaryDCartanObstruction.build().payload)
        payload["flags"]["BERGER_UNARY_D_CARTAN_EXISTENCE_FULL_4D"] = True
        with self.assertRaises(AssertionError):
            BergerUnaryDCartanObstruction(payload).verify()


if __name__ == "__main__":
    unittest.main()
