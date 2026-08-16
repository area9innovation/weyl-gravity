#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
RESULT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1.json"
CHECKER = ROOT / "quantum-weyl/classical_import/check_strict_m1b_primal_composite_contraction.py"
BUILDER = ROOT / "quantum-weyl/classical_import/build_strict_m1b_primal_composite_contraction.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("m1b_primal_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class M1BPrimalCompositeContractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.checker = load_checker()

    def test_independent_checker_accepts(self) -> None:
        self.assertEqual(self.checker.check(copy.deepcopy(self.value)), [])

    def test_sparse_coefficient_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["represented_contraction"]["blocks"][0]["matrices"]["q0_rep"]["entries"][0][2] = "2"
        self.assertIn("represented block payload", self.checker.check(mutated))

    def test_bundle_and_represented_categories_cannot_be_identified(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["typed_operator_dag"]["nodes"][1]["coordinate_dimension"] = 4080
        self.assertIn("typed operator DAG", self.checker.check(mutated))

    def test_arbitrary_smooth_domain_promotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["composition_obligations"]["domain_gluing"]["arbitrary_smooth_domain_claimed"] = True
        self.assertIn("composition obligations", self.checker.check(mutated))

    def test_harmonic_support_locality_promotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["claim_flags"]["HARMONIC_RESTRICTION_SUPPORT_LOCAL"] = True
        self.assertIn("fail-closed flag HARMONIC_RESTRICTION_SUPPORT_LOCAL", self.checker.check(mutated))

    def test_raw_component_matrix_claim_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["claim_flags"]["RAW_386_BY_470_COMPONENT_MATRIX_CONSTRUCTED"] = True
        self.assertIn("fail-closed flag RAW_386_BY_470_COMPONENT_MATRIX_CONSTRUCTED", self.checker.check(mutated))

    def test_formal_composition_defect_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["formal_composition_replay"]["composite_contraction_rewrite_defects"] = 1
        self.assertIn("formal composition replay", self.checker.check(mutated))

    def test_downstream_promotions_are_rejected(self) -> None:
        for flag in (
            "M1B_ACTION_DUAL_LIFT_COMPLETE", "M1B_TYPED_CYCLIC_REPLAY_COMPLETE",
            "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE",
            "M1C_COMMON_MANIFEST_REPLAY_COMPLETE", "CLASSICAL_IMPORT_GATE_PASSED",
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED",
        ):
            with self.subTest(flag=flag):
                mutated = copy.deepcopy(self.value)
                mutated["claim_flags"][flag] = True
                self.assertIn(f"fail-closed flag {flag}", self.checker.check(mutated))

    def test_generator_is_current(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(BUILDER), "--check"], cwd=ROOT, text=True, capture_output=True
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_cli_checker_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(CHECKER)], cwd=ROOT, text=True, capture_output=True
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
