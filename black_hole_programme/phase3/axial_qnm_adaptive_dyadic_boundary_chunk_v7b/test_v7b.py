from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from . import verify


class AdaptiveBoundaryV7bTest(unittest.TestCase):
    def test_certificate(self) -> None:
        verify.main()

    def test_ep2_promotion_rejected(self) -> None:
        payload = json.loads(verify.CERT.read_text())
        payload["claim_flags"]["defective_fibre_or_EP2_certified"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "certificate.json"
            path.write_text(json.dumps(payload))
            with patch.object(verify, "CERT", path):
                with self.assertRaises(AssertionError):
                    verify.main()

    def test_child_identity_rejected(self) -> None:
        payload = json.loads(verify.RAW.read_text())
        payload["requested_child_segments"] = ["210/1024", "211/1024"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "raw.json"
            path.write_text(json.dumps(payload))
            with patch.object(verify, "RAW", path):
                with self.assertRaises(AssertionError):
                    verify.main()


if __name__ == "__main__":
    unittest.main()
