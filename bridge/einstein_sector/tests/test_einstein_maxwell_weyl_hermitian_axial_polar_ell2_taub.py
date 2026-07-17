from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_hermitian_axial_polar_ell2_taub import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    verify_certificate,
)


class HermitianAxialPolarTaubTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(DEFAULT_OUTPUT.read_text())

    def test_schema_and_fast_verifier(self) -> None:
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(self.payload)
        verify_certificate()

    def test_chevreton_and_taub_matrices(self) -> None:
        self.assertTrue(self.payload["chevreton_second_order"]["nonzero"])
        self.assertEqual(self.payload["chevreton_second_order"]["cosine_amplitude_matrix_A_P"][0][1], "0")
        taub = self.payload["weyl_maxwell_taub"]
        self.assertTrue(taub["positive_definite"])
        self.assertEqual(taub["cosine_amplitude_matrix_A_P"][0][1], "0")
        self.assertEqual(len(taub["real_quadrature_matrix"]), 4)

    def test_fixed_bundle_no_go_and_boundaries(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["every_nonzero_real_combination_fixed_bundle_obstructed"])
        self.assertFalse(classification["remaining_harmonic_blocks_needed_for_fixed_bundle_no_go"])
        self.assertFalse(classification["charge_relaxed_extension_constructed"])
        self.assertFalse(classification["general_nonlinear_Einstein_sector_closed"])


if __name__ == "__main__":
    unittest.main()
