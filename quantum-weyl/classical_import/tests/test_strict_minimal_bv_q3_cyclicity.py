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
RESULT = HERE / "certificates/STRICT_MINIMAL_BV_Q3_CYCLICITY_V1.json"
REPORT = HERE / "REPORT_STRICT_MINIMAL_BV_Q3_CYCLICITY_V1.md"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
CHECK = module("strict_q3_cyclic_check", HERE / "check_strict_minimal_bv_q3_cyclicity.py")
VERIFY = module("strict_q3_cyclic_verify", HERE / "verify_strict_minimal_bv_q3_cyclicity.py")


class StrictMinimalBvQ3CyclicityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.report = REPORT.read_text()

    def test_repository_result(self) -> None:
        self.assertEqual(CHECK.check(self.value), [])
        self.assertEqual(VERIFY.verify(self.value, self.report), [])

    def test_generated_current(self) -> None:
        result = subprocess.run([sys.executable, str(HERE / "build_strict_minimal_bv_q3_cyclicity.py"), "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def mutation_fails(self, mutate) -> None:
        value = copy.deepcopy(self.value)
        mutate(value)
        self.assertTrue(CHECK.check(value))

    def test_weight_mutation_fails(self) -> None:
        self.mutation_fails(lambda value: value["cyclic_four_form"]["metric_component_weights"].__setitem__(1, "1"))

    def test_pointwise_promotion_fails(self) -> None:
        self.mutation_fails(lambda value: value["variational_proof"].__setitem__("result_kind_boundary", "pointwise equality"))

    def test_386_promotion_fails(self) -> None:
        self.mutation_fails(lambda value: value["claim_flags"].__setitem__("STRICT_386_Q3_STABILIZED", True))


if __name__ == "__main__":
    unittest.main()
