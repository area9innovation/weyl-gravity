import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_active_presymplectic_divisors import OUTPUT, build


class ActivePresymplecticDivisorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(OUTPUT.read_text())

    def test_certificate_rebuilds_exactly(self) -> None:
        self.assertEqual(self.payload, build())

    def test_conormal_theorem_controls_radical_and_quotient(self) -> None:
        theorem = self.payload["conormal_divisor_theorem"]
        self.assertEqual(theorem["radical_dimension"], "nullity(K)")
        self.assertEqual(theorem["degeneracy_divisor"], "det(K)=0")
        self.assertIn("induced nondegenerate", theorem["presymplectic_quotient"])

    def test_third_transvectant_witness_is_generic_corank_one(self) -> None:
        witness = self.payload["candidate17_20_third_transvectant"]["exact_smooth_witness"]
        self.assertEqual(witness["J_rank"], 3)
        self.assertEqual(witness["K_rank"], 2)
        self.assertEqual(witness["K_nullity"], 1)
        self.assertEqual(witness["restricted_tangent_nullity"], 1)

    def test_candidate18_aligned_divisor_has_two_corank_four_branches(self) -> None:
        aligned = self.payload["candidate18_rank_one"]["aligned_section"]
        self.assertEqual(
            aligned["det_C"],
            "(2*b*r - w_y)*(6*b*r - w_x)/(b**2*w_x*w_y)",
        )
        self.assertEqual(
            [row["full_conormal_nullity"] for row in aligned["divisor_branches"]],
            [4, 4],
        )

    def test_global_and_causal_claims_remain_fail_closed(self) -> None:
        flags = self.payload["classification"]
        self.assertFalse(flags["global_quotient_topology_classified"])
        self.assertFalse(flags["occupation_strata_glued"])
        self.assertFalse(flags["singular_locus_quotient_classified"])
        self.assertFalse(flags["causal_residual_observational_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
