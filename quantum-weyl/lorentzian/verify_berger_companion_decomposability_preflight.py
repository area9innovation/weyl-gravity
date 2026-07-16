#!/usr/bin/env python3
"""Independent verifier for the companion decomposability preflight."""

from __future__ import annotations

from copy import deepcopy
import json

from local_bv.schema_validation import validate_instance

from .berger_companion_decomposability_preflight import null_symbol_replay, validate
from .berger_companion_decomposability_preflight_certificate import HERE, OUTPUT


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads(
        (HERE / "schema/berger-companion-decomposability-preflight-v1.schema.json").read_text()
    )
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    validate(certificate)
    replay = null_symbol_replay(
        certificate["principal_symbol_analysis"]["null_symbol_replay"][
            "imported_null_fixture_rank"
        ]
    )
    if replay != certificate["principal_symbol_analysis"]["null_symbol_replay"]:
        raise ValueError("independent null-symbol replay mismatch")

    mutant = deepcopy(certificate)
    mutant["claim_flags"]["BERGER_COMPANION_NULL_CONE_DECOMPOSABLE"] = True
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("uncertified decomposability mutation was accepted")
    return certificate


def main() -> int:
    verify()
    print("BERGER COMPANION DECOMPOSABILITY PREFLIGHT independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
