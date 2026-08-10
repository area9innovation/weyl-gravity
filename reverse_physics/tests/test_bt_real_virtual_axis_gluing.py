"""Tests for the BT real/virtual axis-compatible gluing obstruction."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from fractions import Fraction


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CERT = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_REAL_VIRTUAL_AXIS_GLUING_V1.json",
)
PRODUCER = os.path.join(
    REPO_ROOT, "reverse_physics", "bt_real_virtual_axis_gluing.py",
)
VERIFIER = os.path.join(
    REPO_ROOT, "reverse_physics", "verify_bt_real_virtual_axis_gluing.py",
)
MISE_PYTHON = "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestCertificate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.cert = json.load(handle)

    def test_dependency_and_lifecycle(self):
        self.assertEqual(self.cert["dependency_tags"], ["REDUCED-MODE"])
        self.assertEqual(self.cert["lifecycle_state"], "COEFFICIENT_COMPUTED")

    def test_general_kernel_is_angle_independent(self):
        kernel = self.cert["real_kernel"]
        self.assertEqual(kernel["splitting_fraction"],
                         "zeta cancels identically")
        self.assertEqual(kernel["outer_ratio"],
                         "chi=-T/S cancels identically")

    def test_phase_sign_and_pair_sum(self):
        phase = self.cert["phase_and_combinatorics"]
        self.assertEqual(phase["delta_prime_sign"], "(-1)^5=-1")
        self.assertEqual(phase["unordered_final_pairs"], 3)
        self.assertIn("+3*lambda^6", phase["common_three_pair_shift"])

    def test_scoped_obstruction(self):
        disposition = self.cert["disposition"]
        self.assertEqual(disposition["logarithmic_real_virtual_cancellation"],
                         "EXACT_OBSTRUCTION")
        self.assertEqual(disposition["full_nlo_quotient_trace"],
                         "NOT_COMPUTED")
        self.assertEqual(disposition["physical_nlo_probability"],
                         "NOT_ESTABLISHED")


class TestIndependentAlgebra(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verifier = load(VERIFIER, "bt_axis_gluing_verifier")

    def test_phase_coefficients(self):
        before, after, per_pair, all_pairs = self.verifier.phase_coefficients()
        self.assertEqual(before, Fraction(1, 768))
        self.assertEqual(after, Fraction(1, 192))
        self.assertEqual(per_pair, Fraction(1, 512))
        self.assertEqual(all_pairs, Fraction(3, 512))

    def test_physical_and_analytic_axis_maps(self):
        self.assertEqual(self.verifier.threshold_map_ratios(), (1, 1))

    def test_mutated_amplitude_normalization_changes_response(self):
        _, _, per_pair, all_pairs = self.verifier.phase_coefficients(
            amplitude_norm=32
        )
        self.assertEqual(per_pair, Fraction(1, 1024))
        self.assertEqual(all_pairs, Fraction(3, 1024))


class TestExecutableRails(unittest.TestCase):
    def test_producer_reproduces_certificate(self):
        run = subprocess.run(
            [MISE_PYTHON, PRODUCER, "--check"], cwd=REPO_ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("RESULT: PASS", run.stdout)

    def test_verifier_accepts_certificate(self):
        run = subprocess.run(
            [MISE_PYTHON, VERIFIER], cwd=REPO_ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("RESULT: PASS", run.stdout)

    def test_false_cancellation_is_rejected(self):
        with open(CERT, encoding="utf-8") as handle:
            mutated = json.load(handle)
        mutated["virtual_comparison"]["disposition"] = "CANCELS"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                         encoding="utf-8") as handle:
            json.dump(mutated, handle)
            handle.flush()
            run = subprocess.run(
                [MISE_PYTHON, VERIFIER, "--verify", handle.name],
                cwd=REPO_ROOT, text=True, capture_output=True, check=False,
            )
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("[FAIL] strict_schema", run.stdout)


if __name__ == "__main__":
    unittest.main()
