"""Tests for the BT pair-block g4 L6 numerical preflight."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_pair_block_response_g4_l6_preflight import (
    CERT_PATH,
    build,
)
from reverse_physics.verify_bt_euclidean_pair_block_response_g4_l6_preflight import (
    fast_compiled_calibration,
    verify,
)


class PreflightTests(unittest.TestCase):
    def test_fast_compiled_one_loop_calibration(self) -> None:
        self.assertTrue(fast_compiled_calibration())


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def test_deterministic_builder(self) -> None:
        self.assertEqual(build(), self.certificate)

    def test_independent_data_verifier(self) -> None:
        self.assertTrue(verify(CERT_PATH))

    def assert_mutation_rejected(self, mutate) -> None:
        changed = copy.deepcopy(self.certificate)
        descriptor, path = tempfile.mkstemp(suffix=".json")
        try:
            mutate(changed)
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(changed, handle)
            self.assertFalse(verify(path))
        finally:
            os.unlink(path)

    def test_mutation_sum(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert["six_term_result"].__setitem__("sum", -1e-3))

    def test_mutation_exact_promotion(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert["method_disposition"].__setitem__("exact_or_rigorous_L6_g4_sign", "POSITIVE"))

    def test_mutation_lifecycle_promotion(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert["method_disposition"].__setitem__("coefficient_computed_lifecycle", "COEFFICIENT_COMPUTED"))

    def test_mutation_dependency_boundary(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert["dependency_tags"].append("LORENTZIAN-CAUSAL"))

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
