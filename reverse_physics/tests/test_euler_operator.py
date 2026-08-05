"""Falsification tests for the Euler-operator capability certificate.

The computation lives in Forge (tango).  What these guard is the thing a
capability certificate is most likely to lose: the distinction between "the
machinery works" and "we learned something about Weyl gravity".  The Euler
operator establishes the first and nothing of the second, and that has to stay
visible.
"""

from __future__ import annotations

import json
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CERTS = os.path.join(REPO_ROOT, "reverse_physics", "certificates")
CERT = os.path.join(CERTS, "REVERSE_PHYSICS_EULER_OPERATOR_V1.json")
PARITY = os.path.join(CERTS, "REVERSE_PHYSICS_PARITY_CONFORMAL_COUNT_V1.json")
REPORT = os.path.join(REPO_ROOT, "reverse_physics", "reports",
                      "euler-operator.md")


def load(path=CERT):
    with open(path) as fh:
        return json.load(fh)


class TestItIsACapabilityNotAResult(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_the_kind_says_so(self):
        self.assertEqual(self.cert["kind"], "substrate-capability")

    def test_no_physics_result_is_claimed(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("any physics result", joined)
        self.assertIn("nothing about weyl gravity that was not already known",
                      joined)

    def test_the_question_it_was_built_for_is_still_open(self):
        joined = " ".join(self.cert["does_not_establish"])
        self.assertIn("D = 6 parity-odd field-equation question", joined)

    def test_validated_only_in_d4_at_one_weight(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("dimensions other than 4", joined)

    def test_total_derivative_blindness_is_stated(self):
        """Two Lagrangians differing by a total derivative have the same field
        equations.  Nothing here distinguishes them, and claiming otherwise
        would be an easy overreach."""
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("total derivative", joined)

    def test_all_checks_pass(self):
        self.assertTrue(self.cert["checks"]["ok"])
        self.assertEqual(self.cert["checks"]["failures"], [])
        self.assertEqual(self.cert["checks"]["passed"],
                         self.cert["checks"]["total"])


class TestTheControlsIncludeANonzeroOne(unittest.TestCase):
    """Two vanishing controls do not pin an operator.  An operator missing a
    term that happens to vanish on topological densities passes both."""

    def setUp(self):
        self.c = load()["controls"]

    def test_the_reason_a_nonzero_control_was_needed_is_recorded(self):
        why = self.c["why_a_nonzero_control_was_required"].lower()
        self.assertIn("vanishing controls", why)
        self.assertIn("overall factor", why)

    def test_the_trace_law_is_the_anchor_and_is_ratio_based(self):
        anchor = self.c["the_trace_law_is_the_nonzero_anchor"]
        self.assertIn("2 (a + b + 3c)", anchor)
        self.assertIn("RATIO", anchor)

    def test_all_four_trace_checks_are_present(self):
        joined = " ".join(self.c["trace_checks"])
        self.assertIn("NONZERO", joined)
        self.assertIn("EQUALS", joined)
        self.assertIn("THREE TIMES", joined)
        self.assertIn("ZERO while the tensor is NONZERO", joined)

    def test_gauss_bonnet_is_a_cancellation_not_three_zeros(self):
        gb = self.c["gauss_bonnet_vanishes"]
        self.assertIn("NONZERO", gb)
        self.assertIn("cancellation", gb)

    def test_pontryagin_is_checked_nonzero_before_its_variation_is_required_zero(self):
        p = self.c["pontryagin_vanishes"]
        self.assertIn("nonzero density", p)


class TestTheTwoBugsAreRecorded(unittest.TestCase):
    def setUp(self):
        self.bugs = load()["two_bugs_this_found_in_its_own_construction"]

    def test_both_are_recorded(self):
        self.assertEqual(len(self.bugs), 2)

    def test_the_truncation_bug_carries_its_evidence(self):
        b = self.bugs[0]
        self.assertIn("FIRST operand", b["bug"])
        self.assertIn("EXACTLY zero", b["evidence_of_the_fix"])

    def test_the_symbol_tensor_bug_names_its_reach(self):
        """This is the one that matters beyond the gate: the same shortcut is
        used by the parity certificate.  If that consequence ever drops out of
        the record, the next field-equation computation repeats the bug."""
        b = self.bugs[1]
        self.assertIn("consequence_beyond_this_gate", b)
        self.assertIn("REVERSE_PHYSICS_PARITY_CONFORMAL_COUNT_V1",
                      b["consequence_beyond_this_gate"])
        self.assertIn("silent wrong answer",
                      b["consequence_beyond_this_gate"])

    def test_the_parity_certificate_is_said_to_be_unaffected(self):
        """Counting invariants at a point is sound under the shortcut.  Saying
        so protects a correct result from being retracted by association."""
        b = self.bugs[1]
        self.assertIn("unaffected", b["consequence_beyond_this_gate"])

    def test_the_parity_certificate_still_stands(self):
        p = load(PARITY)
        self.assertTrue(p["checks"]["ok"])


class TestTheDegreeBudget(unittest.TestCase):
    def setUp(self):
        self.d = load()["the_degree_budget"]

    def test_the_rule_is_stated(self):
        self.assertIn("d + 1", self.d["rule"])
        self.assertIn("d + 3", self.d["rule"])

    def test_it_is_stated_to_fail_silently(self):
        why = self.d["why_it_is_stated_as_a_rule"].lower()
        self.assertIn("silently", why)
        self.assertIn("well-formed", why)

    def test_it_is_a_numbered_check(self):
        self.assertIn("check 12", self.d["it_is_a_numbered_check"])
        self.assertTrue(
            load()["checks"]["detail"]["the_degree_budget_reaches_x_degree_two"])


class TestTheSubstrate(unittest.TestCase):
    def setUp(self):
        self.s = " ".join(load()["substrate_additions"])

    def test_the_nv_assumption_removal_is_recorded_with_its_blast_radius(self):
        self.assertIn("nine gates", self.s)
        self.assertIn("re-run unchanged", self.s)

    def test_the_square_root_traps_rather_than_guessing(self):
        self.assertIn("traps", self.s)

    def test_the_determinant_refuses_rather_than_reporting(self):
        self.assertIn("returning none", self.s)


class TestTheMeasureRuleAndParallelism(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_the_measure_rule_is_a_determinant_not_a_root(self):
        r = self.cert["the_parity_odd_measure_rule"]["the_rule"]
        self.assertIn("DETERMINANT, not a square root", r)

    def test_it_says_why_it_needed_validating(self):
        w = self.cert["the_parity_odd_measure_rule"]["why_it_needed_validating"].lower()
        self.assertIn("indistinguishable", w)
        self.assertIn("no symptom", w)

    def test_the_validation_is_against_a_known_density(self):
        h = self.cert["the_parity_odd_measure_rule"]["how_it_is_validated"]
        self.assertIn("Pontryagin", h)
        self.assertIn("up to a SIGN", h)

    def test_parallelism_is_argued_sound_not_asserted(self):
        p = self.cert["it_runs_in_parallel"]
        self.assertIn("exactly once", p["why_it_is_sound"])
        self.assertIn("race-free by construction", p["why_it_is_sound"])

    def test_the_send_question_is_sidestepped_not_relied_on(self):
        c = self.cert["it_runs_in_parallel"]["the_capture_discipline"]
        self.assertIn("sidesteps", c)

    def test_there_are_three_independent_confirmations(self):
        p = self.cert["it_runs_in_parallel"]
        self.assertIn("recomputes one component sequentially", p["the_rail"])
        self.assertIn("separately compiled binary", p["independent_confirmation"])
        self.assertIn("TSan", p["independent_confirmation"])

    def test_it_was_probed_before_use(self):
        self.assertIn("before the gate was touched",
                      self.cert["it_runs_in_parallel"]["it_was_probed_before_it_was_used"])


class TestTheReport(unittest.TestCase):
    def setUp(self):
        with open(REPORT) as fh:
            self.text = fh.read()

    def test_it_leads_with_capability_not_result(self):
        self.assertIn("capability, not a physics result",
                      self.text[:600].lower().replace("**", ""))

    def test_it_records_the_falsifier_lesson(self):
        low = self.text.lower()
        self.assertIn("falsifier", low)
        self.assertIn("should have existed", low)

    def test_it_carries_the_verification_command(self):
        self.assertIn("curvature_euler_gate.forge", self.text)


if __name__ == "__main__":
    unittest.main()
