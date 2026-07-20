#!/usr/bin/env python3
"""Independent verifier for the cutoff Volterra orientation reduction."""

from __future__ import annotations

from copy import deepcopy
import json

from local_bv.schema_validation import validate_instance

from .berger_cutoff_volterra_microlocal_orientation_reduction import (
    validate,
)
from .berger_cutoff_volterra_microlocal_orientation_reduction_certificate import (
    HERE,
    OUTPUT,
)


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads(
        (
            HERE
            / "schema/berger-cutoff-volterra-microlocal-orientation-reduction-v1.schema.json"
        ).read_text()
    )
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    validate(certificate)
    finite = certificate["finite_term_orientation"]
    for sign, key, ray in (
        ("PLUS", "plus", "R_PLUS"),
        ("MINUS", "minus", "R_MINUS"),
    ):
        tower = finite[key]
        expected_relation = ["DELTA", ray]
        if (
            tower["sign"] != sign
            or tower["Gamma"] != expected_relation
            or not all(tower["induction"].values())
            or any(
                row["relation"] != expected_relation
                or row["contained_in_Gamma"] is not True
                or row["order"] != index
                for index, row in enumerate(tower["sampled_terms"])
            )
        ):
            raise ValueError(f"independent {sign} finite-term audit mismatch")
    negative = certificate["negative_control"]
    if (
        negative["contains_mixed_direction"] is not True
        or negative["contained_in_one_oriented_Gamma"] is not False
        or negative["relation"]
        != ["DELTA", "MIXED_DIRECTION", "R_MINUS", "R_PLUS"]
    ):
        raise ValueError("mixed-side negative control mismatch")
    gate = certificate["infinite_series_gate"]
    if gate["gate_passes"]:
        raise ValueError("open Hörmander convergence gate was promoted")
    if (
        not all(gate["conditional_replay"]["conditions"].values())
        or not all(
            gate["conditional_replay"]["conditional_conclusions"].values()
        )
    ):
        raise ValueError("conditional convergence implication failed")
    mutant = deepcopy(certificate)
    mutant["claim_flags"][
        "BERGER_CUTOFF_COMPANION_PAULI_JORDAN_ORIENTATION_EXCLUSION"
    ] = True
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("uncertified infinite-series orientation was accepted")
    return certificate


def main() -> int:
    verify()
    print(
        "BERGER CUTOFF VOLTERRA MICROLOCAL ORIENTATION REDUCTION "
        "independent verification: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
