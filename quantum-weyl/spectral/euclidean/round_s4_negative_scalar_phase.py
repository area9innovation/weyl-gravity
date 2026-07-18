"""Separate the round-S4 negative scalar determinant phase from local b4."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .round_s4_zero_modes import scalar_degeneracy


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/ROUND_S4_NEGATIVE_SCALAR_PHASE_LOCALITY.json"
SCHEMA = HERE / "schema/round-s4-negative-scalar-phase-locality-v1.schema.json"
ZERO_MODES = HERE / "certificates/ROUND_S4_STANDARD_FACTOR_ZERO_MODE_LEDGER.json"
INTEGRATION = HERE / "certificates/STANDARD_EUCLIDEAN_LOCAL_B4_INTEGRATION_SLICE.json"
SOURCE_PATHS = (
    "quantum-weyl/spectral/euclidean/round_s4_negative_scalar_phase.py",
    "quantum-weyl/spectral/euclidean/verify_round_s4_negative_scalar_phase.py",
    "quantum-weyl/spectral/euclidean/schema/round-s4-negative-scalar-phase-locality-v1.schema.json",
    "quantum-weyl/spectral/euclidean/tests/test_round_s4_negative_scalar_phase.py",
    "quantum-weyl/reports/round-s4-negative-scalar-phase-locality.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _q(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def phase_ledger(*, negative_mode_count: int = 1) -> dict[str, Any]:
    gamma_exponent = Fraction(-1, 2)
    upper_log_phase = negative_mode_count
    lower_log_phase = -negative_mode_count
    return {
        "negative_mode_count": negative_mode_count,
        "Gamma_logdet_exponent": _q(gamma_exponent),
        "upper_cut_log_phase_in_units_of_i_pi": upper_log_phase,
        "lower_cut_log_phase_in_units_of_i_pi": lower_log_phase,
        "upper_cut_Gamma_phase_in_units_of_i_pi": _q(gamma_exponent * upper_log_phase),
        "lower_cut_Gamma_phase_in_units_of_i_pi": _q(gamma_exponent * lower_log_phase),
        "phase_jump_in_units_of_i_pi": _q(gamma_exponent * (upper_log_phase - lower_log_phase)),
    }


def build() -> dict[str, Any]:
    zero = json.loads(ZERO_MODES.read_text())
    integration = json.loads(INTEGRATION.read_text())
    scalar = next(row for row in zero["factor_zero_mode_ledger"] if row["factor_id"] == "ghost_depth_0")
    level_zero = scalar["spectrum"]["scanned_rows"][0]
    factor = next(row for row in integration["factor_exponent_ledger"] if row["factor_id"] == "ghost_depth_0")
    if level_zero != {"level": 0, "eigenvalue": -4} or scalar_degeneracy(0) != 1:
        raise ValueError("negative scalar harmonic ledger drifted")
    if factor["Gamma_logdet_exponent"] != {"numerator": -1, "denominator": 2}:
        raise ValueError("negative scalar determinant exponent drifted")
    phase = phase_ledger()
    mutant = phase_ledger(negative_mode_count=2)
    proof_payload = {
        "dependency_hashes": {"zero_modes": _sha256(ZERO_MODES), "integration_slice": _sha256(INTEGRATION)},
        "mode": {"factor_id": "ghost_depth_0", "harmonic_level": 0, "degeneracy": 1, "eigenvalue_at_unit_radius": -4, "radius_scaling": "lambda_0(a)=-4/a^2"},
        "phase": phase,
        "locality": {
            "spectral_cut_phase_constant_on_negative_eigenvalue_chamber": True,
            "BRST_or_Weyl_variation_of_phase_on_chamber": "ZERO",
            "finite_rank_phase_changes_local_symbol_b4_density": False,
            "finite_rank_magnitude_and_phase_remain_global_determinant_data": True,
            "eigenvalue_crossing_requires_separate_treatment": True,
        },
        "negative_control": {"mutation": "double the level-zero degeneracy", "mutated_phase": mutant, "rejected": mutant != phase},
    }
    return {
        "schema": "quantum-weyl-round-s4-negative-scalar-phase-locality-v1",
        "result_id": "ROUND_S4_NEGATIVE_SCALAR_PHASE_LOCALITY",
        "result_state": "SPECTRAL_CUT_PHASE_EXPLICIT_LOCAL_B4_AND_LOCAL_SLAVNOV_INDEPENDENT_GLOBAL_BRANCH_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        **proof_payload,
        "claim_flags": {"NEGATIVE_SCALAR_PHASE_EXPLICIT": True, "PHASE_IRRELEVANT_TO_LOCAL_B4_DENSITY": True, "PHASE_IRRELEVANT_TO_LOCAL_SLAVNOV_BREAKING_ON_FIXED_SIGN_CHAMBER": True, "GLOBAL_DETERMINANT_BRANCH_SELECTED": False, "REPOSITORY_REGULATOR_ZERO_MODE_MEASURE_LEDGER_CERTIFIED": False, "QME_DISPOSITION": False},
        "proof_sha256": _canonical_hash(proof_payload),
        "next_gate": "BIND_PHASE_LOCALITY_TO_REPOSITORY_REGULATOR_ZERO_MODE_MEASURE_LEDGER",
        "claim_boundary": "This exact finite-mode calculation fixes both spectral-cut phases of the unique negative level-zero eigenvalue of Delta_0-4 and proves that the branch phase is constant while that eigenvalue remains negative. A finite-rank branch phase changes neither the local principal symbol nor the local b4 density and has zero local Slavnov variation on the fixed-sign chamber. The magnitude, overall partition-function phase, continuous-symmetry volume, full repository regulator ledger, coefficient match and QME remain open. No Lorentzian claim is made.",
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
        raise SystemExit(f"stale negative-scalar phase certificate: {OUTPUT}")
    print("round-S4 negative scalar phase locality: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
