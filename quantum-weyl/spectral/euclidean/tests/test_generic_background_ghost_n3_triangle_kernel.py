from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator

from spectral.euclidean.generic_background_ghost_n3_triangle_kernel import OUTPUT, SCHEMA, build, validate
from spectral.euclidean.verify_generic_background_ghost_n3_triangle_kernel import verify


class GenericGhostN3TriangleKernelTests(unittest.TestCase):
    def test_eight_projector_sectors_and_twenty_wick_rows(self) -> None:
        expansion = build()["projector_sector_expansion"]
        self.assertEqual(expansion["sector_count"], 8)
        self.assertEqual(expansion["sector_multiplicities_by_projector_count"], [1, 3, 3, 1])
        self.assertEqual(expansion["total_Wick_rows"], 20)

    def test_three_projector_wick_coefficients(self) -> None:
        row = build()["projector_sector_expansion"]["sectors"][-1]
        self.assertEqual(row["subset_bits"], "111")
        self.assertEqual(
            [wick["coefficient_per_pairing"] for wick in row["wick_rows"]],
            [
                {"numerator": 6, "denominator": 1},
                {"numerator": 1, "denominator": 1},
                {"numerator": 1, "denominator": 4},
                {"numerator": 1, "denominator": 8},
            ],
        )

    def test_fail_closed_repository_projection(self) -> None:
        value = build()
        self.assertEqual(value["carrier_projection"]["repository_I10_projection"], "NOT_COMPUTED")
        self.assertFalse(value["claim_flags"]["GENERIC_GHOST_N3_REPOSITORY_I10_PROJECTION_COMPUTED"])

    def test_schema_is_strict(self) -> None:
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(build())
        mutant = deepcopy(build())
        mutant["extra"] = True
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(mutant)))

    def test_semantic_mutation_is_rejected(self) -> None:
        mutant = deepcopy(build())
        mutant["projector_sector_expansion"]["sectors"][0]["subset_bits"] = "111"
        with self.assertRaises(ValueError):
            validate(mutant)
        mutant = deepcopy(build())
        mutant["claim_flags"]["GENERIC_GHOST_N3_REPOSITORY_I10_PROJECTION_COMPUTED"] = True
        with self.assertRaises(ValueError):
            validate(mutant)
        mutant = deepcopy(build())
        mutant["projector_sector_expansion"]["sectors"][-1]["wick_rows"][2][
            "coefficient_per_pairing"
        ] = {"numerator": 1, "denominator": 3}
        with self.assertRaises(ValueError):
            validate(mutant)

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_independent_direct_integrand_replay(self) -> None:
        self.assertEqual(verify(), build())


if __name__ == "__main__":
    unittest.main()
