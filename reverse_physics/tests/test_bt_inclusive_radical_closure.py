"""Falsification tests for BT finite inclusive radical closure."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CERT = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_INCLUSIVE_RADICAL_CLOSURE_V1.json",
)
PRODUCER = os.path.join(REPO_ROOT, "reverse_physics",
                        "bt_inclusive_radical_closure.py")
VERIFIER = os.path.join(REPO_ROOT, "reverse_physics",
                        "verify_bt_inclusive_radical_closure.py")


def load_module():
    spec = importlib.util.spec_from_file_location("bt_inclusive", PRODUCER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestCertificateGate(unittest.TestCase):
    def setUp(self):
        with open(CERT, encoding="utf-8") as handle:
            self.cert = json.load(handle)

    def test_checks_tag_and_lifecycle(self):
        self.assertTrue(self.cert["checks"]["ok"])
        self.assertEqual(self.cert["checks"]["passed"],
                         self.cert["checks"]["total"])
        self.assertEqual(self.cert["dependency_tags"], ["LOCAL-ALGEBRAIC"])
        self.assertEqual(self.cert["lifecycle_state"], "CLASSIFIED")

    def test_physical_inclusive_map_stays_fail_closed(self):
        disposition = self.cert["disposition"]
        self.assertEqual(disposition["radical_closure"],
                         "PROVED_FOR_FINITE_EQ20_COMPLETENESS_KERNEL")
        self.assertEqual(disposition["physical_inclusive_map"],
                         "NOT_CONSTRUCTED")
        self.assertEqual(disposition["real_virtual_cancellation"],
                         "NOT_COMPUTED")
        self.assertEqual(disposition["beyond_tree_positivity"],
                         "NOT_ESTABLISHED")

    def test_missing_objects_and_claim_boundary_are_populated(self):
        self.assertGreaterEqual(len(self.cert["missing_object_ledger"]), 5)
        boundary = " ".join(self.cert["does_not_establish"])
        self.assertIn("KLN", boundary)
        self.assertIn("LORENTZIAN-CAUSAL", boundary)
        self.assertIn("trace class", boundary)


class TestExactChargeAlgebra(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def test_bt_adjoint_preserves_charge_and_nullity(self):
        c = self.module.Series({-1: Fraction(2, 3), -4: Fraction(-5, 7)})
        self.assertEqual(c.dagger(), c)
        self.assertTrue(c.strictly_negative())
        self.assertEqual(c.trace(), 0)
        self.assertEqual((c.dagger() * c).trace(), 0)

    def test_negative_sector_is_only_a_relative_radical(self):
        negative = self.module.Series.monomial(-1)
        positive = self.module.Series.monomial(+1)
        self.assertEqual((negative.dagger() * positive).trace(), 1)
        with open(CERT, encoding="utf-8") as handle:
            certificate = json.load(handle)
        boundary = " ".join(certificate["does_not_establish"])
        self.assertIn("full graded algebra", boundary)

    def test_hilbert_adjoint_mutation_exposes_negative_component(self):
        c = self.module.Series({-1: Fraction(2, 3), -4: Fraction(-5, 7)})
        product = c.dagger(preserves_charge=False) * c
        self.assertGreater(product.trace(), 0)

    def test_eq20_tensor_powers_preserve_every_negative_fixture(self):
        kernel = [self.module.kernel_term(+1, -1),
                  self.module.kernel_term(-1, +1)]
        for charge in range(-8, 0):
            value = self.module.Series.monomial(charge, Fraction(3, 11))
            for power in range(7):
                image = self.module.apply_kernel(
                    value, self.module.tensor_power_kernel(kernel, power))
                self.assertEqual(image, Fraction(2**power) * value)
                self.assertTrue(image.strictly_negative())

    def test_positive_shift_has_sharp_trace_witness(self):
        for shift in range(1, 7):
            left = min(3, shift)
            right = shift - left
            value = self.module.Series.monomial(-shift)
            image = self.module.sandwich(value, left, right)
            self.assertEqual(image.trace(), 1)

    def test_negative_diagonal_is_an_independence_control(self):
        value = self.module.Series.monomial(-1)
        image = self.module.apply_kernel(
            value, [self.module.kernel_term(-1, -1)])
        self.assertEqual(image.support(), [-3])
        self.assertTrue(image.strictly_negative())

    def test_recorded_certificate_is_deterministic(self):
        run = subprocess.run(
            [sys.executable, PRODUCER, "--check"], cwd=REPO_ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


class TestIndependentVerifier(unittest.TestCase):
    def test_independent_verifier_accepts_certificate(self):
        run = subprocess.run(
            [sys.executable, VERIFIER], cwd=REPO_ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("RESULT: PASS", run.stdout)

    def test_positive_diagonal_mutation_is_rejected(self):
        with open(CERT, encoding="utf-8") as handle:
            mutated = json.load(handle)
        term = mutated["eq20_completeness_kernel"]["nonzero_terms"][0]
        term["right_charge"] = +1
        term["total_shift"] = +2
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                         encoding="utf-8") as handle:
            json.dump(mutated, handle)
            handle.flush()
            run = subprocess.run(
                [sys.executable, VERIFIER, "--verify", handle.name],
                cwd=REPO_ROOT, text=True, capture_output=True, check=False,
            )
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("[FAIL] Eq20_kernel_exact", run.stdout)


if __name__ == "__main__":
    unittest.main()
