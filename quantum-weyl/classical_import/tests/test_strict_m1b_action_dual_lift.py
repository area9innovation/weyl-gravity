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
RESULT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1B_ACTION_DUAL_LIFT_V1.json"
CHECKER = ROOT / "quantum-weyl/classical_import/check_strict_m1b_action_dual_lift.py"
BUILDER = ROOT / "quantum-weyl/classical_import/build_strict_m1b_action_dual_lift.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("m1b_action_dual_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class M1BActionDualLiftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.checker = load_checker()

    def test_independent_checker_accepts(self) -> None:
        self.assertEqual(self.checker.check(copy.deepcopy(self.value)), [])

    def test_transpose_coefficient_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["represented_dual_lift"]["blocks"][0]["matrices"]["q_dual_rep"]["entries"][0][2] = "2"
        self.assertIn("represented dual block payload", self.checker.check(mutated))

    def test_compact_source_dictionary_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["action_residual_coordinate_actions"][0]["compact_source_representative"] = "invented"
        self.assertIn("action residual crosswalk", self.checker.check(mutated))

    def test_verification_core_cannot_be_promoted(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["typed_adjoint_dag"]["nodes"][3]["authority"] = "AUTHORITATIVE"
        self.assertIn("typed adjoint DAG", self.checker.check(mutated))

    def test_full_dual_promotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["claim_flags"]["FULL_4080_ALGEBRAIC_DUAL_COMPACT_SOURCE_IDENTIFIED"] = True
        self.assertIn("fail-closed flag FULL_4080_ALGEBRAIC_DUAL_COMPACT_SOURCE_IDENTIFIED", self.checker.check(mutated))

    def test_downstream_promotions_are_rejected(self) -> None:
        for flag in (
            "M1B_TYPED_CYCLIC_REPLAY_COMPLETE", "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE",
            "M1C_COMMON_MANIFEST_REPLAY_COMPLETE", "CLASSICAL_IMPORT_GATE_PASSED",
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED",
        ):
            with self.subTest(flag=flag):
                mutated = copy.deepcopy(self.value)
                mutated["claim_flags"][flag] = True
                self.assertIn(f"fail-closed flag {flag}", self.checker.check(mutated))

    def test_content_digest_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["content_sha256"] = "0" * 64
        self.assertIn("content digest", self.checker.check(mutated))

    def test_generator_is_current(self) -> None:
        completed = subprocess.run([sys.executable, str(BUILDER), "--check"], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_cli_checker_passes(self) -> None:
        completed = subprocess.run([sys.executable, str(CHECKER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
