#!/usr/bin/env python3
"""Independent verifier for the global ghost/identity Hadamard pair."""

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
    from .berger_ghost_identity_global_hadamard_pair import (
        DEPENDENCIES,
        endpoint_pullback_replay,
        ghost_identity_dilation_replay,
        validate,
    )
    from .berger_ghost_identity_global_hadamard_pair_certificate import (
        HERE,
        OUTPUT,
        build_certificate,
    )
except ImportError:
    from berger_ghost_identity_global_hadamard_pair import (
        DEPENDENCIES,
        endpoint_pullback_replay,
        ghost_identity_dilation_replay,
        validate,
    )
    from berger_ghost_identity_global_hadamard_pair_certificate import (
        HERE,
        OUTPUT,
        build_certificate,
    )


def verify() -> dict[str, object]:
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    if payload != build_certificate():
        raise ValueError("ghost/identity Hadamard certificate does not reproduce")
    schema = json.loads(
        (
            HERE
            / "schema/berger-ghost-identity-global-hadamard-pair-v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    errors = validate_instance(payload, schema)
    if errors:
        raise ValueError(f"ghost/identity Hadamard schema failed: {errors}")
    validate(payload)
    for name, path in DEPENDENCIES.items():
        if payload["dependency_refs"][name]["sha256"] != hashlib.sha256(
            path.read_bytes()
        ).hexdigest():
            raise ValueError(f"ghost/identity dependency drift: {name}")
    if not ghost_identity_dilation_replay()["all_pass"]:
        raise ValueError("ghost/identity dilation replay failed")
    if not endpoint_pullback_replay()["all_pass"]:
        raise ValueError("ghost/identity pullback replay failed")
    mutant = deepcopy(payload)
    mutant["claim_flags"]["BERGER_26_ROW_BRST_HADAMARD"] = True
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("q26 Ward overpromotion was accepted")
    return payload


def main() -> int:
    verify()
    print("BERGER GHOST/IDENTITY HADAMARD independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
