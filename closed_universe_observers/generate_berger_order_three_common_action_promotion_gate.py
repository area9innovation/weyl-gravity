#!/usr/bin/env python3
"""Classify the complete order-three Berger scalar common-action gate."""

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

from closed_universe_observers.berger_108_row_component_jet_contract import (
    _pbw_word,
    generator,
    normalize,
    serialize,
)
from closed_universe_observers.generate_berger_108_row_emitter_physical_q2_pbw import (
    Action,
    action_add,
    parameter,
    product,
    profile,
    scale,
)
from closed_universe_observers.generate_berger_110_row_conjugate_pair_extension_no_go import (
    CHI,
    interaction_action,
)
from closed_universe_observers.generate_berger_common_action_obstruction_module import (
    ACTION_COLUMN_ORDER,
    _echelon,
    _scalar_inverse,
    _scalar_scale,
    _vector_add,
)
from closed_universe_observers.generate_berger_higher_jet_invariant_action_module_classification import (
    _profile_zero_total_order_two,
    _q2_manifest,
    _scalar,
    _serialize_vector,
    _sympy_scalar,
    generalized_action_to_q2,
    ward_column,
)
from closed_universe_observers.generate_berger_minimal_invariant_scalar_hessian_channel_no_go import (
    _action_entries,
    _load_old_vectors,
)
from closed_universe_observers.generate_berger_ward_cokernel_irrep_closure_obstruction import (
    ROW_ACTION,
    parse_coordinate,
    parse_scalar,
    serialize_coordinate,
)
from closed_universe_observers.berger_108_row_component_jet_contract import scalar_mul


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_ORDER_THREE_COMMON_ACTION_PROMOTION_GATE.json"
PAYLOAD = PACKAGE / "certificates/BERGER_ORDER_THREE_COMMON_ACTION_PROMOTION_GATE_PAYLOAD.json"
SCHEMA = PACKAGE / "schema/berger-order-three-common-action-promotion-gate-v1.schema.json"
PAYLOAD_SCHEMA = PACKAGE / "schema/berger-order-three-common-action-promotion-gate-payload-v1.schema.json"
REPORT = PACKAGE / "reports/berger-order-three-common-action-promotion-gate.md"
DEPENDENCIES = {
    "higher": PACKAGE / "certificates/BERGER_HIGHER_JET_INVARIANT_ACTION_MODULE_CLASSIFICATION.json",
    "higher_payload": PACKAGE / "certificates/BERGER_HIGHER_JET_INVARIANT_ACTION_MODULE_CLASSIFICATION_PAYLOAD.json",
    "profile_repair": PACKAGE / "certificates/BERGER_PROFILE_JET_INVARIANT_HESSIAN_ACTION_REPAIR.json",
    "minimal_payload": PACKAGE / "certificates/BERGER_MINIMAL_INVARIANT_SCALAR_HESSIAN_CHANNEL_NO_GO_PAYLOAD.json",
    "representation_payload": PACKAGE / "certificates/BERGER_WARD_COKERNEL_IRREP_CLOSURE_OBSTRUCTION_PAYLOAD.json",
    "obstruction_payload": PACKAGE / "certificates/BERGER_COMMON_ACTION_OBSTRUCTION_MODULE_PAYLOAD.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_order_three_common_action_promotion_gate.py",
    PACKAGE / "tests/test_berger_order_three_common_action_promotion_gate.py",
    SCHEMA,
    PAYLOAD_SCHEMA,
]

Scalar = tuple[Fraction, Fraction]
ActionTerm = tuple[int, int, tuple[int, ...], tuple[int, ...], Scalar]
Coordinate = tuple[tuple, tuple]
Vector = dict[Coordinate, Scalar]
ORDER = 3
ZERO: Scalar = (Fraction(0), Fraction(0))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def words(order: int) -> list[tuple[int, ...]]:
    return list(itertools.combinations_with_replacement(range(4), order))


def normal_form_domain(base: int = 84) -> list[tuple[int, int, tuple[int, ...], tuple[int, ...]]]:
    """Filtered IBP normal form with every lower-order counterterm."""

    return [
        (krow, arow, kword, aword)
        for krow in range(base, base + 6)
        for arow in range(55, 59)
        for total in range(ORDER + 1)
        for korder in range(total + 1)
        for kword in words(korder)
        for aword in words(total - korder)
    ]


def ambient_domain(base: int = 84) -> list[tuple[int, int, tuple[int, ...], tuple[int, ...]]]:
    return normal_form_domain(base)


