from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.json"
SCHEMA = HERE / "schema/strict-386-local-cyclic-pairing-closure-v1.schema.json"
BUILDER = HERE / "build_strict_386_local_cyclic_pairing_closure.py"
CHECKER = HERE / "check_strict_386_local_cyclic_pairing_closure.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("m4l_checker", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Strict386LocalCyclicPairingClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.checker = load_checker()

    def test_generated_current(self) -> None:
        subprocess.run([sys.executable, str(BUILDER), "--check"], cwd=ROOT, check=True)

    def test_schema_and_independent_replay(self) -> None:
        Draft202012Validator(json.loads(SCHEMA.read_text())).validate(self.value)
        self.assertEqual([], self.checker.check())

    def test_local_pairing_and_cyclicity_close(self) -> None:
        replay = self.value["pairing_replay"]
        self.assertEqual((386, 410, 386), (replay["carrier_rows"], replay["nonzero_ordered_pairing_entries"], replay["exact_rational_rank"]))
        self.assertTrue(self.value["claim_flags"]["M4L_LOCAL_GRAPH_CYCLIC_PAIRING_COMPLETE"])
        self.assertTrue(all(item["status"] == "COMPLETE" for item in self.value["obligation_ledger"][:-1]))

    def test_residual_firewall_remains_closed(self) -> None:
        flags = self.value["claim_flags"]
        self.assertFalse(flags["M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED"])
        self.assertFalse(flags["M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE"])
        self.assertFalse(flags["CLASSICAL_IMPORT_GATE_PASSED"])

    def test_pairing_rank_mutation_fails(self) -> None:
        mutated = deepcopy(self.value)
        mutated["pairing_replay"]["exact_rational_rank"] = 385
        self.assertIn("independent full-pairing replay", self.checker.check(mutated))

    def test_false_residual_promotion_fails(self) -> None:
        mutated = deepcopy(self.value)
        mutated["claim_flags"]["M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE"] = True
        self.assertIn("claim promotion M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE", self.checker.check(mutated))


if __name__ == "__main__":
    unittest.main()
