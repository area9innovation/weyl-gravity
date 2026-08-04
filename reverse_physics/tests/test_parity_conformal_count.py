"""Falsification tests for the parity-odd conformal invariant count.

The computation lives in Forge (tango).  These tests guard the two things this
result is most likely to lose: the exactness precondition that makes a
Levi-Civita tensor rational at all, and the distinction between "parity-odd
invariants exist in D = 6" and the stronger D = 4 statement about field
equations, which is NOT what was computed.
"""

from __future__ import annotations

import json
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CERTS = os.path.join(REPO_ROOT, "reverse_physics", "certificates")
CERT = os.path.join(CERTS, "REVERSE_PHYSICS_PARITY_CONFORMAL_COUNT_V1.json")
D6 = os.path.join(CERTS, "REVERSE_PHYSICS_WEYL_ACTION_D6_V1.json")
REPORT = os.path.join(REPO_ROOT, "reverse_physics", "reports",
                      "parity-conformal-count.md")


def load(path=CERT):
    with open(path) as fh:
        return json.load(fh)


class TestTheNumbers(unittest.TestCase):
    def setUp(self):
        self.cert = load()
        self.rows = self.cert["results"]

    def test_all_checks_pass(self):
        self.assertTrue(self.cert["checks"]["ok"])
        self.assertEqual(self.cert["checks"]["failures"], [])
        self.assertEqual(self.cert["checks"]["passed"],
                         self.cert["checks"]["total"])

    def test_the_counting_identity_where_ranks_are_recorded(self):
        for r in self.rows:
            if "value_rank" in r:
                self.assertEqual(r["value_rank"] - r["variation_rank"],
                                 r["parity_odd_invariants"], r)

    def test_d6_weight6_has_two(self):
        r = [x for x in self.rows if x["dimension"] == 6 and x["weight"] == 6]
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["parity_odd_invariants"], 2)

    def test_d4_weight4_pontryagin_is_one(self):
        r = [x for x in self.rows
             if x["dimension"] == 4 and x["weight"] == 4]
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["parity_odd_invariants"], 1)
        self.assertIn("Pontryagin", r[0]["exhibited_as"])

    def test_odd_dimensions_are_counted_not_computed(self):
        """There is nothing for a rank to evaluate there, and saying otherwise
        would claim a computation that never ran."""
        r = [x for x in self.rows if x["dimension"] == "odd"]
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["parity_odd_invariants"], 0)
        self.assertIn("COUNTED", r[0]["status"])
        self.assertIn("nothing for a rank", r[0]["status"])

    def test_every_nonzero_count_is_exhibited(self):
        """A count without a witness is weaker than this claims to be."""
        for r in self.rows:
            if r["parity_odd_invariants"] > 0:
                self.assertTrue(r["exhibited_as"].strip(), r)


class TestTheExactnessPrecondition(unittest.TestCase):
    """eps = sqrt(|det g|) * symbol.  Everything rational about this result rests
    on |det g| = 1 at the base point."""

    def setUp(self):
        self.cert = load()
        self.how = self.cert["how_a_levi_civita_tensor_stays_in_exact_arithmetic"]

    def test_the_problem_is_stated(self):
        self.assertIn("sqrt", self.how["the_problem"])
        self.assertIn("not rational", self.how["the_problem"])

    def test_the_condition_is_checked_not_assumed(self):
        self.assertIn("check", self.how["it_is_checked_not_assumed"].lower())
        self.assertIn("18/20", self.how["it_is_checked_not_assumed"])

    def test_the_determinant_check_is_among_the_checks(self):
        self.assertTrue(
            self.cert["checks"]["detail"]["det_g_is_unit_on_every_fixture"])

    def test_covariant_constancy_is_why_derivatives_need_nothing_extra(self):
        self.assertIn("COVARIANTLY CONSTANT",
                      self.how["the_other_thing_that_makes_it_work"])


