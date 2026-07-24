from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from . import verify


class OutgoingPopulationCellTest(unittest.TestCase):
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

    def test_whole_pilot_overclaim_rejected(self) -> None:
        payload = self.load()
        payload["claim_flags"][
            "whole_pilot_interval_outgoing_population_certified"
        ] = True
        self.run_mutation(payload)

    def test_explicit_matrix_overclaim_rejected(self) -> None:
        payload = self.load()
        payload["claim_flags"]["explicit_Tplus_entries_certified"] = True
        self.run_mutation(payload)

    def test_no_exceptional_frequency_overclaim_rejected(self) -> None:
        payload = self.load()
        payload["claim_flags"][
            "absence_of_positive_real_reflection_zeros_certified"
        ] = True
        self.run_mutation(payload)

    def test_full_axis_inverse_bound_overclaim_rejected(self) -> None:
        payload = self.load()
        payload["claim_flags"][
            "uniform_full_positive_axis_inverse_bound_certified"
        ] = True
        self.run_mutation(payload)


if __name__ == "__main__":
    unittest.main()
