import json
import unittest

from local_bv.algebra import canonical_sha256
from local_bv.ambient_factor_orbit_certificate import (
    BUNDLE_DIRECTORY,
    BUNDLE_SCHEMA_PATH,
    OUTPUT_PATH,
    SCHEMA_PATH,
    build_artifacts,
)
from local_bv.ambient_factor_orbits import (
    ambient_factor_orbit_analysis,
    factor_permutation_actions,
    profile_orbit_reduction,
)
from local_bv.schema_validation import validate_instance


class AmbientFactorOrbitTests(unittest.TestCase):
    def test_two_identical_odd_vectors_are_killed_by_the_signed_swap(self) -> None:
        factors = [
            {
                "factor_id": f"xi{index}",
                "factor_type": "COVARIANT_DERIVATIVE_DIFF_GHOST",
                "derivative_order": 0,
                "Grassmann_parity": 1,
                "slot_variances": ["UPPER"],
            }
            for index in range(2)
        ]
        profile_payload = {
            "factors": factors,
            "epsilon_slot_count": 0,
        }
        profile = {
            **profile_payload,
            "profile_sha256": canonical_sha256(profile_payload),
        }
        signature_payload = {
            "total_index_slots_with_dx": 2,
            "epsilon_count": 0,
        }
        signature = {
            **signature_payload,
            "signature_sha256": canonical_sha256(signature_payload),
        }
        actions = factor_permutation_actions(profile)
        self.assertEqual(len(actions), 2)
        self.assertEqual(sorted(sign for _, sign in actions), [-1, 1])
        reduction = profile_orbit_reduction(signature, profile)
        self.assertEqual(reduction["raw_graph_count"], 1)
        self.assertEqual(reduction["signed_orbit_count"], 1)
        self.assertEqual(reduction["surviving_orbit_count"], 0)
        self.assertEqual(reduction["Grassmann_zero_orbit_count"], 1)

    def test_degree_three_four_orbit_counts_and_coverage_are_frozen(self) -> None:
        analysis, bundle = ambient_factor_orbit_analysis()
        self.assertEqual(
            analysis["totals"],
            {
                "refined_signature_count": 144,
                "factor_profile_count": 192,
                "raw_graph_count": 388_011,
                "signed_orbit_count": 139_889,
                "surviving_orbit_count": 130_937,
                "Grassmann_zero_orbit_count": 8_952,
            },
        )
        self.assertEqual(bundle["profile_reduction_count"], 192)
        self.assertEqual(
            sum(row["raw_graph_count"] for row in bundle["profile_reductions"]),
            388_011,
        )
        for row in bundle["profile_reductions"]:
            covered = sum(
                item["orbit_size"] * item["orbit_count"]
                for item in row["orbit_size_histogram"]
            )
            self.assertEqual(covered, row["raw_graph_count"])
            self.assertEqual(
                row["signed_orbit_count"],
                row["surviving_orbit_count"] + row["Grassmann_zero_orbit_count"],
            )

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
