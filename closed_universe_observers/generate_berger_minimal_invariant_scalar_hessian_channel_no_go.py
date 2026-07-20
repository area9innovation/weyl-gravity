#!/usr/bin/env python3
"""Certify the minimal Berger-invariant scalar Hessian channel no-go."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers.berger_108_row_component_jet_contract import (
    Scalar,
    serialize,
)
from closed_universe_observers.generate_berger_108_row_emitter_physical_q2_pbw import (
    Action,
    Tensor,
    action_add,
    derivative,
    parameter,
    product,
    profile,
    rational,
    scale,
    tensor_add_symmetric,
)
from closed_universe_observers.generate_berger_110_row_conjugate_pair_extension_no_go import (
    CHI,
    CHI_PLUS,
    _dual_and_sign,
    extension_q1,
)
from closed_universe_observers.generate_berger_common_action_obstruction_module import (
    ACTION_COLUMN_ORDER,
    _echelon,
    _vector_add,
)
from closed_universe_observers.generate_berger_ward_cokernel_irrep_closure_obstruction import (
    parse_coordinate,
    parse_scalar,
    vector_action,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = (
    PACKAGE
    / "certificates/BERGER_MINIMAL_INVARIANT_SCALAR_HESSIAN_CHANNEL_NO_GO.json"
)
PAYLOAD = (
    PACKAGE
    / "certificates/BERGER_MINIMAL_INVARIANT_SCALAR_HESSIAN_CHANNEL_NO_GO_PAYLOAD.json"
)
SCHEMA = (
    PACKAGE
    / "schema/berger-minimal-invariant-scalar-hessian-channel-no-go-v1.schema.json"
)
PAYLOAD_SCHEMA = (
    PACKAGE
    / "schema/berger-minimal-invariant-scalar-hessian-channel-no-go-payload-v1.schema.json"
)
REPORT = (
    PACKAGE / "reports/berger-minimal-invariant-scalar-hessian-channel-no-go.md"
)
DEPENDENCIES = {
    "component_contract": PACKAGE
    / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "conjugate_pair_no_go": PACKAGE
    / "certificates/BERGER_110_ROW_CONJUGATE_PAIR_EXTENSION_NO_GO.json",
    "obstruction_module": PACKAGE
    / "certificates/BERGER_COMMON_ACTION_OBSTRUCTION_MODULE.json",
    "obstruction_payload": PACKAGE
    / "certificates/BERGER_COMMON_ACTION_OBSTRUCTION_MODULE_PAYLOAD.json",
    "representation_closure": PACKAGE
    / "certificates/BERGER_WARD_COKERNEL_IRREP_CLOSURE_OBSTRUCTION.json",
    "representation_payload": PACKAGE
    / "certificates/BERGER_WARD_COKERNEL_IRREP_CLOSURE_OBSTRUCTION_PAYLOAD.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_minimal_invariant_scalar_hessian_channel_no_go.py",
    PACKAGE / "tests/test_berger_minimal_invariant_scalar_hessian_channel_no_go.py",
    SCHEMA,
    PAYLOAD_SCHEMA,
]

Coordinate = tuple[arity.BilinearKey, tuple]
Vector = dict[Coordinate, Scalar]
ZERO: Scalar = (Fraction(0), Fraction(0))
ONE: Scalar = (Fraction(1), Fraction(0))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def minimal_action(emitter: int, *, tensor: str = "epsilon") -> Action:
    """Return chi g_b h_b T^ij (e_i A0)(e_j K_b12)."""

    if emitter not in (0, 1):
        raise ValueError("emitter must be zero or one")
    terms = {
        "epsilon": ((1, 2, 1), (2, 1, -1)),
        "delta": ((1, 1, 1), (2, 2, 1)),
        "symmetric_cross": ((1, 2, 1), (2, 1, 1)),
    }[tensor]
    k12 = 87 + 6 * emitter
    coefficient = product(parameter(f"g{emitter}"), profile(f"h{emitter}"))
    action: Action = {}
    for left_axis, right_axis, sign in terms:
        action_add(
            action,
            (
                (CHI, ()),
                (55, (left_axis,)),
                (k12, (right_axis,)),
            ),
            scale(coefficient, rational(sign)),
        )
    return action


def action_to_q2(action: Action) -> Tensor:
    """Differentiate one local cubic action through the signed odd pairing."""

    output: Tensor = {}
    for factors, coefficient in action.items():
        if len(factors) != 3:
            raise AssertionError("minimal channel action must be cubic")
        for position, varied in enumerate(factors):
            remaining = list(factors)
            remaining.pop(position)
            dual, pairing_sign = _dual_and_sign(varied[0])
            if not varied[1]:
                tensor_add_symmetric(
                    output,
                    dual,
                    remaining[0],
                    remaining[1],
                    scale(coefficient, rational(pairing_sign)),
                )
                continue
            axis, = varied[1]
            adjoint_sign = rational(-pairing_sign)
            tensor_add_symmetric(
                output,
                dual,
                remaining[0],
                remaining[1],
                scale(derivative(coefficient, axis), adjoint_sign),
            )
            tensor_add_symmetric(
                output,
                dual,
                (remaining[0][0], (axis, *remaining[0][1])),
                remaining[1],
                scale(coefficient, adjoint_sign),
            )
            tensor_add_symmetric(
                output,
                dual,
                remaining[0],
                (remaining[1][0], (axis, *remaining[1][1])),
                scale(coefficient, adjoint_sign),
            )
    return output


def ward_column(emitter: int, *, tensor: str = "epsilon") -> Vector:
    q2 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
    for (output, left, left_word, right, right_word), coefficient in (
        action_to_q2(minimal_action(emitter, tensor=tensor)).items()
    ):
        arity.add_bilinear_term(
            q2[(0, 0)].setdefault(output, {}),
            (left, left_word, right, right_word),
            coefficient,
        )
    row = arity.arity_two_row(
        52,
        (0, 0),
        {(0, 0): extension_q1(temporal_order=0)},
        q2,
        arity.parities() + (0, 1),
    )
    specialized = arity.specialize_bilinear_rows({52: row})[52]
    return {
        (key, monomial): coefficient
        for key, polynomial in specialized.items()
        if (key[0] in range(55, 59) and key[2] in range(84, 96))
        or (key[2] in range(55, 59) and key[0] in range(84, 96))
        for monomial, coefficient in polynomial.items()
    }


def _load_old_vectors(document: dict[str, Any]) -> tuple[list[Coordinate], dict[str, Vector]]:
    coordinates = [parse_coordinate(value) for value in document["coordinate_basis"]]
    vectors = {
        name: {
            coordinates[index]: parse_scalar(scalar)
            for index, scalar in entries
        }
        for name, entries in document["vectors"].items()
    }
    return coordinates, vectors


def _rank(columns: list[Vector]) -> int:
    return len(_echelon(columns)[0])


def _entries(vector: Vector, index: dict[Coordinate, int]) -> list[list[Any]]:
    return [
        [
            index[coordinate],
            [
                [coefficient[0].numerator, coefficient[0].denominator],
                [coefficient[1].numerator, coefficient[1].denominator],
            ],
        ]
        for coordinate, coefficient in sorted(
            vector.items(), key=lambda item: index[item[0]]
        )
    ]


def _q2_entries(tensor: Tensor) -> list[dict[str, Any]]:
    return [
        {
            "output": output,
            "left": [left, list(left_word)],
            "right": [right, list(right_word)],
            "coefficient": serialize(coefficient),
        }
        for (output, left, left_word, right, right_word), coefficient in sorted(
            tensor.items()
        )
    ]


def _action_entries(action: Action) -> list[dict[str, Any]]:
    return [
        {
            "factors": [[row, list(word)] for row, word in factors],
            "coefficient": serialize(coefficient),
        }
        for factors, coefficient in sorted(action.items())
    ]


def _profile_first_jet(coordinate: Coordinate) -> bool:
    return any(
        factor[0] == "profile" and factor[2] == (1,)
        for factor in coordinate[1]
    )


def _tensor_classification() -> dict[str, Any]:
    rotation = sp.Matrix([[0, -1], [1, 0]])
    a, b, c, d = sp.symbols("a b c d")
    tensor = sp.Matrix([[a, b], [c, d]])
    equations = list(rotation.T * tensor + tensor * rotation)
    matrix, _ = sp.linear_eq_to_matrix(equations, (a, b, c, d))
    invariant_nullspace = matrix.nullspace()
    reflection = sp.diag(1, -1)
    odd_equations = equations + list(reflection.T * tensor * reflection + tensor)
    odd_matrix, _ = sp.linear_eq_to_matrix(odd_equations, (a, b, c, d))
    odd_nullspace = odd_matrix.nullspace()
    if len(invariant_nullspace) != 2 or len(odd_nullspace) != 1:
        raise AssertionError("transverse invariant tensor classification drifted")
    return {
        "ambient_tensor_dimension": 4,
        "invariant_dimension": len(invariant_nullspace),
        "invariant_basis": ["delta_ij", "epsilon_ij"],
        "reflection_odd_invariant_dimension": len(odd_nullspace),
        "reflection_odd_basis": ["epsilon_ij"],
        "selected_tensor": [[0, 1], [-1, 0]],
    }


def build_payload() -> tuple[dict[str, Any], dict[str, Any]]:
    representation_payload = json.loads(
        DEPENDENCIES["representation_payload"].read_text()
    )
    complete = [
        parse_coordinate(value)
        for value in representation_payload["closure_coordinate_basis"]
    ]
    index = {coordinate: position for position, coordinate in enumerate(complete)}
    old_payload = json.loads(DEPENDENCIES["obstruction_payload"].read_text())
    _, old_vectors = _load_old_vectors(old_payload)
    epsilon = {
        f"epsilon_{emitter}": ward_column(emitter)
        for emitter in (0, 1)
    }
    typed = old_vectors["base_maxwell_typed"]
    residual = dict(typed)
    for column in epsilon.values():
        residual = _vector_add(
            residual, column, (Fraction(2), Fraction(0))
        )
    if not all(set(vector) <= set(complete) for vector in epsilon.values()):
        raise AssertionError("minimal channel escaped the certified closure")
    payload = {
        "schema": "closed-universe-berger-minimal-invariant-scalar-hessian-channel-no-go-payload-v1",
        "result_id": "BERGER_MINIMAL_INVARIANT_SCALAR_HESSIAN_CHANNEL_NO_GO_PAYLOAD",
        "closure_basis_ref": {
            "path": str(DEPENDENCIES["representation_payload"].relative_to(ROOT)),
            "result_id": representation_payload["result_id"],
            "sha256": sha256(DEPENDENCIES["representation_payload"]),
        },
        "local_action_entries": {
            f"emitter_{emitter}": _action_entries(minimal_action(emitter))
            for emitter in (0, 1)
        },
        "cyclic_q2_entries": {
            f"emitter_{emitter}": _q2_entries(
                action_to_q2(minimal_action(emitter))
            )
            for emitter in (0, 1)
        },
        "ward_vectors_on_900_coordinate_closure": {
            **{
                name: _entries(vector, index)
                for name, vector in epsilon.items()
            },
            "typed_maxwell_source": _entries(typed, index),
            "normalized_residual": _entries(residual, index),
        },
    }
    return payload, {
        "complete": complete,
        "index": index,
        "old_vectors": old_vectors,
        "epsilon": epsilon,
        "typed": typed,
        "residual": residual,
    }


def build_certificate(payload: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    dependencies = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    complete = audit["complete"]
    old_vectors = audit["old_vectors"]
    old_image = [old_vectors[name] for name in ACTION_COLUMN_ORDER]
    epsilon = [audit["epsilon"][f"epsilon_{emitter}"] for emitter in (0, 1)]
    typed = audit["typed"]
    residual = audit["residual"]
    if [len(minimal_action(emitter)) for emitter in (0, 1)] != [2, 2]:
        raise AssertionError("minimal local action support drifted")
    if [
        len(action_to_q2(minimal_action(emitter))) for emitter in (0, 1)
    ] != [24, 24]:
        raise AssertionError("cyclic q2 support drifted")
    if [len(vector) for vector in epsilon] != [4, 4]:
        raise AssertionError("minimal Ward support drifted")
    if any(vector_action(vector) for vector in epsilon):
        raise AssertionError("minimal Ward column ceased to be invariant")
    if (
        _rank(old_image),
        _rank(old_image + epsilon),
        _rank(old_image + epsilon + [typed]),
    ) != (4, 6, 7):
        raise AssertionError("minimal channel quotient ranks drifted")
    if len(residual) != 112 or vector_action(residual):
        raise AssertionError("normalized invariant residual drifted")
    if _rank(old_image + epsilon + [residual]) != 7:
        raise AssertionError("normalized residual entered the enlarged image")

    typed_first_jet = {
        coordinate: coefficient
        for coordinate, coefficient in typed.items()
        if _profile_first_jet(coordinate)
    }
    old_first_jet = [
        {
            coordinate: coefficient
            for coordinate, coefficient in vector.items()
            if _profile_first_jet(coordinate)
        }
        for vector in old_image
    ]
    epsilon_first_jet = [
        {
            coordinate: coefficient
            for coordinate, coefficient in vector.items()
            if _profile_first_jet(coordinate)
        }
        for vector in epsilon
    ]
    if (
        len(typed_first_jet),
        _rank(old_first_jet + epsilon_first_jet),
        _rank(old_first_jet + epsilon_first_jet + [typed_first_jet]),
    ) != (24, 2, 3):
        raise AssertionError("profile-first-jet obstruction drifted")
    if any(epsilon_first_jet) or vector_action(typed_first_jet):
        raise AssertionError("profile-first-jet representation type drifted")

    delta = [ward_column(emitter, tensor="delta") for emitter in (0, 1)]
    symmetric_cross = [
        ward_column(emitter, tensor="symmetric_cross") for emitter in (0, 1)
    ]
    if any(vector_action(vector) for vector in delta):
        raise AssertionError("delta mutation ceased to be invariant")
    if not all(vector_action(vector) for vector in symmetric_cross):
        raise AssertionError("symmetric-cross mutation ceased to detect equivariance")
    if any(set(vector) & set(typed) for vector in delta):
        raise AssertionError("delta mutation acquired typed-source overlap")

    rendered_payload = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": "closed-universe-berger-minimal-invariant-scalar-hessian-channel-no-go-v1",
        "result_id": "BERGER_MINIMAL_INVARIANT_SCALAR_HESSIAN_CHANNEL_NO_GO",
        "setting_id": dependencies["component_contract"]["setting_id"],
        "claim_status": "OBSTRUCTED_MINIMAL_EPSILON_HESSIAN_LEAVES_PROFILE_JET_CLASS",
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": dependencies[name].get("result_id", path.stem),
                "sha256": sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": hashlib.sha256(rendered_payload.encode()).hexdigest(),
            "canonical_sha256": canonical_sha256(payload),
        },
        "auxiliary_cyclic_domain": {
            "carrier_rows": 110,
            "new_rows": [
                {"row": CHI, "row_id": "chi", "degree": 0, "Berger_weight": 0},
                {
                    "row": CHI_PLUS,
                    "row_id": "chi_plus",
                    "degree": 1,
                    "Berger_weight": 0,
                },
            ],
            "pairing": "<chi,chi_plus>=1 with signed reverse entry",
            "pairing_rank": 110,
            "additional_outer_scalar_pairs": 0,
            "unary_action": "integral tau chi_plus",
        },
        "transverse_tensor_classification": _tensor_classification(),
        "local_common_action": {
            "formula": (
                "S_epsilon=sum_b gamma_b integral chi g_b h_b "
                "epsilon^{ij}(e_i A_0)(e_j K_{b,12}), i,j in {1,2}"
            ),
            "unit_action_monomials_per_emitter": 2,
            "action_derived_cyclic_q2_keys_per_emitter": 24,
            "unit_Ward_coordinates_per_emitter": 4,
            "normalized_cancellation_parameters": {"gamma_0": 2, "gamma_1": 2},
            "residual_Berger_equivariant": True,
            "background_specialization": (
                "pinned positive Berger frame; g_b constant and h_b scalar "
                "clock profiles; no cross-background identification"
            ),
        },
        "image_in_representation_closure": {
            "closure_dimension": len(complete),
            "old_action_image_dimension": 4,
            "new_epsilon_image_mod_old_dimension": 2,
            "enlarged_action_image_dimension": 6,
            "enlarged_closed_cokernel_dimension": 894,
            "enlarged_closed_cokernel_isotypic_dimensions": {
                "0": 454,
                "2": 424,
                "4": 16,
            },
            "typed_source_augmented_rank": 7,
            "typed_source_in_enlarged_image": False,
        },
        "normalized_residual": {
            "formula": "r_typed=source_typed+2 epsilon_0+2 epsilon_1",
            "support_coordinate_count": len(residual),
            "cyclic_module_dimension": 1,
            "Berger_type": "weight_0 trivial line",
            "dimension_mod_enlarged_action_image": 1,
            "transverse_A0_K12_pseudoscalar_coordinates_cancelled": 8,
        },
        "next_invariant_obstruction": {
            "sector": "profile vertical first jet g_b h_b'",
            "source_support_coordinate_count": len(typed_first_jet),
            "epsilon_channel_support_coordinate_count": 0,
            "old_plus_epsilon_projected_image_rank": 2,
            "source_augmented_projected_rank": 3,
            "Berger_type": "weight_0 trivial line",
            "theorem": (
                "The unique minimal reflection-odd transverse invariant "
                "Hessian reaches and cancels the displayed A0--K12 "
                "pseudoscalar projection, but it has zero profile-first-jet "
                "support. The complete typed-Maxwell class therefore remains "
                "outside the enlarged action image, already on the invariant "
                "24-coordinate g_b h_b' sector."
            ),
        },
        "mutations": {
            "drop_epsilon_mate": {
                "replacement": "symmetric transverse cross tensor",
                "Berger_equivariance_fails": True,
                "detected": True,
            },
            "replace_epsilon_by_delta": {
                "Berger_equivariance_survives": True,
                "typed_source_coordinate_overlap_count": 0,
                "typed_source_remains_outside_image": True,
                "detected": True,
            },
            "delete_one_cyclic_q2_key": {
                "action_Hessian_reconstruction_fails": True,
                "detected": True,
            },
            "fit_only_display_coordinate": {
                "scientific_status": (
                    "REJECTED_NON_EQUIVARIANT_NON_CYCLIC_COLUMN; the epsilon "
                    "mate and all action-derived cyclic slots are mandatory"
                ),
                "detected": True,
            },
            "project_900_closure_to_old_444_space": {
                "scientific_status": "REJECTED_NONCANONICAL_PROJECTED_ACTION",
                "detected": True,
            },
        },
        "proof_obligation_dag": [
            {"id": "P1_DECLARE_CYCLIC_AUXILIARY_DOMAIN", "status": "CERTIFIED"},
            {"id": "P2_CLASSIFY_TRANSVERSE_INVARIANT_TENSORS", "status": "CERTIFIED"},
            {"id": "P3_DIFFERENTIATE_LOCAL_EPSILON_ACTION", "status": "CERTIFIED"},
            {"id": "P4_VERIFY_BERGER_EQUIVARIANCE", "status": "CERTIFIED"},
            {"id": "P5_COMPUTE_IMAGE_IN_900_CLOSURE", "status": "CERTIFIED"},
            {"id": "P6_TEST_COMPLETE_TYPED_SOURCE_CLASS", "status": "OBSTRUCTED"},
            {"id": "P7_ISOLATE_PROFILE_FIRST_JET_CLASS", "status": "CERTIFIED"},
        ],
        "activation_disposition": {
            "representation_complete_common_action_extension_exists": False,
            "observer_q1_q2_carrier_freeze_authorized": False,
            "q3_authorized": False,
            "detector_or_causal_promotion_authorized": False,
            "branch_particle_positivity_or_quantum_promotion_authorized": False,
        },
        "next_gate": (
            "CLASSIFY_LOCAL_BERGER_INVARIANT_SCALAR_HESSIAN_CHANNELS_WITH_"
            "NONZERO_PROFILE_FIRST_JET_WARD_PROJECTION"
        ),
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE result consumes the "
            "certified 900-coordinate Berger representation closure and tests "
            "the smallest local invariant tensor channel selected by the "
            "surviving A_0--K_12 projection. It reuses the already certified "
            "single degree-(0,1) scalar conjugate pair and adds no further "
            "outer scalar pair. On the pinned Berger transverse plane the "
            "rank-two invariant tensors are exactly delta and epsilon; after "
            "transverse-reflection oddness, epsilon is the unique line. The "
            "local cubic action chi g_b h_b epsilon^{ij}(e_i A_0)(e_j "
            "K_{b,12}) has two monomials and differentiates through the signed "
            "odd pairing to 24 cyclic q2 keys per emitter. Its constant unary "
            "partner integral tau chi_plus produces four Ward coordinates per "
            "emitter. Both Ward columns are exact Berger-invariant trivial "
            "lines in the 900-coordinate closure and add rank two modulo the "
            "old rank-four image. The enlarged quotient has dimension 894 "
            "and exact isotypic dimensions 454,424,16. The unique parameters "
            "gamma_0=gamma_1=2 cancel all eight transverse pseudoscalar "
            "coordinates, including the displayed -2 g0 h0 coefficient. "
            "Nevertheless the complete typed-Maxwell source raises the image "
            "rank from six to seven. Its normalized residual has 112 "
            "coordinates and remains an invariant trivial line. Already its "
            "24-coordinate profile-first-jet sector g_b h_b' has zero epsilon "
            "support and raises the projected old-plus-epsilon image rank from "
            "two to three. Therefore reaching one displayed projection is not "
            "action-level sufficiency. The next necessary action channel must "
            "have a nonzero invariant profile-first-jet Ward projection. No "
            "decomposition of the non-closed 440-dimensional carrier, fitted "
            "column, additional scalar pair, q3, detector, causal, branch, "
            "particle, positivity, Conflux or quantum claim is made."
        ),
        "provenance": {
            "science_forge_work_item": (
                "sf:program/work/observer-minimal-invariant-scalar-hessian-channel"
            ),
            "input_commit": "bab60f60",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def report(value: dict[str, Any]) -> str:
    image = value["image_in_representation_closure"]
    obstruction = value["next_invariant_obstruction"]
    return f"""# Berger minimal invariant scalar Hessian channel no-go

