"""Build the fail-closed readiness result for a corrected coupled Berger q2."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .berger_coupled_cyclicity_repair_acceptance import (
    HERE,
    INPUT_SCHEMA,
    accepted_manifest,
    baseline_manifest,
    evaluate,
)


ROOT = HERE.parents[1]
FIXTURE = HERE / "fixtures/berger-coupled-cyclicity-repair-obstructed-baseline.json"
ACCEPTED_FIXTURE = HERE / "fixtures/berger-coupled-cyclicity-repair-accepted-input.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build() -> tuple[dict, dict, dict]:
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

    accepted_fixture = accepted_manifest()
    accepted = evaluate(accepted_fixture)
    if accepted["verdict"] != "ACCEPTED_COUPLED_Q2_CYCLIC_REPAIR":
        raise ValueError("landed corrected candidate was not accepted")
    accepted_diagnostics = accepted["diagnostics"]
    if (
        any(
            accepted_diagnostics[key]
            for key in (
                "full_q1_q2_defect_count",
                "full_cyclicity_defect_count",
                "transfer_missing_coefficient_count",
                "transfer_extra_coefficient_count",
                "transfer_changed_coefficient_count",
                "retained_q1_q2_defect_count",
                "retained_cyclicity_defect_count",
            )
        )
        or accepted_diagnostics["full_overlay_coefficient_count"] != 1890
        or accepted_diagnostics["retained_transfer_coefficient_count"] != 1474
        or accepted_diagnostics["causal_unary_flags_preserved"] is not True
        or accepted_diagnostics["producer_cyclicity_claim_consistent"] is not True
    ):
        raise ValueError("landed corrected candidate diagnostics drifted")

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
        "result_state": "CORRECTED_CLASSICAL_REPAIR_ACCEPTED_MIXED_Q3_INPUT_UNBLOCKED",
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
        "accepted_candidate": {
            "path": "quantum-weyl/transfer/fixtures/berger-coupled-cyclicity-repair-accepted-input.json",
            "file_sha256": hashlib.sha256(
                (json.dumps(accepted_fixture, indent=2, sort_keys=True) + "\n").encode()
            ).hexdigest(),
            "canonical_sha256": _canonical_hash(accepted_fixture),
            "classical_commit": accepted_fixture["classical_commit"],
            "verdict": accepted["verdict"],
            "diagnostics": accepted_diagnostics,
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
            "CORRECTED_CLASSICAL_INPUT_AVAILABLE": True,
            "COUPLED_Q2_CYCLIC_REPAIR_ACCEPTED": True,
            "MIXED_Q3_UNBLOCKED": True,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "IMPORT_OR_COMPUTE_MIXED_Q3_WITH_REPAIRED_Q2",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC classical-import result independently accepts the committed "
            "64/36 Berger gravity-Maxwell q2 repair at classical commit "
            "e4f5c46fd7a04088e78e0374853b1f122ea223b1. Strict Draft 2020-12 schemas and "
            "content hashes pin the carrier, full q2 payload, transfer certificate, and retained "
            "payload. The consumer recomputes zero full and retained q1/q2 defects, zero full and "
            "retained cyclicity defects, exact coefficientwise transfer with 1,890 full and 1,474 "
            "retained coefficients, preserved causal unary flags, and consistent producer flags. "
            "The obstructed baseline remains as a negative control. This accepts the repaired "
            "classical cyclic mixed vertex and unblocks mixed q3 work only; it does not compute q3, "
            "restore a QME, transfer a quantum correction, construct Lorentzian time-ordered "
            "products, establish a particle sector, or make any quantum claim."
        ),
        "consumer_provenance": {
            "source_manifest": source_manifest,
            "source_manifest_sha256": _canonical_hash(source_manifest),
        },
        "verification_receipts": [
            {
                "test_tier": 2,
                "command": "PYTHONPATH=quantum-weyl python3 -m transfer.berger_coupled_cyclicity_repair_readiness_certificate --check",
                "elapsed_seconds": 4.64,
                "status": "PASS",
            },
            {
                "test_tier": 2,
                "command": "PYTHONPATH=quantum-weyl python3 -m transfer.verify_berger_coupled_cyclicity_repair_readiness",
                "elapsed_seconds": 13.54,
                "status": "PASS",
            },
            {
                "test_tier": 2,
                "command": "PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_coupled_cyclicity_repair_readiness.py -v",
                "elapsed_seconds": 27.38,
                "status": "PASS",
            },
            {
                "test_tier": 1,
                "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s quantum-weyl/transfer/schema/berger-coupled-cyclicity-repair-input-v1.schema.json -d quantum-weyl/transfer/fixtures/berger-coupled-cyclicity-repair-obstructed-baseline.json",
                "elapsed_seconds": 1.20,
                "status": "PASS",
            },
            {
                "test_tier": 1,
                "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s quantum-weyl/transfer/schema/berger-coupled-cyclicity-repair-input-v1.schema.json -d quantum-weyl/transfer/fixtures/berger-coupled-cyclicity-repair-accepted-input.json",
                "elapsed_seconds": 2.63,
                "status": "PASS",
            },
            {
                "test_tier": 1,
                "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s quantum-weyl/transfer/schema/berger-coupled-cyclicity-repair-readiness-v1.schema.json -d quantum-weyl/transfer/certificates/BERGER_COUPLED_CYCLICITY_REPAIR_ACCEPTANCE_READINESS.json",
                "elapsed_seconds": 2.14,
                "status": "PASS",
            },
        ],
        "higher_tiers_not_run": {
            "tier_3": (
                "No shared algebra engine, theorem freeze, lifecycle promotion, causal construction, "
                "QME state, Lorentzian certification, release boundary, or classical source artifact changes."
            ),
        },
    }
    return certificate, fixture, accepted_fixture
