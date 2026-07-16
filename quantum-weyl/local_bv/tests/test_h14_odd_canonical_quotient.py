import json
import unittest

from local_bv.h14_odd_canonical_quotient import (
    canonical_quotient_payload,
    h14_odd_canonical_quotient_analysis,
)
from local_bv.h14_odd_canonical_quotient_certificate import (
    OUTPUT_PATH,
    SCHEMA_PATH,
    build_certificate,
)
from local_bv.schema_validation import validate_instance


class H14OddCanonicalQuotientTests(unittest.TestCase):
    def test_all_mixed_orbits_have_explicit_bianchi_witnesses(self) -> None:
        analysis = h14_odd_canonical_quotient_analysis()
        self.assertEqual(len(analysis["mixed_sectors"]), 3)
        for sector in analysis["mixed_sectors"]:
            self.assertEqual(
                (sector["raw_graph_count"], sector["signed_symmetry_orbit_count"], sector["bianchi_relation_rank"], sector["canonical_quotient_dimension"]),
                (15, 3, 3, 0),
            )
            self.assertTrue(all(row["verification"] == "ZERO_BY_ALGEBRAIC_BIANCHI" for row in sector["orbit_witnesses"]))

    def test_target_native_odd_quotient_and_relative_matrices(self) -> None:
        analysis = h14_odd_canonical_quotient_analysis()
        self.assertEqual(analysis["target_native_odd_quotient"]["quotient_dimension"], 1)
        self.assertEqual(analysis["boundary_rank"], 0)
        self.assertEqual(analysis["closure_rank"], 1)
        self.assertEqual(analysis["quotient_dimension"], 1)
        self.assertFalse(analysis["q_matrix"].entries)
        self.assertFalse(analysis["dh_matrix"].entries)

    def test_complete_normalized_witness(self) -> None:
        payload = canonical_quotient_payload()
        self.assertEqual(payload["top_basis"], ["ANOM_OMEGA_C_DUAL_C"])
        self.assertEqual(payload["classes"][0]["dual_witness_type"], "COMPLETE_NONTRIVIALITY_WITNESS")
        self.assertEqual(payload["classes"][0]["dual_pairing"], {"numerator": 1, "denominator": 1})
        proof = h14_odd_canonical_quotient_analysis()["basis_exhaustiveness_proof"]
        proof.verify(expected_basis_manifest_hash=proof.basis_manifest_hash)

    def test_schema_and_checked_in_certificate_reproduce(self) -> None:
        certificate = build_certificate()
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertFalse(validate_instance(certificate, schema))
        self.assertEqual(json.loads(OUTPUT_PATH.read_text(encoding="utf-8")), certificate)


if __name__ == "__main__":
    unittest.main()
