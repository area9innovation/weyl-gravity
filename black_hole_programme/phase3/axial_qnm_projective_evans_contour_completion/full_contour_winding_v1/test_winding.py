from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from . import verify


class FullContourWindingTest(unittest.TestCase):
    def test_certificate(self) -> None:
        verify.main()

    def test_wrong_winding_rejected(self) -> None:
        payload = json.loads(verify.CERTIFICATE.read_text())
        payload["result"]["winding_number"] = 0
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "certificate.json"
            path.write_text(json.dumps(payload))
            with patch.object(verify, "CERTIFICATE", path):
                with self.assertRaises(AssertionError):
                    verify.main()

    def test_open_coverage_rejected(self) -> None:
        payload = json.loads(verify.LEDGER.read_text())
        payload["summary"]["coverage_stop"] = "1023/1024"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "phase-ledger.json"
            path.write_text(json.dumps(payload))
            with patch.object(verify, "LEDGER", path):
                with self.assertRaises(AssertionError):
                    verify.main()

    def test_false_tangent_promotion_rejected(self) -> None:
        payload = json.loads(verify.CERTIFICATE.read_text())
        payload["claim_flags"]["intrinsic_tangent_selector_certified"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "certificate.json"
            path.write_text(json.dumps(payload))
            with patch.object(verify, "CERTIFICATE", path):
                with self.assertRaises(AssertionError):
                    verify.main()


if __name__ == "__main__":
    unittest.main()

