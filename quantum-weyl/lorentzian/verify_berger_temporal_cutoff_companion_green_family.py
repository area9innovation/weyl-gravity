#!/usr/bin/env python3
"""Independent replay of the Berger temporal-cutoff Green family."""

from __future__ import annotations

import json

from local_bv.schema_validation import validate_instance

from .berger_temporal_cutoff_companion_green_family import (
    cutoff_specialization_replay,
    mutate_overpromotion,
    validate,
)
from .berger_temporal_cutoff_companion_green_family_certificate import HERE, OUTPUT


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads(
        (HERE / "schema/berger-temporal-cutoff-companion-green-family-v1.schema.json").read_text()
    )
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    validate(certificate)
    replay = cutoff_specialization_replay()
    if certificate["specialization_replay"]["checks"] != replay["checks"]:
        raise ValueError("independent cutoff specialization mismatch")
    negative = cutoff_specialization_replay(drop_time_dependence=True)
    if negative["all_pass"] or negative["checks"][
        "generic_theorem_accepts_cutoff_time_dependence"
    ]:
        raise ValueError("cutoff time-dependence negative control mismatch")
    try:
        validate(mutate_overpromotion(certificate))
    except ValueError:
        pass
    else:
        raise ValueError("cutoff wavefront promotion mutation was accepted")
    return certificate


def main() -> int:
    verify()
    print("BERGER TEMPORAL-CUTOFF COMPANION GREEN FAMILY independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
