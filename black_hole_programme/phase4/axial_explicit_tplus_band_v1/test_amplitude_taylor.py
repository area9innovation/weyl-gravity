#!/usr/bin/env python3
"""Scoped tests and a mutation rejection for the amplitude shortfall."""

from __future__ import annotations

import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from . import produce_amplitude_summary as producer
from . import verify_amplitude_taylor as verifier


class AmplitudeTaylorTests(unittest.TestCase):
    def test_fail_closed_certificate(self) -> None:
        document = json.loads(producer.CERTIFICATE.read_text())
        self.assertEqual(
            document["status"], "FAIL_CLOSED_REPRESENTATION_WRAPPING"
        )
        self.assertFalse(
            document["claim_flags"]["explicit_Tplus_certified"]
        )
        self.assertFalse(
            document["validated_result"]["terminal_rank_certified"]
        )

    def test_independent_audit(self) -> None:
        verifier.audit()

    def test_mutated_certificate_is_rejected(self) -> None:
        document = json.loads(producer.CERTIFICATE.read_text())
        document["claim_flags"]["explicit_Tplus_certified"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutated.json"
            path.write_text(json.dumps(document))
            with patch.object(producer, "CERTIFICATE", path):
                with self.assertRaises(AssertionError):
                    verifier.audit()


if __name__ == "__main__":
    unittest.main()
