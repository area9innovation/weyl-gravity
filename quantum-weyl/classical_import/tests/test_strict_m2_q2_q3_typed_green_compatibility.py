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
RESULT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1.json"
CHECKER = ROOT / "quantum-weyl/classical_import/check_strict_m2_q2_q3_typed_green_compatibility.py"
BUILDER = ROOT / "quantum-weyl/classical_import/build_strict_m2_q2_q3_typed_green_compatibility.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("m2_green_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StrictM2Q2Q3TypedGreenCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.checker = load_checker()

    def test_independent_checker_accepts(self) -> None:
        self.assertEqual(self.checker.check(copy.deepcopy(self.value)), [])

    def test_snapshot_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["snapshot_binding"]["snapshot_sha256"] = "0" * 64
        self.assertIn("Gate-A snapshot binding", self.checker.check(mutated))

    def test_provenance_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["provenance"]["inputs"][3]["sha256"] = "f" * 64
        self.assertIn("provenance binding", self.checker.check(mutated))

    def test_q3_response_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["causal_response_names"]["plus"]["responses"]["B3"]["operator_name"]["arity"] = 2
        self.assertIn("causal response construction", self.checker.check(mutated))

    def test_arity_three_defect_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["compatibility_replay"]["q1_q3_plus_q2_q2_identity"] = 1
        self.assertIn("nonlinear identity replay", self.checker.check(mutated))

    def test_second_source_coefficient_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["lambda2_general_source_cocycle"]["coefficients"]["q3_image"] = "1/5"
        self.assertIn("general second-source closure", self.checker.check(mutated))

    def test_mixed_tree_promotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["claim_flags"]["STRICT_386_ARBITRARY_MIXED_SIGN_TREES_CERTIFIED"] = True
        self.assertIn("fail-closed flag STRICT_386_ARBITRARY_MIXED_SIGN_TREES_CERTIFIED", self.checker.check(mutated))

    def test_hadamard_promotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["claim_flags"]["FULL_COMPLEX_BRST_HADAMARD_TWO_POINT_FUNCTION_CONSTRUCTED"] = True
        self.assertIn("fail-closed flag FULL_COMPLEX_BRST_HADAMARD_TWO_POINT_FUNCTION_CONSTRUCTED", self.checker.check(mutated))

    def test_generator_is_current(self) -> None:
        completed = subprocess.run([sys.executable, str(BUILDER), "--check"], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
