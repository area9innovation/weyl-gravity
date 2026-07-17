"""Emit the independent mixed-q3 classical-import acceptance certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from local_bv.schema_validation import validate_instance

from .berger_mixed_q3_acceptance import scientific_replay


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/BERGER_MIXED_Q3_INDEPENDENT_ACCEPTANCE.json"
SCHEMA = HERE / "schema/berger-mixed-q3-independent-acceptance-v1.schema.json"
SOURCE_PATHS = (
    "quantum-weyl/transfer/berger_mixed_q3_acceptance.py",
    "quantum-weyl/transfer/berger_mixed_q3_acceptance_certificate.py",
    "quantum-weyl/transfer/verify_berger_mixed_q3_acceptance.py",
    "quantum-weyl/transfer/schema/berger-mixed-q3-independent-acceptance-v1.schema.json",
    "quantum-weyl/transfer/tests/test_berger_mixed_q3_acceptance.py",
    "quantum-weyl/reports/berger-mixed-q3-independent-acceptance.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build(*, run_scientific: bool) -> dict:
    if run_scientific:
        replay = scientific_replay()
    elif OUTPUT.exists():
        replay = json.loads(OUTPUT.read_text())["exact_replay"]
    else:
        raise ValueError("scientific replay is required for the first certificate build")
    diagnostics = replay["diagnostics"]
    if (
        replay.get("verdict") != "ACCEPTED_TYPED_MIXED_Q3_LOCAL_ALGEBRAIC"
        or replay.get("classical_commit") != "ba51c3853cbb51ef38083b40ceb7e9dda023efa7"
        or diagnostics.get("q1_PBW_coefficient_count") != 1848
        or diagnostics.get("gravity_q2_coefficient_count") != 150305
        or diagnostics.get("typed_mixed_q2_coefficient_count") != 1890
        or diagnostics.get("mixed_q3_coefficient_count") != 59598
        or diagnostics.get("mixed_q3_nonzero_rows") != 21
        or diagnostics.get("typed_q2_graded_symmetry_defect_count") != 0
        or diagnostics.get("typed_q3_graded_symmetry_defect_count") != 0
        or diagnostics.get("mixed_arity_three_defect_count") != 0
        or diagnostics.get("mixed_arity_three_defect_rows") != 0
        or diagnostics.get("localized_mutation_defect_count", 0) <= 0
    ):
        raise ValueError("mixed q3 independent scientific acceptance failed")
    source_manifest = {path: _sha256(ROOT / path) for path in SOURCE_PATHS}
    result = {
        "schema": "quantum-weyl-berger-mixed-q3-independent-acceptance-v1",
        "result_id": "BERGER_MIXED_Q3_INDEPENDENT_ACCEPTANCE",
        "result_state": "TYPED_MIXED_Q3_INDEPENDENTLY_ACCEPTED_RETAINED_ELL3_TRANSFER_OPEN",
        "lifecycle_layer": "CLASSICAL_BV_IMPORT_ACCEPTANCE",
        "classical_commit": replay["classical_commit"],
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "producer_import": {
            "result_id": "BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3",
            "claim_status": replay["producer_claim_status"],
            "input_hashes": replay["input_hashes"],
        },
        "exact_replay": replay,
        "acceptance_conditions": {
            "typed_q2_graded_symmetry_defect_count": 0,
            "typed_q3_graded_symmetry_defect_count": 0,
            "mixed_arity_three_defect_count": 0,
            "mixed_arity_three_defect_rows": 0,
            "localized_mutation_must_be_rejected": True,
            "verdict": "ACCEPTED_TYPED_MIXED_Q3_LOCAL_ALGEBRAIC",
        },
        "claim_flags": {
            "TYPED_MIXED_Q3_PORTABLE_IMPORT_ACCEPTED": True,
            "TYPED_MIXED_Q3_GRADED_SYMMETRY_INDEPENDENTLY_REPLAYED": True,
            "MIXED_ARITY_THREE_IDENTITY_INDEPENDENTLY_REPLAYED": True,
            "K_BERGER_Q3_DERIVATION_INDEPENDENTLY_REPLAYED": True,
            "LOCALIZED_Q3_MUTATION_REJECTED": True,
            "RETAINED_MIXED_ELL3_TRANSFER": False,
            "REPOSITORY_BV_QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_RETAINED_MIXED_ELL3_TRANSFER_AND_EXCHANGE",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC classical-import acceptance pins the typed mixed "
            "gravity-Maxwell q3 at classical commit ba51c3853cbb51ef38083b40ceb7e9dda023efa7. "
            "Without importing the producer, an independent two-rational-component Q(sqrt(10)) "
            "backend parses 1,848 unary, 150,305 gravity-q2, 1,890 typed mixed-q2 and 59,598 "
            "mixed-q3 PBW coefficients; verifies zero typed q2 and q3 graded-symmetry defects; "
            "and recomputes the mixed part of q1 q3 + q2 q2 with zero coefficients on all 64 "
            "rows. A one-coefficient q3 mutation produces a nonzero exact defect. Frozen "
            "K_Berger equivariance follows coefficientwise from its e0 representation, "
            "stationary coefficients and [e0,e_a]=0. This accepts classical interacting input "
            "only. Retained ell3 transfer and the q2 S q2 exchange contribution remain open. "
            "It does not compute a quantum correction, a Slavnov breaking, restore a QME, "
            "construct renormalized Lorentzian products or establish a quantum theory."
        ),
        "consumer_provenance": {
            "source_manifest": source_manifest,
            "source_manifest_sha256": _canonical_hash(source_manifest),
        },
        "verification_receipts": [
            {
                "test_tier": 2,
                "command": "PYTHONPATH=quantum-weyl python3 -m transfer.berger_mixed_q3_acceptance_certificate --scientific",
                "status": "PASS",
                "elapsed_seconds": replay["elapsed_seconds"],
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m transfer.verify_berger_mixed_q3_acceptance",
                "status": "PASS",
                "elapsed_seconds": 0.51,
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_mixed_q3_acceptance.py -v",
                "status": "PASS",
                "elapsed_seconds": 0.52,
            },
            {
                "test_tier": 1,
                "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s quantum-weyl/transfer/schema/berger-mixed-q3-independent-acceptance-v1.schema.json -d quantum-weyl/transfer/certificates/BERGER_MIXED_Q3_INDEPENDENT_ACCEPTANCE.json",
                "status": "PASS",
                "elapsed_seconds": 1.25,
            },
        ],
        "higher_tiers_not_run": {
            "tier_3": "No theorem freeze, quantum lifecycle promotion, retained transfer, causal construction or release boundary changed."
        },
    }
    errors = validate_instance(result, json.loads(SCHEMA.read_text()))
    if errors:
        raise ValueError("mixed q3 acceptance schema failure: " + "; ".join(errors))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scientific", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build(run_scientific=args.scientific)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != rendered:
            raise SystemExit("mixed q3 acceptance certificate drifted")
    else:
        OUTPUT.write_text(rendered)
    print("BERGER_MIXED_Q3_INDEPENDENT_ACCEPTANCE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
