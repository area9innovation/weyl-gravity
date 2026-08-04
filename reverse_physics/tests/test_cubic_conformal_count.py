"""Falsification tests for the cubic conformal invariant count.

The computation itself lives in Forge (tango), not here.  These tests guard the
certificate against the two ways a result like this rots: a count quietly drifting
away from what the rail returned, and a boundary quietly widening into a claim it
was never entitled to.
"""

from __future__ import annotations

import json
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CERT = os.path.join(REPO_ROOT, "reverse_physics", "certificates",
                    "REVERSE_PHYSICS_CUBIC_CONFORMAL_COUNT_V1.json")
D6_CERT = os.path.join(REPO_ROOT, "reverse_physics", "certificates",
                       "REVERSE_PHYSICS_WEYL_ACTION_D6_V1.json")
REPORT = os.path.join(REPO_ROOT, "reverse_physics", "reports",
                      "cubic-conformal-count.md")


def load(path=CERT):
    with open(path) as fh:
        return json.load(fh)


class TestTheNumbers(unittest.TestCase):
    def setUp(self):
        self.cert = load()
        self.by_dim = {r["dimension"]: r for r in self.cert["results"]}

    def test_all_checks_pass(self):
        self.assertTrue(self.cert["checks"]["ok"])
        self.assertEqual(self.cert["checks"]["failures"], [])
        self.assertEqual(self.cert["checks"]["passed"],
                         self.cert["checks"]["total"])

    def test_the_three_dimensions_are_present(self):
        self.assertEqual(set(self.by_dim), {4, 5, 6})

    def test_every_row_is_computed_not_cited(self):
        for d, row in self.by_dim.items():
            self.assertEqual(row["status"], "COMPUTED", d)

    def test_the_counting_identity_holds_in_every_row(self):
        """invariant dim = rank(VALUES) - rank(VARIATIONS), row by row."""
        for d, row in self.by_dim.items():
            self.assertEqual(
                row["cubic_curvature_span"] - row["variation_rank"],
                row["pointwise_conformal_invariants_cubic"], d)

    def test_the_span_grows_with_dimension(self):
        spans = [self.by_dim[d]["cubic_curvature_span"] for d in (4, 5, 6)]
        self.assertEqual(spans, sorted(spans))
        self.assertEqual(len(set(spans)), 3, "a flat span would say nothing")

    def test_the_second_invariant_appears_at_six(self):
        """The finding, and it is not what I expected: D = 5 has ONE, not two.
        If this ever reads 4:1 5:2 6:2 the shape of the result has changed."""
        counts = [self.by_dim[d]["pointwise_conformal_invariants_cubic"]
                  for d in (4, 5, 6)]
        self.assertEqual(counts, [1, 1, 2])


class TestTheBoundaryIsNotWidened(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_the_cited_three_is_not_claimed(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("not contradicted", joined)
        self.assertIn("stays cited", joined)

    def test_derivative_invariants_are_explicitly_out_of_scope(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("derivatives", joined)

    def test_total_derivatives_are_explicitly_not_quotiented(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("total derivatives", joined)
        self.assertIn("lagrangian", joined)

    def test_the_parity_sector_stays_open(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("parity", joined)

    def test_e6_absence_is_not_claimed(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("e6", joined)

    def test_the_dependency_tag_is_local_algebraic_only(self):
        """A pointwise algebraic count is not evidence for anything Lorentzian."""
        self.assertEqual(self.cert["dependency_tags"], ["LOCAL-ALGEBRAIC"])

    def test_no_quantum_or_dynamical_claim(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("dynamics", joined)
        self.assertIn("quantum", joined)


class TestTheOlderCertificateIsUntouched(unittest.TestCase):
    """Append-only: this is a new event, not a repair.  The D = 6 certificate's
    own CITED row must still be CITED -- it carries a larger claim (three type-B
    invariants) than the one computed here."""

    def test_the_d6_certificate_still_cites_its_count(self):
        d6 = load(D6_CERT)
        rows = {r["dimension"]: r for r in d6["at_the_selected_degree"]}
        self.assertEqual(rows[6]["status"], "CITED")
        self.assertEqual(rows[6]["quotient"], 3)

    def test_this_certificate_says_it_supersedes_nothing(self):
        cert = load()
        self.assertIn("supersedes_nothing", cert)
        self.assertIn("REVERSE_PHYSICS_WEYL_ACTION_D6_V1",
                      cert["supersedes_nothing"])


class TestTheControlsAreRecorded(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_the_known_answer_control_is_named_and_ran_first(self):
        c = self.cert["controls"]["known_answer_control_ran_first"]
        self.assertIn("D = 4", c)
        self.assertIn("curvature_invariants_d4_gate", c)

    def test_non_degeneracy_is_per_metric(self):
        c = self.cert["controls"]
        self.assertIn("non_degeneracy_per_metric", c)
        self.assertIn("understatement", c["non_degeneracy_per_metric"].lower())

    def test_saturation_is_recorded(self):
        self.assertIn("rank_saturation", self.cert["controls"])

    def test_two_rank_rails(self):
        self.assertIn("two_rank_rails", self.cert["controls"])

    def test_the_mutation_battery_actually_discriminates(self):
        """Every mutation must score BELOW the baseline.  A mutation that scores
        the baseline is a check that was never testing anything."""
        mb = self.cert["mutation_battery"]
        base = mb["baseline"]
        self.assertGreater(len(mb["mutations"]), 0)
        for m in mb["mutations"]:
            self.assertLess(m["score"], base, m["mutation"])

    def test_the_arithmetic_is_exact(self):
        method = self.cert["method"]["arithmetic"].lower()
        self.assertIn("exact rational", method)
        self.assertIn("no floating point", method)


class TestTheReport(unittest.TestCase):
    def setUp(self):
        with open(REPORT) as fh:
            self.text = fh.read()

    def test_the_report_leads_with_the_boundary(self):
        head = self.text[:1200]
        self.assertIn("does not overturn", head.lower())

    def test_the_report_records_the_expectation_that_was_wrong(self):
        """D = 5 having ONE, not two, contradicted what I predicted before
        running it.  That has to survive in the writing."""
        self.assertIn("wrong about", self.text.lower())

    def test_the_report_carries_the_verification_command(self):
        self.assertIn("curvature_invariants_d6_gate.forge", self.text)
        self.assertIn("forge verify --full", self.text)


if __name__ == "__main__":
    unittest.main()
