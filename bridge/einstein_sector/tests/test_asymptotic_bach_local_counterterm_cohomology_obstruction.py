from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator

from bridge.einstein_sector.asymptotic_bach_local_counterterm_cohomology_obstruction import (
    ATLAS,
    OUTPUT,
    SCHEMA,
    build_atlas,
    build_certificate,
    check_outputs,
)
from bridge.einstein_sector.verify_asymptotic_bach_local_counterterm_cohomology_obstruction import (
    verify,
)


class AsymptoticLocalCountertermObstructionTests(unittest.TestCase):
    def test_generated_outputs_are_current(self) -> None:
        check_outputs()

    def test_schema_and_independent_verifier(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(build_certificate())
        verify()

    def test_fail_closed_boundary(self) -> None:
        certificate = build_certificate()
        flags = certificate["classification"]
        self.assertTrue(flags["fixed_boundary_local_counterterm_repair_obstructed"])
        self.assertFalse(flags["full_tensor_Bondi_BV_BFV_carrier_constructed"])
        self.assertFalse(flags["enlarged_p0_p1_renormalized_phase_space_constructed"])
        self.assertEqual(
            certificate["verdicts"]["work_item"],
            "SHORTFALL_FULL_STOP_CONDITION_NOT_MET",
        )

    def test_atlas_is_generated_and_fail_closed(self) -> None:
        certificate = json.loads(OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(json.loads(ATLAS.read_text(encoding="utf-8")), build_atlas(certificate))
        entry = build_atlas(certificate)["entries"][0]
        self.assertEqual(entry["descriptions"]["symplectic"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["lee_wald"]["status"], "OBSTRUCTED")


if __name__ == "__main__":
    unittest.main()
