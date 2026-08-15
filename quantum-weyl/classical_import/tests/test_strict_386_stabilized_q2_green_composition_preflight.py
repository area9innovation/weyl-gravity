#!/usr/bin/env python3
"""Mutation tests for the strict candidate q2/Green preflight."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_strict_386_stabilized_q2_green_composition_preflight.py", "test_q2_green_builder")
checker = module(HERE / "check_strict_386_stabilized_q2_green_composition_preflight.py", "test_q2_green_checker")
verifier = module(HERE / "verify_strict_386_stabilized_q2_green_composition_preflight.py", "test_q2_green_verifier")


class Strict386StabilizedQ2GreenCompositionPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())

    def test_repository_result(self) -> None:
        self.assertEqual(checker.check(self.value), [])
        self.assertEqual(verifier.main(), 0)

    def test_generated_current(self) -> None:
        self.assertEqual(RESULT.read_bytes(), builder.generated()[0])

    def test_carrier_mismatch_fails(self) -> None:
        value = deepcopy(self.value)
        value["carrier_alignment"]["basis_match"] = False
        self.assertTrue(checker.check(value))

    def test_support_overclaim_fails(self) -> None:
        value = deepcopy(self.value)
        value["response_names"]["plus"]["support"] = "supp B_plus is compact"
        self.assertTrue(checker.check(value))

    def test_green_name_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["response_names"]["minus"]["name"]["children"][1]["sha256"] = "0" * 64
        self.assertTrue(checker.check(value))

    def test_response_identity_sign_fails(self) -> None:
        value = deepcopy(self.value)
        value["homotopy_response_replay"]["response_identity"] = value["homotopy_response_replay"]["response_identity"].replace("-B_sign", "+B_sign", 1)
        self.assertTrue(checker.check(value))

    def test_recursive_tree_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["claim_flags"]["STRICT_386_RECURSIVE_NONLINEAR_GREEN_TREES_CERTIFIED"] = True
        self.assertTrue(checker.check(value))

    def test_authority_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["authority_boundary"]["authoritative_full_q2_imported"] = True
        value["authority_boundary"]["q2_green_result_status"] = "AUTHORITATIVE"
        value["claim_flags"]["STRICT_386_AUTHORITATIVE_Q2_GREEN_COMPATIBILITY_CERTIFIED"] = True
        self.assertTrue(checker.check(value))

    def test_foundational_overclaim_fails(self) -> None:
        value = deepcopy(self.value)
        value["foundational_strength"]["weakest_complete_foundational_base"] = "PRA"
        self.assertTrue(checker.check(value))

    def test_quantum_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["claim_flags"]["HADAMARD_STATE_CONSTRUCTED"] = True
        value["claim_flags"]["QME_RESTORED"] = True
        self.assertTrue(checker.check(value))

    def test_source_hash_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["provenance"]["inputs"][0]["sha256"] = "f" * 64
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
