from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from . import verify


class EvansContourChunk254261Test(unittest.TestCase):
    def test_certificate(self) -> None:
        verify.main()

    def test_full_contour_promotion_rejected(self) -> None:
        payload = json.loads(verify.CERT.read_text())
        payload["claim_flags"]["full_contour_nonzero_certified"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "certificate.json"
            path.write_text(json.dumps(payload))
            with patch.object(verify, "CERT", path):
                with self.assertRaises(AssertionError):
                    verify.main()

    def test_noncontiguous_acceptance_rejected(self) -> None:
        payload = json.loads(verify.RAW.read_text())
        if len(payload["accepted_segments"]) < 2:
            self.skipTest("fewer than two accepted panels")
        payload["accepted_segments"][1]["panel"] += 1
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "raw.json"
            path.write_text(json.dumps(payload))
            with patch.object(verify, "RAW", path):
                with self.assertRaises(AssertionError):
                    verify.main()


if __name__ == "__main__":
    unittest.main()
