from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_axial_ee_ell2_source import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    verify_certificate,
)


class AxialEEEll2SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(DEFAULT_OUTPUT.read_text())

    def test_schema_and_fast_verifier(self) -> None:
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(self.payload)
        verify_certificate()

    def test_source_is_nonzero_and_correction_is_exact(self) -> None:
        self.assertTrue(self.payload["quadratic_source"]["source_nonzero"])
        correction = self.payload["second_order_correction"]
        self.assertTrue(correction["explicit_selected_block_correction"])
        self.assertEqual(correction["operator_remainder"], ["0", "0", "0", "0"])

    def test_full_extension_claim_stays_open(self) -> None:
        classification = self.payload["classification"]
        self.assertFalse(classification["complete_second_order_correction_for_combined_tangent"])
        self.assertFalse(classification["even_AA_and_PP_output_blocks_computed"])
        self.assertTrue(classification["metric_t_and_maxwell_t_rows_computed"])
        self.assertFalse(classification["dependent_angular_rows_directly_replayed"])
        self.assertFalse(classification["general_nonlinear_Einstein_sector_closed"])


if __name__ == "__main__":
    unittest.main()