class TestTheBoundaryOfWhatWasAnswered(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_exactness_is_not_claimed(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("lower bound", joined)

    def test_the_field_equation_half_is_explicitly_not_done(self):
        """The D = 4 parity result is about ACTIONS versus FIELD EQUATIONS.  This
        certificate counts invariants; it does not redo that comparison."""
        joined = " ".join(self.cert["does_not_establish"])
        self.assertIn("FIELD-EQUATION", joined)
        self.assertIn("is NOT done", joined)

    def test_the_trace_anomaly_is_not_claimed(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("trace anomaly", joined)
        self.assertIn("total derivatives", joined)

    def test_two_epsilon_candidates_are_out_of_scope(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("two levi-civita", joined)

    def test_dependency_tag_is_local_algebraic_only(self):
        self.assertEqual(self.cert["dependency_tags"], ["LOCAL-ALGEBRAIC"])

    def test_no_dynamical_or_quantum_claim(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("dynamics", joined)
        self.assertIn("quantum", joined)


class TestTheGateItAnswers(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_it_names_the_gate_and_the_half(self):
        self.assertIn("WEYL_ACTION_SIX_DERIVATIVE_D6", self.cert["answers"])
        self.assertIn("parity", self.cert["answers"])

    def test_the_answer_is_yes_and_says_what_the_analogue_is(self):
        a = self.cert["the_answer_to_the_gate"]
        self.assertIn("yes", a["answered"].lower())
        self.assertIn("weyl", a["the_shape_of_the_analogue"].lower())

    def test_the_older_certificate_is_untouched(self):
        """Append-only.  WEYL_ACTION_D6 still records its own parity half as
        unanswered; this is a new event that answers it, not an edit."""
        d6 = load(D6)
        joined = " ".join(d6["does_not_establish"])
        self.assertIn("PARITY", joined)


class TestTheControls(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_the_known_answer_control_is_the_pontryagin_density(self):
        c = self.cert["controls"]["known_answer_control"]
        self.assertIn("Pontryagin", c)
        self.assertIn("asserts", c)

    def test_the_positive_control_is_argued_not_just_asserted(self):
        c = self.cert["controls"]["positive_control"]
        self.assertIn("weight -6", c)
        self.assertIn("NONZERO", c)

    def test_there_is_a_control_that_must_vanish(self):
        self.assertIn("machinery_control_that_must_vanish", self.cert["controls"])

    def test_non_vacuity_is_checked(self):
        c = self.cert["controls"]["non_vacuity"]
        self.assertIn("statement about nothing", c)

    def test_the_undersampled_run_is_recorded(self):
        """A run that reported one fewer invariant, caught only by saturation.
        That has to survive in the record or the check looks like ceremony."""
        s = self.cert["a_run_that_failed_its_own_saturation_check"]
        self.assertIn("ONE FEWER", s)
        self.assertIn("saturation", s.lower())

    def test_the_mutation_battery_discriminates(self):
        mb = self.cert["mutation_battery"]
        self.assertGreater(len(mb["mutations"]), 0)
        for m in mb["mutations"]:
            self.assertLess(m["score"], mb["baseline"], m["mutation"])

    def test_the_arithmetic_is_exact(self):
        a = self.cert["method"]["arithmetic"].lower()
        self.assertIn("exact rational", a)
        self.assertIn("no floating point", a)


class TestTheReport(unittest.TestCase):
    def setUp(self):
        with open(REPORT) as fh:
            self.text = fh.read()

    def test_it_leads_with_the_bound(self):
        self.assertIn("lower bound", self.text[:700].lower())

    def test_it_states_the_answer_to_the_gate(self):
        self.assertIn("yes", self.text[:2500].lower())

    def test_it_records_the_undersampled_run(self):
        self.assertIn("one fewer invariant", self.text.lower())

    def test_it_carries_the_verification_command(self):
        self.assertIn("curvature_invariants_parity_gate.forge", self.text)


if __name__ == "__main__":
    unittest.main()
