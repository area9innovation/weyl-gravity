from __future__ import annotations

import json
import unittest

from lorentzian.berger_canonical_graph_q_cauchy_obstruction import OUTPUT
from lorentzian.verify_berger_canonical_graph_q_cauchy_obstruction import verify


class BergerCanonicalGraphQCauchyObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = json.loads(OUTPUT.read_text())

    def test_independent_verifier(self) -> None:
        verify()

    def test_upstream_q_remains_nilpotent(self) -> None:
        checks = self.certificate["exact_checks"]
        self.assertTrue(checks["q26_squared_zero"])
        self.assertTrue(checks["q52_squared_zero"])

    def test_stationary_candidate_is_rejected_twice(self) -> None:
        checks = self.certificate["exact_checks"]
        self.assertFalse(checks["candidate_q_Cauchy_squared_zero"])
        self.assertFalse(checks["full_A104_commutes_with_candidate_q_Cauchy"])
        self.assertEqual(
            self.certificate["defects"]["candidate_q_Cauchy_square"][
                "nonzero_sparse_entries"
            ],
            157,
        )
        self.assertEqual(
            self.certificate["defects"][
                "A104_candidate_q_Cauchy_commutator"
            ]["nonzero_sparse_entries"],
            207,
        )

    def test_claim_boundary_is_scoped(self) -> None:
        scope = self.certificate["candidate_definition"]["scope"]
        self.assertEqual(
            scope, "THIS_CANONICAL_GRAPH_LIFT_ONLY_NOT_ALL_LOCAL_COMPANION_LIFTS"
        )
        self.assertFalse(self.certificate["claim_flags"]["BERGER_Q_CAUCHY_104"])
        self.assertFalse(self.certificate["claim_flags"]["BERGER_HADAMARD_DATA"])


if __name__ == "__main__":
    unittest.main()
