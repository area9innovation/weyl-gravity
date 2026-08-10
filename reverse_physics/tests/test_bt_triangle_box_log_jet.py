"""Tests for the BT triangle and box logarithmic four-mass jets."""

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
    "REVERSE_PHYSICS_BT_TRIANGLE_BOX_LOG_JET_V1.json",
)
PRODUCER = os.path.join(
    REPO_ROOT, "reverse_physics", "bt_triangle_box_log_jet.py",
)
VERIFIER = os.path.join(
    REPO_ROOT, "reverse_physics", "verify_bt_triangle_box_log_jet.py",
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

    def test_dependency_lifecycle_and_scope(self):
        self.assertEqual(self.cert["dependency_tags"], ["REDUCED-MODE"])
        self.assertEqual(self.cert["lifecycle_state"], "COEFFICIENT_COMPUTED")
        self.assertIn("cut-constructible", self.cert["declared_carrier"]["scope"])

    def test_tree_identity(self):
        identity = self.cert["perfect_square_tree_identity"]
        self.assertEqual(identity["degree_zero"], "0")
        self.assertEqual(identity["degree_one"], "0")
        self.assertEqual(identity["degree_two"],
                         "A^(2)=1/2*sum_{i<j}x_i*x_j")

    def test_channel_polynomials_cancel_on_shell(self):
        cut = self.cert["channel_cut_decomposition"]
        self.assertIn("19*S^2", cut["triangle_polynomial"])
        self.assertIn("31*Sigma_cross", cut["box_polynomial"])
        self.assertEqual(
            cut["on_shell_control"],
            "P_B+P_T+P_X=0 when all x_i=0, channel by channel",
        )

    def test_interference_rows_and_reduction(self):
        jets = self.cert["interference_jets"]
        self.assertEqual(jets["triangle_rows"]["Ls"],
                         list(reversed(jets["triangle_rows"]["Lt"])))
        self.assertEqual(jets["box_rows"]["Ls"],
                         list(reversed(jets["box_rows"]["Lt"])))
        self.assertEqual(jets["complete_reduction"],
                         "J_B+J_T+J_X=15*(Ls+Lt+Lu)")

    def test_collinear_inverse_powers_cancel(self):
        expansion = self.cert["collinear_expansion"]
        self.assertEqual(expansion["complete"],
                         "J_log=45L-15ell+O(r)=15*(3L-ell)+O(r)")
        self.assertIn("r^-2 and r^-1 terms cancel", expansion["conclusion"])

    def test_finite_and_physical_boundaries_fail_closed(self):
        disposition = self.cert["disposition"]
        self.assertEqual(disposition["triangle_logarithmic_jet"], "COMPUTED")
        self.assertEqual(disposition["box_logarithmic_jet"], "COMPUTED")
        self.assertEqual(
            disposition["triangle_cut_free_finite_rational_part"],
            "NOT_COMPUTED",
        )
        self.assertEqual(disposition["external_phase_space_projector"],
                         "NOT_APPLIED")
        self.assertEqual(disposition["beyond_tree_positivity"],
                         "NOT_ESTABLISHED")


class TestIndependentRail(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verifier = load(VERIFIER, "bt_triangle_box_verifier")
        with open(CERT, encoding="utf-8") as handle:
            cls.cert = json.load(handle)

    def test_subset_tree_identity(self):
        import sympy as sp

        _, _, tree = self.verifier.subset_tree()
        self.assertEqual(tree.coefficient(0), 0)
        for mask in (3, 5, 9, 6, 10, 12):
            self.assertEqual(sp.factor(tree.coefficient(mask)), sp.Rational(1, 2))

    def test_transverse_projector_topologies(self):
        import sympy as sp

        direct = self.verifier.transverse_projector_cut()
        S, T, xa, xb, xc, xd = direct["symbols"]
        _, triangle, box = self.verifier.topology_polynomials()
        self.assertEqual(sp.expand(
            direct["triangle"] - triangle(S, T, xa, xb, xc, xd) / 12), 0)
        self.assertEqual(sp.expand(
            direct["box"] - box(S, T, xa, xb, xc, xd) / 12), 0)

    def test_subset_rows_reproduce_certificate(self):
        _, triangle, box = self.verifier.topology_polynomials()
        _, triangle_rows = self.verifier.subset_interference_rows(triangle)
        _, box_rows = self.verifier.subset_interference_rows(box)
        jets = self.cert["interference_jets"]
        self.assertEqual(triangle_rows, jets["triangle_rows"])
        self.assertEqual(box_rows, jets["box_rows"])


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

    def test_false_finite_completion_is_rejected(self):
        with open(CERT, encoding="utf-8") as handle:
            mutated = json.load(handle)
        mutated["disposition"]["box_cut_free_finite_rational_part"] = "COMPUTED"
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
