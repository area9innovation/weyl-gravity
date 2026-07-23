"""Fast sanity tests for the unvalidated axial connection preview."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

import mpmath as mp

from .preview import (
    FREQUENCIES,
    FUTURE_REGULAR,
    IMINUS_ROWS,
    INFINITY_ORDER,
    IPLUS_ROWS,
    extrapolated_step,
    future_horizon_outward_gram,
    hermitian_inertia,
    numeric_rank,
)


HERE = Path(__file__).resolve().parent


class PreviewSanityTests(unittest.TestCase):
    def test_exact_coefficient_extrapolator(self):
        mp.mp.dps = 60

        def rhs(_, y):
            return y

        initial = mp.matrix([[1]])
        result, defect = extrapolated_step(rhs, mp.mpf("0"), initial, mp.mpf("0.1"))
        self.assertLess(abs(result[0] - mp.exp(mp.mpf("0.1"))), mp.mpf("1e-12"))
        self.assertGreater(defect, 0)

    def test_rank_and_inertia_helpers(self):
        mp.mp.dps = 40
        matrix = mp.matrix([[1, 0], [0, 2]])
        self.assertEqual(numeric_rank(matrix, mp.mpf("1e-20")), 2)
        form = mp.matrix([[2, 0, 0], [0, -1, 0], [0, 0, 0]])
        self.assertEqual(hermitian_inertia(form, mp.mpf("1e-20"))[:3], (1, 1, 1))

    def test_future_horizon_uses_inner_boundary_orientation(self):
        state = mp.matrix([[1]])
        # i*Jhat=+1 is the increasing-r coordinate Gram.  The future horizon
        # is the inner boundary, so its outward Gram must be -1.
        jhat = mp.matrix([[-mp.j]])
        outward = future_horizon_outward_gram(state, jhat)
        self.assertEqual(outward[0, 0], -1)

    def test_basis_contract(self):
        self.assertEqual([INFINITY_ORDER[i] for i in IMINUS_ROWS],
                         ["XI0", "XI1", "EI0"])
        self.assertEqual([INFINITY_ORDER[i] for i in IPLUS_ROWS],
                         ["XI2", "XI3", "EI2"])
        self.assertEqual(list(FUTURE_REGULAR), ["XH0a", "XH0b", "EH0"])
        self.assertEqual([str(value) for value in FREQUENCIES],
                         ["1/2", "9/16", "5/8", "11/16", "3/4"])

    def test_emitted_result_is_fail_closed(self):
        path = HERE / "numeric-preview.json"
        if not path.exists():
            self.skipTest("full numerical preview has not been emitted")
        data = json.loads(path.read_text())
        self.assertEqual(data["lifecycle"], "UNVALIDATED-NUMERIC")
        self.assertFalse(data["claim_flags"]["validated_global_connection"])
        self.assertFalse(data["claim_flags"]["physical_scattering_channels_classified"])
        self.assertFalse(data["claim_flags"]["physical_ghost_established"])
        self.assertFalse(data["claim_flags"]["stability_or_pole_exclusion_established"])
        self.assertEqual(len(data["results"]), 5)
        for row in data["results"]:
            self.assertFalse(row["missing_Hminus"]["available"])


if __name__ == "__main__":
    unittest.main()
