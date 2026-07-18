from __future__ import annotations

from copy import deepcopy
import unittest

from transfer.third_curvature_weyl_manifest import build, validate
from transfer.verify_third_curvature_weyl_manifest import verify


class ThirdCurvatureWeylManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_five_carriers_and_stabilizers(self) -> None:
        rows = self.value["carrier_manifest"]
        self.assertEqual([row["carrier_id"] for row in rows], ["I10", "I24", "I25", "I28", "I29"])
        self.assertEqual(
            [row["source_generic_stabilizer"] for row in rows],
            ["S3", "S2_23", "S2_23", "S2_12", "C3"],
        )
        self.assertEqual([row["stabilizer"] for row in rows], ["S3", "S2_23", "S2_23", "S2_12", "S3"])

    def test_effective_label_modules_reduce_eleven_to_ten(self) -> None:
        self.assertEqual(self.value["raw_module"]["generic_label_orbit_dimension"], 11)
        self.assertEqual(self.value["quotient_module"]["generic_label_orbit_dimension"], 10)

    def test_irreducible_multiplicities(self) -> None:
        self.assertEqual(
            self.value["raw_module"]["irreducible_multiplicities"],
            {"trivial": 5, "sign": 0, "standard": 3},
        )
        self.assertEqual(
            self.value["quotient_module"]["irreducible_multiplicities"],
            {"trivial": 4, "sign": 0, "standard": 3},
        )

    def test_scalar_flat_i29_symmetry_enhancement(self) -> None:
        row = self.value["scalar_flat_symmetry_enhancement"]
        self.assertEqual(row["source_generic_stabilizer"], "C3")
        self.assertEqual(row["effective_scalar_flat_K_stabilizer"], "S3")
        self.assertTrue(
            self.value["claim_flags"]["SCALAR_FLAT_I29_REVERSAL_IDENTITY_REPLAYED"]
        )

    def test_four_dimensional_relation_has_one_symmetric_direction(self) -> None:
        relation = self.value["four_dimensional_identity"]
        self.assertEqual(relation["relation_rank"], 1)
        self.assertEqual(relation["elimination_choice"], "REMOVE_TRIVIAL_S3_COMPONENT_OF_I28")
        self.assertEqual(relation["absent_carrier"], "I29")

    def test_i29_is_only_an_algebraic_lineage_anchor(self) -> None:
        anchor = self.value["algebraic_anchor"]
        self.assertEqual(anchor["carrier_id"], "I29")
        self.assertEqual(anchor["normalization_to_C3_EVEN"], "NOT_COMPUTED")

    def test_coefficient_and_quantum_promotions_fail_closed(self) -> None:
        for flag in (
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED",
            "REPOSITORY_CUBIC_COEFFICIENTS_COMPUTED",
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
            "RESIDUAL_TRANSFER_AUTHORIZED",
        ):
            mutation = deepcopy(self.value)
            mutation["claim_flags"][flag] = True
            with self.assertRaises(Exception):
                validate(mutation)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.value)


if __name__ == "__main__":
    unittest.main()
