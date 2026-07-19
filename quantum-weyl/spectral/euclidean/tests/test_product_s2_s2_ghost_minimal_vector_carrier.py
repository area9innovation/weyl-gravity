from __future__ import annotations

from fractions import Fraction
import json
import unittest

from jsonschema import Draft202012Validator

from spectral.euclidean.product_s2_s2_ghost_minimal_vector_carrier import OUTPUT, SCHEMA, _vector_mode, build
from spectral.euclidean.verify_product_s2_s2_ghost_minimal_vector_carrier import main as independent_verify


def _q(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


class ProductS2S2GhostMinimalVectorCarrierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_schema_and_checked_in_certificate(self) -> None:
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.value)
        self.assertEqual(self.value, json.loads(OUTPUT.read_text()))

    def test_exceptional_exact_and_coexact_policies_differ(self) -> None:
        row = _vector_mode(1, 0)
        self.assertEqual(row["degeneracy"], 3)
        self.assertEqual(
            {entry["status"] for entry in row["polarizations"]},
            {"MATCHED_WITH_SCHUR_POLE", "KILLING_ZERO_PRIMED_OUT"},
        )
        self.assertEqual(_q(row["paired_exact_vector_times_schur_ratio"]), Fraction(1, 3))

    def test_regular_mode_has_two_polarizations_per_active_factor(self) -> None:
        row = _vector_mode(1, 1)
        self.assertEqual(len(row["polarizations"]), 4)
        self.assertEqual(_q(row["regular_minimal_vector_ratio"]), Fraction(4, 81))

    def test_local_zeta_weighted_defect(self) -> None:
        defect = self.value["zeta_weighted_local_defect"]
        self.assertEqual(_q(defect["two_polarization_total_defect"]), -10)
        self.assertFalse(self.value["claim_flags"]["MINIMAL_VECTOR_INFINITE_WEIGHTED_DETERMINANT_COMPUTED"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(independent_verify(), 0)


if __name__ == "__main__":
    unittest.main()
