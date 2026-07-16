from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian import berger_endpoint_factor_import as IMPORTER
from lorentzian.berger_endpoint_factor_import_certificate import (
    OUTPUT,
    build_certificate,
)


ROOT = Path(__file__).resolve().parents[1]


class BergerEndpointFactorImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = IMPORTER._git_json(IMPORTER.CERTIFICATE)
        cls.schema = IMPORTER._git_json(IMPORTER.SCHEMA)
        cls.q1 = IMPORTER._git_json(IMPORTER.Q1_CERTIFICATE)

    def test_checked_certificate_reproduces_and_validates(self) -> None:
        certificate = build_certificate()
        self.assertEqual(json.loads(OUTPUT.read_text()), certificate)
        schema = json.loads(
            (ROOT / "schema" / "berger-endpoint-factor-import-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(certificate, schema))

    def test_exact_endpoint_and_metric_boundary_replay(self) -> None:
        result = IMPORTER.validate_import(self.payload, self.schema, self.q1)
        self.assertTrue(all(result["independent_exact_checks"].values()))
        self.assertEqual(result["metric_boundary"]["fourth_order_rank"], 8)
        self.assertEqual(result["metric_boundary"]["polynomial_kernel_dimension"], 2)
        self.assertFalse(result["metric_boundary"]["negative_physical_direction_introduced"])

    def test_partial_causal_result_does_not_open_quantum_execution(self) -> None:
        result = IMPORTER.validate_import(self.payload, self.schema, self.q1)
        status = result["causal_endpoint_status"]
        self.assertIn("GREEN_HYPERBOLIC", status["ghost_endpoint"])
        self.assertEqual(status["retained_26_row_chain_homotopy"], "NOT_CONSTRUCTED")
        self.assertEqual(status["hadamard_data"], "NOT_CONSTRUCTED")
        self.assertFalse(result["quantum_execution_authorized"])

    def test_mutated_ghost_matrix_fails_closed(self) -> None:
        forged = deepcopy(self.payload)
        forged["degreewise_P_blocks"]["ghost"]["entries"][0][2][0][1] = "0"
        with self.assertRaisesRegex(ValueError, "record hash mismatch"):
            IMPORTER.validate_import(forged, self.schema, self.q1)

    def test_mutated_metric_promotion_fails_closed(self) -> None:
        forged = deepcopy(self.payload)
        forged["flags"]["BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION"] = True
        with self.assertRaisesRegex(ValueError, "claim boundary"):
            IMPORTER.validate_import(forged, self.schema, self.q1)

    def test_mutated_endpoint_factor_theorem_fails_closed(self) -> None:
        forged = deepcopy(self.payload)
        forged["endpoint_factorization"]["factor_1_principal"] = "elliptic"
        with self.assertRaisesRegex(ValueError, "factor theorem"):
            IMPORTER.validate_import(forged, self.schema, self.q1)


if __name__ == "__main__":
    unittest.main()
