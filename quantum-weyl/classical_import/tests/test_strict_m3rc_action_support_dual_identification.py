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
SOURCE = HERE / "build_strict_m3rc_action_support_dual_identification.py"
CHECKER = HERE / "check_strict_m3rc_action_support_dual_identification.py"
RESULT = HERE / "certificates/STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1.json"
REPORT = HERE / "REPORT_STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1.md"
SCHEMA = HERE / "schema/strict-m3rc-action-support-dual-identification-v1.schema.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "strict_m3rc_action_support_dual_source")
checker = load(CHECKER, "strict_m3rc_action_support_dual_checker")


class StrictM3RCActionSupportDualIdentificationTests(unittest.TestCase):
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

    def test_all_formal_duals_have_compact_action_representatives(self):
        action = self.value["action_pairing_identification"]
        support = self.value["support_dual_identification"]
        self.assertEqual(len(action["dual_dictionary"]), 470)
        self.assertTrue(all(item["compact_source_support"] for item in action["dual_dictionary"]))
        self.assertEqual(support["compact_source_representatives"], 470)
        self.assertEqual(action["phase_pairing_rank"], 940)

    def test_family_sign_and_phase_normalization(self):
        for item in self.value["action_pairing_identification"]["dual_dictionary"]:
            expected_sign = 1 if item["family"] == "E" else -1
            expected_phase = "-i" if expected_sign == 1 else "+i"
            self.assertEqual(item["action_krein_sign"], expected_sign)
            self.assertEqual(item["phase_normalization"], expected_phase)

    def test_sign_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["action_pairing_identification"]["dual_dictionary"][0]["action_krein_sign"] = -1
        self.assertTrue(checker.check(value))

    def test_compact_support_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["action_pairing_identification"]["dual_dictionary"][0]["compact_source_support"] = False
        self.assertTrue(checker.check(value))

    def test_full_continuous_dual_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["support_dual_identification"]["full_continuous_dual_of_all_smooth_sections_claimed"] = True
        value["claim_flags"]["FULL_ALL_ENERGY_CONTINUOUS_DUAL_IDENTIFIED"] = True
        self.assertTrue(checker.check(value))

    def test_downstream_promotions_fail(self):
        for flag in (
            "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE",
            "FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX",
            "CLASSICAL_IMPORT_GATE_PASSED",
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED",
            "QME_RESTORED",
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
        ):
            with self.subTest(flag=flag):
                value = copy.deepcopy(self.value)
                value["claim_flags"][flag] = True
                self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
