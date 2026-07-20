#!/usr/bin/env python3
"""Independent verifier for the dilation restriction audit."""

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
    from .berger_dilation_retained26_restriction_audit import (
        DEPENDENCIES,
        canonical_summand_replay,
        graph_restriction_contract,
        validate,
    )
    from .berger_dilation_retained26_restriction_audit_certificate import (
        HERE,
        OUTPUT,
        build_certificate,
    )
except ImportError:
    from berger_dilation_retained26_restriction_audit import (
        DEPENDENCIES,
        canonical_summand_replay,
        graph_restriction_contract,
        validate,
    )
    from berger_dilation_retained26_restriction_audit_certificate import (
        HERE,
        OUTPUT,
        build_certificate,
    )


def verify() -> dict[str, object]:
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    if payload != build_certificate():
        raise ValueError("retained-26 restriction audit does not reproduce")
    schema = json.loads(
        (
            HERE
            / "schema/berger-dilation-retained26-restriction-audit-v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    errors = validate_instance(payload, schema)
    if errors:
        raise ValueError(f"retained-26 restriction schema failed: {errors}")
    validate(payload)
    for name, path in DEPENDENCIES.items():
        ref = payload["dependency_refs"][name]
        if ref["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"retained-26 restriction dependency drift: {name}")
    replay = canonical_summand_replay()
    if (
        not replay["all_pass"]
        or replay["first_summand"]["pairing_rank_in_block_replay"] != 0
        or replay["second_summand"]["pairing_rank_in_block_replay"] != 0
    ):
        raise ValueError("independent canonical-summand replay failed")
    if graph_restriction_contract()["retained_26_covariance_ready"]:
        raise ValueError("empty graph contract was accepted")
    mutant = deepcopy(payload)
    mutant["claim_flags"]["BERGER_54_ROW_BRST_HADAMARD"] = True
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("54-row Hadamard overpromotion was accepted")
    return payload


def main() -> int:
    verify()
    print("BERGER DILATION TO RETAINED-26 independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
