from __future__ import annotations

import copy
import json
import unittest

from cartan.classical_import import (
    DEFAULT_STATUS_PATH,
    EXPECTED_SETTINGS,
    import_receipt,
    imported_setting_ledger,
    validate_classical_d_status,
)


def current_record() -> dict[str, object]:
    return json.loads(DEFAULT_STATUS_PATH.read_text(encoding="utf-8"))


class ClassicalDImportTests(unittest.TestCase):
    def test_current_certificate_and_sector_split_are_accepted(self) -> None:
        record = validate_classical_d_status(current_record())
        ledger = imported_setting_ledger(record)
        self.assertEqual(tuple(item["setting_id"] for item in ledger), EXPECTED_SETTINGS)
        self.assertEqual(
            ledger[0]["D_charge"],
            "SECTOR_DEPENDENT_CLASSICALLY_P_LIN_CHARGED_P_TAUB0_GAUGE",
        )
        self.assertEqual(
            import_receipt()["required_sector_verdicts"],
            {"P_lin": "D_CHARGED", "P_Taub0": "D_GAUGE"},
        )
        self.assertEqual(
            import_receipt()["additional_setting_ids"],
            ["cylinder_neutral_clock_pair", "positive_berger_clock"],
        )
        self.assertEqual(
            import_receipt()["semantic_validation"],
            "REQUIRED_SETTINGS_VERIFIED_ADDITIONAL_SETTINGS_ENUMERATED_NOT_CONSUMED",
        )

    def test_wrong_result_id_is_rejected(self) -> None:
        mutated = current_record()
        mutated["result_id"] = "WRONG"
        with self.assertRaisesRegex(ValueError, "result_id"):
            validate_classical_d_status(mutated)

    def test_duplicate_setting_is_rejected(self) -> None:
        mutated = current_record()
        settings = copy.deepcopy(mutated["settings"])
        settings[-1] = copy.deepcopy(settings[0])
        mutated["settings"] = settings
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_classical_d_status(mutated)

    def test_missing_required_setting_is_rejected_but_additive_setting_is_allowed(self) -> None:
        mutated = current_record()
        mutated["settings"] = [
            setting
            for setting in mutated["settings"]
            if setting["setting_id"] != "asymptotically_flat"
        ]
        with self.assertRaisesRegex(ValueError, "missing a required"):
            validate_classical_d_status(mutated)

        mutated = current_record()
        extra = copy.deepcopy(mutated["settings"][-1])
        extra["setting_id"] = "future_separately_gated_setting"
        mutated["settings"].append(extra)
        validated = validate_classical_d_status(mutated)
        self.assertEqual(validated["settings"][-1]["setting_id"], extra["setting_id"])

    def test_vacuum_verdict_mutation_is_rejected(self) -> None:
        mutated = current_record()
        mutated["settings"][0]["verdict"] = "D_GAUGE"
        with self.assertRaisesRegex(ValueError, "sector-dependent"):
            validate_classical_d_status(mutated)

    def test_sector_reversal_is_rejected(self) -> None:
        mutated = current_record()
        sectors = mutated["settings"][0]["sector_results"]
        by_id = {sector["sector_id"]: sector for sector in sectors}
        by_id["P_lin"]["verdict"] = "D_GAUGE"
        with self.assertRaisesRegex(ValueError, "P_lin"):
            validate_classical_d_status(mutated)


if __name__ == "__main__":
    unittest.main()
