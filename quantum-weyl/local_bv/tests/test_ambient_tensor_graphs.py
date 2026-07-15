import json
import unittest

from local_bv.algebra import canonical_sha256
from local_bv.ambient_tensor_graph_certificate import (
    BUNDLE_DIRECTORY,
    BUNDLE_SCHEMA_PATH,
    OUTPUT_PATH,
    SCHEMA_PATH,
    build_artifacts,
)
from local_bv.ambient_tensor_graphs import (
    EXPLICIT_GRAPH_THRESHOLD,
    ambient_tensor_graph_analysis,
    factor_profiles,
    nondecreasing_distributions,
    raw_graph_count,
)
from local_bv.lower_form_ambient import ambient_lower_form_signature_analysis
from local_bv.schema_validation import validate_instance


class AmbientTensorGraphTests(unittest.TestCase):
    def test_unlabeled_derivative_distributions_are_exhaustive(self) -> None:
        self.assertEqual(
            nondecreasing_distributions(4, 2),
            ((0, 4), (1, 3), (2, 2)),
        )
        self.assertEqual(nondecreasing_distributions(0, 0), ((),))
        self.assertEqual(nondecreasing_distributions(1, 0), ())
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            nondecreasing_distributions(-1, 2)

    def test_raw_graph_formula_matches_small_explicit_counts(self) -> None:
        self.assertEqual(raw_graph_count(8, 0), 105)
        self.assertEqual(raw_graph_count(8, 1), 210)
        self.assertEqual(raw_graph_count(18, 0), 34_459_425)
        self.assertEqual(raw_graph_count(18, 1), 413_513_100)
        self.assertEqual(raw_graph_count(3, 0), 0)

    def test_all_refined_signatures_have_slot_exact_profiles(self) -> None:
        refined = [
            signature
            for manifest in ambient_lower_form_signature_analysis()["manifests"]
            for signature in manifest["signatures"]
            if signature["refinement_status"] == "REFINED_ADMISSIBLE"
        ]
        self.assertEqual(len(refined), 720)
        profile_count = 0
        for signature in refined:
            profiles = factor_profiles(signature)
            self.assertTrue(profiles)
            profile_count += len(profiles)
            for profile in profiles:
                self.assertEqual(
                    profile["slot_count"], signature["total_index_slots_with_dx"]
                )
                self.assertLessEqual(
                    profile["weyl_ghost_derivative_orders"].count(0), 1
                )
                payload = {
                    key: value
                    for key, value in profile.items()
                    if key != "profile_sha256"
                }
                self.assertEqual(profile["profile_sha256"], canonical_sha256(payload))
        self.assertEqual(profile_count, 1224)

    def test_factored_realization_counts_are_frozen(self) -> None:
        analysis, bundle = ambient_tensor_graph_analysis()
        self.assertEqual(
            analysis["totals"],
            {
                "coarse_signature_count": 2480,
                "rejected_signature_count": 1760,
                "refined_signature_count": 720,
                "factor_profile_count": 1224,
                "total_raw_graph_count": 2_860_932_903,
                "factored_count_only_signature_count": 167,
            },
        )
        self.assertEqual(bundle["realization_count"], 720)
        self.assertEqual(
            sum(row["total_raw_graph_count"] for row in bundle["realizations"]),
            2_860_932_903,
        )
        largest = max(
            bundle["realizations"], key=lambda row: row["total_raw_graph_count"]
        )
        self.assertGreater(largest["total_raw_graph_count"], EXPLICIT_GRAPH_THRESHOLD)
        self.assertEqual(largest["graph_storage_mode"], "FACTORED_COUNT_ONLY")

    def test_schema_and_checked_in_artifacts(self) -> None:
        certificate, bundle = build_artifacts()
        self.assertFalse(
            validate_instance(certificate, json.loads(SCHEMA_PATH.read_text()))
        )
        self.assertFalse(
            validate_instance(bundle, json.loads(BUNDLE_SCHEMA_PATH.read_text()))
        )
        bundle_path = BUNDLE_DIRECTORY / f"{bundle['bundle_sha256']}.json"
        self.assertEqual(json.loads(OUTPUT_PATH.read_text()), certificate)
        self.assertEqual(json.loads(bundle_path.read_text()), bundle)


if __name__ == "__main__":
    unittest.main()
