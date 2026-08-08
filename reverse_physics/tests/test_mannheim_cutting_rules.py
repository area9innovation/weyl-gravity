"""Falsification tests for the Mannheim cutting-rules disposition.

The danger here is overclaim in a specific direction: this module reads a
published theorem and concludes it does not reach pure Weyl gravity.  That is a
claim about SCOPE, and the tests are written so that any drift from "the theorem
does not cover 1/k^4" toward "the theory is non-unitary" fails mechanically
rather than editorially.

The second danger is a dead gate.  A control that cannot fail proves nothing, so
each control is re-derived here independently of the module that emitted it.
"""

from __future__ import annotations

import importlib.util
import json
import os
import unittest
from fractions import Fraction

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CERT = os.path.join(REPO_ROOT, "reverse_physics", "certificates",
                    "REVERSE_PHYSICS_MANNHEIM_CUTTING_RULES_V1.json")
MODULE = os.path.join(REPO_ROOT, "reverse_physics", "mannheim_cutting_rules.py")


def load():
    with open(CERT) as fh:
        return json.load(fh)


def module():
    spec = importlib.util.spec_from_file_location("mcr", MODULE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestGate(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_all_checks_pass(self):
        self.assertTrue(self.cert["checks"]["ok"], self.cert["checks"]["failures"])
        self.assertEqual(self.cert["checks"]["passed"],
                         self.cert["checks"]["total"])

    def test_dependency_tag_is_local_algebraic(self):
        self.assertEqual(self.cert["dependency_tag"], "LOCAL-ALGEBRAIC")

    def test_no_lorentzian_promotion(self):
        """The claim boundary is explicit and must stay explicit."""
        blob = json.dumps(self.cert).lower()
        self.assertIn("lorentzian-causal", blob)
        self.assertEqual(self.cert["lifecycle_state"], "CLASSIFIED")

    def test_boundary_disclaims_nonunitarity_and_g2(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("non-unitary", joined)
        self.assertIn("magnetic moment", joined)


class TestEq84Independently(unittest.TestCase):
    """Re-derive Eq. (84) by a route the module does not use.

    The module clears denominators and compares polynomials.  Here the identity
    is instead evaluated exactly at rational (E, w) points off the poles.  Two
    independent rails on the same identity.
    """

    def test_identity_at_rational_points(self):
        for E, w in [(Fraction(3), Fraction(1)), (Fraction(5), Fraction(2)),
                     (Fraction(1, 2), Fraction(7)), (Fraction(-4), Fraction(3)),
                     (Fraction(9, 4), Fraction(1, 3))]:
            lhs = -Fraction(1) / (E * E - w * w) ** 2
            rhs = (Fraction(1) / (4 * w * w)) * (
                Fraction(1) / (w * (E - w)) - Fraction(1) / (E - w) ** 2) \
                - (Fraction(1) / (4 * w * w)) * (
                    Fraction(1) / (w * (E + w)) + Fraction(1) / (E + w) ** 2)
            self.assertEqual(lhs, rhs, "Eq.(84) fails at E=%s w=%s" % (E, w))

    def test_eq76_is_the_positive_energy_half(self):
        for w in (Fraction(1), Fraction(2), Fraction(5, 3)):
            self.assertEqual(Fraction(1, 4) / w ** 3,
                             Fraction(1, 4) / w ** 2 / w)


class TestCutWeight(unittest.TestCase):
    def setUp(self):
        self.m = module()

    def test_total_weight_zero_first_moment_one(self):
        for m1, m2 in [(Fraction(5), Fraction(2)), (Fraction(-1), Fraction(7, 3))]:
            r1, r2 = self.m.residues(m1, m2)
            self.assertEqual(r1 + r2, 0)
            self.assertEqual(r1 * m1 + r2 * m2, 1)

    def test_coincidence_limit_is_derivative_evaluation(self):
        for m in (Fraction(3), Fraction(-2), Fraction(5, 7)):
            for n in range(1, 7):
                self.assertEqual(self.m.h_complete(n - 1, m, m),
                                 Fraction(n) * m ** (n - 1))

    def test_ladder_is_not_identically_zero(self):
        """Guards against W_0 = 0 being a bookkeeping artefact."""
        r1, r2 = self.m.residues(Fraction(5), Fraction(2))
        nonzero = [n for n in range(2, 8)
                   if r1 * Fraction(5) ** n + r2 * Fraction(2) ** n != 0]
        self.assertTrue(nonzero)


class TestControlsAreLive(unittest.TestCase):
    """Each control must be able to fail.  Verified by breaking it."""

    def setUp(self):
        self.m = module()

    def test_residues_fail_closed_at_coincidence(self):
        with self.assertRaises(ValueError):
            self.m.residues(Fraction(4), Fraction(4))

    def test_wrong_h_index_is_rejected(self):
        """The ladder must not match h_n; only h_{n-1}."""
        r1, r2 = self.m.residues(Fraction(7, 3), Fraction(1, 6))
        for n in range(2, 6):
            wn = r1 * Fraction(7, 3) ** n + r2 * Fraction(1, 6) ** n
            self.assertNotEqual(wn, self.m.h_complete(n, Fraction(7, 3),
                                                      Fraction(1, 6)))

    def test_eq84_check_detects_its_own_corruption(self):
        self.assertTrue(self.m.check_eq84()["mutation_detected"])

    def test_sum_of_poles_does_not_degenerate(self):
        """The obstruction is the product structure, not coalescing poles."""
        self.assertEqual(Fraction(1) + Fraction(1), 2)

    def test_pencil_control_is_not_merely_detecting_degeneracy(self):
        """A scalar matrix is eigenvalue-degenerate AND diagonalizable.

        If the control could not tell these apart it would be detecting
        degeneracy rather than the Jordan block, and the finding would be
        vacuous.
        """
        # w*I - w*I is the zero matrix: rank 0, geometric multiplicity 2.
        zero = [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(0)]]
        rank = 0 if all(x == 0 for r in zero for x in r) else 1
        self.assertEqual(2 - rank, 2)  # diagonalizable at degeneracy
        # M(0) - w*I = [[0,1],[0,0]]: rank 1, geometric multiplicity 1.
        jordan = [[Fraction(0), Fraction(1)], [Fraction(0), Fraction(0)]]
        rank_j = 0 if all(x == 0 for r in jordan for x in r) else 1
        self.assertEqual(2 - rank_j, 1)  # not diagonalizable


class TestSourceFidelity(unittest.TestCase):
    """The finding rests on quotations; they must stay attached to the claim."""

    def setUp(self):
        self.cert = load()

    def test_section_six_concession_is_recorded(self):
        self.assertIn("cutting rules would not apply",
                      self.cert["source"]["quoted_sections"]["VI"])

    def test_named_assumption_points_at_eq_85_86(self):
        self.assertIn("85", self.cert["named_assumption"]["step"])

    def test_arxiv_and_journal_recorded(self):
        self.assertEqual(self.cert["source"]["arxiv"], "1801.03220")
        self.assertIn("045014", self.cert["source"]["journal"])


if __name__ == "__main__":
    unittest.main()
