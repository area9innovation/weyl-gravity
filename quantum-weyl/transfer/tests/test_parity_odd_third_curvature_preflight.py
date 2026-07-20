from __future__ import annotations

from copy import deepcopy
import unittest

from transfer import parity_odd_third_curvature_preflight as producer
from transfer import verify_parity_odd_third_curvature_preflight as verifier


class ParityOddThirdCurvaturePreflightTest(unittest.TestCase):
    def test_stored_certificate_is_current(self) -> None:
        self.assertEqual(verifier.verify(), producer.build())

    def test_dimension_promotion_is_rejected(self) -> None:
        mutation = producer.build()
        mutation["decision"]["quotient_dimension"] = 10
        with self.assertRaises(Exception):
            producer.validate(mutation)

    def test_even_dualization_promotion_is_rejected(self) -> None:
        mutation = producer.build()
        mutation["decision"]["even_basis_dualization_promoted"] = True
        with self.assertRaises(Exception):
            producer.validate(mutation)

    def test_sampling_promotion_is_rejected(self) -> None:
        mutation = producer.build()
        mutation["decision"]["sampling_used"] = True
        with self.assertRaises(Exception):
            producer.validate(mutation)

    def test_completeness_flag_is_rejected(self) -> None:
        mutation = producer.build()
        mutation["claim_flags"][
            "PARITY_ODD_DERIVATIVE_CARRIER_MANIFEST_COMPLETE"
        ] = True
        with self.assertRaises(Exception):
            producer.validate(mutation)

    def test_missing_syzygy_row_is_rejected(self) -> None:
        mutation = deepcopy(producer.build())
        mutation["first_missing_operation"]["quotient_by"].pop()
        with self.assertRaises(Exception):
            producer.validate(mutation)


if __name__ == "__main__":
    unittest.main()
