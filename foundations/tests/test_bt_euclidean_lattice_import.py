from __future__ import annotations

import copy
import unittest

from foundations.build_bt_euclidean_lattice_import import build
from foundations.check_bt_euclidean_lattice_import import check
from foundations.verify_bt_euclidean_lattice_import import verify


class BTEuclideanLatticeImportTests(unittest.TestCase):
    def test_exact_capability_partition(self):
        value = build()
        roles = [item["evidence_role"] for item in value["capability_decisions"]]
        self.assertEqual(5, roles.count("DIRECT_LOCAL"))
        self.assertEqual(1, roles.count("SUPPORTING"))

    def test_independent_checker(self):
        self.assertEqual([], check(build())[0])

    def test_continuum_promotion_fails(self):
        value = copy.deepcopy(build())
        item = next(item for item in value["capability_decisions"] if item["coordinate"]["obligation"] == "RECONSTRUCTION_LIMITS")
        item["status_change"] = True
        self.assertIn("supporting-only reconstruction decision", check(value)[0])

    def test_precision_overclaim_fails(self):
        value = copy.deepcopy(build())
        value["numerical_reproducibility_records"][0]["status"] = "PRECISION_MATCH"
        self.assertIn("four-sigma pass and two-sigma non-pass", check(value)[0])

    def test_interface_identity_fails(self):
        value = copy.deepcopy(build())
        value["carrier_interface"]["relation"] = "IDENTICAL_OBJECT"
        self.assertIn("carrier interface classification", check(value)[0])

    def test_verifier(self):
        self.assertEqual([], verify()[0])


if __name__ == "__main__":
    unittest.main()
