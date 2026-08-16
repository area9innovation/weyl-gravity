from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
SOURCE = HERE / "build_strict_typed_residual_cyclicity.py"
CHECKER = HERE / "check_strict_typed_residual_cyclicity.py"
RESULT = HERE / "certificates/STRICT_TYPED_RESIDUAL_CYCLICITY_V1.json"
REPORT = HERE / "REPORT_STRICT_TYPED_RESIDUAL_CYCLICITY_V1.md"
SCHEMA = HERE / "schema/strict-typed-residual-cyclicity-v1.schema.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "strict_typed_residual_cyclicity_source")
checker = load(CHECKER, "strict_typed_residual_cyclicity_checker")


class StrictTypedResidualCyclicityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_generated_current_schema_and_independent_replay(self):
        certificate, report = producer.generated()
        self.assertEqual(RESULT.read_bytes(), certificate)
        self.assertEqual(REPORT.read_bytes(), report)
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.value)
        self.assertEqual(checker.check(copy.deepcopy(self.value)), [])

    def test_all_five_blocks_are_exact(self):
        blocks = self.value["exact_cyclic_replay"]["block_replays"]
        self.assertEqual([block["energy"] for block in blocks], [2, 3, 4, 5, 6])
        self.assertTrue(all(block["total_identity_defects"] == 0 for block in blocks))
        self.assertEqual(sum(block["residual_pairing_rank"] for block in blocks), 940)

    def test_adjoint_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["exact_cyclic_replay"]["block_replays"][0]["identity_defects"]["projection_equals_inclusion_sharp"] = 1
        value["exact_cyclic_replay"]["block_replays"][0]["total_identity_defects"] = 1
        self.assertTrue(checker.check(value))

    def test_map_hash_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["exact_cyclic_replay"]["block_replays"][0]["map_hashes"]["iota_cotangent"] = "0" * 64
        self.assertTrue(checker.check(value))

    def test_authority_and_all_energy_promotions_fail(self):
        for field in ("formal_source_is_authoritative_full_BV_source", "full_continuous_all_energy_dual_identified"):
            with self.subTest(field=field):
                value = copy.deepcopy(self.value)
                value["typed_carrier"][field] = True
                self.assertTrue(checker.check(value))

    def test_downstream_promotions_fail(self):
        for flag in (
            "FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX",
            "M1_COMMON_STRICT_SNAPSHOT_COMPLETE",
            "CLASSICAL_IMPORT_GATE_PASSED",
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED",
            "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED",
            "QME_RESTORED",
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
        ):
            with self.subTest(flag=flag):
                value = copy.deepcopy(self.value)
                value["claim_flags"][flag] = True
                self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
