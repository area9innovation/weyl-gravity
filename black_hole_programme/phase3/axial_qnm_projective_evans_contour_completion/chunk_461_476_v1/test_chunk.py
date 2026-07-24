from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from . import verify
from ..continuation import verify as verify_config


class EvansContourChunk461476Test(unittest.TestCase):
    def test_certificate(self) -> None:
        verify.main()

    def test_full_contour_promotion_rejected(self) -> None:
        payload = json.loads(verify.CONFIG.certificate.read_text())
        payload["claim_flags"]["full_contour_nonzero_certified"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "certificate.json"
            path.write_text(json.dumps(payload))
            with self.assertRaises(AssertionError):
                verify_config(verify.CONFIG, certificate_path=path)

    def test_noncontiguous_acceptance_rejected(self) -> None:
        payload = json.loads(verify.CONFIG.raw.read_text())
        if len(payload["accepted_segments"]) < 2:
            self.skipTest("fewer than two accepted panels")
        payload["accepted_segments"][1]["panel"] += 1
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "raw.json"
            path.write_text(json.dumps(payload))
            with self.assertRaises(AssertionError):
                verify_config(verify.CONFIG, raw_path=path)


if __name__ == "__main__":
    unittest.main()
