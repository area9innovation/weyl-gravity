from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from transfer.berger_coupled_cyclicity_defect_atlas import HERE, PAYLOAD_PATH, build
from transfer.berger_coupled_cyclicity_defect_atlas_certificate import OUTPUT, build_certificate
from transfer.verify_berger_coupled_cyclicity_defect_atlas import _rejects_overclaim, verify


class BergerCoupledCyclicityDefectAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate, cls.payload = build()

    def test_complete_defect_atlas(self) -> None:
        atlas = self.certificate["retained_atlas"]
        self.assertEqual(atlas["total_defect_coefficients"], 953)
        self.assertEqual(atlas["Maxwell_slot_counts"], [{"Maxwell_slots": 2, "count": 953}])
        self.assertEqual(len(self.payload["entries"]), 953)
        self.assertEqual(sum(row["count"] for row in atlas["jet_order_counts"]), 953)

    def test_factor_two_fixture_and_partial_repair(self) -> None:
        fixture = self.certificate["minimal_hAA_fixture"]
        self.assertEqual(
            fixture["raw_q2_coefficients"]["q2_A1_A1_to_h_hat_star_00"]["rational"],
            {"numerator": 40, "denominator": 9},
        )
        self.assertEqual(
            fixture["raw_q2_coefficients"]["q2_h_hat_00_A1_to_A_plus_1"]["rational"],
            {"numerator": 20, "denominator": 9},
        )
        sweep = {
            row["convention"]: row
            for row in self.certificate["convention_sweep"]["output_scaling_cases"]
        }
        self.assertEqual(sweep["uniform_Maxwell_output_x2"]["retained_cyclicity_defect_count"], 15)
        self.assertEqual(sweep["uniform_Maxwell_output_x2"]["retained_q1_q2_defect_count"], 0)

    def test_inadmissible_complete_scaling_and_overclaim_are_rejected(self) -> None:
        sweep = {
            row["convention"]: row
            for row in self.certificate["convention_sweep"]["output_scaling_cases"]
        }
        self.assertEqual(sweep["cyclic_but_nonchain_sector_scaling"]["retained_cyclicity_defect_count"], 0)
        self.assertEqual(sweep["cyclic_but_nonchain_sector_scaling"]["retained_q1_q2_defect_count"], 108)
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["COMPLETE_ADMISSIBLE_CYCLIC_REPAIR_FOUND"] = True
        with self.assertRaises(ValueError):
            _rejects_overclaim(mutant)

    def test_persisted_outputs_and_strict_schemas(self) -> None:
        certificate, payload = build_certificate()
        self.assertEqual(json.loads(OUTPUT.read_text()), certificate)
        self.assertEqual(json.loads(PAYLOAD_PATH.read_text()), payload)
        certificate_schema = json.loads(
            (HERE / "schema/berger-coupled-cyclicity-defect-atlas-v1.schema.json").read_text()
        )
        payload_schema = json.loads(
            (HERE / "schema/berger-coupled-retained-cyclicity-defect-payload-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(certificate, certificate_schema))
        self.assertFalse(validate_instance(payload, payload_schema))

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), build_certificate()[0])


if __name__ == "__main__":
    unittest.main()
