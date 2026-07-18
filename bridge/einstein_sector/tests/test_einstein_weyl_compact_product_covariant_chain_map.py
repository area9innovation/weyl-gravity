"""Regression tests for the compact-product covariant relative chain map."""

from __future__ import annotations

import json
import unittest
from bridge.einstein_sector.verify_einstein_weyl_compact_product_covariant_chain_map import (
    CERTIFICATE,
    verify,
)


class CompactProductCovariantChainMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        verify(CERTIFICATE)
        cls.value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))

    def test_independent_consumer(self) -> None:
        verify(CERTIFICATE)

    def test_local_chain_map_is_certified(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(classification["single_covariant_support_local_map_reconstructed"])
        self.assertTrue(classification["full_curved_minimal_local_chain_map_certified"])
        self.assertTrue(classification["harmonic_row_selection_eliminated"])
        self.assertEqual(self.value["exact_identities"]["all_symbolic_defects"], "0")

    def test_claim_boundary_remains_fail_closed(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["noncyclic_three_form_triangle_completed"])
        self.assertFalse(classification["standard_pairing_cyclic_map_exists"])
        self.assertFalse(classification["finite_large_gauge_and_residual_endpoints_included"])
        self.assertFalse(classification["causal_nonlinear_observational_or_quantum_claim"])

    def test_support_local_formula_has_no_spectral_inverse(self) -> None:
        chain_map = self.value["chain_map"]
        self.assertTrue(chain_map["support_local"])
        self.assertFalse(chain_map["uses_inverse_laplacian_curl_frequency_or_momentum"])
        self.assertIn("3 P(E)", chain_map["metric_equation_map"])
        self.assertIn(
            "+3 B(I,J_S;nabla M)-3 B(J_S,I;nabla M)",
            chain_map["metric_equation_map"],
        )


if __name__ == "__main__":
    unittest.main()
