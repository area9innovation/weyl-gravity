#!/usr/bin/env python3
"""Independent verifier for the companion Hadamard existence audit."""

from __future__ import annotations

from copy import deepcopy
import json

from local_bv.schema_validation import validate_instance

from .berger_companion_hadamard_existence_audit import DEPENDENCIES, _sha256, validate
from .berger_companion_hadamard_existence_audit_certificate import HERE, OUTPUT


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads(
        (HERE / "schema/berger-companion-hadamard-existence-audit-v1.schema.json").read_text()
    )
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    validate(certificate)
    for name, path in DEPENDENCIES.items():
        if certificate["dependency_refs"][name]["sha256"] != _sha256(path):
            raise ValueError(f"dependency hash mismatch: {name}")

    for path in (
        "literature_criterion.general_existence_from_decomposability_alone",
        "literature_criterion.theorem_5_3_applies_to_companion",
        "claim_flags.FEWSTER_GENERAL_EXISTENCE_THEOREM_APPLIES",
        "claim_flags.BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION",
        "claim_flags.BERGER_26_ROW_BRST_HADAMARD",
        "claim_flags.BERGER_54_ROW_BRST_HADAMARD",
        "claim_flags.BERGER_PHYSICAL_OBSERVABLE_POSITIVITY",
        "claim_flags.QUANTUM_CLAIM",
    ):
        mutant = deepcopy(certificate)
        cursor = mutant
        parts = path.split(".")
        for part in parts[:-1]:
            cursor = cursor[part]
        cursor[parts[-1]] = True
        try:
            validate(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"overpromotion mutation survived: {path}")
    return certificate


def main() -> int:
    verify()
    print("BERGER COMPANION HADAMARD EXISTENCE independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
