"""Falsification tests for the derivative-sector conformal invariant count.

The computation lives in Forge (tango), not here.  These tests guard the two ways
this particular result could rot: the count drifting away from what the rail
returned, and "a lower bound that equals the cited value" quietly hardening into
"the count is exactly three".
"""

from __future__ import annotations

import json
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CERTS = os.path.join(REPO_ROOT, "reverse_physics", "certificates")
CERT = os.path.join(CERTS, "REVERSE_PHYSICS_DERIVATIVE_CONFORMAL_COUNT_V1.json")
CUBIC = os.path.join(CERTS, "REVERSE_PHYSICS_CUBIC_CONFORMAL_COUNT_V1.json")
D6 = os.path.join(CERTS, "REVERSE_PHYSICS_WEYL_ACTION_D6_V1.json")
REPORT = os.path.join(REPO_ROOT, "reverse_physics", "reports",
                      "derivative-conformal-count.md")


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

    def test_the_three_dimensions_are_present_and_computed(self):
        self.assertEqual(set(self.by_dim), {4, 5, 6})
        for d, row in self.by_dim.items():
            self.assertEqual(row["status"], "COMPUTED", d)

    def test_the_counting_identity_holds_in_every_row(self):
        """invariant dim = rank(VALUES) - rank(VARIATIONS), row by row."""
        for d, row in self.by_dim.items():
            self.assertEqual(
                row["full_value_rank"] - row["full_variation_rank"],
                row["pointwise_conformal_invariants_weight_6"], d)

    def test_d6_reaches_three(self):
        self.assertEqual(
            self.by_dim[6]["pointwise_conformal_invariants_weight_6"], 3)

    def test_the_derivative_sector_adds_exactly_one_everywhere(self):
        """The part that was NOT predicted.  If this ever reads anything but a
        uniform +1, the shape of the result has changed."""
        for d, row in self.by_dim.items():
            self.assertEqual(
                row["pointwise_conformal_invariants_weight_6"]
                - row["cubic_invariants"], 1, d)
            self.assertEqual(row["derivative_sector_contribution"], 1, d)

    def test_the_counts_are_2_2_3(self):
        counts = [self.by_dim[d]["pointwise_conformal_invariants_weight_6"]
                  for d in (4, 5, 6)]
        self.assertEqual(counts, [2, 2, 3])


class TestTheCrossCheckAgainstTheSeparatePipeline(unittest.TestCase):
    """The cubic columns are recomputed here through a DIFFERENT candidate
    pipeline and must reproduce the earlier certificate exactly.  If these two
    ever disagree, one of the two pipelines is wrong and neither result stands."""

    def setUp(self):
        self.cert = load()
        self.cubic = load(CUBIC)
        self.by_dim = {r["dimension"]: r for r in self.cert["results"]}
        self.cub_dim = {r["dimension"]: r for r in self.cubic["results"]}

    def test_cubic_span_agrees(self):
        for d in (4, 5, 6):
            self.assertEqual(self.by_dim[d]["cubic_span"],
                             self.cub_dim[d]["cubic_curvature_span"], d)

    def test_cubic_invariant_count_agrees(self):
        for d in (4, 5, 6):
            self.assertEqual(
                self.by_dim[d]["cubic_invariants"],
                self.cub_dim[d]["pointwise_conformal_invariants_cubic"], d)


