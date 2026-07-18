"""Independent verifier for the consolidated standard integration slice."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/STANDARD_EUCLIDEAN_LOCAL_B4_INTEGRATION_SLICE.json"
SCHEMA = HERE / "schema/standard-euclidean-local-b4-integration-slice-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rows = value["factor_exponent_ledger"]
    observed = [
        (
            row["factor_id"], row["bundle_rank"], row["determinant_sign_in_Gamma"],
            _fraction(row["Gamma_logdet_exponent"]), _fraction(row["Z_determinant_exponent"]),
            row["zero_mode_dimension"], row["primed"],
        )
        for row in rows
    ]
    if observed != [
        ("physical_depth_0", 5, 1, Fraction(1, 2), Fraction(-1, 2), 0, False),
        ("ghost_depth_0", 1, -1, Fraction(-1, 2), Fraction(1, 2), 5, True),
        ("physical_depth_1", 5, 1, Fraction(1, 2), Fraction(-1, 2), 0, False),
        ("ghost_depth_1", 3, -1, Fraction(-1, 2), Fraction(1, 2), 10, True),
    ]:
        raise ValueError("standard integration factor ledger drifted")
    checks = value["aggregate_checks"]
    if checks["signed_effective_bundle_rank"] != 6 or checks["zero_mode_dimension"] != 15:
        raise ValueError("standard integration aggregate drifted")
    if (
        value["measure_and_contour"]["algebraic_TT_auxiliary_modewise_phase"] != "+1"
        or _fraction(value["measure_and_contour"]["unwanted_scalar_Delta0_exponent"]) != 0
        or value["repository_map"]["missing_artifact"]
        != "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1"
        or value["negative_control"]["rejected"] is not True
    ):
        raise ValueError("standard integration measure/map boundary drifted")
    for relative, digest in value["provenance"]["source_sha256"].items():
        if _sha256(ROOT / relative) != digest:
            raise ValueError(f"standard integration source hash drifted: {relative}")
    return value


def main() -> int:
    verify()
    print("independent standard Euclidean integration-slice verifier: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
