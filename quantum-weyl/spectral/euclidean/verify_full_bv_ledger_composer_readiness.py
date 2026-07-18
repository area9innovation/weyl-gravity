"""Independent verifier for the full-BV multiplicity composer readiness."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/REPOSITORY_FULL_BV_LEDGER_COMPOSER_READINESS.json"
SCHEMA = HERE / "schema/repository-full-bv-ledger-composer-readiness-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    contract = value["accepted_contract"]
    if contract["standard_factor_operators"] != [
        "Delta_2_perp(4)",
        "Delta_0(-4)",
        "Delta_2_perp(2)",
        "Delta_1_perp(-3)",
    ] or contract["physical_input_status"] != "NOT_SUPPLIED":
        raise ValueError("full-BV composer contract drifted")
    receipt = value["composer_mechanics"]["synthetic_receipt"]
    if (
        receipt["status"] != "COMPOSED_LEDGER_SEMANTICALLY_ACCEPTED"
        or receipt["target_signed_rank"] != 6
        or receipt["Z_exponent_weighted_rank"]
        != {"numerator": -3, "denominator": 1}
    ):
        raise ValueError("full-BV composer synthetic receipt drifted")
    mutations = value["composer_mechanics"]["mutation_receipts"]
    if len(mutations) != 4 or not all(row["rejected"] for row in mutations):
        raise ValueError("full-BV composer mutation battery drifted")
    for relative, digest in value["provenance"]["source_sha256"].items():
        if _sha256(ROOT / relative) != digest:
            raise ValueError(f"full-BV composer source hash drifted: {relative}")
    return value


def main() -> int:
    verify()
    print("independent full-BV ledger composer-readiness verifier: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
