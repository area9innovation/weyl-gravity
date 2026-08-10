#!/usr/bin/env python3
"""Focused tests for the BT UV hard-scattering physical result."""

from __future__ import annotations

import copy
import json
import os
import subprocess
import tempfile
import unittest
from fractions import Fraction

from reverse_physics import bt_uv_hard_scattering_law as producer


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT_PATH = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "certificates",
    "REVERSE_PHYSICS_BT_UV_HARD_SCATTERING_LAW_V1.json",
)
VERIFIER = os.path.join(REPO_ROOT, "reverse_physics", "verify_bt_uv_hard_scattering_law.py")


def load_certificate():
    with open(CERT_PATH, encoding="utf-8") as handle:
        return json.load(handle)


def fraction(item):
    return Fraction(item["numerator"], item["denominator"])


class TestPhysicalResult(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cert = load_certificate()

    def test_dependency_tags_and_lifecycle(self):
        self.assertEqual(
            self.cert["dependency_tags"], ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
        )
        self.assertEqual(self.cert["lifecycle_state"], "COEFFICIENT_COMPUTED")

    def test_callan_symanzik_identity(self):
        cs = self.cert["callan_symanzik_certificate"]
        self.assertEqual(fraction(cs["beta_on_born_scale_derivative"]), Fraction(-15, 128))
        self.assertEqual(fraction(cs["explicit_loop_scale_derivative"]), Fraction(15, 128))
        self.assertEqual(fraction(cs["residual"]), 0)

    def test_nlo_hard_log_coefficient(self):
        ll = self.cert["leading_log_hard_rate"]
        self.assertEqual(fraction(ll["nlo_relative_coefficient_without_pi"]), Fraction(-5, 8))
        self.assertEqual(fraction(ll["nlo_absolute_coefficient_without_pi"]), Fraction(-15, 256))

    def test_universal_uv_constants(self):
        fixed = fraction(self.cert["universal_uv_law"]["fixed_angle_constant_without_pi2"])
        window = fraction(self.cert["detector_window"]["constant_without_pi3_cos_theta0"])
        self.assertEqual(fixed, Fraction(24, 25))
        self.assertEqual(window, 4 * fixed)

    def test_physical_scope_is_nonforward_and_fail_closed(self):
        disposition = self.cert["disposition"]
        self.assertEqual(disposition["nonforward_window_uv_scaling"], "PHYSICAL_HARD_RESULT")
        self.assertEqual(disposition["full_inclusive_nlo_probability"], "NOT_ESTABLISHED")
        self.assertEqual(disposition["jordan_asymptotic_generator"], "NOT_CONSTRUCTED")
        self.assertIn("0<theta0<pi/2", self.cert["detector_window"]["definition"])

    def test_certificate_is_deterministic(self):
        self.assertEqual(producer.build(), self.cert)


class TestIndependentVerifier(unittest.TestCase):
    def run_verifier(self, certificate):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(certificate, handle)
            path = handle.name
        try:
            return subprocess.run(
                ["python3", VERIFIER, "--certificate", path],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        finally:
            os.unlink(path)

    def test_verifier_accepts_certificate(self):
        result = self.run_verifier(load_certificate())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_two_channel_mutation_is_rejected(self):
        mutated = copy.deepcopy(load_certificate())
        mutated["callan_symanzik_certificate"]["channel_log_count"] = 2
        result = self.run_verifier(mutated)
        self.assertNotEqual(result.returncode, 0)

    def test_false_inclusive_promotion_is_rejected(self):
        mutated = copy.deepcopy(load_certificate())
        mutated["disposition"]["full_inclusive_nlo_probability"] = "ESTABLISHED"
        result = self.run_verifier(mutated)
        self.assertNotEqual(result.returncode, 0)

    def test_provenance_hash_mutation_is_rejected(self):
        mutated = copy.deepcopy(load_certificate())
        mutated["provenance"]["inputs"][0]["sha256"] = "0" * 64
        result = self.run_verifier(mutated)
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
