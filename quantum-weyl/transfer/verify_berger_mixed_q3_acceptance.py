#!/usr/bin/env python3
"""Fast independent verifier for the persisted mixed-q3 acceptance."""

from __future__ import annotations

import hashlib
import json

from local_bv.schema_validation import validate_instance

from .berger_mixed_q3_acceptance_certificate import OUTPUT, ROOT, SCHEMA, build


def verify() -> dict:
    value = json.loads(OUTPUT.read_text())
    errors = validate_instance(value, json.loads(SCHEMA.read_text()))
    if errors:
        raise ValueError("mixed q3 acceptance schema failure: " + "; ".join(errors))
    for path, expected in value["consumer_provenance"]["source_manifest"].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError(f"mixed q3 consumer source drifted: {path}")
    if value != build(run_scientific=False):
        raise ValueError("mixed q3 acceptance deterministic replay drifted")
    return value


if __name__ == "__main__":
    verify()
    print("BERGER_MIXED_Q3_INDEPENDENT_ACCEPTANCE verifier: PASS")
