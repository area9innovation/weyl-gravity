from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
RESULT = HERE / "certificates/STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1.json"
REPORT = HERE / "REPORT_STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1.md"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


CHECK = module("strict_quadratic_channel_check_test", HERE / "check_strict_386_quadratic_auxiliary_elimination_channel.py")
VERIFY = module("strict_quadratic_channel_verify_test", HERE / "verify_strict_386_quadratic_auxiliary_elimination_channel.py")


class Strict386QuadraticAuxiliaryEliminationChannelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text())
        cls.report = REPORT.read_text()

    def test_repository(self):
        self.assertEqual(CHECK.check(self.value), [])
        self.assertEqual(VERIFY.verify(self.value, self.report), [])

    def test_generated(self):
        result = subprocess.run(
            [sys.executable, str(HERE / "build_strict_386_quadratic_auxiliary_elimination_channel.py"), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def mutation_fails(self, mutate):
        value = copy.deepcopy(self.value)
        mutate(value)
        self.assertTrue(CHECK.check(value))

    def test_correction_sign_mutation(self):
        self.mutation_fails(lambda value: value["channel_pullback_replay"].__setitem__("inverse_shift_mass_cross_correction", "-1"))

    def test_residual_mutation(self):
        self.mutation_fails(lambda value: value["channel_pullback_replay"].__setitem__("transformed_source_minus_candidate_residual", "1"))

    def test_full_equivalence_overclaim(self):
        self.mutation_fails(lambda value: value["claim_flags"].__setitem__("FULL_CYCLIC_L_INFINITY_EQUIVALENCE_CONSTRUCTED", True))

    def test_gate_overclaim(self):
        self.mutation_fails(lambda value: value["claim_flags"].__setitem__("CLASSICAL_IMPORT_GATE_PASSED", True))

    def test_float_fails(self):
        value = copy.deepcopy(self.value)
        value["scope"]["carrier_rows"] = 386.0
        self.assertTrue(VERIFY.verify(value, self.report))


if __name__ == "__main__":
    unittest.main()
