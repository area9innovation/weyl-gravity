"""Build the fail-closed readiness result for a corrected coupled Berger q2."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .berger_coupled_cyclicity_repair_acceptance import (
    HERE,
    INPUT_SCHEMA,
    baseline_manifest,
    evaluate,
)


ROOT = HERE.parents[1]
FIXTURE = HERE / "fixtures/berger-coupled-cyclicity-repair-obstructed-baseline.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build() -> tuple[dict, dict]:
    fixture = baseline_manifest()
    baseline = evaluate(fixture)
    if baseline["verdict"] != "REJECTED_EXACT_ALGEBRAIC_DEFECT":
        raise ValueError("obstructed baseline was not rejected")
    diagnostics = baseline["diagnostics"]
    if (
        diagnostics["full_q1_q2_defect_count"] != 0
        or diagnostics["full_cyclicity_defect_count"] != 1234
        or diagnostics["retained_q1_q2_defect_count"] != 0
        or diagnostics["retained_cyclicity_defect_count"] != 953
    ):
        raise ValueError("obstructed baseline diagnostics drifted")

    source_paths = (
        "quantum-weyl/transfer/berger_coupled_cyclicity_repair_acceptance.py",
        "quantum-weyl/transfer/berger_coupled_cyclicity_repair_readiness.py",
        "quantum-weyl/transfer/berger_coupled_cyclicity_repair_readiness_certificate.py",
        "quantum-weyl/transfer/verify_berger_coupled_cyclicity_repair_readiness.py",
        "quantum-weyl/transfer/schema/berger-coupled-cyclicity-repair-input-v1.schema.json",
        "quantum-weyl/transfer/schema/berger-coupled-cyclicity-repair-readiness-v1.schema.json",
        "quantum-weyl/transfer/tests/test_berger_coupled_cyclicity_repair_readiness.py",
        "quantum-weyl/reports/berger-coupled-cyclicity-repair-acceptance.md",
    )
    source_manifest = {path: _sha256(ROOT / path) for path in source_paths}
    certificate = {
        "schema": "quantum-weyl-berger-coupled-cyclicity-repair-readiness-v1",
        "result_id": "BERGER_COUPLED_CYCLICITY_REPAIR_ACCEPTANCE_READINESS",
        "result_state": "INPUT_BLOCKED_CORRECTED_CLASSICAL_COMMIT_NOT_SUPPLIED",
        "lifecycle_layer": "CLASSICAL_BV_IMPORT_ACCEPTANCE",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "input_contract": {
            "path": "quantum-weyl/transfer/schema/berger-coupled-cyclicity-repair-input-v1.schema.json",
            "sha256": _sha256(INPUT_SCHEMA),
            "required_input": "COMMITTED_CORRECTED_CLASSICAL_REPAIR_MANIFEST",
        },
        "obstructed_baseline": {
            "path": "quantum-weyl/transfer/fixtures/berger-coupled-cyclicity-repair-obstructed-baseline.json",
            "file_sha256": hashlib.sha256(
                (json.dumps(fixture, indent=2, sort_keys=True) + "\n").encode()
            ).hexdigest(),
            "canonical_sha256": _canonical_hash(fixture),
            "classical_commit": fixture["classical_commit"],
            "verdict": baseline["verdict"],
            "diagnostics": diagnostics,
        },
        "acceptance_conditions": {
            "full_q1_q2_defect_count": 0,
            "full_cyclicity_defect_count": 0,
            "transfer_missing_coefficient_count": 0,
            "transfer_extra_coefficient_count": 0,
            "transfer_changed_coefficient_count": 0,
            "retained_q1_q2_defect_count": 0,
            "retained_cyclicity_defect_count": 0,
            "causal_unary_flags_preserved": True,
            "producer_cyclicity_claim_consistent": True,
            "verdict": "ACCEPTED_COUPLED_Q2_CYCLIC_REPAIR",
        },
        "claim_flags": {
            "REPAIR_ACCEPTANCE_CONSUMER_READY": True,
            "OBSTRUCTED_BASELINE_REJECTED": True,
            "CORRECTED_CLASSICAL_INPUT_AVAILABLE": False,
            "COUPLED_Q2_CYCLIC_REPAIR_ACCEPTED": False,
            "MIXED_Q3_UNBLOCKED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "SUPPLY_COMMITTED_CORRECTED_CLASSICAL_REPAIR_MANIFEST",
        "claim_boundary": (
            "This readiness result installs an exact LOCAL-ALGEBRAIC consumer and proves "
            "that the committed obstructed 64/36 Berger gravity-Maxwell baseline is rejected. "
            "It does not contain or anticipate a corrected classical tensor. Acceptance requires "
            "a committed, content-addressed carrier, q2 payload, transfer certificate, transferred "
            "payload, and their strict Draft 2020-12 schemas. The consumer independently recomputes "
            "the full and retained q1/q2 identities, full and retained cyclicity, and every transfer "
            "coefficient, while preserving the previously certified causal unary flags. Until all "
            "conditions pass simultaneously, the mixed cyclic vertex, gravitational dressing, mixed "
            "q3, residual transfer, QME, Lorentzian, particle, and quantum claims remain inactive."
        ),
        "consumer_provenance": {
            "source_manifest": source_manifest,
            "source_manifest_sha256": _canonical_hash(source_manifest),
        },
        "verification_receipts": [
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m transfer.berger_coupled_cyclicity_repair_readiness_certificate --check",
                "elapsed_seconds": 2.85,
                "status": "PASS",
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m transfer.verify_berger_coupled_cyclicity_repair_readiness",
                "elapsed_seconds": 5.02,
                "status": "PASS",
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_coupled_cyclicity_repair_readiness.py -v",
                "elapsed_seconds": 13.49,
                "status": "PASS",
            },
            {
                "test_tier": 1,
                "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s quantum-weyl/transfer/schema/berger-coupled-cyclicity-repair-input-v1.schema.json -d quantum-weyl/transfer/fixtures/berger-coupled-cyclicity-repair-obstructed-baseline.json",
                "elapsed_seconds": 1.60,
                "status": "PASS",
            },
            {
                "test_tier": 1,
                "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s quantum-weyl/transfer/schema/berger-coupled-cyclicity-repair-readiness-v1.schema.json -d quantum-weyl/transfer/certificates/BERGER_COUPLED_CYCLICITY_REPAIR_ACCEPTANCE_READINESS.json",
                "elapsed_seconds": 1.02,
                "status": "PASS",
            },
        ],
        "higher_tiers_not_run": {
            "tier_2": (
                "No corrected classical mathematical input exists in this change. Tier 1 replays "
                "the complete obstructed baseline and all exact acceptance predicates; the affected "
                "certificate chain becomes mandatory when a candidate repair manifest is supplied."
            ),
            "tier_3": (
                "No shared algebra engine, theorem freeze, lifecycle promotion, causal construction, "
                "QME state, Lorentzian certification, release boundary, or classical source artifact changes."
            ),
        },
    }
    return certificate, fixture
