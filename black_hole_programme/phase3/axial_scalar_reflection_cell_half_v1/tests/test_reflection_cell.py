from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from .. import verify


class ReflectionCellTest(unittest.TestCase):
    def load(self) -> dict:
        return json.loads(verify.CERTIFICATE.read_text())

    def run_mutation(self, payload: dict) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "certificate.json"
            path.write_text(json.dumps(payload))
            with patch.object(verify, "CERTIFICATE", path):
                with self.assertRaises(RuntimeError):
                    verify.main()

    def test_committed_certificate(self) -> None:
        self.assertEqual(verify.main(), 0)

    def test_interval_overclaim_rejected(self) -> None:
        payload = self.load()
        payload["claim_flags"]["whole_pilot_interval_certified"] = True
        self.run_mutation(payload)

    def test_zero_lower_bound_rejected(self) -> None:
        payload = self.load()
        payload["certified_lower_bounds"]["spin_2"][
            "abs_A_out_lower"
        ] = "0"
        self.run_mutation(payload)


if __name__ == "__main__":
    unittest.main()
