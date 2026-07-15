from __future__ import annotations

from copy import deepcopy
import json
import sys
import unittest
from pathlib import Path


QUANTUM_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(QUANTUM_ROOT))

from transfer.d_derivation_defect import (
    HT1_PATH,
    OUTPUT_PATH,
    SCHEMA_PATH,
    _canonical_hash,
    analyze_selected_q2,
    build_certificate,
    validate_certificate,
)


class DDerivationDefectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_checked_in_certificate_reproduces(self) -> None:
        checked = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(checked, self.certificate)

    def test_all_available_q2_defect_tensors_are_recorded_and_zero(self) -> None:
        analysis = self.certificate["analysis_payload"]
        self.assertEqual(len(analysis["defect_tensors"]), 4)
        self.assertEqual(
            analysis["checks"]["full_selected_defect_coefficient_count"],
            529470,
        )
        self.assertTrue(
            all(not tensor["entries"] for tensor in analysis["defect_tensors"].values())
        )
        self.assertEqual(
            analysis["selected_verdict"],
            "SELECTED_RESIDUAL_D_DERIVATION_HOLDS_AT_ARITY_TWO",
        )

    def test_every_nonzero_component_has_D_weight_and_particle_ledger(self) -> None:
        ledgers = self.certificate["analysis_payload"]["component_ledgers"]
        self.assertEqual(
            sum(item["source_nonzero_component_count"] for item in ledgers),
            3976,
        )
        self.assertTrue(all(item["D_weight_violation_count"] == 0 for item in ledgers))
        changes = {item["block"]: item["particle_number_change"] for item in ledgers}
        self.assertEqual(changes["matter_matter_to_ghost_momentum"], -2)
        self.assertEqual(sum(value != 0 for value in changes.values()), 1)

    def test_full_interacting_D_quotient_remains_input_gated(self) -> None:
        self.assertEqual(self.certificate["setting_verdict"], "INPUT_GATE_BLOCKED")
        self.assertTrue(
            all(
                status.startswith(("BLOCKED", "NOT_"))
                for status in self.certificate["input_gates"].values()
            )
        )

    def test_hash_consistent_analysis_tamper_is_semantically_rejected(self) -> None:
        certificate = deepcopy(self.certificate)
        certificate["analysis_payload"]["selected_verdict"] = "SELECTED_RESIDUAL_D_DERIVATION_DEFECT_NONZERO"
        certificate["analysis_payload_sha256"] = _canonical_hash(certificate["analysis_payload"])
        with self.assertRaisesRegex(ValueError, "disagrees with HT1"):
            validate_certificate(certificate)

    def test_non_equivariant_q2_input_produces_explicit_defect(self) -> None:
        payload = json.loads(HT1_PATH.read_text(encoding="utf-8"))["transfer_payload"]
        entries = payload["q2"]["ghost_matter_to_matter"]["matrices"]["Lx"]["entries"]
        entries.insert(1, [0, 5, "Integer(1)"])
        analysis = analyze_selected_q2(payload)
        ledger = next(
            item
            for item in analysis["component_ledgers"]
            if item["block"] == "ghost_matter_to_matter"
        )
        self.assertGreater(ledger["D_weight_violation_count"], 0)
        self.assertGreater(ledger["defect_nonzero_component_count"], 0)
        self.assertEqual(
            analysis["selected_verdict"],
            "SELECTED_RESIDUAL_D_DERIVATION_DEFECT_NONZERO",
        )

    def test_false_setting_promotion_is_rejected(self) -> None:
        certificate = deepcopy(self.certificate)
        certificate["setting_verdict"] = "INTERACTING_CARTAN_EXISTS"
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate_certificate(certificate)

    def test_schema_receipt_is_present(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "selected-residual-d-derivation-v1.schema.json")


if __name__ == "__main__":
    unittest.main()
