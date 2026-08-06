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

    def test_exactly_four_ledger_claims_are_upgraded(self):
        claims = self.cert["claims_upgraded"]
        self.assertEqual(len(claims), 4)
        names = " ".join(c["claim"] for c in claims)
        self.assertIn("tracelessness", names)
        self.assertIn("G1", names)
        self.assertIn("G3", names)
        self.assertIn("N1", names)

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


class TestTheRemainingWorkIsTwoJobsNotThree(unittest.TestCase):
    """It was recorded as three sharing one blocker.  That was wrong: N1 needed
    only the covariant derivative, which already existed, and grouping it with
    the two variational claims hid that."""

    def test_only_the_two_variational_claims_share_the_blocker(self):
        dne = " ".join(load()["does_not_establish"])
        self.assertIn("N2", dne)
        self.assertIn("Euler operator over this ring", dne)
        self.assertIn("about the VARIATION rather than the curvature", dne)

    def test_the_wrong_grouping_is_recorded_rather_than_quietly_fixed(self):
        """Append-only: a mispredicted blocker is a finding, not an
        embarrassment to edit away."""
        n1 = load()["n1"]
        self.assertIn("wrong blocker", " ".join(n1.keys()).replace("_", " "))
        self.assertIn("WRONG for N1", n1["the_certificate_predicted_the_wrong_blocker"])
        dne = " ".join(load()["does_not_establish"])
        self.assertIn("should not have been", dne)


class TestN1(unittest.TestCase):
    def setUp(self):
        self.n1 = load()["n1"]
        self.claim = [c for c in load()["claims_upgraded"]
                      if "N1" in c["claim"]][0]

    def test_the_negative_control_is_named_as_the_load_bearing_one(self):
        """nabla^a R_ab = (1/2) nabla_b R does not vanish, so the same
        machinery on Ricci must come back nonzero.  Without it, a divergence
        routine that returns zero for everything passes."""
        ctl = self.claim["control"]
        self.assertIn("NONZERO", ctl)
        self.assertIn("Ricci", ctl)
        self.assertIn("returns zero for everything", ctl)

    def test_it_is_recorded_as_holding_over_a_SMALLER_family(self):
        """The one overstatement N1 invites: it sits in a certificate whose
        headline number is ten, and it is not ten."""
        self.assertIn("NOT the full ten", self.claim["family"])
        self.assertIn("strictly smaller", self.claim["family"].lower())
        self.assertIn("not determined", self.claim["family"])
        dne = " ".join(load()["does_not_establish"])
        self.assertIn("N1 over the full family", dne)

    def test_the_ceiling_is_a_budget_not_a_wall_and_says_so(self):
        """Every other check in that gate demands the full family because a
        PREDICTED cost nearly became a silent cap.  N1 is the one exception, so
        it has to carry the distinction explicitly or it reads as the same
        failure."""
        c = self.n1["the_cost_ceiling_is_measured"]
        self.assertIn("A BUDGET, NOT A WALL", c)
        self.assertIn("RECORDED AS VERIFIED", c)

    def test_the_undetermined_value_is_named_as_undetermined(self):
        """A killed run is neither a pass nor a fail.  Letting np=5 read as a
        limit would be exactly the fail-closed law inverted."""
        c = self.n1["the_cost_ceiling_is_measured"]
        self.assertIn("NOT\nDETERMINED", c.replace(" ", "\n"))
        self.assertIn("neither", c)
        self.assertIn("a pass nor a fail", c)

    def test_the_disproportionate_search_is_recorded_as_a_defect(self):
        """Not a correctness failure -- a proportion failure, which is the kind
        most likely to repeat because nothing goes red."""
        d = self.n1["the_search_for_the_ceiling_was_itself_disproportionate"]
        self.assertIn("SHARED machine", d)
        self.assertIn("never depended on the ceiling being maximal", d)
        self.assertIn("edited\nmid-sweep", d.replace(" ", "\n"))

    def test_only_the_constant_term_is_read_and_the_reason_is_the_chain(self):
        r = self.n1["only_the_constant_term_is_read_and_that_is_derived"]
        self.assertIn("truncation garbage", r)
        self.assertIn("polynomial in the PARAMETERS", r)


