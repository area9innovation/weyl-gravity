"""Falsification tests for the D = 6 parity field-equation certificate — which
is RETRACTED.

The result was wrong.  The Lagrangian differentiated is not a scalar: its slot
spec summed one contracted index over two lower slots and another over two
upper ones, and under a chart change in SL(6, Z) its value moves.  See
REVERSE_PHYSICS_PARITY_SCALAR_CONTROL_V1.

These tests are kept, and their job has changed.  They no longer certify the
result; they certify that the retraction stays attached to it, that the
original claims stay preserved rather than quietly deleted, and that the
boundary discipline the certificate did get right — local versus global, one
invariant of two, no quantum claim — is still on the record.  A retracted
certificate whose tests were simply removed is a certificate that can be
rediscovered and believed.

The controls were not the weak point and are still worth reading: the n = 6
exercise of the Euler operator was sound and the operator is untouched.  What
was missing was a check nobody had thought to write — whether the contraction
was covariant at all.
"""

from __future__ import annotations

import json
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CERTS = os.path.join(REPO_ROOT, "reverse_physics", "certificates")
CERT = os.path.join(CERTS, "REVERSE_PHYSICS_PARITY_FIELD_EQUATIONS_V1.json")
COUNT = os.path.join(CERTS, "REVERSE_PHYSICS_PARITY_CONFORMAL_COUNT_V1.json")
EULER = os.path.join(CERTS, "REVERSE_PHYSICS_EULER_OPERATOR_V1.json")
REPORT = os.path.join(REPO_ROOT, "reverse_physics", "reports",
                      "parity-field-equations.md")


def load(path=CERT):
    with open(path) as fh:
        return json.load(fh)


class TestTheRetractionIsAttached(unittest.TestCase):
    """First, and before anything below is read: this certificate is withdrawn."""

    def setUp(self):
        self.cert = load()

    def test_the_status_is_retracted(self):
        self.assertEqual(self.cert["status"], "RETRACTED")

    def test_the_retraction_comes_before_the_claims(self):
        keys = list(self.cert.keys())
        self.assertLess(keys.index("retraction"), keys.index("establishes"))

    def test_it_names_the_certificate_that_replaces_it(self):
        self.assertEqual(self.cert["retraction"]["by"],
                         "REVERSE_PHYSICS_PARITY_SCALAR_CONTROL_V1")

    def test_the_replacement_exists_and_retracts_this_one(self):
        import os as _os
        with open(_os.path.join(CERTS,
                  "REVERSE_PHYSICS_PARITY_SCALAR_CONTROL_V1.json")) as fh:
            new = json.load(fh)
        self.assertIn("REVERSE_PHYSICS_PARITY_FIELD_EQUATIONS_V1", new["retracts"])

    def test_the_euler_operator_is_not_dragged_down_with_it(self):
        """The instrument was correct.  Losing it would cost a working tool for
        no reason."""
        s = self.cert["retraction"]["what_survives"]
        self.assertIn("untouched", s)
        self.assertIn("exactly zero", s)


class TestTheResultIsNonzeroAndExact(unittest.TestCase):
    """Preserved as the historical record of what was claimed.  Every assertion
    below describes the WITHDRAWN content and must not be read as current."""

    def setUp(self):
        self.cert = load()

    def test_the_kind_is_variational_not_a_count(self):
        """Counting invariants and varying one are different questions.  The
        kind is what keeps this from being read as more counting."""
        self.assertEqual(self.cert["kind"], "variational-classification")

    def test_every_reported_component_is_nonzero(self):
        results = self.cert["results"]
        self.assertTrue(results)
        for r in results:
            self.assertTrue(r["nonzero"])

    def test_the_values_are_exact_rationals(self):
        """A decimal here would mean the field equation was read off a float,
        and a float near zero cannot distinguish 'nonzero' from 'roundoff'."""
        for r in self.cert["results"]:
            v = r["value"]
            self.assertNotIn(".", v)
            self.assertNotIn("e", v.lower())
            num, _, den = v.partition("/")
            self.assertTrue(den)
            int(num)
            int(den)

    def test_more_than_one_metric_is_reported(self):
        metrics = {r["metric"] for r in self.cert["results"]}
        self.assertGreater(len(metrics), 1)

    def test_all_checks_pass(self):
        c = self.cert["checks"]
        self.assertTrue(c["ok"])
        self.assertEqual(c["failures"], [])
        self.assertEqual(c["passed"], c["total"])

    def test_it_is_local_algebraic_only(self):
        self.assertEqual(self.cert["dependency_tags"], ["LOCAL-ALGEBRAIC"])


