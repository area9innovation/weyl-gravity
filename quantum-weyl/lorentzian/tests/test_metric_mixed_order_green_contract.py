from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.metric_mixed_order_green_contract import (
    OPERATOR_IDS,
    PROOF_CHECKS,
    validate_metric_green_export,
)
from lorentzian.metric_mixed_order_green_contract_certificate import (
    OUTPUT,
    ROOT,
    build_certificate,
)


class MetricMixedOrderGreenContractTests(unittest.TestCase):
    def _artifact(self, root: Path, name: str, format_: str) -> dict[str, str]:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(name + "\n", encoding="utf-8")
        return {
            "format": format_,
            "path": name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }

    def _payload(self, root: Path) -> dict[str, object]:
        operators = {
            name: self._artifact(root, f"operators/{name}.json", "JSON_EXACT_SPARSE_OPERATOR")
            for name in OPERATOR_IDS
        }
        proofs = {
            name: {
                "status": "VERIFIED",
                "proof_artifact": self._artifact(
                    root, f"proofs/{name}.json", "JSON_PROOF_CERTIFICATE"
                ),
            }
            for name in PROOF_CHECKS
        }
        return {
            "schema": "quantum-weyl-berger-metric-mixed-order-green-export-v1",
            "result_id": "BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION",
            "result_state": "METRIC_AND_ANTIFIELD_GREEN_CERTIFIED",
            "classical_commit": "2" * 40,
            "dependency_tags": ["LORENTZIAN-CAUSAL"],
            "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
            "row_layout": {
                "rows_per_degree": 10,
                "metric_row_ids": [f"metric_{index}" for index in range(10)],
                "metric_antifield_row_ids": [f"metric_antifield_{index}" for index in range(10)],
            },
            "principal_boundary": {
                "generic_fourth_order_rank": 8,
                "polynomial_kernel_dimension": 2,
                "characteristic_rank_stratification": "CLASSIFIED",
                "rank_proof": self._artifact(
                    root, "proofs/principal_rank.json", "JSON_PROOF_CERTIFICATE"
                ),
            },
            "realization": {
                "kind": "FIRST_ORDER_DIFFERENTIAL_ALGEBRAIC",
                "auxiliary_rows": 12,
                "support_local": True,
            },
            "support_category": {
                "spacetime_dimension": 4,
                "globally_hyperbolic": True,
                "test_function_space": "compactly_supported_smooth_sections",
                "boundary_conditions": "closed_spatial_cylinder",
                "zero_mode_policy": "conformal_killing_modes_projected",
            },
            "operators": operators,
            "proof_checks": proofs,
            "claim_boundary": "Metric endpoints only; full 26-row assembly remains separate.",
        }

    def test_checked_certificate_and_schema_reproduce(self) -> None:
        certificate = build_certificate()
        self.assertEqual(json.loads(OUTPUT.read_text()), certificate)
        schema = json.loads(
            (ROOT / "schema" / "berger-metric-mixed-order-green-contract-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(certificate, schema))
        self.assertFalse(certificate["quantum_execution_authorized"])
        forged = deepcopy(certificate)
        forged["required_proof_checks"][0] = "invented_check"
        self.assertTrue(validate_instance(forged, schema))

    def test_complete_metric_export_validates_without_promoting_full_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = validate_metric_green_export(self._payload(root), repository_root=root)
        self.assertEqual(result["metric_green_status"], "CERTIFIED")
        self.assertEqual(
            result["full_26_row_green_status"],
            "ASSEMBLY_REQUIRED_NOT_IMPLICITLY_PROMOTED",
        )

    def test_unclassified_characteristic_rank_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self._payload(root)
            payload["principal_boundary"]["characteristic_rank_stratification"] = "NOT_CLASSIFIED"
            with self.assertRaisesRegex(ValueError, "rank boundary"):
                validate_metric_green_export(payload, repository_root=root)

    def test_downstream_factor_request_does_not_block_metric_verdict(self) -> None:
        certificate = build_certificate()
        self.assertEqual(len(certificate["downstream_endpoint_factor_record_ids"]), 4)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = validate_metric_green_export(self._payload(root), repository_root=root)
        self.assertEqual(result["metric_green_status"], "CERTIFIED")

    def test_unverified_constraint_proof_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self._payload(root)
            payload["proof_checks"]["constraint_compatibility"]["status"] = "OPEN"
            with self.assertRaisesRegex(ValueError, "not verified"):
                validate_metric_green_export(payload, repository_root=root)

    def test_forged_operator_hash_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self._payload(root)
            payload["operators"]["P_metric"]["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "artifact hash mismatch"):
                validate_metric_green_export(payload, repository_root=root)


if __name__ == "__main__":
    unittest.main()
