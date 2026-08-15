from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "quantum-weyl/classical_import/build_strict_386_shifted_auxiliary_cubic_inventory.py"
CHECKER = ROOT / "quantum-weyl/classical_import/check_strict_386_shifted_auxiliary_cubic_inventory.py"
RESULT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class ShiftedAuxiliaryReceiverTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load(SOURCE, "shifted_auxiliary_receiver_source")
        cls.checker = load(CHECKER, "shifted_auxiliary_receiver_checker")
        cls.value = json.loads(RESULT.read_text())

    def test_generated_current(self):
        self.assertEqual(self.source.generated()[0], RESULT.read_bytes())

    def test_independent_checker(self):
        self.assertEqual(self.checker.check(self.value), [])

    def test_component_counts(self):
        lift = self.value["vv_BV_cotangent_lift"]
        self.assertEqual((len(lift["field_map_entries"]), len(lift["cotangent_partner_entries"])), (22, 16))
        self.assertEqual(lift["canonicality_defects"], 0)

    def test_carrier_boundary(self):
        lift = self.value["vv_BV_cotangent_lift"]
        self.assertEqual(lift["quadratic_active_output_rows"] + lift["quadratic_zero_output_rows"], 386)

    def test_fail_closed(self):
        flags = self.value["claim_flags"]
        self.assertTrue(flags["VV_BV_COTANGENT_LIFT_CANONICAL"])
        self.assertFalse(flags["FULL_386_BV_COTANGENT_LIFT_SERIALIZED"])
        self.assertFalse(flags["FULL_CYCLIC_L_INFINITY_EQUIVALENCE_CONSTRUCTED"])

    def test_mutation_detected(self):
        changed = json.loads(json.dumps(self.value))
        changed["vv_BV_cotangent_lift"]["cotangent_partner_entries"][0]["coefficient"] = "0"
        self.assertTrue(self.checker.check(changed))


if __name__ == "__main__":
    unittest.main()
