"""Tests for the BT pair-block g4 topology reduction."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_pair_block_response_g4_topology_reduction import (
    CERT_PATH,
    build,
    topology_rows,
)
from reverse_physics.verify_bt_euclidean_pair_block_response_g4_topology_reduction import (
    independent_counts,
    verify,
)


class ExactTopologyTests(unittest.TestCase):
    def test_exact_counts(self) -> None:
        rows = topology_rows()
        self.assertEqual(sum(row["raw_pairings"] for row in rows), 1226)
        self.assertEqual(sum(row["connected_pairings"] for row in rows), 1046)
        self.assertEqual(sum(row["connected_topology_count"] for row in rows), 27)
        self.assertEqual(sum(row["momentum_admissible_topology_count"] for row in rows), 6)

    def test_nonimporting_enumerator_agrees(self) -> None:
        counts, multiplicities, per_row = independent_counts()
        self.assertEqual(dict(counts), {"raw": 1226, "connected": 1046, "topologies": 27, "live": 6})
        self.assertEqual(multiplicities, [1, 1, 3, 6, 12, 36])
        self.assertEqual([len(row) for row in per_row], [3, 1, 1, 1, 0, 0, 0])

    def test_all_Dm1_rows_vanish(self) -> None:
        self.assertTrue(all(row["momentum_admissible_topology_count"] == 0 for row in topology_rows()[4:]))


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

    def test_mutation_live_count(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert["enumeration"].__setitem__("momentum_admissible_topologies", 7))

    def test_mutation_multiplicity(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert["six_term_fourier_reduction"]["live_topologies"][5].__setitem__("pairing_multiplicity", 35))

    def test_mutation_coefficient_promotion(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert["method_disposition"].__setitem__("full_gibbs_L6_g4_coefficient", "COEFFICIENT_COMPUTED"))

    def test_mutation_dependency_boundary(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert["dependency_tags"].append("LORENTZIAN-CAUSAL"))

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
