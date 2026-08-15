from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
RESULT = HERE / "certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
CHECK = module(
    "strict_minimal_bv_cyclic_sign_check",
    HERE / "check_strict_minimal_bv_cyclic_sign_reconciliation.py",
)
VERIFY = module(
    "strict_minimal_bv_cyclic_sign_verify",
    HERE / "verify_strict_minimal_bv_cyclic_sign_reconciliation.py",
)


class StrictMinimalBVCyclicSignReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.report = (
            HERE / "REPORT_STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.md"
        ).read_text()

    def test_repository_result(self) -> None:
        self.assertEqual(CHECK.check(self.value), [])

    def test_schema_determinism_and_report(self) -> None:
        self.assertEqual(VERIFY.verify(self.value, self.report), [])

    def test_omitting_diff_noether_sign_fails(self) -> None:
        value = copy.deepcopy(self.value)
        row = next(
            row
            for row in value["sign_translation"]["q2_rows"]
            if row["component_id"] == "q2_cstar_hhstar__forward"
        )
        row["translation_multiplier"] = 1
        row["translated_coefficient_relative_to_primary"] *= -1
        self.assertTrue(
            any("conjugation crosswalk" in error for error in CHECK.check(value))
        )

    def test_pairing_weight_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        row = next(
            row
            for row in value["canonical_pairing"]["entries"]
            if row["left"] == "h_01" and row["right"] == "h_star_01"
        )
        row["coefficient"] = "1"
        self.assertTrue(any("component pairing" in error for error in CHECK.check(value)))

    def test_cyclicity_promotion_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["cyclicity_receiver"]["translated_convention_defect"]["coefficient_count"] = 1
        self.assertTrue(any("receiver summary" in error for error in CHECK.check(value)))

    def test_D_or_gate_promotion_fails(self) -> None:
        for flag in ("D_Q2_DERIVATION_REPLAYED", "CLASSICAL_IMPORT_GATE_PASSED"):
            with self.subTest(flag=flag):
                value = copy.deepcopy(self.value)
                value["claim_flags"][flag] = True
                self.assertTrue(any("claim flags" in error for error in CHECK.check(value)))

    def test_report_overclaim_fails(self) -> None:
        report = self.report.replace("Gate A remains fail closed", "Gate A passed")
        self.assertTrue(any("report missing" in error for error in VERIFY.verify(self.value, report)))


if __name__ == "__main__":
    unittest.main()
