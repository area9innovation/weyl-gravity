#!/usr/bin/env python3
"""Independent verifier for the cutoff microlocal response preflight."""

from __future__ import annotations

from copy import deepcopy
import json

from local_bv.schema_validation import validate_instance

from .berger_cutoff_companion_microlocal_response_preflight import (
    orientation_sector_replay,
    regularity_replay,
    validate,
)
from .berger_cutoff_companion_microlocal_response_preflight_certificate import (
    HERE,
    OUTPUT,
)


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads(
        (HERE / "schema/berger-cutoff-companion-microlocal-response-preflight-v1.schema.json").read_text()
    )
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    validate(certificate)
    if orientation_sector_replay() != certificate["orientation_sector_ledger"]:
        raise ValueError("independent orientation replay mismatch")
    expected_regularity = regularity_replay()
    for key in ("map", "cutoff_eta", "support_input", "conditions", "all_pass"):
        if certificate["regular_timeslice_source_map"][key] != expected_regularity[key]:
            raise ValueError("independent regularity replay mismatch")

    mutant = deepcopy(certificate)
    mutant["claim_flags"]["BERGER_REGULAR_GREENHYP_MORPHISM"] = True
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("uncertified GreenHyp response morphism was accepted")
    return certificate


def main() -> int:
    verify()
    print("BERGER CUTOFF MICROLOCAL RESPONSE PREFLIGHT independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
