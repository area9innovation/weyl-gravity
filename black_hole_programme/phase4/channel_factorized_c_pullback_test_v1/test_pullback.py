"""Mutation tests for the channel-factorized C pullback theorem."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from .exact import criterion_fixture
from .verify import HERE, verify_path


class PullbackCriterionTests(unittest.TestCase):
    def test_positive_fixture(self) -> None:
        fixture = criterion_fixture("positive")
        self.assertTrue(fixture["L_G_self_adjoint"])
        self.assertTrue(fixture["L_diagonalizable"])
        self.assertEqual(fixture["H0_inertia"], (3, 0, 0))
        self.assertEqual(fixture["KH_C_inertia"], (3, 0, 0))
        self.assertEqual(fixture["Kplus_C_inertia"], (3, 0, 0))

    def test_negative_eigenvalue_rejected(self) -> None:
        fixture = criterion_fixture("negative_eigenvalue")
        self.assertNotEqual(fixture["KH_C_inertia"], (3, 0, 0))

    def test_nonreal_pair_rejected(self) -> None:
        fixture = criterion_fixture("nonreal_pair")
        self.assertTrue(fixture["L_G_self_adjoint"])
        self.assertTrue(any("I" in value for value in fixture["spectrum"]))

    def test_jordan_block_rejected(self) -> None:
        fixture = criterion_fixture("jordan")
        self.assertTrue(fixture["L_G_self_adjoint"])
        self.assertFalse(fixture["L_diagonalizable"])

    def _verify_mutation_rejected(self, mutate) -> None:
        certificate = json.loads((HERE / "certificate.json").read_text())
        mutated = copy.deepcopy(certificate)
        mutate(mutated)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutated.json"
            path.write_text(json.dumps(mutated))
            with self.assertRaises(AssertionError):
                verify_path(path)

    def test_missing_tminus_promotion_rejected(self) -> None:
        self._verify_mutation_rejected(
            lambda cert: cert["claim_flags"].__setitem__(
                "physical_full_typed_Tminus_available", True
            )
        )

    def test_product_bound_mutation_rejected(self) -> None:
        self._verify_mutation_rejected(
            lambda cert: cert["physical_audit"][
                "partial_determinant_information"
            ].__setitem__("cell_bound", "0<det(L_H)<1")
        )

    def test_import_hash_mutation_rejected(self) -> None:
        self._verify_mutation_rejected(
            lambda cert: cert["imports"]["horizon_gram"].__setitem__(
                "sha256", "0" * 64
            )
        )


if __name__ == "__main__":
    unittest.main()
