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
RESULT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1.json"
CHECKER = ROOT / "quantum-weyl/classical_import/check_strict_m1a_represented_carrier_crosswalk.py"
BUILDER = ROOT / "quantum-weyl/classical_import/build_strict_m1a_represented_carrier_crosswalk.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("m1a3_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class M1ARepresentedCarrierCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.checker = load_checker()

    def test_independent_checker_accepts(self) -> None:
        self.assertEqual(self.checker.check(copy.deepcopy(self.value)), [])

    def test_sector_species_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["represented_endpoint_rows"][0]["local_species_id"] = "omega"
        self.assertTrue(any("represented row crosswalk" in error for error in self.checker.check(mutated)))

    def test_test_doublet_promotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["test_nonminimal_rows"][0]["bv_ghost_number"] = -1
        self.assertTrue(any("test local field applicability" in error for error in self.checker.check(mutated)))

    def test_action_dual_weight_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["action_residual_dual_rows"][0]["conformal_compact_weight"] = 2
        self.assertTrue(any("dual residual typing" in error for error in self.checker.check(mutated)))

    def test_source_coordinate_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["action_residual_primal_rows"][0]["source_coordinate_label"] = "E2:metric_tf:0"
        self.assertTrue(any("primal residual crosswalk" in error for error in self.checker.check(mutated)))

    def test_gate_promotions_are_rejected(self) -> None:
        for flag in ("M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE", "CLASSICAL_IMPORT_GATE_PASSED", "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED"):
            with self.subTest(flag=flag):
                mutated = copy.deepcopy(self.value)
                mutated["claim_flags"][flag] = True
                self.assertIn(f"fail-closed flag {flag}", self.checker.check(mutated))

    def test_generator_is_current(self) -> None:
        completed = subprocess.run([sys.executable, str(BUILDER), "--check"], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_cli_checker_passes(self) -> None:
        completed = subprocess.run([sys.executable, str(CHECKER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
