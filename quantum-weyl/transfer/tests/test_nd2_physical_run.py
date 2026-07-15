from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


TRANSFER_ROOT = Path(__file__).resolve().parents[1]
ROOT = TRANSFER_ROOT.parents[1]
if str(TRANSFER_ROOT) not in sys.path:
    sys.path.insert(0, str(TRANSFER_ROOT))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


RUN = _load("nd2_physical_run_test_module", TRANSFER_ROOT / "nd2_physical_run.py")
CERTIFICATE = _load(
    "nd2_physical_run_certificate_test_module",
    TRANSFER_ROOT / "nd2_physical_run_certificate.py",
)
CONSUMER = _load("nd2_physical_consumer_test_module", TRANSFER_ROOT / "support_local_q2_consumer.py")
TOTAL_D_CERTIFICATE = _load(
    "total_d_disposition_certificate_nd2_test_module",
    TRANSFER_ROOT / "total_d_disposition_certificate.py",
)
ENGINE = sys.modules["arity_two_cartan"]


def _disposition_payload(status: str) -> dict[str, object]:
    payload = deepcopy(TOTAL_D_CERTIFICATE.build_certificate())
    if status == "OPEN":
        payload["result_id"] = "ND2_FIXTURE_OPEN"
        payload["claim_status"] = "OPEN"
        payload["assessment_status"] = "OPEN"
        payload["verdict"] = None
        payload["charge_audit"] = {
            "combined_gravitational_matter_presymplectic_contraction": "OPEN",
            "normalization": "OPEN",
            "integrability": "OPEN",
            "allowed_fixed_coupling_delta_Q_tangent": "OPEN",
            "presymplectic_kernel": "OPEN",
            "total_D_charge_variation": "OPEN",
        }
        payload["exact_checks"] = {
            key: key == "exact_arithmetic" for key in payload["exact_checks"]
        }
        payload["fail_closed"] = {
            "D_quotient_authorized": False,
            "unresolved_fields": ["fixture total-D audit"],
            "claim_boundary": "ND2 open routing fixture only.",
        }
        return payload
    payload["result_id"] = f"ND2_FIXTURE_{status}"
    payload["claim_status"] = "CERTIFIED"
    payload["assessment_status"] = "COMPUTED"
    payload["verdict"] = status
    payload["charge_audit"].update(
        {
            "combined_gravitational_matter_presymplectic_contraction": "COMPUTED",
            "normalization": "FIXED",
            "allowed_fixed_coupling_delta_Q_tangent": "EXISTS",
        }
    )
    signatures = {
        "D_GAUGE": ("INTEGRABLE", "D_IN_KERNEL", "ZERO"),
        "D_CHARGED": ("INTEGRABLE", "D_NOT_IN_KERNEL", "NONZERO"),
        "SECTOR_DEPENDENT": (
            "SECTOR_DEPENDENT",
            "SECTOR_DEPENDENT",
            "SECTOR_DEPENDENT",
        ),
        "NOT_HAMILTONIAN": ("NONINTEGRABLE", "NOT_DEFINED", "NOT_DEFINED"),
    }
    (
        payload["charge_audit"]["integrability"],
        payload["charge_audit"]["presymplectic_kernel"],
        payload["charge_audit"]["total_D_charge_variation"],
    ) = signatures[status]
    payload["exact_checks"] = {key: True for key in payload["exact_checks"]}
    payload["fail_closed"] = {
        "D_quotient_authorized": status == "D_GAUGE",
        "unresolved_fields": [],
        "claim_boundary": "ND2 exact routing fixture only.",
    }
    if status == "SECTOR_DEPENDENT":
        payload["charge_audit"]["allowed_fixed_coupling_delta_Q_tangent"] = "SECTOR_DEPENDENT"
        payload["sector_ledger"] = [
            {
                "sector_id": "gauge-sector",
                "phase_space_id": payload["phase_space_id"],
                "verdict": "D_GAUGE",
                "total_D_charge_variation": "ZERO",
                "presymplectic_kernel": "D_IN_KERNEL",
            },
            {
                "sector_id": "charged-sector",
                "phase_space_id": payload["phase_space_id"],
                "verdict": "D_CHARGED",
                "total_D_charge_variation": "NONZERO",
                "presymplectic_kernel": "D_NOT_IN_KERNEL",
            },
        ]
    return payload


