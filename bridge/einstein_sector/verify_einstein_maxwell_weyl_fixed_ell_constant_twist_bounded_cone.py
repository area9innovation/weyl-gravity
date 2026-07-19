"""Independent verifier for the fixed-ell constant-twist bounded cone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_constant_twist_bounded_cone.json"


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema_path = ROOT / value["schema_path"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert hashlib.sha256(schema_path.read_bytes()).hexdigest() == value["schema_sha256"]
    for item in value["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]
    for neighbor in value["neighbor_output_ledger"].values():
        assert neighbor["all_input_shells_invertible"]
        assert neighbor["target_determinant"] == "nonzero scalar times target_p^2*target_q"
    assert value["complete_bounded_zero_locus"]["necessity_and_sufficiency"]
    assert value["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"] == "CERTIFIED"
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    print("EINSTEIN_MAXWELL_WEYL_FIXED_ELL_CONSTANT_TWIST_BOUNDED_CONE independent verification: PASS")


if __name__ == "__main__":
    main()
