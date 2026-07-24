"""Scoped tests for the transport-free outgoing-defect preflight."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from .verify import verify


HERE = Path(__file__).resolve().parent


class TransportFreePreflightTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads((HERE / "certificate.json").read_text())

    def test_independent_verifier(self) -> None:
        verify(self.document)

    def test_abstract_embedding_activated(self) -> None:
        self.assertTrue(
            self.document["claim_flags"][
                "raw_one_sided_pseudo_isometric_embedding_certified"
            ]
        )

    def test_determinant_fail_closed(self) -> None:
        self.assertFalse(
            self.document["claim_flags"]["det_O_nonzero_certified"]
        )

    def test_outgoing_rank_fail_closed(self) -> None:
        self.assertFalse(
            self.document["claim_flags"][
                "Tplus_rank_or_outgoing_population_certified"
            ]
        )

    def test_orientation(self) -> None:
        identity = self.document["tier_A_transport_free_determinant"][
            "exact_audit"
        ]["oriented_forms"]["one_sided_identity"]
        self.assertEqual(
            identity,
            "Hout+Tplus^dagger*Gplus*Tplus"
            "-Tminus^dagger*Gminus*Tminus=0",
        )


if __name__ == "__main__":
    unittest.main()
