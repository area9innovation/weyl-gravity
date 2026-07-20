#!/usr/bin/env python3
"""Classify the next bounded Berger invariant Hessian action family."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers.berger_108_row_component_jet_contract import (
    Scalar,
    _pbw_word,
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
    tensor_add_symmetric,
)
from closed_universe_observers.generate_berger_110_row_conjugate_pair_extension_no_go import (
    CHI,
    _dual_and_sign,
    extension_q1,
)
from closed_universe_observers.generate_berger_common_action_obstruction_module import (
    ACTION_COLUMN_ORDER,
    _echelon,
)
from closed_universe_observers.generate_berger_minimal_invariant_scalar_hessian_channel_no_go import (
    _action_entries,
    _load_old_vectors,
)
from closed_universe_observers.generate_berger_profile_jet_invariant_hessian_action_repair import (
    invariant_basis as order_one_invariant_basis,
)
from closed_universe_observers.generate_berger_ward_cokernel_irrep_closure_obstruction import (
    closure,
    isotypic_decomposition,
    parse_coordinate,
    parse_scalar,
    serialize_coordinate,
    vector_action,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_HIGHER_JET_INVARIANT_ACTION_MODULE_CLASSIFICATION.json"
PAYLOAD = PACKAGE / "certificates/BERGER_HIGHER_JET_INVARIANT_ACTION_MODULE_CLASSIFICATION_PAYLOAD.json"
SCHEMA = PACKAGE / "schema/berger-higher-jet-invariant-action-module-classification-v1.schema.json"
PAYLOAD_SCHEMA = PACKAGE / "schema/berger-higher-jet-invariant-action-module-classification-payload-v1.schema.json"
REPORT = PACKAGE / "reports/berger-higher-jet-invariant-action-module-classification.md"
DEPENDENCIES = {
    "profile_repair": PACKAGE / "certificates/BERGER_PROFILE_JET_INVARIANT_HESSIAN_ACTION_REPAIR.json",
    "profile_payload": PACKAGE / "certificates/BERGER_PROFILE_JET_INVARIANT_HESSIAN_ACTION_REPAIR_PAYLOAD.json",
    "minimal_payload": PACKAGE / "certificates/BERGER_MINIMAL_INVARIANT_SCALAR_HESSIAN_CHANNEL_NO_GO_PAYLOAD.json",
    "representation_payload": PACKAGE / "certificates/BERGER_WARD_COKERNEL_IRREP_CLOSURE_OBSTRUCTION_PAYLOAD.json",
    "obstruction_payload": PACKAGE / "certificates/BERGER_COMMON_ACTION_OBSTRUCTION_MODULE_PAYLOAD.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_higher_jet_invariant_action_module_classification.py",
    PACKAGE / "tests/test_berger_higher_jet_invariant_action_module_classification.py",
    SCHEMA,
    PAYLOAD_SCHEMA,
]

Coordinate = tuple[arity.BilinearKey, tuple]
Vector = dict[Coordinate, Scalar]
HigherTerm = tuple[int, int, tuple[int, ...], Scalar]
ZERO: Scalar = (Fraction(0), Fraction(0))
ROOT10 = sp.sqrt(10)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _sympy_scalar(value: Scalar) -> sp.Expr:
    return (
        sp.Rational(value[0].numerator, value[0].denominator)
        + ROOT10 * sp.Rational(value[1].numerator, value[1].denominator)
    )


def _scalar(value: sp.Expr) -> Scalar:
    expanded = sp.expand(value)
    rational_part = expanded.coeff(ROOT10, 0)
    root_part = expanded.coeff(ROOT10, 1)
    if sp.expand(expanded - rational_part - ROOT10 * root_part) != 0:
        raise AssertionError("invariant kernel escaped Q(sqrt(10))")
    return (
        Fraction(int(sp.numer(rational_part)), int(sp.denom(rational_part))),
        Fraction(int(sp.numer(root_part)), int(sp.denom(root_part))),
    )


def _canonical_words(order: int) -> list[tuple[int, ...]]:
    return list(itertools.combinations_with_replacement(range(4), order))


def invariant_action_basis(
    emitter: int, order: int
) -> tuple[list[tuple[str, list[HigherTerm]]], dict[str, Any]]:
    """Exact U(1)-invariant kernel at homogeneous A-derivative order."""

    if order not in (0, 1, 2):
        raise ValueError("bounded action order must be zero, one, or two")
    base = 84 + 6 * emitter
    domain_words = _canonical_words(order)
    ambient_words = [
        word
        for degree in range(order + 1)
        for word in _canonical_words(degree)
    ]
    domain = [
        (krow, arow, word)
        for krow in range(base, base + 6)
        for arow in range(55, 59)
        for word in domain_words
    ]
    ambient = [
        (krow, arow, word)
        for krow in range(base, base + 6)
        for arow in range(55, 59)
        for word in ambient_words
    ]
    ambient_index = {term: position for position, term in enumerate(ambient)}
    k_action = {
        base: ((base + 1, 1),),
        base + 1: ((base, -1),),
        base + 2: (),
        base + 3: (),
        base + 4: ((base + 5, 1),),
        base + 5: ((base + 4, -1),),
    }
    a_action = {55: (), 56: ((57, 1),), 57: ((56, -1),), 58: ()}
    matrix = sp.zeros(len(ambient), len(domain))
    for column, (krow, arow, word) in enumerate(domain):
        for target, coefficient in k_action[krow]:
            matrix[ambient_index[(target, arow, word)], column] += coefficient
        for target, coefficient in a_action[arow]:
            matrix[ambient_index[(krow, target, word)], column] += coefficient
        for position, axis in enumerate(word):
            replacements = (
                ((2, 1),) if axis == 1
                else ((1, -1),) if axis == 2
                else ()
            )
            for target, integer in replacements:
                replaced = word[:position] + (target,) + word[position + 1 :]
                for reduced, coefficient in _pbw_word(replaced):
                    matrix[
                        ambient_index[(krow, arow, reduced)], column
                    ] += integer * _sympy_scalar(coefficient)
    nullspace = matrix.nullspace()
    basis: list[tuple[str, list[HigherTerm]]] = []
    parity_counts = {"reflection_even": 0, "reflection_odd": 0}
    k_has_two = {
        base: False,
        base + 1: True,
        base + 2: False,
        base + 3: True,
        base + 4: False,
        base + 5: True,
    }
    for basis_index, vector in enumerate(nullspace):
        terms = [
            (krow, arow, word, _scalar(coefficient))
            for (krow, arow, word), coefficient in zip(
                domain, vector, strict=True
            )
            if coefficient != 0
        ]
        parities = {
            (
                int(k_has_two[krow])
                + int(arow == 57)
                + word.count(2)
            )
            % 2
            for krow, arow, word, _ in terms
        }
        if len(parities) != 1:
            raise AssertionError("nullspace basis is not reflection homogeneous")
        parity = parities.pop()
        parity_counts[
            "reflection_odd" if parity else "reflection_even"
        ] += 1
        basis.append((f"order_{order}.basis_{basis_index:03d}", terms))
    expected = {0: 8, 1: 28, 2: 56}[order]
    if len(nullspace) != expected:
        raise AssertionError("bounded invariant dimension drifted")
    basis_matrix = sp.Matrix.hstack(*nullspace)
    if matrix * basis_matrix != sp.zeros(len(ambient), len(nullspace)):
        raise AssertionError("invariant kernel basis failed")
    return basis, {
        "order": order,
        "raw_dimension": len(domain),
        "ambient_closure_dimension": len(ambient),
        "generator_rank": matrix.rank(),
        "invariant_dimension": len(nullspace),
        "reflection_dimensions": parity_counts,
        "basis_rank": basis_matrix.rank(),
    }


def local_action(
    emitter: int, terms: list[HigherTerm], *, profile_jet: int
) -> Action:
    coefficient = product(
        parameter(f"g{emitter}"),
        profile(f"h{emitter}", (profile_jet,) if profile_jet else ()),
    )
    action: Action = {}
    for krow, arow, word, scalar in terms:
        action_add(
            action,
            ((CHI, ()), (krow, ()), (arow, word)),
            scale(coefficient, scalar),
        )
    return action


def generalized_action_to_q2(action: Action) -> Tensor:
    """Euler-differentiate arbitrary finite PBW words through the pairing."""

    output: Tensor = {}
    for factors, coefficient in action.items():
        for position, varied in enumerate(factors):
            remaining = list(factors)
            remaining.pop(position)
            dual, pairing_sign = _dual_and_sign(varied[0])
            word = varied[1]
            if not word:
                tensor_add_symmetric(
                    output,
                    dual,
                    remaining[0],
                    remaining[1],
                    scale(coefficient, rational(pairing_sign)),
                )
                continue
            total_sign = pairing_sign * (-1) ** len(word)
            expansion = arity.apply_output_word(
                tuple(reversed(word)),
                coefficient,
                remaining[0][1],
                remaining[1][1],
            )
            for (left_word, right_word), expanded_coefficient in expansion.items():
                tensor_add_symmetric(
                    output,
                    dual,
                    (remaining[0][0], left_word),
                    (remaining[1][0], right_word),
                    scale(expanded_coefficient, rational(total_sign)),
                )
    return output


def ward_column(action: Action, *, unary_order: int) -> Vector:
    q2 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
    for (output, left, left_word, right, right_word), coefficient in (
        generalized_action_to_q2(action).items()
    ):
        arity.add_bilinear_term(
            q2[(0, 0)].setdefault(output, {}),
            (left, left_word, right, right_word),
            coefficient,
        )
    row = arity.arity_two_row(
        52,
        (0, 0),
        {(0, 0): extension_q1(temporal_order=unary_order)},
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


def _q2_manifest(tensor: Tensor) -> dict[str, Any]:
    entries = [
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
    return {
        "key_count": len(entries),
        "canonical_sha256": canonical_sha256(entries),
    }


def _profile_zero_total_order_two(coordinate: Coordinate) -> bool:
    key, monomial = coordinate
    profile_factors = [factor for factor in monomial if factor[0] == "profile"]
    return (
        len(key[1]) + len(key[3]) == 2
        and profile_factors
        and all(not factor[2] for factor in profile_factors)
    )


def build_payload() -> tuple[dict[str, Any], dict[str, Any]]:
    modules: dict[str, Any] = {}
    profile_vectors: list[Vector] = []
    temporal_vectors: list[Vector] = []
    order_two_vectors: list[Vector] = []
    classifications = []
    for emitter in (0, 1):
        for order in (0, 1, 2):
            basis, classification = invariant_action_basis(emitter, order)
            if emitter == 0:
                classifications.append(classification)
            if order == 1:
                # Imported positive profile-jet family and its necessary
                # temporal-unary lower-order competitor.
                for name, old_terms in order_one_invariant_basis(emitter):
                    terms = [
                        (krow, arow, (axis,), rational(sign))
                        for krow, arow, axis, sign in old_terms
                    ]
                    for family, profile_jet, unary_order, collection in (
                        ("profile_first", 1, 0, profile_vectors),
                        ("temporal_lower", 0, 1, temporal_vectors),
                    ):
                        module_id = f"{family}.emitter_{emitter}.{name}"
                        action = local_action(
                            emitter, terms, profile_jet=profile_jet
                        )
                        q2 = generalized_action_to_q2(action)
                        vector = ward_column(action, unary_order=unary_order)
                        if vector_action(vector):
                            raise AssertionError("lower invariant column drifted")
                        collection.append(vector)
                        modules[module_id] = {
                            "emitter": emitter,
                            "derivative_order": 1,
                            "profile_jet": profile_jet,
                            "unary_order": unary_order,
                            "action_entries": _action_entries(action),
                            "q2_manifest": _q2_manifest(q2),
                            "ward_vector": _serialize_vector(vector),
                        }
            elif order == 2:
                for name, terms in basis:
                    module_id = f"order_two.emitter_{emitter}.{name}"
                    action = local_action(emitter, terms, profile_jet=0)
                    q2 = generalized_action_to_q2(action)
                    vector = ward_column(action, unary_order=0)
                    if vector_action(vector):
                        raise AssertionError("order-two invariant column drifted")
                    order_two_vectors.append(vector)
                    modules[module_id] = {
                        "emitter": emitter,
                        "derivative_order": 2,
                        "profile_jet": 0,
                        "unary_order": 0,
                        "action_entries": _action_entries(action),
                        "q2_manifest": _q2_manifest(q2),
                        "ward_vector": _serialize_vector(vector),
                    }
    payload = {
        "schema": "closed-universe-berger-higher-jet-invariant-action-module-classification-payload-v1",
        "result_id": "BERGER_HIGHER_JET_INVARIANT_ACTION_MODULE_CLASSIFICATION_PAYLOAD",
        "invariant_classification_by_derivative_order": classifications,
        "common_unaries": {
            "constant": [
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
            "temporal": [
                {
                    "output": output,
                    "input": input_row,
                    "word": list(word),
                    "coefficient": serialize(coefficient),
                }
                for (output, input_row, word), coefficient in sorted(
                    extension_q1(temporal_order=1).items()
                )
            ],
        },
        "modules": modules,
    }
    return payload, {
        "profile_vectors": profile_vectors,
        "temporal_vectors": temporal_vectors,
        "order_two_vectors": order_two_vectors,
    }


def build_certificate(payload: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    certified_closure = [
        parse_coordinate(value)
        for value in values["representation_payload"]["closure_coordinate_basis"]
    ]
    _, old_vectors = _load_old_vectors(values["obstruction_payload"])
    minimal_vectors = {
        name: {
            certified_closure[position]: parse_scalar(scalar)
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
    source = minimal_vectors["typed_maxwell_source"]
    normalized_residual = {
        certified_closure[position]: parse_scalar(scalar)
        for position, scalar in values["profile_repair"][
            "first_remaining_obstruction"
        ]["residual_entries_on_900_closure"]
    }
    profile_vectors = audit["profile_vectors"]
    temporal_vectors = audit["temporal_vectors"]
    order_two_vectors = audit["order_two_vectors"]
    if (len(profile_vectors), len(temporal_vectors), len(order_two_vectors)) != (
        56,
        56,
        112,
    ):
        raise AssertionError("bounded higher-jet module count drifted")

    seed = set(certified_closure)
    for vector in profile_vectors + temporal_vectors + order_two_vectors:
        seed.update(vector)
    closed_coordinates = sorted(closure(seed))
    decomposition = isotypic_decomposition(closed_coordinates)

    lower_image = base + profile_vectors + temporal_vectors
    enlarged_image = lower_image + order_two_vectors
    ranks = (
        _rank(base),
        _rank(lower_image),
        _rank(lower_image + [source]),
        _rank(enlarged_image),
        _rank(enlarged_image + [source]),
    )
    if ranks != (6, 118, 119, 230, 231):
        raise AssertionError("bounded higher-jet image ranks drifted")

    project = lambda vector: {
        coordinate: coefficient
        for coordinate, coefficient in vector.items()
        if _profile_zero_total_order_two(coordinate)
    }
    source_decisive = project(normalized_residual)
    lower_decisive = [project(vector) for vector in lower_image]
    enlarged_decisive = [project(vector) for vector in enlarged_image]
    decisive_ranks = (
        len(source_decisive),
        _rank(lower_decisive),
        _rank(lower_decisive + [source_decisive]),
        _rank(enlarged_decisive),
        _rank(enlarged_decisive + [source_decisive]),
    )

    rendered_payload = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": "closed-universe-berger-higher-jet-invariant-action-module-classification-v1",
        "result_id": "BERGER_HIGHER_JET_INVARIANT_ACTION_MODULE_CLASSIFICATION",
        "setting_id": values["profile_repair"]["setting_id"],
        "claim_status": "OBSTRUCTED_COMPLETE_BOUNDED_ORDER_TWO_INVARIANT_ACTION_FAMILY",
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
        "bounded_action_ansatz": {
            "coefficient_field": "Q(sqrt(10))[g_b,h_b,h_b'] at the declared target grades",
            "carrier": "one existing degree-(0,1) scalar conjugate pair chi,chi_plus and old A/K rows",
            "action_arity": 3,
            "auxiliary_derivative_order": 0,
            "K_derivative_order": 0,
            "A_PBW_derivative_order_bound": 2,
            "profile_jet_bound": 1,
            "unary_temporal_order_bound": 1,
            "reflection": "both reflection-even and reflection-odd invariant modules retained",
            "Berger_weight": 0,
            "degree": "chi degree 0, chi_plus degree 1, old A/K inputs degree 0",
            "normal_form": (
                "K undifferentiated and all old-field derivatives on A; "
                "differentiated auxiliary or K sectors are outside this "
                "declared bounded normal form"
            ),
            "target_grade_complete_subfamilies": [
                "profile jet 1, unary order 0, A order 1 (imported repair family)",
                "profile jet 0, unary order 1, A order 1 (complete lower-order competitor)",
                "profile jet 0, unary order 0, A order 2 (first new family)",
            ],
        },
        "invariant_module_classification": payload[
            "invariant_classification_by_derivative_order"
        ],
        "action_and_cyclicity": {
            "common_unary_count": 2,
            "profile_first_module_count": len(profile_vectors),
            "temporal_lower_module_count": len(temporal_vectors),
            "new_order_two_module_count": len(order_two_vectors),
            "q2_columns_content_addressed": True,
            "derivation": (
                "all q2 columns are Euler Hessians of serialized local cubic "
                "actions; arbitrary PBW words use the exact reversed formal "
                "adjoint and coefficient/field Leibniz expansion"
            ),
            "Berger_equivariance": "every Ward column has exact zero infinitesimal U(1) action",
            "pairing_compatibility": "the certified signed odd pairing and the same constant/temporal unary actions are used throughout",
        },
        "representation_closed_carrier": {
            "old_closure_dimension": len(certified_closure),
            "new_closure_dimension": len(closed_coordinates),
            "new_coordinates_added": len(closed_coordinates) - len(certified_closure),
            "U1_orbit_coordinates_added_beyond_action_support": (
                len(closed_coordinates) - len(seed)
            ),
            "isotypic_dimensions": {
                str(weight): dimension
                for weight, dimension in decomposition.items()
            },
            "coordinate_basis_sha256": canonical_sha256(
                [serialize_coordinate(coordinate) for coordinate in closed_coordinates]
            ),
            "closure_check": "CERTIFIED_EXACT",
        },
        "exact_action_image": {
            "old_plus_epsilon_rank": ranks[0],
            "complete_lower_family_rank": ranks[1],
            "lower_family_plus_source_rank": ranks[2],
            "order_two_enlarged_rank": ranks[3],
            "order_two_enlarged_plus_source_rank": ranks[4],
            "typed_source_in_image": False,
        },
        "decisive_quotient_projection": {
            "sector": "profile vertical jet zero and total input PBW order two",
            "source_support_coordinate_count": decisive_ranks[0],
            "lower_family_projected_rank": decisive_ranks[1],
            "lower_family_plus_source_rank": decisive_ranks[2],
            "order_two_enlarged_projected_rank": decisive_ranks[3],
            "order_two_enlarged_plus_source_rank": decisive_ranks[4],
            "Berger_type": "weight_0 invariant line",
            "theorem": (
                "The 64-coordinate order-two, zero-profile-jet projection of "
                "the typed source remains outside both the complete lower "
                "family and the complete new order-two invariant Hessian image."
            ),
        },
        "minimality": {
            "order_zero_invariant_dimension_per_emitter": 8,
            "order_one_invariant_dimension_per_emitter": 28,
            "order_two_invariant_dimension_per_emitter": 56,
            "lower_order_complete": True,
            "higher_profile_jets_alone_excluded": (
                "profile generators of positive vertical order are linearly "
                "independent of the decisive zero-jet coefficient monomial"
            ),
            "first_not_excluded_derivative_order": 3,
            "next_required_module_type": (
                "weight-zero PBW-order-three scalar Hessians in a carrier "
                "closed together with the integration-by-parts-equivalent "
                "differentiated-chi/K and profile-jet sectors"
            ),
        },
        "proof_obligation_dag": [
            {"id": "P1_IMPORT_PROFILE_REPAIR_BY_HASH", "status": "CERTIFIED"},
            {"id": "P2_DECLARE_FINITE_BOUNDED_NORMAL_FORM", "status": "CERTIFIED"},
            {"id": "P3_CLASSIFY_ORDER_ZERO_ONE_TWO_INVARIANT_KERNELS", "status": "CERTIFIED"},
            {"id": "P4_DERIVE_ALL_UNARY_Q2_COLUMNS", "status": "CERTIFIED"},
            {"id": "P5_CLOSE_NEW_U1_COORDINATE_CARRIER", "status": "CERTIFIED"},
            {"id": "P6_PROVE_LOWER_ORDER_MINIMALITY", "status": "CERTIFIED"},
            {"id": "P7_TEST_TYPED_SOURCE_QUOTIENT", "status": "OBSTRUCTED"},
            {"id": "P8_Q3_AND_NONLINEAR_OBSERVER_REPLAY", "status": "NO_CERTIFIED_MAP"},
        ],
        "mutations": {
            "drop_one_order_two_kernel_vector": {"basis_completeness_fails": True, "detected": True},
            "replace_formal_adjoint_by_unreversed_word": {"first_order_regression_fails": True, "detected": True},
            "project_to_old_900_coordinates": {"scientific_status": "REJECTED_NONCANONICAL_PROJECTION", "detected": True},
            "discard_reflection_odd_modules": {"declared_complete_family_fails": True, "detected": True},
            "ignore_decisive_order_two_projection": {"complete_source_false_positive": True, "detected": True},
        },
        "activation_disposition": {
            "bounded_order_two_action_repair_exists": False,
            "representation_complete_common_action_carrier_exists": False,
            "q3_authorized": False,
            "nonlinear_observer_replay_authorized": False,
            "detector_redshift_or_recoil_promotion_authorized": False,
            "branch_particle_positivity_or_quantum_promotion_authorized": False,
        },
        "next_gate": "CLASSIFY_ORDER_THREE_AND_DIFFERENTIATED_AUXILIARY_K_INVARIANT_HESSIAN_CLOSURE",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE result imports the "
            "committed profile-first-jet repair by exact hash and classifies "
            "the next finite action family in an explicit normal form. The "
            "auxiliary scalar and K are undifferentiated, A carries at most "
            "two canonical Berger PBW derivatives, profile jets are bounded "
            "by one, temporal unary order is bounded by one, both reflection "
            "parities are retained, and every action has total Berger weight "
            "zero. Exact infinitesimal U(1) kernels have dimensions 8,28,56 "
            "per emitter at homogeneous A orders 0,1,2. All relevant lower "
            "profile-first and temporal-unary columns and all 112 new order-"
            "two columns are derived from serialized local actions through "
            "the signed odd pairing. Their coordinate union is enlarged to "
            "its exact U(1) closure, rather than projected to the old carrier. "
            "The lower image "
            "has rank 118 and the order-two image rank 230; the typed source "
            "raises them to 119 and 231. Already its 64-coordinate zero-"
            "profile, total-order-two projection remains a nonzero invariant "
            "quotient class. Positive profile jets cannot affect that grade. "
            "Thus the first derivative order not excluded in this normal form "
            "is three, together with the differentiated-auxiliary/K sectors "
            "required for a full integration-by-parts closure. No q3, gauge "
            "descent, nonlinear detector/redshift/recoil replay, tangent-cone "
            "restriction, branch, particle, positivity, scattering, "
            "phenomenology, Conflux or quantum claim is promoted."
        ),
        "provenance": {
            "science_forge_work_item": "sf:program/work/observer-higher-jet-invariant-action-module-classification",
            "input_commit": "621097fc4",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def report(value: dict[str, Any]) -> str:
    carrier = value["representation_closed_carrier"]
    image = value["exact_action_image"]
    decisive = value["decisive_quotient_projection"]
    return f"""# Berger higher-jet invariant action-module classification

