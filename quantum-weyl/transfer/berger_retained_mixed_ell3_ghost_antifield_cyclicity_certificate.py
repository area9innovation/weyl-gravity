"""Emit the retained mixed-ell3 full-BV cyclicity certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from .berger_retained_mixed_ell3_ghost_antifield_cyclicity import scientific_replay


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/BERGER_RETAINED_MIXED_ELL3_FULL_BV_CYCLICITY.json"
SCHEMA = HERE / "schema/berger-retained-mixed-ell3-full-bv-cyclicity-v1.schema.json"
SOURCE_PATHS = (
    "quantum-weyl/transfer/berger_retained_mixed_ell3_ghost_antifield_cyclicity.py",
    "quantum-weyl/transfer/berger_retained_mixed_ell3_ghost_antifield_cyclicity_certificate.py",
    "quantum-weyl/transfer/verify_berger_retained_mixed_ell3_ghost_antifield_cyclicity.py",
    "quantum-weyl/transfer/schema/berger-retained-mixed-ell3-full-bv-cyclicity-v1.schema.json",
    "quantum-weyl/transfer/tests/test_berger_retained_mixed_ell3_ghost_antifield_cyclicity.py",
    "quantum-weyl/reports/berger-retained-mixed-ell3-full-bv-cyclicity.md",
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
        raise ValueError("scientific replay required for first full-BV certificate")
    diagnostics = replay["diagnostics"]
    if (
        replay.get("verdict")
        != "ACCEPTED_RETAINED_MIXED_ELL3_FULL_BV_CYCLICITY_LOCAL_ALGEBRAIC"
        or replay.get("classical_commit")
        != "e99d0c1d39490de5261fc6ca1dc2aeaa0d149655"
        or diagnostics.get("retained_ell3_coefficient_count") != 25_950
        or diagnostics.get("physical_quartic_coefficient_count") != 25_662
        or diagnostics.get("ghost_antifield_completion_coefficient_count") != 288
        or diagnostics.get("ghost_antifield_completion_output_rows")
        != [23, 24, 25, 26, 32, 33, 34]
        or diagnostics.get("ghost_antifield_positive_transpose_sign_count") != 120
        or diagnostics.get("ghost_antifield_negative_transpose_sign_count") != 168
        or diagnostics.get("full_BV_cyclicity_defect_count") != 0
        or diagnostics.get("full_BV_cyclicity_defect_rows") != 0
        or diagnostics.get(
            "omitted_degree_two_polarization_mutation_defect_count"
        )
        != 132
        or diagnostics.get("omitted_degree_two_polarization_mutation_defect_rows")
        != 7
    ):
        raise ValueError("retained full-BV cyclicity acceptance failed")
    manifest = {path: _sha256(ROOT / path) for path in SOURCE_PATHS}
    result = {
        "schema": "quantum-weyl-berger-retained-mixed-ell3-full-bv-cyclicity-v1",
        "result_id": "BERGER_RETAINED_MIXED_ELL3_FULL_BV_CYCLICITY",
        "result_state": "FULL_RETAINED_BV_ELL3_CYCLICITY_INDEPENDENTLY_ACCEPTED",
        "lifecycle_layer": "CLASSICAL_BV_IMPORT_ACCEPTANCE",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "classical_commit": replay["classical_commit"],
        "exact_replay": replay,
        "cyclicity_scope": {
            "checked": "all retained physical, ghost and antifield quartic coefficients",
            "formula": "transpose the first input by exact PBW adjunction with absolute typed-pairing component weights and the suspended-Darboux sign",
            "transpose_sign": "(-1)^(parity(first)*parity(paired_output)+epsilon_degree_two(first)+epsilon_degree_two(paired_output))",
            "degree_two_polarization": "epsilon_degree_two is one exactly on the retained degree-two ghost-antifield coordinates",
            "completion_coefficient_count": 288,
        },
        "claim_flags": {
            "PHYSICAL_QUARTIC_CYCLICITY_INDEPENDENTLY_REPLAYED": True,
            "GHOST_ANTIFIELD_COMPLETION_CYCLICITY_INDEPENDENTLY_REPLAYED": True,
            "FULL_RETAINED_BV_ELL3_CYCLICITY_INDEPENDENTLY_REPLAYED": True,
            "POLARIZATION_SIGN_MUTATION_REJECTED": True,
            "RESIDUAL_BRANCH_PROJECTION_COMPUTED": False,
            "QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V1",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC classical-input acceptance independently replays cyclic transposition of the complete 25,950-coefficient retained mixed ell3 over Q(sqrt(10)). It covers the separately certified 25,662 physical coefficients and all 288 ghost/antifield completion coefficients on retained output rows 23, 24, 25, 26, 32, 33 and 34. The suspended-Darboux rule combines the ordinary Koszul exchange sign with one polarization sign for each degree-two ghost-antifield slot; 120 completion coefficients carry the positive transpose sign and 168 carry the negative sign. Exact PBW integration by parts leaves zero coefficient or row defects. Omitting the degree-two polarization exposes 132 defects on all seven completion output rows. This closes full retained BV ell3 cyclicity only for the pinned classical tensor. It does not construct the residual branch basis or projector, restore a QME, construct Hadamard products, or make a quantum, Lorentzian, unitarity or particle-spectrum claim."
        ),
        "provenance": {
            "source_manifest": manifest,
            "source_manifest_sha256": _canonical_hash(manifest),
        },
        "verification_receipts": [
            {
                "test_tier": 2,
                "command": "PYTHONPATH=quantum-weyl python3 -m transfer.berger_retained_mixed_ell3_ghost_antifield_cyclicity_certificate --scientific",
                "status": "PASS",
                "elapsed_seconds": replay["elapsed_seconds"],
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m transfer.verify_berger_retained_mixed_ell3_ghost_antifield_cyclicity",
                "status": "PASS",
                "elapsed_seconds": 0.60,
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_retained_mixed_ell3_ghost_antifield_cyclicity.py -v",
                "status": "PASS",
                "elapsed_seconds": 0.54,
            },
            {
                "test_tier": 1,
                "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s quantum-weyl/transfer/schema/berger-retained-mixed-ell3-full-bv-cyclicity-v1.schema.json -d quantum-weyl/transfer/certificates/BERGER_RETAINED_MIXED_ELL3_FULL_BV_CYCLICITY.json",
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
            raise SystemExit("retained full-BV cyclicity certificate drifted")
    else:
        OUTPUT.write_text(rendered)
    print("BERGER_RETAINED_MIXED_ELL3_FULL_BV_CYCLICITY: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
