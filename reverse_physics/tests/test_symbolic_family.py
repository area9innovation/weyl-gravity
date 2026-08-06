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

    def test_exactly_six_ledger_claims_are_upgraded(self):
        claims = self.cert["claims_upgraded"]
        self.assertEqual(len(claims), 6)
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


class TestTheEulerBlockerWasWrongTwice(unittest.TestCase):
    """Two blocker predictions, both wrong in the same direction, both made
    without reading the code.  The pattern is the finding -- a single instance
    is an error, two is a habit worth naming."""

    def setUp(self):
        self.b = load()["the_euler_operator_blocker_was_wrong_twice"]

    def test_both_wrong_predictions_are_quoted_not_paraphrased(self):
        w = self.b["what_this_certificate_predicted"]
        self.assertIn("one job, not three", w)
        self.assertIn("four hundred lines", w)

    def test_the_pattern_is_named_as_a_pattern(self):
        h = self.b["both_halves_were_wrong"]
        self.assertIn("TWO blocker predictions", h)
        self.assertIn("same direction", h)
        self.assertIn("without reading the code", h)

    def test_the_lesson_is_actionable_not_just_regretful(self):
        l = self.b["the_transferable_lesson"]
        self.assertIn("one file read", l)
        self.assertIn("Read the code before recording what it needs", l)

    def test_the_real_obstructions_are_named_and_dissolved(self):
        r = self.b["the_real_obstructions"]
        self.assertIn("metric_inverse divides", r)
        self.assertIn("O(t^2)", r)
        self.assertIn("perfect square", r)

    def test_the_signature_restriction_is_argued_not_asserted(self):
        """sigma^2 sounds like a loss of generality and is not -- LDL^T with a
        sign-definite diagonal IS the general symmetric matrix of Lorentzian
        signature."""
        r = self.b["the_real_obstructions"]
        self.assertIn("NOT a loss of generality", r)
        self.assertIn("LORENTZIAN SIGNATURE", r)


class TestTheEulerOperatorOverTheNestedRing(unittest.TestCase):
    def setUp(self):
        self.e = load()["euler_operator_over_the_nested_ring"]

    def test_the_known_answer_is_not_assumed(self):
        """Building sqrt(-g) from its own variation law would make the check
        circular.  It is built from the Leibniz determinant instead."""
        k = self.e["the_known_answer_is_not_assumed"]
        self.assertIn("Leibniz determinant", k)
        self.assertIn("circular", k)

    def test_three_conditions_and_each_catches_something_else(self):
        c = self.e["three_conditions_not_one"]
        self.assertIn("the comparison cannot check", c)
        self.assertIn("between two constants", c)

    def test_the_base_point_degeneracy_is_recorded(self):
        """Every parameter entered through x + x^2, which vanishes where every
        check is read.  That invalidated the whole gate, not one check."""
        g = self.e["two_guards_fired_on_the_first_run_and_both_were_right"]
        self.assertIn("VANISHES AT THE BASE POINT", g)
        self.assertIn("collapses to one metric", g)

    def test_a_control_can_be_wrong_by_being_too_strong(self):
        """The opposite failure to the Einstein control, and worth naming
        precisely because the stream has only ever recorded the other kind."""
        g = self.e["two_guards_fired_on_the_first_run_and_both_were_right"]
        self.assertIn("TOO STRONG", g)
        self.assertIn("opposite failure", g)

    def test_premise_and_budget_are_distinguished(self):
        """ROOTNP is not a budget: below 7 the determinant depends on no
        parameter at all, so the premise is unsatisfiable rather than false."""
        p = self.e["parameter_counts_are_per_check_and_differ_in_kind"]
        self.assertIn("is a PREMISE, not a budget", p)
        self.assertIn("UNSATISFIABLE", p)
        self.assertIn("BUDGETS, measured", p)

    def test_it_is_a_separate_gate_and_the_reason_is_the_tier_rule(self):
        self.assertIn("SEPARATE gate", self.e["gate"])
        self.assertIn("split rather than normalised", self.e["gate"])


