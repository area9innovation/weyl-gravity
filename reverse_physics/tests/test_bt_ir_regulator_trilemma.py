"""Falsification tests for the BT local-potential regulator trilemma."""

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
    "REVERSE_PHYSICS_BT_IR_REGULATOR_TRILEMMA_V1.json",
)
PRODUCER = os.path.join(REPO_ROOT, "reverse_physics",
                        "bt_ir_regulator_trilemma.py")
VERIFIER = os.path.join(REPO_ROOT, "reverse_physics",
                        "verify_bt_ir_regulator_trilemma.py")


def load_module():
    spec = importlib.util.spec_from_file_location("bt_trilemma", PRODUCER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestCertificateGate(unittest.TestCase):
    def setUp(self):
        with open(CERT, encoding="utf-8") as handle:
            self.cert = json.load(handle)

    def test_checks_and_boundary(self):
        self.assertTrue(self.cert["checks"]["ok"])
        self.assertEqual(self.cert["checks"]["passed"],
                         self.cert["checks"]["total"])
        self.assertEqual(self.cert["dependency_tags"], ["LOCAL-ALGEBRAIC"])
        self.assertEqual(self.cert["lifecycle_state"], "CLASSIFIED")
        boundary = " ".join(self.cert["does_not_establish"])
        self.assertIn("LORENTZIAN-CAUSAL", boundary)
        self.assertIn("Bateman-Turok", boundary)

    def test_four_counterexample_witnesses_are_populated(self):
        witnesses = self.cert["independence_witnesses"]
        self.assertEqual(len(witnesses), 4)
        self.assertEqual(
            {row["drop"] for row in witnesses},
            {"stationarity", "exact fixed-sector SO+(1,1) invariance",
             "coincident pole", "nonzero infrared gap"},
        )
        self.assertTrue(all(row["witness"] for row in witnesses))

    def test_predecessor_claim_is_explicitly_scoped(self):
        correction = self.cert["correction_to_predecessor"]
        self.assertIn("loop order", correction["retained"])
        self.assertIn("IR regulator", correction["withdrawn"])
        self.assertIn("nonstationary", correction["replacement"])


class TestExactProducer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()
        cls.cert = cls.module.build()

    def test_stationary_bt_branch_has_massless_double_root(self):
        terms = self.cert["polynomial_identities"][
            "BT_branch_pole_polynomial"]["terms"]
        self.assertEqual(terms, [
            {"coefficient": {"numerator": -1, "denominator": 1},
             "powers": {"f1": 2}},
            {"coefficient": {"numerator": 2, "denominator": 1},
             "powers": {"z": 1, "f1": 1}},
            {"coefficient": {"numerator": -1, "denominator": 1},
             "powers": {"z": 2}},
        ])
        gradient = self.cert["polynomial_identities"]["BT_branch_gradient"]
        self.assertEqual(gradient["components"][0], [])
        self.assertTrue(gradient["components"][1])

    def test_mass_term_fails_stationarity_at_held_background(self):
        held = self.cert["polynomial_identities"][
            "mass_deformation_held_background"]
        tadpole = held["gradient"][1][0]
        self.assertEqual(tadpole["powers"], {"v": 1, "mu2": 1})
        self.assertEqual(tadpole["coefficient"],
                         {"numerator": 1, "denominator": 1})

    def test_true_stationary_branch_has_two_distinct_roots(self):
        terms = self.cert["polynomial_identities"][
            "mass_deformation_true_vacuum"]["pole_terms"]

        def evaluate(z, mu2):
            total = Fraction(0)
            for term in terms:
                value = Fraction(term["coefficient"]["numerator"],
                                 term["coefficient"]["denominator"])
                value *= z ** term["powers"].get("z", 0)
                value *= mu2 ** term["powers"].get("mu2", 0)
                total += value
            return total

        for mu2 in (Fraction(2, 3), Fraction(-5, 4), Fraction(7)):
            self.assertEqual(evaluate(Fraction(0), mu2), 0)
            self.assertEqual(evaluate(-2 * mu2, mu2), 0)
            self.assertNotEqual(Fraction(0), -2 * mu2)

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

    def test_independent_verifier_rejects_decisive_mutation(self):
        with open(CERT, encoding="utf-8") as handle:
            mutated = json.load(handle)
        mutated["polynomial_identities"]["mass_deformation_true_vacuum"][
            "pole_terms"][0]["coefficient"]["numerator"] = -3
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                         encoding="utf-8") as handle:
            json.dump(mutated, handle)
            handle.flush()
            run = subprocess.run(
                [sys.executable, VERIFIER, "--verify", handle.name],
                cwd=REPO_ROOT, text=True, capture_output=True, check=False,
            )
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("[FAIL] independent_mass_deformation_derivation",
                      run.stdout)


if __name__ == "__main__":
    unittest.main()
