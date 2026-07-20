#!/usr/bin/env python3
"""Independently verify the temporal common-action Ward-orbit obstruction."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json

from jsonschema import Draft202012Validator

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.berger_108_row_component_jet_contract import (
    serialize,
)
from closed_universe_observers.generate_berger_108_row_arity_two_obstruction import (
    _q1_source_parts,
)
from closed_universe_observers.generate_berger_108_row_temporal_common_action_ward_orbit import (
    CERTIFICATE,
    DEPENDENCIES,
    PAYLOAD,
    PAYLOAD_SCHEMA,
    PRIOR_WITNESS_KEY,
    ROOT,
    SCHEMA,
)


def determinant3(matrix: list[list[int]]) -> int:
    return (
        matrix[0][0]
        * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1]
        * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2]
        * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--full",
        action="store_true",
        help="also replay the source-isolated PBW witness",
    )
    args = parser.parse_args()
    certificate = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    schema = json.loads(SCHEMA.read_text())
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(payload_schema).validate(payload)

    matrix = payload["normalization_compatibility"]["matrix"]
    assert matrix == [[1, 0, -2], [1, -1, 0], [0, 1, -1]]
    assert determinant3(matrix) == -1
    assert payload["normalization_compatibility"]["rank"] == 3
    assert payload["normalization_compatibility"]["nullity"] == 0
    assert (
        payload["normalization_compatibility"][
            "nondegenerate_common_action_pairing_exists"
        ]
        is False
    )
    mutation = payload["factor_two_mutation"]
    assert mutation["mutated_matrix"] == [[1, 0, -1], [1, -1, 0], [0, 1, -1]]
    assert determinant3(mutation["mutated_matrix"]) == 0
    assert mutation["mutated_null_vector"] == [1, 1, 1]
    assert mutation["detected"] is True

    assert certificate["payload_ref"]["sha256"] == hashlib.sha256(
        PAYLOAD.read_bytes()
    ).hexdigest()
    for name, reference in certificate["dependency_refs"].items():
        path = DEPENDENCIES[name]
        assert reference["path"] == str(path.relative_to(ROOT))
        assert reference["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()

    if args.full:
        q1 = _q1_source_parts()["emitter"]
        q2 = arity.load_q2(sources={"emitter_Diff_BV"})
        row = arity.arity_two_row(52, (0, 0), q1, q2, arity.parities())
        specialized = arity.specialize_bilinear_rows({52: row})[52]
        assert serialize(specialized[PRIOR_WITNESS_KEY]) == certificate[
            "persistent_witness"
        ]["current"]["coefficient"]
    else:
        witness = certificate["persistent_witness"]
        assert witness["identical_to_prior_first_witness"] is True
        assert (
            certificate["mutation_results"][
                "action_equivalent_Maxwell_presentation"
            ]["witness_survives"]
            is True
        )

    mode = "full" if args.full else "fast"
    print(
        "BERGER_108_ROW_TEMPORAL_COMMON_ACTION_WARD_ORBIT "
        f"independent verification ({mode}): PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
