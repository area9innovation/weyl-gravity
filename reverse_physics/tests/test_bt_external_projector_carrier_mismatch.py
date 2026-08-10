"""Tests for the BT external projector and carrier mismatch certificate."""

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
    "REVERSE_PHYSICS_BT_EXTERNAL_PROJECTOR_CARRIER_MISMATCH_V1.json",
)
PRODUCER = os.path.join(
    REPO_ROOT, "reverse_physics", "bt_external_projector_carrier_mismatch.py",
)
VERIFIER = os.path.join(
    REPO_ROOT, "reverse_physics", "verify_bt_external_projector_carrier_mismatch.py",
)
MISE_PYTHON = (
    "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3"
)


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

    def test_external_projector_coefficient(self):
        projector = self.cert["external_projector"]
        self.assertEqual(projector["massless_phase_value"], "1/(256*pi^2*s)")
        self.assertIn("5*lambda^6", projector["projected_virtual_log_rate"])

    def test_ratios_are_distinct(self):
        self.assertIn("ell=log(-t/s)",
                      self.cert["external_projector"]["hard_collinear_form"])
        self.assertIn("rho=x1/x0",
                      self.cert["carrier_response"]["rescaling"])

    def test_response_mismatch(self):
        response = self.cert["carrier_response"]
        self.assertEqual(response["virtual_hard_log_response"], "0")
        self.assertEqual(response["real_finite_part_shift"], "-(3/8)*log(c)")
        self.assertEqual(response["comparison"],
                         "NONCANCELLING_ON_CURRENT_CARRIERS")

    def test_physical_claims_remain_open(self):
        disposition = self.cert["disposition"]
        self.assertEqual(disposition["hard_log_external_projector"], "APPLIED")
        self.assertEqual(disposition["virtual_external_mass_boundary_layer"],
                         "NOT_COMPUTED")
        self.assertEqual(disposition["real_virtual_cancellation"], "NOT_COMPUTED")
        self.assertEqual(disposition["beyond_tree_positivity"], "NOT_ESTABLISHED")


class TestExactAlgebra(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.producer = load(PRODUCER, "bt_external_projector_producer")
        cls.verifier = load(VERIFIER, "bt_external_projector_verifier")

    def test_phase_constant_only(self):
        interference = {(1, 1, 1, 1): Fraction(2)}
        phase = {(0, 0, 0, 0): Fraction(3),
                 (1, 0, 0, 0): Fraction(5)}
        self.assertEqual(self.producer.top_coefficient(interference, phase), 6)

    def test_lower_degree_mutation(self):
        product = self.verifier.multiply(
            {(0, 1, 1, 1): Fraction(2)},
            {(0, 0, 0, 0): Fraction(3),
             (1, 0, 0, 0): Fraction(5)},
        )
        self.assertEqual(product[(1, 1, 1, 1)], 10)


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
        mutated["disposition"]["real_virtual_cancellation"] = "COMPUTED"
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
