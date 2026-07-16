import json
import unittest

from local_bv.h04_canonical_quotient import (
    canonical_quotient_payload,
    h04_canonical_quotient_analysis,
)
from local_bv.h04_canonical_quotient_certificate import (
    OUTPUT_PATH,
    SCHEMA_PATH,
    build_certificate,
)
from local_bv.schema_validation import validate_instance


class H04CanonicalQuotientTests(unittest.TestCase):
    def test_even_derivative_orbits_reduce_to_exact_box_r(self) -> None:
        sector = h04_canonical_quotient_analysis()["even"]["derivative_sector"]
        self.assertEqual(
            (
                sector["raw_pairing_count"],
                sector["canonical_orbit_count"],
                sector["relation_rank"],
                sector["quotient_dimension_before_d_h"],
                sector["graphwise_divergence_count"],
                sector["quotient_dimension_mod_d_h"],
            ),
            (15, 2, 1, 1, 15, 0),
        )

    def test_exact_even_relative_matrices(self) -> None:
        even = h04_canonical_quotient_analysis()["even"]
        self.assertEqual((even["boundary_rank"], even["closure_rank"], even["quotient_dimension"]), (1, 3, 2))
        self.assertFalse(even["q_matrix"].entries)
        self.assertFalse(
            even["closure_obstruction_matrix"].compose(even["boundary_matrix"]).entries
        )

    def test_odd_derivative_signature_is_a_divergence(self) -> None:
        odd = h04_canonical_quotient_analysis()["odd"]
        divergence = odd["derivative_graph"]["divergence_witness"]
        self.assertEqual(divergence["status"], "VERIFIED_EVERY_RAW_GRAPH")
        self.assertEqual(divergence["graphwise_current_count"], 15)
        self.assertEqual(odd["quadratic_target"]["quotient_dimension"], 1)

    def test_classes_have_complete_normalized_dual_witnesses(self) -> None:
        payload = canonical_quotient_payload()
        classes = payload["even_sector"]["classes"] + payload["odd_sector"]["classes"]
        self.assertEqual([row["representative_id"] for row in classes], ["CT_C2", "CT_E4", "CT_C_DUAL_C"])
        self.assertTrue(all(row["dual_witness_type"] == "COMPLETE_NONTRIVIALITY_WITNESS" for row in classes))
        self.assertTrue(all(row["dual_pairing"] == {"numerator": 1, "denominator": 1} for row in classes))
        proof = h04_canonical_quotient_analysis()["basis_exhaustiveness_proof"]
        proof.verify(expected_basis_manifest_hash=proof.basis_manifest_hash)

    def test_schema_and_checked_in_certificate_reproduce(self) -> None:
        certificate = build_certificate()
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertFalse(validate_instance(certificate, schema))
        self.assertEqual(json.loads(OUTPUT_PATH.read_text(encoding="utf-8")), certificate)


if __name__ == "__main__":
    unittest.main()
