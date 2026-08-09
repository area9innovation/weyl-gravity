"""Tests for the BT independent-mass collinear-threshold obstruction."""

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
    "REVERSE_PHYSICS_BT_FIVE_POINT_INDEPENDENT_MASS_THRESHOLD_V1.json",
)
PRODUCER = os.path.join(
    REPO_ROOT, "reverse_physics",
    "bt_five_point_independent_mass_threshold.py",
)
VERIFIER = os.path.join(
    REPO_ROOT, "reverse_physics",
    "verify_bt_five_point_independent_mass_threshold.py",
)
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

    def test_tag_lifecycle_and_checks(self):
        self.assertEqual(self.certificate["dependency_tags"], ["REDUCED-MODE"])
        self.assertEqual(self.certificate["lifecycle_state"],
                         "COEFFICIENT_COMPUTED")
        self.assertTrue(self.certificate["checks"]["ok"])
        self.assertEqual(self.certificate["checks"]["passed"], 12)

    def test_logarithmic_mixed_slope_is_nonzero(self):
        threshold = self.certificate["threshold_result"]
        self.assertEqual(fraction(threshold["logarithmic_slope_coefficient"]),
                         Fraction(-3, 8))
        obstruction = self.certificate["ordinary_derivative_obstruction"]
        self.assertEqual(obstruction["ordinary_limit"],
                         "DIVERGES_TO_POSITIVE_INFINITY")

    def test_finite_part_has_scale_ambiguity(self):
        finite_part = self.certificate["finite_part_ambiguity"]
        self.assertEqual(finite_part["value"], "FP_c=-1/8-3/8*log(c)")
        self.assertEqual(finite_part["c_four_shift"], "-3/4*log(2)")
        self.assertEqual(finite_part["disposition"],
                         "REGULATOR_NORMALIZATION_DEPENDENT")

    def test_four_ray_defect_is_certifiably_negative(self):
        witness = self.certificate["four_ray_nonpolynomial_witness"]
        lower, upper = map(fraction, witness["defect_bounds"])
        self.assertLess(lower, upper)
        self.assertLess(upper, 0)
        self.assertEqual(witness["annihilator_weights"], [-10, 15, -6, 1])

    def test_physical_claims_remain_fail_closed(self):
        disposition = self.certificate["disposition"]
        self.assertEqual(
            disposition["ordinary_reduced_mixed_five_mass_derivative"],
            "DOES_NOT_EXIST",
        )
        self.assertEqual(disposition["full_five_body_phase_space_projector"],
                         "NOT_CONSTRUCTED")
        self.assertEqual(disposition["physical_integrated_2to3_probability"],
                         "NOT_COMPUTED")


class TestIndependentExactRail(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verifier = load(VERIFIER, "bt5_mass_threshold_verifier")

    def test_invariant_amplitude_reproduces_projection(self):
        self.assertTrue(self.verifier.independent_amplitude_projection())

    def test_exp_y_rationalization_reproduces_integral(self):
        self.assertTrue(self.verifier.independent_threshold_integral())

    def test_atanh_bounds_need_no_floating_point(self):
        lower, upper = self.verifier.log_bounds(2)
        self.assertIsInstance(lower, Fraction)
        self.assertIsInstance(upper, Fraction)
        self.assertLess(lower, upper)


class TestExecutableRails(unittest.TestCase):
    def test_producer_accepts_recorded_certificate(self):
        run = subprocess.run(
            [MISE_PYTHON, PRODUCER, "--check"], cwd=REPO_ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("RESULT: PASS", run.stdout)

    def test_verifier_accepts_recorded_certificate(self):
        run = subprocess.run(
            [MISE_PYTHON, VERIFIER], cwd=REPO_ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("RESULT: PASS", run.stdout)

    def test_false_canonical_finite_part_is_rejected(self):
        with open(CERT, encoding="utf-8") as handle:
            mutated = json.load(handle)
        mutated["finite_part_ambiguity"]["disposition"] = "CANONICAL"
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
