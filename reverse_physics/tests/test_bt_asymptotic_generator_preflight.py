"""Falsification tests for the BT asymptotic-generator preflight."""

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
    "REVERSE_PHYSICS_BT_ASYMPTOTIC_GENERATOR_PREFLIGHT_V1.json",
)
PRODUCER = os.path.join(
    REPO_ROOT, "reverse_physics", "bt_asymptotic_generator_preflight.py",
)
VERIFIER = os.path.join(
    REPO_ROOT, "reverse_physics", "verify_bt_asymptotic_generator_preflight.py",
)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class TestCertificate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.cert = json.load(handle)

    def test_tags_and_lifecycle(self):
        self.assertEqual(
            self.cert["dependency_tags"],
            ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        )
        self.assertEqual(self.cert["lifecycle_state"], "CLASSIFIED")

    def test_v1_is_explicitly_superseded(self):
        self.assertEqual(
            self.cert["v1_supersession"]["status"],
            "SUPERSEDED_NORMALIZATION",
        )
        self.assertEqual(
            self.cert["v1_supersession"]["uncancelled_absolute_coefficient"],
            {"numerator": 87, "denominator": 16384},
        )

    def test_physical_gate_stays_open(self):
        disposition = self.cert["disposition"]
        self.assertEqual(
            disposition["ordinary_single_denominator_fock_generator"],
            "EXACT_OBSTRUCTION",
        )
        self.assertEqual(
            disposition["jordan_distributional_generator"],
            "NOT_CONSTRUCTED",
        )
        self.assertEqual(
            disposition["physical_nlo_probability"], "NOT_ESTABLISHED",
        )


class TestExactAlgebra(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.producer = load(PRODUCER, "bt_asymptotic_preflight_producer")
        cls.verifier = load(VERIFIER, "bt_asymptotic_preflight_verifier")

    def test_rate_ratio(self):
        result = self.producer.normalization()
        self.assertEqual(result["gram_per_pair"], Fraction(1, 48))
        self.assertEqual(result["gram_total"], Fraction(1, 16))
        self.assertEqual(result["old_v1_residual"], Fraction(87, 16384))

    def test_corrected_algebraic_amplitude(self):
        result = self.producer.projector()
        self.assertEqual(
            result["amplitude"] * result["amplitude"],
            self.producer.Qsqrt3(Fraction(1, 48)),
        )
        self.assertTrue(self.producer.all_zero(result["defect_1"]))
        self.assertTrue(self.producer.all_zero(result["defect_2"]))

    def test_energy_deficit_fixtures(self):
        for energy, zeta in [
            (Fraction(5), Fraction(1, 3)),
            (Fraction(7, 2), Fraction(2, 5)),
        ]:
            t_coefficient, deficit = self.verifier.collinear_coefficients(
                energy, zeta
            )
            self.assertEqual(deficit / t_coefficient, 1 / (2 * energy))

    def test_recorded_certificate_is_deterministic(self):
        run = subprocess.run(
            [sys.executable, PRODUCER, "--check"], cwd=REPO_ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("RESULT: PASS", run.stdout)


class TestIndependentVerifier(unittest.TestCase):
    def run_mutation(self, mutate):
        with open(CERT, encoding="utf-8") as handle:
            payload = json.load(handle)
        mutate(payload)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                         encoding="utf-8") as handle:
            json.dump(payload, handle)
            handle.flush()
            return subprocess.run(
                [sys.executable, VERIFIER, "--verify", handle.name],
                cwd=REPO_ROOT, text=True, capture_output=True, check=False,
            )

    def test_verifier_accepts_certificate(self):
        run = subprocess.run(
            [sys.executable, VERIFIER], cwd=REPO_ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("RESULT: PASS", run.stdout)

    def test_absolute_coefficient_mutation_is_rejected(self):
        def mutate(payload):
            payload["normalization_ledger"]["gram_per_pair"] = {
                "numerator": 1, "denominator": 512,
            }
        run = self.run_mutation(mutate)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("[FAIL] independent_rate_normalization", run.stdout)

    def test_nonzero_ordinary_kernel_mutation_is_rejected(self):
        def mutate(payload):
            payload["cubic_generator_preflight"]["ordinary_gram_target"] = {
                "numerator": 1, "denominator": 48,
            }
        run = self.run_mutation(mutate)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("[FAIL] single_vs_double_denominator", run.stdout)


if __name__ == "__main__":
    unittest.main()
