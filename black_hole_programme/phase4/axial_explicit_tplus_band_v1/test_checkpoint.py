"""Mutation tests for the Phase-4 outgoing checkpoint."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .verify import HERE, verify


class OutgoingCheckpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads((HERE / "certificate.json").read_text())

    def mutate_fails(self, mutate) -> None:
        data = json.loads(json.dumps(self.data))
        mutate(data)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "certificate.json"
            path.write_text(json.dumps(data))
            with self.assertRaises(AssertionError):
                verify(path)

    def test_certificate(self) -> None:
        verify(HERE / "certificate.json")

    def test_predecessor_hash_mutation(self) -> None:
        self.mutate_fails(
            lambda data: data["imports"]["checkpoint"].__setitem__(
                "sha256", "0" * 64
            )
        )

    def test_tplus_promotion_mutation(self) -> None:
        self.mutate_fails(
            lambda data: data["claim_flags"].__setitem__(
                "explicit_Tplus_certified", True
            )
        )


if __name__ == "__main__":
    unittest.main()
