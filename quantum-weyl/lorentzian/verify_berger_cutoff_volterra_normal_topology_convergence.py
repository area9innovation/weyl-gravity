#!/usr/bin/env python3
"""Independent verifier for cutoff Volterra normal convergence."""

from __future__ import annotations

from copy import deepcopy
import json

from local_bv.schema_validation import validate_instance

from .berger_cutoff_volterra_normal_topology_convergence import (
    majorant_ratio,
    seminorm_majorant,
    validate,
)
from .berger_cutoff_volterra_normal_topology_convergence_certificate import (
    HERE,
    OUTPUT,
)


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads(
        (
            HERE
            / "schema/berger-cutoff-volterra-normal-topology-convergence-v1.schema.json"
        ).read_text()
    )
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    validate(certificate)

    for r in range(7):
        for n in range(12):
            left = seminorm_majorant(n + 1, derivative_order=r)
            right = seminorm_majorant(n, derivative_order=r)
            if left != right * majorant_ratio(n, derivative_order=r):
                raise ValueError("exact seminorm-majorant ratio mismatch")
    if majorant_ratio(64, derivative_order=6) >= 1:
        raise ValueError("majorant ratio did not enter the convergent regime")

    mutant = deepcopy(certificate)
    mutant["claim_flags"]["BERGER_FULL_DILATION_HADAMARD_KREIN_COVARIANCE"] = True
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("uncertified transported covariance was accepted")
    return certificate


def main() -> int:
    verify()
    print(
        "BERGER CUTOFF VOLTERRA NORMAL TOPOLOGY "
        "independent verification: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
