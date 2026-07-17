from __future__ import annotations

import copy
import json
import unittest

from d_quotient_classical.backreacted_clock.paper_09_nonlinear_frozen_k_generator_signoff import build_payload
from d_quotient_classical.backreacted_clock.verify_paper_09_nonlinear_frozen_k_generator_signoff import (
    CERTIFICATE,
    VerificationError,
    mutations,
    verify_payload,
)


class FrozenPaper09NonlinearSignoffTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))

    def test_producer(self) -> None:
        self.assertEqual(build_payload(), self.payload)

    def test_independent_verifier(self) -> None:
        verify_payload(self.payload)

    def test_mutations(self) -> None:
        mutations(self.payload)

    def test_maxwell_promotion_rejected(self) -> None:
        mutant = copy.deepcopy(self.payload)
        mutant["flags"]["MAXWELL_MAIN_THEOREM_INCLUDED"] = True
        with self.assertRaises(VerificationError):
            verify_payload(mutant, files=False)

    def test_affine_D_promotion_rejected(self) -> None:
        mutant = copy.deepcopy(self.payload)
        mutant["flags"]["RAW_D_CARTAN_CERTIFIED"] = True
        with self.assertRaises(VerificationError):
            verify_payload(mutant, files=False)


if __name__ == "__main__":
    unittest.main()
