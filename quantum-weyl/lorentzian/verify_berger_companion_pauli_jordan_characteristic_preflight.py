#!/usr/bin/env python3
"""Independent verifier for the Pauli--Jordan characteristic preflight."""

from __future__ import annotations

from copy import deepcopy
import json

from local_bv.schema_validation import validate_instance

from .berger_companion_pauli_jordan_characteristic_preflight import (
    orientation_sector_replay,
    validate,
)
from .berger_companion_pauli_jordan_characteristic_preflight_certificate import (
    HERE,
    OUTPUT,
)


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads(
        (HERE / "schema/berger-companion-pauli-jordan-characteristic-preflight-v1.schema.json").read_text()
    )
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    validate(certificate)
    if orientation_sector_replay() != certificate["orientation_sector_ledger"]:
        raise ValueError("independent orientation-sector replay mismatch")

    mutant = deepcopy(certificate)
    mutant["claim_flags"]["BERGER_COMPANION_NULL_CONE_DECOMPOSABLE"] = True
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("uncertified orientation exclusion was accepted")
    return certificate


def main() -> int:
    verify()
    print("BERGER PAULI-JORDAN CHARACTERISTIC PREFLIGHT independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
