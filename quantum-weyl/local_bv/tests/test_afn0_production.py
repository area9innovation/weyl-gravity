import json
import unittest

from local_bv.afn0_production import afn0_production_results
from local_bv.afn0_production_certificate import (
    CERTIFICATE_PATH,
    RESULT_DIR,
    SCHEMA_PATH,
    build_certificate,
)
from local_bv.schema_validation import validate_instance


class AfnZeroProductionTests(unittest.TestCase):
    def test_sprint_one_slices_run_without_promotion(self) -> None:
        results = afn0_production_results()
        h04 = results["H04_AFN0_RESULT"]
        h14 = results["H14_AFN0_RESULT"]
        self.assertEqual(
            [slice_["slice_id"] for slice_ in h04["slices"]],
            ["H04_AFN0_EVEN", "H04_AFN0_ODD"],
        )
        self.assertEqual(
            [slice_["slice_id"] for slice_ in h14["slices"]],
            ["H14_AFN0_EVEN_WITHOUT_EULER", "H14_AFN0_ODD"],
        )
        self.assertTrue(
            all(
                slice_["relative_cohomology_status"] == "UNDECIDED"
                for result in results.values()
                for slice_ in result["slices"]
            )
        )

    def test_known_exact_classes_keep_explicit_witnesses(self) -> None:
        candidates = {
            candidate["representative_id"]: candidate
            for result in afn0_production_results().values()
            for slice_ in result["slices"]
            for candidate in slice_["candidates"]
        }
        for class_id in ("CT_BOX_R", "ANOM_OMEGA_BOX_R"):
            self.assertEqual(candidates[class_id]["relative_cohomology_status"], "EXACT")
            self.assertIsNotNone(candidates[class_id]["exactness_witness"])
        self.assertTrue(
            all(candidate["nontriviality_witness"] is None for candidate in candidates.values())
        )

    def test_schema_and_checked_in_receipts(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text())
        for result_id, result in afn0_production_results().items():
            self.assertFalse(validate_instance(result, schema))
            checked = json.loads((RESULT_DIR / f"{result_id}.json").read_text())
            self.assertEqual(checked, result)
        self.assertEqual(json.loads(CERTIFICATE_PATH.read_text()), build_certificate())


if __name__ == "__main__":
    unittest.main()
