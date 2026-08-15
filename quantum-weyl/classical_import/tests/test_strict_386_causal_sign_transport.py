#!/usr/bin/env python3
"""Mutation tests for the strict 386-row causal sign transport."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
sys.path.insert(0, str(HERE))

from build_strict_386_causal_sign_transport import generated  # noqa: E402
from check_strict_386_causal_sign_transport import check  # noqa: E402


RESULT = HERE / "certificates/STRICT_386_CAUSAL_SIGN_TRANSPORT_V1.json"
REPORT = HERE / "REPORT_STRICT_386_CAUSAL_SIGN_TRANSPORT_V1.md"


class Strict386CausalSignTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())

    def test_repository_result(self) -> None:
        self.assertEqual(check(self.value), [])

    def test_generated_artifacts_current(self) -> None:
        result, report = generated()
        self.assertEqual(RESULT.read_bytes(), result)
        self.assertEqual(REPORT.read_bytes(), report)

    def test_endpoint_rank_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["carrier_bridge"]["endpoint_blocks"][3]["dimension"] = 4
        self.assertTrue(check(value))

    def test_involution_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["transport"]["negative_eigenvalue_multiplicity"] = 4
        self.assertTrue(check(value))

    def test_common_hash_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["claim_flags"]["GATE_V5_TO_386_COMMON_BYTES_IDENTIFIED"] = True
        self.assertTrue(check(value))

    def test_nonlinear_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["claim_flags"]["STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED"] = True
        self.assertTrue(check(value))

    def test_hadamard_or_qme_promotion_fails(self) -> None:
        for flag in ("BRST_HADAMARD_STATE_CONSTRUCTED", "LORENTZIAN_QME_RESTORED"):
            with self.subTest(flag=flag):
                value = copy.deepcopy(self.value)
                value["claim_flags"][flag] = True
                self.assertTrue(check(value))


if __name__ == "__main__":
    unittest.main()
