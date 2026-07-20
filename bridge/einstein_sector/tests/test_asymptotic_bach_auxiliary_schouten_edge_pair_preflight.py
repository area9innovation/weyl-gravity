from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator

from bridge.einstein_sector.asymptotic_bach_auxiliary_schouten_edge_pair_preflight import (
    ATLAS,
    OUTPUT,
    SCHEMA,
    build_atlas,
    build_certificate,
    check_outputs,
)
from bridge.einstein_sector.verify_asymptotic_bach_auxiliary_schouten_edge_pair_preflight import (
    verify,
)


class AuxiliarySchoutenEdgePairPreflightTests(unittest.TestCase):
    def test_outputs_are_current(self) -> None:
        check_outputs()

    def test_schema_and_independent_rail(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(build_certificate())
        verify()

    def test_minimal_pair_and_boundary(self) -> None:
        certificate = build_certificate()
        witness = certificate["minimality_theorem"]["rank_witness"]
        self.assertEqual(witness["rank"], 4)
        self.assertEqual(witness["determinant"], "1")
        self.assertFalse(certificate["classification"]["full_Bondi_BV_BFV_phase_space_constructed"])
        self.assertEqual(certificate["verdicts"]["renormalized_boundary_phase_space"], "OPEN")

    def test_atlas_is_fail_closed(self) -> None:
        certificate = json.loads(OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(json.loads(ATLAS.read_text(encoding="utf-8")), build_atlas(certificate))
        entry = build_atlas(certificate)["entries"][0]
        self.assertEqual(entry["mode_data"]["lee_wald"]["status"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["symplectic"], "OPEN")


if __name__ == "__main__":
    unittest.main()