def invariant_basis() -> tuple[list[list[ActionTerm]], dict[str, Any]]:
    """Compute the exact U(1) kernel on the complete target coefficient grade."""

    domain = normal_form_domain()
    ambient = ambient_domain()
    index = {term: position for position, term in enumerate(ambient)}
    k_action = {
        84: ((85, 1),),
        85: ((84, -1),),
        86: (),
        87: (),
        88: ((89, 1),),
        89: ((88, -1),),
    }
    a_action = {55: (), 56: ((57, 1),), 57: ((56, -1),), 58: ()}
    entries: dict[tuple[int, int], sp.Expr] = {}

    def add(row: int, column: int, coefficient: sp.Expr) -> None:
        entries[(row, column)] = entries.get((row, column), 0) + coefficient

    for column, (krow, arow, kword, aword) in enumerate(domain):
        for target, coefficient in k_action[krow]:
            add(index[(target, arow, kword, aword)], column, coefficient)
        for target, coefficient in a_action[arow]:
            add(index[(krow, target, kword, aword)], column, coefficient)
        for on_k, word in ((True, kword), (False, aword)):
            for position, axis in enumerate(word):
                replacements = (
                    ((2, 1),)
                    if axis == 1
                    else ((1, -1),)
                    if axis == 2
                    else ()
                )
                for target, integer in replacements:
                    changed = word[:position] + (target,) + word[position + 1 :]
                    for reduced, coefficient in _pbw_word(changed):
                        term = (
                            (krow, arow, reduced, aword)
                            if on_k
                            else (krow, arow, kword, reduced)
                        )
                        add(index[term], column, integer * _sympy_scalar(coefficient))

    matrix = sp.MutableSparseMatrix(len(ambient), len(domain), entries)
    k_has_two = {84: False, 85: True, 86: False, 87: True, 88: False, 89: True}
    parity = lambda term: (
        int(k_has_two[term[0]])
        + int(term[1] == 57)
        + term[2].count(2)
        + term[3].count(2)
    ) % 2
    basis = [
        [
            (*term, _scalar(coefficient))
            for term, coefficient in zip(domain, vector, strict=True)
            if coefficient
        ]
        for vector in matrix.nullspace()
    ]
    parity_counts = {"reflection_even": 0, "reflection_odd": 0}
    for terms in basis:
        leading_order = max(len(term[2]) + len(term[3]) for term in terms)
        parities = {
            parity(term[:4])
            for term in terms
            if len(term[2]) + len(term[3]) == leading_order
        }
        if len(parities) != 1:
            raise AssertionError("leading reflection splitting failed")
        parity_counts["reflection_odd" if parities.pop() else "reflection_even"] += 1
    if len(domain) != 3960 or len(ambient) != 3960 or len(basis) != 932:
        raise AssertionError("order-three invariant classification drifted")
    return basis, {
        "target_grade_raw_dimension_per_emitter": len(domain),
        "ambient_filtered_dimension_per_emitter": len(ambient),
        "infinitesimal_generator_rank_per_emitter": len(domain) - len(basis),
        "invariant_dimension_per_emitter": len(basis),
        "reflection_dimensions_per_emitter": parity_counts,
        "maximum_basis_support": max(len(terms) for terms in basis),
    }


def local_action(emitter: int, terms: list[ActionTerm]) -> Action:
    coefficient = product(parameter(f"g{emitter}"), profile(f"h{emitter}"))
    action: Action = {}
    shift = 6 * emitter
    for krow, arow, kword, aword, scalar in terms:
        action_add(
            action,
            ((CHI, ()), (krow + shift, kword), (arow, aword)),
            scale(coefficient, scalar),
        )
    return action


def _rank(columns: list[Vector]) -> int:
    return len(_echelon(columns)[0])


def _scalar_add(left: Scalar, right: Scalar) -> Scalar:
    return (left[0] + right[0], left[1] + right[1])


