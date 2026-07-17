from __future__ import annotations

import copy
import json
import unittest

from d_quotient_classical.backreacted_clock.paper_09_nonlinear_k_generator_signoff import build_payload
from d_quotient_classical.backreacted_clock.verify_paper_09_nonlinear_k_generator_signoff import (
    CERTIFICATE,
    VerificationError,
    run_mutation_tests,
    verify_payload,
)


class Paper09NonlinearKGeneratorSignoffTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))

    def test_authoritative_signoff(self) -> None:
        verify_payload(self.payload, check_files=True)

    def test_deterministic_producer(self) -> None:
        self.assertEqual(build_payload(), self.payload)

    def test_mutation_rail(self) -> None:
        run_mutation_tests(self.payload)

    def test_raw_D_promotion_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.payload)
        mutant["flags"]["RAW_D_CARTAN_CERTIFIED"] = True
        with self.assertRaises(VerificationError):
            verify_payload(mutant, check_files=False)

    def test_all_orders_promotion_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.payload)
        mutant["flags"]["ALL_ORDERS_CARTAN_CERTIFIED"] = True
        with self.assertRaises(VerificationError):
            verify_payload(mutant, check_files=False)

    def test_generator_rename_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.payload)
        mutant["review_scope"]["certified_generator"] = "D=partial_t"
        with self.assertRaises(VerificationError):
            verify_payload(mutant, check_files=False)


if __name__ == "__main__":
    unittest.main()
