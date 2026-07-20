#!/usr/bin/env python3
"""Certify the Berger-isotropy closure obstruction for the Ward cokernel."""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.berger_108_row_component_jet_contract import (
    Generator,
    Monomial,
    Scalar,
)
from closed_universe_observers.generate_berger_common_action_obstruction_module import (
    _echelon,
    _vector_add,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = (
    PACKAGE
    / "certificates/BERGER_WARD_COKERNEL_IRREP_CLOSURE_OBSTRUCTION.json"
)
PAYLOAD = (
    PACKAGE
    / "certificates/BERGER_WARD_COKERNEL_IRREP_CLOSURE_OBSTRUCTION_PAYLOAD.json"
)
SCHEMA = (
    PACKAGE
    / "schema/berger-ward-cokernel-irrep-closure-obstruction-v1.schema.json"
)
PAYLOAD_SCHEMA = (
    PACKAGE
    / "schema/berger-ward-cokernel-irrep-closure-obstruction-payload-v1.schema.json"
)
REPORT = (
    PACKAGE / "reports/berger-ward-cokernel-irrep-closure-obstruction.md"
)
DEPENDENCIES = {
    "component_contract": PACKAGE
    / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "obstruction_module": PACKAGE
    / "certificates/BERGER_COMMON_ACTION_OBSTRUCTION_MODULE.json",
    "obstruction_payload": PACKAGE
    / "certificates/BERGER_COMMON_ACTION_OBSTRUCTION_MODULE_PAYLOAD.json",
    "two_pair_no_go": PACKAGE
    / "certificates/BERGER_112_ROW_TWO_PAIR_EXTENSION_NO_GO.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_ward_cokernel_irrep_closure_obstruction.py",
    PACKAGE / "tests/test_berger_ward_cokernel_irrep_closure_obstruction.py",
    SCHEMA,
    PAYLOAD_SCHEMA,
]

WardKey = tuple[int, tuple[int, ...], int, tuple[int, ...]]
Coordinate = tuple[WardKey, Monomial]
Vector = dict[Coordinate, Scalar]
ZERO: Scalar = (Fraction(0), Fraction(0))
ONE: Scalar = (Fraction(1), Fraction(0))
ACTION_COLUMNS = ("z_00", "z_01", "z_10", "z_11")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def parse_coordinate(value: dict[str, Any]) -> Coordinate:
    left, left_word, right, right_word = value["ward_key"]
    monomial = tuple(
        (kind, name, tuple(vertical), tuple(spacetime))
        for kind, name, vertical, spacetime in value["coefficient_monomial"]
    )
    return (left, tuple(left_word), right, tuple(right_word)), monomial


def serialize_coordinate(value: Coordinate) -> dict[str, Any]:
    (left, left_word, right, right_word), monomial = value
    return {
        "ward_key": [left, list(left_word), right, list(right_word)],
        "coefficient_monomial": [
            [kind, name, list(vertical), list(spacetime)]
            for kind, name, vertical, spacetime in monomial
        ],
    }


def parse_scalar(value: list[list[int]]) -> Scalar:
    return tuple(Fraction(numerator, denominator) for numerator, denominator in value)


def _row_action() -> dict[int, tuple[tuple[int, int], ...]]:
    action: dict[int, tuple[tuple[int, int], ...]] = {
        55: (),
        56: ((57, 1),),
        57: ((56, -1),),
        58: (),
    }
    for base in (84, 90):
        action.update(
            {
                base: ((base + 1, 1),),
                base + 1: ((base, -1),),
                base + 2: (),
                base + 3: (),
                base + 4: ((base + 5, 1),),
                base + 5: ((base + 4, -1),),
            }
        )
    return action


ROW_ACTION = _row_action()


def coordinate_action(value: Coordinate) -> dict[Coordinate, int]:
    """Infinitesimal Berger U(1): J e1=e2 and J e2=-e1."""

    (left, left_word, right, right_word), monomial = value
    output: dict[Coordinate, int] = defaultdict(int)
    for target, coefficient in ROW_ACTION[left]:
        output[((target, left_word, right, right_word), monomial)] += coefficient
    for position, axis in enumerate(left_word):
        if axis == 1:
            word = left_word[:position] + (2,) + left_word[position + 1 :]
            output[((left, word, right, right_word), monomial)] += 1
        elif axis == 2:
            word = left_word[:position] + (1,) + left_word[position + 1 :]
            output[((left, word, right, right_word), monomial)] -= 1
    for target, coefficient in ROW_ACTION[right]:
        output[((left, left_word, target, right_word), monomial)] += coefficient
    for position, axis in enumerate(right_word):
        if axis == 1:
            word = right_word[:position] + (2,) + right_word[position + 1 :]
            output[((left, left_word, right, word), monomial)] += 1
        elif axis == 2:
            word = right_word[:position] + (1,) + right_word[position + 1 :]
            output[((left, left_word, right, word), monomial)] -= 1
    return {coordinate: coefficient for coordinate, coefficient in output.items() if coefficient}


def vector_action(value: Vector) -> Vector:
    output: Vector = {}
    for coordinate, scalar in value.items():
        for target, coefficient in coordinate_action(coordinate).items():
            output = _vector_add(
                output,
                {target: (coefficient * scalar[0], coefficient * scalar[1])},
            )
    return output


def vector_scale(value: Vector, factor: Fraction) -> Vector:
    return {
        coordinate: (factor * scalar[0], factor * scalar[1])
        for coordinate, scalar in value.items()
        if scalar != ZERO
    }


def closure(seed: set[Coordinate]) -> set[Coordinate]:
    result = set(seed)
    queue = deque(seed)
    while queue:
        coordinate = queue.popleft()
        for target in coordinate_action(coordinate):
            if target not in result:
                result.add(target)
                queue.append(target)
    return result


def connected_blocks(coordinates: list[Coordinate]) -> list[list[Coordinate]]:
    universe = set(coordinates)
    adjacency: dict[Coordinate, set[Coordinate]] = {
        coordinate: set() for coordinate in coordinates
    }
    for coordinate in coordinates:
        for target in coordinate_action(coordinate):
            if target in universe:
                adjacency[coordinate].add(target)
                adjacency[target].add(coordinate)
    blocks = []
    unseen = set(coordinates)
    while unseen:
        start = min(unseen)
        block = {start}
        queue = deque([start])
        unseen.remove(start)
        while queue:
            current = queue.popleft()
            for target in adjacency[current]:
                if target in unseen:
                    unseen.remove(target)
                    block.add(target)
                    queue.append(target)
        blocks.append(sorted(block))
    return blocks


def block_matrix(block: list[Coordinate]) -> sp.Matrix:
    index = {coordinate: row for row, coordinate in enumerate(block)}
    matrix = sp.zeros(len(block))
    for column, coordinate in enumerate(block):
        for target, coefficient in coordinate_action(coordinate).items():
            matrix[index[target], column] += coefficient
    return matrix


def isotypic_decomposition(coordinates: list[Coordinate]) -> dict[int, int]:
    dimensions: dict[int, int] = defaultdict(int)
    for block in connected_blocks(coordinates):
        matrix = block_matrix(block)
        for weight in range(5):
            operator = (
                matrix
                if weight == 0
                else matrix * matrix + weight * weight * sp.eye(len(block))
            )
            nullity = len(block) - operator.rank()
            if nullity:
                dimensions[weight] += nullity
    return dict(sorted(dimensions.items()))


def _load_vectors(document: dict[str, Any], coordinates: list[Coordinate]) -> dict[str, Vector]:
    return {
        name: {
            coordinates[index]: parse_scalar(scalar)
            for index, scalar in entries
        }
        for name, entries in document["vectors"].items()
    }


def cyclic_vectors(value: Vector) -> list[Vector]:
    output = []
    current = value
    for _ in range(5):
        output.append(current)
        current = vector_action(current)
    return output


def build_payload() -> tuple[dict[str, Any], dict[str, Any]]:
    old_payload = json.loads(DEPENDENCIES["obstruction_payload"].read_text())
    seed_coordinates = [
        parse_coordinate(value) for value in old_payload["coordinate_basis"]
    ]
    seed = set(seed_coordinates)
    complete = sorted(closure(seed))
    index = {coordinate: position for position, coordinate in enumerate(complete)}
    generator_entries = [
        [
            column,
            [
                [index[target], coefficient]
                for target, coefficient in sorted(
                    coordinate_action(coordinate).items(),
                    key=lambda item: index[item[0]],
                )
            ],
        ]
        for column, coordinate in enumerate(complete)
        if coordinate_action(coordinate)
    ]
    payload = {
        "schema": "closed-universe-berger-ward-cokernel-irrep-closure-obstruction-payload-v1",
        "result_id": "BERGER_WARD_COKERNEL_IRREP_CLOSURE_OBSTRUCTION_PAYLOAD",
        "generator": {
            "id": "J_Berger_U1",
            "convention": "J(e1)=e2, J(e2)=-e1; e0,e3 fixed",
            "component_action": (
                "(A1,A2), (K01,K02), and (K13,K23) are standard real "
                "weight-one doublets; A0,A3,K03,K12 are fixed"
            ),
            "coefficient_action": (
                "g_b and switch-specialized h_b vertical/temporal jets are scalars"
            ),
        },
        "original_coordinate_indices_in_closure": [index[value] for value in seed_coordinates],
        "closure_coordinate_basis": [
            serialize_coordinate(coordinate) for coordinate in complete
        ],
        "sparse_generator_columns": generator_entries,
    }
    audit = {
        "old_payload": old_payload,
        "seed_coordinates": seed_coordinates,
        "seed": seed,
        "complete": complete,
        "index": index,
    }
    return payload, audit


def build_certificate(payload: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    values = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    seed: set[Coordinate] = audit["seed"]
    complete: list[Coordinate] = audit["complete"]
    seed_coordinates: list[Coordinate] = audit["seed_coordinates"]
    vectors = _load_vectors(audit["old_payload"], seed_coordinates)
    escaping_basis = [
        coordinate
        for coordinate in seed
        if set(coordinate_action(coordinate)) - seed
    ]
    first_step_targets = set().union(
        *(
            set(coordinate_action(coordinate)) - seed
            for coordinate in seed
        )
    )
    escape_incidences = sum(
        sum(target not in seed for target in coordinate_action(coordinate))
        for coordinate in seed
    )
    if (
        len(seed),
        len(escaping_basis),
        len(first_step_targets),
        escape_incidences,
        len(complete),
    ) != (444, 392, 424, 848, 900):
        raise AssertionError("Berger representation-closure census drifted")

    decomposition = isotypic_decomposition(complete)
    if decomposition != {0: 460, 2: 424, 4: 16}:
        raise AssertionError(f"closure isotypic decomposition drifted: {decomposition}")
    emitter_decompositions = {}
    for emitter in ("g0", "g1"):
        sector = [
            coordinate
            for coordinate in complete
            if any(
                factor[0] == "parameter" and factor[1] == emitter
                for factor in coordinate[1]
            )
        ]
        sector_decomposition = isotypic_decomposition(sector)
        if len(sector) != 450 or sector_decomposition != {0: 230, 2: 212, 4: 8}:
            raise AssertionError("emitter-labelled isotypic sector drifted")
        emitter_decompositions[emitter] = {
            "dimension": len(sector),
            "isotypic_dimensions": {
                str(weight): dimension
                for weight, dimension in sector_decomposition.items()
            },
        }

    image = [vectors[name] for name in ACTION_COLUMNS]
    image_rank = len(_echelon(image)[0])
    image_actions = [vector_action(vector) for vector in image]
    if image_rank != 4 or any(image_actions):
        raise AssertionError("four-column action image ceased to be a trivial submodule")
    closure_cokernel = {
        0: decomposition[0] - image_rank,
        2: decomposition[2],
        4: decomposition[4],
    }

    source_types = {}
    for name in ("emitter_Diff_BV", "base_maxwell_typed", "source_total"):
        orbit = cyclic_vectors(vectors[name])
        rank = len(_echelon(orbit)[0])
        if name == "base_maxwell_typed":
            expected = {"0": 1}
            if vector_action(vectors[name]) or rank != 1:
                raise AssertionError("typed-Maxwell source ceased to be invariant")
        else:
            weight_zero = _vector_add(
                vectors[name],
                vector_scale(vector_action(vector_action(vectors[name])), Fraction(1, 4)),
            )
            weight_two = _vector_add(vectors[name], weight_zero, (Fraction(-1), Fraction(0)))
            if vector_action(weight_zero):
                raise AssertionError("source weight-zero projector drifted")
            if vector_action(vector_action(weight_two)) != vector_scale(
                weight_two, Fraction(-4)
            ):
                raise AssertionError("source weight-two projector drifted")
            expected = {"0": 1, "2": 2}
            if rank != 3:
                raise AssertionError("source cyclic module rank drifted")
        augmented = len(_echelon(image + orbit)[0])
        source_types[name] = {
            "cyclic_module_dimension": rank,
            "isotypic_dimensions": expected,
            "dimension_mod_action_image": augmented - image_rank,
        }

    module = values["obstruction_module"]
    decisive_index = module["complete_declared_source_pair_orbit"][
        "typed_maxwell_projection_recovery"
    ]["coordinate"]
    decisive = seed_coordinates[decisive_index]
    decisive_vector = {decisive: ONE}
    decisive_orbit = cyclic_vectors(decisive_vector)
    decisive_rank = len(_echelon(decisive_orbit)[0])
    decisive_augmented = len(_echelon(image + decisive_orbit)[0])
    second_action = vector_action(vector_action(decisive_vector))
    weight_zero = _vector_add(
        decisive_vector, vector_scale(second_action, Fraction(1, 4))
    )
    weight_two = _vector_add(
        decisive_vector, weight_zero, (Fraction(-1), Fraction(0))
    )
    if (
        decisive_rank != 3
        or decisive_augmented - image_rank != 3
        or vector_action(weight_zero)
        or vector_action(vector_action(weight_two))
        != vector_scale(weight_two, Fraction(-4))
    ):
        raise AssertionError("decisive coordinate orbit decomposition drifted")
    if weight_zero[decisive] != (Fraction(1, 2), Fraction(0)) or weight_two[
        decisive
    ] != (Fraction(1, 2), Fraction(0)):
        raise AssertionError("decisive coordinate projector coefficient drifted")

    payload_rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": "closed-universe-berger-ward-cokernel-irrep-closure-obstruction-v1",
        "result_id": "BERGER_WARD_COKERNEL_IRREP_CLOSURE_OBSTRUCTION",
        "setting_id": values["component_contract"]["setting_id"],
        "claim_status": "OBSTRUCTED_444_WARD_SPACE_NOT_BERGER_REPRESENTATION_CLOSED",
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name].get("result_id", path.stem),
                "sha256": sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": hashlib.sha256(payload_rendered.encode()).hexdigest(),
            "canonical_sha256": canonical_sha256(payload),
        },
        "residual_action_definition": payload["generator"],
        "original_444_space_gate": {
            "dimension": len(seed),
            "escaping_basis_vector_count": len(escaping_basis),
            "distinct_first_step_outside_coordinate_count": len(first_step_targets),
            "nonzero_escape_incidence_count": escape_incidences,
            "invariant_under_J_Berger_U1": False,
            "four_dimensional_action_image_invariant": True,
            "induced_action_on_440_cokernel_exists": False,
            "theorem": (
                "Because J(W_444) is not contained in W_444 while the action "
                "image lies inside W_444, no Berger U(1) action descends to "
                "W_444/im(Phi). Therefore the certified 440-dimensional "
                "vector-space cokernel has no intrinsic Berger irrep or "
                "isotypic decomposition."
            ),
        },
        "minimal_representation_closure": {
            "dimension": len(complete),
            "added_coordinate_count": len(complete) - len(seed),
            "connected_block_count": len(connected_blocks(complete)),
            "maximum_connected_block_dimension": max(
                map(len, connected_blocks(complete))
            ),
            "isotypic_dimensions": {
                str(weight): dimension for weight, dimension in decomposition.items()
            },
            "irreducible_copy_counts": {
                "weight_0_real_lines": decomposition[0],
                "weight_2_real_planes": decomposition[2] // 2,
                "weight_4_real_planes": decomposition[4] // 2,
            },
            "emitter_label_sectors": emitter_decompositions,
        },
        "action_image_and_closed_cokernel": {
            "action_image_dimension": image_rank,
            "action_image_type": {"weight_0": 4},
            "minimal_closed_cokernel_dimension": len(complete) - image_rank,
            "minimal_closed_cokernel_isotypic_dimensions": {
                str(weight): dimension
                for weight, dimension in closure_cokernel.items()
            },
            "warning": (
                "the 896-dimensional closed quotient is a replacement carrier, "
                "not an implicit promotion or reinterpretation of the 440-dimensional cokernel"
            ),
        },
        "source_pair_orbit_types": source_types,
        "witness_location": {
            "normalization_H_equals_2": {
                "module": "separate one-dimensional valuation cokernel",
                "Berger_type": "weight_0 trivial line",
                "projection": 1,
            },
            "typed_Maxwell_source_class": {
                "module": "minimal closed Ward cokernel",
                "Berger_type": "weight_0 trivial line",
                "dimension_mod_action_image": source_types[
                    "base_maxwell_typed"
                ]["dimension_mod_action_image"],
                "coordinate_display": "-2 g0 h0",
            },
            "display_coordinate_orbit": {
                "cyclic_module_dimension": decisive_rank,
                "isotypic_dimensions": {"0": 1, "2": 2},
                "dimension_mod_action_image": decisive_augmented - image_rank,
                "weight_0_projector": "P0=(J^2+4 I)/4",
                "weight_2_projector": "P2=-J^2/4",
                "display_coordinate_fraction_in_each_projector": "1/2",
                "interpretation": (
                    "the isolated coordinate is not an invariant witness; "
                    "the complete typed-Maxwell source vector is the invariant obstruction class"
                ),
            },
        },
        "representation_content_theorem": {
            "module_level_necessary_and_sufficient_condition": (
                "An equivariant extension reaches the complete typed-Maxwell "
                "obstruction class iff its new Ward image contains that "
                "weight-zero line."
            ),
            "minimal_new_isotypic_content": "one additional weight-0 real line",
            "Hessian_support_condition": (
                "a generator of that line must be independent of the four "
                "existing metric-natural image lines and have nonzero "
                "A_0--K_12 component projection"
            ),
            "pure_weight_2_or_weight_4_channel": "INSUFFICIENT",
            "more_trivial_scalar_pairs_with_old_tensor": (
                "INSUFFICIENT_BY_BERGER_112_ROW_TWO_PAIR_EXTENSION_NO_GO"
            ),
            "action_level_sufficiency": (
                "NO_CERTIFIED_MAP: a representation-complete auxiliary "
                "Hessian domain and action differentiation map have not been declared"
            ),
        },
        "candidate_family_disposition": {
            "requested_440_irrep_decomposition": "OBSTRUCTED_NOT_A_MODULE",
            "minimal_900_coordinate_closure": "CERTIFIED",
            "minimal_896_dimensional_closed_cokernel": "CERTIFIED_REPLACEMENT_ONLY",
            "one_pure_nontrivial_weight_channel": "PROVED_INSUFFICIENT",
            "complete_minimal_action_tensor_channel": "OPEN",
        },
        "mutations": {
            "drop_one_escape_target": {
                "closure_test_fails": True,
                "detected": True,
            },
            "project_outside_coordinates_to_zero": {
                "scientific_status": (
                    "REJECTED_NONCANONICAL_PROJECTED_ACTION; not a representation repair"
                ),
                "detected": True,
            },
            "delete_one_action_image_column": {
                "image_rank_after_mutation": 3,
                "detected": True,
            },
            "replace_display_coordinate_by_weight_zero_projector": {
                "cyclic_dimension_after_mutation": 1,
                "detected": True,
            },
        },
        "proof_obligation_dag": [
            {"id": "P1_DECLARE_BERGER_U1_ACTION", "status": "CERTIFIED"},
            {"id": "P2_TEST_444_SPACE_CLOSURE", "status": "OBSTRUCTED"},
            {"id": "P3_MINIMAL_REPRESENTATION_CLOSURE", "status": "CERTIFIED"},
            {"id": "P4_CLOSURE_ISOTYPIC_DECOMPOSITION", "status": "CERTIFIED"},
            {"id": "P5_ACTION_IMAGE_AND_SOURCE_TYPES", "status": "CERTIFIED"},
            {"id": "P6_INVARIANT_WITNESS_LOCATION", "status": "CERTIFIED"},
            {
                "id": "P7_COMPLETE_ACTION_HESSIAN_CHANNEL",
                "status": "NO_CERTIFIED_MAP",
            },
        ],
        "activation_disposition": {
            "minimal_tensor_channel_common_action_exists": False,
            "observer_q1_q2_carrier_freeze_authorized": False,
            "q3_authorized": False,
            "detector_or_causal_promotion_authorized": False,
            "branch_particle_positivity_or_quantum_promotion_authorized": False,
        },
        "next_gate": (
            "DECLARE_A_REPRESENTATION_COMPLETE_A_K_HESSIAN_DOMAIN_ON_THE_"
            "900_COORDINATE_CLOSURE_AND_COMPUTE_ITS_ACTION_TO_WARD_IMAGE"
        ),
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE result tests whether the "
            "certified 444-dimensional old-A--K Ward coefficient space and "
            "its 440-dimensional vector-space cokernel carry the Berger "
            "stabilizer representation required by the requested irrep "
            "decomposition. The declared infinitesimal U(1) generator sends "
            "e1 to e2 and e2 to -e1, rotates the A1/A2, K01/K02 and K13/K23 "
            "component doublets, fixes A0,A3,K03,K12, and treats the "
            "switch-specialized formal coefficient monomials as scalars. "
            "Exact application to all 444 basis coordinates finds 392 "
            "escaping basis directions, 424 distinct first-step outside "
            "coordinates and 848 nonzero escape incidences. Thus the "
            "four-dimensional action image is an invariant trivial submodule, "
            "but the ambient 444-space is not a module and no action descends "
            "to its 440-dimensional cokernel. Calling a raw basis grouping an "
            "irrep decomposition would therefore be false. The unique minimal "
            "coordinate closure has dimension 900 and exact real isotypic "
            "dimensions 460 at weight zero, 424 at weight two and 16 at weight "
            "four; each emitter-labelled half has dimensions 230,212,8. "
            "Quotienting the unchanged four trivial action-image lines gives "
            "a new 896-dimensional representation carrier with isotypic "
            "dimensions 456,424,16. This replacement is not identified with "
            "the prior 440-dimensional cokernel. The H=2 valuation class is a "
            "separate trivial line. The complete typed-Maxwell source vector "
            "is an invariant trivial obstruction line independent of the "
            "action image, while its displayed -2 g0 h0 coordinate alone "
            "generates a three-dimensional weight-zero plus weight-two orbit "
            "and is not itself invariant. At representation level, reaching "
            "the full typed source class is equivalent to adding one new "
            "trivial image line, independent of the four existing lines and "
            "with nonzero A_0--K_12 projection; pure weight-two or weight-four "
            "channels are insufficient. This does not construct an action "
            "Hessian: the representation-complete Hessian domain and its "
            "action-to-Ward differentiation map are missing, so action-level "
            "sufficiency and a common-action carrier remain NO_CERTIFIED_MAP. "
            "No projected action, fitted cancellation, outer scalar jet, q3, "
            "detector, causal, branch, particle, positivity, Conflux or "
            "quantum claim is made, and no compact-product mode is identified "
            "with a Berger row."
        ),
        "provenance": {
            "science_forge_work_item": (
                "sf:program/work/observer-ward-cokernel-irrep-decomposition"
            ),
            "input_commit": "abfbe54dc3839ef9d61685d2858720d652df39cd",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def report(value: dict[str, Any]) -> str:
    gate = value["original_444_space_gate"]
    closed = value["minimal_representation_closure"]
    return f"""# Berger Ward-cokernel representation-closure obstruction

## First obstruction

The certified 444-coordinate old-`A`--`K` Ward space is not a Berger
`U(1)` module.  Under the exact stabilizer generator

```text
J(e1)=e2,  J(e2)=-e1,
```

`{gate['escaping_basis_vector_count']}` basis directions leave the space,
through `{gate['nonzero_escape_incidence_count']}` nonzero incidences.
Although the four-dimensional action image is invariant, no action descends
to the 440-dimensional vector-space cokernel.  It therefore has no intrinsic
Berger irrep decomposition.

## Minimal closed replacement

The unique coordinate closure has dimension `{closed['dimension']}` and real
isotypic dimensions

```text
weight 0: 460
weight 2: 424
weight 4: 16.
```

The four action columns are trivial lines, so the closed replacement quotient
has dimension 896 and isotypic dimensions `(456,424,16)`.  This is a new
representation carrier, not a relabelling of the old 440-dimensional
cokernel.

`H=2` lies in its separate valuation trivial line.  The complete typed-Maxwell
source vector is also a nonzero trivial class.  The displayed
`-2 g0 h0` coordinate alone is not invariant: its cyclic module is one
weight-zero line plus one real weight-two plane.

## Representation content

At module level, an equivariant extension reaches the typed obstruction
exactly when its image contains that new trivial line.  Thus the minimal new
content is one additional invariant scalar tensor channel, independent of the
four existing metric-natural image lines and with nonzero `A_0--K_12`
projection.  Pure weight-two or weight-four channels cannot suffice.

Action-level sufficiency remains fail-closed because no
representation-complete auxiliary Hessian domain on the 900-coordinate
closure has been declared or differentiated.

CLOSE-OUT: OBSTRUCTED — the requested 440-dimensional irrep decomposition is undefined because the certified coefficient space is not representation closed
EVIDENCE: closed_universe_observers/certificates/BERGER_WARD_COKERNEL_IRREP_CLOSURE_OBSTRUCTION.json
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload, audit = build_payload()
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(payload_schema).validate(payload)
    value = build_certificate(payload, audit)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered_payload = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    rendered_report = report(value)
    if args.emit:
        PAYLOAD.write_text(rendered_payload)
        CERTIFICATE.write_text(rendered)
        REPORT.write_text(rendered_report)
    if args.check and (
        not PAYLOAD.exists()
        or PAYLOAD.read_text() != rendered_payload
        or not CERTIFICATE.exists()
        or CERTIFICATE.read_text() != rendered
        or not REPORT.exists()
        or REPORT.read_text() != rendered_report
    ):
        raise SystemExit("stale Berger Ward-cokernel representation closure")
    print("BERGER_WARD_COKERNEL_IRREP_CLOSURE_OBSTRUCTION generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
