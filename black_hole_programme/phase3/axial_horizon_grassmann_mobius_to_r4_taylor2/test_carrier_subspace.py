import json
from pathlib import Path
import unittest

import sympy as sp

from . import carrier_subspace


class CarrierSubspaceWitnessTests(unittest.TestCase):
    def test_committed_witness_reproduces(self):
        committed = json.loads(carrier_subspace.OUTPUT.read_text())
        self.assertEqual(carrier_subspace.produce(), committed)

    def test_all_non_invariance_determinants_are_exactly_nonzero(self):
        payload = json.loads(carrier_subspace.OUTPUT.read_text())
        for value in payload["determinants"].values():
            self.assertNotEqual(sp.sympify(value), 0)

    def test_witness_is_fail_closed_about_boundary_rank(self):
        payload = json.loads(carrier_subspace.OUTPUT.read_text())
        self.assertIn(
            "the rank of any boundary projection",
            payload["does_not_establish"],
        )


if __name__ == "__main__":
    unittest.main()
