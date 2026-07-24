"""Mutation tests for the endpoint partial-jet frame verifier."""
from __future__ import annotations

import copy
import json
import unittest

from .produce import OUTPUT
from .verify import verify_document


class EndpointFrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = json.loads(OUTPUT.read_text())

    def reject(self, mutate) -> None:
        changed = copy.deepcopy(self.doc)
        mutate(changed)
        self.assertTrue(verify_document(changed))

    def test_certificate(self) -> None:
        self.assertEqual(verify_document(copy.deepcopy(self.doc)), [])

    def test_Iplus_sign_mutation(self) -> None:
        self.reject(lambda d: d["endpoint_frames"]["Iplus"]["spin_one_quotient_amplitudes_XI2_XI3"].__setitem__(1, "2*I*omega"))

    def test_EI2_amplitude_mutation(self) -> None:
        self.reject(lambda d: d["endpoint_frames"]["Iplus"]["scalar_amplitudes_R_S_E"].__setitem__(2, "1"))

    def test_K_promotion(self) -> None:
        self.reject(lambda d: d["endpoint_frame_derivative_law"].__setitem__("K_H_computed", True))

    def test_Tplus_promotion(self) -> None:
        self.reject(lambda d: d["claim_flags"].__setitem__("T_plus_recovered", True))

    def test_K_lower_left_mutation(self) -> None:
        self.reject(lambda d: d["endpoint_frame_derivative_law"].__setitem__("K_allowed_shape", [["k_2","h"],["x","0"]]))

    def test_hash_mutation(self) -> None:
        self.reject(lambda d: d["imports"]["complete_reconstruction"].__setitem__("sha256", "0"*64))


if __name__ == "__main__":
    unittest.main()
