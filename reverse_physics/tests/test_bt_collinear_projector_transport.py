"""Falsification tests for the BT coherent collinear projector transport."""

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
    "REVERSE_PHYSICS_BT_COLLINEAR_PROJECTOR_TRANSPORT_V1.json",
)
PRODUCER = os.path.join(
    REPO_ROOT, "reverse_physics", "bt_collinear_projector_transport.py",
)
VERIFIER = os.path.join(
    REPO_ROOT, "reverse_physics", "verify_bt_collinear_projector_transport.py",
)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class TestCertificate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.cert = json.load(handle)

    def test_dependency_and_lifecycle(self):
        self.assertEqual(
            self.cert["dependency_tags"],
            ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        )
        self.assertEqual(self.cert["lifecycle_state"], "CLASSIFIED")

    def test_physical_claim_stays_fail_closed(self):
        disposition = self.cert["disposition"]
        self.assertEqual(
            disposition["finite_coherent_projector_transport"],
            "EXACT_EXISTENCE_WITNESS",
        )
        self.assertEqual(
            disposition["bt_asymptotic_hamiltonian_derivation"],
            "NOT_CONSTRUCTED",
        )
        self.assertEqual(
            disposition["physical_nlo_probability"], "NOT_ESTABLISHED",
        )

    def test_response_ledger(self):
        response = self.cert["forced_responses"]
        self.assertEqual(response["per_pair_real_diagonal"],
                         {"numerator": 1, "denominator": 512})
        self.assertEqual(response["three_pair_real_diagonal"],
                         {"numerator": 3, "denominator": 512})
        self.assertEqual(response["hard_normalization_diagonal"],
                         {"numerator": -3, "denominator": 512})
        self.assertEqual(response["sum"],
                         {"numerator": 0, "denominator": 1})


class TestExactConstruction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load(PRODUCER, "bt_projector_transport_producer")

    def test_quadratic_field_is_exact(self):
        amplitude = self.module.Qsqrt2(Fraction(0), Fraction(1, 32))
        self.assertEqual(
            amplitude * amplitude,
            self.module.Qsqrt2(Fraction(1, 512)),
        )

    def test_forced_normalization_cancels_real_diagonal(self):
        data = self.module.construction()
        p2 = data["P2"]
        hard = p2[0][0]
        real = sum((p2[i][i] for i in range(1, 4)), self.module.ZERO)
        self.assertEqual(hard, self.module.Qsqrt2(Fraction(-3, 512)))
        self.assertEqual(real, self.module.Qsqrt2(Fraction(3, 512)))
        self.assertEqual(hard + real, self.module.ZERO)

    def test_recorded_certificate_is_deterministic(self):
        run = subprocess.run(
            [sys.executable, PRODUCER, "--check"], cwd=REPO_ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("RESULT: PASS", run.stdout)


class TestIndependentVerifier(unittest.TestCase):
    def test_verifier_accepts_certificate(self):
        run = subprocess.run(
            [sys.executable, VERIFIER], cwd=REPO_ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("RESULT: PASS", run.stdout)

    def test_missing_hard_normalization_is_rejected(self):
        with open(CERT, encoding="utf-8") as handle:
            mutated = json.load(handle)
        p2 = mutated["projector_transport"]["P2"]
        p2[:] = [
            entry for entry in p2
            if not (entry["row"] == 0 and entry["column"] == 0)
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                         encoding="utf-8") as handle:
            json.dump(mutated, handle)
            handle.flush()
            run = subprocess.run(
                [sys.executable, VERIFIER, "--verify", handle.name],
                cwd=REPO_ROOT, text=True, capture_output=True, check=False,
            )
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("[FAIL] formal_idempotence", run.stdout)

    def test_positive_charge_mutation_is_rejected(self):
        with open(CERT, encoding="utf-8") as handle:
            mutated = json.load(handle)
        mutated["bt_charge_gate"]["generator_total_charge_shift"] = 2
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                         encoding="utf-8") as handle:
            json.dump(mutated, handle)
            handle.flush()
            run = subprocess.run(
                [sys.executable, VERIFIER, "--verify", handle.name],
                cwd=REPO_ROOT, text=True, capture_output=True, check=False,
            )
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("[FAIL] neutral_charge_gate", run.stdout)


if __name__ == "__main__":
    unittest.main()
