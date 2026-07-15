import json
import unittest

from local_bv.afn0_production import afn0_production_results, afn0_slice_results
from local_bv.afn0_production_certificate import (
    CERTIFICATE_PATH,
    RESULT_DIR,
    SLICE_RESULT_DIR,
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
                slice_["truncated_quotient_result"]["relative_cohomology_status"]
                == "UNDECIDED"
                for result in results.values()
                for slice_ in result["slices"]
            )
        )
        expected = {
            "H04_AFN0_EVEN_CLOSURE",
            "H04_AFN0_ODD_CLOSURE",
            "H14_AFN0_EVEN_NO_EULER_CLOSURE",
            "H14_AFN0_ODD_CLOSURE",
        }
        self.assertEqual(
            {
                slice_["closure_result"]["result_id"]
                for result in results.values()
                for slice_ in result["slices"]
            },
            expected,
        )

    def test_known_exact_classes_keep_explicit_witnesses(self) -> None:
        candidates = {
            candidate["representative_id"]: candidate
            for result in afn0_production_results().values()
            for slice_ in result["slices"]
            for candidate in slice_["truncated_quotient_result"]["candidates"]
        }
        for class_id in ("CT_BOX_R", "ANOM_OMEGA_BOX_R"):
            self.assertEqual(candidates[class_id]["relative_cohomology_status"], "EXACT")
            self.assertIsNotNone(candidates[class_id]["exactness_witness"])
        self.assertTrue(
            all(candidate["nonmembership_witness"] is None for candidate in candidates.values())
        )
        self.assertEqual(
            candidates["CT_C2"]["permitted_nonmembership_witness_type"],
            "TRUNCATED_NONMEMBERSHIP_WITNESS",
        )

    def test_schema_and_checked_in_receipts(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text())
        for result_id, result in afn0_production_results().items():
            self.assertFalse(validate_instance(result, schema))
            checked = json.loads((RESULT_DIR / f"{result_id}.json").read_text())
            self.assertEqual(checked, result)
        self.assertEqual(json.loads(CERTIFICATE_PATH.read_text()), build_certificate())

    def test_eight_standalone_slice_receipts(self) -> None:
        slices = afn0_slice_results()
        self.assertEqual(len(slices), 8)
        closure_schema = json.loads(
            (SCHEMA_PATH.parent / "afn0_closure_result.schema.json").read_text()
        )
        quotient_schema = json.loads(
            (
                SCHEMA_PATH.parent
                / "afn0_truncated_quotient_result.schema.json"
            ).read_text()
        )
        for result_id, result in slices.items():
            schema = (
                closure_schema
                if result["result_state"] == "CLOSURE_RESULT"
                else quotient_schema
            )
            self.assertFalse(validate_instance(result, schema))
            checked = json.loads(
                (SLICE_RESULT_DIR / f"{result_id}.json").read_text()
            )
            self.assertEqual(checked, result)


if __name__ == "__main__":
    unittest.main()