class TestTheBoundaryOnANonzeroAnswer(unittest.TestCase):
    """The single most available overreach: a nonzero Euler-Lagrange
    expression says 'not LOCALLY a total divergence'.  It does not say
    'not topological'."""

    def setUp(self):
        self.cert = load()
        self.dne = " ".join(self.cert["does_not_establish"])

    def test_local_versus_global_is_stated(self):
        low = self.dne.lower()
        self.assertIn("global", low)
        self.assertIn("local", low)

    def test_the_exact_distinction_is_spelled_out(self):
        self.assertIn("'Not topological' is NOT what is shown", self.dne)

    def test_the_retraction_is_what_is_up_front_now(self):
        """This originally asserted that the local-versus-global boundary led the
        report.  It did, and that was right at the time.  What has to lead it now
        is the RETRACTION -- a boundary on a withdrawn claim is not the first
        thing a reader needs.  The old boundary is still required to be present,
        just no longer first."""
        with open(REPORT) as fh:
            text = fh.read()
        head = text[:900]
        self.assertIn("RETRACTED", head)
        self.assertIn("not a scalar", head)
        self.assertIn("locally", text.lower())
        self.assertIn("not topological", text.lower())

    def test_the_title_itself_no_longer_asserts_the_withdrawn_claim(self):
        """The title read "Parity is not redundant on the D = 6 field equations".
        A reader who gets no further than the first line must not come away with
        the withdrawn result."""
        with open(REPORT) as fh:
            first = fh.readline()
        self.assertIn("RETRACTED", first)

    def test_only_one_of_two_invariants_is_differentiated(self):
        self.assertIn("SECOND parity-odd invariant", self.dne)

    def test_the_d4_result_is_not_reported_as_wrong(self):
        self.assertIn("that the D = 4 result is wrong", self.dne)
        self.assertIn("does not travel", self.dne)

    def test_total_derivative_blindness_carries_over(self):
        self.assertIn("total derivative", self.dne.lower())

    def test_no_quantum_claim_is_taken_from_the_anomaly_link(self):
        """The type-B coefficients multiply these invariants, which makes the
        anomaly the tempting sentence to write next.  It is classical."""
        self.assertIn("trace anomaly", self.dne.lower())
        self.assertIn("no quantum claim follows", self.dne)


class TestBothControlsSurviveInTheRecord(unittest.TestCase):
    """Neither control existed before this computation.  A nonzero result with
    an unexercised operator and an unverified Lagrangian is two independent
    ways to be confidently wrong."""

    def setUp(self):
        self.c = load()["controls"]

    def test_the_reason_controls_were_built_is_recorded(self):
        why = self.c["why_they_matter_here"].lower()
        self.assertIn("nonzero", why)
        self.assertIn("masquerades as a discovery", why)

    def test_they_were_identified_before_the_result_was_claimed(self):
        self.assertIn("BEFORE the result was claimed",
                      self.c["why_they_matter_here"])

    def test_control_one_exercises_the_operator_at_n_equals_6(self):
        c1 = self.c["control_1_the_operator_at_n_equals_6"]
        self.assertIn("D = 4", c1["the_gap"])
        self.assertIn("total divergence BY CONSTRUCTION", c1["the_control"])
        self.assertIn("exactly zero", c1["result"])

    def test_control_one_is_not_vacuous(self):
        """Zero field equations from a zero Lagrangian is not a control."""
        self.assertIn("nonzero first",
                      self.c["control_1_the_operator_at_n_equals_6"]["result"])

    def test_control_two_checks_the_lagrangian_is_the_right_one(self):
        c2 = self.c["control_2_conformal_invariance_of_this_implementation"]
        self.assertIn("nonzero trivially", c2["the_gap"])
        self.assertIn("=", c2["result"])

    def test_the_density_is_checked_nonzero_before_variation(self):
        self.assertIn("nonzero", self.c["non_vacuity"].lower())

    def test_the_measure_rule_is_a_determinant(self):
        self.assertIn("DETERMINANT, not a square root", self.c["the_measure_rule"])

    def test_the_epsilon_collapse_was_checked_against_a_nonzero_value(self):
        """The first attempt compared two zeros.  That lesson is the reason
        this line exists."""
        e = self.c["the_epsilon_collapse"]
        self.assertIn("NONZERO", e)
        self.assertIn("vanished identically", e)

    def test_every_named_check_passed(self):
        detail = load()["checks"]["detail"]
        self.assertEqual(len(detail), load()["checks"]["total"])
        for name, ok in detail.items():
            self.assertTrue(ok, name)


