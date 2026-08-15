#!/usr/bin/env python3
"""Mutation tests for the strict graph Green-action operator names."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_GRAPH_GREEN_ACTION_NAME_V1.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_strict_386_graph_green_action_name.py", "test_green_name_builder")
checker = module(HERE / "check_strict_386_graph_green_action_name.py", "test_green_name_checker")
verifier = module(HERE / "verify_strict_386_graph_green_action_name.py", "test_green_name_verifier")


class Strict386GraphGreenActionNameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())

    def test_repository_result(self) -> None:
        self.assertEqual(checker.check(self.value), [])
        self.assertEqual(verifier.main(), 0)

    def test_generated_current(self) -> None:
        self.assertEqual(RESULT.read_bytes(), builder.generated()[0])

    def test_zero_mode_removal_fails(self) -> None:
        value = deepcopy(self.value)
        value["parent_spectral_name"]["spatial_spectrum"][0]["zero_mode"] = "none"
        self.assertTrue(checker.check(value))

    def test_coexact_spectrum_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["parent_spectral_name"]["spatial_spectrum"][2]["eigenvalue"] = "k*(k+2)"
        self.assertTrue(checker.check(value))

    def test_causal_sign_swap_fails(self) -> None:
        value = deepcopy(self.value)
        value["operator_names"]["plus"]["parent_green_name"]["orientation"] = "past/advanced"
        self.assertTrue(checker.check(value))

    def test_graph_projection_removal_fails(self) -> None:
        value = deepcopy(self.value)
        value["operator_names"]["minus"]["full_graph_386_name"]["children"][1]["children"].pop()
        self.assertTrue(checker.check(value))

    def test_effective_solver_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["foundational_strength"]["TTE_computability"] = True
        value["gate_disposition"]["receiver_executable_numeric_solver_serialized"] = True
        value["claim_flags"]["STRICT_386_RECEIVER_EXECUTABLE_NUMERIC_GREEN_SOLVER"] = True
        self.assertTrue(checker.check(value))

    def test_gate_a_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["gate_disposition"]["one_common_unary_causal_snapshot_accepted"] = True
        value["gate_disposition"]["classical_import_gate_a_status"] = "PASS"
        value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] = True
        self.assertTrue(checker.check(value))

    def test_hadamard_qme_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["claim_flags"]["HADAMARD_STATE_CONSTRUCTED"] = True
        value["claim_flags"]["QME_RESTORED"] = True
        value["claim_flags"]["LORENTZIAN_QUANTUM_THEORY"] = True
        self.assertTrue(checker.check(value))

    def test_source_hash_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.assertTrue(checker.check(value))

    def test_spectral_source_hash_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["analytic_sources"][1]["artifact"]["sha256"] = "0" * 64
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
