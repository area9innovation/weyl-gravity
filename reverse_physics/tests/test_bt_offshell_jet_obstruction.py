"""Falsification tests for the BT external-virtuality-jet obstruction."""

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
    "REVERSE_PHYSICS_BT_OFFSHELL_JET_OBSTRUCTION_V1.json",
)
PRODUCER = os.path.join(
    REPO_ROOT, "reverse_physics", "bt_offshell_jet_obstruction.py")
VERIFIER = os.path.join(
    REPO_ROOT, "reverse_physics", "verify_bt_offshell_jet_obstruction.py")


def load_module():
    spec = importlib.util.spec_from_file_location("bt_jet", PRODUCER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestExactJetAlgebra(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def test_overlapping_variables_are_truncated(self):
        x1 = self.module.Jet.monomial(3, 1)
        self.assertEqual(x1 * x1, self.module.Jet(3))

    def test_disjoint_subsets_reach_top_derivative(self):
        left = self.module.Jet.monomial(4, 0b0101)
        right = self.module.Jet.monomial(4, 0b1010)
        self.assertEqual((left * right).projector(), 1)

    def test_equal_on_shell_amplitudes_have_unequal_probabilities(self):
        for n in range(1, 8):
            base = self.module.Jet.one(n)
            a = Fraction(n, n + 3)
            mutated = base + self.module.Jet.monomial(
                n, (1 << n) - 1, a)
            self.assertEqual(base.on_shell(), mutated.on_shell())
            self.assertEqual((base * base).projector(), 0)
            self.assertEqual((mutated * mutated).projector(), 2 * a)

    def test_all_nlo_jet_slots_have_complement_partner(self):
        for n in (4, 5):
            rows = self.module.complement_rows(n)
            self.assertEqual(len(rows), 1 << n)
            self.assertTrue(all(
                row["projector_of_pair_squared"]
                == self.module.rational(2) for row in rows
            ))

    def test_recorded_certificate_is_deterministic(self):
        run = subprocess.run(
            [sys.executable, PRODUCER, "--check"], cwd=REPO_ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


class TestCertificateBoundary(unittest.TestCase):
    def setUp(self):
        with open(CERT, encoding="utf-8") as handle:
            self.certificate = json.load(handle)

    def test_tag_lifecycle_and_disposition(self):
        self.assertEqual(self.certificate["dependency_tags"],
                         ["LOCAL-ALGEBRAIC"])
        self.assertEqual(self.certificate["lifecycle_state"], "CLASSIFIED")
        disposition = self.certificate["disposition"]
        self.assertEqual(disposition["offshell_jet_necessity"], "PROVED")
        self.assertEqual(disposition["physical_nlo_process_map"],
                         "NOT_CONSTRUCTED")
        self.assertEqual(disposition["underlying_theory_ambiguous"],
                         "NOT_ESTABLISHED")

    def test_missing_objects_and_claim_boundary_are_explicit(self):
        self.assertGreaterEqual(len(self.certificate["missing_object_ledger"]), 6)
        boundary = " ".join(self.certificate["does_not_establish"])
        self.assertIn("KLN", boundary)
        self.assertIn("LORENTZIAN-CAUSAL", boundary)
        self.assertIn("field-redefinition", boundary)


class TestIndependentVerifier(unittest.TestCase):
    def test_independent_verifier_accepts_certificate(self):
        run = subprocess.run(
            [sys.executable, VERIFIER], cwd=REPO_ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("RESULT: PASS", run.stdout)

    def test_zeroed_ambiguity_is_rejected(self):
        with open(CERT, encoding="utf-8") as handle:
            mutated = json.load(handle)
        row = mutated["first_nlo_pair"]["virtual_channel"]["fixture"]
        row["probability_shift"] = {"numerator": 0, "denominator": 1}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                         encoding="utf-8") as handle:
            json.dump(mutated, handle)
            handle.flush()
            run = subprocess.run(
                [sys.executable, VERIFIER, "--verify", handle.name],
                cwd=REPO_ROOT, text=True, capture_output=True, check=False,
            )
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("[FAIL] independent_nlo_pair", run.stdout)

    def test_false_physical_promotion_is_rejected(self):
        with open(CERT, encoding="utf-8") as handle:
            mutated = json.load(handle)
        mutated["disposition"]["physical_nlo_process_map"] = "CONSTRUCTED"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                         encoding="utf-8") as handle:
            json.dump(mutated, handle)
            handle.flush()
            run = subprocess.run(
                [sys.executable, VERIFIER, "--verify", handle.name],
                cwd=REPO_ROOT, text=True, capture_output=True, check=False,
            )
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("[FAIL] strict_schema", run.stdout)
        self.assertIn("[FAIL] fail_closed_disposition", run.stdout)


if __name__ == "__main__":
    unittest.main()