def _write_disposition(directory: Path, status: str) -> Path:
    path = directory / "D_DISPOSITION.json"
    path.write_text(json.dumps(_disposition_payload(status)), encoding="utf-8")
    return path


def _manifest_payload(status: str, disposition_path: Path) -> dict[str, object]:
    disposition = json.loads(disposition_path.read_text(encoding="utf-8"))
    registry = CONSUMER.build_evaluator_registry(repository_root=ROOT)
    evaluator = registry.descriptor("scalar-identity-fixture-v1")
    artifact_path = TRANSFER_ROOT / "arity_two_cartan.py"
    relative = artifact_path.relative_to(ROOT).as_posix()
    digest = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
    disposition_relative = disposition_path.relative_to(ROOT).as_posix()
    disposition_digest = hashlib.sha256(disposition_path.read_bytes()).hexdigest()
    return {
        "schema": RUN.MANIFEST_SCHEMA,
        "run_id": f"fixture-{status.lower()}",
        "classical_commit": disposition["classical_commit"],
        "dependency_tags": disposition["dependency_tags"],
        "artifacts": [
            {
                "artifact_id": artifact_id,
                "path": relative,
                "sha256": digest,
                "dependency_tags": ["LOCAL-ALGEBRAIC"],
            }
            for artifact_id in (
                "support_local_q1_q2_D",
                "classical_contraction",
                "admissibility_policy",
            )
        ]
        + [
            {
                "artifact_id": "D_disposition_certificate",
                "path": disposition_relative,
                "sha256": disposition_digest,
                "dependency_tags": disposition["dependency_tags"],
            }
        ],
        "evaluator": {
            "evaluator_id": evaluator.evaluator_id,
            "expression_schema_version": evaluator.expression_schema_version,
            "implementation_manifest_sha256": evaluator.implementation_manifest_sha256,
        },
        "assembly_adapter_id": "fixture-assembly-v1",
        "D_disposition": {
            "status": status,
            "setting_id": disposition["setting_id"],
            "phase_space_id": disposition["phase_space_id"],
            "generator_id": disposition["generator_id"],
            "boundary_conditions_sha256": disposition["boundary_conditions_sha256"],
        },
    }


