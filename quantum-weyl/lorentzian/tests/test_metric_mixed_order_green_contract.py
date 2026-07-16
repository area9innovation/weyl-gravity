from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.metric_mixed_order_green_contract import (
    CLOCK_PROOF_CHECKS,
    CLOCK_REALIZATION_KIND,
    COMMON_PROOF_CHECKS,
    DIRECT_PROOF_CHECKS,
    OPERATOR_IDS,
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

    def _json_artifact(
        self, root: Path, name: str, payload: dict[str, object]
    ) -> dict[str, str]:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
        return {
            "format": "JSON_PROOF_CERTIFICATE",
            "path": name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }

    def _payload(
        self, root: Path, *, kind: str = "FIRST_ORDER_DIFFERENTIAL_ALGEBRAIC"
    ) -> dict[str, object]:
        operators = {
            name: self._artifact(root, f"operators/{name}.json", "JSON_EXACT_SPARSE_OPERATOR")
            for name in OPERATOR_IDS
        }
        route_checks = CLOCK_PROOF_CHECKS if kind == CLOCK_REALIZATION_KIND else DIRECT_PROOF_CHECKS
        proofs = {
            name: {
                "status": "VERIFIED",
                "proof_artifact": self._artifact(
                    root, f"proofs/{name}.json", "JSON_PROOF_CERTIFICATE"
                ),
            }
            for name in COMMON_PROOF_CHECKS + route_checks
        }
        if kind == CLOCK_REALIZATION_KIND:
            principal_proof = self._json_artifact(
                root,
                "proofs/clock_principal_import.json",
                {
                    "result_id": "BERGER_CLOCK_REATTACHED_PRINCIPAL_INPUT_IMPORT",
                    "result_state": "PRINCIPAL_WITNESS_IMPORTED_CURVED_LOWER_ORDERS_OPEN",
                    "preferred_realization": {"kind": CLOCK_REALIZATION_KIND},
                    "quantum_execution_authorized": False,
                },
            )
            characteristic_status = "RESOLVED_BY_SUPPORT_LOCAL_CLOCK_REATTACHMENT"
            characteristic_set = "zeta^2=0"
            auxiliary_rows = 8
            working_degree_ranks = [5, 12, 12, 5]
        else:
            principal_proof = self._artifact(
                root, "proofs/direct_principal_rank.json", "JSON_PROOF_CERTIFICATE"
            )
            characteristic_status = "CLASSIFIED_DIRECTLY"
            characteristic_set = "directly_classified_characteristic_set"
            auxiliary_rows = 12
            working_degree_ranks = [3, 10, 10, 3]
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
                "retained_characteristic_status": characteristic_status,
                "scalar_characteristic_set": characteristic_set,
                "principal_proof": principal_proof,
            },
            "realization": {
                "kind": kind,
                "auxiliary_rows": auxiliary_rows,
                "support_local": True,
                "working_degree_ranks": working_degree_ranks,
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
        self.assertEqual(
            certificate["current_curved_boundary"]["status"],
            "IMPORTED_AND_EXACTLY_REPLAYED",
        )
        self.assertEqual(certificate["metric_green_status"], "NOT_CONSTRUCTED")
        forged = deepcopy(certificate)
        forged["common_proof_checks"][0] = "invented_check"
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

    def test_unclassified_direct_characteristic_rank_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self._payload(root)
            payload["principal_boundary"]["retained_characteristic_status"] = "NOT_CLASSIFIED"
            with self.assertRaisesRegex(ValueError, "not classified"):
                validate_metric_green_export(payload, repository_root=root)

    def test_clock_reattached_route_bypasses_direct_rank_stratification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = validate_metric_green_export(
                self._payload(root, kind=CLOCK_REALIZATION_KIND), repository_root=root
            )
        self.assertEqual(result["realization_kind"], CLOCK_REALIZATION_KIND)
        self.assertEqual(
            result["principal_resolution"],
            "RESOLVED_BY_SUPPORT_LOCAL_CLOCK_REATTACHMENT",
        )
        self.assertIn("clock_sdr_green_transport", result["required_proof_checks"])
        self.assertNotIn("characteristic_rank_stratification", result["required_proof_checks"])

    def test_clock_route_requires_curved_QW_plus_WQ_proof(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self._payload(root, kind=CLOCK_REALIZATION_KIND)
            del payload["proof_checks"]["curved_clock_reattached_QW_plus_WQ"]
            with self.assertRaisesRegex(ValueError, "proof checks fields drifted"):
                validate_metric_green_export(payload, repository_root=root)

    def test_clock_route_rejects_promoted_principal_import(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self._payload(root, kind=CLOCK_REALIZATION_KIND)
            artifact = payload["principal_boundary"]["principal_proof"]
            path = root / artifact["path"]
            forged = json.loads(path.read_text())
            forged["result_state"] = "CURVED_WITNESS_CERTIFIED"
            path.write_text(json.dumps(forged), encoding="utf-8")
            artifact["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError, "identity or boundary"):
                validate_metric_green_export(payload, repository_root=root)

    def test_downstream_factor_request_does_not_block_metric_verdict(self) -> None:
        certificate = build_certificate()
        self.assertEqual(len(certificate["downstream_endpoint_factor_record_ids"]), 4)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = validate_metric_green_export(self._payload(root), repository_root=root)
        self.assertEqual(result["metric_green_status"], "CERTIFIED")

    def test_next_gate_is_green_realization_not_curved_algebra(self) -> None:
        certificate = build_certificate()
        self.assertIn("GREEN_OPERATORS_FOR_P34", certificate["next_gate"])
        self.assertFalse(certificate["quantum_execution_authorized"])

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