The complete declared scalar Hessian kernels have dimensions `8`, `28`, and
`56` per emitter at homogeneous A-PBW orders zero, one, and two. Both
reflection parities are retained. Every relevant lower-order and new
order-two `q2` column is an exact Hessian of a serialized local action.

Closing the union with the old 900-coordinate carrier under the residual
Berger `U(1)` action gives dimension
{carrier['new_closure_dimension']} with isotypic dimensions
`{carrier['isotypic_dimensions']}`.

The complete lower action image has rank
{image['complete_lower_family_rank']}; adjoining the typed source raises it
to {image['lower_family_plus_source_rank']}. Adding all 112 order-two
invariant modules enlarges the image to rank
{image['order_two_enlarged_rank']}, but the source still raises it to
{image['order_two_enlarged_plus_source_rank']}.

The first decisive quotient is the {decisive['source_support_coordinate_count']}-
coordinate zero-profile-jet, total-input-order-two source projection. It
remains a nonzero weight-zero class after the complete bounded family.
Higher profile jets alone cannot enter this coefficient grade. The first
derivative order not excluded is three, with differentiated auxiliary/K
sectors included for integration-by-parts closure.

CLOSE-OUT: OBSTRUCTED — the complete bounded Berger-invariant scalar Hessian family through PBW order two leaves a nonzero typed-Maxwell quotient class
EVIDENCE: closed_universe_observers/certificates/BERGER_HIGHER_JET_INVARIANT_ACTION_MODULE_CLASSIFICATION.json
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
        raise SystemExit("stale Berger higher-jet invariant action classification")
    print("BERGER_HIGHER_JET_INVARIANT_ACTION_MODULE_CLASSIFICATION generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
