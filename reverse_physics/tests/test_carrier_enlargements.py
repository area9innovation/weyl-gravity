"""Falsification tests for the RP-METRIC and RP-LOCAL enlargements.

Both results are weight bookkeeping, so the danger is that the bookkeeping is
self-consistent and wrong.  The tests attack it from outside: by checking that
it reproduces facts nobody in this stream chose -- the conformal scalar
potential exponents, and the classical trio of dimensions admitting a polynomial
one -- and by checking the arithmetic against a directly recomputed alternative
rather than against itself.
"""

from __future__ import annotations

import json
import unittest
from fractions import Fraction

from reverse_physics.carrier_enlargements import (
    CERT_PATH,
    MAX_INVERSE_BOXES,
    build,
    conformal_power,
    control_scalar_carrying_gl_weight,
    density_weight,
    nonlocal_weight,
    scalar_weight,
)

_CERT = None


def cert():
    global _CERT
    if _CERT is None:
        _CERT = build()
    return _CERT


class TestPartAReproducesKnownPhysics(unittest.TestCase):
    """The exponents are not this stream's to choose."""

    def test_conformal_potential_exponents(self):
        """phi^6, phi^4, phi^3 in D = 3, 4, 6 -- the textbook answers."""
        self.assertEqual(conformal_power(3), 6)
        self.assertEqual(conformal_power(4), 4)
        self.assertEqual(conformal_power(6), 3)

    def test_the_integer_dimensions_are_exactly_three_four_six(self):
        """2D/(D-2) = 2 + 4/(D-2) is an integer iff (D-2) | 4.  Recomputed
        here by divisibility rather than by reusing the module's scan."""
        by_divisibility = [d for d in range(3, 51) if 4 % (d - 2) == 0]
        self.assertEqual(by_divisibility, [3, 4, 6])
        self.assertEqual(
            cert()["part_a_rp_metric"]["integer_dimensions"], [3, 4, 6])

    def test_D5_is_not_an_integer_power(self):
        """A non-integer answer is a real feature, not a gap to paper over."""
        self.assertEqual(conformal_power(5), Fraction(10, 3))
        row = next(r for r in cert()["part_a_rp_metric"]["rows"]
                   if r["dimension"] == 5)
        self.assertFalse(row["conformal_power_is_an_integer"])
        self.assertIsNone(row["witness"])

    def test_the_witness_actually_has_weight_zero(self):
        """Checked by evaluating the weight function, not by trusting the
        solution formula that produced k."""
        for dim in (3, 4, 6):
            k = conformal_power(dim)
            self.assertEqual(density_weight(dim, 0, 0, k), 0, "D=%d" % dim)

    def test_scalar_weight_convention(self):
        self.assertEqual(scalar_weight(4), Fraction(-1, 2))
        self.assertEqual(scalar_weight(6), -1)
        self.assertEqual(scalar_weight(2), 0,
                         "in D = 2 the conformal scalar is weightless")

    def test_D2_has_no_conformal_power(self):
        self.assertIsNone(conformal_power(2))


class TestPartABreaksTheVacuityFindings(unittest.TestCase):
    """F2 and F3 held for the metric-only carrier; a compensator must break
    both, or the enlargement changed nothing."""

    def test_f3_is_broken(self):
        """F3: no order-zero density is both diff- and Weyl-invariant.  With a
        compensator, sqrt(-g) phi^4 is both."""
        self.assertEqual(density_weight(4, 0, 0, 4), 0)
        row = next(r for r in cert()["part_a_rp_metric"]["rows"]
                   if r["dimension"] == 4)
        self.assertTrue(row["witness_weight_is_zero"])
        self.assertTrue(row["metric_factor_is_diff_invariant"])

    def test_f2_is_broken_in_odd_dimension(self):
        """F2: odd dimension has no weight-zero order-zero metric density.
        D = 3 with phi^6 has one."""
        self.assertEqual(density_weight(3, 0, 0, 6), 0)
        row = next(r for r in cert()["part_a_rp_metric"]["rows"]
                   if r["dimension"] == 3)
        self.assertTrue(row["witness_weight_is_zero"])

    def test_metric_only_odd_dimension_still_has_none(self):
        """Without the scalar, odd D cannot reach weight zero at any degree."""
        for dim in (3, 5):
            for n in range(8):
                for m in range(8):
                    self.assertNotEqual(density_weight(dim, n, m, 0), 0)


