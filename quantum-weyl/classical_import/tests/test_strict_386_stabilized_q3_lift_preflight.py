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
RESULT = HERE / "certificates/STRICT_386_STABILIZED_Q3_LIFT_PREFLIGHT_V1.json"
REPORT = HERE / "REPORT_STRICT_386_STABILIZED_Q3_LIFT_PREFLIGHT_V1.md"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
CHECK = module("strict_386_q3_preflight_check", HERE / "check_strict_386_stabilized_q3_lift_preflight.py")
VERIFY = module("strict_386_q3_preflight_verify", HERE / "verify_strict_386_stabilized_q3_lift_preflight.py")


class Strict386StabilizedQ3LiftPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.report = REPORT.read_text()

    def test_repository_result(self) -> None:
        self.assertEqual(CHECK.check(self.value), [])
        self.assertEqual(VERIFY.verify(self.value, self.report), [])

    def test_generated_current(self) -> None:
        result = subprocess.run(
            [sys.executable, str(HERE / "build_strict_386_stabilized_q3_lift_preflight.py"), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def mutation_fails(self, mutate) -> None:
        value = copy.deepcopy(self.value)
        mutate(value)
        self.assertTrue(CHECK.check(value))

    def test_channel_removal_fails(self) -> None:
        self.mutation_fails(lambda value: value["graph_transport_dag"]["ternary_block_channel_ledger"].pop())

    def test_authoritative_promotion_fails(self) -> None:
        self.mutation_fails(lambda value: value["claim_flags"].__setitem__("STRICT_386_AUTHORITATIVE_FULL_Q3_IMPORTED", True))

    def test_theory_identity_promotion_fails(self) -> None:
        self.mutation_fails(lambda value: value["theory_identity_boundary"].__setitem__("candidate_equals_authoritative_nonminimal_classical_theory", "CERTIFIED"))

    def test_cyclicity_mutation_fails(self) -> None:
        self.mutation_fails(lambda value: value["identity_transport"]["q3_cyclicity_mod_d"].__setitem__("defects_mod_d", 1))

    def test_float_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["scope"]["carrier_rows"] = 386.0
        self.assertTrue(VERIFY.verify(value, self.report))


if __name__ == "__main__":
    unittest.main()
