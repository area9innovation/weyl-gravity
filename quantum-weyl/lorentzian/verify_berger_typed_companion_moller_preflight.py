#!/usr/bin/env python3
"""Independent replay for the typed companion Møller preflight."""

from __future__ import annotations

from copy import deepcopy
import json

from local_bv.schema_validation import validate_instance

from .berger_typed_companion_moller_preflight import triangular_replay, validate
from .berger_typed_companion_moller_preflight_certificate import HERE, OUTPUT


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads(
        (HERE / "schema/berger-typed-companion-moller-preflight-v1.schema.json").read_text()
    )
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    validate(certificate)
    if certificate["typed_transport"]["checks"] != triangular_replay()["checks"]:
        raise ValueError("independent noncommutative replay mismatch")

    mutant = deepcopy(certificate)
    mutant["claim_flags"]["BERGER_TYPED_COMPANION_DISTRIBUTIONAL_TRANSPORT"] = True
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("distributional transport mutation was accepted")
    return certificate


def main() -> int:
    verify()
    print("BERGER TYPED COMPANION MOLLER PREFLIGHT independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
