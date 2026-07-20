import json
import unittest
from copy import deepcopy

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_active_local_rotation_leaf_descent import OUTPUT, build
from jsonschema import Draft202012Validator, ValidationError


class ActiveLocalRotationLeafDescentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(OUTPUT.read_text())

    def test_certificate_rebuilds_exactly(self) -> None:
        self.assertEqual(self.payload, build())

    def test_all_three_active_candidates_are_covered(self) -> None:
        application = self.payload["candidate_application"]
        self.assertEqual(application["candidates"], [17, 18, 20])
        self.assertTrue(application["all_constant_corank_smooth_strata_covered"])
        self.assertTrue(application["parity_channels_remain_coupled"])
        self.assertTrue(application["candidate18_positive_spectators_remain_present"])

    def test_moment_map_is_basic_and_zero_fibre_commutes(self) -> None:
        theorem = self.payload["presymplectic_descent_theorem"]
        self.assertIn("Omega_U(xi_sharp,r)=0", theorem["radical_annihilation"])
        self.assertIn("mu_bar^{-1}(0)", theorem["zero_fibre_commutation"])
        flags = self.payload["classification"]
        self.assertTrue(flags["moment_map_basic_on_current_radical"])
        self.assertTrue(flags["local_zero_fibre_and_radical_reductions_commute"])

    def test_global_and_singular_claims_remain_fail_closed(self) -> None:
        flags = self.payload["classification"]
        self.assertFalse(flags["node_phases_identified_with_rotations"])
        self.assertFalse(flags["global_rotation_zero_fibre_connected"])
        self.assertFalse(flags["global_leaf_space_or_Hausdorff_quotient_classified"])
        self.assertFalse(flags["singular_locus_reduction_classified"])
        self.assertFalse(flags["occupation_strata_glued"])
        self.assertFalse(flags["causal_residual_observational_or_quantum_claim"])

    def test_schema_rejects_global_connectedness_promotion(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["classification"]["global_rotation_zero_fibre_connected"] = True
        schema = json.loads(
            (
                OUTPUT.parents[1]
                / "einstein_sector/schema/einstein_maxwell_weyl_same_sign_active_local_rotation_leaf_descent.schema.json"
            ).read_text()
        )
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutated)


if __name__ == "__main__":
    unittest.main()
