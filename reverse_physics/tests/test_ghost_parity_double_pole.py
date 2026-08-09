"""Falsification tests for the ghost-parity / double-pole incompatibility.

The claim is an IMPOSSIBILITY at the quadratic level, and impossibility claims
fail by being too narrow: if the case enumeration missed the configuration that
works, the theorem is an artefact of the sample.  So the tests re-derive the
statement symbolically over free a, b rather than trusting the table, and check
that the broken case really does produce the double pole -- otherwise the
"impossibility" would be about a propagator nobody wanted.
"""

from __future__ import annotations

import importlib.util
import json
import os
import unittest

import sympy as sp

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CERT = os.path.join(REPO_ROOT, "reverse_physics", "certificates",
                    "REVERSE_PHYSICS_GHOST_PARITY_DOUBLE_POLE_V1.json")
MODULE = os.path.join(REPO_ROOT, "reverse_physics",
                      "ghost_parity_double_pole.py")


def module():
    spec = importlib.util.spec_from_file_location("gpdp", MODULE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestGate(unittest.TestCase):
    def setUp(self):
        with open(CERT) as fh:
            self.cert = json.load(fh)

    def test_all_checks_pass(self):
        self.assertTrue(self.cert["checks"]["ok"],
                        self.cert["checks"]["failures"])

    def test_tag_and_lifecycle(self):
        self.assertEqual(self.cert["dependency_tag"], "LOCAL-ALGEBRAIC")
        self.assertEqual(self.cert["lifecycle_state"], "CLASSIFIED")

    def test_it_does_not_claim_the_gravitational_case(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("no tensor field", joined)
        self.assertIn("any refutation of bateman-turok", joined)


class TestTheoremSymbolically(unittest.TestCase):
    """Re-derive over free a, b -- do not trust the sampled table."""

    def setUp(self):
        self.m = module()
        self.k2, self.a, self.b = self.m.k2, self.m.a, self.m.b

    def test_exchange_is_symmetry_exactly_when_a_equals_b(self):
        M = self.m.quadratic_form()
        diff = sp.simplify(self.m.exchange(M) - M)
        # the only obstruction is the diagonal, and it is a - b
        self.assertEqual(sp.simplify(diff[0, 0] + diff[1, 1]), 0)
        self.assertEqual(sp.simplify(diff[0, 0] - 2 * (self.b - self.a)), 0)

    def test_at_a_equals_b_the_poles_separate_or_the_function_vanishes(self):
        """The theorem, over the whole symmetric line, not at sample points."""
        oo = sp.simplify(self.m.propagator(self.m.quadratic_form())[0, 0])
        on_line = sp.simplify(oo.subs(self.a, self.b))
        # b = 0: two-point function vanishes identically
        self.assertEqual(sp.simplify(on_line.subs(self.b, 0)), 0)
        # b != 0: denominator factorises into two DISTINCT roots
        det = sp.factor(self.m.quadratic_form(self.b, self.b).det())
        roots = sp.solve(sp.Eq(det, 0), self.k2)
        self.assertEqual(len(set(roots)), 2)

    def test_the_double_pole_needs_a_not_equal_b(self):
        """Otherwise the impossibility would be about nothing anyone wants."""
        oo = sp.simplify(self.m.propagator(self.m.quadratic_form(0, 1))[0, 0])
        self.assertEqual(sp.simplify(oo * self.k2**2 + 2), 0)


class TestCasesAreLive(unittest.TestCase):
    def setUp(self):
        self.m = module()
        with open(CERT) as fh:
            self.cert = json.load(fh)

    def test_enumeration_covers_both_sides(self):
        rows = self.cert["cases"]
        sym = [r for r in rows if r["exchange_symmetric"]]
        asym = [r for r in rows if not r["exchange_symmetric"]]
        self.assertGreaterEqual(len(sym), 2)
        self.assertGreaterEqual(len(asym), 2)

    def test_no_symmetric_row_has_the_double_pole(self):
        for r in self.cert["cases"]:
            if r["exchange_symmetric"]:
                self.assertFalse(r["has_coincident_double_pole"], r)

    def test_some_broken_row_does(self):
        self.assertTrue(any(r["has_coincident_double_pole"]
                            for r in self.cert["cases"]
                            if not r["exchange_symmetric"]))

    def test_symmetric_nonzero_rows_really_split(self):
        for r in self.cert["cases"]:
            if r["exchange_symmetric"] and r["OmegaOmega"] != "0":
                self.assertEqual(len(set(r["poles_k2"])), 2, r)


class TestTheReframing(unittest.TestCase):
    """The point of the result is what it does to the queued test."""

    def setUp(self):
        with open(CERT) as fh:
            self.cert = json.load(fh)

    def test_it_records_that_the_queued_test_was_too_weak(self):
        c = self.cert["consequence_for_the_tensor_lift"]
        self.assertIn("BRST", c["the_queued_test_was"])
        self.assertIn("one level earlier", c["why_that_is_too_weak"])
        self.assertEqual(len(c["what_a_lift_must_actually_supply"]), 2)

    def test_the_hard_half_is_named(self):
        c = self.cert["consequence_for_the_tensor_lift"]
        self.assertIn("vacuum", c["which_half_is_hard"])
        self.assertIn("BRST", c["which_half_is_hard"])


if __name__ == "__main__":
    unittest.main()
