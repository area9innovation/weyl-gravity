#!/usr/bin/env python3
"""Independent verifier for the retained-26 Ward reduction."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

try:
    from local_bv.schema_validation import validate_instance
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from local_bv.schema_validation import validate_instance

try:
    from .berger_retained26_hadamard_ward_reduction import (
        DEPENDENCIES,
        support_class_audit,
        validate,
        ward_reduction_replay,
    )
    from .berger_retained26_hadamard_ward_reduction_certificate import (
        HERE,
        OUTPUT,
        build_certificate,
    )
except ImportError:
    from berger_retained26_hadamard_ward_reduction import (
        DEPENDENCIES,
        support_class_audit,
        validate,
        ward_reduction_replay,
    )
    from berger_retained26_hadamard_ward_reduction_certificate import (
        HERE,
        OUTPUT,
        build_certificate,
    )


def verify() -> dict[str, object]:
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    if payload != build_certificate():
        raise ValueError("retained-26 Ward certificate does not reproduce")
    schema = json.loads(
        (
            HERE
            / "schema/berger-retained26-hadamard-ward-reduction-v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    errors = validate_instance(payload, schema)
    if errors:
        raise ValueError(f"retained-26 Ward schema failed: {errors}")
    validate(payload)
    for name, path in DEPENDENCIES.items():
        if payload["dependency_refs"][name]["sha256"] != hashlib.sha256(
            path.read_bytes()
        ).hexdigest():
            raise ValueError(f"retained-26 Ward dependency drift: {name}")
    if not ward_reduction_replay()["all_pass"]:
        raise ValueError("Ward formula replay failed")
    if not support_class_audit()["all_pass"]:
        raise ValueError("support-class audit replay failed")
    mutant = deepcopy(payload)
    mutant["claim_flags"]["BERGER_26_ROW_BRST_HADAMARD"] = True
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("BRST Hadamard overpromotion was accepted")
    return payload


def main() -> int:
    verify()
    print("BERGER RETAINED-26 HADAMARD WARD independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
