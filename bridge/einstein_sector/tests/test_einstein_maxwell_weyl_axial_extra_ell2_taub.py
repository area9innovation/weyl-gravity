from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_axial_extra_ell2_taub import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    verify_certificate,
)


class AxialExtraEll2TaubTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(DEFAULT_OUTPUT.read_text())

    def test_schema_and_fast_provenance(self) -> None:
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(self.payload)
        verify_certificate()

    def test_real_mode_and_witness(self) -> None:
        self.assertTrue(self.payload["quadratic_source"]["real_conjugate_zero_mode_included"])
        self.assertTrue(self.payload["adjoint_cokernel_witness"]["witness_imported_by_hash"])

    def test_scoped_classification(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["quadratic_Taub_matrix_computed"])
        self.assertTrue(classification["all_nonzero_amplitude_combinations_obstructed"])
        self.assertTrue(self.payload["quadratic_source"]["negative_definite"])
        self.assertEqual(self.payload["quadratic_source"]["signature_positive_negative"], [0, 2])
        self.assertFalse(classification["generic_ell_or_nonzero_k_classified"])
        self.assertFalse(classification["EE_and_EX_quadratic_blocks_computed"])
        self.assertFalse(classification["quantum_claim"])


if __name__ == "__main__":
    unittest.main()
