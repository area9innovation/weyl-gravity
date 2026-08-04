"""Falsification tests for the carrier-vacuity method.

The three findings are index-counting statements, so they are attacked here from
the side that does NOT use index counting: by checking the exact computed
dimensions against independently predictable values, and by checking that the
machinery still discriminates -- a grid where every answer is zero would satisfy
F1 and F3 vacuously and prove nothing.
"""

from __future__ import annotations

import json
import os
import unittest
from fractions import Fraction

from reverse_physics.carrier_vacuity import (
    CERT_PATH,
    EMPTY,
    LEDGER_AUDIT,
    LIVE,
    MAX_BASIS,
    VACUOUS,
    build,
    diff_invariant_dimension,
    monomials,
    pairs,
    weyl_weight,
)

# The grid is the same for every test class, and computing it is the whole cost
# of this module.  Cached once here rather than per class.
_CERT = None


def cert():
    global _CERT
    if _CERT is None:
        _CERT = build()
    return _CERT


class TestTheGradedComputation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cert = cert()
        cls.grid = cls.cert["grid"]

    def test_findings_hold(self):
        d = self.cert["checks"]["detail"]
        self.assertTrue(d["F1_diff_invariant_exactly_when_n_equals_m"])
        self.assertTrue(d["F2_no_weight_zero_piece_in_odd_dimension"])
        self.assertTrue(d["F3_never_both_weyl_and_diff_invariant_at_order_zero"])

    def test_the_grid_discriminates(self):
        """F1 and F3 are satisfied vacuously by an all-zero grid, so the grid
        must contain both kinds of nonzero answer."""
        self.assertTrue(any(r["diff_invariant_dimension"] > 0
                            for r in self.grid),
                        "no piece is diff-invariant -- F1 would be vacuous")
        self.assertTrue(any(r["is_weyl_invariant"] for r in self.grid),
                        "no piece is Weyl-invariant -- F3 would be vacuous")

    def test_all_rank_rails_agree(self):
        for r in self.grid:
            self.assertTrue(r["rails_agree"],
                            "rails disagree at D=%d (%d,%d)"
                            % (r["dimension"], r["n_inverse"], r["m_metric"]))

    def test_nothing_is_silently_truncated(self):
        """Every piece over the cap must be listed, with its size."""
        for s in self.cert["skipped"]:
            self.assertGreater(s["basis_dimension"], MAX_BASIS)
            self.assertIn("reason", s)


