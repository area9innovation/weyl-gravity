"""Tests for the BT perfect-square one-loop RG separatrix."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import tempfile
import unittest


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CERT = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_PERFECT_SQUARE_RG_SEPARATRIX_V1.json",
)
PRODUCER = os.path.join(
    REPO_ROOT, "reverse_physics", "bt_perfect_square_rg_separatrix.py",
)
VERIFIER = os.path.join(
    REPO_ROOT, "reverse_physics", "verify_bt_perfect_square_rg_separatrix.py",
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

    def test_claim_boundary(self):
        self.assertEqual(self.cert["dependency_tags"], ["LOCAL-ALGEBRAIC"])
        self.assertEqual(self.cert["lifecycle_state"], "COEFFICIENT_COMPUTED")
        self.assertEqual(
            self.cert["disposition"]["renormalized_four_leg_loop_jet"],
            "NOT_COMPUTED",
        )

    def test_coupling_map_and_restricted_beta(self):
        self.assertEqual(self.cert["coupling_map"]["lambda3"], "-lambda")
        self.assertEqual(self.cert["coupling_map"]["lambda4"], "-lambda^2/2")
        beta = self.cert["one_loop_beta_restriction"]
        self.assertEqual(beta["restricted_beta_lambda"],
                         "-5*lambda^3/(16*pi^2)")
        self.assertIn("5/(8*pi^2)", beta["integrated_running"])

    def test_unique_nonzero_quartic_parabola(self):
        rows = self.cert["one_loop_beta_restriction"][
            "monomial_parabola_classification"]["roots"]
        self.assertEqual(len(rows), 2)
        self.assertEqual(sum(row["has_nonzero_quartic_coupling"] for row in rows), 1)

    def test_four_point_sectors(self):
        rows = self.cert["four_point_one_loop_sectors"]["rows"]
        self.assertEqual(
            [(row["cubic_vertices"], row["quartic_vertices"],
              row["internal_lines"]) for row in rows],
            [(4, 0, 4), (2, 1, 3), (0, 2, 2)],
        )
        self.assertTrue(all(row["ps_lambda_power"] == 4 for row in rows))

    def test_finite_jet_remains_open(self):
        witness = self.cert["finite_jet_nonuniqueness"]
        self.assertEqual(witness["carrier_dimension"], 16)
        self.assertIn("x1*x2*x3*x4", witness["crossing_symmetric_mutation"])
        self.assertEqual(self.cert["real_threshold_matching"]["status"],
                         "NOT_COMPUTED")


class TestIndependentRail(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verifier = load(VERIFIER, "bt_ps_rg_verifier")

    def test_symbolic_rg_identities(self):
        self.assertTrue(all(self.verifier.exact_rg_identities().values()))

    def test_dual_number_counterterms(self):
        self.assertTrue(all(
            self.verifier.exact_counterterm_identities().values()
        ))

    def test_diophantine_sector_enumeration(self):
        self.assertEqual(
            self.verifier.exact_sector_enumeration(),
            [(0, 2, 2), (2, 1, 3), (4, 0, 4)],
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

    def test_false_loop_completion_is_rejected(self):
        with open(CERT, encoding="utf-8") as handle:
            mutated = json.load(handle)
        mutated["disposition"]["renormalized_four_leg_loop_jet"] = "COMPUTED"
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
