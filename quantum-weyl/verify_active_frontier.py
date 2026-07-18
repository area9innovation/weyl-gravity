#!/usr/bin/env python3
"""Independent verifier for the active quantum-frontier certificate."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from jsonschema import Draft202012Validator

try:
    from .active_frontier import DEPENDENCIES, validate
    from .active_frontier_certificate import HERE, OUTPUT, build_certificate
except ImportError:
    from active_frontier import DEPENDENCIES, validate
    from active_frontier_certificate import HERE, OUTPUT, build_certificate


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads((HERE / "schema/active-frontier-v1.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    if certificate != build_certificate():
        raise ValueError("active frontier does not reproduce")
    for name, path in DEPENDENCIES.items():
        reference = certificate["dependency_refs"][name]
        if reference["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"active frontier dependency drifted: {name}")
    for key in (
        "GLOBAL_BRST_HADAMARD_STATE",
        "HADAMARD_EXISTENCE_THEOREM_APPLIES",
        "RANK_46_IS_QUANTUM_PREREQUISITE",
        "RANK_46_SUPPORT_LOCAL_PROJECTOR_CONSTRUCTED",
        "FULL_EXTENDED_BV_QME_RESTORED",
        "QME_RESTORED",
        "LORENTZIAN_QUANTUM_THEORY",
    ):
        mutant = deepcopy(certificate)
        mutant["claim_flags"][key] = True
        try:
            validate(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"active frontier overclaim accepted: {key}")
    for key in (
        "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX_CERTIFIED",
        "REPOSITORY_C2_COEFFICIENT_COMPUTED",
        "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED",
        "REGULATED_SLAVNOV_BREAKING_COMPUTED",
        "QME_OBSTRUCTED_STRICT_FIELD_CONTENT",
        "STANDARD_UNITARY_FREE_MATTER_CANCELLATION_OBSTRUCTED",
        "WZ_AFN0_PRIMITIVE_CERTIFIED",
    ):
        mutant = deepcopy(certificate)
        mutant["claim_flags"][key] = False
        try:
            validate(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"active frontier certified result dropped: {key}")
    return certificate


def main() -> int:
    verify()
    print("QUANTUM WEYL ACTIVE FRONTIER independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
