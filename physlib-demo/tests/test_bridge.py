from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

DEMO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_bridge", DEMO / "check_bridge.py")
CHECKER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CHECKER)


class PhyslibBridgeCertificateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result = json.loads(CHECKER.CERTIFICATE.read_text())
        self.arity = json.loads(CHECKER.ARITY_CERTIFICATE.read_text())

    def test_certificate_passes(self) -> None:
        errors, _ = CHECKER.check(self.result)
        self.assertEqual(errors, [])

    def test_causal_overpromotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.result)
        mutated["dependency_tags"].append("LORENTZIAN-CAUSAL")
        errors, _ = CHECKER.check(mutated)
        self.assertIn("dependency boundary", errors)

    def test_false_formalization_flag_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.result)
        mutated["claim_flags"]["GREEN_HOMOTOPY_FORMALIZED"] = True
        errors, _ = CHECKER.check(mutated)
        self.assertIn("claim flags", errors)

    def test_source_hash_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.result)
        mutated["provenance"]["lean_source"]["sha256"] = "0" * 64
        errors, _ = CHECKER.check(mutated)
        self.assertIn("Lean source hash", errors)

    def test_physlib_pin_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.result)
        mutated["toolchain"]["physlib_commit"] = "0" * 40
        errors, _ = CHECKER.check(mutated)
        self.assertIn("Physlib manifest pin", errors)

    def test_arity_certificate_passes(self) -> None:
        errors, _ = CHECKER.check_arity_three(self.arity)
        self.assertEqual(errors, [])

    def test_arity_natural_operator_overpromotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.arity)
        mutated["claim_flags"]["NATURAL_OPERATOR_EVALUATOR_FORMALIZED"] = True
        errors, _ = CHECKER.check_arity_three(mutated)
        self.assertIn("arity claim flags", errors)

    def test_arity_source_hash_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.arity)
        mutated["provenance"]["forge_source_certificate"]["sha256"] = "0" * 64
        errors, _ = CHECKER.check_arity_three(mutated)
        self.assertIn("arity forge_source_certificate hash", errors)

    def test_semantic_evaluator_hash_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.arity)
        mutated["provenance"]["semantic_lean_source"]["sha256"] = "0" * 64
        errors, _ = CHECKER.check_arity_three(mutated)
        self.assertIn("arity semantic_lean_source hash", errors)

    def test_replaced_premise_cannot_be_reimported(self) -> None:
        mutated = copy.deepcopy(self.arity)
        mutated["imported_premises"].append("the pre-summed signed aggregation")
        errors, _ = CHECKER.check_arity_three(mutated)
        self.assertIn("replaced arity premise still imported", errors)

    def test_source_path_aggregation_is_rejected(self) -> None:
        source = CHECKER.SEMANTIC_SOURCE.read_text()
        mutated_source = source.replace(
            "(outputPairs output).all pairDerivedZero",
            "(outputPairs output).all pairSourceZero",
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "FiniteGradedEvaluator.lean"
            path.write_text(mutated_source)
            original = CHECKER.SEMANTIC_SOURCE
            try:
                CHECKER.SEMANTIC_SOURCE = path
                errors, _ = CHECKER.check_arity_three(self.arity)
            finally:
                CHECKER.SEMANTIC_SOURCE = original
        self.assertIn("semantic zero theorem does not target derived paths", errors)

    def test_native_decide_boundary_is_rejected(self) -> None:
        source = CHECKER.SEMANTIC_SOURCE.read_text() + "\n-- native_decide diagnostic\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "FiniteGradedEvaluator.lean"
            path.write_text(source)
            original = CHECKER.SEMANTIC_SOURCE
            try:
                CHECKER.SEMANTIC_SOURCE = path
                errors, _ = CHECKER.check_arity_three(self.arity)
            finally:
                CHECKER.SEMANTIC_SOURCE = original
        self.assertIn("semantic evaluator introduced a native_decide axiom boundary", errors)


if __name__ == "__main__":
    unittest.main()
