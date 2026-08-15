from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
sys.path.insert(0, str(HERE))

from build_strict_386_component_pairing_serialization import generated  # noqa: E402
from check_strict_386_component_pairing_serialization import RESULT, check  # noqa: E402


class Strict386ComponentPairingSerializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text())

    def test_repository_result(self):
        self.assertEqual(check(self.value), [])

    def test_generated_artifacts_current(self):
        result, _ = generated()
        self.assertEqual(RESULT.read_bytes(), result)

    def test_row_order_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["component_basis"]["rows"][30]["row_id"] = "wrong"
        self.assertTrue(check(value))

    def test_pairing_coefficient_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["pairing_serialization"]["entries"][30]["coefficient"] = "7"
        self.assertTrue(check(value))

    def test_pairing_rank_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["pairing_serialization"]["rank"] = 385
        self.assertTrue(check(value))

    def test_suspension_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["suspension_serialization"]["R_diagonal"][0] = 1
        self.assertTrue(check(value))

    def test_all_operator_adjoint_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["operator_adjoint_disposition"]["every_component_operator_adjoint_replayed"] = True
        self.assertTrue(check(value))

    def test_gate_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] = True
        self.assertTrue(check(value))

    def test_quantum_promotions_fail(self):
        for key in ("HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "LORENTZIAN_QUANTUM_THEORY"):
            with self.subTest(key=key):
                value = copy.deepcopy(self.value)
                value["claim_flags"][key] = True
                self.assertTrue(check(value))


if __name__ == "__main__":
    unittest.main()
