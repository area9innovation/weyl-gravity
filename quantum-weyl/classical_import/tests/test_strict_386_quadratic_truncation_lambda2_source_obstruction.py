#!/usr/bin/env python3
"""Mutation tests for the q2-only lambda-squared source obstruction."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
sys.path.insert(0, str(HERE))


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


CHECK = module("lambda2_obstruction_check_test", HERE / "check_strict_386_quadratic_truncation_lambda2_source_obstruction.py")
VERIFY = module("lambda2_obstruction_verify_test", HERE / "verify_strict_386_quadratic_truncation_lambda2_source_obstruction.py")
RESULT = HERE / "certificates/STRICT_386_QUADRATIC_TRUNCATION_LAMBDA2_SOURCE_OBSTRUCTION_V1.json"


class Lambda2SourceObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text())

    def mutation_fails(self, change):
        value = deepcopy(self.value)
        change(value)
        self.assertTrue(CHECK.check(value) or VERIFY.verify(value))

    def test_current(self):
        self.assertEqual(CHECK.check(self.value), [])
        self.assertEqual(VERIFY.verify(self.value), [])

    def test_result_id(self):
        self.mutation_fails(lambda value: value.__setitem__("result_id", "WRONG"))

    def test_fixture_not_closed(self):
        self.mutation_fails(lambda value: value["exact_q1_closed_fixture"].__setitem__("linear_equation_terms", [{"fake": 1}]))

    def test_jacobiator(self):
        self.mutation_fails(lambda value: value["exact_q1_closed_fixture"].__setitem__("jacobiator_weyl_identity_value", "0"))

    def test_source_closed_overclaim(self):
        self.mutation_fails(lambda value: value["quadratic_truncation_disposition"].__setitem__("quadratic_only_lambda_squared_source_closed", True))

    def test_source_defect(self):
        self.mutation_fails(lambda value: value["quadratic_truncation_disposition"].__setitem__("witness_source_closure_defect", "0"))

    def test_q3_target(self):
        self.mutation_fails(lambda value: value["quadratic_truncation_disposition"].__setitem__("required_q3_q1_image_on_witness", "0"))

    def test_full_theory_boundary(self):
        self.mutation_fails(lambda value: value["quadratic_truncation_disposition"].__setitem__("not_an_obstruction_to_full_weyl_theory", False))

    def test_authoritative_q3_overclaim(self):
        self.mutation_fails(lambda value: value["claim_flags"].__setitem__("STRICT_386_AUTHORITATIVE_Q3_IMPORTED", True))

    def test_full_source_overclaim(self):
        self.mutation_fails(lambda value: value["claim_flags"].__setitem__("STRICT_386_FULL_WEYL_LAMBDA2_SOURCE_CLOSURE_CERTIFIED", True))

    def test_gate_overclaim(self):
        self.mutation_fails(lambda value: value["claim_flags"].__setitem__("CLASSICAL_IMPORT_GATE_PASSED", True))

    def test_contract_removed(self):
        self.mutation_fails(lambda value: value["authoritative_q3_export_contract"].__setitem__("required_objects", []))

    def test_hash(self):
        self.mutation_fails(lambda value: value["canonical_hashes"].__setitem__("fixture_sha256", "0" * 64))


if __name__ == "__main__":
    unittest.main()
