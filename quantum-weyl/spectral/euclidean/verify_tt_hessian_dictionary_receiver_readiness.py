"""Independent verifier for TT Hessian dictionary receiver readiness."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_RECEIVER_READINESS.json"
SCHEMA = HERE / "schema/repository-round-s4-tt-hessian-dictionary-receiver-readiness-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    contract = value["accepted_contract"]
    if (
        contract["required_kappa"] != {"numerator": 1, "denominator": 2}
        or contract["required_operator"]
        != "(1/2) Delta_2_perp(2) Delta_2_perp(4)"
        or contract["physical_input_status"] != "NOT_SUPPLIED"
    ):
        raise ValueError("TT Hessian receiver contract drifted")
    receipt = value["receiver_mechanics"]["synthetic_receipt"]
    if receipt["status"] != "SEMANTIC_RECEIVER_ACCEPTED" or receipt["Hessian_kernel_dimension"] != 0:
        raise ValueError("TT Hessian synthetic receiver receipt drifted")
    mutations = value["receiver_mechanics"]["mutation_receipts"]
    if len(mutations) != 4 or not all(row["rejected"] for row in mutations):
        raise ValueError("TT Hessian receiver mutation battery drifted")
    for relative, digest in value["provenance"]["source_sha256"].items():
        if _sha256(ROOT / relative) != digest:
            raise ValueError(f"TT Hessian receiver source hash drifted: {relative}")
    return value


def main() -> int:
    verify()
    print("independent TT Hessian dictionary receiver-readiness verifier: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
