#!/usr/bin/env python3
"""Mutation tests for the strict 386-row graph q1/SDR certificate."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_strict_386_graph_q1_sdr_component_jets.py", "test_graph_builder")
checker = module(HERE / "check_strict_386_graph_q1_sdr_component_jets.py", "test_graph_checker")
verifier = module(HERE / "verify_strict_386_graph_q1_sdr_component_jets.py", "test_graph_verifier")


class Strict386GraphQ1SdrComponentJetsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())

    def test_repository_result(self) -> None:
        self.assertEqual(checker.check(self.value), [])
        self.assertEqual(verifier.main(), 0)

    def test_generated_current(self) -> None:
        self.assertEqual(RESULT.read_bytes(), builder.generated()[0])

    def test_graph_coefficient_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["graph_q1_serialization"]["tables"][-1]["coefficients"][0]["entries"][0][2] = "23"
        self.assertTrue(checker.check(value))

    def test_central_attachment_removal_fails(self) -> None:
        value = deepcopy(self.value)
        value["graph_q1_serialization"]["tables"].pop(24)
        value["graph_q1_serialization"]["counts"]["operator_tables"] = 26
        self.assertTrue(checker.check(value))

    def test_diagonal_suspension_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        r_graph = value["graph_sdr_component_maps"]["R_graph"]
        r_graph["coefficients"][0]["entries"] = [
            item for item in r_graph["coefficients"][0]["entries"] if item[0] == item[1]
        ]
        r_graph["nonzero_coefficients"] = 386
        self.assertTrue(checker.check(value))

    def test_raw_pbw_residual_cannot_be_declared_zero(self) -> None:
        value = deepcopy(self.value)
        value["exact_replay"]["transported_R_raw_parallel_cyclicity_residual_coefficients"] = 0
        value["exact_replay"]["raw_N_A_minus_B_C_parallel_residual_coefficients"] = 0
        self.assertTrue(checker.check(value))

    def test_gate_and_green_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["gate_disposition"]["represented_advanced_retarded_actions_bound"] = True
        value["gate_disposition"]["one_common_gate_a_snapshot_accepted"] = True
        value["gate_disposition"]["classical_import_gate_a_status"] = "PASS"
        value["claim_flags"]["STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED"] = True
        value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] = True
        self.assertTrue(checker.check(value))

    def test_quantum_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["claim_flags"]["HADAMARD_STATE_CONSTRUCTED"] = True
        value["claim_flags"]["QME_RESTORED"] = True
        value["claim_flags"]["LORENTZIAN_QUANTUM_THEORY"] = True
        self.assertTrue(checker.check(value))

    def test_source_snapshot_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["graph_snapshot"]["canonical_shear_snapshot_sha256"] = "0" * 64
        self.assertTrue(checker.check(value))

    def test_source_hash_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
