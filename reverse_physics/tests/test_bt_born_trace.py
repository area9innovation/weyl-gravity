"""Falsification tests for the Krein Born-trace evaluation.

Two dangers here, and the tests are shaped by both.

The first is overclaim.  This computes a FINITE-SHELL shadow of a continuum
statement, and the temptation is to report it as the capstone.  Every test that
touches the conclusion also pins the boundary.

The second is subtler and nearly bit us: the conclusion is computed from a
diagonal entry that this same work had to REPAIR upstream.  A result whose sign
depends on a value one has just corrected is not a result, so the margin control
is tested here independently of the module that emitted it.
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
                    "REVERSE_PHYSICS_BT_BORN_TRACE_V1.json")
MODULE = os.path.join(REPO_ROOT, "reverse_physics", "bt_born_trace.py")


def load():
    with open(CERT) as fh:
        return json.load(fh)


def module():
    spec = importlib.util.spec_from_file_location("bt", MODULE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestGate(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_all_checks_pass(self):
        self.assertTrue(self.cert["checks"]["ok"], self.cert["checks"]["failures"])

    def test_dependency_tag(self):
        self.assertEqual(self.cert["dependency_tag"], "LOCAL-ALGEBRAIC")
        self.assertEqual(self.cert["lifecycle_state"], "CLASSIFIED")

    def test_boundary_says_this_is_not_the_capstone(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("not a necessary condition for it", joined)
        self.assertIn("open", joined)
        self.assertIn("loop level", joined)

    def test_boundary_disclaims_the_invisibility_reading(self):
        """The first version of this claimed the obstruction was invisible.

        It is not: it contributes 2c^2 to the shell trace.  That correction
        must stay pinned, or the overclaim can quietly return.
        """
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("invisible", joined)
        self.assertIn("it is not", joined)

    def test_mechanism_is_credited_to_paper_05(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("lem:chargenull", joined)
        self.assertIn("restated here, not claimed", joined)
        self.assertIn("attribution", self.cert["the_fork"])

    def test_charge_nullity_failure_is_recorded_with_its_size(self):
        f = self.cert["charge_null_failure_on_the_shell"]
        self.assertIn("0", f["lemma_predicts"])
        self.assertIn("482403/1554251776", f["shell_gives"])
        self.assertIn("transported", f["reading"].lower())


class TestBornTrace(unittest.TestCase):
    def setUp(self):
        self.m = module()

    def test_positive_and_exactly_so(self):
        prob = self.m.born(self.m.shell_T())
        ok, a, b = self.m.positive_by_inspection(prob)
        self.assertTrue(ok)
        self.assertTrue(a.is_rational and b.is_rational)
        self.assertGreater(a, 0)
        self.assertGreater(b, 0)

    def test_prob_equals_even_minus_odd(self):
        """The kappa-graded cross terms must vanish."""
        T = self.m.shell_T()
        Tp, Tm = self.m.split(T)
        self.assertEqual(
            sp.simplify(self.m.born(T)
                        - (self.m.frob2(Tp) - self.m.frob2(Tm))), 0)

    def test_krein_self_adjoint_and_not_hilbert_self_adjoint(self):
        T = self.m.shell_T()
        self.assertEqual(sp.simplify(self.m.krein_adjoint(T) - T),
                         sp.zeros(2, 2))
        self.assertNotEqual(sp.simplify(T - T.T.conjugate()), sp.zeros(2, 2))


class TestControlsAreLive(unittest.TestCase):
    def setUp(self):
        self.m = module()

    def test_criterion_can_go_negative(self):
        """If it could not fail, 'positive' would not be a measurement."""
        bad = self.m.born(self.m.shell_T(odd_scale=10))
        self.assertLess(sp.radsimp(sp.expand(bad)), 0)

    def test_crossover_tracks_the_norm_ratio(self):
        """The sign flips at odd_scale = ||T_+||/||T_-||, not somewhere else."""
        T = self.m.shell_T()
        Tp, Tm = self.m.split(T)
        ratio = sp.sqrt(self.m.frob2(Tp) / self.m.frob2(Tm))
        below = self.m.born(self.m.shell_T(odd_scale=ratio * sp.Rational(99, 100)))
        above = self.m.born(self.m.shell_T(odd_scale=ratio * sp.Rational(101, 100)))
        self.assertGreater(sp.N(below, 30), 0)
        self.assertLess(sp.N(above, 30), 0)

    def test_positivity_witness_rejects_negatives(self):
        self.assertFalse(self.m.positive_by_inspection(-sp.sqrt(5) + 1)[0])
        self.assertFalse(self.m.positive_by_inspection(sp.sqrt(5) - 3)[0])

    def test_sign_does_not_depend_on_the_repaired_entry(self):
        """Independently of the module: zero out T11 and the sign must hold."""
        prob = self.m.born(self.m.shell_T(diag11=sp.Integer(0)))
        self.assertGreater(sp.radsimp(sp.expand(prob)), 0)

    def test_odd_part_is_nonzero(self):
        _, Tm = self.m.split(self.m.shell_T())
        self.assertNotEqual(sp.simplify(self.m.frob2(Tm)), 0)

    def test_shell_does_not_implement_charge_nullity(self):
        """Paper 05's lem:chargenull sends the odd contribution to ZERO.

        On this truncated shell it is exactly 2c^2.  That gap is the finding;
        if it ever became zero the module would silently turn into support
        for a claim it cannot support.
        """
        _, Tm = self.m.split(self.m.shell_T())
        odd = self.m.frob2(Tm)
        self.assertEqual(
            sp.simplify(odd - sp.radsimp(sp.expand(2 * self.m.COBS**2))), 0)
        self.assertEqual(odd, sp.Rational(482403, 1554251776))
        self.assertNotEqual(odd, 0)


class TestUpstreamRepair(unittest.TestCase):
    """The defect must stay described, and the true value must stay a surd."""

    def setUp(self):
        self.m = module()
        self.cert = load()

    def test_fabricated_value_is_not_the_true_value(self):
        self.assertNotEqual(
            sp.simplify(self.m.T11_FABRICATED - self.m.T11), 0)

    def test_agreement_is_subnumeric(self):
        """~2e-19 is the signature of a float match, not an identity."""
        gap = abs(sp.N(self.m.T11_FABRICATED - self.m.T11, 40))
        self.assertLess(gap, sp.Rational(1, 10**15))
        self.assertGreater(gap, 0)

    def test_true_entry_is_a_quadratic_surd(self):
        """Degree 2 over Q -- a 449th root cannot arise in this problem."""
        shifted = self.m.T11 + sp.Rational(2759177557, 995045990400)
        self.assertEqual(
            sp.simplify(sp.expand(shifted**2
                                  - 5 * sp.Rational(13264093, 987148800)**2)), 0)

    def test_repair_claims_no_published_quantity(self):
        self.assertIn("none", self.cert["upstream_repair"]["claims_affected"])


class TestSourceFidelity(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_arxiv_and_date(self):
        self.assertEqual(self.cert["source"]["arxiv"], "2607.00096")
        self.assertIn("2026", self.cert["source"]["date"])

    def test_mechanism_recorded_as_charge_rule(self):
        self.assertIn("charge selection rule",
                      self.cert["source"]["mechanism"])

    def test_their_tree_level_limit_recorded(self):
        self.assertIn("TREE LEVEL", self.cert["source"]["self_declared_limit"])

    def test_the_fork_is_recorded(self):
        fork = self.cert["the_fork"]
        self.assertIn("ODD", fork["obstruction_parity"])
        self.assertIn("EVEN", fork["their_B_parity"])


if __name__ == "__main__":
    unittest.main()
