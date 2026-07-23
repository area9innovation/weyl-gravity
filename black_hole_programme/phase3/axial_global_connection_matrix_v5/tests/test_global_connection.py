from __future__ import annotations

import json
import unittest

from black_hole_programme.phase3.axial_global_connection_matrix_v5.produce import OUTPUT
from black_hole_programme.phase3.axial_global_connection_matrix_v5.verify import verify_data


class GlobalConnectionShortfallTests(unittest.TestCase):
    def test_certificate(self):
        self.assertTrue(verify_data(json.loads(OUTPUT.read_text())))

    def test_fail_closed_boundary(self):
        data = json.loads(OUTPUT.read_text())
        self.assertEqual(data["stop_condition_disposition"], "SHORTFALL")
        self.assertTrue(data["table_backed_runtime_gate"]["coefficient_table_materialized"])
        self.assertFalse(data["table_backed_runtime_gate"]["carrier_flow_returned_within_20_minutes"])
        self.assertFalse(data["table_backed_runtime_gate"]["mathematical_refusal_reached"])
        self.assertEqual(data["chunk_successor"]["radial_chunks"], 28)
        self.assertEqual(data["chunk_successor"]["panels_per_chunk"], 64)
        self.assertFalse(data["claim_flags"]["global_connection_certified"])
        self.assertFalse(data["claim_flags"]["radial_current_conservation_certified"])
        self.assertFalse(data["claim_flags"]["endpoint_flux_or_scattering_claim"])


if __name__ == "__main__":
    unittest.main()
