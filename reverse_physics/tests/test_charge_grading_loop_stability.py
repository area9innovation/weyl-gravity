"""Falsification tests for the charge-grading loop-stability result.

The claim is permissive -- it says an obstruction is ABSENT -- and permissive
claims are the easy ones to get wrong, because a bookkeeping bug that loses
charge looks exactly like a theorem that conserves it.  So the controls that
make charge MOVE are tested first and hardest.
"""

from __future__ import annotations

import importlib.util
import json
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CERT = os.path.join(REPO_ROOT, "reverse_physics", "certificates",
                    "REVERSE_PHYSICS_CHARGE_GRADING_LOOP_STABILITY_V1.json")
MODULE = os.path.join(REPO_ROOT, "reverse_physics",
                      "charge_grading_loop_stability.py")


def module():
    spec = importlib.util.spec_from_file_location("cg", MODULE)
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

    def test_boundary_disclaims_the_loop_extension(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("no loop integral is computed", joined)
        self.assertIn("anomalous", joined)
        self.assertIn("scalar", joined)

    def test_successor_question_is_recorded(self):
        self.assertIn("inclusive",
                      self.cert["successor_question"]["question"].lower())
        self.assertIn("anomalous",
                      self.cert["successor_question"]["separate_open_risk"].lower())


class TestTheorem(unittest.TestCase):
    def setUp(self):
        self.m = module()

    def test_vertex_and_contraction_are_neutral(self):
        self.assertEqual(self.m.charge(self.m.VERTEX), 0)
        self.assertEqual(self.m.CHARGE[self.m.OM] + self.m.CHARGE[self.m.UP], 0)

    def test_charge_invariant_under_vertex_insertion(self):
        for ext in [(), (self.m.OM,), (self.m.UP,),
                    (self.m.OM, self.m.OM), (self.m.OM, self.m.UP)]:
            q0 = self.m.charge(ext)
            for nv in (0, 1, 2):
                got, _ = self.m.dress(ext, nv)
                self.assertEqual(got, {q0},
                                 "ext=%s vertices=%d" % (ext, nv))

    def test_negative_charge_stays_non_positive(self):
        """The hypothesis BT need: charges <= 0 must not become positive."""
        for nv in (0, 1, 2):
            got, _ = self.m.dress((self.m.UP, self.m.UP), nv)
            self.assertTrue(all(q <= 0 for q in got))


class TestControlsAreLive(unittest.TestCase):
    """Each control must make charge MOVE, or the theorem is unmeasured."""

    def setUp(self):
        self.m = module()

    def test_diagonal_propagator_breaks_conservation(self):
        got, _ = self.m.dress((self.m.OM,), 1, diagonal_propagator=True)
        self.assertNotEqual(got, {1})
        self.assertGreater(len(got), 1)

    def test_charged_vertex_breaks_conservation(self):
        got, _ = self.m.dress((self.m.OM,), 1,
                              vertex=(self.m.OM, self.m.OM,
                                      self.m.OM, self.m.UP))
        self.assertNotEqual(got, {1})

    def test_enumeration_is_nonvacuous(self):
        _, n = self.m.dress((self.m.OM, self.m.UP), 2)
        self.assertGreater(n, 50)

    def test_enumeration_is_fast(self):
        """It was 4m42s before the matching enumerator; keep it a Tier-1 gate."""
        import time
        t0 = time.time()
        self.m.dress((self.m.OM, self.m.UP), 2)
        self.assertLess(time.time() - t0, 5.0)


class TestQuadraticRegulatorPreflight(unittest.TestCase):
    def setUp(self):
        with open(CERT) as fh:
            self.cert = json.load(fh)

    def test_the_two_regulators_are_separated(self):
        rows = {r["term"]: r for r in
                self.cert["quadratic_regulator_preflight"]["rows"]}
        mu = rows["mu^2 * Omega * Upsilon"]
        eps = rows["(eps/2) * Omega^2"]
        self.assertEqual(mu["charge"], 0)
        self.assertTrue(mu["preserves_grading"])
        self.assertTrue(
            mu["preserves_quadratic_degeneracy_at_held_background"])
        self.assertFalse(mu["vacuum_compatible"])
        self.assertIn("tadpole", mu["vacuum_failure"])
        self.assertEqual(eps["charge"], 2)
        self.assertFalse(eps["preserves_grading"])
        self.assertFalse(
            eps["preserves_quadratic_degeneracy_at_held_background"])
        self.assertFalse(eps["vacuum_compatible"])

    def test_preflight_defers_to_exact_vacuum_certificate(self):
        self.assertEqual(
            self.cert["quadratic_regulator_preflight"]["vacuum_compatibility"],
            "REFUTED_BY_REVERSE_PHYSICS_BT_IR_REGULATOR_TRILEMMA_V1",
        )

    def test_mass_formula_is_credited_to_paper_05(self):
        self.assertIn("Paper 05",
                      self.cert["quadratic_regulator_preflight"]["imported_exactly"])


if __name__ == "__main__":
    unittest.main()
