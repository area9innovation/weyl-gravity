#!/usr/bin/env python3
"""Emit the stable ND2 physical-run contract and current input-gate receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
INPUT_PATH = ROOT / "quantum-weyl" / "classical_import" / "exports" / "ND2_PHYSICAL_RUN_INPUT.json"
OUTPUT_PATH = TRANSFER_ROOT / "certificates" / "ND2_PHYSICAL_RUN.json"

try:
    from .arity_two_cartan import build_exact_correction_fixture
    from .nd2_physical_run import AssemblyAdapterRegistry, MANIFEST_SCHEMA, TERMINAL_STATES, execute_evaluated_cartan, load_manifest
    from .support_local_q2_consumer import build_evaluator_registry
except ImportError:
    from arity_two_cartan import build_exact_correction_fixture
    from nd2_physical_run import AssemblyAdapterRegistry, MANIFEST_SCHEMA, TERMINAL_STATES, execute_evaluated_cartan, load_manifest
    from support_local_q2_consumer import build_evaluator_registry


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _source_manifest() -> dict[str, str]:
    paths = (
        "arity_two_cartan.py",
        "evaluator_registry.py",
        "local_expression_ast.py",
        "support_local_q2_consumer.py",
        "nd2_physical_run.py",
        "nd2_physical_run_certificate.py",
        "schema/nd2-physical-run-input-v1.schema.json",
        "schema/nd2-physical-run-certificate-v1.schema.json",
        "tests/test_evaluator_registry.py",
        "tests/test_nd2_physical_run.py",
    )
    return {path: _sha256(TRANSFER_ROOT / path) for path in paths}


def build_certificate() -> dict[str, Any]:
    registry = build_evaluator_registry(repository_root=ROOT)
    adapter_registry = AssemblyAdapterRegistry(ROOT)
    descriptors = [descriptor.to_payload() for descriptor in registry.descriptors()]
    if INPUT_PATH.exists():
        try:
            manifest = load_manifest(INPUT_PATH, repository_root=ROOT, registry=registry)
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            input_gate = {
                "status": "INPUT_REJECTED",
                "manifest_path": str(INPUT_PATH.relative_to(ROOT)),
                "manifest_sha256": _sha256(INPUT_PATH),
                "reason": str(exc),
            }
        else:
            input_gate = {
                "status": "INPUT_VERIFIED_ASSEMBLY_ADAPTER_PENDING",
                "manifest_path": str(INPUT_PATH.relative_to(ROOT)),
                "manifest_sha256": _sha256(INPUT_PATH),
                "reason": f"pinned manifest {manifest.run_id} passed integrity; assembly adapter {manifest.assembly_adapter_id} is not registered",
            }
    else:
        input_gate = {
            "status": "INPUT_NOT_AVAILABLE",
            "manifest_path": str(INPUT_PATH.relative_to(ROOT)),
            "manifest_sha256": None,
            "reason": "no pinned total-D disposition, support-local q1/q2/D, contraction, and admissibility manifest is present",
        }

    self_test = execute_evaluated_cartan(build_exact_correction_fixture())
    source_manifest = _source_manifest()
    return {
        "result_id": "ND2_PHYSICAL_RUN_CONTRACT",
        "result_state": "CONTRACT_READY_PHYSICAL_INPUT_BLOCKED",
        "lifecycle_layer": "INTERACTING",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "setting_verdict": "INPUT_GATE_BLOCKED",
        "contract": {
            "manifest_schema": MANIFEST_SCHEMA,
            "input_schema": "quantum-weyl/transfer/schema/nd2-physical-run-input-v1.schema.json",
            "required_artifacts": [
                "support_local_q1_q2_D",
                "classical_contraction",
                "admissibility_policy",
                "D_disposition_certificate",
            ],
            "D_disposition_routes": {
                "OPEN": "BLOCKED_PENDING_TOTAL_D_DISPOSITION",
                "D_GAUGE": "CARTAN_CONTRACTION_EXECUTED",
                "D_CHARGED_NO_QUOTIENT": "EQUIVARIANCE_ONLY_D_CHARGED_NO_QUOTIENT",
                "SECTOR_DEPENDENT": "SCOPED_DISPOSITION_REQUIRED",
                "NOT_HAMILTONIAN": "CARTAN_CONTRACTION_NOT_APPLICABLE",
            },
            "cartan_execution_policy": "D_GAUGE_ONLY",
            "terminal_disposition_claim_status": "CERTIFIED",
            "accepted_terminal_states": list(TERMINAL_STATES),
            "unregistered_evaluator_policy": "REJECT",
            "unregistered_assembly_adapter_policy": "REJECT",
        },
        "registered_evaluators": descriptors,
        "registered_assembly_adapters": [
            descriptor.to_payload() for descriptor in adapter_registry.descriptors()
        ],
        "engine_self_test": {
            "classification": self_test["classification"],
            "all_checks_pass": all(self_test["checks"].values()),
            "correction_retained": self_test["correction"] is not None,
            "physical_coefficient_claim": False,
        },
        "input_gate": input_gate,
        "established": [
            "stable content-addressed physical-run manifest contract",
            "pinned evaluator identity and implementation hashes are verified before dispatch",
            "support-local, contraction, admissibility, and total-D disposition artifacts must all be present and hashed",
            "only a certified D_GAUGE disposition is routed into Cartan contraction",
            "exact assembled inputs return a retained correction or normalized obstruction witness",
        ],
        "not_established": [
            "a registered conformal-gravity expression evaluator",
            "a registered classical contraction assembly adapter",
            "a terminal total-D disposition for the Berger clock setting",
            "a physical conformal-gravity arity-two Cartan execution",
            "cyclic, real, boundary-compatible, or causal admissibility in a physical setting",
        ],
        "next_gate": "certify the total-D disposition, then install the pinned classical input manifest and register its exact evaluator plus contraction assembly adapter",
        "provenance": {
            "source_manifest": source_manifest,
            "source_manifest_sha256": _canonical_hash(source_manifest),
            "schema": "quantum-weyl/transfer/schema/nd2-physical-run-certificate-v1.schema.json",
        },
    }


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = _render(build_certificate())
    if args.emit:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(content, encoding="utf-8")
    if args.check and (not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != content):
        raise SystemExit(f"ND2 physical-run contract certificate is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("ND2 PHYSICAL RUN: CONTRACT READY, CLASSICAL INPUT BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
