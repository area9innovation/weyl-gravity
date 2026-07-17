import json
import unittest

from local_bv.algebra import canonical_sha256
from local_bv.ambient_intrinsic_orbit_certificate import (
    BUNDLE_DIRECTORY,
    BUNDLE_SCHEMA_PATH,
    OUTPUT_PATH,
    SCHEMA_PATH,
    build_artifacts,
)
from local_bv.ambient_intrinsic_orbits import (
    SignedDisjointSet,
    ambient_intrinsic_orbit_analysis,
    profile_intrinsic_orbit_reduction,
    symmetry_generators,
)
from local_bv.ambient_factor_orbits import ambient_factor_orbit_analysis
from local_bv.schema_validation import validate_instance


def _profile(factors: list[dict[str, object]], epsilon_slots: int = 0) -> dict[str, object]:
    payload = {"factors": factors, "epsilon_slot_count": epsilon_slots}
    return {**payload, "profile_sha256": canonical_sha256(payload)}


def _signature(slot_count: int, epsilon_count: int = 0) -> dict[str, object]:
    payload = {
        "total_index_slots_with_dx": slot_count,
        "epsilon_count": epsilon_count,
    }
    return {**payload, "signature_sha256": canonical_sha256(payload)}


class AmbientIntrinsicOrbitTests(unittest.TestCase):
    def test_signed_disjoint_set_detects_an_odd_stabilizer(self) -> None:
        disjoint = SignedDisjointSet(2)
        disjoint.relate(0, 1, 1)
        disjoint.relate(0, 1, -1)
        components, zero_roots = disjoint.components()
        self.assertEqual(len(components), 1)
        self.assertEqual(set(components), zero_roots)

    def test_horizontal_two_form_metric_trace_is_zero(self) -> None:
        profile = _profile(
            [
                {
                    "factor_id": "dx",
                    "factor_type": "HORIZONTAL_FORM_CARRIER",
                    "derivative_order": 0,
                    "Grassmann_parity": 0,
                    "slot_variances": ["UPPER", "UPPER"],
                }
            ]
        )
        generators = symmetry_generators(profile)
        self.assertEqual(
            [row["generator_type"] for row in generators],
            ["HORIZONTAL_FORM_ADJACENT_TRANSPOSITION"],
        )
        reduction = profile_intrinsic_orbit_reduction(_signature(2), profile)
        self.assertEqual(reduction["raw_graph_count"], 1)
        self.assertEqual(reduction["surviving_orbit_count"], 0)
        self.assertEqual(reduction["odd_stabilizer_zero_orbit_count"], 1)

    def test_degree_three_four_intrinsic_counts_are_frozen(self) -> None:
        analysis, bundle = ambient_intrinsic_orbit_analysis()
        self.assertEqual(
            analysis["totals"],
            {
                "refined_signature_count": 144,
                "factor_profile_count": 192,
                "raw_graph_count": 388_011,
                "generator_edge_count": 3_277_285,
                "signed_orbit_count": 9_534,
                "surviving_orbit_count": 5_637,
                "odd_stabilizer_zero_orbit_count": 3_897,
            },
        )
        self.assertEqual(bundle["profile_reduction_count"], 192)
        for row in bundle["profile_reductions"]:
            self.assertEqual(
                sum(
                    item["orbit_size"] * item["orbit_count"]
                    for item in row["orbit_size_histogram"]
                ),
                row["raw_graph_count"],
            )
            self.assertEqual(
                row["signed_orbit_count"],
                row["surviving_orbit_count"]
                + row["odd_stabilizer_zero_orbit_count"],
            )

    def test_intrinsic_quotient_is_profilewise_monotone_from_factor_orbits(self) -> None:
        _, factor_bundle = ambient_factor_orbit_analysis()
        _, intrinsic_bundle = ambient_intrinsic_orbit_analysis()
        factor_rows = factor_bundle["profile_reductions"]
        intrinsic_rows = intrinsic_bundle["profile_reductions"]
        self.assertEqual(len(factor_rows), len(intrinsic_rows))
        for factor, intrinsic in zip(factor_rows, intrinsic_rows):
            self.assertEqual(factor["profile_sha256"], intrinsic["profile_sha256"])
            self.assertEqual(factor["raw_graph_count"], intrinsic["raw_graph_count"])
            self.assertLessEqual(
                intrinsic["surviving_orbit_count"],
                factor["surviving_orbit_count"],
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
