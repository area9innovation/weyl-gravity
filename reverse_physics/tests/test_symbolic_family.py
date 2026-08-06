"""Falsification tests for the symbolic-family capability and the three claims
it upgrades.

The temptation this guards against is specific.  "Proved for a family" reads
like "proved for all metrics", and it is not: the family is general in the
METRIC but carries a fixed coordinate pattern.  If that distinction erodes, the
stream will have replaced one overstatement with a better-dressed one -- which
is exactly what the parity retraction earlier in this session was about.

The second thing guarded is the cost lesson.  Two predictions of infeasibility
were wrong by four and five orders of magnitude, and the reason the ceiling was
found anyway is that the gate DEMANDS the full family rather than accepting
whatever the sweep reached.  If that ever becomes "whatever passed", a future
prediction becomes a silent cap.
"""

from __future__ import annotations

import json
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CERTS = os.path.join(REPO_ROOT, "reverse_physics", "certificates")
CERT = os.path.join(CERTS, "REVERSE_PHYSICS_SYMBOLIC_FAMILY_V1.json")
REPORT = os.path.join(REPO_ROOT, "reverse_physics", "reports",
                      "symbolic-families.md")


def load(path=CERT):
    with open(path) as fh:
        return json.load(fh)


class TestWhatIsActuallyClaimed(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_it_is_a_capability_and_a_generalization_not_a_physics_result(self):
        self.assertEqual(self.cert["kind"],
                         "substrate-capability-and-generalization")

    def test_the_family_is_general_in_the_metric(self):
        """LDL^T is the general symmetric matrix: six strictly-lower plus four
        diagonal is ten, every independent component of a symmetric 4x4."""
        e = self.cert["establishes"]
        self.assertIn("LDL^T is the general symmetric matrix", e)
        self.assertIn("ten parameters", e)

    def test_exactly_three_ledger_claims_are_upgraded(self):
        claims = self.cert["claims_upgraded"]
        self.assertEqual(len(claims), 3)
        names = " ".join(c["claim"] for c in claims)
        self.assertIn("tracelessness", names)
        self.assertIn("G1", names)
        self.assertIn("G3", names)

    def test_every_upgraded_claim_records_what_it_was_before(self):
        for c in self.cert["claims_upgraded"]:
            self.assertTrue(c["was"], c["claim"])

    def test_G1_is_marked_as_having_rested_on_one_metric(self):
        """That is the sharpest instance and the reason the exercise was worth
        doing -- G1 is the coordinate vectors the whole D = 4 classification is
        expressed in."""
        g1 = [c for c in self.cert["claims_upgraded"] if "G1" in c["claim"]][0]
        self.assertIn("ONE metric", g1["was"])


class TestEveryUpgradedClaimHasAControlThatCanFail(unittest.TestCase):
    """Three separate controls in this session returned a negative result that
    was indistinguishable from the thing they were meant to detect.  A claim
    without a failing control is not evidence."""

    def setUp(self):
        self.claims = load()["claims_upgraded"]

    def test_each_names_a_control(self):
        for c in self.claims:
            self.assertIn("control", c, c["claim"])
            self.assertTrue(c["control"])

    def test_the_controls_are_things_that_must_FAIL_or_CHANGE(self):
        for c in self.claims:
            ctl = c["control"]
            self.assertTrue(
                any(w in ctl for w in ("NONZERO", "FAIL", "CHANGED")),
                f"the control for {c['claim']} does not name a failing outcome")

    def test_the_G3_control_says_why_it_is_needed(self):
        """Weyl and Riemann differ only by trace terms, so a G3 check without
        the Riemann comparison can be comparing something to itself."""
        g3 = [c for c in self.claims if "G3" in c["claim"]][0]
        self.assertIn("trace terms", g3["control"])
        self.assertIn("comparing something to itself", g3["control"])


class TestTheBoundaryBetweenFamilyAndAllMetrics(unittest.TestCase):
    """The one overstatement this work invites."""

    def setUp(self):
        self.dne = " ".join(load()["does_not_establish"])

    def test_all_metrics_is_explicitly_disclaimed(self):
        self.assertIn("'all metrics'", self.dne)
        self.assertIn("not every metric", self.dne)

    def test_the_residual_restriction_is_named_precisely(self):
        """Not a vague hedge: the restriction is the coordinate pattern, and
        the metric restriction is gone."""
        self.assertIn("FIXED QUADRATIC PATTERN", self.dne)
        self.assertIn("unimodularity restriction of an earlier draft is gone",
                      self.dne)

    def test_it_is_not_claimed_as_a_theorem(self):
        self.assertIn("weaker object", self.dne)

    def test_the_report_carries_the_same_boundary(self):
        with open(REPORT) as fh:
            text = fh.read()
        self.assertIn("not every metric", text)


class TestTheTruncationGuardIsNotOptional(unittest.TestCase):
    def test_the_inner_degree_is_derived_not_tuned(self):
        t = load()["truncation_is_a_check_not_a_caveat"]
        self.assertIn("DERIVED", t)
        self.assertIn("Riemann degree 16", t)

    def test_a_dropped_term_is_called_indistinguishable_from_zero(self):
        """That sentence is the whole reason the guard exists."""
        t = load()["truncation_is_a_check_not_a_caveat"]
        self.assertIn("indistinguishable", t)
        self.assertIn("void without it", t)


class TestTheCostLesson(unittest.TestCase):
    """Two wrong predictions, and the design decision that survived them."""

    def setUp(self):
        self.c = load()["the_cost_and_two_wrong_predictions"]

    def test_both_wrong_predictions_are_recorded_with_their_magnitudes(self):
        self.assertIn("74,613", self.c["prediction_at_six_parameters"])
        self.assertIn("four orders", self.c["prediction_at_six_parameters"])
        self.assertIn("5,311,735", self.c["prediction_at_ten_parameters"])
        self.assertIn("five", self.c["prediction_at_ten_parameters"])

    def test_the_lesson_is_the_design_rule_not_just_the_numbers(self):
        """"Measure it" is advice; "make the gate demand the full family" is a
        mechanism, and only the mechanism survives being forgotten."""
        lesson = self.c["the_lesson"]
        self.assertIn("DEMAND the full family", lesson)
        self.assertIn("quietly become a cap", lesson)

    def test_it_records_what_would_have_happened_if_the_estimate_were_trusted(self):
        self.assertIn("stopped at three", self.c["the_lesson"])


class TestTheRemainingWorkIsOneJobNotThree(unittest.TestCase):
    def test_the_three_open_claims_share_a_blocker(self):
        dne = " ".join(load()["does_not_establish"])
        self.assertIn("N1", dne)
        self.assertIn("N2", dne)
        self.assertIn("Euler operator over this ring", dne)
        self.assertIn("one job, not three", dne)

    def test_the_next_step_names_its_own_known_answer_control_in_advance(self):
        """The Bach tensor vanishes on Einstein metrics.  Naming the control
        before building is what this stream learned to do the hard way."""
        nxt = load()["next"]
        self.assertIn("VANISHES on Einstein metrics", nxt)
        self.assertIn("before it can be believed", nxt)


class TestNoNewTensorCodeIsTheHeadline(unittest.TestCase):
    """The reusable finding: the contraction layer was already generic, and
    what was missing was only a coefficient ring."""

    def test_the_reuse_is_recorded(self):
        h = load()["how"]["no_new_tensor_code"]
        self.assertIn("already generic enough", h)
        self.assertIn("never been handed anything but rationals", h)

    def test_division_is_recorded_as_avoided_rather_than_implemented(self):
        d = load()["how"]["division_is_avoided_not_implemented"]
        self.assertIn("division BY UNITS", d)
        self.assertIn("rather than trapping", d)

    def test_the_L_inverse_bug_is_recorded(self):
        """I - N is valid only for non-chaining slots.  It was right for two
        and wrong for six, and the gate catches it."""
        li = load()["how"]["L_inverse_is_exact"]
        self.assertIn("WRONG for six", li)
        self.assertIn("rather than trusting the series length", li)


if __name__ == "__main__":
    unittest.main()
