from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
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
ENGINE = sys.modules["arity_two_cartan"]


def _write_disposition(directory: Path, status: str) -> Path:
    path = directory / "D_DISPOSITION.json"
    payload = {
        "setting_id": "fixture-setting",
        "generator_id": "D_compact",
        "D_disposition": {"status": status},
    }
    if status != "OPEN":
        payload["claim_status"] = "CERTIFIED"
    path.write_text(
        json.dumps(payload),
        encoding="utf-8",
    )
    return path


def _manifest_payload(status: str, disposition_path: Path) -> dict[str, object]:
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
        "classical_commit": "0" * 40,
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "artifacts": [
            {
                "artifact_id": artifact_id,
                "path": relative,
                "sha256": digest,
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
            "setting_id": "fixture-setting",
            "generator_id": "D_compact",
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
            manifest.verify(ROOT, registry)
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

            disposition_path.write_text(
                json.dumps(
                    {
                        "setting_id": "fixture-setting",
                        "generator_id": "D_compact",
                        "D_disposition": {"status": "D_GAUGE"},
                    }
                ),
                encoding="utf-8",
            )
            uncertified = _manifest_payload("D_GAUGE", disposition_path)
            with self.assertRaisesRegex(ValueError, "not certified"):
                RUN.PhysicalRunManifest.from_payload(uncertified).verify(ROOT, registry)

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
                        "generator_id": "D_compact",
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
            manifest.verify(ROOT, registry)
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
            result = RUN.execute_verified_manifest(manifest, adapter_registry=adapters)
            self.assertEqual(result["disposition_route"], "CARTAN_CONTRACTION_EXECUTED")
            self.assertEqual(result["cartan_execution"]["classification"], "EXACT_CORRECTION")
            self.assertIsNotNone(result["cartan_execution"]["correction"])

            missing = RUN.AssemblyAdapterRegistry(ROOT)
            with self.assertRaisesRegex(ValueError, "unregistered assembly adapter"):
                RUN.execute_verified_manifest(manifest, adapter_registry=missing)

    def test_non_gauge_D_dispositions_do_not_invoke_adapter(self) -> None:
        expected_routes = {
            "OPEN": "BLOCKED_PENDING_TOTAL_D_DISPOSITION",
            "D_CHARGED_NO_QUOTIENT": "EQUIVARIANCE_ONLY_D_CHARGED_NO_QUOTIENT",
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
                    manifest.verify(ROOT, registry)
                    result = RUN.execute_verified_manifest(
                        manifest,
                        adapter_registry=RUN.AssemblyAdapterRegistry(ROOT),
                    )
                    self.assertEqual(result["disposition_route"], expected_route)
                    self.assertIsNone(result["cartan_execution"])


if __name__ == "__main__":
    unittest.main()