class TestTheNoetherIdentityVersusTheCount(unittest.TestCase):
    """The sharpest overstatement available here: "the Noether identity holds
    over a family" reads like the generator COUNT moved.  It did not.  The
    original result had two halves and only one has moved."""

    def setUp(self):
        self.claim = [c for c in load()["claims_upgraded"]
                      if "Noether identity" in c["claim"]][0]

    def test_the_identity_is_recorded_as_upgraded(self):
        self.assertIn("SAMPLED FIXTURES", self.claim["was"])

    def test_the_count_has_its_own_claim_entry(self):
        cnt = [c for c in load()["claims_upgraded"]
               if "GENERATOR COUNT" in c["claim"]]
        self.assertEqual(len(cnt), 1)

    def test_the_general_trace_law_is_also_disclaimed(self):
        """The Weyl case is the VANISHING instance of N2, not N2."""
        dne = " ".join(load()["does_not_establish"])
        self.assertIn("general trace law N2", dne)
        self.assertIn("vanishing instance", dne)

    def test_the_small_family_is_stated_as_a_real_restriction(self):
        self.assertIn("smallest sub-family", self.claim["family"])
        dne = " ".join(load()["does_not_establish"])
        self.assertIn("not a formality", dne)

    def test_the_conformal_route_is_justified_on_both_counts(self):
        """Cheaper AND sharper -- and the cheapness is load-bearing, since the
        component route did not finish."""
        h = self.claim["how"]
        self.assertIn("did NOT finish in 580 s", h)
        self.assertIn("IS Weyl invariance", h)

    def test_the_control_discriminates_and_that_was_MEASURED(self):
        """The previous known-answer control in this stream survived three
        defects.  This one was mutation-tested before being believed."""
        c = self.claim["control"]
        self.assertIn("MUTATION TESTED", c)
        self.assertIn("DISCRIMINATES", c)
        self.assertIn("1/(D-1)", c)

    def test_the_negative_control_is_present_too(self):
        c = self.claim["control"]
        self.assertIn("NONZERO", c)
        self.assertIn("returns zero for everything", c)

    def test_C_squared_is_independent_of_G1_rather_than_built_on_it(self):
        """Using the certified G1 identity would have been legitimate and would
        have coupled the two results.  It did not."""
        i = self.claim["independence"]
        self.assertIn("from the DEFINITION", i)
        self.assertIn("INDEPENDENT CONFIRMATION", i)

    def test_next_names_the_boundary_that_is_still_open(self):
        """The inherited-span question has been CLOSED -- the list was
        incomplete, was completed, and the count survived.  What remains is
        degree 3 and the derivative candidates, and `next` must have moved on
        rather than still pointing at the closed one."""
        nxt = load()["next"]
        self.assertIn("degree 3", nxt)
        self.assertIn("derivative candidates", nxt)
        self.assertNotIn("INHERITED", nxt)


class TestTheGeneratorCount(unittest.TestCase):
    def setUp(self):
        self.c = [c for c in load()["claims_upgraded"]
                  if "GENERATOR COUNT" in c["claim"]][0]

    def test_the_result_is_over_the_COMPLETE_ten_not_the_inherited_seven(self):
        r = self.c["result"]
        self.assertIn("TEN candidate tensors", r)
        self.assertIn("not the inherited seven", r)
        for t in ("R g", "R^2 g", "|Ric|^2 g", "|Riem|^2 g"):
            self.assertIn(t, r)
        self.assertIn("ALL FIVE are f g", r)

    def test_the_discriminating_half_is_identified_as_such(self):
        """Four vanishing is not the evidence.  Three NOT vanishing is."""
        m = self.c["the_module_trap"]
        self.assertIn("not that four vanish", m)
        self.assertIn("discriminating half", m)

    def test_the_module_trap_is_quantified(self):
        m = self.c["the_module_trap"]
        self.assertIn("MODULE OVER FUNCTIONS", m)
        self.assertIn("overcounts four to one", m)

    def test_the_count_was_not_left_at_the_first_number_that_worked(self):
        """It ran at 1 and was pushed to 2, matching the identity.  A claim that
        could have covered a wider family and did not is a cap."""
        f = self.c["family"]
        self.assertIn("First run at 1 and not", f)
        self.assertIn("is a cap, not a boundary", f)

    def test_the_small_family_is_still_called_a_real_restriction(self):
        dne = " ".join(load()["does_not_establish"])
        self.assertIn("real restriction", dne)

    def test_the_remaining_completeness_boundary_is_named_precisely(self):
        """Not a vague hedge: degree <= 2, and ALGEBRAIC only."""
        dne = " ".join(load()["does_not_establish"])
        self.assertIn("beyond curvature degree 2", dne)
        self.assertIn("DERIVATIVES of curvature", dne)
        self.assertIn("in that class", dne)