class TestAgainstIndependentlyKnownValues(unittest.TestCase):
    """Dimensions predictable without the module's own reasoning."""

    def test_basis_sizes_are_the_multiset_counts(self):
        # degree-n monomials in the D(D+1)/2 independent components
        for dim in (2, 3, 4):
            npairs = dim * (dim + 1) // 2
            self.assertEqual(len(pairs(dim)), npairs)
            self.assertEqual(len(monomials(dim, 1, 0)), npairs)
            self.assertEqual(len(monomials(dim, 2, 0)),
                             npairs * (npairs + 1) // 2)
            self.assertEqual(len(monomials(dim, 1, 1)), npairs * npairs)

    def test_the_trace_is_the_only_bilinear_invariant(self):
        """h^ab g_cd has exactly one GL-invariant in every dimension: the
        trace.  This is a fact about GL representations, not about this code."""
        for dim in (2, 3, 4):
            info = diff_invariant_dimension(dim, 1, 1)
            self.assertEqual(info["invariant_dimension"], 1,
                             "dimension %d" % dim)

    def test_the_empty_monomial_is_invariant(self):
        """Degree (0,0) is the constant 1, which is a scalar."""
        for dim in (2, 3, 4):
            self.assertEqual(
                diff_invariant_dimension(dim, 0, 0)["invariant_dimension"], 1)

    def test_a_single_inverse_metric_has_no_invariant(self):
        """h^ab alone has two free upper indices and cannot be a scalar."""
        for dim in (2, 3, 4):
            self.assertEqual(
                diff_invariant_dimension(dim, 1, 0)["invariant_dimension"], 0)

    def test_weyl_weight_formula(self):
        self.assertEqual(weyl_weight(4, 2, 0), 0)
        self.assertEqual(weyl_weight(2, 1, 0), 0)
        self.assertEqual(weyl_weight(4, 0, 0), 2)
        # odd dimension can never reach zero from integer degrees
        for n in range(6):
            for m in range(6):
                self.assertNotEqual(weyl_weight(3, n, m), 0)
                self.assertNotEqual(weyl_weight(5, n, m), 0)

    def test_odd_dimension_weights_are_half_integers(self):
        for n in range(4):
            for m in range(4):
                w = weyl_weight(3, n, m)
                self.assertEqual(Fraction(w).denominator, 2)


class TestTheAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cert = cert()

    def test_three_assumptions_are_vacuous(self):
        vac = self.cert["audit_summary"]["vacuous_assumptions"]
        self.assertEqual(sorted(vac),
                         ["RP-DIFF", "RP-LOCAL", "RP-METRIC"])

    def test_vacuous_is_exactly_being_a_construction_constraint(self):
        """The diagnosis is that the two coincide; the audit must not record a
        vacuous assumption that is not a construction constraint, or vice
        versa."""
        for a in LEDGER_AUDIT:
            self.assertEqual(a["status"] == VACUOUS,
                             a["is_a_construction_constraint"],
                             a["assumption"])

    def test_only_rp_diff_has_been_enlarged(self):
        untreated = self.cert["audit_summary"]["vacuous_and_still_untreated"]
        self.assertEqual(sorted(untreated), ["RP-LOCAL", "RP-METRIC"])

    def test_every_vacuous_assumption_names_its_enlargement(self):
        for a in LEDGER_AUDIT:
            if a["status"] == VACUOUS:
                self.assertTrue(a.get("enlargement"),
                                "%s is vacuous with no named enlargement"
                                % a["assumption"])

    def test_live_assumptions_give_a_reason(self):
        for a in LEDGER_AUDIT:
            if a["status"] == LIVE:
                self.assertTrue(a["because"])
                self.assertFalse(a["is_a_construction_constraint"])


class TestSelfCriticism(unittest.TestCase):
    """The audit must keep reporting that its own witness carrier is EMPTY."""

    @classmethod
    def setUpClass(cls):
        cls.union = cert()["union_carrier"]

    def test_order_zero_alone_is_empty_for_rp_diff(self):
        self.assertEqual(self.union["rp_diff_on_order_zero_alone"], EMPTY)
        self.assertEqual(self.union["order_zero_diff_invariant"], 0)

    def test_the_union_carrier_is_live(self):
        self.assertEqual(self.union["rp_diff_on_the_union"], LIVE)
        self.assertGreater(self.union["union_diff_invariant"], 0)
        self.assertLess(self.union["union_diff_invariant"],
                        self.union["union_dimension"])

    def test_the_splitting_argument_is_recorded(self):
        self.assertIn("derivative order", self.union["why_the_sum_splits"])


class TestCertificateBoundary(unittest.TestCase):
    def setUp(self):
        with open(CERT_PATH) as fh:
            self.disk = json.load(fh)

    def test_declarations_are_flagged_as_declarations(self):
        joined = " ".join(self.disk["does_not_establish"]).lower()
        self.assertIn("declaration", joined)
        self.assertIn("judgement", joined)

    def test_it_does_not_claim_to_be_a_weakenable_base(self):
        joined = " ".join(self.disk["does_not_establish"]).lower()
        self.assertIn("does not build one", joined)

    def test_order_zero_scope_is_declared(self):
        joined = " ".join(self.disk["does_not_establish"]).lower()
        self.assertIn("derivative order", joined)

    def test_emitted_grid_matches_a_fresh_run(self):
        self.assertEqual(self.disk["grid"], cert()["grid"])


if __name__ == "__main__":
    unittest.main()


class TestTheAOPConnectionCitationsResolve(unittest.TestCase):
    """The AOP note asserts things about certificates in this stream.  A
    dangling reference there is the same failure mode the comparison ledger's
    C2 check exists to catch, and it fails silently in prose."""

    NOTE = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))),
        "reverse_physics", "reports", "AOP-CONNECTION.md")

    def setUp(self):
        with open(self.NOTE) as fh:
            self.text = fh.read()

    def test_every_named_certificate_exists(self):
        import re
        root = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
        certs = set(re.findall(r"REVERSE_PHYSICS_[A-Z0-9_]+_V\d", self.text))
        self.assertTrue(certs, "the note cites no certificates at all")
        for name in certs:
            path = os.path.join(root, "reverse_physics", "certificates",
                                name + ".json")
            self.assertTrue(os.path.exists(path),
                            "AOP-CONNECTION.md cites missing %s" % name)

    def test_it_declares_which_of_their_sources_were_read(self):
        self.assertIn("have **not** read the book", self.text)

    def test_it_does_not_claim_to_refute_them(self):
        self.assertIn("scope correction, not a refutation", self.text)

    def test_the_ambiguous_reading_is_left_open(self):
        """Where a slide is terse we must present both readings, not pick one."""
        self.assertIn("we do not claim to know which is theirs", self.text)
