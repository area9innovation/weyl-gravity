from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator

from spectral.euclidean.generic_background_ghost_schur_wodzicki_residue import (
    OUTPUT,
    SCHEMA,
    build,
)
from spectral.euclidean.verify_generic_background_ghost_schur_wodzicki_residue import (
    main as independent_verify,
)


class GenericBackgroundGhostSchurWodzickiResidueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_schema_and_checked_in_certificate(self) -> None:
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.value)
        self.assertEqual(self.value, json.loads(OUTPUT.read_text()))

    def test_exact_residue_formulas(self) -> None:
        residues = self.value["exact_residues"]
        self.assertEqual(
            residues["K_Ricci_basis"],
            "Wres(K)=(4 pi)^-2 integral[R^2+4 Ric_mn Ric^mn]/9",
        )
        self.assertEqual(
            residues["log_S_Ricci_basis"],
            "Wres(log S_L)=(4 pi)^-2 integral[5 R^2+22 Ric_mn Ric^mn]/54",
        )

    def test_residue_truncation_is_complete(self) -> None:
        truncation = self.value["residue_truncation"]
        self.assertEqual(truncation["B1_order"], -2)
        self.assertEqual(truncation["B2_order"], -4)
        self.assertIn("n>=3", truncation["higher_Bn"])

    def test_einstein_crosscheck(self) -> None:
        check = self.value["exact_residues"]["coefficient_replay"]["Einstein_crosscheck"]
        self.assertEqual(check["direct_R2"], {"numerator": 2, "denominator": 9})
        self.assertEqual(check["general_R2"], check["direct_R2"])
        self.assertEqual(check["residual"], {"numerator": 0, "denominator": 1})

    def test_isotropic_W_crosscheck(self) -> None:
        check = self.value["exact_residues"]["coefficient_replay"]["isotropic_W_B1_crosscheck"]
        self.assertEqual(check["direct_wR"], {"numerator": 1, "denominator": 3})
        self.assertEqual(check["general_wR"], check["direct_wR"])
        self.assertEqual(check["residual"], {"numerator": 0, "denominator": 1})

    def test_claim_boundary_remains_fail_closed(self) -> None:
        flags = self.value["claim_flags"]
        self.assertTrue(flags["WODZICKI_RESIDUE_K_COMPUTED"])
        self.assertTrue(flags["WODZICKI_RESIDUE_LOG_S_COMPUTED"])
        self.assertFalse(flags["FULL_SCHUR_REGULARIZED_DETERMINANT_COMPUTED"])
        self.assertFalse(flags["RENORMALIZED_R_K_COMPUTED"])
        self.assertFalse(flags["FINITE_PART_R_K2_COMPUTED"])
        self.assertFalse(flags["ZETA_MULTIPLICATIVE_ANOMALY_COMPUTED"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(independent_verify(), 0)


if __name__ == "__main__":
    unittest.main()
