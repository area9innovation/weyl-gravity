#!/usr/bin/env python3
"""Independently verify the common-action observable replay disposition."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_common_action_observable_replay_disposition import (
    CERTIFICATE,
    DEPENDENCIES,
    ROOT,
    SCHEMA,
)
from closed_universe_observers.verify_berger_ward_cokernel_irrep_closure_obstruction import (
    _coordinate,
    _decomposition,
    _rank,
    _scalar,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    dependencies = {}
    for name, reference in value["dependency_refs"].items():
        path = ROOT / reference["path"]
        assert path == DEPENDENCIES[name]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference["sha256"]
        dependencies[name] = json.loads(path.read_text())

    assert not dependencies["minimal_channel"]["activation_disposition"][
        "representation_complete_common_action_extension_exists"
    ]
    expected_statuses = {
        "two_record_poisson_algebra": dependencies["records"]["claim_status"],
        "leading_dynamical_emitter_rank_two": dependencies["rank_two"]["claim_status"],
        "g0_relational_redshift": dependencies["redshift"]["claim_status"],
        "absolute_g3_recoil_order": dependencies["recoil"]["claim_status"],
        "emitter_stress_clock_q2_ledger": dependencies["backreaction"]["claim_status"],
    }
    ledger = value["standalone_observable_survival_ledger"]
    assert {
        name: row["imported_claim_status"] for name, row in ledger.items()
    } == expected_statuses
    assert all(
        row["common_action_transport"] in {"NO_CERTIFIED_MAP", "OBSTRUCTED"}
        for row in ledger.values()
    )

    closure = [
        _coordinate(item)
        for item in dependencies["representation_payload"]["closure_coordinate_basis"]
    ]
    first = [
        coordinate
        for coordinate in closure
        if any(
            factor[0] == "profile" and factor[2] == (1,)
            for factor in coordinate[1]
        )
    ]
    assert len(first) == 108
    assert _decomposition(first) == {0: 60, 2: 48}
    old_payload = dependencies["obstruction_payload"]
    old_coordinates = [_coordinate(item) for item in old_payload["coordinate_basis"]]
    old = {
        name: {
            old_coordinates[index]: _scalar(scalar)
            for index, scalar in entries
        }
        for name, entries in old_payload["vectors"].items()
    }
    minimal = {
        name: {
            closure[index]: _scalar(scalar)
            for index, scalar in entries
        }
        for name, entries in dependencies["minimal_payload"][
            "ward_vectors_on_900_coordinate_closure"
        ].items()
    }
    image = [old[name] for name in ("z_00", "z_01", "z_10", "z_11")] + [
        minimal["epsilon_0"],
        minimal["epsilon_1"],
    ]
    project = lambda vector: {
        coordinate: coefficient
        for coordinate, coefficient in vector.items()
        if coordinate in set(first)
    }
    projected = [project(vector) for vector in image]
    source = project(minimal["typed_maxwell_source"])
    assert len(source) == 24
    assert _rank(projected, closure) == 2
    assert _rank(projected + [source], closure) == 3
    module = value["smallest_next_action_module"]
    assert module["source_vector_entries"] == [
        [
            closure.index(coordinate),
            [
                [coefficient[0].numerator, coefficient[0].denominator],
                [coefficient[1].numerator, coefficient[1].denominator],
            ],
        ]
        for coordinate, coefficient in sorted(
            source.items(), key=lambda item: closure.index(item[0])
        )
    ]
    assert not any(value["activation_disposition"].values())
    print(
        "BERGER_COMMON_ACTION_OBSERVABLE_REPLAY_DISPOSITION "
        "independent verification: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
