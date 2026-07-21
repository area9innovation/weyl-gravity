from __future__ import annotations

import copy
import json
import unittest

import jsonschema

from bridge.anomaly_restriction.cylinder_derived_bfv_koszul_time_slice_carrier import (
    ATLAS_OUTPUT,
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_atlas,
    build_certificate,
)
from bridge.anomaly_restriction.verify_cylinder_derived_bfv_koszul_time_slice_carrier import (
    _jacobi_defects,
    verify_certificate,
)


class CylinderDerivedBFVKoszulCarrierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_schema_and_input_count(self) -> None:
        jsonschema.Draft202012Validator(self.schema).validate(self.payload)
        self.assertEqual(len(self.payload["provenance"]["imported_artifacts"]), 13)

    def test_fifteen_eta_generators_and_bfv_nilpotency(self) -> None:
        carrier = self.payload["derived_carrier"]
        self.assertEqual(carrier["constraint_count"], 15)
        self.assertEqual(carrier["generators"]["eta_A_equals_b_A"]["count"], 15)
        self.assertEqual(carrier["nilpotency"]["full_bfv"], "VERIFIED_EXACT_CUBIC_MASTER_EQUATION")

    def test_selected_time_slice_transgression_is_normalized(self) -> None:
        transgression = self.payload["chain_map_ledger"]["endpoint_to_BFV_ghost_momentum"]
        self.assertEqual(transgression["status"], "CERTIFIED_SELECTED_ALGEBRAIC_TIME_SLICE")
        self.assertEqual(transgression["normalization"], "1")

    def test_support_local_map_remains_obstructed(self) -> None:
        support = self.payload["chain_map_ledger"]["support_local_full_BV_bulk_to_slice"]
        self.assertEqual(support["status"], "OBSTRUCTED")
        self.assertEqual(support["witnesses"]["full_support_local_q2"], "NOT_COMPUTED")
        self.assertIn("portable local q1", " ".join(support["missing"]))

    def test_anomaly_first_metric_orders(self) -> None:
        orders = {row["class_id"]: row["first_metric_order"] for row in self.payload["anomaly_perturbative_orders"]}
        self.assertEqual(orders, {"ANOM_OMEGA_C2": 2, "ANOM_OMEGA_E4": 1, "ANOM_OMEGA_C_DUAL_C": 2})
        self.assertTrue(all(row["derived_receiver_map"] == "NO_CERTIFIED_MAP" for row in self.payload["anomaly_perturbative_orders"]))

    def test_decisive_conformal_mutation_breaks_jacobi(self) -> None:
        self.assertEqual(_jacobi_defects(False), 0)
        self.assertGreater(_jacobi_defects(True), 0)

    def test_schema_rejects_support_local_promotion(self) -> None:
        mutation = copy.deepcopy(self.payload)
        mutation["classification"]["support_local_full_BV_time_slice_chain_map_certified"] = True
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(self.schema).validate(mutation)

    def test_atlas_is_fail_closed(self) -> None:
        if not DEFAULT_OUTPUT.exists():
            self.skipTest("certificate not generated")
        atlas = build_atlas(self.payload, DEFAULT_OUTPUT)
        entry = atlas["entries"][0]
        self.assertEqual(entry["descriptions"]["symplectic"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertEqual(entry["descriptions"]["quantum"], "NO_CERTIFIED_MAP")

    def test_committed_artifacts_match_and_verify(self) -> None:
        if not DEFAULT_OUTPUT.exists() or not ATLAS_OUTPUT.exists():
            self.skipTest("generated artifacts absent")
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()


if __name__ == "__main__":
    unittest.main()
