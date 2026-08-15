#!/usr/bin/env python3
"""Mutation tests for the strict 386-row canonical shear component jets."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_strict_386_canonical_shear_component_jets.py", "test_shear_builder")
checker = module(HERE / "check_strict_386_canonical_shear_component_jets.py", "test_shear_checker")
verifier = module(HERE / "verify_strict_386_canonical_shear_component_jets.py", "test_shear_verifier")


class Strict386CanonicalShearComponentJetsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())

    def test_repository_result(self) -> None:
        self.assertEqual(checker.check(self.value), [])
        self.assertEqual(verifier.main(), 0)

    def test_generated_current(self) -> None:
        self.assertEqual(RESULT.read_bytes(), builder.generated()[0])

    def test_primal_coefficient_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["canonical_transform"]["forward"]["tables"][0]["coefficients"][0]["entries"][0][2] = "17"
        self.assertTrue(checker.check(value))

    def test_forced_partner_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["canonical_transform"]["elementary_shears"][1]["forced_partner_table"]["coefficients"][0]["entries"][0][2] = "1/7"
        self.assertTrue(checker.check(value))

    def test_cross_term_removal_fails(self) -> None:
        value = deepcopy(self.value)
        value["canonical_transform"]["inverse"]["tables"].pop()
        value["canonical_transform"]["inverse"]["table_count"] = 6
        self.assertTrue(checker.check(value))

    def test_graph_and_gate_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["gate_disposition"]["graph_coordinate_q1_component_replay_complete"] = True
        value["gate_disposition"]["one_common_gate_a_snapshot_accepted"] = True
        value["gate_disposition"]["classical_import_gate_a_status"] = "PASS"
        value["claim_flags"]["STRICT_386_GRAPH_Q1_COMPONENT_JET_TABLE_SERIALIZED"] = True
        value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] = True
        self.assertTrue(checker.check(value))

    def test_quantum_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["claim_flags"]["HADAMARD_STATE_CONSTRUCTED"] = True
        value["claim_flags"]["QME_RESTORED"] = True
        value["claim_flags"]["LORENTZIAN_QUANTUM_THEORY"] = True
        self.assertTrue(checker.check(value))

    def test_snapshot_binding_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["canonical_shear_snapshot"]["split_local_sdr_snapshot_sha256"] = "0" * 64
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
