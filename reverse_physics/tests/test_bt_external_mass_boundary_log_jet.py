"""Tests for the BT external-mass boundary logarithmic jet."""

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
    "REVERSE_PHYSICS_BT_EXTERNAL_MASS_BOUNDARY_LOG_JET_V1.json",
)
PRODUCER = os.path.join(
    REPO_ROOT, "reverse_physics", "bt_external_mass_boundary_log_jet.py",
)
VERIFIER = os.path.join(
    REPO_ROOT, "reverse_physics", "verify_bt_external_mass_boundary_log_jet.py",
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

    def test_boundary_polynomial(self):
        result = self.cert["boundary_cut_result"]
        self.assertIn("-5*(a2*a3", result["square_free_polynomial"])
        self.assertIn("10*sum_", result["crossed_leg_loop_term"])

    def test_projected_rate(self):
        result = self.cert["four_mass_interference"]
        self.assertIn("12*(L1+L2+L3+L4)", result["reduced_top_coefficient"])
        self.assertIn("3*lambda^6", result["projected_rate"])
        self.assertIn("128*pi^4*s", result["projected_rate"])

    def test_regulator_response(self):
        response = self.cert["regulator_response"]
        self.assertIn("sum_i log(c_i)", response["rate_shift"])
        self.assertEqual(
            response["comparison_status"],
            "NOT_COMPARABLE_WITHOUT_REGULATOR_GLUING_AND_FULL_REAL_PHASE_SPACE",
        )

    def test_claims_fail_closed(self):
        disposition = self.cert["disposition"]
        self.assertEqual(disposition["complete_external_mass_boundary_log_jet"],
                         "COMPUTED")
        self.assertEqual(disposition["physical_collinear_family_dependence"],
                         "INDEPENDENT_OF_ZETA_AND_CHI")
        self.assertEqual(disposition["real_virtual_cancellation"],
                         "NOT_COMPUTED")
        self.assertEqual(disposition["beyond_tree_positivity"],
                         "NOT_ESTABLISHED")


class TestIndependentAlgebra(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verifier = load(VERIFIER, "bt_external_boundary_verifier")

    def test_invariant_cut(self):
        result = self.verifier.invariant_boundary_cut()
        self.assertTrue(result["identity"])

    def test_symbolic_splitting_family(self):
        result = self.verifier.invariant_symbolic_family_cut()
        self.assertTrue(result["identity"])
        self.assertTrue(result["zeta_independent"])
        self.assertTrue(result["chi_independent"])

    def test_sparse_top_weights(self):
        self.assertEqual(
            self.verifier.interference_weights(),
            (Fraction(12),) * 4,
        )

    def test_mutated_coefficient_changes_answer(self):
        self.assertEqual(
            self.verifier.interference_weights(pair_weight=8),
            (Fraction(9),) * 4,
        )


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