class TestTheControlDiscriminates(unittest.TestCase):
    def test_index_carrying_compensator_changes_the_answer(self):
        c = control_scalar_carrying_gl_weight(4)
        self.assertTrue(c["rejected"])
        self.assertNotEqual(c["inert_case_invariants"],
                            c["index_carrying_case_invariants"])


class TestPartBLocality(unittest.TestCase):
    def test_locality_gives_exactly_one_solution(self):
        for dim in (4, 6):
            local = [k for k in range(0, 30)
                     if nonlocal_weight(dim, k, 0) == 0]
            self.assertEqual(local, [dim // 2])

    def test_nonlocality_gives_one_solution_per_j(self):
        for dim in (4, 6):
            for j in range(0, MAX_INVERSE_BOXES + 1):
                sols = [k for k in range(0, 40)
                        if nonlocal_weight(dim, k, j) == 0]
                self.assertEqual(sols, [dim // 2 + j],
                                 "D=%d j=%d" % (dim, j))

    def test_net_derivative_order_is_unchanged(self):
        """2(k - j) = D for every solution -- nonlocality does not buy a
        different derivative count."""
        for dim in (4, 6):
            for j in range(0, MAX_INVERSE_BOXES + 1):
                k = dim // 2 + j
                self.assertEqual(2 * k - 2 * j, dim)

    def test_the_certificate_says_so(self):
        for r in cert()["part_b_rp_local"]["rows"]:
            self.assertEqual(r["local_solution_count"], 1)
            self.assertTrue(r["derivative_order_is_unchanged"])
            self.assertGreater(r["nonlocal_solution_count"], 1)


class TestJointConsequenceAndBoundary(unittest.TestCase):
    def test_all_three_assumptions_are_listed_with_distinct_failures(self):
        entries = cert()["joint_consequence"]["each_fails_differently"]
        self.assertEqual(sorted(e["assumption"] for e in entries),
                         ["RP-DIFF", "RP-LOCAL", "RP-METRIC"])
        modes = [e["how_it_fails"] for e in entries]
        self.assertEqual(len(set(modes)), 3, "the failures must be distinct")

    def test_the_ghost_row_does_not_overclaim(self):
        row = cert()["ghost_table_row"]
        self.assertIn("what_is_NOT_established", row,
                      "the row must carry an explicit non-claim")
        self.assertIn("not thereby ghost-free",
                      row["what_is_NOT_established"])
        self.assertIn("DERIVATION", row["what_is_NOT_established"])
        self.assertIn("pole-count", row["what_is_established"])

    def test_certificate_disclaims_removing_the_ghost(self):
        with open(CERT_PATH) as fh:
            disk = json.load(fh)
        joined = " ".join(disk["does_not_establish"]).lower()
        self.assertIn("ghost", joined)
        self.assertIn("derivation", joined)
        self.assertIn("infinite-derivative", joined)

    def test_certificate_disclaims_classifying_nonlocal_invariants(self):
        """Part B counts solutions of a weight condition; it does not compute
        how many independent invariants sit at each (k, j)."""
        with open(CERT_PATH) as fh:
            disk = json.load(fh)
        joined = " ".join(disk["does_not_establish"]).lower()
        self.assertIn("weight condition", joined)
        self.assertIn("not independent invariants", joined)

    def test_all_checks_pass(self):
        self.assertTrue(cert()["checks"]["ok"])
        self.assertEqual(cert()["checks"]["failures"], [])

    def test_emitted_certificate_is_current(self):
        with open(CERT_PATH) as fh:
            disk = json.load(fh)
        self.assertEqual(disk["part_a_rp_metric"]["rows"],
                         cert()["part_a_rp_metric"]["rows"])
        self.assertEqual(disk["part_b_rp_local"]["rows"],
                         cert()["part_b_rp_local"]["rows"])


if __name__ == "__main__":
    unittest.main()
