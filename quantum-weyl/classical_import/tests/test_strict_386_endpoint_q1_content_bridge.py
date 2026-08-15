from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
sys.path.insert(0, str(HERE))

from build_strict_386_endpoint_q1_content_bridge import generated  # noqa: E402
from check_strict_386_endpoint_q1_content_bridge import RESULT, WITNESS, check  # noqa: E402


class Strict386EndpointQ1ContentBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text())
        cls.witness = json.loads(WITNESS.read_text())

    def test_repository_result(self):
        self.assertEqual(check(self.value, self.witness)[0], [])

    def test_generated_artifacts_current(self):
        result, _ = generated()
        self.assertEqual(RESULT.read_bytes(), result)

    def test_common_hash_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["coefficientwise_identification"]["common_q1_sha256"] = "0" * 64
        self.assertTrue(check(value, self.witness)[0])

    def test_pairing_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["SIMULTANEOUSLY_TRANSPORTED_CAUSAL_PAIRING_EQUALS_GATE_CANONICAL"] = True
        self.assertTrue(check(value, self.witness)[0])

    def test_full_carrier_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["gate_disposition"]["full_common_carrier_established"] = True
        self.assertTrue(check(value, self.witness)[0])

    def test_q2_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED"] = True
        self.assertTrue(check(value, self.witness)[0])

    def test_witness_coefficient_mutation_fails(self):
        witness = copy.deepcopy(self.witness)
        witness["columns"][0]["coordinate_entries"][0][1] = "2"
        self.assertTrue(check(self.value, witness)[0])

    def test_hadamard_qme_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["HADAMARD_STATE_CONSTRUCTED"] = True
        value["claim_flags"]["QME_RESTORED"] = True
        self.assertTrue(check(value, self.witness)[0])


if __name__ == "__main__":
    unittest.main()
