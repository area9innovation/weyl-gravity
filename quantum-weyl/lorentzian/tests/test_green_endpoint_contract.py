from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from local_bv.schema_validation import validate_instance
from lorentzian import green_endpoint_contract as CONTRACT
from lorentzian.green_endpoint_contract import (
    GREEN_CHECKS,
    HADAMARD_CHECKS,
    OPERATOR_IDS,
    validate_green_endpoint_export,
)
from lorentzian.green_endpoint_contract_certificate import (
    OUTPUT,
    ROOT,
    build_certificate,
)


class GreenEndpointContractTests(unittest.TestCase):
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
        checks = {
            name: {
                "status": "VERIFIED",
                "proof_artifact": self._artifact(
                    root, f"proofs/{name}.json", "JSON_PROOF_CERTIFICATE"
                ),
            }
            for name in GREEN_CHECKS
        }
        return {
            "schema": "quantum-weyl-berger-26-row-green-endpoint-export-v1",
            "result_id": "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY",
            "result_state": "GREEN_CERTIFIED_HADAMARD_OPEN",
            "classical_commit": "1" * 40,
            "dependency_tags": ["LORENTZIAN-CAUSAL"],
            "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
            "row_layout": {
                "total_rows": 26,
                "degree_ranks": [3, 10, 10, 3],
                "row_ids": [f"row_{index}" for index in range(26)],
            },
            "support_category": {
                "spacetime_dimension": 4,
                "globally_hyperbolic": True,
                "test_function_space": "compactly_supported_smooth_sections",
                "boundary_conditions": "closed_spatial_cylinder",
                "zero_mode_policy": "fifteen_conformal_killing_modes_projected_by_pi_cl",
            },
            "operators": operators,
            "green_proof_checks": checks,
            "hadamard": {"status": "NOT_CONSTRUCTED", "proof_checks": {}},
            "claim_boundary": "Green endpoint only; Hadamard and quantum products remain open.",
        }

    def test_checked_certificate_and_schema_reproduce(self) -> None:
        certificate = build_certificate()
        self.assertEqual(json.loads(OUTPUT.read_text()), certificate)
        schema = json.loads(
            (ROOT / "schema" / "berger-26-row-green-endpoint-contract-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(certificate, schema))
        self.assertEqual(
            certificate["physical_input_status"],
            "PARTIAL_FACTORS_AND_CLOCK_PRINCIPAL_RECEIVED_CURVED_OPEN",
        )
        self.assertEqual(certificate["partial_input"]["certified_blocks"], ["ghost", "identity"])
        factor_path = ROOT.parents[1] / certificate["partial_input"]["certificate"]["path"]
        self.assertEqual(
            hashlib.sha256(factor_path.read_bytes()).hexdigest(),
            certificate["partial_input"]["certificate"]["sha256"],
        )
        self.assertFalse(certificate["quantum_execution_authorized"])
        self.assertEqual(
            certificate["partial_input"]["preferred_metric_principal_route"]["kind"],
            "CLOCK_REATTACHED_SUPPORT_LOCAL_SDR",
        )
        clock_record = certificate["partial_input"]["preferred_metric_principal_route"][
            "certificate"
        ]
        clock_path = ROOT.parents[1] / clock_record["path"]
        self.assertEqual(
            hashlib.sha256(clock_path.read_bytes()).hexdigest(),
            clock_record["sha256"],
        )
        self.assertEqual(certificate["next_gate"], "BERGER_CURVED_CLOCK_REATTACHED_WITNESS")
        forged = deepcopy(certificate)
        forged["required_green_checks"][0] = "invented_check"
        self.assertTrue(validate_instance(forged, schema))

    def test_partial_input_cannot_promote_full_endpoint(self) -> None:
        payload = json.loads(CONTRACT.PARTIAL_INPUT_CERTIFICATE.read_text())
        payload["causal_endpoint_status"]["retained_26_row_chain_homotopy"] = "CERTIFIED"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged-partial-input.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with patch.object(CONTRACT, "PARTIAL_INPUT_CERTIFICATE", path):
                with self.assertRaisesRegex(ValueError, "input identity or boundary"):
                    CONTRACT.build_contract_receipt()

    def test_clock_principal_input_cannot_promote_curved_stage(self) -> None:
        payload = json.loads(CONTRACT.CLOCK_PRINCIPAL_CERTIFICATE.read_text())
        payload["result_state"] = "CURVED_WITNESS_CERTIFIED"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged-clock-principal.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with patch.object(CONTRACT, "CLOCK_PRINCIPAL_CERTIFICATE", path):
                with self.assertRaisesRegex(ValueError, "principal input identity"):
                    CONTRACT.build_contract_receipt()

    def test_complete_green_open_hadamard_payload_validates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            summary = validate_green_endpoint_export(
                self._payload(root), repository_root=root
            )
        self.assertEqual(summary["row_count"], 26)
        self.assertEqual(summary["hadamard_status"], "NOT_CONSTRUCTED")

    def test_bad_artifact_hash_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self._payload(root)
            payload["operators"]["q26"]["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "artifact hash mismatch"):
                validate_green_endpoint_export(payload, repository_root=root)

    def test_row_omission_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self._payload(root)
            payload["row_layout"]["row_ids"].pop()
            with self.assertRaisesRegex(ValueError, "row layout"):
                validate_green_endpoint_export(payload, repository_root=root)

    def test_hadamard_cannot_be_promoted_without_proofs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self._payload(root)
            payload["result_state"] = "GREEN_AND_HADAMARD_CERTIFIED"
            payload["hadamard"]["status"] = "CERTIFIED"
            with self.assertRaisesRegex(ValueError, "fields drifted"):
                validate_green_endpoint_export(payload, repository_root=root)

    def test_green_and_hadamard_complete_branch_validates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self._payload(root)
            payload["result_state"] = "GREEN_AND_HADAMARD_CERTIFIED"
            payload["hadamard"] = {
                "status": "CERTIFIED",
                "proof_checks": {
                    name: {
                        "status": "VERIFIED",
                        "proof_artifact": self._artifact(
                            root,
                            f"hadamard/{name}.json",
                            "JSON_PROOF_CERTIFICATE",
                        ),
                    }
                    for name in HADAMARD_CHECKS
                },
            }
            result = validate_green_endpoint_export(payload, repository_root=root)
        self.assertEqual(result["hadamard_status"], "CERTIFIED")

    def test_missing_support_proof_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self._payload(root)
            del payload["green_proof_checks"]["retarded_support"]
            with self.assertRaisesRegex(ValueError, "fields drifted"):
                validate_green_endpoint_export(payload, repository_root=root)


if __name__ == "__main__":
    unittest.main()
