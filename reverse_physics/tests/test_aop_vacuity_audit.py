"""Falsification tests for the audit of an external framework.

Auditing someone else's work is where overclaim is cheapest and most damaging,
so these tests are aimed at the framing as much as the arithmetic.
"""

from __future__ import annotations

import json
import os
import unittest
from math import comb

from reverse_physics.aop_vacuity_audit import (
    ASSUMPTIONS, CERT_PATH, FLAGS, LIVE, SOURCES, VACUOUS,
    build, closedness_conditions,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))


class TestTheArithmetic(unittest.TestCase):
    def test_closedness_vanishes_only_at_one_degree_of_freedom(self):
        self.assertEqual(closedness_conditions(1), 0)
        for n in range(2, 8):
            self.assertGreater(closedness_conditions(n), 0, "n=%d" % n)

    def test_it_is_the_three_form_dimension(self):
        """Recomputed by binomial directly, not by reusing the module."""
        for n in range(1, 8):
            self.assertEqual(closedness_conditions(n), comb(2 * n, 3))

    def test_the_reason_is_dimensional(self):
        """A three-form needs three independent directions."""
        self.assertEqual(comb(2, 3), 0)
        self.assertEqual(comb(4, 3), 4)


class TestTheAuditIsFair(unittest.TestCase):
    def setUp(self):
        self.cert = build()

    def test_all_checks_pass(self):
        self.assertTrue(self.cert["checks"]["ok"])
        self.assertEqual(self.cert["checks"]["failures"], [])

    def test_no_assumption_of_theirs_is_marked_vacuous(self):
        """The flags are about DERIVED STEPS.  Marking one of their stated
        assumptions vacuous would be a much stronger claim and is not made."""
        for a in ASSUMPTIONS:
            self.assertNotEqual(a["verdict"], VACUOUS, a["name"])

    def test_every_live_assumption_credits_its_witness(self):
        for a in ASSUMPTIONS:
            if a["verdict"] == LIVE:
                self.assertTrue(a["witness"], a["name"])
                self.assertTrue(a["witness_supplied_by"], a["name"])

    def test_the_witnesses_are_mostly_theirs(self):
        """Two of the three witnesses are supplied by the authors themselves;
        if that ever stopped being true the framing would need rewriting."""
        theirs = [a for a in ASSUMPTIONS
                  if "authors" in (a.get("witness_supplied_by") or "")]
        self.assertGreaterEqual(len(theirs), 2)

    def test_every_flag_says_where_it_becomes_live(self):
        """A flag with no live regime is an accusation, not an observation."""
        for f in FLAGS:
            self.assertTrue(f["becomes_live_at"], f["id"])
            self.assertTrue(f["why"], f["id"])


class TestItDoesNotOverclaim(unittest.TestCase):
    def setUp(self):
        with open(CERT_PATH) as fh:
            self.disk = json.load(fh)

    def test_it_disclaims_finding_any_error(self):
        joined = " ".join(self.disk["does_not_establish"]).lower()
        self.assertIn("any error in their results", joined)
        self.assertIn("scope observation", joined)

    def test_it_disclaims_completeness(self):
        joined = " ".join(self.disk["does_not_establish"]).lower()
        self.assertIn("not audited here at all", joined)

    def test_it_says_closedness_does_not_fail(self):
        joined = " ".join(self.disk["does_not_establish"]).lower()
        self.assertIn("does no work at one degree of freedom", joined)

    def test_the_framing_is_recorded_as_a_credit(self):
        self.assertIn("credit to them", self.disk["framing"]["headline"])
        self.assertIn("rhetorical device",
                      self.disk["framing"]["why_run_it_at_all"])

    def test_sources_are_resolvable_urls(self):
        for s in SOURCES:
            self.assertTrue(s["url"].startswith("https://"), s["what"])
            self.assertTrue(s["where"], s["what"])

    def test_the_note_declares_the_book_was_read(self):
        with open(os.path.join(REPO_ROOT, "reverse_physics", "reports",
                               "AOP-CONNECTION.md")) as fh:
            text = fh.read()
        self.assertIn("and the book", text)
        self.assertNotIn("have **not** read the book", text)
        self.assertIn("2.1e", text)


if __name__ == "__main__":
    unittest.main()
