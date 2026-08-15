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
RESULT = HERE / "certificates/STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1.json"
REPORT = HERE / "REPORT_STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1.md"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
CHECK = module("strict_arity_three_check", HERE / "check_strict_minimal_bv_arity_three_identity.py")
VERIFY = module("strict_arity_three_verify", HERE / "verify_strict_minimal_bv_arity_three_identity.py")


class StrictMinimalBvArityThreeIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.report = REPORT.read_text()

    def test_repository_result_and_full_replay(self) -> None:
        self.assertEqual(CHECK.check(self.value), [])
        self.assertEqual(VERIFY.verify(self.value, self.report, replay=False), [])

    def test_generated_artifacts_current(self) -> None:
        result = subprocess.run(
            [sys.executable, str(HERE / "build_strict_minimal_bv_arity_three_identity.py"), "--check"],
            cwd=ROOT,
            env={**__import__("os").environ, "PYTHONPATH": str(HERE)},
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def mutation_fails_static(self, mutate) -> None:
        value = copy.deepcopy(self.value)
        mutate(value)
        self.assertTrue(CHECK.check(value, replay=False))

    def test_channel_multiplier_mutation_fails(self) -> None:
        self.mutation_fails_static(lambda value: value["channel_inventory"]["channels"][0]["paths"][0].__setitem__("multiplier", 9))

    def test_channel_count_mutation_fails(self) -> None:
        self.mutation_fails_static(lambda value: value["channel_inventory"].__setitem__("channel_count", 71))

    def test_mutation_ledger_removal_fails(self) -> None:
        self.mutation_fails_static(lambda value: value["exact_receiver"].__setitem__("mutation_checks", []))

    def test_cyclicity_promotion_fails(self) -> None:
        self.mutation_fails_static(lambda value: value["claim_flags"].__setitem__("MINIMAL_BV_Q3_CYCLICITY_CERTIFIED", True))

    def test_386_promotion_fails(self) -> None:
        self.mutation_fails_static(lambda value: value["claim_flags"].__setitem__("STRICT_386_Q3_STABILIZED", True))

    def test_float_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["channel_inventory"]["channel_count"] = 72.0
        self.assertTrue(any("floating-point" in item for item in VERIFY.verify(value, self.report, replay=False)))


if __name__ == "__main__":
    unittest.main()