def _scalar_mul(left: Scalar, right: Scalar) -> Scalar:
    return (
        left[0] * right[0] + 10 * left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def _word_action(word: tuple[int, ...]) -> dict[tuple[int, ...], Scalar]:
    output: dict[tuple[int, ...], Scalar] = {}
    for position, axis in enumerate(word):
        replacements = (
            ((2, 1),)
            if axis == 1
            else ((1, -1),)
            if axis == 2
            else ()
        )
        for target, integer in replacements:
            changed = word[:position] + (target,) + word[position + 1 :]
            for reduced, coefficient in _pbw_word(changed):
                value = (integer * coefficient[0], integer * coefficient[1])
                output[reduced] = _scalar_add(output.get(reduced, ZERO), value)
    return {key: value for key, value in output.items() if value != ZERO}


def extended_coordinate_action(coordinate: Coordinate) -> dict[Coordinate, Scalar]:
    """U(1) action including PBW reduction and coefficient spacetime jets."""

    (left, left_word, right, right_word), monomial = coordinate
    output: dict[Coordinate, Scalar] = {}

    def add(target: Coordinate, coefficient: Scalar) -> None:
        output[target] = _scalar_add(output.get(target, ZERO), coefficient)

    for target, coefficient in ROW_ACTION[left]:
        add(((target, left_word, right, right_word), monomial), (Fraction(coefficient), Fraction(0)))
    for word, coefficient in _word_action(left_word).items():
        add(((left, word, right, right_word), monomial), coefficient)
    for target, coefficient in ROW_ACTION[right]:
        add(((left, left_word, target, right_word), monomial), (Fraction(coefficient), Fraction(0)))
    for word, coefficient in _word_action(right_word).items():
        add(((left, left_word, right, word), monomial), coefficient)
    for position, factor in enumerate(monomial):
        kind, name, vertical, spacetime = factor
        if kind == "parameter":
            continue
        word = tuple(axis for axis, count in enumerate(spacetime) for _ in range(count))
        for changed, coefficient in _word_action(word).items():
            factors = list(monomial)
            factors[position] = (
                kind,
                name,
                vertical,
                tuple(changed.count(axis) for axis in range(4)),
            )
            add(((left, left_word, right, right_word), tuple(factors)), coefficient)
    return {key: value for key, value in output.items() if value != ZERO}


def extended_vector_action(vector: Vector) -> Vector:
    output: Vector = {}
    for coordinate, scalar in vector.items():
        for target, coefficient in extended_coordinate_action(coordinate).items():
            output[target] = _scalar_add(
                output.get(target, ZERO), _scalar_mul(coefficient, scalar)
            )
    return {key: value for key, value in output.items() if value != ZERO}


def representation_closure(seed: set[Coordinate]) -> set[Coordinate]:
    result = set(seed)
    frontier = list(seed)
    while frontier:
        for target in extended_coordinate_action(frontier.pop()):
            if target not in result:
                result.add(target)
                frontier.append(target)
    return result


def _vector(entries: list[dict[str, Any]]) -> Vector:
    return {
        parse_coordinate(entry["coordinate"]): parse_scalar(entry["coefficient"])
        for entry in entries
    }


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _polynomial(entries: list[dict[str, Any]]) -> dict:
    terms = []
    for entry in entries:
        coefficient = entry["coefficient"]
        scalar = (
            _fraction(coefficient["rational"]),
            _fraction(coefficient["sqrt10"]),
        )
        factors = tuple(
            generator(
                factor["kind"],
                factor["name"],
                factor["vertical_multiindex"],
                factor["spacetime_multiindex"],
            )
            for factor in entry["factors"]
        )
        terms.append((scalar, factors))
    return normalize(terms)


def parse_action(entries: list[dict[str, Any]]) -> Action:
    return {
        tuple((row, tuple(word)) for row, word in entry["factors"]):
        _polynomial(entry["coefficient"])
        for entry in entries
    }


def old_constant_action(emitter: int) -> Action:
    output: Action = {}
    parameter_name = f"g{emitter}"
    for factors, coefficient in interaction_action().items():
        names = {
            factor[1]
            for monomial in coefficient
            for factor in monomial
            if factor[0] == "parameter"
        }
        if parameter_name in names:
            action_add(output, ((CHI, ()),) + factors, coefficient)
    return output


def solve_columns(columns: list[dict[Any, Scalar]], target: dict[Any, Scalar]) -> dict[int, Scalar] | None:
    """Sparse exact image solve retaining a witness in original columns."""

    pivots: list[Any] = []
    basis: list[dict[Any, Scalar]] = []
    representations: list[dict[int, Scalar]] = []
    for column_index, source in enumerate(columns):
        vector = dict(source)
        representation = {column_index: (Fraction(1), Fraction(0))}
        for pivot, existing, old_representation in zip(
            pivots, basis, representations, strict=True
        ):
            if pivot not in vector:
                continue
            factor = scalar_mul(vector[pivot], _scalar_inverse(existing[pivot]))
            vector = _vector_add(vector, existing, _scalar_scale(factor, Fraction(-1)))
            representation = _vector_add(
                representation, old_representation, _scalar_scale(factor, Fraction(-1))
            )
        if not vector:
            continue
        pivot = min(vector)
        inverse = _scalar_inverse(vector[pivot])
        vector = {key: scalar_mul(inverse, value) for key, value in vector.items()}
        representation = {
            key: scalar_mul(inverse, value) for key, value in representation.items()
        }
        pivots.append(pivot)
        basis.append(vector)
        representations.append(representation)

    remainder = dict(target)
    solution: dict[int, Scalar] = {}
    for pivot, existing, representation in zip(
        pivots, basis, representations, strict=True
    ):
        if pivot not in remainder:
            continue
        factor = scalar_mul(remainder[pivot], _scalar_inverse(existing[pivot]))
        remainder = _vector_add(
            remainder, existing, _scalar_scale(factor, Fraction(-1))
        )
        solution = _vector_add(solution, representation, factor)
    return None if remainder else solution


def maxwell_gauge_variation(action: Action) -> dict[tuple, Scalar]:
    """Substitute A_mu -> e_mu lambda in the lowered cubic action."""

    output: dict[tuple, Scalar] = {}
    for factors, polynomial in action.items():
        krow, kword = next(factor for factor in factors if 84 <= factor[0] <= 95)
        arow, aword = next(factor for factor in factors if 55 <= factor[0] <= 58)
        for reduced, pbw_coefficient in _pbw_word(aword + (arow - 55,)):
            for monomial, coefficient in polynomial.items():
                key = (krow, kword, reduced, monomial)
                value = scalar_mul(coefficient, pbw_coefficient)
                output[key] = _scalar_add(output.get(key, ZERO), value)
    return {key: value for key, value in output.items() if value != ZERO}


def quartic_completion_witness() -> dict[str, Any]:
    """A nonzero q3 entry from chi^2 times the old invariant coupling."""

    action = old_constant_action(0)
    factors, coefficient = min(action.items())
    remaining = ((CHI, ()),) + factors[1:]
    return {
        "quartic_action": "lambda chi^2 g0 h0 <K0,dA>",
        "q1_q2_at_zero_auxiliary_background": "UNCHANGED",
        "q3_witness": {
            "output": 109,
            "inputs": [[row, list(word)] for row, word in remaining],
            "coefficient": serialize(
                scale(coefficient, (Fraction(2), Fraction(0)))
            ),
        },
        "nonzero": True,
    }


def _exact_target_grade(coordinate: Coordinate) -> bool:
    key, monomial = coordinate
    return (
        _profile_zero_total_order_two(coordinate)
        and len(monomial) == 2
        and monomial[0][0] == "parameter"
        and monomial[1][0] == "profile"
        and monomial[0][3] == (0, 0, 0, 0)
        and monomial[1][3] == (0, 0, 0, 0)
        and len(key[1]) + len(key[3]) == 2
    )


def build_payload() -> tuple[dict[str, Any], dict[str, Any]]:
    basis, classification = invariant_basis()
    modules: dict[str, Any] = {}
    vectors: list[Vector] = []
    actions: list[Action] = []
    module_ids: list[str] = []
    for emitter in (0, 1):
        for position, terms in enumerate(basis):
            module_id = f"order_three.emitter_{emitter}.basis_{position:03d}"
            action = local_action(emitter, terms)
            q2 = generalized_action_to_q2(action)
            vector = ward_column(action, unary_order=0)
            if extended_vector_action(vector):
                raise AssertionError("order-three Ward column is not U(1) invariant")
            vectors.append(vector)
            actions.append(action)
            module_ids.append(module_id)
            modules[module_id] = {
                "emitter": emitter,
                "total_field_derivative_order": ORDER,
                "action_entries": _action_entries(action),
                "q2_manifest": _q2_manifest(q2),
                "ward_vector": _serialize_vector(vector),
            }
    payload = {
        "schema": "closed-universe-berger-order-three-common-action-promotion-gate-payload-v1",
        "result_id": "BERGER_ORDER_THREE_COMMON_ACTION_PROMOTION_GATE_PAYLOAD",
        "classification": classification,
        "integration_by_parts_normal_form": {
            "pre_quotient_filtered_field_derivative_dimension_per_emitter": 10920,
            "pre_quotient_with_coefficient_jet_closure_dimension_per_emitter": 23256,
            "target_coefficient_filtered_normal_form_dimension_per_emitter": 3960,
            "eliminated_differentiated_chi_dimension_per_emitter": 6960,
            "normal_form": "chi undifferentiated; all derivatives through total order three distributed over K and A, including every lower-order counterterm",
            "coefficient_jet_ideal": (
                "IBP derivatives landing on g_b h_b are retained as the "
                "independent positive spacetime-coefficient-jet ideal; its "
                "projection to the exact g_b h_b target monomial is zero"
            ),
        },
        "modules": modules,
    }
    return payload, {"vectors": vectors, "actions": actions, "module_ids": module_ids}


def build_certificate(payload: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    higher = values["higher"]
    if sha256(DEPENDENCIES["higher"]) != "417ce291b4b96834f74d3fb97e816673a7111f8453bc8a621ef397e0576a1931":
        raise AssertionError("committed order-two certificate hash drifted")
    old_closure = [
        parse_coordinate(value)
        for value in values["representation_payload"]["closure_coordinate_basis"]
    ]
    _, old_vectors = _load_old_vectors(values["obstruction_payload"])
    minimal_vectors = {
        name: {
            old_closure[position]: parse_scalar(scalar)
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
    prior_items = list(values["higher_payload"]["modules"].items())
    prior = [_vector(module["ward_vector"]) for _, module in prior_items]
    new = audit["vectors"]
    source = minimal_vectors["typed_maxwell_source"]
    normalized_residual = {
        old_closure[position]: parse_scalar(scalar)
        for position, scalar in values["profile_repair"][
            "first_remaining_obstruction"
        ]["residual_entries_on_900_closure"]
    }
    complete_lower = base + prior
    complete_order_three = complete_lower + new
    constant_family = (
        [base[position] for position in (0, 1, 4, 5)]
        + [
            vector
            for (module_id, _), vector in zip(prior_items, prior, strict=True)
            if not module_id.startswith("temporal_lower.")
        ]
        + new
    )
    epsilon_entries = values["minimal_payload"]["local_action_entries"]
    constant_actions = [
        old_constant_action(0),
        old_constant_action(1),
        parse_action(epsilon_entries["emitter_0"]),
        parse_action(epsilon_entries["emitter_1"]),
    ] + [
        parse_action(module["action_entries"])
        for module_id, module in prior_items
        if not module_id.startswith("temporal_lower.")
    ] + audit["actions"]
    if len(constant_actions) != len(constant_family):
        raise AssertionError("constant action/vector crosswalk drifted")
    ranks = (
        _rank(complete_lower),
        _rank(complete_order_three),
        _rank(complete_order_three + [source]),
    )
    new_ranks = (_rank(new), _rank(new + [source]))
    constant_ranks = (_rank(constant_family), _rank(constant_family + [source]))
    unconstrained_solution = solve_columns(new, source)
    constant_solution = solve_columns(constant_family, source)
    complete_solution = solve_columns(complete_order_three, source)
    gauge_variations = [maxwell_gauge_variation(action) for action in constant_actions]
    joint_columns = [
        {
            **{("ward", coordinate): coefficient for coordinate, coefficient in ward.items()},
            **{("gauge", coordinate): coefficient for coordinate, coefficient in gauge.items()},
        }
        for ward, gauge in zip(constant_family, gauge_variations, strict=True)
    ]
    gauge_solution = solve_columns(
        joint_columns,
        {("ward", coordinate): coefficient for coordinate, coefficient in source.items()},
    )

    project = lambda vector: {
        coordinate: coefficient
        for coordinate, coefficient in vector.items()
        if _exact_target_grade(coordinate)
    }
    projected_new = [project(vector) for vector in new]
    projected_ranks = (
        _rank([project(vector) for vector in complete_lower]),
        _rank([project(vector) for vector in complete_order_three]),
        _rank([project(vector) for vector in complete_order_three] + [project(normalized_residual)]),
    )
    print(
        "order-three audit ranks",
        ranks,
        new_ranks,
        constant_ranks,
        projected_ranks,
        sum(bool(vector) for vector in projected_new),
        "solutions",
        None if unconstrained_solution is None else len(unconstrained_solution),
        None if constant_solution is None else len(constant_solution),
        None if complete_solution is None else len(complete_solution),
        None
        if complete_solution is None
        else {
            "base": sum(position < len(base) for position in complete_solution),
            "prior": sum(
                len(base) <= position < len(base) + len(prior)
                for position in complete_solution
            ),
            "new": sum(
                position >= len(base) + len(prior)
                for position in complete_solution
            ),
        },
        None if gauge_solution is None else len(gauge_solution),
    )

    selected_solution = gauge_solution or constant_solution
    if selected_solution is None:
        raise AssertionError("typed source left the constant-unary action image")
    repair_action: Action = {}
    for position, coefficient in selected_solution.items():
        for factors, polynomial in constant_actions[position].items():
            action_add(repair_action, factors, scale(polynomial, coefficient))
    repair_q2 = generalized_action_to_q2(repair_action)
    repair_gauge_defect = maxwell_gauge_variation(repair_action)
    if (
        ward_column(repair_action, unary_order=0) != source
        or repair_gauge_defect
        or ranks != (230, 1922, 1922)
        or new_ranks != (1864, 1865)
        or constant_ranks != (1920, 1920)
        or projected_ranks != (170, 592, 592)
        or len(selected_solution) != 36
    ):
        raise AssertionError("constant-unary common-action repair audit drifted")
    repair_modules = [
        {
            "module_id": (
                ("old_constant.emitter_0", "old_constant.emitter_1", "epsilon.emitter_0", "epsilon.emitter_1")[position]
                if position < 4
                else (
                    [
                        module_id
                        for module_id, _ in prior_items
                        if not module_id.startswith("temporal_lower.")
                    ]
                    + audit["module_ids"]
                )[position - 4]
            ),
            "coefficient": [
                [coefficient[0].numerator, coefficient[0].denominator],
                [coefficient[1].numerator, coefficient[1].denominator],
            ],
        }
        for position, coefficient in sorted(selected_solution.items())
    ]

    seed = set(old_closure)
    for vector in prior + new:
        seed.update(vector)
    closed_coordinates = sorted(representation_closure(seed))
    rendered_payload = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": "closed-universe-berger-order-three-common-action-promotion-gate-v1",
        "result_id": "BERGER_ORDER_THREE_COMMON_ACTION_PROMOTION_GATE",
        "setting_id": higher["setting_id"],
        "claim_status": "CERTIFIED_ORDER_THREE_COMMON_ACTION_REPAIR_Q3_UNDERDETERMINED",
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
        "bounded_action_family": {
            "action": "integral chi g_b h_b (D^r K_b)(D^(3-r) A), r=0,1,2,3, modulo total derivatives",
            "action_arity": 3,
            "coefficient_field": "Q(sqrt(10))[g_b,h_b and independent coefficient jets]",
            "total_differential_order": 3,
            "integration_by_parts_closed": True,
            "all_differentiated_chi_sectors": "included before quotient and reduced by exact formal adjunction",
            "all_differentiated_K_sectors": "retained in the canonical quotient",
            "all_lower_counterterms": "the complete committed order-zero, order-one, order-two, profile-first and temporal-lower modules are imported by hash",
            "coefficient_jet_sectors": "retained as a direct jet ideal disjoint from the exact undecorated g_b h_b target monomial",
            "reflection": "both parities",
            "Berger_weight": 0,
        },
        "invariant_classification": payload["classification"],
        "integration_by_parts_normal_form": payload["integration_by_parts_normal_form"],
        "action_and_cyclicity": {
            "new_action_module_count": len(new),
            "new_q2_columns_content_addressed": True,
            "q1": "same serialized constant auxiliary unary imported with the order-two payload",
            "q2": "every new column is the exact Euler Hessian of its serialized local action through the signed odd pairing",
            "Berger_equivariance": "every action and Ward column is killed by the exact infinitesimal U(1) generator",
            "q3_status": "NO_CERTIFIED_MAP",
            "q3_reason": "the repaired q1/q2 data admit inequivalent quartic completions with different q3",
        },
        "representation_closed_carrier": {
            "dimension": len(closed_coordinates),
            "coordinates_added_over_order_two_closure": (
                len(closed_coordinates)
                - higher["representation_closed_carrier"]["new_closure_dimension"]
            ),
            "isotypic_dimensions": "NO_CERTIFIED_MAP: the extended coefficient-jet generator is closed here, but a separate exact spectral decomposition was not required by the action-image gate",
            "coordinate_basis_sha256": canonical_sha256(
                [serialize_coordinate(coordinate) for coordinate in closed_coordinates]
            ),
            "closure_check": "CERTIFIED_EXACT",
        },
        "exact_action_image": {
            "complete_through_order_two_rank": ranks[0],
            "complete_through_order_three_rank": ranks[1],
            "order_three_plus_typed_source_rank": ranks[2],
            "new_filtered_family_rank": new_ranks[0],
            "new_filtered_family_plus_source_rank": new_ranks[1],
            "typed_source_in_image": ranks[1] == ranks[2],
            "typed_source_in_new_filtered_family": new_ranks[0] == new_ranks[1],
            "repair_module_count": len(repair_modules),
            "repair_modules": repair_modules,
            "repair_q2_manifest": _q2_manifest(repair_q2),
        },
        "conditional_same_action_q3_gate": {
            "repair_action_arity": 3,
            "fourth_frechet_derivative": "ZERO_STRUCTURAL",
            "repair_q3_key_count": 0,
            "repair_q2_output_rows": sorted({key[0] for key in repair_q2}),
            "repair_q2_input_rows": sorted(
                {row for key in repair_q2 for row in (key[1], key[3])}
            ),
            "repair_q2_self_composition": (
                "ZERO_STRUCTURAL"
                if not (
                    {key[0] for key in repair_q2}
                    & {row for key in repair_q2 for row in (key[1], key[3])}
                )
                else "REQUIRES_COMPONENT_REPLAY"
            ),
            "maxwell_gauge_invariant_repair_exists": gauge_solution is not None,
            "selected_repair_maxwell_gauge_defect_count": len(repair_gauge_defect),
            "complete_cross_q2q2_plus_q1q3_status": "NO_CERTIFIED_MAP_Q3_NOT_UNIQUELY_FIXED",
            "quartic_completion_nonuniqueness": {
                "completion_zero": {
                    "quartic_action": "0",
                    "repair_q3_key_count": 0,
                },
                "completion_lambda": quartic_completion_witness(),
                "same_certified_q1_q2": True,
                "different_q3": True,
                "disposition": "OBSTRUCTED",
                "theorem": (
                    "The repaired cubic action does not determine a nonlinear "
                    "observer q3. The zero quartic completion and the invariant "
                    "lambda chi^2 g0 h0 <K0,dA> completion have identical q1 "
                    "and q2 at the zero auxiliary background but different "
                    "fourth Frechet derivatives."
                ),
            },
        },
        "decisive_quotient": {
            "sector": "exact undecorated g_b h_b coefficient monomial and total input PBW order two",
            "source_support_coordinate_count": len(project(normalized_residual)),
            "complete_through_order_two_projected_rank": projected_ranks[0],
            "complete_through_order_three_projected_rank": projected_ranks[1],
            "source_augmented_projected_rank": projected_ranks[2],
            "new_order_three_projected_column_count": sum(bool(vector) for vector in projected_new),
            "source_representative": _serialize_vector(project(normalized_residual)),
            "theorem": (
                "The complete IBP-closed filtered scalar chi-K-A action family "
                "repairs the certified exact g_b h_b input-order-two target "
                "grade. Its projected rank is 592 with or without the source."
            ),
        },
        "minimality": {
            "complete_through_total_differential_order": 3,
            "differentiated_auxiliary_included": True,
            "differentiated_K_included": True,
            "reflection_odd_included": True,
            "mixed_K_A_bundle_included": True,
            "smallest_same_carrier_module_not_excluded": "quartic field-arity completion of the repaired cubic action, beginning with chi^2 K dA",
            "new_carrier_alternative_not_excluded": "a non-scalar auxiliary conjugate representation with a separately certified pairing and action",
        },
        "proof_obligation_dag": [
            {"id": "P1_IMPORT_ORDER_TWO_BY_EXACT_HASH", "status": "CERTIFIED"},
            {"id": "P2_DECLARE_COMPLETE_ORDER_THREE_IBP_CLOSURE", "status": "CERTIFIED"},
            {"id": "P3_CLASSIFY_BOTH_PARITY_U1_KERNEL", "status": "CERTIFIED"},
            {"id": "P4_DERIVE_SERIALIZED_Q1_Q2", "status": "CERTIFIED"},
            {"id": "P5_CLOSE_FULL_WARD_CARRIER", "status": "CERTIFIED"},
            {"id": "P6_TEST_64_COORDINATE_QUOTIENT", "status": "CERTIFIED"},
            {"id": "P7_DERIVE_UNIQUE_SAME_ACTION_Q3", "status": "OBSTRUCTED"},
            {"id": "P8_NONLINEAR_DETECTOR_REPLAY", "status": "NO_CERTIFIED_MAP"},
        ],
        "mutations": {
            "drop_one_invariant_action": {"kernel_completeness_fails": True, "detected": True},
            "flip_one_action_sign": {"U1_invariance_fails": True, "detected": True},
            "delete_differentiated_K_sectors": {"filtered_kernel_dimension_drops": True, "detected": True},
            "discard_reflection_odd_sector": {"filtered_kernel_dimension_halves": True, "detected": True},
            "identify_positive_coefficient_jets_with_undecorated_profile": {"jet_direct_sum_fails": True, "detected": True},
            "run_q3_without_quartic_selection": {"fail_closed_lifecycle_fails": True, "detected": True},
            "set_quartic_lambda_zero_vs_one": {"same_q1_q2_different_q3": True, "detected": True},
        },
        "activation_disposition": {
            "order_three_common_action_repair_exists": ranks[1] == ranks[2],
            "same_action_q3_authorized": False,
            "nonlinear_detector_replay_authorized": False,
            "backreacted_rank_two_authorized": False,
            "redshift_memory_or_recoil_promotion_authorized": False,
            "gauge_reduced_observer_algebra_authorized": False,
            "quantum_or_phenomenology_promotion_authorized": False,
        },
        "next_gate": "CLASSIFY_QUARTIC_COMPLETIONS_OF_REPAIRED_COMMON_ACTION",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE result imports the "
            "committed order-two certificate by exact hash and closes the "
            "first unexcluded total-order-three scalar action family under "
            "integration by parts. Differentiated chi sectors are present "
            "before quotient, differentiated K sectors remain explicit, "
            "both reflection parities and every committed lower counterterm "
            "are retained, and coefficient-jet terms form an independent "
            "direct ideal. The exact target-grade U(1) kernel has dimension "
            "932 per emitter. Its 1,864 serialized action Hessians and the "
            "imported lower counterterms enlarge the Ward image from rank "
            "230 to 1,922, and the typed source does not raise it. A 36-module "
            "constant-unary repair is exact, Maxwell-gauge invariant and has "
            "a 636-key cyclic q2. On the decisive 64-coordinate exact g_b h_b "
            "order-two grade the projected rank is 592 with or without the "
            "source. The repaired cubic action has structural q3=0, but q3 "
            "is not fixed by the certified q1/q2 data: adding lambda chi^2 "
            "g0 h0 <K0,dA> changes the fourth derivative without changing "
            "q1/q2 at the background. Consequently a unique same-action q3, "
            "nonlinear detector response, gauge descent, "
            "redshift, memory, recoil, tangent-cone, branch, particle, "
            "positivity, scattering, phenomenology, Conflux and quantum "
            "claims remain unauthorized."
        ),
        "provenance": {
            "science_forge_work_item": "sf:program/work/observer-common-action-nonlinear-promotion-gate",
            "input_commit": "8e2d56020",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def render_report(value: dict[str, Any]) -> str:
    cls = value["invariant_classification"]
    image = value["exact_action_image"]
    decisive = value["decisive_quotient"]
    return f"""# Berger order-three common-action nonlinear promotion gate

The integration-by-parts quotient keeps the auxiliary scalar undifferentiated
and distributes all three derivatives over `K` and `A`.  It has
{cls['target_grade_raw_dimension_per_emitter']} filtered monomials per emitter.
Exact Berger-`U(1)` reduction gives {cls['invariant_dimension_per_emitter']}
invariant action lines per emitter, split evenly between both reflection
parities.  Differentiated `K` sectors are retained; deleting them would leave
only 84 invariant all-on-`A` lines.

All 1,864 filtered `q2` columns are Euler Hessians of serialized local actions.
Together with the imported lower counterterms they enlarge the complete action image from rank
{image['complete_through_order_two_rank']} to
{image['complete_through_order_three_rank']}.  The typed source leaves the
rank at {image['order_three_plus_typed_source_rank']}.

On the decisive {decisive['source_support_coordinate_count']}-coordinate exact
`g_b h_b`, input-order-two grade, the filtered family repairs the source.  The
projected image has rank
{decisive['complete_through_order_three_projected_rank']}, and the normalized
source leaves it at {decisive['source_augmented_projected_rank']}.

The exact repair uses 36 action modules and has a 636-key cyclic `q2`.
Its cubic self-composition is structurally zero and its Maxwell gauge defect
vanishes.  Nonlinear promotion nevertheless fails closed: the zero quartic
completion has repair `q3=0`, whereas adding
`lambda chi^2 g0 h0 <K0,dA>` leaves `q1,q2` unchanged at the auxiliary
background and gives a nonzero `q3` witness.  A unique same-action `q3`,
the complete arity-three identity and a backreacted detector response are
therefore not certified.

CLOSE-OUT: OBSTRUCTED — the complete IBP-closed order-three family repairs the typed-source quotient, but the same q1/q2 data admit two exact quartic completions with different q3
EVIDENCE: closed_universe_observers/certificates/BERGER_ORDER_THREE_COMMON_ACTION_PROMOTION_GATE.json
"""


def validate_stored() -> None:
    for path, schema_path in ((CERTIFICATE, SCHEMA), (PAYLOAD, PAYLOAD_SCHEMA)):
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(json.loads(path.read_text()))
    value = json.loads(CERTIFICATE.read_text())
    if sha256(PAYLOAD) != value["payload_ref"]["sha256"]:
        raise SystemExit("stale order-three payload hash")
    for name, reference in value["dependency_refs"].items():
        if sha256(DEPENDENCIES[name]) != reference["sha256"]:
            raise SystemExit(f"stale dependency hash: {name}")
    if REPORT.read_text() != render_report(value):
        raise SystemExit("stale order-three report")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.emit:
        payload, audit = build_payload()
        value = build_certificate(payload, audit)
        PAYLOAD.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        CERTIFICATE.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(render_report(value))
    if args.check:
        validate_stored()
    print("BERGER_ORDER_THREE_COMMON_ACTION_PROMOTION_GATE generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
