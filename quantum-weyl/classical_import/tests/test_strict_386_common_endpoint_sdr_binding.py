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
SOURCE = HERE / "build_strict_386_common_endpoint_sdr_binding.py"
CHECKER = HERE / "check_strict_386_common_endpoint_sdr_binding.py"
RESULT = HERE / "certificates/STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1.json"
REPORT = HERE / "REPORT_STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1.md"
SCHEMA = HERE / "schema/strict-386-common-endpoint-sdr-binding-v1.schema.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "strict_386_common_endpoint_sdr_binding_source")
checker = load(CHECKER, "strict_386_common_endpoint_sdr_binding_checker")


class Strict386CommonEndpointSdrBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_generated_current(self):
        certificate, report = producer.generated()
        self.assertEqual(RESULT.read_bytes(), certificate)
        self.assertEqual(REPORT.read_bytes(), report)

    def test_schema_and_independent_replay(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.value)
        self.assertEqual(checker.check(copy.deepcopy(self.value)), [])

    def test_manifest_binds_exact_common_carrier(self):
        manifest = self.value["common_manifest"]
        self.assertEqual(
            (manifest["carrier_rows"], manifest["endpoint_rows"], manifest["contracted_rows"]),
            (386, 30, 356),
        )
        self.assertEqual(len(manifest["artifact_pins"]), 10)
        self.assertEqual(len(manifest["object_hashes"]), 17)
        self.assertEqual(self.value["exact_replay"]["compatibility_links_checked"], 15)
        self.assertTrue(all(self.value["compatibility_checks"].values()))

    def test_manifest_hash_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["common_manifest"]["object_hashes"]["graph_q1_sha256"] = "0" * 64
        self.assertTrue(checker.check(value))

    def test_compatibility_promotion_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["compatibility_checks"]["q3_pins_accepted_q2_object"] = False
        self.assertTrue(checker.check(value))

    def test_residual_and_gate_firewalls(self):
        for flag in (
            "M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED",
            "FULL_RESIDUAL_CYCLIC_PAIRING_CERTIFIED",
            "NEW_GATE_A_TOP_LEVEL_HASH_ACCEPTED",
            "CLASSICAL_IMPORT_GATE_PASSED",
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED",
            "QME_RESTORED",
        ):
            with self.subTest(flag=flag):
                value = copy.deepcopy(self.value)
                value["claim_flags"][flag] = True
                self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