class ND2PhysicalRunTests(unittest.TestCase):
    def test_checked_in_certificate_reproduces_and_stays_blocked(self) -> None:
        checked = json.loads(CERTIFICATE.OUTPUT_PATH.read_text(encoding="utf-8"))
        rebuilt = CERTIFICATE.build_certificate()
        self.assertEqual(checked, rebuilt)
        self.assertEqual(rebuilt["input_gate"]["status"], "INPUT_NOT_AVAILABLE")
        self.assertEqual(rebuilt["setting_verdict"], "INPUT_GATE_BLOCKED")

    def test_evaluated_exact_fixture_returns_retained_correction(self) -> None:
        result = RUN.execute_evaluated_cartan(ENGINE.build_exact_correction_fixture())
        self.assertEqual(result["classification"], "EXACT_CORRECTION")
        self.assertTrue(all(result["checks"].values()))
        self.assertIsNotNone(result["correction"])
        self.assertIsNone(result["dual_witness"])

    def test_manifest_verifies_four_pinned_artifacts_and_evaluator(self) -> None:
        registry = CONSUMER.build_evaluator_registry(repository_root=ROOT)
        with tempfile.TemporaryDirectory(prefix=".nd2-disposition-", dir=ROOT) as raw:
            disposition_path = _write_disposition(Path(raw), "OPEN")
            payload = _manifest_payload("OPEN", disposition_path)
            manifest = RUN.PhysicalRunManifest.from_payload(payload)
            verified = manifest.verify(ROOT, registry)
            self.assertIs(verified.manifest, manifest)
            tampered = dict(payload)
            tampered["evaluator"] = dict(payload["evaluator"])
            tampered["evaluator"]["implementation_manifest_sha256"] = "f" * 64
            with self.assertRaisesRegex(ValueError, "implementation hash mismatch"):
                RUN.PhysicalRunManifest.from_payload(tampered).verify(ROOT, registry)

            mismatched = dict(payload)
            mismatched["D_disposition"] = dict(payload["D_disposition"])
            mismatched["D_disposition"]["status"] = "D_GAUGE"
            with self.assertRaisesRegex(ValueError, "disagrees"):
                RUN.PhysicalRunManifest.from_payload(mismatched).verify(ROOT, registry)

            phase_mismatch = dict(payload)
            phase_mismatch["D_disposition"] = dict(payload["D_disposition"])
            phase_mismatch["D_disposition"]["phase_space_id"] = "wrong-phase-space"
            with self.assertRaisesRegex(ValueError, "phase space disagrees"):
                RUN.PhysicalRunManifest.from_payload(phase_mismatch).verify(ROOT, registry)

            boundary_mismatch = dict(payload)
            boundary_mismatch["D_disposition"] = dict(payload["D_disposition"])
            boundary_mismatch["D_disposition"]["boundary_conditions_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "boundary conditions disagree"):
                RUN.PhysicalRunManifest.from_payload(boundary_mismatch).verify(
                    ROOT,
                    registry,
                )

            commit_mismatch = dict(payload)
            commit_mismatch["classical_commit"] = "0" * 40
            with self.assertRaisesRegex(ValueError, "classical commit disagrees"):
                RUN.PhysicalRunManifest.from_payload(commit_mismatch).verify(ROOT, registry)

            dependency_mismatch = dict(payload)
            dependency_mismatch["dependency_tags"] = ["LOCAL-ALGEBRAIC"]
            with self.assertRaisesRegex(ValueError, "artifact union"):
                RUN.PhysicalRunManifest.from_payload(dependency_mismatch)

            disposition_scope_mismatch = dict(payload)
            disposition_scope_mismatch["artifacts"] = [
                dict(artifact) for artifact in payload["artifacts"]
            ]
            disposition_artifact = next(
                artifact
                for artifact in disposition_scope_mismatch["artifacts"]
                if artifact["artifact_id"] == "D_disposition_certificate"
            )
            disposition_artifact["dependency_tags"] = ["LOCAL-ALGEBRAIC"]
            next(
                artifact
                for artifact in disposition_scope_mismatch["artifacts"]
                if artifact["artifact_id"] == "support_local_q1_q2_D"
            )["dependency_tags"] = ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
            with self.assertRaisesRegex(ValueError, "artifact dependency scope"):
                RUN.PhysicalRunManifest.from_payload(disposition_scope_mismatch).verify(
                    ROOT,
                    registry,
                )

            disposition_payload = json.loads(
                disposition_path.read_text(encoding="utf-8")
            )
            disposition_payload["provenance"]["source_artifacts"][0]["sha256"] = "f" * 64
            disposition_path.write_text(
                json.dumps(disposition_payload),
                encoding="utf-8",
            )
            provenance_mismatch = _manifest_payload("OPEN", disposition_path)
            with self.assertRaisesRegex(ValueError, "provenance hash mismatch"):
                RUN.PhysicalRunManifest.from_payload(provenance_mismatch).verify(
                    ROOT,
                    registry,
                )

    def test_manifest_inventory_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "inventory"):
            RUN.PhysicalRunManifest.from_payload(
                {
                    "schema": RUN.MANIFEST_SCHEMA,
                    "run_id": "bad",
                    "classical_commit": "0" * 40,
                    "dependency_tags": ["LOCAL-ALGEBRAIC"],
                    "artifacts": [],
                    "evaluator": {
                        "evaluator_id": "none",
                        "expression_schema_version": "none",
                        "implementation_manifest_sha256": "0" * 64,
                    },
                    "assembly_adapter_id": "none",
                    "D_disposition": {
                        "status": "OPEN",
                        "setting_id": "fixture-setting",
                        "phase_space_id": "fixture-phase-space",
                        "generator_id": "D_compact",
                        "boundary_conditions_sha256": "0" * 64,
                    },
                }
            )

    def test_only_D_gauge_route_executes_content_addressed_adapter(self) -> None:
        registry = CONSUMER.build_evaluator_registry(repository_root=ROOT)
        artifact_path = TRANSFER_ROOT / "arity_two_cartan.py"
        with tempfile.TemporaryDirectory(prefix=".nd2-disposition-", dir=ROOT) as raw:
            disposition_path = _write_disposition(Path(raw), "D_GAUGE")
            manifest = RUN.PhysicalRunManifest.from_payload(
                _manifest_payload("D_GAUGE", disposition_path)
            )
            verified = manifest.verify(ROOT, registry)
            adapters = RUN.AssemblyAdapterRegistry(ROOT)
            descriptor = RUN.AssemblyAdapterDescriptor.from_paths(
                adapter_id="fixture-assembly-v1",
                repository_root=ROOT,
                implementation_paths=(artifact_path,),
            )
            adapters.register(
                descriptor,
                lambda _manifest: (ENGINE.build_exact_correction_fixture(), None),
            )
            with self.assertRaisesRegex(TypeError, "VerifiedPhysicalRun"):
                RUN.execute_verified_manifest(manifest, adapter_registry=adapters)
            with self.assertRaisesRegex(TypeError, "created only"):
                RUN.VerifiedPhysicalRun(manifest, None)

            result = RUN.execute_verified_manifest(verified, adapter_registry=adapters)
            self.assertEqual(result["disposition_route"], "CARTAN_CONTRACTION_EXECUTED")
            self.assertEqual(result["cartan_execution"]["classification"], "EXACT_CORRECTION")
            self.assertIsNotNone(result["cartan_execution"]["correction"])

            missing = RUN.AssemblyAdapterRegistry(ROOT)
            with self.assertRaisesRegex(ValueError, "unregistered assembly adapter"):
                RUN.execute_verified_manifest(verified, adapter_registry=missing)

    def test_non_gauge_D_dispositions_do_not_invoke_adapter(self) -> None:
        expected_routes = {
            "OPEN": "BLOCKED_PENDING_TOTAL_D_DISPOSITION",
            "D_CHARGED": "EQUIVARIANCE_ONLY_D_CHARGED_NO_QUOTIENT",
            "SECTOR_DEPENDENT": "SCOPED_DISPOSITION_REQUIRED",
            "NOT_HAMILTONIAN": "CARTAN_CONTRACTION_NOT_APPLICABLE",
        }
        registry = CONSUMER.build_evaluator_registry(repository_root=ROOT)
        with tempfile.TemporaryDirectory(prefix=".nd2-disposition-", dir=ROOT) as raw:
            directory = Path(raw)
            for status, expected_route in expected_routes.items():
                with self.subTest(status=status):
                    disposition_path = _write_disposition(directory, status)
                    manifest = RUN.PhysicalRunManifest.from_payload(
                        _manifest_payload(status, disposition_path)
                    )
                    verified = manifest.verify(ROOT, registry)
                    result = RUN.execute_verified_manifest(
                        verified,
                        adapter_registry=RUN.AssemblyAdapterRegistry(ROOT),
                    )
                    self.assertEqual(result["disposition_route"], expected_route)
                    self.assertIsNone(result["cartan_execution"])


if __name__ == "__main__":
    unittest.main()
