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
RESULT = HERE / "certificates/STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1.json"
REPORT = HERE / "REPORT_STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1.md"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
CHECK = module("strict_minimal_q3_import_check", HERE / "check_strict_pure_weyl_minimal_bv_q3_import.py")
VERIFY = module("strict_minimal_q3_import_verify", HERE / "verify_strict_pure_weyl_minimal_bv_q3_import.py")
SEMANTICS = module("strict_minimal_q3_import_semantics", HERE / "pure_weyl_cubic_natural_operator.py")


class StrictPureWeylMinimalBvQ3ImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.report = REPORT.read_text()

    def test_repository_result(self) -> None:
        self.assertEqual(VERIFY.verify(self.value, self.report), [])

    def test_generated_artifacts_current(self) -> None:
        result = subprocess.run(
            [sys.executable, str(HERE / "build_strict_pure_weyl_minimal_bv_q3_import.py"), "--check"],
            cwd=ROOT,
            env={**__import__("os").environ, "PYTHONPATH": str(HERE)},
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def mutation_fails(self, mutate) -> None:
        value = copy.deepcopy(self.value)
        mutate(value)
        self.assertTrue(CHECK.check(value, replay_exact=False))

    def test_carrier_change_fails(self) -> None:
        self.mutation_fails(lambda value: value["import_bridge"].__setitem__("carrier_or_convention_change", True))

    def test_symmetry_mutation_fails(self) -> None:
        self.mutation_fails(lambda value: value["exact_receiver_checks"].__setitem__("S3_exact_symmetry", False))

    def test_polarization_mutation_fails(self) -> None:
        self.mutation_fails(lambda value: value["exact_receiver_checks"]["seven_diagonal_polarization"].__setitem__("exact_equality", False))

    def test_arity_three_promotion_fails(self) -> None:
        self.mutation_fails(lambda value: value["claim_flags"].__setitem__("MINIMAL_BV_ARITY_THREE_IDENTITY_CERTIFIED", True))

    def test_lorentzian_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["dependency_tags"].append("LORENTZIAN-CAUSAL")
        self.assertTrue(VERIFY.verify(value, self.report, replay_exact=False))

    def test_semantics_rejects_factorial_drift(self) -> None:
        classical = json.loads((ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1.json").read_text())
        ast = copy.deepcopy(classical["natural_operator_ast"])
        ast["nodes"][-1]["parameters"]["hidden_factorial"] = True
        with self.assertRaisesRegex(SEMANTICS.CubicNaturalOperatorError, "convention"):
            SEMANTICS.validate_imported_ast(ast)


if __name__ == "__main__":
    unittest.main()
