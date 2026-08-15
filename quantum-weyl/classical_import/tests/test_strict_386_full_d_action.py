#!/usr/bin/env python3
"""Mutation tests for the strict 386-row cylinder-flow action."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_FULL_D_ACTION_V1.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_strict_386_full_d_action.py", "test_full_d_builder")
checker = module(HERE / "check_strict_386_full_d_action.py", "test_full_d_checker")
verifier = module(HERE / "verify_strict_386_full_d_action.py", "test_full_d_verifier")


class Strict386FullDActionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())

    def test_repository_result(self) -> None:
        self.assertEqual(checker.check(self.value), [])
        self.assertEqual(verifier.main(), 0)

    def test_generated_current(self) -> None:
        self.assertEqual(RESULT.read_bytes(), builder.generated()[0])

    def test_missing_row_fails(self) -> None:
        value = deepcopy(self.value)
        value["D_action"]["entries"].pop()
        value["D_action"]["nonzero_coefficients"] = 385
        self.assertTrue(checker.check(value))

    def test_spatial_generator_substitution_fails(self) -> None:
        value = deepcopy(self.value)
        value["D_action"]["temporal_multiindex"] = [0, 1, 0, 0]
        self.assertTrue(checker.check(value))

    def test_row_mixing_fails(self) -> None:
        value = deepcopy(self.value)
        value["D_action"]["entries"][10][1] = 11
        self.assertTrue(checker.check(value))

    def test_commutator_promotion_without_replay_fails(self) -> None:
        value = deepcopy(self.value)
        value["exact_replay"]["D_q1_commutator_defects"] = 1
        value["exact_replay"]["D_q1_commutator_zero"] = False
        self.assertTrue(checker.check(value))

    def test_minkowski_or_berger_conflation_fails(self) -> None:
        value = deepcopy(self.value)
        value["generator_selection"]["not_minkowski_dilation"] = False
        value["generator_selection"]["not_berger_helical_generator"] = False
        self.assertTrue(checker.check(value))

    def test_q2_gate_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["gate_disposition"]["M2_full_carrier_q2_status"] = "RECEIVER_VERIFIED_SCOPED"
        value["gate_disposition"]["M2_D_q2_derivation_status"] = "RECEIVER_VERIFIED_SCOPED"
        value["claim_flags"]["STRICT_386_FULL_Q2_D_COMMON_SNAPSHOT"] = True
        value["claim_flags"]["STRICT_386_D_Q2_DERIVATION_REPLAYED"] = True
        self.assertTrue(checker.check(value))

    def test_gate_and_quantum_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["gate_disposition"]["classical_import_gate_a_status"] = "PASS"
        value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] = True
        value["claim_flags"]["HADAMARD_STATE_CONSTRUCTED"] = True
        value["claim_flags"]["QME_RESTORED"] = True
        self.assertTrue(checker.check(value))

    def test_source_hash_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.assertTrue(checker.check(value))

    def test_extended_snapshot_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["extended_common_snapshot"]["accepted_object_hashes"] = 15
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
