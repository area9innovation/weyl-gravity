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
RESULT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1B_TYPED_CYCLIC_COMPOSITE_V1.json"
CHECKER = ROOT / "quantum-weyl/classical_import/check_strict_m1b_typed_cyclic_composite.py"
BUILDER = ROOT / "quantum-weyl/classical_import/build_strict_m1b_typed_cyclic_composite.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("m1b_cyclic_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class M1BTypedCyclicCompositeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.checker = load_checker()

    def test_independent_checker_accepts(self) -> None:
        self.assertEqual(self.checker.check(copy.deepcopy(self.value)), [])

    def test_map_hash_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["exact_cyclic_replay"]["blocks"][0]["map_hashes"]["q_cyclic"] = "0" * 64
        self.assertIn("exact cyclic block replay", self.checker.check(mutated))

    def test_identity_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["exact_cyclic_replay"]["blocks"][0]["identity_defects"]["inclusion_isometry_defects"] = 1
        self.assertIn("exact cyclic block replay", self.checker.check(mutated))

    def test_formal_source_cannot_be_promoted(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["typed_cyclic_dag"]["nodes"][5]["authority"] = "AUTHORITATIVE"
        self.assertIn("typed cyclic DAG", self.checker.check(mutated))

    def test_legacy_boundary_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["legacy_comparison_boundary"]["deleted_test_doublet_cotangent_coordinates"] = 0
        self.assertIn("legacy comparison boundary", self.checker.check(mutated))

    def test_downstream_promotions_are_rejected(self) -> None:
        for flag in (
            "M1C_COMMON_MANIFEST_REPLAY_COMPLETE", "CLASSICAL_IMPORT_GATE_PASSED",
            "NONLINEAR_GREEN_COMPATIBILITY_CERTIFIED", "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED",
            "QME_RESTORED",
        ):
            with self.subTest(flag=flag):
                mutated = copy.deepcopy(self.value)
                mutated["claim_flags"][flag] = True
                self.assertIn(f"fail-closed flag {flag}", self.checker.check(mutated))

    def test_content_digest_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["content_sha256"] = "f" * 64
        self.assertIn("content digest", self.checker.check(mutated))

    def test_generator_is_current(self) -> None:
        completed = subprocess.run([sys.executable, str(BUILDER), "--check"], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_cli_checker_passes(self) -> None:
        completed = subprocess.run([sys.executable, str(CHECKER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
