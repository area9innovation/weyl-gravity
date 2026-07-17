#!/usr/bin/env python3
"""Independent verifier for the super-cotangent redefinition convention."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/BERGER_SUPER_COTANGENT_REDEFINITION_CONVENTION_V1.json"


def main() -> None:
    value = json.loads(CERT.read_text())
    replay = value["scientific_replay"]
    records = replay["generated_seed_records"]
    if replay["all_64_rows_match"] is not True or len(records) != 12:
        raise ValueError("complete shear replay receipt is absent")
    by_role = {}
    for record in records:
        by_role.setdefault(record["role"], []).append(record["coefficient"])
    if by_role != {
        "base": ["-2"] * 4,
        "odd_input_dual": ["-2"] * 4,
        "even_input_dual": ["2"] * 4,
    }:
        raise ValueError("odd/even cotangent sign ledger drifted")
    if replay["odd_sign_omission_mutation_defect_rows"] != [49, 50, 51, 52]:
        raise ValueError("odd-sign mutation localization drifted")
    for relative, digest in value["provenance"]["source_manifest"].items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual != digest:
            raise ValueError(f"source hash drifted: {relative}")
    flags = value["claim_flags"]
    if flags["SUPER_COTANGENT_SIGN_CONVENTION_CERTIFIED"] is not True or any(
        flags[name] is not False
        for name in (
            "FULL_BV_ELL3_REDEFINITION_COMPUTED",
            "CYCLIC_DEFORMATION_CLASS_DECIDED",
            "QUANTUM_CLAIM",
        )
    ):
        raise ValueError("claim boundary drifted")
    print("BERGER_SUPER_COTANGENT_REDEFINITION_CONVENTION_V1 verification: PASS")


if __name__ == "__main__":
    main()