class TestTheBoundStaysABound(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_exactness_is_not_claimed(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("lower bound", joined)
        self.assertIn("exactly 3", joined)

    def test_the_omitted_shape_is_named(self):
        lb = self.cert["it_is_a_lower_bound_and_why_that_is_sound"]
        self.assertIn("box box R", lb["omitted_shape"])
        self.assertIn("hide", lb["consequence"])

    def test_the_soundness_argument_is_recorded(self):
        """Omitting candidates must be argued to be safe in ONE direction, not
        waved at.  Adding a non-invariant candidate raises both ranks."""
        why = self.cert["it_is_a_lower_bound_and_why_that_is_sound"][
            "why_omission_cannot_inflate"].lower()
        self.assertIn("both ranks", why)
        self.assertIn("never decrease", why)

    def test_no_basis_is_claimed(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("no basis is exhibited", joined)

    def test_total_derivatives_still_not_quotiented(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("total derivatives", joined)
        self.assertIn("lagrangian", joined)

    def test_parity_stays_open(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("parity", joined)

    def test_dependency_tag_is_local_algebraic_only(self):
        self.assertEqual(self.cert["dependency_tags"], ["LOCAL-ALGEBRAIC"])

    def test_no_dynamical_or_quantum_claim(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("dynamics", joined)
        self.assertIn("quantum", joined)


class TestTheOlderCertificatesAreUntouched(unittest.TestCase):
    """Append-only: this is a new event.  Neither predecessor is edited."""

    def test_the_cubic_certificate_still_says_two_in_d6(self):
        cub = load(CUBIC)
        by = {r["dimension"]: r for r in cub["results"]}
        self.assertEqual(by[6]["pointwise_conformal_invariants_cubic"], 2)

    def test_this_certificate_declares_what_it_extends(self):
        cert = load()
        self.assertIn("extends", cert)
        self.assertIn("REVERSE_PHYSICS_CUBIC_CONFORMAL_COUNT_V1",
                      cert["extends"])
        self.assertIn("not a repair", cert["extends"])

    def test_the_d6_certificates_own_row_is_still_its_own(self):
        """WEYL_ACTION_D6's row is CITED at 3.  This certificate MATCHES that
        number from below; it does not rewrite the older record."""
        d6 = load(D6)
        rows = {r["dimension"]: r for r in d6["at_the_selected_degree"]}
        self.assertEqual(rows[6]["status"], "CITED")
        self.assertEqual(rows[6]["quotient"], 3)


class TestTheControlsAreRecorded(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_the_derivative_layer_is_certified_separately(self):
        layer = self.cert["the_derivative_layer_is_certified_separately"]
        self.assertIn("curvature_covderiv_gate", layer["rail"])
        self.assertTrue(layer["this_gate_does_not_re_derive_any_of_it"])
        joined = " ".join(layer["checks"]).lower()
        for needle in ("bianchi", "commutator", "symmetric space"):
            self.assertIn(needle, joined)

    def test_the_commutator_blind_spot_is_recorded(self):
        """The commutator antisymmetrises, so a symmetric error cancels out of
        it.  That is why the differentiated Bianchi identity exists, and the
        reason has to survive in the record."""
        joined = " ".join(
            self.cert["the_derivative_layer_is_certified_separately"]["checks"])
        self.assertIn("antisymmetrises", joined)

    def test_both_positive_and_negative_controls(self):
        c = self.cert["controls"]
        self.assertIn("positive_control", c)
        self.assertIn("negative_control", c)
        self.assertIn("EXACTLY two", c["negative_control"])

    def test_the_fixture_non_degeneracy_covers_the_derivatives(self):
        nd = self.cert["controls"]["non_degeneracy_per_metric"]
        self.assertIn("grad R", nd)
        self.assertIn("grad grad R", nd)

    def test_the_normal_coordinates_trap_is_recorded(self):
        why = self.cert["method"]["why_the_linear_term_matters"].lower()
        self.assertIn("normal coordinates", why)
        self.assertIn("clean baseline", why)

    def test_saturation_and_two_rank_rails(self):
        self.assertIn("rank_saturation", self.cert["controls"])
        self.assertIn("two_rank_rails", self.cert["controls"])

    def test_the_arithmetic_is_exact(self):
        a = self.cert["method"]["arithmetic"].lower()
        self.assertIn("exact rational", a)
        self.assertIn("no floating point", a)

    def test_what_was_not_known_in_advance_is_stated(self):
        s = self.cert["what_was_not_known_in_advance"].lower()
        self.assertIn("weak evidence", s)


class TestTheReport(unittest.TestCase):
    def setUp(self):
        with open(REPORT) as fh:
            self.text = fh.read()

    def test_the_report_leads_with_the_bound(self):
        self.assertIn("lower bound", self.text[:600].lower())

    def test_the_report_records_the_defects_found_in_our_own_work(self):
        low = self.text.lower()
        self.assertIn("factor of 2", low)
        self.assertIn("miscounted", low)
        self.assertIn("normal coordinates", low)

    def test_the_report_carries_the_verification_commands(self):
        self.assertIn("curvature_invariants_deriv_gate.forge", self.text)
        self.assertIn("curvature_covderiv_gate.forge", self.text)


if __name__ == "__main__":
    unittest.main()
