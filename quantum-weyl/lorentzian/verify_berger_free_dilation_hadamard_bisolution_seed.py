#!/usr/bin/env python3
"""Independent verifier for the free-dilation Hadamard seed."""

from __future__ import annotations

from copy import deepcopy
import json

from local_bv.schema_validation import validate_instance

from .berger_free_dilation_hadamard_bisolution_seed import validate
from .berger_free_dilation_hadamard_bisolution_seed_certificate import (
    HERE,
    OUTPUT,
)


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads(
        (
            HERE
            / "schema/berger-free-dilation-hadamard-bisolution-seed-v1.schema.json"
        ).read_text()
    )
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    validate(certificate)
    operator = certificate["free_operator"]
    if (
        operator["dilation"] != "D_free=diag(C_free,C_free^dagger)"
        or operator["principal_symbol"] != "sigma_2(D_free)=q I40"
        or operator["fibre_form_signature"] != [20, 20]
    ):
        raise ValueError("independent free-operator audit mismatch")
    theorem = certificate["theorem_instantiation"]
    if (
        not all(theorem["hypotheses"].values())
        or not all(theorem["conclusions"].values())
        or theorem["selected_objects"]["Hadamard_bisolution"]
        != "omega_Dfree=-i(G_F,Dfree-G_adv,Dfree)"
    ):
        raise ValueError("independent theorem-instantiation audit mismatch")
    obstruction = certificate["positive_metric_obstruction"]
    if (
        obstruction["signature"] != [20, 20]
        or obstruction["positive_state_follows"] is not False
        or not all(obstruction["checks"].values())
    ):
        raise ValueError("independent positivity-boundary audit mismatch")
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
        "BERGER FREE DILATION HADAMARD BISOLUTION SEED "
        "independent verification: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
