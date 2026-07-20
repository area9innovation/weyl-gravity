from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator

from bridge.einstein_sector.asymptotic_bach_schouten_corner_zero_mode_obstruction import (
    ATLAS,
    OUTPUT,
    SCHEMA,
    build_atlas,
    build_certificate,
    check_outputs,
)
from bridge.einstein_sector.verify_asymptotic_bach_schouten_corner_zero_mode_obstruction import (
    verify,
)


class SchoutenCornerZeroModeTests(unittest.TestCase):
    def test_outputs_are_current(self) -> None:
        check_outputs()

    def test_schema_and_independent_rail(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(build_certificate())
        verify()

    def test_minimal_corner_count(self) -> None:
        certificate = build_certificate()
        witness = certificate["exact_finite_jet_witness"]
        self.assertEqual(witness["two_tracefree_components_completed_rank"], 10)
        self.assertEqual(witness["one_corner_component_missing_rank"], 9)
        self.assertFalse(certificate["classification"]["minimal_bulk_Schouten_pair_nondegenerate_with_memory"])

    def test_atlas_is_fail_closed(self) -> None:
        certificate = json.loads(OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(json.loads(ATLAS.read_text(encoding="utf-8")), build_atlas(certificate))
        self.assertEqual(build_atlas(certificate)["entries"][0]["descriptions"]["symplectic"], "OBSTRUCTED")


if __name__ == "__main__":
    unittest.main()
