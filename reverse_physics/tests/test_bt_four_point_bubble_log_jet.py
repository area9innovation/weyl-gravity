"""Tests for the BT four-point two-quartic bubble logarithmic jet."""

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
    "REVERSE_PHYSICS_BT_FOUR_POINT_BUBBLE_LOG_JET_V1.json",
)
PRODUCER = os.path.join(
    REPO_ROOT, "reverse_physics", "bt_four_point_bubble_log_jet.py",
)
VERIFIER = os.path.join(
    REPO_ROOT, "reverse_physics", "verify_bt_four_point_bubble_log_jet.py",
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
        self.assertIn("fixed-(s,t)", self.cert["declared_carrier"]["scope"])

    def test_channel_polynomial_and_on_shell_control(self):
        cut = self.cert["double_pole_cut"]
        self.assertIn("7*S^2+S*T+T^2", cut["channel_polynomial"])
        self.assertEqual(cut["cut_normalization"],
                         "d_y*d_z ordinary_cut = P/12 for physical S>0")
        self.assertEqual(cut["on_shell_control"],
                         "P|x=0=7*S^2+S*T+T^2")

    def test_logarithmic_jet_rows(self):
        rows = self.cert["bubble_log_interference_jet"][
            "numerator_coefficients"]
        self.assertEqual(rows["Ls"], list(reversed(rows["Lt"])))
        self.assertEqual(rows["Lu"], list(reversed(rows["Lu"])))
        self.assertEqual(rows["rational"], [0, -28, -59, -63, -59, -28, 0])

    def test_collinear_expansion_is_nonzero(self):
        expansion = self.cert["collinear_expansion"]["reduced_J"]
        self.assertIn("(15*L-ell)/r^2", expansion)
        self.assertIn("(-45*L+3*ell-35)/r", expansion)

    def test_incomplete_sectors_fail_closed(self):
        disposition = self.cert["disposition"]
        self.assertEqual(disposition["triangle_sector"], "NOT_COMPUTED")
        self.assertEqual(disposition["box_sector"], "NOT_COMPUTED")
        self.assertEqual(disposition["external_phase_space_projector"],
                         "NOT_APPLIED")
        self.assertEqual(disposition["real_virtual_collinear_cancellation"],
                         "NOT_COMPUTED")


class TestIndependentRail(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verifier = load(VERIFIER, "bt_bubble_log_verifier")
        with open(CERT, encoding="utf-8") as handle:
            cls.cert = json.load(handle)

    def test_coordinate_cut_fixtures(self):
        fixtures = [
            self.verifier.coordinate_cut_fixture(
                5, (3, 1, 0, 1), (-2, 0, 1, 1)),
            self.verifier.coordinate_cut_fixture(
                7, (4, 1, 2, 0), (-3, 2, -1, 1)),
            self.verifier.coordinate_cut_fixture(
                6, (2, -1, 1, 1), (-4, 1, 0, -2)),
        ]
        self.assertTrue(all(row["cut"] == row["expected"] for row in fixtures))

    def test_subset_jet_reproduces_rows(self):
        _, rows = self.verifier.subset_jet_result()
        self.assertEqual(
            rows,
            self.cert["bubble_log_interference_jet"]["numerator_coefficients"],
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

    def test_false_triangle_completion_is_rejected(self):
        with open(CERT, encoding="utf-8") as handle:
            mutated = json.load(handle)
        mutated["disposition"]["triangle_sector"] = "COMPUTED"
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
