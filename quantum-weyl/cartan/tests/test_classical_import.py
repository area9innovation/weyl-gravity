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

    def test_wrong_result_id_is_rejected(self) -> None:
        mutated = current_record()
        mutated["result_id"] = "WRONG"
        with self.assertRaisesRegex(ValueError, "result_id"):
            validate_classical_d_status(mutated)

    def test_duplicate_or_missing_setting_is_rejected(self) -> None:
        mutated = current_record()
        settings = copy.deepcopy(mutated["settings"])
        settings[-1] = copy.deepcopy(settings[0])
        mutated["settings"] = settings
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_classical_d_status(mutated)

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
