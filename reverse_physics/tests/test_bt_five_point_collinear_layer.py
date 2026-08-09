"""Falsification tests for the BT five-point collinear boundary layer."""

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
    "REVERSE_PHYSICS_BT_FIVE_POINT_COLLINEAR_LAYER_V1.json",
)
PRODUCER = os.path.join(
    REPO_ROOT, "reverse_physics", "bt_five_point_collinear_layer.py")
VERIFIER = os.path.join(
    REPO_ROOT, "reverse_physics", "verify_bt_five_point_collinear_layer.py")
MISE_PYTHON = (
    "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3"
)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fraction(payload):
    return Fraction(payload["numerator"], payload["denominator"])


class TestCertificateBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def test_dependency_and_lifecycle(self):
        self.assertEqual(self.certificate["dependency_tags"], ["REDUCED-MODE"])
        self.assertEqual(self.certificate["lifecycle_state"],
                         "COEFFICIENT_COMPUTED")
        self.assertTrue(self.certificate["checks"]["ok"])

    def test_boundary_is_exactly_total_order_five(self):
        amplitude = self.certificate["amplitude_boundary"]
        phase = self.certificate["phase_space_boundary"]
        self.assertEqual(amplitude["delta_order"], 2)
        self.assertEqual(phase["window"], [10, 11])
        self.assertGreater(fraction(phase["strict_lower_bound"]), 0)
        self.assertEqual(
            self.certificate["disposition"][
                "collinear_boundary_total_order_five"],
            "STRICTLY_NONZERO_ON_DECLARED_RAY",
        )

    def test_result_does_not_promote_the_common_ray(self):
        disposition = self.certificate["disposition"]
        self.assertEqual(disposition["mixed_five_mass_distribution"],
                         "NOT_DEFINED_WITHOUT_PRESCRIPTION")
        self.assertEqual(disposition["physical_integrated_2to3_probability"],
                         "NOT_COMPUTED")
        boundary = " ".join(self.certificate["does_not_establish"])
        self.assertIn("nonzero mixed", boundary)
        self.assertIn("LORENTZIAN-CAUSAL", boundary)

    def test_rational_physical_limit_fixture(self):
        physical = self.certificate["physical_limit_fixture"]
        self.assertTrue(all(fraction(value) == 0 for value in physical["sum"]))
        self.assertTrue(all(fraction(value) == 0
                            for value in physical["external_squares"]))
        self.assertEqual(
            [fraction(value) for value in physical["cyclic_invariants"]],
            [Fraction(0), Fraction(32, 3), Fraction(-8), Fraction(16),
             Fraction(-8, 3)],
        )


class TestIndependentLaurentRail(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verifier = load(VERIFIER, "bt5_collinear_verifier")

    def test_correct_sign_has_two_exact_cancellations(self):
        amplitude = self.verifier.build_series_amplitude(
            self.verifier.FractionDomain(), 10)
        self.assertEqual(amplitude.coefficient(0), 0)
        self.assertEqual(amplitude.coefficient(1), 0)
        self.assertEqual(amplitude.coefficient(2), Fraction(-140679, 400))

    def test_relative_sign_mutation_destroys_cancellation(self):
        amplitude = self.verifier.build_series_amplitude(
            self.verifier.FractionDomain(), 10, relative_sign=1)
        self.assertEqual(amplitude.coefficient(0), Fraction(15848, 75))


class TestExecutableRails(unittest.TestCase):
    def test_fast_producer_accepts_recorded_certificate(self):
        run = subprocess.run(
            [MISE_PYTHON, PRODUCER, "--check"], cwd=REPO_ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("RESULT: PASS", run.stdout)

    def test_independent_verifier_accepts_recorded_certificate(self):
        run = subprocess.run(
            [MISE_PYTHON, VERIFIER], cwd=REPO_ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("RESULT: PASS", run.stdout)

    def test_false_physical_promotion_is_rejected(self):
        with open(CERT, encoding="utf-8") as handle:
            mutated = json.load(handle)
        mutated["disposition"]["physical_integrated_2to3_probability"] = (
            "COMPUTED"
        )
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
        self.assertIn("[FAIL] fail_closed_disposition", run.stdout)


if __name__ == "__main__":
    unittest.main()
