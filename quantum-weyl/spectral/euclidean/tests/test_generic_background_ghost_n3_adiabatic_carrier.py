from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import json
import unittest

from jsonschema import Draft202012Validator

from spectral.euclidean.generic_background_ghost_n3_adiabatic_carrier import (
    OUTPUT,
    SCHEMA,
    build,
    validate,
)
from spectral.euclidean.verify_generic_background_ghost_n3_adiabatic_carrier import verify


class GenericGhostN3AdiabaticCarrierTests(unittest.TestCase):
    def test_exact_coefficients(self) -> None:
        value = build()
        self.assertEqual(
            value["angular_average"]["coefficients"]["tr_R3"],
            {"numerator": 503, "denominator": 648},
        )
        self.assertEqual(
            value["three_insertion_log_term"]["coefficients"]["tr_R3"],
            {"numerator": -503, "denominator": 243},
        )

    def test_scalar_flat_specialization_keeps_only_cubic_trace(self) -> None:
        value = build()
        self.assertEqual(value["angular_average"]["scalar_flat_specialization"], "(503/648) tr(R^3)")
        self.assertEqual(value["three_insertion_log_term"]["scalar_flat_specialization"], "J3*(-503/243) tr(R^3)")

    def test_polarized_carrier_has_S3_stabilizer(self) -> None:
        value = build()["polarized_S3_carrier"]
        self.assertEqual(value["stabilizer"], "S3")
        self.assertEqual(
            value["Tr_log_coefficients"]["sym_tr_R1_R2_R3"],
            {"numerator": -503, "denominator": 243},
        )

    def test_fail_closed_momentum_and_crosswalk_status(self) -> None:
        value = build()
        self.assertEqual(value["radial_and_momentum_status"]["full_nonzero_external_momentum_triangle"], "NOT_COMPUTED")
        self.assertEqual(value["carrier_crosswalk"]["repository_I10_normalization_map"], "NO_CERTIFIED_MAP")
        self.assertFalse(value["claim_flags"]["GENERIC_GHOST_N3_FULL_MOMENTUM_KERNEL_COMPUTED"])

    def test_schema_is_strict(self) -> None:
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(build())
        mutant = deepcopy(build())
        mutant["unexpected"] = True
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(mutant)))

    def test_semantic_mutation_is_rejected(self) -> None:
        mutant = deepcopy(build())
        mutant["claim_flags"]["GENERIC_GHOST_N3_FULL_MOMENTUM_KERNEL_COMPUTED"] = True
        with self.assertRaises(ValueError):
            validate(mutant)
        mutant = deepcopy(build())
        mutant["angular_average"]["coefficients"]["tr_R3"] = {
            "numerator": 504,
            "denominator": 648,
        }
        with self.assertRaises(ValueError):
            validate(mutant)

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_independent_wick_replay(self) -> None:
        self.assertEqual(verify(), build())


if __name__ == "__main__":
    unittest.main()
