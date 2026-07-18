#!/usr/bin/env python3
"""Match the repository round-S4 full-BV ledger to the Euler coefficient."""

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
OUTPUT = HERE / "certificates/REPOSITORY_ROUND_S4_EULER_COEFFICIENT.json"
SCHEMA = HERE / "schema/repository-round-s4-euler-coefficient-v1.schema.json"
STANDARD = HERE / "certificates/WEYL_GRAVITON_ANOMALY_COEFFICIENTS_D_DESCENT.json"
TT_DICTIONARY = HERE / "certificates/REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1.json"
LEDGER = HERE / "certificates/REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER.json"

SOURCE_PATHS = (
    "quantum-weyl/spectral/euclidean/repository_round_s4_euler_coefficient.py",
    "quantum-weyl/spectral/euclidean/verify_repository_round_s4_euler_coefficient.py",
    "quantum-weyl/spectral/euclidean/schema/repository-round-s4-euler-coefficient-v1.schema.json",
    "quantum-weyl/spectral/euclidean/tests/test_repository_round_s4_euler_coefficient.py",
    "quantum-weyl/reports/repository-round-s4-euler-coefficient.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _fraction(value: str) -> Fraction:
    return Fraction(value)


def analysis() -> dict[str, Any]:
    standard = json.loads(STANDARD.read_text())
    tt = json.loads(TT_DICTIONARY.read_text())
    ledger = json.loads(LEDGER.read_text())
    if not (
        tt.get("result_state")
        == "REPOSITORY_ROUND_S4_TT_HESSIAN_FACTORIZED_AND_NORMALIZED"
        and ledger.get("result_state")
        == "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED"
        and ledger.get("classical_commit") == tt.get("classical_commit")
    ):
        raise ValueError("repository round-S4 operator/multiplicity inputs drifted")
    standard_rows = standard["coefficient_calculation"][
        "constant_curvature_factor_ledger"
    ]
    standard_by_id = {row["factor_id"]: row for row in standard_rows}
    repository_by_id = {
        row["factor_id"]: row for row in ledger["repository_factors"]
    }
    maps = ledger["standard_factor_map"]
    rows = []
    total = Fraction(0)
    for mapping in maps:
        target = mapping["target_factor_id"]
        if len(mapping["repository_factor_ids"]) != 1:
            raise ValueError("round-S4 coefficient map is not one-to-one")
        repository_id = mapping["repository_factor_ids"][0]
        standard_row = standard_by_id[target]
        repository_row = repository_by_id[repository_id]
        gamma_sign = -2 * Fraction(
            repository_row["determinant_exponent"]["numerator"],
            repository_row["determinant_exponent"]["denominator"],
        )
        if not (
            gamma_sign == standard_row["determinant_sign"]
            and repository_row["component_rank"] == mapping["target_bundle_rank"]
        ):
            raise ValueError("repository/standard factor sign or rank map drifted")
        contribution = _fraction(standard_row["signed_a_contribution"])
        total += contribution
        rows.append(
            {
                "target_factor_id": target,
                "repository_factor_id": repository_id,
                "operator": repository_row["operator"],
                "bundle_rank": repository_row["component_rank"],
                "Gamma_determinant_sign": int(gamma_sign),
                "signed_a_contribution": str(contribution),
                "status": "MATCHED",
            }
        )
    if total != Fraction(87, 20):
        raise AssertionError("repository round-S4 Euler sum drifted")
    return {
        "classical_commit": tt["classical_commit"],
        "rows": rows,
        "a": str(total),
        "E4_coordinate": str(-total),
        "standard_c_cross_check_only": standard["coefficient_calculation"][
            "derived_c_equals_a_plus_beta1"
        ],
    }


def build() -> dict[str, Any]:
    replay = analysis()
    dependencies = {
        "standard_coefficient_reconstruction": _sha256(STANDARD),
        "repository_TT_dictionary": _sha256(TT_DICTIONARY),
        "repository_full_BV_multiplicity_ledger": _sha256(LEDGER),
    }
    missing = {
        "result": "MINIMAL_MISSING_CARRIER_THEOREM",
        "unresolved_coefficient": "c_C2",
        "reason": "C2 vanishes identically on the conformally flat round S4, so its coefficient is invisible to this physical background ledger",
        "required_artifact": "REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH",
        "standard_value_status": "199/30_AVAILABLE_AS_STANDARD_EUCLIDEAN_CROSS_CHECK_NOT_REPOSITORY_PROMOTED",
    }
    payload: dict[str, Any] = {
        "schema": "quantum-weyl-repository-round-s4-euler-coefficient-v1",
        "result_id": "REPOSITORY_ROUND_S4_EULER_COEFFICIENT",
        "result_state": "REPOSITORY_EUCLIDEAN_S4_EULER_COEFFICIENT_MATCHED_C_COEFFICIENT_OPEN",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL", "LOCAL-ALGEBRAIC"],
        "classical_commit": replay["classical_commit"],
        "dependency_hashes": dependencies,
        "background": {
            "geometry": "round unit S4",
            "Weyl": "0",
            "coefficient_visibility": {"E4": "VISIBLE", "C2": "INVISIBLE"},
        },
        "factor_match": replay["rows"],
        "coefficient_result": {
            "convention": "(4 pi)^(-2) [c C2-a E4] modulo BoxR",
            "a": replay["a"],
            "E4_coordinate": replay["E4_coordinate"],
            "c": "NOT_DETERMINED_ON_ROUND_S4",
            "standard_c_cross_check_only": replay["standard_c_cross_check_only"],
            "parity_odd_coordinate": "0_FOR_DECLARED_PARITY_EVEN_REGULATOR",
        },
        "minimal_missing_carrier_theorem": missing,
        "claim_flags": {
            "REPOSITORY_ROUND_S4_EULER_COEFFICIENT_COMPUTED": True,
            "REPOSITORY_C2_COEFFICIENT_COMPUTED": False,
            "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED": False,
            "REGULATED_SLAVNOV_BREAKING_COMPUTED": False,
            "QME_DISPOSITION": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "next_gate": "SUPPLY_REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH_AND_REGULATED_SLAVNOV_INSERTION",
        "claim_boundary": (
            "This exact EUCLIDEAN-SPECTRAL composition matches every repository "
            "round-S4 full-BV determinant factor to the standard heat-kernel row "
            "and computes a=87/20, equivalently E4 coordinate -87/20. Because the "
            "round sphere is conformally flat, it cannot determine the C2 "
            "coefficient; 199/30 remains a standard Euclidean cross-check rather "
            "than a repository promotion. No regulated Slavnov breaking, BV anomaly "
            "coefficient vector, QME disposition, D-Cartan class, residual transfer, "
            "or Lorentzian quantum theorem is claimed."
        ),
        "provenance": {
            "source_sha256": {path: _sha256(ROOT / path) for path in SOURCE_PATHS}
        },
    }
    payload["proof_sha256"] = _canonical_hash(
        {key: value for key, value in payload.items() if key != "proof_sha256"}
    )
    validate_claim_boundary(payload)
    return payload


def validate_claim_boundary(payload: dict[str, Any]) -> None:
    flags = payload.get("claim_flags", {})
    if flags.get("REPOSITORY_ROUND_S4_EULER_COEFFICIENT_COMPUTED") is not True or any(
        flags.get(name) is not False
        for name in (
            "REPOSITORY_C2_COEFFICIENT_COMPUTED",
            "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED",
            "REGULATED_SLAVNOV_BREAKING_COMPUTED",
            "QME_DISPOSITION",
            "LORENTZIAN_CERTIFIED",
        )
    ):
        raise ValueError("repository round-S4 coefficient claim boundary crossed")


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
    if args.check and (not OUTPUT.is_file() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale repository round-S4 Euler coefficient: {OUTPUT}")
    print("repository round-S4 Euler coefficient: PASS; C2 coefficient open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
