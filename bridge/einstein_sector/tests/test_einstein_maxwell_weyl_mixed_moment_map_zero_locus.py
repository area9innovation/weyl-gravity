from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_mixed_moment_map_zero_locus import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
    verify_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_mixed_moment_map_zero_locus import (
    verify_certificate as verify_independently,
)


class MixedMomentMapZeroLocusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_same_k_no_go_and_balanced_fixture(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["same_nonzero_k_travelling_common_H_Px_zero_locus_trivial"])
        self.assertTrue(classification["minimal_nonzero_all_five_moment_map_zero_fixture_constructed"])
        self.assertTrue(self.payload["minimal_k0_balanced_fixture"]["common_moment_maps"]["all_five_zero"])

    def test_preflight_boundary(self) -> None:
        classification = self.payload["classification"]
        self.assertFalse(classification["complete_second_order_extension_constructed"])
        self.assertFalse(classification["absolute_stabilizer_quotient_certified"])

    def test_schema_and_verifiers(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()
        verify_independently()


if __name__ == "__main__":
    unittest.main()
