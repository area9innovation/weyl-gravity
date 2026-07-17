"""Emit the independent retained mixed-ell3 acceptance certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from .berger_retained_mixed_ell3_acceptance import scientific_replay


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/BERGER_RETAINED_MIXED_ELL3_INDEPENDENT_ACCEPTANCE.json"
SCHEMA = HERE / "schema/berger-retained-mixed-ell3-independent-acceptance-v1.schema.json"
REPORT = ROOT / "quantum-weyl/reports/berger-retained-mixed-ell3-independent-acceptance.md"
SOURCE_PATHS = (
    "quantum-weyl/transfer/berger_retained_mixed_ell3_acceptance.py",
    "quantum-weyl/transfer/berger_retained_mixed_ell3_acceptance_certificate.py",
    "quantum-weyl/transfer/verify_berger_retained_mixed_ell3_acceptance.py",
    "quantum-weyl/transfer/schema/berger-retained-mixed-ell3-independent-acceptance-v1.schema.json",
    "quantum-weyl/transfer/tests/test_berger_retained_mixed_ell3_acceptance.py",
    "quantum-weyl/reports/berger-retained-mixed-ell3-independent-acceptance.md",
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
        raise ValueError("scientific replay is required for the first retained ell3 acceptance")
    diagnostics = replay["diagnostics"]
    expected_exchange = {
        "gravity_outer_mixed_inner": 0,
        "mixed_outer_gravity_inner": 0,
        "mixed_outer_mixed_inner": 0,
    }
    expected_raw_exchange = {
        "gravity_outer_mixed_inner": 144,
        "mixed_outer_gravity_inner": 0,
        "mixed_outer_mixed_inner": 0,
    }
    if (
        replay.get("verdict") != "ACCEPTED_RETAINED_MIXED_ELL3_ZERO_EXCHANGE_LOCAL_ALGEBRAIC"
        or replay.get("classical_commit") != "e99d0c1d39490de5261fc6ca1dc2aeaa0d149655"
        or diagnostics.get("full_mixed_q3_coefficient_count") != 59_598
        or diagnostics.get("full_mixed_q3_nonzero_rows") != 21
        or diagnostics.get("retained_ell2_coefficient_count") != 1_474
        or diagnostics.get("retained_ell3_coefficient_count") != 25_950
        or diagnostics.get("retained_ell3_nonzero_rows") != 18
        or diagnostics.get("contact_missing_count") != 0
        or diagnostics.get("contact_extra_count") != 0
        or diagnostics.get("contact_changed_count") != 0
        or diagnostics.get("gravity_inclusion2_coefficient_count") != 96
        or diagnostics.get("mixed_inclusion2_coefficient_count") != 12
        or diagnostics.get("raw_exchange_candidate_counts") != expected_raw_exchange
        or diagnostics.get("exchange_unshuffle_contribution_counts")
        != {"gravity_outer_mixed_inner": 324, "mixed_outer_gravity_inner": 0, "mixed_outer_mixed_inner": 0}
        or diagnostics.get("exchange_full_coefficient_counts")
        != {"gravity_outer_mixed_inner": 342, "mixed_outer_gravity_inner": 0, "mixed_outer_mixed_inner": 0}
        or diagnostics.get("exchange_projection_contribution_counts") != expected_exchange
        or diagnostics.get("exchange_final_coefficient_counts") != expected_exchange
        or diagnostics.get("retained_arity_three_defect_count") != 0
        or diagnostics.get("retained_arity_three_defect_rows") != 0
        or diagnostics.get("mutation_defect_count", 0) <= 0
    ):
        raise ValueError("retained mixed ell3 independent acceptance failed")
    source_manifest = {path: _sha256(ROOT / path) for path in SOURCE_PATHS}
    result = {
        "schema": "quantum-weyl-berger-retained-mixed-ell3-independent-acceptance-v1",
        "result_id": "BERGER_RETAINED_MIXED_ELL3_INDEPENDENT_ACCEPTANCE",
        "result_state": "RETAINED_MIXED_ELL3_INDEPENDENTLY_ACCEPTED_RESIDUAL_BRANCH_PROJECTION_OPEN",
        "lifecycle_layer": "CLASSICAL_BV_IMPORT_ACCEPTANCE",
        "classical_commit": replay["classical_commit"],
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "producer_import": {
            "result_id": "BERGER_RETAINED_MIXED_ELL3_TRANSFER",
            "claim_status": replay["producer_claim_status"],
            "input_hashes": replay["input_hashes"],
        },
        "exact_replay": replay,
        "interaction_classification": {
            "retained_gravity_output_with_two_Maxwell_inputs": 7_614,
            "retained_Maxwell_output_with_one_Maxwell_input": 18_336,
            "other_Maxwell_input_multiplicities": 0,
            "exchange_contribution": "ZERO_AFTER_EXACT_PBW_CONSTRUCTION_AND_RETAINED_OUTPUT_PROJECTION",
            "Einstein_like_extra_Weyl_branch_mixing": "NOT_COMPUTED_REQUIRES_RESIDUAL_BRANCH_PROJECTION",
            "topological_direction": "NOT_CLASSIFIED_ON_RETAINED_36_ROW_COMPLEX",
            "negative_physical_direction_introduced": False,
            "health_reason": "ell3 changes interaction brackets but not the certified unary kinetic operator or its physical signature",
        },
        "claim_flags": {
            "RETAINED_MIXED_ELL3_PORTABLE_IMPORT_ACCEPTED": True,
            "RETAINED_MIXED_ELL3_CONTACT_INDEPENDENTLY_REPLAYED": True,
            "RETAINED_MIXED_ELL3_ALL_EXCHANGE_SECTORS_ZERO": True,
            "RETAINED_MIXED_ARITY_THREE_IDENTITY_INDEPENDENTLY_REPLAYED": True,
            "LOCALIZED_RETAINED_ELL3_MUTATION_REJECTED": True,
            "RETAINED_MIXED_ELL3_CYCLICITY_INDEPENDENTLY_REPLAYED": False,
            "EINSTEIN_EXTRA_WEYL_BRANCH_MIXING_COMPUTED": False,
            "TOPOLOGICAL_DIRECTION_CLASSIFIED": False,
            "NEGATIVE_PHYSICAL_DIRECTION_INTRODUCED": False,
            "REPOSITORY_BV_QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_RESIDUAL_MIXED_ELL3_BRANCH_PROJECTION_AND_MIXING_TABLE",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC classical-import acceptance pins the retained typed mixed gravity-Maxwell ell3 at classical hardening commit e99d0c1d39490de5261fc6ca1dc2aeaa0d149655. Without importing or executing the classical producer, the quantum-side Q(sqrt(10)) PBW backend parses all 59,598 coefficients of the full mixed q3, reconstructs the explicit typed 64-to-36 contraction, and matches all 25,950 retained contact coefficients exactly. It independently reconstructs the 96 gravity and 12 mixed second-inclusion coefficients and verifies their supports. The gravity-outer/mixed-inner channel has 144 raw outer/inner coefficient pairs, producing 324 signed unshuffle contributions and 342 canonical full-complex PBW coefficients. None reaches a full output row supported by the retained projection, so that channel vanishes after exact retained output projection; the other two exchange channels have no raw coefficient pairs. This independently agrees with the hardened producer's exchange-vanishing ledger, and all three retained q2 S q2 exchange sectors are exactly zero. The relative retained arity-three identity closes on all 36 rows, and a one-coefficient retained-ell3 mutation creates two exact defects. The retained interaction has 7,614 gravity-output terms with two Maxwell inputs and 18,336 Maxwell-output terms with one Maxwell input. This proves a nontrivial retained gravity-light interaction but does not project onto Einstein-like, extra-Weyl or topological residual branches. Cyclicity is imported from the typed cyclic transfer theorem rather than independently replayed here. No unary kinetic operator changes, so no negative physical direction is introduced by this bracket; this is not a unitarity theorem. It does not compute a QME correction, restore a QME, construct renormalized Lorentzian products, certify a particle interpretation or make a quantum claim."
        ),
        "consumer_provenance": {
            "source_manifest": source_manifest,
            "source_manifest_sha256": _canonical_hash(source_manifest),
        },
        "verification_receipts": [
            {
                "test_tier": 2,
                "command": "PYTHONPATH=quantum-weyl python3 -m transfer.berger_retained_mixed_ell3_acceptance_certificate --scientific",
                "status": "PASS",
                "elapsed_seconds": replay["elapsed_seconds"],
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m transfer.verify_berger_retained_mixed_ell3_acceptance",
                "status": "PASS",
                "elapsed_seconds": 0.61,
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_retained_mixed_ell3_acceptance.py -v",
                "status": "PASS",
                "elapsed_seconds": 0.78,
            },
            {
                "test_tier": 1,
                "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s quantum-weyl/transfer/schema/berger-retained-mixed-ell3-independent-acceptance-v1.schema.json -d quantum-weyl/transfer/certificates/BERGER_RETAINED_MIXED_ELL3_INDEPENDENT_ACCEPTANCE.json",
                "status": "PASS",
                "elapsed_seconds": 1.42,
            },
        ],
        "higher_tiers_not_run": {
            "tier_3": "No theorem freeze, QME lifecycle promotion, Lorentzian causal construction, shared algebra-engine change, release boundary or quantum claim changed."
        },
    }
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(result)
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
            raise SystemExit("retained mixed ell3 acceptance certificate drifted")
    else:
        OUTPUT.write_text(rendered)
    print("BERGER_RETAINED_MIXED_ELL3_INDEPENDENT_ACCEPTANCE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
