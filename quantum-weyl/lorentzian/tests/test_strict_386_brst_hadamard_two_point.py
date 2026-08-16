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
RESULT = ROOT / "quantum-weyl/lorentzian/certificates/STRICT_386_BRST_HADAMARD_TWO_POINT_V1.json"
CHECKER = ROOT / "quantum-weyl/lorentzian/check_strict_386_brst_hadamard_two_point.py"
BUILDER = ROOT / "quantum-weyl/lorentzian/build_strict_386_brst_hadamard_two_point.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("strict_hadamard_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Strict386BRSTHadamardTwoPointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.checker = load_checker()

    def test_independent_checker_accepts(self) -> None:
        self.assertEqual(self.checker.check(copy.deepcopy(self.value)), [])

    def test_generator_is_current(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(BUILDER), "--check"], cwd=ROOT, text=True, capture_output=True
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_classical_snapshot_mutation_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.value)
        mutant["scope"]["classical_snapshot_sha256"] = "0" * 64
        self.assertIn("classical causal-envelope gate", self.checker.check(mutant))

    def test_modal_CCR_mutation_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.value)
        mutant["modal_exact_checks"]["positive_lambda"]["symbolic_replay"]["CCR_difference"] = False
        self.assertIn("independent modal replay", self.checker.check(mutant))

    def test_zero_mode_deletion_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.value)
        mutant["modal_exact_checks"]["zero_lambda"]["arbitrary_scale_or_zero_mode_deletion"] = True
        self.assertIn("independent modal replay", self.checker.check(mutant))

    def test_transport_map_mutation_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.value)
        graph = mutant["two_point_operator_names"]["plus"]["full_graph_386_name"]
        graph["children"][0]["map_id"] = "wrong_inclusion"
        self.assertIn("operator-name transport", self.checker.check(mutant))

    def test_wavefront_failure_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.value)
        mutant["proof_obligations"]["Hadamard_wavefront_set"]["status"] = "OPEN"
        self.assertIn("proof-obligation result", self.checker.check(mutant))

    def test_positive_state_promotion_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.value)
        mutant["claim_flags"]["STRICT_386_POSITIVE_HADAMARD_STATE_CONSTRUCTED"] = True
        self.assertIn(
            "fail-closed flag STRICT_386_POSITIVE_HADAMARD_STATE_CONSTRUCTED",
            self.checker.check(mutant),
        )

    def test_QME_promotion_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.value)
        mutant["claim_flags"]["LORENTZIAN_QME_RESTORED"] = True
        self.assertIn("fail-closed flag LORENTZIAN_QME_RESTORED", self.checker.check(mutant))

    def test_snapshot_digest_mutation_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.value)
        mutant["hadamard_snapshot"]["plus_name_sha256"] = "f" * 64
        self.assertIn("Hadamard snapshot binding", self.checker.check(mutant))


if __name__ == "__main__":
    unittest.main()
