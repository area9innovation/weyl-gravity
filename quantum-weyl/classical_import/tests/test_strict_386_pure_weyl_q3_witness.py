from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


CHECK = module("strict_q3_witness_check", HERE / "check_strict_386_pure_weyl_q3_witness.py")
VERIFY = module("strict_q3_witness_verify", HERE / "verify_strict_386_pure_weyl_q3_witness.py")
RESULT = HERE / "certificates/STRICT_386_PURE_WEYL_Q3_WITNESS_V1.json"


class StrictPureWeylQ3WitnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text())

    def test_generated_current(self):
        result = subprocess.run(
            [sys.executable, str(HERE / "build_strict_386_pure_weyl_q3_witness.py"), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_independent_scientific_check(self):
        self.assertEqual(CHECK.check(), [])

    def test_schema_and_report(self):
        self.assertEqual(VERIFY.verify(), [])

    def test_mutated_cancellation_rejected(self):
        value = deepcopy(self.value)
        value["arity_three_cancellation"]["computed_q1_q3"] = "0"
        self.assertTrue(CHECK.check(value))

    def test_berger_import_overclaim_rejected(self):
        value = deepcopy(self.value)
        value["q3_source_compatibility"]["sources"][0]["strict_386_direct_import"] = True
        self.assertTrue(CHECK.check(value))

    def test_authoritative_promotion_rejected(self):
        value = deepcopy(self.value)
        value["claim_flags"]["STRICT_386_AUTHORITATIVE_Q3_IMPORTED"] = True
        self.assertTrue(CHECK.check(value))


if __name__ == "__main__":
    unittest.main()
