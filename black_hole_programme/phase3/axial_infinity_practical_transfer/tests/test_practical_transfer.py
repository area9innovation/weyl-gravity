from __future__ import annotations

import json
import unittest

from black_hole_programme.phase3.axial_infinity_practical_transfer.produce import OUTPUT
from black_hole_programme.phase3.axial_infinity_practical_transfer.verify import verify_data


class PracticalTransferTests(unittest.TestCase):
    def test_certificate(self):
        self.assertTrue(verify_data(json.loads(OUTPUT.read_text())))

    def test_claim_boundary(self):
        flags = json.loads(OUTPUT.read_text())["claim_flags"]
        self.assertTrue(flags["full_rank_R32_initializer_certified"])
        self.assertTrue(flags["direct_ivlinode_compatible"])
        self.assertFalse(flags["global_matching_certified"])
        self.assertFalse(flags["flux_certified"])


if __name__ == "__main__":
    unittest.main()
