from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from spectral.euclidean.generic_background_ghost_n3_barycentric_factorization import (
    OUTPUT,
    SCHEMA,
    build,
    validate,
)
from spectral.euclidean.verify_generic_background_ghost_n3_barycentric_factorization import (
    verify,
)


class GenericGhostN3BarycentricFactorizationTests(unittest.TestCase):
    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_independent_verifier(self) -> None:
        verify()

    def test_exact_factorization_summary(self) -> None:
        value = build()
        summary = value["factorization_summary"]
        self.assertEqual(summary["channels_with_exact_Delta_factor"], 10)
        self.assertEqual(
            summary["channels_with_nonzero_direct_open_edge_restriction"],
            ["I10_123"],
        )
        self.assertEqual(summary["minimum_vertex_integrability_margin"], 1)
        self.assertFalse(
            value["claim_flags"]["GENERIC_RELATIVE_IBP_REDUCTION_COMPUTED"]
        )

    def test_schema_and_semantic_mutations_are_rejected(self) -> None:
        value = build()
        mutant = deepcopy(value)
        mutant["claim_flags"]["GENERIC_EDGE_BUBBLE_COEFFICIENTS_COMPUTED"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutant)
        mutant = deepcopy(value)
        mutant["factorization_summary"]["minimum_vertex_integrability_margin"] = 0
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutant)

    def test_formula_mutation_is_rejected(self) -> None:
        value = build()
        mutant = deepcopy(value)
        mutant["channel_rows"][0]["reduced_numerator_terms"][0]["coefficient"][
            "numerator"
        ] += 1
        with self.assertRaises(ValueError):
            validate(mutant)


if __name__ == "__main__":
    unittest.main()
