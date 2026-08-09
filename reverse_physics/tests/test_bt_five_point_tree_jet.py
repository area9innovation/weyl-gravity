"""Falsification tests for the exact BT five-point tree-amplitude jet."""

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
    "REVERSE_PHYSICS_BT_FIVE_POINT_TREE_JET_V1.json",
)
PRODUCER = os.path.join(
    REPO_ROOT, "reverse_physics", "bt_five_point_tree_jet.py")
VERIFIER = os.path.join(
    REPO_ROOT, "reverse_physics", "verify_bt_five_point_tree_jet.py")
MISE_PYTHON = (
    "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3"
)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestCertificateGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def test_tag_lifecycle_and_checks(self):
        self.assertEqual(self.certificate["dependency_tags"],
                         ["LOCAL-ALGEBRAIC"])
        self.assertEqual(self.certificate["lifecycle_state"],
                         "COEFFICIENT_COMPUTED")
        self.assertTrue(self.certificate["checks"]["ok"])
        self.assertEqual(self.certificate["checks"]["passed"],
                         self.certificate["checks"]["total"])

    def test_complete_support_and_zero_projector(self):
        symbolic = self.certificate["symbolic_jet"]
        self.assertEqual(len(symbolic["zero_low_degree_rows"]), 16)
        self.assertEqual(len(symbolic["coefficient_hashes"]), 16)
        self.assertEqual(symbolic["nonzero_degree_counts"],
                         {"3": 10, "4": 5, "5": 1})
        self.assertTrue(symbolic["projected_square_zero"])

    def test_physical_probability_stays_fail_closed(self):
        disposition = self.certificate["disposition"]
        self.assertEqual(disposition["pointwise_D5_amplitude_square"], "ZERO")
        self.assertEqual(disposition["five_body_phase_space_projector"],
                         "NOT_CONSTRUCTED")
        self.assertEqual(disposition["distributional_boundary_terms"],
                         "NOT_CLASSIFIED")
        self.assertEqual(disposition["beyond_tree_positivity"],
                         "NOT_ESTABLISHED")

    def test_claim_boundary_names_distributional_problem(self):
        boundary = " ".join(self.certificate["does_not_establish"])
        self.assertIn("distributional", boundary)
        self.assertIn("KLN", boundary)
        self.assertIn("LORENTZIAN-CAUSAL", boundary)


class TestExactAmplitude(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.producer = load(PRODUCER, "bt5_producer")
        cls.verifier = load(VERIFIER, "bt5_verifier")
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def test_topology_counts_are_10_plus_15(self):
        amplitude, cq, ccc = self.producer.build_amplitude(
            self.producer.RationalDomain(),
            [Fraction(2), Fraction(3), Fraction(5), Fraction(7), Fraction(11)],
        )
        self.assertEqual(len(cq), 10)
        self.assertEqual(len(ccc), 15)
        self.assertEqual(len(amplitude.coefficients), 16)

    def test_two_derivations_agree_on_complete_exact_jet(self):
        invariants = [Fraction(2), Fraction(3), Fraction(5),
                      Fraction(7), Fraction(11)]
        left, _, _ = self.producer.build_amplitude(
            self.producer.RationalDomain(), invariants)
        right, _ = self.verifier.build_amplitude(
            self.verifier.RationalDomain(), invariants)
        for mask in range(32):
            self.assertEqual(left.coefficient(mask), right.coefficient(mask))

    def test_amplitude_starts_at_degree_three(self):
        amplitude, _, _ = self.producer.build_amplitude(
            self.producer.RationalDomain(), [2, 3, 5, 7, 11])
        self.assertEqual(
            sorted(amplitude.coefficients),
            [mask for mask in range(32) if mask.bit_count() >= 3],
        )
        self.assertEqual((amplitude * amplitude).coefficient(31), 0)

    def test_relative_sign_mutation_destroys_cancellation(self):
        mutated, _ = self.verifier.build_amplitude(
            self.verifier.RationalDomain(), [2, 3, 5, 7, 11], sign=+1)
        self.assertEqual(sorted(mutated.coefficients), list(range(32)))
        self.assertNotEqual((mutated * mutated).coefficient(31), 0)

    def test_leading_face_coefficients_have_no_worse_than_simple_poles(self):
        for face in self.certificate["soft_collinear_faces"]:
            degree_three = [
                row["epsilon_valuation"] for row in face["coefficient_rows"]
                if row["degree"] == 3
            ]
            self.assertGreaterEqual(min(degree_three), -1)
            self.assertTrue(face["projected_square_zero_for_nonzero_epsilon"])


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

    def test_false_phase_space_promotion_is_rejected(self):
        with open(CERT, encoding="utf-8") as handle:
            mutated = json.load(handle)
        mutated["disposition"]["five_body_phase_space_projector"] = "CONSTRUCTED"
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
