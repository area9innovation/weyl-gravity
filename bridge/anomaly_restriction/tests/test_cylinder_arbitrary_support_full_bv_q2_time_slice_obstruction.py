from __future__ import annotations

import copy
import json
import unittest

import jsonschema

from bridge.anomaly_restriction.cylinder_arbitrary_support_full_bv_q2_time_slice_obstruction import (
    ATLAS,
    OUTPUT,
    SCHEMA,
    build_atlas,
    build_certificate,
    obstruction_witness,
)
from bridge.anomaly_restriction.verify_cylinder_arbitrary_support_full_bv_q2_time_slice_obstruction import verify_certificate


class CylinderArbitrarySupportQ2TimeSliceObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_schema_and_imports(self) -> None:
        jsonschema.Draft202012Validator(self.schema).validate(self.payload)
        self.assertEqual(len(self.payload["provenance"]["imported_artifacts"]), 8)

    def test_frozen_causal_contraction_is_not_rejected(self) -> None:
        contraction = self.payload["frozen_causal_contraction"]
        self.assertEqual((contraction["full_rank"], contraction["endpoint_rank"]), (386, 30))
        self.assertTrue(contraction["status"].startswith("CERTIFIED_TO_ALL_ENERGY"))

    def test_energy_five_witness_has_rank_64(self) -> None:
        witness = obstruction_witness()
        self.assertEqual(witness["both_chiralities_dimension"], 64)
        self.assertEqual(witness["selected_target_weight_dimension"], 0)
        self.assertEqual(witness["minimum_sdr_defect_rank"], 64)

    def test_all_energy_mutation_removes_only_this_witness(self) -> None:
        witness = obstruction_witness((2, 3, 4, 5))
        self.assertEqual(witness["minimum_sdr_defect_rank"], 0)
        self.assertFalse(self.payload["classification"]["all_energy_repair_carrier_constructed"])

    def test_complete_minimal_q2_ansatz_has_all_roles(self) -> None:
        roles = self.payload["local_q2_ansatz"]["complete_minimal_roles"]
        self.assertEqual([row["symbol"] for row in roles], ["c_mu", "omega", "h_mu_nu", "hstar_mu_nu", "cstar_mu", "omegastar"])
        self.assertEqual(self.payload["local_q2_ansatz"]["domain"]["maximum_metric_derivative_order"], 4)

    def test_anomaly_images_remain_fail_closed(self) -> None:
        self.assertEqual(set(self.payload["anomaly_receiver_verdicts"].values()), {"NO_CERTIFIED_MAP"})

    def test_schema_rejects_false_promotion(self) -> None:
        mutated = copy.deepcopy(self.payload)
        mutated["classification"]["full_arity_two_time_slice_chain_map_certified"] = True
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(self.schema).validate(mutated)

    def test_atlas_is_fail_closed(self) -> None:
        if not OUTPUT.exists():
            self.skipTest("generated certificate absent")
        entry = build_atlas(self.payload)["entries"][0]
        self.assertEqual(entry["descriptions"]["causal"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "NOT_APPLICABLE")

    def test_committed_artifacts_and_independent_verifier(self) -> None:
        if not OUTPUT.exists() or not ATLAS.exists():
            self.skipTest("generated artifacts absent")
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()


if __name__ == "__main__":
    unittest.main()