## Local action

The minimal reflection-odd Berger scalar tensor is the transverse epsilon
line.  Reusing the certified single scalar conjugate pair, its local action is

```text
S_epsilon = sum_b gamma_b integral chi g_b h_b
            epsilon^ij (e_i A_0)(e_j K_b,12).
```

Exact action differentiation gives 24 cyclic `q2` keys and four invariant Ward
coordinates per emitter.  No additional outer scalar pair is introduced.

## Closed quotient

The two source-labelled epsilon columns add rank two to the old rank-four
image in the exact 900-coordinate representation closure.  The resulting
quotient has dimension `{image['enlarged_closed_cokernel_dimension']}` and
isotypic dimensions `(454,424,16)`.

The unique normalization `gamma_0=gamma_1=2` cancels all eight transverse
pseudoscalar coordinates, including the displayed `-2 g0 h0` coefficient.
It does not reach the complete typed-Maxwell source class, which still raises
the image rank from six to seven.

## Next invariant obstruction

The normalized residual is a 112-coordinate invariant trivial line.  Already
the `{obstruction['source_support_coordinate_count']}`-coordinate
`g_b h_b'` profile-first-jet sector has zero epsilon-channel support and raises
the projected image rank from two to three.  Any next action ansatz must
therefore contain an invariant scalar Hessian channel with nonzero
profile-first-jet Ward projection.

CLOSE-OUT: OBSTRUCTED — the unique minimal transverse epsilon Hessian reaches the displayed projection but not the complete typed-Maxwell obstruction class
EVIDENCE: closed_universe_observers/certificates/BERGER_MINIMAL_INVARIANT_SCALAR_HESSIAN_CHANNEL_NO_GO.json
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
        raise SystemExit("stale Berger minimal invariant scalar Hessian channel")
    print("BERGER_MINIMAL_INVARIANT_SCALAR_HESSIAN_CHANNEL_NO_GO generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
