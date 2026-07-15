import json
import unittest
from fractions import Fraction

from local_bv.h14_even_canonical_quotient import (
    TOP_BASIS,
    canonical_quotient_payload,
    h14_even_canonical_quotient_analysis,
)
from local_bv.h14_even_canonical_quotient_certificate import (
    OUTPUT_PATH,
    SCHEMA_PATH,
    build_certificate,
)
from local_bv.schema_validation import validate_instance


class H14EvenCanonicalQuotientTests(unittest.TestCase):
    def test_only_thirty_target_pairings_are_materialized(self) -> None:
        payload = canonical_quotient_payload()
        self.assertEqual(
            payload["enumeration_policy"],
            {
                "mode": "ORBIT_FIRST_TWO_PENDING_MIXED_SIGNATURES",
                "ambient_raw_graph_count": 2_860_932_903,
                "ambient_raw_graphs_materialized": 0,
                "target_raw_pairings_materialized": 30,
            },
        )

    def test_orbit_first_bianchi_quotients(self) -> None:
        analysis = h14_even_canonical_quotient_analysis()
        hessian = analysis["hessian_sector"]
        gradient = analysis["gradient_sector"]
        self.assertEqual(
            (hessian["raw_pairing_count"], hessian["canonical_orbit_count"], hessian["quotient_dimension"]),
            (15, 2, 2),
        )
        self.assertEqual(
            (gradient["raw_pairing_count"], gradient["canonical_orbit_count"], gradient["relation_rank"], gradient["quotient_dimension"]),
            (15, 2, 1, 1),
        )
        self.assertEqual(
            analysis["contracted_bianchi_coefficient"], Fraction(-1, 2)
        )
        self.assertEqual(
            hessian["four_dimensional_antisymmetrization_candidate_count"], 0
        )
        self.assertEqual(
            gradient["four_dimensional_antisymmetrization_candidate_count"], 0
        )

    def test_generated_ibp_and_relative_matrices(self) -> None:
        analysis = h14_even_canonical_quotient_analysis()
        self.assertEqual(
            analysis["ibp_coordinates"],
            (
                (0, 1, 0, 1),
                (0, 0, 1, Fraction(1, 2)),
                (1, 0, 0, 1),
            ),
        )
        self.assertEqual(analysis["q_matrix"].rank(), 1)
        self.assertEqual(analysis["dh_matrix"].rank(), 3)
        self.assertEqual(analysis["boundary_rank"], 4)
        self.assertEqual(analysis["closure_rank"], 6)
        self.assertEqual(analysis["quotient_dimension"], 2)
        self.assertFalse(
            analysis["closure_obstruction_matrix"]
            .compose(analysis["boundary_matrix"])
            .entries
        )

    def test_omega_r2_has_nonzero_reduced_consistency_defect(self) -> None:
        wz = h14_even_canonical_quotient_analysis()["wz_obstruction"]
        self.assertEqual(wz["quotient"].quotient_dimension, 1)
        self.assertEqual(wz["reduced_obstruction_coefficient"], -12)
        self.assertEqual(len(wz["divergence"].terms), 2)
        self.assertEqual(
            wz["grassmann_square_term"],
            "ZERO_BY_SIGNED_IDENTICAL_GRAD_OMEGA_FACTOR_EXCHANGE",
        )

    def test_complete_dual_witnesses_and_exact_class(self) -> None:
        payload = canonical_quotient_payload()
        self.assertEqual(payload["top_basis"], list(TOP_BASIS))
        self.assertEqual(
            [row["representative_id"] for row in payload["classes"]],
            ["ANOM_OMEGA_C2", "ANOM_OMEGA_E4"],
        )
        self.assertTrue(
            all(
                row["dual_witness_type"]
                == "COMPLETE_NONTRIVIALITY_WITNESS"
                and row["dual_pairing"] == {"numerator": 1, "denominator": 1}
                for row in payload["classes"]
            )
        )
        self.assertEqual(
            payload["exact_classes"],
            [
                {
                    "representative_id": "ANOM_OMEGA_BOX_R",
                    "relative_cohomology_status": "EXACT",
                    "primitive_id": "R_SQUARED",
                    "primitive_coefficient": {"numerator": -1, "denominator": 12},
                    "current_id": "CURRENT_R_GRAD_OMEGA_MINUS_OMEGA_GRAD_R",
                }
            ],
        )
        proof = h14_even_canonical_quotient_analysis()[
            "basis_exhaustiveness_proof"
        ]
        proof.verify(expected_basis_manifest_hash=proof.basis_manifest_hash)

    def test_schema_and_checked_in_certificate_reproduce(self) -> None:
        certificate = build_certificate()
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertFalse(validate_instance(certificate, schema))
        self.assertEqual(json.loads(OUTPUT_PATH.read_text(encoding="utf-8")), certificate)


if __name__ == "__main__":
    unittest.main()
