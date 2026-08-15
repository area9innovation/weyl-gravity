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
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/classical-minimal-bv-q3-export-v1.md"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
CHECK = module("classical_minimal_q3_check", HERE / "check_classical_minimal_bv_q3_export_v1.py")
VERIFY = module("classical_minimal_q3_verify", HERE / "verify_classical_minimal_bv_q3_export_v1.py")


class ClassicalMinimalBvQ3ExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.report = REPORT.read_text()

    def test_repository_result(self) -> None:
        self.assertEqual(CHECK.check(self.value), [])
        self.assertEqual(VERIFY.verify(self.value, self.report), [])

    def test_generated_artifacts_current(self) -> None:
        result = subprocess.run(
            [sys.executable, str(HERE / "classical_minimal_bv_q3_export_v1.py"), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def mutation_fails(self, mutate) -> None:
        value = copy.deepcopy(self.value)
        mutate(value)
        self.assertTrue(CHECK.check(value))

    def test_root_mutation_fails(self) -> None:
        self.mutation_fails(lambda value: value["natural_operator_ast"].__setitem__("root_node", "E_g"))

    def test_hidden_factorial_mutation_fails(self) -> None:
        self.mutation_fails(lambda value: value["natural_operator_ast"]["nodes"][-1]["parameters"].__setitem__("hidden_factorial", True))

    def test_second_nonzero_row_fails(self) -> None:
        self.mutation_fails(lambda value: value["minimal_q3_support"]["rows"][0].__setitem__("q3_status", "NONZERO_NATURAL_OPERATOR"))

    def test_arity_three_promotion_fails(self) -> None:
        self.mutation_fails(lambda value: value["claim_flags"].__setitem__("ARITY_THREE_Q_SQUARED_IDENTITY_REPLAYED", True))

    def test_float_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["scope"]["carrier_dimension"] = 6.0
        self.assertTrue(any("floating-point" in item for item in VERIFY.verify(value, self.report)))


if __name__ == "__main__":
    unittest.main()
