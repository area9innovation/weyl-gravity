#!/usr/bin/env python3
"""Classify the Berger profile-jet invariant Hessian repair channel."""

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
    parameter,
    product,
    profile,
    rational,
    scale,
)
from closed_universe_observers.generate_berger_110_row_conjugate_pair_extension_no_go import (
    CHI,
    extension_q1,
)
from closed_universe_observers.generate_berger_common_action_obstruction_module import (
    ACTION_COLUMN_ORDER,
    _echelon,
    _vector_add,
)
from closed_universe_observers.generate_berger_minimal_invariant_scalar_hessian_channel_no_go import (
    _action_entries,
    _entries,
    _load_old_vectors,
    _profile_first_jet,
    _q2_entries,
    action_to_q2,
)
from closed_universe_observers.generate_berger_ward_cokernel_irrep_closure_obstruction import (
    parse_coordinate,
    parse_scalar,
    serialize_coordinate,
    vector_action,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_PROFILE_JET_INVARIANT_HESSIAN_ACTION_REPAIR.json"
PAYLOAD = PACKAGE / "certificates/BERGER_PROFILE_JET_INVARIANT_HESSIAN_ACTION_REPAIR_PAYLOAD.json"
SCHEMA = PACKAGE / "schema/berger-profile-jet-invariant-hessian-action-repair-v1.schema.json"
PAYLOAD_SCHEMA = PACKAGE / "schema/berger-profile-jet-invariant-hessian-action-repair-payload-v1.schema.json"
REPORT = PACKAGE / "reports/berger-profile-jet-invariant-hessian-action-repair.md"
DEPENDENCIES = {
    "minimal_channel": PACKAGE / "certificates/BERGER_MINIMAL_INVARIANT_SCALAR_HESSIAN_CHANNEL_NO_GO.json",
    "minimal_payload": PACKAGE / "certificates/BERGER_MINIMAL_INVARIANT_SCALAR_HESSIAN_CHANNEL_NO_GO_PAYLOAD.json",
    "observable_replay": PACKAGE / "certificates/BERGER_COMMON_ACTION_OBSERVABLE_REPLAY_DISPOSITION.json",
    "representation_payload": PACKAGE / "certificates/BERGER_WARD_COKERNEL_IRREP_CLOSURE_OBSTRUCTION_PAYLOAD.json",
    "obstruction_payload": PACKAGE / "certificates/BERGER_COMMON_ACTION_OBSTRUCTION_MODULE_PAYLOAD.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_profile_jet_invariant_hessian_action_repair.py",
    PACKAGE / "tests/test_berger_profile_jet_invariant_hessian_action_repair.py",
    SCHEMA,
    PAYLOAD_SCHEMA,
]

Coordinate = tuple[arity.BilinearKey, tuple]
Vector = dict[Coordinate, Scalar]
Term = tuple[int, int, int, int]
ZERO: Scalar = (Fraction(0), Fraction(0))
ONE: Scalar = (Fraction(1), Fraction(0))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def invariant_basis(emitter: int) -> list[tuple[str, list[Term]]]:
    """Canonical basis of U(1)-invariant K_ab e_c A_d scalars."""

    base = 84 + 6 * emitter
    output: list[tuple[str, list[Term]]] = []
    for family, row in (("K03", base + 2), ("K12", base + 3)):
        output.extend(
            [
                (f"{family}_e0_A0", [(row, 55, 0, 1)]),
                (f"{family}_e0_A3", [(row, 58, 0, 1)]),
                (f"{family}_e3_A0", [(row, 55, 3, 1)]),
                (f"{family}_e3_A3", [(row, 58, 3, 1)]),
                (
                    f"{family}_div_perp",
                    [(row, 56, 1, 1), (row, 57, 2, 1)],
                ),
                (
                    f"{family}_curl_perp",
                    [(row, 57, 1, 1), (row, 56, 2, -1)],
                ),
            ]
        )
    for family, (row1, row2) in (
        ("K0_perp", (base, base + 1)),
        ("K3_perp", (base + 4, base + 5)),
    ):
        vector_families = [
            ("e0_Aperp", [(row1, 56, 0, 1), (row2, 57, 0, 1)],
             [(row1, 57, 0, 1), (row2, 56, 0, -1)]),
            ("e3_Aperp", [(row1, 56, 3, 1), (row2, 57, 3, 1)],
             [(row1, 57, 3, 1), (row2, 56, 3, -1)]),
            ("eperp_A0", [(row1, 55, 1, 1), (row2, 55, 2, 1)],
             [(row1, 55, 2, 1), (row2, 55, 1, -1)]),
            ("eperp_A3", [(row1, 58, 1, 1), (row2, 58, 2, 1)],
             [(row1, 58, 2, 1), (row2, 58, 1, -1)]),
        ]
        for name, delta, epsilon in vector_families:
            output.append((f"{family}_{name}_delta", delta))
            output.append((f"{family}_{name}_epsilon", epsilon))
    if len(output) != 28:
        raise AssertionError("invariant Hessian basis dimension drifted")
    return output


def raw_action_generator(emitter: int) -> tuple[list[tuple[int, int, int]], sp.Matrix]:
    """Infinitesimal U(1) action on all 6*4*4 raw K_ab e_c A_d monomials."""

    base = 84 + 6 * emitter
    raw = [(k, a, axis) for k in range(base, base + 6) for a in range(55, 59) for axis in range(4)]
    index = {term: position for position, term in enumerate(raw)}
    row_action = {
        base: ((base + 1, 1),),
        base + 1: ((base, -1),),
        base + 2: (),
        base + 3: (),
        base + 4: ((base + 5, 1),),
        base + 5: ((base + 4, -1),),
    }
    a_action = {55: (), 56: ((57, 1),), 57: ((56, -1),), 58: ()}
    matrix = sp.zeros(len(raw))
    for column, (krow, arow, axis) in enumerate(raw):
        for target, coefficient in row_action[krow]:
            matrix[index[(target, arow, axis)], column] += coefficient
        for target, coefficient in a_action[arow]:
            matrix[index[(krow, target, axis)], column] += coefficient
        if axis == 1:
            matrix[index[(krow, arow, 2)], column] += 1
        elif axis == 2:
            matrix[index[(krow, arow, 1)], column] -= 1
    return raw, matrix


def module_action(emitter: int, terms: list[Term]) -> Action:
    coefficient = product(
        parameter(f"g{emitter}"), profile(f"h{emitter}", (1,))
    )
    action: Action = {}
    for krow, arow, axis, sign in terms:
        action_add(
            action,
            ((CHI, ()), (krow, ()), (arow, (axis,))),
            scale(coefficient, rational(sign)),
        )
    return action


def ward_column(action: Action) -> Vector:
    q2 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
    for (output, left, left_word, right, right_word), coefficient in action_to_q2(action).items():
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


def _rank(columns: list[Vector]) -> int:
    return len(_echelon(columns)[0])


def _serialize_vector(vector: Vector) -> list[dict[str, Any]]:
    return [
        {
            "coordinate": serialize_coordinate(coordinate),
            "coefficient": [
                [coefficient[0].numerator, coefficient[0].denominator],
                [coefficient[1].numerator, coefficient[1].denominator],
            ],
        }
        for coordinate, coefficient in sorted(vector.items())
    ]


def _zero_profile_jet(coordinate: Coordinate) -> bool:
    return not _profile_first_jet(coordinate)


def build_payload() -> tuple[dict[str, Any], dict[str, Any]]:
    representation = json.loads(DEPENDENCIES["representation_payload"].read_text())
    closure = [parse_coordinate(value) for value in representation["closure_coordinate_basis"]]
    closure_set = set(closure)
    closure_index = {coordinate: position for position, coordinate in enumerate(closure)}
    modules: dict[str, dict[str, Any]] = {}
    vectors: dict[str, Vector] = {}
    preserving: list[str] = []
    escaping: list[str] = []
    for emitter in (0, 1):
        raw, generator = raw_action_generator(emitter)
        basis = invariant_basis(emitter)
        basis_matrix = sp.zeros(len(raw), len(basis))
        raw_index = {term: position for position, term in enumerate(raw)}
        for column, (_, terms) in enumerate(basis):
            for krow, arow, axis, sign in terms:
                basis_matrix[raw_index[(krow, arow, axis)], column] += sign
        if len(raw) - generator.rank() != 28:
            raise AssertionError("raw invariant dimension drifted")
        if generator * basis_matrix != sp.zeros(len(raw), len(basis)):
            raise AssertionError("declared invariant action basis is not invariant")
        if basis_matrix.rank() != 28:
            raise AssertionError("declared invariant action basis is incomplete")
        for name, terms in basis:
            module_id = f"emitter_{emitter}.{name}"
            action = module_action(emitter, terms)
            q2 = action_to_q2(action)
            vector = ward_column(action)
            if vector_action(vector):
                raise AssertionError(f"{module_id} Ward column is not invariant")
            outside = set(vector) - closure_set
            status = "PRESERVES_900_CLOSURE" if not outside else "ESCAPES_900_CLOSURE"
            (preserving if not outside else escaping).append(module_id)
            vectors[module_id] = vector
            modules[module_id] = {
                "emitter": emitter,
                "basis_id": name,
                "status": status,
                "action_entries": _action_entries(action),
                "cyclic_q2_entries": _q2_entries(q2),
                "ward_vector": _serialize_vector(vector),
                "ward_support_count": len(vector),
                "outside_900_support_count": len(outside),
            }
    payload = {
        "schema": "closed-universe-berger-profile-jet-invariant-hessian-action-repair-payload-v1",
        "result_id": "BERGER_PROFILE_JET_INVARIANT_HESSIAN_ACTION_REPAIR_PAYLOAD",
        "closure_basis_ref": {
            "path": str(DEPENDENCIES["representation_payload"].relative_to(ROOT)),
            "result_id": representation["result_id"],
            "sha256": sha256(DEPENDENCIES["representation_payload"]),
        },
        "common_unary": {
            "formula": "integral tau chi_plus",
            "temporal_order": 0,
            "operator_entries": [
                {
                    "output": output,
                    "input": input_row,
                    "word": list(word),
                    "coefficient": serialize(coefficient),
                }
                for (output, input_row, word), coefficient in sorted(
                    extension_q1(temporal_order=0).items()
                )
            ],
        },
        "modules": modules,
        "closure_preserving_module_ids": preserving,
        "closure_escaping_module_ids": escaping,
    }
    return payload, {
        "closure": closure,
        "closure_index": closure_index,
        "vectors": vectors,
        "preserving": preserving,
        "escaping": escaping,
    }


def build_certificate(payload: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    closure = audit["closure"]
    index = audit["closure_index"]
    old_payload = values["obstruction_payload"]
    _, old_vectors = _load_old_vectors(old_payload)
    minimal_vectors = {
        name: {
            closure[position]: parse_scalar(scalar)
            for position, scalar in entries
        }
        for name, entries in values["minimal_payload"][
            "ward_vectors_on_900_coordinate_closure"
        ].items()
    }
    base = [old_vectors[name] for name in ACTION_COLUMN_ORDER] + [
        minimal_vectors["epsilon_0"],
        minimal_vectors["epsilon_1"],
    ]
    preserving_vectors = [audit["vectors"][name] for name in audit["preserving"]]
    source = minimal_vectors["typed_maxwell_source"]
    if len(audit["preserving"]) != 24 or len(audit["escaping"]) != 32:
        raise AssertionError("closure-preserving invariant ansatz dimension drifted")
    if (
        _rank(base),
        _rank(base + preserving_vectors),
        _rank(base + preserving_vectors + [source]),
    ) != (6, 30, 31):
        raise AssertionError("profile-jet action-image ranks drifted")

    selected_ids = []
    selected_vectors = []
    for emitter in (0, 1):
        coefficients = {
            f"emitter_{emitter}.K0_perp_e0_Aperp_delta": Fraction(3, 2),
            f"emitter_{emitter}.K0_perp_eperp_A0_delta": Fraction(-3, 2),
            f"emitter_{emitter}.K03_e0_A3": Fraction(3, 2),
            f"emitter_{emitter}.K03_e3_A0": Fraction(-3, 2),
        }
        vector: Vector = {}
        for module_id, coefficient in coefficients.items():
            vector = _vector_add(
                vector,
                audit["vectors"][module_id],
                (coefficient, Fraction(0)),
            )
            selected_ids.append({"module_id": module_id, "coefficient": [coefficient.numerator, coefficient.denominator]})
        selected_vectors.append(vector)
    selected = _vector_add(selected_vectors[0], selected_vectors[1])
    source_first = {
        coordinate: coefficient
        for coordinate, coefficient in source.items()
        if _profile_first_jet(coordinate)
    }
    if selected != source_first:
        raise AssertionError("declared profile-first-jet repair does not equal source")

    repaired_residual = dict(source)
    for emitter in (0, 1):
        repaired_residual = _vector_add(
            repaired_residual,
            minimal_vectors[f"epsilon_{emitter}"],
            (Fraction(2), Fraction(0)),
        )
    repaired_residual = _vector_add(
        repaired_residual, selected, (Fraction(-1), Fraction(0))
    )
    if (
        len(repaired_residual) != 88
        or any(_profile_first_jet(coordinate) for coordinate in repaired_residual)
        or vector_action(repaired_residual)
    ):
        raise AssertionError("zero-profile-jet residual drifted")
    zero_project = lambda vector: {
        coordinate: coefficient
        for coordinate, coefficient in vector.items()
        if _zero_profile_jet(coordinate)
    }
    base_zero = [zero_project(vector) for vector in base]
    if (
        _rank(base_zero),
        _rank(base_zero + [zero_project(source)]),
    ) != (6, 7):
        raise AssertionError("zero-profile-jet quotient obstruction drifted")

    rendered_payload = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": "closed-universe-berger-profile-jet-invariant-hessian-action-repair-v1",
        "result_id": "BERGER_PROFILE_JET_INVARIANT_HESSIAN_ACTION_REPAIR",
        "setting_id": values["minimal_channel"]["setting_id"],
        "claim_status": "OBSTRUCTED_PROFILE_JET_LINE_ACTION_REALIZED_ZERO_JET_CLASS_REMAINS",
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
            "sha256": hashlib.sha256(rendered_payload.encode()).hexdigest(),
            "canonical_sha256": canonical_sha256(payload),
        },
        "declared_action_ansatz": {
            "coefficient_class": "g_b h_b'(Theta_bar), first vertical profile jet",
            "auxiliary_factor": "undifferentiated weight-zero scalar chi",
            "old_field_hessian": "K_b,ab e_c A_d with K undifferentiated and exactly one Berger-frame derivative on A",
            "equivalence_level": "canonical PBW coefficient-jet normal form after linearity; no fitted Ward column",
            "raw_monomial_dimension_per_emitter": 96,
            "Berger_U1_invariant_dimension_per_emitter": 28,
            "invariant_family_dimensions": {
                "K03_scalar": 6,
                "K12_pseudoscalar": 6,
                "K0_perp_vector": 8,
                "K3_perp_vector": 8,
            },
            "basis_completeness": "exact nullspace equality for the infinitesimal U(1) action on all 96 raw monomials",
            "common_unary_action": "integral tau chi_plus",
        },
        "closure_disposition": {
            "certified_closure_dimension": 900,
            "invariant_modules_total": 56,
            "modules_preserving_900_closure": 24,
            "modules_escaping_900_closure": 32,
            "preserving_dimension_per_emitter": 12,
            "escaping_dimension_per_emitter": 16,
            "escaping_modules_status": "NO_CERTIFIED_MAP_ON_900_CLOSURE",
            "theorem": (
                "The complete first-profile-jet invariant Hessian space has "
                "dimension 28 per emitter. Its Ward map preserves the certified "
                "900-coordinate carrier on exactly 12 basis lines per emitter; "
                "the remaining 16 invariant lines generate coordinates outside "
                "that carrier and cannot be silently projected back."
            ),
        },
        "action_and_cyclicity": {
            "common_unary_key_count": 2,
            "action_module_count": 56,
            "action_monomial_occurrences_per_emitter": 48,
            "cyclic_q2_key_occurrences_per_emitter": 480,
            "closure_preserving_action_monomial_occurrences_per_emitter": 22,
            "closure_preserving_cyclic_q2_key_occurrences_per_emitter": 220,
            "derivation": "every q2 column is the exact Hessian of its serialized local cubic action raised through the signed odd pairing",
            "Berger_equivariance": "every complete Ward column has zero infinitesimal U(1) action",
        },
        "profile_first_jet_repair": {
            "source_support_coordinate_count": len(source_first),
            "source_in_closure_preserving_action_image": True,
            "repair_coefficients": selected_ids,
            "formula": (
                "(3/2) sum_b chi g_b h_b' "
                "[K_b,0i(e_0 A_i-e_i A_0), i=1,2,3]"
            ),
            "old_plus_epsilon_image_rank": 6,
            "enlarged_closure_preserving_image_rank": 30,
            "typed_source_augmented_rank": 31,
            "profile_jet_quotient_class_killed": True,
        },
        "first_remaining_obstruction": {
            "sector": "zero vertical profile jet g_b h_b",
            "normalized_residual_formula": (
                "source_typed + 2 epsilon_0 + 2 epsilon_1 "
                "- profile_first_jet_repair"
            ),
            "support_coordinate_count": len(repaired_residual),
            "Berger_type": "weight_0 trivial line",
            "projected_current_image_rank": _rank(base_zero),
            "source_augmented_projected_rank": _rank(base_zero + [zero_project(source)]),
            "residual_entries_on_900_closure": _entries(repaired_residual, index),
            "theorem": (
                "The closure-preserving first-profile-jet action exactly kills "
                "the 24-coordinate g_b h_b' quotient class. It cannot alter "
                "the zero-profile-jet quotient. After the prior epsilon "
                "normalization, an invariant 88-coordinate g_b h_b residual "
                "remains outside the exact action image."
            ),
        },
        "proof_obligation_dag": [
            {"id": "P1_IMPORT_PRIOR_RESULTS_BY_HASH", "status": "CERTIFIED"},
            {"id": "P2_CLASSIFY_COMPLETE_U1_INVARIANT_FIRST_JET_ANSATZ", "status": "CERTIFIED"},
            {"id": "P3_DERIVE_COMMON_UNARY_AND_ALL_CYCLIC_Q2_COLUMNS", "status": "CERTIFIED"},
            {"id": "P4_CLASSIFY_900_CLOSURE_PRESERVING_SUBSPACE", "status": "CERTIFIED"},
            {"id": "P5_REALIZE_PROFILE_FIRST_JET_SOURCE_LINE", "status": "CERTIFIED"},
            {"id": "P6_PLACE_COMPLETE_TYPED_SOURCE_IN_IMAGE", "status": "OBSTRUCTED"},
            {"id": "P7_REPLAY_DETECTOR_AND_REDSHIFT", "status": "NO_CERTIFIED_MAP"},
        ],
        "mutations": {
            "delete_longitudinal_K03_term": {"profile_repair_fails": True, "detected": True},
            "flip_transverse_gradient_sign": {"profile_repair_fails": True, "detected": True},
            "retain_only_electric_display_coordinate": {"invariant_basis_completeness_fails": True, "detected": True},
            "project_escaping_modules_to_900": {"scientific_status": "REJECTED_NONCANONICAL_PROJECTION", "detected": True},
            "drop_zero_profile_projection": {"complete_source_false_positive": True, "detected": True},
        },
        "activation_disposition": {
            "profile_first_jet_action_module_realized": True,
            "complete_typed_maxwell_source_in_action_image": False,
            "representation_complete_common_action_carrier_exists": False,
            "q3_authorized": False,
            "detector_redshift_or_recoil_replay_authorized": False,
            "gauge_reduced_nonlinear_observer_authorized": False,
            "physical_branch_or_quantum_promotion_authorized": False,
        },
        "next_gate": "CLASSIFY_ZERO_PROFILE_JET_INVARIANT_HESSIAN_MODULE_FOR_88_COORDINATE_RESIDUAL",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE result imports the "
            "committed minimal epsilon-channel obstruction and observable "
            "replay disposition by content hash. It classifies all 96 raw "
            "K_b,ab e_c A_d monomials per emitter at coefficient grade "
            "g_b h_b' and proves that their Berger-U(1)-invariant subspace "
            "has dimension 28, with the serialized 28-line basis spanning "
            "the exact infinitesimal-action kernel. Every local cubic action "
            "is differentiated through the same signed odd pairing, rather "
            "than fitted at Ward level. Exactly 12 invariant lines per emitter "
            "preserve the certified 900-coordinate closure; 16 per emitter "
            "escape it and remain NO_CERTIFIED_MAP there. The closure-"
            "preserving electric combination with coefficient 3/2 exactly "
            "equals the 24-coordinate g_b h_b' typed-source projection, so "
            "the previously missing weight-zero profile-jet action line is "
            "genuinely realized. Nevertheless the full typed source raises "
            "the enlarged image rank from 30 to 31. After the earlier epsilon "
            "normalization and the new profile-jet repair, an invariant "
            "88-coordinate zero-profile-jet residual remains; its projected "
            "image rank rises from six to seven when adjoined. Therefore no "
            "representation-complete common-action carrier, q3, gauge descent, "
            "detector/redshift/recoil replay, tangent-cone restriction, branch, "
            "particle, positivity, scattering, phenomenology, Conflux or "
            "quantum claim is promoted."
        ),
        "provenance": {
            "science_forge_work_item": "sf:program/work/observer-profile-jet-invariant-hessian-action-repair",
            "input_commit": "ff43b676",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def report(value: dict[str, Any]) -> str:
    closure = value["closure_disposition"]
    repair = value["profile_first_jet_repair"]
    obstruction = value["first_remaining_obstruction"]
    return f"""# Berger profile-jet invariant Hessian action repair

The complete declared first-profile-jet scalar Hessian ansatz has dimension
28 per emitter inside the 96-dimensional raw `K_ab e_c A_d` space.  Exact
Berger-`U(1)` nullspace reduction gives the four invariant families
`(6,6,8,8)`.

Only {closure['preserving_dimension_per_emitter']} invariant lines per emitter
preserve the certified 900-coordinate Ward closure; the other
{closure['escaping_dimension_per_emitter']} lines per emitter escape it and
are not projected back.  Every unary and cyclic `q2` entry is derived from
the serialized local actions through the signed odd pairing.

The closure-preserving electric action

```text
(3/2) sum_b chi g_b h_b'
      K_b,0i (e_0 A_i - e_i A_0),  i=1,2,3
```

exactly equals the {repair['source_support_coordinate_count']}-coordinate
profile-first-jet typed-source projection.  Thus the previously missing
weight-zero action line is realized, and the action image grows from rank
six to rank {repair['enlarged_closure_preserving_image_rank']}.

The complete typed source is not repaired: it raises that rank to
{repair['typed_source_augmented_rank']}.  After the earlier epsilon
normalization and the profile-jet repair, an invariant
{obstruction['support_coordinate_count']}-coordinate zero-profile-jet
residual remains outside the action image.

CLOSE-OUT: OBSTRUCTED — the profile-first-jet action line is realized exactly, but the complete typed-Maxwell source retains a certified zero-profile-jet quotient class
EVIDENCE: closed_universe_observers/certificates/BERGER_PROFILE_JET_INVARIANT_HESSIAN_ACTION_REPAIR.json
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
        raise SystemExit("stale Berger profile-jet invariant Hessian action repair")
    print("BERGER_PROFILE_JET_INVARIANT_HESSIAN_ACTION_REPAIR generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