class TestTheEinsteinControlWasBuiltAndDoesNotWork(unittest.TestCase):
    """The debt was discharged by BUILDING the control, and building it showed
    the advice was wrong.  The finding is the vacuity, not the passing check --
    so the record must not read as "Einstein control: passed"."""

    def setUp(self):
        self.e = load()["the_einstein_control_was_built_and_is_nearly_vacuous"]

    def test_the_old_debt_entry_points_at_the_finding_rather_than_being_deleted(self):
        """Append-only: the superseded entry stays and forwards."""
        old = load()["n1"]["a_control_named_in_advance_and_then_not_built"]
        self.assertIn("SUPERSEDED", old)
        self.assertIn("nearly_vacuous", old)

    def test_all_three_mutations_are_recorded_with_the_control_passing(self):
        m = self.e["and_it_does_not_do_what_it_was_advertised_to_do"]
        self.assertIn("PASSED ALL THREE", m)
        self.assertIn("1/2 to 1/3", m)
        self.assertIn("C_{acdb}", m)
        self.assertIn("derivative indices swapped", m)

    def test_the_reason_is_given_as_a_mechanism_not_an_apology(self):
        """R^{cd} C_{acbd} = 0 on any Einstein metric by Weyl tracelessness, so
        the coefficient is multiplied by zero.  A mechanism generalises; "it
        turned out to be weak" does not."""
        w = self.e["why_that_is_structural_and_should_have_been_predicted"]
        self.assertIn("multiplied by zero", w)
        self.assertIn("TRACELESSNESS", w)
        self.assertIn("OVERDETERMINED", w)

    def test_the_transferable_lesson_is_stated(self):
        w = self.e["why_that_is_structural_and_should_have_been_predicted"]
        self.assertIn("does not make the control discriminating", w)
        self.assertIn("without checking that it could fail", w)

    def test_the_check_that_actually_works_is_named(self):
        self.assertIn("CONFORMAL WEIGHT", self.e["what_actually_constrains_bach_of"])

    def test_it_is_kept_under_an_honest_label_not_discarded(self):
        k = self.e["what_the_control_is_kept_for"]
        self.assertIn("PIPELINE check", k)
        self.assertIn("OUTSIDE the LDL^T family", k)

    def test_the_open_mutation_entry_forwards_rather_than_being_deleted(self):
        """Append-only.  It was open, it is settled, and the settlement is a
        new entry that the old one points at."""
        u = self.e["one_mutation_is_undetermined"]
        self.assertIn("SETTLED", u)
        self.assertIn("semantic no-op", u)

    def test_does_not_establish_denies_the_coefficient_claim(self):
        dne = " ".join(load()["does_not_establish"])
        self.assertIn("does not discriminate", dne)
        self.assertIn("survived it", dne)


class TestTheDerivativeOrderQuestionWasSettledByComputation(unittest.TestCase):
    """It was carried open for exactly one commit, then answered.  An open
    question about a routine N1 rests on is not something to reason about --
    the reasoning is what produced the retraction."""

    def setUp(self):
        self.s = load()["the_undetermined_mutation_is_now_settled"]

    def test_the_answer_is_stated_as_an_identity_over_the_full_family(self):
        a = self.s["the_answer"]
        self.assertIn("POLYNOMIAL IDENTITY", a)
        self.assertIn("FULL TEN-PARAMETER", a)
        self.assertIn("semantic no-op", a)

    def test_nothing_caught_it_because_nothing_could(self):
        """The point that turns an alarming non-detection into a non-event."""
        self.assertIn("nothing could", self.s["the_answer"])
        self.assertIn("no untested degree of freedom", self.s["the_answer"])

    def test_one_implementation_two_orderings_rather_than_a_copy(self):
        h = self.s["how_it_was_settled"]
        self.assertIn("by computation, not argument", h)
        self.assertIn("second copy that could drift", h)

    def test_the_comparator_can_report_disagreement(self):
        """An agreement test that cannot disagree establishes nothing -- and
        the premises stop it being two zeros agreeing."""
        c = self.s["the_comparator_was_itself_mutation_tested"]
        self.assertIn("orders-agree = 0", c)
        self.assertIn("cannot report disagreement establishes nothing", c)
        self.assertIn("NONZERO", c)
        self.assertIn("SYMBOLICALLY", c)

    def test_the_identity_is_demanded_not_merely_printed(self):
        d = self.s["it_is_now_demanded_not_reported"]
        self.assertIn("FAILS if the identity breaks", d)

    def test_the_regression_rail_is_distinguished_from_the_result(self):
        """Same budget-not-wall reasoning as N1, and it has to be visible or it
        reads as a cap."""
        d = self.s["it_is_now_demanded_not_reported"]
        self.assertIn("regression rail", d)
        self.assertIn("is the RESULT", d)

    def test_the_resolution_is_reachable_from_does_not_establish(self):
        dne = " ".join(load()["does_not_establish"])
        self.assertIn("RESOLVED and kept for the record", dne)

    def test_the_reproduction_command_for_the_full_family_is_given(self):
        cmds = " ".join(load()["verification"]["commands"])
        self.assertIn("BOCHNP", cmds)
        self.assertIn("comparator is not blind", cmds)

    def test_the_report_carries_the_mutation_table(self):
        with open(REPORT) as fh:
            text = fh.read()
        self.assertIn("passed all three", text.lower())
        self.assertIn("could fail", text)


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
