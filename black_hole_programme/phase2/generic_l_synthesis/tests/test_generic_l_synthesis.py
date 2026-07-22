from __future__ import annotations

import json
import unittest
from pathlib import Path

import sympy as sp

from ..verify import HERE, load_q21, replay_triangular_counts


class TestGenericLSynthesis(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = json.loads((HERE / "certificate.json").read_text())

    def test_joint_disposition_is_scoped(self) -> None:
        joint = self.certificate["joint_disposition"]
        self.assertEqual(
            joint["einstein_only_selection"],
            "FALSE_IN_THE_DECLARED_FORMAL_RADIAL_CLASS_BY_AXIAL_X0",
        )
        self.assertIn("horizon-to-infinity matching", self.certificate["does_not_establish"])
        self.assertIn("axial X2 disposition", self.certificate["does_not_establish"])

    def test_q21_fixture_variable_correction(self) -> None:
        lam, x, q21 = load_q21()
        fixture = self.certificate["q21_exceptional_frequency_count"]["legacy_fixture"]
        correct = sp.factor(q21.subs({lam: 6, x: sp.Rational(9, 25)}))
        prior = sp.factor(q21.subs({lam: 6, x: sp.Rational(81, 625)}))
        self.assertEqual(sp.sstr(correct), fixture["Q21_value"])
        self.assertEqual(
            sp.sstr(prior), fixture["evaluator_variable_correction"]["prior_value"]
        )
        self.assertNotEqual(correct, prior)

    def test_exact_triangular_root_counts(self) -> None:
        counts = replay_triangular_counts()
        self.assertEqual(counts[2], 0)
        self.assertEqual(counts[3], 3)
        self.assertTrue(all(counts[ell] == 1 for ell in range(4, 11)))
        self.assertTrue(all(counts[ell] == 3 for ell in range(11, 41)))
        self.assertEqual(counts[41], 1)

    def test_evidence_types_are_distinct(self) -> None:
        ledger = self.certificate["q21_exceptional_frequency_count"]
        self.assertEqual(ledger["count_evidence_type"], "EXACT_RATIONAL_STURM")
        self.assertEqual(
            ledger["discriminant_factorization"]["root_isolation_evidence_type"],
            "CERTIFIED_INTERVAL_NUMERIC",
        )

    def test_paper_request_is_request_only(self) -> None:
        request_path = HERE.parents[2] / "planning/paper-coverage/phase2-black-hole-paper-correction-request.json"
        request = json.loads(request_path.read_text())
        self.assertEqual(request["status"], "REQUEST_ONLY_NO_PAPER_EDIT")
        self.assertIn("formal radial integrability to horizon-to-infinity admissibility", request["forbidden_promotions"])


if __name__ == "__main__":
    unittest.main()
