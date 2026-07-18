"""Independent verifier for the York/Hodge nonminimal Berezinian match."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/YORK_HODGE_NONMINIMAL_BEREZINIAN_MATCH.json"
SCHEMA = HERE / "schema/york-hodge-nonminimal-berezinian-match-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _as_fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)

    ledger = value["hodge_superjacobians"]["measure_exponent_ledger"]
    totals: dict[str, Fraction] = {}
    for row in ledger["rows"]:
        totals[row["factor"]] = totals.get(row["factor"], Fraction(0)) + _as_fraction(
            row["determinant_exponent"]
        )
    expected = {
        "Delta_1_T-R/4": Fraction(1, 2),
        "Delta_0": Fraction(0),
        "Delta_0-R/3": Fraction(1, 2),
    }
    if totals != expected or ledger["verified"] is not True:
        raise ValueError("York/Hodge exponent cancellation drifted")

    york = value["exact_york_dimension_identity"]
    canonical = york["canonical"]
    dimension_mutant = york["dimension_five_mutant"]
    if (
        canonical["dimension"] != 4
        or _as_fraction(canonical["vector_operator_R_shift"]) != Fraction(1, 4)
        or _as_fraction(canonical["scalar_norm_prefactor"]) != Fraction(3, 4)
        or _as_fraction(canonical["scalar_operator_R_shift"]) != Fraction(1, 3)
        or canonical["verified_4d_target"] is not True
        or dimension_mutant["dimension"] != 5
        or dimension_mutant["verified_4d_target"] is not False
        or york["mutation_rejected"] is not True
    ):
        raise ValueError("dimension-derived York Gram identity drifted")

    quartet = value["nonminimal_quartet_identity"]["identity"]
    quartet_total = _as_fraction(quartet["bosonic_gaussian_det_M_exponent"]) + _as_fraction(
        quartet["fermionic_antighost_ghost_det_M_exponent"]
    )
    if quartet_total != 0 or _as_fraction(quartet["total_det_M_exponent"]) != 0:
        raise ValueError("BRST quartet superdeterminant drifted")

    factors = value["standard_ghost_factor_match"]["rows"]
    observed = [
        (
            row["factor_id"],
            row["operator"],
            row["rank"],
            _as_fraction(row["partition_function_exponent"]),
            row["standard_M_squared_at_R_12"],
        )
        for row in factors
    ]
    if observed != [
        ("ghost_depth_1", "Delta_1_T-R/4", 3, Fraction(1, 2), -3),
        ("ghost_depth_0", "Delta_0-R/3", 1, Fraction(1, 2), -4),
    ]:
        raise ValueError("standard ghost factor ledger drifted")

    mutant = value["negative_control"]["mutated_ledger"]
    mutant_delta = next(
        _as_fraction(exponent)
        for factor, exponent in mutant["totals"].items()
        if factor == "Delta_0"
    )
    if mutant["verified"] is not False or mutant_delta != Fraction(-1, 2):
        raise ValueError("multiplier-Hodge mutation was not exposed")

    for relative, digest in value["provenance"]["source_sha256"].items():
        if _sha256(ROOT / relative) != digest:
            raise ValueError(f"York/Hodge source hash drifted: {relative}")
    return value


def main() -> int:
    verify()
    print("independent York/Hodge nonminimal Berezinian verifier: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