class TestItIsWiredToWhatItQualifies(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_it_completes_the_half_the_count_left_open(self):
        self.assertIn("REVERSE_PHYSICS_PARITY_CONFORMAL_COUNT_V1",
                      self.cert["completes"])
        self.assertIn("NOT DONE", self.cert["completes"])

    def test_the_count_certificate_it_completes_still_stands(self):
        self.assertTrue(load(COUNT)["checks"]["ok"])

    def test_the_operator_it_uses_still_stands(self):
        self.assertTrue(load(EULER)["checks"]["ok"])

    def test_the_d4_statement_is_quoted_rather_than_paraphrased(self):
        d4 = self.cert["the_d4_statement_it_qualifies"]
        self.assertIn("REVERSE_PHYSICS_WEYL_ACTION_V1", d4["what_d4_says"])
        self.assertIn("TWO-parameter family of ACTIONS", d4["what_d4_says"])
        self.assertIn("ONE-parameter family of FIELD EQUATIONS",
                      d4["what_d4_says"])

    def test_the_theta_angle_reading_is_kept(self):
        self.assertIn("theta",
                      self.cert["the_d4_statement_it_qualifies"]
                      ["the_physical_reading"].lower())

    def test_it_is_the_second_dimension_dependent_finding(self):
        d4 = self.cert["the_d4_statement_it_qualifies"]
        self.assertIn("REVERSE_PHYSICS_WEYL_ACTION_D6_V1",
                      d4["this_is_the_second_such_finding"])

    def test_the_consequence_for_the_ledger_count_is_recorded(self):
        """Six-as-action versus five-as-field-equations turns on RP-PARITY
        dropping out.  If it does not drop out in D = 6, that count is
        dimension-dependent, and that is the finding's actual reach."""
        c = self.cert["the_d4_statement_it_qualifies"][
            "consequence_for_the_assumption_count"]
        self.assertIn("RP-PARITY", c)
        self.assertIn("DIMENSION-DEPENDENT", c.upper())

    def test_the_verification_command_is_recorded(self):
        cmds = " ".join(self.cert["verification"]["commands"])
        self.assertIn("curvature_parity_field_equations_gate.forge", cmds)

    def test_the_rails_it_rests_on_are_named(self):
        rails = " ".join(self.cert["verification"]["depends_on_rails"])
        self.assertIn("curvature_euler_gate", rails)
        self.assertIn("curvature_invariants_parity_gate", rails)


class TestTheReport(unittest.TestCase):
    def setUp(self):
        with open(REPORT) as fh:
            self.text = fh.read()

    def test_it_carries_the_verification_command(self):
        self.assertIn("curvature_parity_field_equations_gate.forge", self.text)

    def test_it_states_the_result_is_special_to_four_dimensions(self):
        self.assertIn("special to four dimensions", self.text.lower())

    def test_it_has_a_does_not_establish_section(self):
        self.assertIn("does **not** establish", self.text.lower())

    def test_the_reported_values_match_the_certificate(self):
        for r in load()["results"]:
            self.assertIn(r["value"].replace("-", ""),
                          self.text.replace("−", ""))

    def test_it_declares_exact_arithmetic(self):
        low = self.text.lower()
        self.assertIn("no floating point", low)


if __name__ == "__main__":
    unittest.main()
