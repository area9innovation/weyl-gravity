#!/usr/bin/env python3
"""Independent verifier for the cutoff companion Hermitian dilation."""

from __future__ import annotations

from copy import deepcopy
import json

from local_bv.schema_validation import validate_instance

from .berger_cutoff_companion_hermitian_dilation import (
    dilation_replay,
    endpoint_morphism_replay,
    validate,
)
from .berger_cutoff_companion_hermitian_dilation_certificate import HERE, OUTPUT


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads(
        (HERE / "schema/berger-cutoff-companion-hermitian-dilation-v1.schema.json").read_text()
    )
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    validate(certificate)
    expected = dilation_replay()
    for key in (
        "fibre_metric",
        "dilated_operator",
        "positive_metric_formal_adjoint",
        "H_conjugated_adjoint",
        "Green_operators",
        "checks",
        "all_pass",
    ):
        if certificate["Hermitian_dilation"][key] != expected[key]:
            raise ValueError("independent dilation replay mismatch")
    morphisms = endpoint_morphism_replay()
    for key in ("past_leg", "future_leg", "checks", "all_pass"):
        if certificate["regular_Cauchy_morphisms"][key] != morphisms[key]:
            raise ValueError("independent morphism replay mismatch")
    mutant = deepcopy(certificate)
    mutant["claim_flags"]["BERGER_DILATED_RESPONSE_MORPHISM_CONE_MAPPING"] = True
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("uncertified cone mapping was accepted")
    return certificate


def main() -> int:
    verify()
    print("BERGER CUTOFF COMPANION HERMITIAN DILATION independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
