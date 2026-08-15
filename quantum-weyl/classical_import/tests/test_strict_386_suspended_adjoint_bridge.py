from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
sys.path.insert(0, str(HERE))

from build_strict_386_suspended_adjoint_bridge import generated  # noqa: E402
from check_strict_386_suspended_adjoint_bridge import RESULT, check  # noqa: E402


class Strict386SuspendedAdjointBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text())

    def test_repository_result(self):
        self.assertEqual(check(self.value), [])

    def test_generated_artifacts_current(self):
        result, _ = generated()
        self.assertEqual(RESULT.read_bytes(), result)

    def test_suspension_character_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["endpoint_exact_algebra"]["R_diagonal"][0] = 1
        self.assertTrue(check(value))

    def test_full_sign_count_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["full_carrier_extension"]["R_386_negative"] = 9
        self.assertTrue(check(value))

    def test_component_pairing_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["full_carrier_extension"]["full_component_pairing_coefficients_serialized"] = True
        self.assertTrue(check(value))

    def test_gate_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] = True
        self.assertTrue(check(value))

    def test_q2_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED"] = True
        self.assertTrue(check(value))

    def test_quantum_promotions_fail(self):
        for key in ("HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "LORENTZIAN_QUANTUM_THEORY"):
            with self.subTest(key=key):
                value = copy.deepcopy(self.value)
                value["claim_flags"][key] = True
                self.assertTrue(check(value))


if __name__ == "__main__":
    unittest.main()
