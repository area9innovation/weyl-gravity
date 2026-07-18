"""Separate round-S4 conformal zero-mode volume from the local b4 density."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/ROUND_S4_CONFORMAL_ZERO_MODE_VOLUME_LOCALITY.json"
SCHEMA = HERE / "schema/round-s4-conformal-zero-mode-volume-locality-v1.schema.json"
ZERO_MODES = HERE / "certificates/ROUND_S4_STANDARD_FACTOR_ZERO_MODE_LEDGER.json"
MULTIPLICITY = HERE / "certificates/REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER.json"
SOURCE_PATHS = (
    "quantum-weyl/spectral/euclidean/round_s4_conformal_volume_locality.py",
    "quantum-weyl/spectral/euclidean/verify_round_s4_conformal_volume_locality.py",
    "quantum-weyl/spectral/euclidean/schema/round-s4-conformal-zero-mode-volume-locality-v1.schema.json",
    "quantum-weyl/spectral/euclidean/tests/test_round_s4_conformal_volume_locality.py",
    "quantum-weyl/reports/round-s4-conformal-zero-mode-volume-locality.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def conformal_dimension(*, ambient_dimension: int = 6) -> int:
    if ambient_dimension < 2:
        raise ValueError("orthogonal ambient dimension must be at least two")
    return ambient_dimension * (ambient_dimension - 1) // 2


def build() -> dict[str, Any]:
    zero = json.loads(ZERO_MODES.read_text())
    multiplicity = json.loads(MULTIPLICITY.read_text())
    reducibility = zero["reducibility_match"]
    if (
        reducibility["Killing_vector_modes"] != 10
        or reducibility["proper_conformal_scalar_modes"] != 5
        or reducibility["total_conformal_Killing_modes"] != 15
        or conformal_dimension() != 15
        or multiplicity.get("result_state")
        != "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED"
    ):
        raise ValueError("round-S4 conformal zero-mode ledger drifted")
    negative_control = {
        "mutation": "drop one proper-conformal generator",
        "mutated_dimension": 14,
        "so_5_1_dimension": conformal_dimension(),
        "rejected": 14 != conformal_dimension(),
    }
    proof_payload = {
        "dependency_hashes": {"zero_modes": _sha256(ZERO_MODES), "physical_multiplicity": _sha256(MULTIPLICITY)},
        "group_ledger": {"Euclidean_conformal_group": "SO(5,1)", "Lie_algebra": "so(5,1)", "Killing_generators": 10, "proper_conformal_generators": 5, "total_generators": 15, "dimension_formula": "6*5/2=15", "naive_Haar_volume": "NONCOMPACT_DIVERGENT"},
        "measure_disposition": {"prime_deleted_kernel_dimension": 15, "collective_coordinate_or_group_volume_factor_required": True, "normalization_selected": False, "Gram_or_Faddeev_Popov_measure_required_for_global_partition_function": True},
        "locality": {"constant_Haar_normalization_changes_local_symbol": False, "constant_Haar_normalization_changes_local_b4_density": False, "local_Slavnov_variation_on_fixed_stabilizer_stratum": "ZERO", "stabilizer_dimension_jump_requires_separate_treatment": True, "global_partition_function_normalization_remains_open": True},
        "negative_control": negative_control,
    }
    return {
        "schema": "quantum-weyl-round-s4-conformal-zero-mode-volume-locality-v1",
        "result_id": "ROUND_S4_CONFORMAL_ZERO_MODE_VOLUME_LOCALITY",
        "result_state": "SO_5_1_ZERO_MODE_VOLUME_LOCALLY_IRRELEVANT_GLOBAL_COLLECTIVE_COORDINATE_NORMALIZATION_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        **proof_payload,
        "claim_flags": {"FIFTEEN_CONFORMAL_ZERO_MODES_BOUND": True, "NAIVE_CONFORMAL_HAAR_VOLUME_FINITE": False, "VOLUME_NORMALIZATION_IRRELEVANT_TO_LOCAL_B4_FIXED_STRATUM": True, "VOLUME_NORMALIZATION_IRRELEVANT_TO_LOCAL_SLAVNOV_FIXED_STRATUM": True, "GLOBAL_COLLECTIVE_COORDINATE_MEASURE_NORMALIZED": False, "REPOSITORY_REGULATOR_ZERO_MODE_MEASURE_LEDGER_CERTIFIED": False, "QME_DISPOSITION": False},
        "proof_sha256": _canonical_hash(proof_payload),
        "next_gate": "SUPPLY_GLOBAL_COLLECTIVE_COORDINATE_NORMALIZATION_OR_DECLARE_LOCAL_SLAVNOV_ONLY_SCOPE",
        "claim_boundary": "This exact bookkeeping certificate identifies the ten Killing and five proper-conformal round-S4 zero modes with the fifteen-dimensional noncompact Euclidean conformal group SO(5,1). Its naive Haar volume is divergent and no global collective-coordinate normalization is selected. A constant choice of group-volume normalization cannot modify the local operator symbol, local b4 density, or local Slavnov breaking on a fixed stabilizer stratum. Stabilizer jumps, the collective-coordinate Gram/Faddeev-Popov factor, the global partition function, the combined repository measure ledger, QME disposition and Lorentzian theory remain open.",
        "provenance": {"source_sha256": {path: _sha256(ROOT / path) for path in SOURCE_PATHS}},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale conformal-volume locality certificate: {OUTPUT}")
    print("round-S4 conformal zero-mode volume locality: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
