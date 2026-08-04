"""Falsification tests for the D = 6 scaling test.

The result is half computed and half cited, so the tests police the seam.
"""

from __future__ import annotations

import json
import os
import unittest
from fractions import Fraction

from reverse_physics.weyl_action_d6 import (
    AT_THE_DEGREE, BLOCKER, CERT_PATH, build, scan, selected_degree,
)


class TestWhatScales(unittest.TestCase):
    def setUp(self):
        self.cert = build()

    def test_all_checks_pass(self):
        self.assertTrue(self.cert["checks"]["ok"])
        self.assertEqual(self.cert["checks"]["failures"], [])

    def test_a_sector_exists_exactly_in_even_dimension(self):
        """Recomputed from parity directly, not from the module's summary."""
        for r in scan(16):
            self.assertEqual(r["degree_is_an_integer"], r["dimension"] % 2 == 0,
                             "D=%d" % r["dimension"])

    def test_the_degree_is_half_the_dimension(self):
        for d in range(2, 17):
            self.assertEqual(selected_degree(d), Fraction(d, 2))

    def test_derivative_order_equals_the_dimension(self):
        for r in scan(16):
            if r["degree_is_an_integer"]:
                self.assertEqual(Fraction(r["derivative_order"]), r["dimension"])

    def test_einstein_hilbert_survives_only_in_D2(self):
        for r in scan(16):
            self.assertEqual(r["excludes_einstein_hilbert"],
                             r["dimension"] != 2, "D=%d" % r["dimension"])

    def test_the_cosmological_term_is_excluded_everywhere(self):
        for r in scan(16):
            self.assertTrue(r["excludes_cosmological_term"])


class TestTheFinding(unittest.TestCase):
    def setUp(self):
        self.by = {a["dimension"]: a for a in AT_THE_DEGREE}

    def test_uniqueness_does_not_scale(self):
        self.assertEqual(self.by[4]["quotient"], 1)
        self.assertEqual(self.by[6]["quotient"], 3)
        self.assertNotEqual(self.by[4]["quotient"], self.by[6]["quotient"])

    def test_the_computed_and_cited_halves_are_labelled(self):
        """The seam is the whole risk: D=4 is ours, D=6 is not."""
        self.assertEqual(self.by[4]["status"], "COMPUTED")
        self.assertEqual(self.by[6]["status"], "CITED")

    def test_the_computed_half_cites_a_certificate_of_this_stream(self):
        root = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
        self.assertTrue(os.path.exists(os.path.join(
            root, "reverse_physics", "certificates",
            self.by[4]["source"] + ".json")))

    def test_the_cited_half_carries_literature(self):
        self.assertTrue(self.by[6]["literature"])
        self.assertNotIn("source", self.by[6],
                         "a CITED row must not also claim an in-repo source")

    def test_the_degenerate_hit_is_recorded(self):
        cert = build()
        self.assertEqual(cert["degenerate_hit"]["dimension"], 2)
        self.assertIn("dynamically", cert["degenerate_hit"]["reading"].lower())


class TestItDoesNotOverclaim(unittest.TestCase):
    def setUp(self):
        with open(CERT_PATH) as fh:
            self.disk = json.load(fh)

    def test_it_says_the_D6_count_is_not_computed(self):
        joined = " ".join(self.disk["does_not_establish"]).lower()
        self.assertIn("not computed here", joined)
        self.assertIn("marked cited throughout", joined)

    def test_it_admits_the_parity_half_is_unanswered(self):
        joined = " ".join(self.disk["does_not_establish"]).lower()
        self.assertIn("parity", joined)
        self.assertIn("not answered", joined)
        self.assertIn("not answered",
                      self.disk["the_gate"]["answered"].lower())

    def test_the_ghost_qualification_is_not_stated_as_a_correction(self):
        c = self.disk["consequence_for_the_ghost_argument"]
        self.assertIn("not_a_correction", c)
        self.assertIn("correct there", c["not_a_correction"])
        joined = " ".join(self.disk["does_not_establish"]).lower()
        self.assertIn("dimension-general and the existing", joined)

    def test_the_blocker_is_named_with_a_reason(self):
        for key in ("what", "why_it_is_needed", "why_it_is_not_cheap",
                    "consequence"):
            self.assertTrue(BLOCKER[key], key)
        self.assertEqual(self.disk["blocker"]["what"], BLOCKER["what"])


if __name__ == "__main__":
    unittest.main()
