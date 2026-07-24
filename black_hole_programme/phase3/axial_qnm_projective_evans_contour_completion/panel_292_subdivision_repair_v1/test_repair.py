from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from . import verify


class EvansPanel292SubdivisionRepairTest(unittest.TestCase):
    def test_certificate(self) -> None:
        verify.main()

    def test_full_contour_promotion_rejected(self) -> None:
        payload = json.loads(verify.CERTIFICATE.read_text())
        payload["claim_flags"]["full_contour_nonzero_certified"] = True
        with tempfile.TemporaryDirectory() as directory:
            altered = Path(directory) / "certificate.json"
            altered.write_text(json.dumps(payload))
            with patch.object(verify, "CERTIFICATE", altered):
                with self.assertRaises(AssertionError):
                    verify.main()

    def test_noncontiguous_aggregate_rejected(self) -> None:
        payload = json.loads(verify.AGGREGATE.read_text())
        payload["segments"][-1]["start"] = "585/2048"
        with tempfile.TemporaryDirectory() as directory:
            altered = Path(directory) / "aggregate.json"
            altered.write_text(json.dumps(payload))
            with patch.object(verify, "AGGREGATE", altered):
                with self.assertRaises(AssertionError):
                    verify.main()


if __name__ == "__main__":
    unittest.main()
