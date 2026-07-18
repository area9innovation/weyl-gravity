from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import ValidationError

from spectral.euclidean.generic_background_ghost_endo_duhamel_reduction import (
    OUTPUT,
    build,
    validate,
)
from spectral.euclidean.verify_generic_background_ghost_endo_duhamel_reduction import (
    verify,
)


class GenericGhostEndoDuhamelReductionTests(unittest.TestCase):
    def test_exact_operator_split(self) -> None:
        value = build()
        self.assertEqual(value["exact_Endo_split"]["alpha"], {"numerator": -1, "denominator": 2})
        self.assertEqual(
            value["exact_Endo_split"]["W_coefficients"],
            [
                {"numerator": 0, "denominator": 1},
                {"numerator": -2, "denominator": 1},
                {"numerator": 0, "denominator": 1},
            ],
        )

    def test_endo_heat_kernel_and_determinant(self) -> None:
        value = build()
        self.assertEqual(
            value["exact_Endo_heat_kernel"]["proper_time_upper_multiplier"],
            {"numerator": 3, "denominator": 2},
        )
        self.assertIn("zeta_Delta0(0) log(3/2)", value["nonzero_mode_determinant_identity"]["zeta_scaled_formula"])

    def test_cubic_work_table_is_finite(self) -> None:
        rows = build()["Duhamel_expansion"]["cubic_work_table"]
        self.assertEqual([row["Ricci_insertion_count"] for row in rows], [0, 1, 2, 3])
        self.assertEqual(
            [row["maximum_background_order_from_Endo_kernels"] for row in rows],
            [3, 2, 1, 0],
        )

    def test_source_is_version_and_hash_pinned(self) -> None:
        source = build()["source_provenance"]
        self.assertEqual(source["arxiv"], "2508.06439v2")
        self.assertRegex(source["source_archive_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(source["source_tex_sha256"], r"^[0-9a-f]{64}$")

    def test_claim_mutation_is_rejected(self) -> None:
        mutant = deepcopy(build())
        mutant["claim_flags"]["GENERIC_NONMINIMAL_GHOST_CPT_DETERMINANT_COMPUTED"] = True
        with self.assertRaises((ValidationError, ValueError)):
            validate(mutant)

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), build())


if __name__ == "__main__":
    unittest.main()
