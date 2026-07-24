"""Mutation tests for the exact axial threshold certificate."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .verify import HERE, verify


class ThresholdCertificateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads((HERE / "certificate.json").read_text())

    def verify_mutation_fails(self, mutation) -> None:
        changed = json.loads(json.dumps(self.data))
        mutation(changed)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "certificate.json"
            path.write_text(json.dumps(changed))
            with self.assertRaises(AssertionError):
                verify(path)

    def test_checked_certificate(self) -> None:
        verify(HERE / "certificate.json")

    def test_zero_mode_mutation_fails(self) -> None:
        self.verify_mutation_fails(
            lambda data: data["zero_modes"].__setitem__("spin_two", "r**3/7")
        )

    def test_cocycle_mutation_fails(self) -> None:
        self.verify_mutation_fails(
            lambda data: data["projective_cocycle"].__setitem__(
                "threshold_decomposition", "0"
            )
        )

    def test_promotion_ledger_mutation_fails(self) -> None:
        self.verify_mutation_fails(
            lambda data: data["does_not_establish"].remove(
                "a punctured positive-real interval on which T_plus is invertible"
            )
        )


if __name__ == "__main__":
    unittest.main()
