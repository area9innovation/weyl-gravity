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
SOURCE = HERE / "build_strict_m1_common_snapshot_preflight.py"
CHECKER = HERE / "check_strict_m1_common_snapshot_preflight.py"
RESULT = HERE / "certificates/STRICT_M1_COMMON_SNAPSHOT_PREFLIGHT_V1.json"
REPORT = HERE / "REPORT_STRICT_M1_COMMON_SNAPSHOT_PREFLIGHT_V1.md"
SCHEMA = HERE / "schema/strict-m1-common-snapshot-preflight-v1.schema.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "strict_m1_common_snapshot_preflight_source")
checker = load(CHECKER, "strict_m1_common_snapshot_preflight_checker")


class StrictM1CommonSnapshotPreflightTests(unittest.TestCase):
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

    def test_carrier_categories_are_not_collapsed(self):
        carriers = {row["id"]: row for row in self.value["carrier_inventory"]}
        self.assertEqual(carriers["LOCAL_GRAPH_BV_386"]["dimension"], 386)
        self.assertEqual(carriers["FORMAL_COTANGENT_COMPARISON_8980"]["dimension"], 8980)
        self.assertEqual(carriers["ACTION_RESIDUAL_940"]["dimension"], 940)
        self.assertEqual(carriers["FORMAL_COTANGENT_COMPARISON_8980"]["status"], "NOT_AUTHORITATIVE_FULL_BV_SOURCE")

    def test_export_and_hash_blocker_partition(self):
        self.assertEqual(self.value["counts"], {
            "exports_total": 20,
            "exports_common_object_ready": 14,
            "exports_blocked_full_typed_ledger": 2,
            "exports_blocked_composite_contraction": 4,
            "hashes_total": 7,
            "hash_objects_ready_await_binding": 4,
            "hashes_blocked_before_binding": 3,
            "freeze_checks_total": 10,
            "freeze_checks_common_snapshot_replayed": 0,
        })

    def test_ledger_completion_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["local_row_ledger_audit"]["missing_explicit_fields"] = []
        value["local_row_ledger_audit"]["all_rows_have_required_explicit_fields"] = True
        self.assertTrue(checker.check(value))

    def test_composite_completion_mutation_fails(self):
        value = copy.deepcopy(self.value)
        edge = next(row for row in value["cross_category_edges"] if row["id"] == "M1B_ACTUAL_REPRESENTED_COMPOSITE_CONTRACTION")
        edge["status"] = "COMPLETE"
        self.assertTrue(checker.check(value))

    def test_export_partition_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["export_inventory"][0]["m1_preflight_status"] = "COMMON_OBJECT_READY_FOR_BINDING"
        self.assertTrue(checker.check(value))

    def test_downstream_promotions_fail(self):
        for flag in (
            "M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE",
            "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE",
            "M1C_COMMON_MANIFEST_REPLAY_COMPLETE",
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