class TestTheInheritedListWasIncomplete(unittest.TestCase):
    """The count was right for an incomplete reason.  Finding that out is the
    result here -- a survived challenge is worth more than an unchallenged
    claim, but only if the challenge is recorded."""

    def setUp(self):
        self.i = load()["the_inherited_candidate_list_was_incomplete"]

    def test_the_defect_in_the_inherited_list_is_stated_as_a_pattern(self):
        w = self.i["what_was_inherited"]
        self.assertIn("built from g and RICCI", w)
        self.assertIn("beyond its Ricci trace", w)

    def test_the_complete_enumeration_is_given_not_just_a_count(self):
        m = self.i["what_was_missing"]
        self.assertIn("TEN, not seven", m)
        self.assertIn("R_{acde} R_b^{cde}", m)
        self.assertIn("Ric^{cd} R_{acbd}", m)

    def test_the_omission_is_argued_to_be_the_dangerous_one(self):
        """Not "we found three more" -- "the three we found are precisely the
        ones that could have changed the answer"."""
        w = self.i["why_the_omission_was_exactly_the_dangerous_one"]
        self.assertIn("IS the Bach tensor", w)
        self.assertIn("SECOND generator", w)
        self.assertIn("structurally could not have seen it", w)

    def test_the_count_is_recorded_as_having_SURVIVED_the_challenge(self):
        r = self.i["the_result"]
        self.assertIn("SURVIVES", r)
        self.assertIn("right for an incomplete reason", r)

    def test_over_completeness_is_addressed_rather_than_ignored(self):
        """Linear dependence among the ten would over-count the dimension, and
        that is the harmless direction.  Saying so is what makes the spanning
        claim honest."""
        o = self.i["over_complete_is_the_safe_direction"]
        self.assertIn("SPANNING set", o)
        self.assertIn("cannot hide an identity", o)
        self.assertIn("UNDER-completeness", o)

    def test_the_marginal_cost_is_recorded(self):
        self.assertIn("shared across every candidate", self.i["cost"])


class TestTheDirectionalRouteFailedItsOwnControl(unittest.TestCase):
    """A wrong method caught by a control that was designed to be able to fail,
    and then diagnosed rather than worked around."""

    def setUp(self):
        self.d = load()["the_directional_route_failed_its_own_control"]

    def test_the_failure_is_recorded_not_just_the_working_method(self):
        self.assertIn("FUNCTION-LINEAR = 0", self.d["it_failed_and_the_control_that_caught_it"])

    def test_the_control_was_run_on_a_nonzero_case_deliberately(self):
        """R g would have given 0 = R x 0 and proved nothing."""
        c = self.d["it_failed_and_the_control_that_caught_it"]
        self.assertIn("NONZERO case", c)
        self.assertIn("proved nothing", c)

    def test_the_diagnosis_is_a_mechanism(self):
        g = self.d["the_diagnosis"]
        self.assertIn("DEGREE BUDGET", g)
        self.assertIn("ldeg + 4", g)
        self.assertIn("silently truncates", g)

    def test_the_same_form_of_argument_is_not_trusted_twice(self):
        """"g costs no derivatives so check 6 is safe" has the same shape as
        the argument that just failed, so it was measured instead."""
        w = self.d["why_check_6_is_unaffected_and_how_that_was_established"]
        self.assertIn("exactly the same form", w)
        self.assertIn("required to AGREE", w)
        self.assertIn("not evidence the second time", w)

    def test_the_choice_of_fix_is_justified_by_cost_and_by_scope(self):
        w = self.d["why_the_component_route_was_taken_rather_than_more_degree"]
        self.assertIn("outer degree 7", w)
        self.assertIn("ALL SEVEN contractions", w)


class TestTheLadderOfKnownAnswers(unittest.TestCase):
    def setUp(self):
        self.e = load()["euler_operator_over_the_nested_ring"]

    def test_each_rung_tests_something_the_previous_cannot(self):
        l = self.e["the_ladder"]
        self.assertIn("must contribute NOTHING", l)
        self.assertIn("must be NONZERO", l)
        self.assertIn("passes rung one completely and fails rung two", l)

    def test_the_sign_is_read_off_rather_than_asserted(self):
        s = self.e["the_sign_is_read_off_not_asserted"]
        self.assertIn("up to an", s)
        self.assertIn("OVERALL SIGN", s)
        self.assertIn("asserting conventions from memory", s)


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
