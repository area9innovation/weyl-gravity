"""Emit the retained mixed-ell3 physical-quartic cyclicity certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from .berger_retained_mixed_ell3_physical_cyclicity import scientific_replay


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/BERGER_RETAINED_MIXED_ELL3_PHYSICAL_CYCLICITY.json"
SCHEMA = HERE / "schema/berger-retained-mixed-ell3-physical-cyclicity-v1.schema.json"
SOURCE_PATHS = (
    "quantum-weyl/transfer/berger_retained_mixed_ell3_physical_cyclicity.py",
    "quantum-weyl/transfer/berger_retained_mixed_ell3_physical_cyclicity_certificate.py",
    "quantum-weyl/transfer/verify_berger_retained_mixed_ell3_physical_cyclicity.py",
    "quantum-weyl/transfer/schema/berger-retained-mixed-ell3-physical-cyclicity-v1.schema.json",
    "quantum-weyl/transfer/tests/test_berger_retained_mixed_ell3_physical_cyclicity.py",
    "quantum-weyl/reports/berger-retained-mixed-ell3-physical-cyclicity.md",
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
        raise ValueError("scientific replay required for first cyclicity certificate")
    diagnostics = replay["diagnostics"]
    if (
        replay.get("verdict")
        != "ACCEPTED_RETAINED_MIXED_ELL3_PHYSICAL_QUARTIC_CYCLICITY_LOCAL_ALGEBRAIC"
        or replay.get("classical_commit")
        != "e99d0c1d39490de5261fc6ca1dc2aeaa0d149655"
        or diagnostics.get("retained_ell3_coefficient_count") != 25_950
        or diagnostics.get("physical_quartic_coefficient_count") != 25_662
        or diagnostics.get("physical_gravity_output_coefficient_count") != 7_506
        or diagnostics.get("physical_Maxwell_output_coefficient_count") != 18_156
        or diagnostics.get("physical_quartic_cyclicity_defect_count") != 0
        or diagnostics.get("physical_quartic_cyclicity_defect_rows") != 0
        or diagnostics.get("Maxwell_pairing_weight_mutation_defect_count")
        != 17_108
        or diagnostics.get("Maxwell_pairing_weight_mutation_defect_rows") != 14
        or diagnostics.get(
            "nonphysical_ghost_antifield_completion_coefficient_count"
        )
        != 288
        or diagnostics.get("physical_pairing_weight_ledger")
        != {
            "gravity": {
                "signed_odd_pairing_entries": ["-1"],
                "absolute_field_equation_weights": ["1"],
                "row_count": 10,
            },
            "Maxwell": {
                "signed_odd_pairing_entries": ["2"],
                "absolute_field_equation_weights": ["2"],
                "row_count": 4,
            },
        }
    ):
        raise ValueError("retained physical-quartic cyclicity acceptance failed")
    manifest = {path: _sha256(ROOT / path) for path in SOURCE_PATHS}
    result = {
        "schema": "quantum-weyl-berger-retained-mixed-ell3-physical-cyclicity-v1",
        "result_id": "BERGER_RETAINED_MIXED_ELL3_PHYSICAL_CYCLICITY",
        "result_state": "PHYSICAL_QUARTIC_CYCLICITY_INDEPENDENTLY_ACCEPTED_FULL_BV_CYCLICITY_OPEN",
        "lifecycle_layer": "CLASSICAL_BV_IMPORT_ACCEPTANCE",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "classical_commit": replay["classical_commit"],
        "exact_replay": replay,
        "cyclicity_scope": {
            "checked": "degree-zero physical inputs paired against degree-one Euler/antifield outputs",
            "formula": "transpose the first input with the positive typed-pairing weight ratio and exact PBW formal adjoint",
            "Maxwell_pairing_weight": 2,
            "gravity_pairing_weight": 1,
            "pairing_sign_convention": "signed odd-pairing orientations are retained in the ledger; the physical field-equation transpose uses their absolute component multiplicities",
            "unreplayed_completion_coefficient_count": 288,
            "unreplayed_completion": "ghost and ghost-antifield BV completion",
        },
        "claim_flags": {
            "PHYSICAL_QUARTIC_CYCLICITY_INDEPENDENTLY_REPLAYED": True,
            "MAXWELL_PAIRING_WEIGHT_MUTATION_REJECTED": True,
            "FULL_RETAINED_BV_ELL3_CYCLICITY_INDEPENDENTLY_REPLAYED": False,
            "RESIDUAL_BRANCH_PROJECTION_COMPUTED": False,
            "TOPOLOGICAL_DEFORMATION_DIRECTION_CLASSIFIED": False,
            "QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_RETAINED_MIXED_ELL3_GHOST_ANTIFIELD_CYCLICITY_REPLAY",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC classical-input acceptance independently lowers the retained mixed ell3 with the exact typed 36-row pairing and replays cyclic transposition of every degree-zero physical quartic coefficient modulo exact PBW integration by parts. The convention receipt records signed odd-pairing entries -1 on ten gravity rows and +2 on four Maxwell rows; the physical field-equation transpose uses their absolute component multiplicities one and two without silently discarding the signed ledger. All 25,662 physical coefficients reproduce with zero defects: 7,506 have gravity output and 18,156 have Maxwell output. Mutating the Maxwell pairing weight from two to one creates 17,108 exact defects on 14 rows. The remaining 288 coefficients belong to the ghost/antifield BV completion and are explicitly not promoted to an independently replayed full-BV cyclicity theorem. The result does not construct an Einstein-like or extra-Weyl residual branch projector, does not identify a topological deformation class with a particle mode, does not restore a QME, and makes no quantum, Lorentzian or unitarity claim."
        ),
        "provenance": {
            "source_manifest": manifest,
            "source_manifest_sha256": _canonical_hash(manifest),
        },
        "verification_receipts": [
            {
                "test_tier": 2,
                "command": "PYTHONPATH=quantum-weyl python3 -m transfer.berger_retained_mixed_ell3_physical_cyclicity_certificate --scientific",
                "status": "PASS",
                "elapsed_seconds": replay["elapsed_seconds"],
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m transfer.verify_berger_retained_mixed_ell3_physical_cyclicity",
                "status": "PASS",
                "elapsed_seconds": 0.60,
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_retained_mixed_ell3_physical_cyclicity.py -v",
                "status": "PASS",
                "elapsed_seconds": 0.54,
            },
            {
                "test_tier": 1,
                "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s quantum-weyl/transfer/schema/berger-retained-mixed-ell3-physical-cyclicity-v1.schema.json -d quantum-weyl/transfer/certificates/BERGER_RETAINED_MIXED_ELL3_PHYSICAL_CYCLICITY.json",
                "status": "PASS",
                "elapsed_seconds": 1.12,
            },
        ],
        "higher_tiers_not_run": {
            "tier_3": "No classical source tensor, shared PBW engine, QME lifecycle state, Lorentzian analytic construction, theorem freeze, release boundary or quantum claim changed."
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
            raise SystemExit("retained physical cyclicity certificate drifted")
    else:
        OUTPUT.write_text(rendered)
    print("BERGER_RETAINED_MIXED_ELL3_PHYSICAL_CYCLICITY: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
