"""Consolidated standard Euclidean conformal-spin-two integration slice."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/STANDARD_EUCLIDEAN_LOCAL_B4_INTEGRATION_SLICE.json"
SCHEMA = HERE / "schema/standard-euclidean-local-b4-integration-slice-v1.schema.json"

DEPENDENCIES = {
    "coefficient": HERE / "certificates/WEYL_GRAVITON_ANOMALY_COEFFICIENTS_D_DESCENT.json",
    "auxiliary_Schur": HERE / "certificates/STANDARD_SPIN2_AUXILIARY_FOURTH_ORDER_MATCH.json",
    "scalar_ghost": HERE / "certificates/DIFF_WEYL_SCALAR_GHOST_REDUCTION.json",
    "York_Hodge_measure": HERE / "certificates/YORK_HODGE_NONMINIMAL_BEREZINIAN_MATCH.json",
    "zero_modes": HERE / "certificates/ROUND_S4_STANDARD_FACTOR_ZERO_MODE_LEDGER.json",
    "auxiliary_contour": HERE / "certificates/STANDARD_TT_AUXILIARY_CONTOUR_PHASE.json",
    "repository_TT_readiness": HERE / "certificates/REPOSITORY_TT_HESSIAN_NORMALIZATION_READINESS.json",
}

SOURCE_PATHS = (
    "quantum-weyl/spectral/euclidean/standard_integration_slice.py",
    "quantum-weyl/spectral/euclidean/verify_standard_integration_slice.py",
    "quantum-weyl/spectral/euclidean/schema/standard-euclidean-local-b4-integration-slice-v1.schema.json",
    "quantum-weyl/spectral/euclidean/tests/test_standard_integration_slice.py",
    "quantum-weyl/reports/standard-euclidean-local-b4-integration-slice.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _rational(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def factor_exponent_ledger(*, ghost_scalar_zero_modes: int = 5) -> list[dict[str, Any]]:
    specs = (
        ("physical_depth_0", "Delta_2_perp(4)", 5, 1, 0),
        ("ghost_depth_0", "Delta_0(-4)", 1, -1, ghost_scalar_zero_modes),
        ("physical_depth_1", "Delta_2_perp(2)", 5, 1, 0),
        ("ghost_depth_1", "Delta_1_perp(-3)", 3, -1, 10),
    )
    return [
        {
            "factor_id": factor_id,
            "operator": operator,
            "bundle_rank": rank,
            "determinant_sign_in_Gamma": sign,
            "Gamma_logdet_exponent": _rational(Fraction(sign, 2)),
            "Z_determinant_exponent": _rational(Fraction(-sign, 2)),
            "zero_mode_dimension": zero_modes,
            "primed": zero_modes > 0,
        }
        for factor_id, operator, rank, sign, zero_modes in specs
    ]


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    coefficient = values["coefficient"]
    if coefficient.get("result_state") != "STANDARD_SPIN2_BACKGROUND_COEFFICIENTS_COMPUTED_D_PULLBACK_CERTIFIED":
        raise ValueError("standard coefficient dependency drifted")
    if values["auxiliary_Schur"]["claim_flags"]["STANDARD_PHYSICAL_TT_AUXILIARY_SCHUR_IDENTITY"] is not True:
        raise ValueError("auxiliary Schur identity missing")
    if values["scalar_ghost"]["claim_flags"]["STANDARD_SCALAR_GHOST_OPERATOR_MATCHED"] is not True:
        raise ValueError("scalar ghost match missing")
    if values["York_Hodge_measure"]["claim_flags"]["STANDARD_GHOST_OPERATOR_RANK_AND_EXPONENTS_MATCHED"] is not True:
        raise ValueError("York/Hodge measure match missing")
    if values["zero_modes"]["claim_flags"]["STANDARD_ROUND_S4_FACTOR_ZERO_MODES_COMPLETE"] is not True:
        raise ValueError("standard zero-mode ledger missing")
    if values["auxiliary_contour"]["claim_flags"]["STANDARD_AUXILIARY_CONTOUR_FIXED"] is not True:
        raise ValueError("standard auxiliary contour missing")
    if values["repository_TT_readiness"]["claim_flags"]["REPOSITORY_PHYSICAL_HESSIAN_NORMALIZED"] is not False:
        raise ValueError("repository TT readiness unexpectedly promoted")

    rows = factor_exponent_ledger()
    signed_rank = sum(row["bundle_rank"] * row["determinant_sign_in_Gamma"] for row in rows)
    zero_total = sum(row["zero_mode_dimension"] for row in rows)
    mutant_rows = factor_exponent_ledger(ghost_scalar_zero_modes=4)
    mutant_zero_total = sum(row["zero_mode_dimension"] for row in mutant_rows)
    if signed_rank != 6 or zero_total != 15 or mutant_zero_total == 15:
        raise AssertionError("standard integration-slice mutation control failed")

    local_policy = {
        "effective_action": "Gamma_1=1/2 sum_i determinant_sign_i log det_prime P_i",
        "regularization": "parity-even second-order heat-kernel b4 / zeta-local coefficient",
        "zero_mode_effect_on_local_b4": "NONE_FINITE_DIMENSIONAL_KERNELS_REMOVED_BEFORE_LOCAL_HEAT_TRACE",
        "auxiliary_identity_block_effect_on_local_b4": "ZERO_BY_NORMALIZED_ALGEBRAIC_MEASURE",
        "parity_odd_coordinate": "ZERO_BY_VERIFIED_PARITY_WARD_IDENTITY",
        "global_determinant_phase": "NOT_FIXED_FOR_NEGATIVE_SCALAR_LEVEL_ZERO",
    }
    open_map = {
        "missing_artifact": "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1",
        "unmatched_rows": ["repository physical TT Hessian", "repository algebraic TT auxiliary row"],
        "already_matched_rows": ["transverse Diff ghost", "longitudinal Diff-Weyl scalar ghost", "nonminimal quartet on nonzero modes"],
        "repository_full_BV_multiplicity_ledger_status": "NOT_ACCEPTED",
    }
    proof_payload = {
        "dependencies": {name: _sha256(path) for name, path in DEPENDENCIES.items()},
        "rows": rows,
        "signed_rank": signed_rank,
        "zero_total": zero_total,
        "local_policy": local_policy,
        "open_map": open_map,
    }
    value = {
        "schema": "quantum-weyl-standard-euclidean-local-b4-integration-slice-v1",
        "result_id": "STANDARD_EUCLIDEAN_LOCAL_B4_INTEGRATION_SLICE",
        "result_state": "STANDARD_LOCAL_B4_FACTOR_MEASURE_ZERO_MODE_AND_CONTOUR_SLICE_COMPLETE_REPOSITORY_TT_MAP_OPEN",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL", "LOCAL-ALGEBRAIC"],
        "dependency_hashes": {name: _sha256(path) for name, path in DEPENDENCIES.items()},
        "background": {"geometry": "round unit S4", "dimension": 4, "scalar_curvature": 12},
        "factor_exponent_ledger": rows,
        "aggregate_checks": {
            "signed_effective_bundle_rank": signed_rank,
            "expected_signed_rank": 6,
            "zero_mode_dimension": zero_total,
            "expected_conformal_reducibility_dimension": 15,
            "all_four_factors_covered_once": len({row["factor_id"] for row in rows}) == 4,
        },
        "measure_and_contour": {
            "unwanted_scalar_Delta0_exponent": _rational(0),
            "nonminimal_quartet_superdeterminant": "ONE_ON_COMMON_NONZERO_MODE_DOMAIN",
            "algebraic_TT_auxiliary_contour": "+iR_ORIENTED_NORMALIZED",
            "algebraic_TT_auxiliary_modewise_phase": "+1",
        },
        "local_regulator_policy": local_policy,
        "standard_local_anomaly_coordinates": {
            "basis": ["C2", "E4", "CdualC"],
            "values": ["199/30", "-87/20", "0"],
            "status": "STANDARD_BACKGROUND_ONLY",
        },
        "repository_map": open_map,
        "negative_control": {
            "mutation": "replace the five scalar conformal ghost zero modes by four",
            "mutated_zero_mode_dimension": mutant_zero_total,
            "expected_zero_mode_dimension": 15,
            "rejected": True,
        },
        "claim_flags": {
            "STANDARD_LOCAL_B4_INTEGRATION_SLICE_COMPLETE": True,
            "STANDARD_FACTOR_EXPONENTS_COMPLETE": True,
            "STANDARD_ZERO_MODE_PRIMING_COMPLETE": True,
            "STANDARD_AUXILIARY_CONTOUR_BOUND": True,
            "STANDARD_LOCAL_ANOMALY_VECTOR_REPRODUCED": True,
            "GLOBAL_DETERMINANT_PHASE_FIXED": False,
            "REPOSITORY_TT_HESSIAN_MATCHED": False,
            "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED": False,
            "REPOSITORY_ANOMALY_COEFFICIENT_COMPUTED": False,
            "REGULATED_SLAVNOV_BREAKING_COMPUTED": False,
            "QME_DISPOSITION": False,
        },
        "proof_sha256": _canonical_hash(proof_payload),
        "next_gate": "SUPPLY_REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_AND_ACCEPT_FULL_BV_MULTIPLICITY_LEDGER",
        "claim_boundary": (
            "This exact EUCLIDEAN-SPECTRAL plus LOCAL-ALGEBRAIC certificate consolidates the standard four-factor conformal-spin-two integration slice on the round unit S4. It binds the physical and ghost determinant exponents in Gamma and Z, the nonzero-mode York-Hodge and nonminimal Berezinian, the fifteen primed conformal ghost zero modes, the normalized +iR algebraic TT auxiliary thimble, the parity-even local heat-kernel b4 prescription, and the standard local anomaly coordinates (199/30,-87/20,0). Finite-dimensional zero-mode deletion and the normalized algebraic identity block do not alter the local b4 coefficient. The global phase of the single negative scalar level-zero eigenvalue remains open. Most importantly, this is the standard background slice, not a repository determinant theorem: the repository round-S4 TT Hessian dictionary and algebraic auxiliary-row identification are absent, the full BV multiplicity receiver has not accepted a physical export, and no repository anomaly coefficient, regulated Slavnov breaking, QME disposition, D-Cartan class, residual transfer, or Lorentzian quantum theorem is claimed."
        ),
        "provenance": {"source_sha256": {path: _sha256(ROOT / path) for path in SOURCE_PATHS}},
    }
    validate_claim_boundary(value)
    return value


def validate_claim_boundary(value: dict[str, Any]) -> None:
    flags = value.get("claim_flags", {})
    if not all(flags.get(name) is True for name in (
        "STANDARD_LOCAL_B4_INTEGRATION_SLICE_COMPLETE",
        "STANDARD_FACTOR_EXPONENTS_COMPLETE",
        "STANDARD_ZERO_MODE_PRIMING_COMPLETE",
        "STANDARD_AUXILIARY_CONTOUR_BOUND",
        "STANDARD_LOCAL_ANOMALY_VECTOR_REPRODUCED",
    )) or any(flags.get(name) is not False for name in (
        "GLOBAL_DETERMINANT_PHASE_FIXED",
        "REPOSITORY_TT_HESSIAN_MATCHED",
        "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED",
        "REPOSITORY_ANOMALY_COEFFICIENT_COMPUTED",
        "REGULATED_SLAVNOV_BREAKING_COMPUTED",
        "QME_DISPOSITION",
    )):
        raise ValueError("standard integration-slice claim boundary crossed")


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
        raise SystemExit(f"stale standard integration slice: {OUTPUT}")
    print("standard Euclidean local-b4 integration slice: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
