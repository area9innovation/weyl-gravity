from __future__ import annotations

from fractions import Fraction
import json
import unittest

from jsonschema import Draft202012Validator

from spectral.euclidean.product_s2_s2_ghost_schur_spectral_carrier import (
    OUTPUT,
    SCHEMA,
    _mode,
    build,
)
from spectral.euclidean.verify_product_s2_s2_ghost_schur_spectral_carrier import (
    main as independent_verify,
)


def _q(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


class ProductS2S2GhostSchurSpectralCarrierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_schema_and_checked_in_certificate(self) -> None:
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.value)
        self.assertEqual(self.value, json.loads(OUTPUT.read_text()))

    def test_constant_and_matched_exceptional_modes(self) -> None:
        self.assertEqual(_mode(Fraction(1), Fraction(2), 0, 0)["status"], "ABSENT_CONSTANT_GRADIENT")
        for ell, emm in [(1, 0), (0, 1)]:
            row = _mode(Fraction(1), Fraction(2), ell, emm)
            self.assertEqual(row["status"], "MATCHED_VECTOR_ZERO_SCHUR_POLE")
            self.assertEqual(_q(row["minimal_vector_ratio"]), 0)
            self.assertEqual(_q(row["paired_vector_times_schur_ratio"]), Fraction(1, 3))

    def test_regular_anisotropic_modes(self) -> None:
        rows = {(row["ell"], row["m"]): row for row in self.value["anisotropic_exact_modes"]}
        self.assertEqual(_q(rows[(1, 1)]["schur_eigenvalue"]), Fraction(3, 2))
        self.assertEqual(_q(rows[(1, 1)]["paired_vector_times_schur_ratio"]), Fraction(1, 3))
        self.assertEqual(_q(rows[(2, 1)]["schur_eigenvalue"]), Fraction(41, 36))
        self.assertEqual(_q(rows[(2, 1)]["paired_vector_times_schur_ratio"]), Fraction(41, 75))

    def test_finite_cutoff_and_residue(self) -> None:
        fixture = self.value["finite_cutoff_fixture"]
        self.assertEqual(fixture["exceptional_matched_dimension"], 6)
        self.assertNotEqual(fixture["paired_vector_times_schur_product"]["numerator"], 0)
        self.assertEqual(_q(self.value["residue_crosscheck"]["fixture_value"]), Fraction(28, 27))

    def test_fail_closed_infinite_rows(self) -> None:
        status = self.value["infinite_sum_status"]
        self.assertEqual(status["det3_value"], "NOT_COMPUTED")
        self.assertEqual(status["full_coupled_vector_schur_determinant"], "NOT_COMPUTED")
        self.assertFalse(self.value["claim_flags"]["COMPLETE_RENORMALIZED_Q1_SUPPLIED"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(independent_verify(), 0)


if __name__ == "__main__":
    unittest.main()
