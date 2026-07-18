"""Independent verifier for the standard round-S4 zero-mode ledger."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/ROUND_S4_STANDARD_FACTOR_ZERO_MODE_LEDGER.json"
SCHEMA = HERE / "schema/round-s4-standard-factor-zero-mode-ledger-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rows = {row["factor_id"]: row for row in value["factor_zero_mode_ledger"]}
    counts = {name: row["zero_mode_dimension"] for name, row in rows.items()}
    if counts != {
        "physical_depth_0": 0,
        "ghost_depth_0": 5,
        "physical_depth_1": 0,
        "ghost_depth_1": 10,
    }:
        raise ValueError("standard factor zero-mode dimensions drifted")
    if rows["ghost_depth_0"]["spectrum"]["zero_levels"] != [1] or rows["ghost_depth_1"]["spectrum"]["zero_levels"] != [1]:
        raise ValueError("ghost zero-mode levels drifted")
    match = value["reducibility_match"]
    if (
        match["total_conformal_Killing_modes"] != 15
        or match["scalar_FP_kernel_at_Delta0_eigenvalue_4"]["kernel_vector_in_c_omega_coordinates"] != [1, 1]
        or value["negative_control"]["rejected"] is not True
    ):
        raise ValueError("conformal reducibility match drifted")
    for relative, digest in value["provenance"]["source_sha256"].items():
        if _sha256(ROOT / relative) != digest:
            raise ValueError(f"round-S4 zero-mode source hash drifted: {relative}")
    return value


def main() -> int:
    verify()
    print("independent round-S4 zero-mode verifier: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
