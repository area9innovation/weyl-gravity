"""Falsification tests for the BT order-lambda R_t Jordan kernel."""

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
    "REVERSE_PHYSICS_BT_RT_JORDAN_KERNEL_V1.json",
)
PRODUCER = os.path.join(REPO_ROOT, "reverse_physics", "bt_rt_jordan_kernel.py")
VERIFIER = os.path.join(
    REPO_ROOT, "reverse_physics", "verify_bt_rt_jordan_kernel.py"
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

    def test_dependency_boundary(self):
        self.assertEqual(
            self.cert["dependency_tags"], ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
        )
        self.assertEqual(self.cert["lifecycle_state"], "COEFFICIENT_COMPUTED")

    def test_label_inconsistency_is_not_overstated(self):
        appendix = self.cert["appendix_c_consistency"]
        self.assertEqual(
            appendix["status"],
            "INTERNALLY_INCONSISTENT_AS_PRINTED_REPAIRED_FOR_DERIVATION",
        )
        self.assertIn("does not identify", appendix["alternative_not_excluded"])

    def test_probability_stays_open(self):
        disposition = self.cert["disposition"]
        self.assertEqual(
            disposition["continuum_distributional_domain"], "NOT_CONSTRUCTED"
        )
        self.assertEqual(disposition["exact_gram_one_over_48"], "NOT_DERIVED")
        self.assertEqual(
            disposition["physical_nlo_probability"], "NOT_ESTABLISHED"
        )


class TestExactProducer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.producer = load(PRODUCER, "bt_rt_jordan_kernel_producer")

    def test_repaired_carrier_has_no_secular_terms(self):
        omega_a, upsilon_a = self.producer.nonlinear_a_kernel()
        omega = self.producer.transport_to_bt(omega_a)
        upsilon = self.producer.transport_to_bt(upsilon_a)
        self.assertTrue(all(value.max_t_degree() <= 0
                            for value in list(omega.values())
                            + list(upsilon.values())))

    def test_upsilonupsilon_cancellation(self):
        omega_a, _ = self.producer.nonlinear_a_kernel()
        omega = self.producer.transport_to_bt(omega_a)
        self.assertEqual(
            omega[("Upsilon", "Upsilon")], self.producer.poly(0)
        )

    def test_endpoint_pole_is_cubic(self):
        omega_a, upsilon_a = self.producer.nonlinear_a_kernel()
        omega = self.producer.transport_to_bt(omega_a)
        upsilon = self.producer.transport_to_bt(upsilon_a)
        gram, _ = self.producer.krein_gram(omega, upsilon)
        cross = gram[("Omega", "Upsilon")]
        self.assertEqual(min(power[0] for power in cross.terms), -3)
        self.assertEqual(min(power[1] for power in cross.terms), -3)

    def test_recorded_certificate_is_deterministic(self):
        run = subprocess.run(
            [sys.executable, PRODUCER, "--check"], cwd=REPO_ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("RESULT: PASS", run.stdout)


class TestIndependentVerifier(unittest.TestCase):
    def run_mutation(self, mutate):
        with open(CERT, encoding="utf-8") as handle:
            payload = json.load(handle)
        mutate(payload)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                         encoding="utf-8") as handle:
            json.dump(payload, handle)
            handle.flush()
            return subprocess.run(
                [sys.executable, VERIFIER, "--verify", handle.name],
                cwd=REPO_ROOT, text=True, capture_output=True, check=False,
            )

    def test_verifier_accepts_certificate(self):
        run = subprocess.run(
            [sys.executable, VERIFIER], cwd=REPO_ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("RESULT: PASS", run.stdout)

    def test_label_mutation_is_rejected(self):
        run = self.run_mutation(lambda payload: payload[
            "appendix_c_consistency"].__setitem__(
                "minimal_repair", "keep the printed labels"
            ))
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("[FAIL] strict_schema", run.stdout)

    def test_gram_mutation_is_rejected(self):
        run = self.run_mutation(lambda payload: payload[
            "fixed_splitting_krein_gram"].__setitem__(
                "G_OmegaUpsilon", "1/48"
            ))
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("[FAIL] recorded_gram_formulas", run.stdout)

    def test_probability_promotion_is_rejected(self):
        run = self.run_mutation(lambda payload: payload["disposition"].__setitem__(
            "physical_nlo_probability", "ESTABLISHED"
        ))
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("[FAIL] claim_boundary", run.stdout)


if __name__ == "__main__":
    unittest.main()
