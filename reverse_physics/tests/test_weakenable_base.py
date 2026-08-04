"""Falsification tests for the weakenable-base structure.

The claim is structural, so the tests attack the structure: monotonicity and the
invariant must actually hold, and the disclaimers must survive.
"""

from __future__ import annotations

import itertools
import json
import os
import unittest

from reverse_physics.weakenable_base import (
    ALWAYS_LIVE, AXIOMS, CERT_PATH, NOT_AN_AXIOM,
    build, lattice, live_on, monotonicity_violations, vacuous_on,
)


class TestTheLattice(unittest.TestCase):
    def setUp(self):
        self.cert = build()

    def test_all_checks_pass(self):
        self.assertTrue(self.cert["checks"]["ok"])
        self.assertEqual(self.cert["checks"]["failures"], [])

    def test_it_is_the_full_powerset(self):
        self.assertEqual(len(self.cert["lattice"]), 2 ** len(AXIOMS))

    def test_monotonicity_recomputed_independently(self):
        """A weaker base must never prove MORE.  Recomputed by brute force over
        every ordered pair, not by reusing the module's own summary."""
        names = [a["axiom"] for a in AXIOMS]
        for k in range(len(names) + 1):
            for base in itertools.combinations(names, k):
                for j in range(k):
                    for weaker in itertools.combinations(base, j):
                        self.assertTrue(
                            vacuous_on(set(weaker)) <= vacuous_on(set(base)),
                            "%s vs %s" % (weaker, base))

    def test_the_module_agrees_that_there_are_no_violations(self):
        self.assertEqual(monotonicity_violations(lattice()), [])

    def test_the_invariant_is_constant(self):
        """Content is conserved: axioms + live assumptions never changes."""
        totals = {len(r["base"]) + r["testable_count"]
                  for r in self.cert["lattice"]}
        self.assertEqual(len(totals), 1)
        self.assertEqual(totals, {len(ALWAYS_LIVE) + len(AXIOMS)})

    def test_the_extremes_behave(self):
        strongest = max(self.cert["lattice"], key=lambda r: r["axiom_count"])
        weakest = min(self.cert["lattice"], key=lambda r: r["axiom_count"])
        self.assertEqual(len(strongest["vacuous"]), len(AXIOMS))
        self.assertEqual(weakest["vacuous"], [])
        self.assertEqual(len(weakest["live"]), len(ALWAYS_LIVE) + len(AXIOMS))

    def test_weakening_strictly_increases_what_is_testable(self):
        for a in AXIOMS:
            full = {x["axiom"] for x in AXIOMS}
            self.assertGreater(len(live_on(full - {a["axiom"]})),
                               len(live_on(full)), a["axiom"])


class TestTheMigrations(unittest.TestCase):
    def setUp(self):
        self.cert = build()

    def test_all_three_are_done_with_witnesses(self):
        for a in AXIOMS:
            self.assertTrue(a["migrated"], a["axiom"])
            self.assertTrue(a["witness"], a["axiom"])
            self.assertTrue(a["certificate"], a["axiom"])

    def test_every_cited_certificate_exists(self):
        root = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
        names = {a["certificate"] for a in AXIOMS}
        names.add(NOT_AN_AXIOM["certificate"])
        for name in names:
            self.assertTrue(os.path.exists(os.path.join(
                root, "reverse_physics", "certificates", name + ".json")), name)

    def test_the_fourth_candidate_is_excluded_with_a_reason(self):
        self.assertIn("derived derivative order", NOT_AN_AXIOM["why_not"])

    def test_every_axiom_pairs_with_a_distinct_assumption(self):
        paired = [a["pairs_with"] for a in AXIOMS]
        self.assertEqual(len(paired), len(set(paired)))
        for p in paired:
            self.assertNotIn(p, ALWAYS_LIVE,
                             "an always-live assumption cannot also be a "
                             "construction constraint")


class TestItDoesNotOverclaim(unittest.TestCase):
    def setUp(self):
        with open(CERT_PATH) as fh:
            self.disk = json.load(fh)

    def test_it_denies_being_reverse_mathematics(self):
        joined = " ".join(self.disk["does_not_establish"]).lower()
        # the entry sits UNDER does_not_establish, so it reads
        # "does not establish ... reverse mathematics"
        self.assertIn("reverse mathematics", joined)
        self.assertIn("no proof system", joined)
        self.assertIn("no independence results in the logical sense", joined)
        self.assertIn("structural", joined)

    def test_it_admits_the_migration_is_only_verified_where_done(self):
        joined = " ".join(self.disk["does_not_establish"]).lower()
        self.assertIn("arbitrary migration", joined)
        self.assertIn("everywhere it matters", joined)

    def test_it_admits_the_weakest_base_is_a_description(self):
        joined = " ".join(self.disk["does_not_establish"]).lower()
        self.assertIn("a description, not a construction", joined)

    def test_it_admits_the_constraint_list_may_be_incomplete(self):
        joined = " ".join(self.disk["does_not_establish"]).lower()
        self.assertIn("complete", joined)

    def test_it_credits_the_prior_certificates(self):
        w = self.disk["where_this_stream_is"]
        self.assertIn("without announcing it", w["note"])


if __name__ == "__main__":
    unittest.main()
