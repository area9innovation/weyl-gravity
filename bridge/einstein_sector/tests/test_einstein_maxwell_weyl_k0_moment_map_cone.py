from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_k0_moment_map_cone import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
    verify_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_k0_moment_map_cone import (
    verify_certificate as verify_independently,
)


class K0MomentMapConeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_full_generic_cone(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["full_generic_k0_common_zero_cone_classified"])
        self.assertTrue(
            classification["all_ell_all_m_both_parities_and_all_extra_polarizations_included"]
        )
        self.assertTrue(classification["cross_ell_charge_cancellations_included"])

    def test_neutral_subcone_and_boundaries(self) -> None:
        neutral = self.payload["rotationally_neutral_subcone"]
        self.assertEqual(neutral["dimension_before_overall_scaling"], 2)
        self.assertIn("boundary ray", neutral["paper91_ray"])
        self.assertFalse(self.payload["classification"]["full_quadratic_source_solvability_on_cone_classified"])

    def test_schema_and_verifiers(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()
        verify_independently()


if __name__ == "__main__":
    unittest.main()
