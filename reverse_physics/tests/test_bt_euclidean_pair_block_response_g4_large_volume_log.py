"""Tests for the BT pair-block g4 large-volume logarithm."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_pair_block_response_g4_large_volume_log import (
    CERT_PATH,
    build,
    gamma3_identity,
    gamma4_identity,
)
from reverse_physics.verify_bt_euclidean_pair_block_response_g4_large_volume_log import (
    gamma3_grid_identity,
    gamma4_grid_identity,
    verify,
)


class AlgebraTests(unittest.TestCase):
    def test_producer_polynomial_identities(self) -> None:
        self.assertTrue(gamma3_identity())
        self.assertTrue(gamma4_identity())

    def test_independent_interpolation_identities(self) -> None:
        self.assertTrue(gamma3_grid_identity())
        self.assertTrue(gamma4_grid_identity())


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def test_deterministic_builder(self) -> None:
        self.assertEqual(build(), self.certificate)

    def test_independent_verifier(self) -> None:
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

    def test_mutation_log_sign(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["leading_log_theorem"].__setitem__("sign", "STRICTLY_POSITIVE")
        )

    def test_mutation_log_prefactor(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["leading_log_theorem"]["rational_prefactor_of_W4_over_pi_squared"].__setitem__("numerator", 3)
        )

    def test_mutation_second_log_topology(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["topology_disposition"][0].__setitem__("large_volume_disposition", "UNIQUE_NEGATIVE_LOG")
        )

    def test_mutation_fixed_coupling_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__("fixed_coupling_pair_response", "NEGATIVE")
        )

    def test_mutation_hminus1_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__("actual_interacting_h_minus_one", "DIVERGES")
        )

    def test_mutation_lorentzian_tag(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert["dependency_tags"].append("LORENTZIAN-CAUSAL"))

    def test_mutation_l6_tadpole(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["tadpole_reduction"]["exact_L6_C"].__setitem__("numerator", 1)
        )

    def test_mutation_input_hash(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["provenance"]["inputs"][0].__setitem__("sha256", "0" * 64)
        )

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
