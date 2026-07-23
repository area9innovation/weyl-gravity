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
        self.assertTrue(data["claim_flags"]["required_first_cell_diagonal_rank_certified"])
        self.assertTrue(data["structured_lower_lift_result"]["all_1792_local_krawczyk_solves_closed"])
        self.assertGreater(data["structured_lower_lift_result"]["maximum_interval_width"], 1e7)
        self.assertFalse(data["claim_flags"]["global_connection_certified"])
        self.assertFalse(data["claim_flags"]["radial_current_conservation_certified"])
        self.assertFalse(data["claim_flags"]["endpoint_flux_or_scattering_claim"])


if __name__ == "__main__":
    unittest.main()
