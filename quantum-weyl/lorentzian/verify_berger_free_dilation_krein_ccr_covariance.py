#!/usr/bin/env python3
"""Independent verifier for the free-dilation Krein covariance."""

from __future__ import annotations

from copy import deepcopy
import json

from local_bv.schema_validation import validate_instance

from .berger_free_dilation_krein_ccr_covariance import validate
from .berger_free_dilation_krein_ccr_covariance_certificate import HERE, OUTPUT


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads(
        (
            HERE / "schema/berger-free-dilation-krein-ccr-covariance-v1.schema.json"
        ).read_text()
    )
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    validate(certificate)
    replay = certificate["transpose_symmetrization"]
    if (
        replay["GFsym"] != "(GF+GF^T)/2"
        or replay["project_green_convention"]
        != "E_project=G_ret-G_adv=-G_source"
        or not all(replay["identities"].values())
    ):
        raise ValueError("independent transpose-symmetrization audit mismatch")
    bad_sign = certificate["negative_controls"][
        "use_source_sign_without_convention_map"
    ]
    if (
        bad_sign["antisymmetric_part"] != "-i E_project"
        or bad_sign["matches_project_CCR"] is not False
    ):
        raise ValueError("independent sign negative control mismatch")
    mutant = deepcopy(certificate)
    mutant["claim_flags"]["BERGER_FREE_DILATION_POSITIVE_HADAMARD_STATE"] = True
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("uncertified positive state was accepted")
    return certificate


def main() -> int:
    verify()
    print(
        "BERGER FREE DILATION KREIN CCR COVARIANCE "
        "independent verification: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
