"""Falsification tests for the ghost/resonance join.

The overstatement this invites is specific and attractive: "the ghost is a
resonance" sounds like the Donoghue-Menezes reframing, in which the ghost is
an unstable particle with a width and therefore not in the asymptotic
spectrum.  That is NOT what was proved, and the evidence points the other
way -- a double pole's time-domain reading is secular GROWTH, not decay.

The second thing guarded is the conditionality.  The identification says what
defectiveness MEANS.  It does not say any particular quasinormal mode is
defective; the upstream package explicitly declines to evaluate the selector
that would decide it.
"""

from __future__ import annotations

import json
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CERTS = os.path.join(REPO_ROOT, "reverse_physics", "certificates")
CERT = os.path.join(CERTS, "REVERSE_PHYSICS_GHOST_RESONANCE_JOIN_V1.json")
REPORT = os.path.join(REPO_ROOT, "reverse_physics", "reports",
                      "ghost-resonance-join.md")


def load(path=CERT):
    with open(path) as fh:
        return json.load(fh)


class TestWhatIsActuallyClaimed(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_it_is_an_identification_not_a_physics_result(self):
        self.assertEqual(self.cert["kind"], "structural-identification")

    def test_the_tag_is_local_algebraic_only(self):
        """Neither imported line's tag is inherited."""
        self.assertEqual(self.cert["dependency_tags"], ["LOCAL-ALGEBRAIC"])

    def test_the_claim_is_that_the_two_readings_are_ONE_equation(self):
        e = self.cert["establishes"]
        self.assertIn("IDENTICALLY", e)
        self.assertIn("SAME EQUATION", e)
        self.assertIn("not a CONSEQUENCE", e.replace("is not a CONSEQUENCE",
                                                     "not a CONSEQUENCE"))

    def test_the_join_field_says_same_polynomial_not_implication(self):
        j = self.cert["the_identity"]["the_join"]
        self.assertIn("same equation", j)
        self.assertIn("same polynomial", j)


class TestTheUnstableResonanceReadingIsDENIED(unittest.TestCase):
    """The single most likely misreading, and the certificate must not merely
    stay silent on it -- it has to say the evidence points the other way."""

    def setUp(self):
        self.dne = " ".join(load()["does_not_establish"])

    def test_the_secular_growth_direction_is_stated(self):
        self.assertIn("SECULAR GROWTH, not decay", self.dne)
        self.assertIn("t*exp(i*omega*t)", self.dne)

    def test_it_says_a_double_pole_is_not_a_finite_lifetime_mode(self):
        self.assertIn("not by itself a finite-lifetime mode", self.dne)

    def test_donoghue_menezes_is_named_and_placed_outside(self):
        self.assertIn("Donoghue-Menezes", self.dne)
        self.assertIn("OUTSIDE this programme's assumptions", self.dne)

    def test_the_report_carries_the_same_denial(self):
        with open(REPORT) as fh:
            text = fh.read()
        self.assertIn("points the other way", text)
        self.assertIn("secular growth", text.lower())

    def test_it_does_not_claim_the_ghost_is_harmless(self):
        """The entries read "does not establish: THAT ...", so the disclaimer
        is the bare proposition."""
        self.assertIn("that the ghost is harmless", self.dne)
        self.assertIn("positivity becomes NONLOCAL", self.dne)
        self.assertIn("not that it is benign", self.dne)


class TestTheConditionalityOnDefectiveness(unittest.TestCase):
    """"Says what defectiveness means" vs "says where defectiveness occurs"."""

    def setUp(self):
        self.dne = " ".join(load()["does_not_establish"])

    def test_no_particular_QNM_is_claimed_defective(self):
        self.assertIn("that any particular Schwarzschild quasinormal mode IS defective",
                      self.dne)
        self.assertIn("no actual QNM is promoted to a double pole", self.dne)

    def test_the_upstream_selector_is_named_as_unevaluated(self):
        self.assertIn("beta_n", self.dne)
        self.assertIn("does NOT evaluate", self.dne)

    def test_the_distinction_is_stated_in_those_words(self):
        self.assertIn("what defectiveness MEANS, not where it occurs", self.dne)

    def test_next_names_exactly_what_would_discharge_it(self):
        nxt = load()["next"]
        self.assertIn("beta_n", nxt)
        self.assertIn("QNM germ", nxt)
        self.assertIn("adjoint cokernel germ", nxt)

    def test_the_dynamics_is_open_in_BOTH_directions(self):
        """Not "we haven't shown decay" -- neither decay nor growth."""
        nxt = load()["next"]
        self.assertIn("open in both directions", nxt.lower())
        self.assertIn("neither decay nor growth", nxt)


class TestTheMathematicsIsNotClaimedNovel(unittest.TestCase):
    def test_the_algebra_is_called_elementary(self):
        dne = " ".join(load()["does_not_establish"])
        self.assertIn("elementary 2x2 linear algebra", dne)
        self.assertIn("anyone who wrote it down would get the same identity", dne)

    def test_the_contribution_is_named_as_the_identification(self):
        dne = " ".join(load()["does_not_establish"])
        self.assertIn("the IDENTIFICATION", dne)
        self.assertIn("evidence, not the result", dne)


class TestTheGateCanFail(unittest.TestCase):
    """Three vacuous controls were found in this stream in one session.  A
    join that cannot be broken is not a join."""

    def setUp(self):
        self.c = load()["checks"]

    def test_the_negative_control_isolates_defectiveness_from_degeneracy(self):
        n = self.c["the_negative_control_isolates_the_cause"]
        self.assertIn("repeated eigenvalue alone does NOT", n)
        self.assertIn("DEFECTIVENESS, not degeneracy", n)

    def test_non_vacuity_covers_the_shared_equation_itself(self):
        """If v^T eta v were identically zero the join would be trivially
        true and say nothing."""
        v = self.c["non_vacuity"]
        self.assertIn("NOT identically zero as a polynomial", v)
        self.assertIn("cut something out", v)

    def test_the_mutations_are_recorded_with_which_checks_they_break(self):
        m = self.c["mutation_tested"]
        self.assertIn("ONLY check 7", m)
        self.assertIn("1, 3, 4 and 7", m)
        self.assertIn("discriminates", m)

    def test_it_is_symbolic_over_the_general_nilpotent(self):
        s = self.c["symbolic_not_sampled"]
        self.assertIn("EVERY rank-two Jordan block", s)
        self.assertIn("rather than at a fixture", s)


class TestTheTwoLinesDidNotCiteEachOther(unittest.TestCase):
    """The reason this needed writing at all, and it should survive as the
    motivation rather than being smoothed into "we proved a lemma"."""

    def test_the_non_citation_is_recorded_as_the_motivation(self):
        w = load()["why_this_needed_writing"]
        self.assertIn("did not cite each other", w)
        self.assertIn("returns nothing", w)

    def test_the_dipole_certificates_own_framing_is_quoted(self):
        w = load()["why_this_needed_writing"]
        self.assertIn("evidence about where to look, not a theorem", w)

    def test_what_it_changes_is_stated_as_a_new_kind_of_observable(self):
        c = load()["what_it_changes"]
        self.assertIn("an ORDER rather than a sign", c)


if __name__ == "__main__":
    unittest.main()
