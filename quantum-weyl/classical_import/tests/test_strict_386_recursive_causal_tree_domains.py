#!/usr/bin/env python3
"""Mutation tests for recursive causal-tree support domains."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_RECURSIVE_CAUSAL_TREE_DOMAINS_V1.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_strict_386_recursive_causal_tree_domains.py", "test_recursive_tree_builder")
checker = module(HERE / "check_strict_386_recursive_causal_tree_domains.py", "test_recursive_tree_checker")
verifier = module(HERE / "verify_strict_386_recursive_causal_tree_domains.py", "test_recursive_tree_verifier")


class Strict386RecursiveCausalTreeDomainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())

    def test_repository_result(self) -> None:
        self.assertEqual(checker.check(self.value), [])
        self.assertEqual(verifier.main(), 0)

    def test_generated_current(self) -> None:
        self.assertEqual(RESULT.read_bytes(), builder.generated()[0])

    def test_polarized_tree_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["recursive_polarized_tree_theorem"]["retarded"]["all_finite_plane_binary_trees"] = False
        self.assertTrue(checker.check(value))

    def test_support_table_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["support_algebra"]["intersection_table_on_RxS3"]["PC*FC"] = "PC"
        self.assertTrue(checker.check(value))

    def test_opposite_green_domain_overclaim_fails(self) -> None:
        value = deepcopy(self.value)
        value["support_algebra"]["green_domain_table"]["plus(FC)"] = "PC"
        self.assertTrue(checker.check(value))

    def test_census_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["sign_decoration_census"][2]["admissible_total"] = 40
        value["sign_decoration_census"][2]["not_uniformly_defined"] = 0
        self.assertTrue(checker.check(value))

    def test_minimal_boundary_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["mixed_sign_boundary"]["first_uniform_failure_leaf_count"] = 5
        self.assertTrue(checker.check(value))

    def test_zero_mode_witness_removal_fails(self) -> None:
        value = deepcopy(self.value)
        value["zero_mode_mismatch_witness"]["advanced_on_PC_witness"] = "converges"
        self.assertTrue(checker.check(value))

    def test_unrestricted_tree_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["claim_flags"]["STRICT_386_UNRESTRICTED_MIXED_SIGN_TREES_CERTIFIED"] = True
        value["claim_flags"]["STRICT_386_ARBITRARY_CAUSAL_DIFFERENCE_TREES_CERTIFIED"] = True
        self.assertTrue(checker.check(value))

    def test_authority_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["authority_boundary"]["authoritative_full_q2_imported"] = True
        value["claim_flags"]["STRICT_386_AUTHORITATIVE_Q2_RECURSIVE_TREES_CERTIFIED"] = True
        self.assertTrue(checker.check(value))

    def test_infinite_series_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["recursive_polarized_tree_theorem"]["formal_power_series"] = "CONVERGENT"
        value["claim_flags"]["STRICT_386_INFINITE_TREE_SERIES_CONVERGENCE_CERTIFIED"] = True
        self.assertTrue(checker.check(value))

    def test_foundation_overclaim_fails(self) -> None:
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
        value["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
