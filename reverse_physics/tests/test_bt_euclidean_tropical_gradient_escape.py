"""Tests for BT tropical gradient escape."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_tropical_gradient_escape import (
    CERT_PATH,
    build,
    cycle_neighbors,
    fixtures,
    tropical_data,
)
from reverse_physics.verify_bt_euclidean_tropical_gradient_escape import (
    complete_small_class_audit,
    decode,
    direct_norms,
    fixture_neighbors,
    maximal_jump_data,
    verify,
)


class ExactMathematicsTests(unittest.TestCase):
    def test_direct_fixture_norms(self) -> None:
        for row in fixtures():
            residual, gradient, gradient_sum = direct_norms(
                tuple(row["exponents"]), fixture_neighbors(row["name"])
            )
            self.assertEqual(residual, decode(row["parameter_two_residual_norm_squared"]))
            self.assertEqual(gradient, decode(row["parameter_two_gradient_norm_squared"]))
            self.assertEqual(gradient_sum, 0)

    def test_independent_leading_coefficients(self) -> None:
        for row in fixtures():
            jump, counts, leading, source = maximal_jump_data(
                tuple(row["exponents"]), fixture_neighbors(row["name"])
            )
            self.assertEqual(jump, row["tropical"]["max_edge_exponent_jump"])
            self.assertEqual(counts, row["tropical"]["max_jump_outdegrees"])
            self.assertEqual(leading, row["tropical"]["gradient_leading_coefficients"])
            self.assertEqual(source, row["tropical"]["chosen_source_vertex"])

    def test_source_coefficient_is_negative_square(self) -> None:
        row = tropical_data((0, -1, -2, -1), cycle_neighbors(4))
        source = row["chosen_source_vertex"]
        count = row["max_jump_outdegrees"][source]
        self.assertEqual(row["source_gradient_leading_coefficient"], -(count**2))
        self.assertGreater(decode(row["leading_quotient_coefficient"]), 0)

    def test_complete_small_class_audit(self) -> None:
        passed, count = complete_small_class_audit()
        self.assertTrue(passed)
        self.assertEqual(count, 621)


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
        mutate(changed)
        descriptor, path = tempfile.mkstemp(suffix=".json")
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(changed, handle)
            self.assertFalse(verify(path))
        finally:
            os.unlink(path)

    def test_mutation_exponent_profile(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_fixtures"][0]["exponents"].__setitem__(1, -2)
        )

    def test_mutation_leading_coefficient(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_fixtures"][0]["tropical"][
                "leading_quotient_coefficient"
            ].__setitem__("numerator", 0)
        )

    def test_mutation_PL_status(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["fixed_graph_PL_theorem"].__setitem__(
                "status", "OPEN"
            )
        )

    def test_mutation_uniform_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["research_disposition"].__setitem__(
                "uniform_L_scaled_PL_constant", "PROVED"
            )
        )

    def test_mutation_hminus1_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["research_disposition"].__setitem__(
                "actual_interacting_h_minus_one", "BOUNDED"
            )
        )

    def test_mutation_dependency_tag(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["dependency_tags"].append("LORENTZIAN-CAUSAL")
        )

    def test_mutation_input_hash(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["provenance"]["inputs"][0].__setitem__(
                "sha256", "0" * 64
            )
        )

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
