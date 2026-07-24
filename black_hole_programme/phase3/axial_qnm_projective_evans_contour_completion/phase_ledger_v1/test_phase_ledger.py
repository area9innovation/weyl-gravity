from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from . import verify


class EvansPhaseLedgerTest(unittest.TestCase):
    def test_certificate(self) -> None:
        verify.main()

    def test_winding_promotion_rejected(self) -> None:
        payload = json.loads(verify.LEDGER.read_text())
        payload["claim_flags"]["winding_number_certified"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "phase-ledger.json"
            path.write_text(json.dumps(payload))
            with patch.object(verify, "LEDGER", path):
                with self.assertRaises(AssertionError):
                    verify.main()

    def test_nonpositive_separator_rejected(self) -> None:
        payload = json.loads(verify.LEDGER.read_text())
        payload["segments"][0]["separator"]["integer_vector"] = [0, 0]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "phase-ledger.json"
            path.write_text(json.dumps(payload))
            with patch.object(verify, "LEDGER", path):
                with self.assertRaises((AssertionError, ZeroDivisionError)):
                    verify.main()


if __name__ == "__main__":
    unittest.main()
