#!/usr/bin/env python3
"""Generate the exact Berger common-action obstruction module."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.berger_108_row_component_jet_contract import (
    Generator,
    Monomial,
    Scalar,
    scalar_add,
    scalar_mul,
)
from closed_universe_observers.generate_berger_108_row_arity_two_obstruction import (
    _q1_source_parts,
)
from closed_universe_observers.generate_berger_110_row_conjugate_pair_extension_no_go import (
    CHI,
    CHI_PLUS,
    PRIOR_WITNESS_KEY,
    SECOND_EMITTER_PRIOR_WITNESS_KEY,
    SECOND_WITNESS_KEY,
    extension_q1,
    extension_q2,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = (
    PACKAGE / "certificates/BERGER_COMMON_ACTION_OBSTRUCTION_MODULE.json"
)
PAYLOAD = (
    PACKAGE / "certificates/BERGER_COMMON_ACTION_OBSTRUCTION_MODULE_PAYLOAD.json"
)
SCHEMA = (
    PACKAGE / "schema/berger-common-action-obstruction-module-v1.schema.json"
)
PAYLOAD_SCHEMA = (
    PACKAGE
    / "schema/berger-common-action-obstruction-module-payload-v1.schema.json"
)
REPORT = PACKAGE / "reports/berger-common-action-obstruction-module.md"
DEPENDENCIES = {
    "component_contract": PACKAGE
    / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "compatibility_theorem": PACKAGE
    / "certificates/BERGER_108_ROW_COMMON_ACTION_COMPATIBILITY_THEOREM.json",
    "conjugate_pair_no_go": PACKAGE
    / "certificates/BERGER_110_ROW_CONJUGATE_PAIR_EXTENSION_NO_GO.json",
    "emitter_q1": PACKAGE
    / "certificates/BERGER_108_ROW_EMITTER_Q1_PBW_OVERLAY.json",
    "emitter_diff_q2": PACKAGE
    / "certificates/BERGER_108_ROW_EMITTER_DIFF_BV_Q2_PBW.json",
    "typed_maxwell_q2": ROOT
    / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_common_action_obstruction_module.py",
    PACKAGE / "tests/test_berger_common_action_obstruction_module.py",
    SCHEMA,
    PAYLOAD_SCHEMA,
]

Coordinate = tuple[arity.BilinearKey, Monomial]
Vector = dict[Coordinate, Scalar]
ACTION_COLUMN_ORDER = ("z_00", "z_01", "z_10", "z_11")
SOURCE_ORDER = ("emitter_Diff_BV", "base_maxwell_typed")
A_ROWS = frozenset(range(55, 59))
K_ROWS = frozenset(range(84, 96))
ZERO: Scalar = (Fraction(0), Fraction(0))
ONE: Scalar = (Fraction(1), Fraction(0))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _scalar_scale(value: Scalar, factor: Fraction) -> Scalar:
    return value[0] * factor, value[1] * factor


def _scalar_inverse(value: Scalar) -> Scalar:
    a, b = value
    denominator = a * a - 10 * b * b
    if denominator == 0:
        raise ZeroDivisionError("zero Q(sqrt(10)) scalar")
    return a / denominator, -b / denominator


def _vector_add(left: Vector, right: Vector, factor: Scalar = ONE) -> Vector:
    output = dict(left)
    for coordinate, coefficient in right.items():
        value = scalar_add(
            output.get(coordinate, ZERO), scalar_mul(factor, coefficient)
        )
        if value == ZERO:
            output.pop(coordinate, None)
        else:
            output[coordinate] = value
    return output


def _echelon(columns: list[Vector]) -> tuple[list[Coordinate], list[Vector]]:
    pivots: list[Coordinate] = []
    basis: list[Vector] = []
    for source in columns:
        vector = dict(source)
        for pivot, existing in zip(pivots, basis, strict=True):
            if pivot in vector:
                vector = _vector_add(
                    vector,
                    existing,
                    _scalar_scale(
                        scalar_mul(vector[pivot], _scalar_inverse(existing[pivot])),
                        Fraction(-1),
                    ),
                )
        if not vector:
            continue
        pivot = min(vector)
        inverse = _scalar_inverse(vector[pivot])
        vector = {
            coordinate: scalar_mul(inverse, coefficient)
            for coordinate, coefficient in vector.items()
        }
        pivots.append(pivot)
        basis.append(vector)
    return pivots, basis


def exact_rank(columns: list[Vector]) -> int:
    return len(_echelon(columns)[0])


def _is_a_k_key(key: arity.BilinearKey) -> bool:
    return (key[0] in A_ROWS and key[2] in K_ROWS) or (
        key[0] in K_ROWS and key[2] in A_ROWS
    )


def flatten(row: arity.BilinearRow) -> Vector:
    return {
        (key, monomial): coefficient
        for key, polynomial in row.items()
        if _is_a_k_key(key)
        for monomial, coefficient in polynomial.items()
    }


def source_vectors() -> dict[str, Vector]:
    """Recompute every coefficient on the declared two-source-pair orbit."""

    q1 = _q1_source_parts()["emitter"]
    output: dict[str, Vector] = {}
    for source in SOURCE_ORDER:
        row = arity.arity_two_row(
            52,
            (0, 0),
            q1,
            arity.load_q2(sources={source}),
            arity.parities(),
        )
        specialized = arity.specialize_bilinear_rows({52: row}).get(52, {})
        output[source] = flatten(specialized)
    return output


def _emitter_action_q2(emitter: int) -> arity.GradedBilinearRows:
    output: arity.GradedBilinearRows = {
        degree: {} for degree in arity.SUPPORTED_BIDEGREES
    }
    parameter = f"g{emitter}"
    for (target, left, left_word, right, right_word), coefficient in extension_q2(
        interaction_scale=1
    ).items():
        names = {
            factor[1]
            for monomial in coefficient
            for factor in monomial
            if factor[0] == "parameter"
        }
        if parameter not in names:
            continue
        arity.add_bilinear_term(
            output[(0, 0)].setdefault(target, {}),
            (left, left_word, right, right_word),
            coefficient,
        )
    return output


def action_columns() -> dict[str, Vector]:
    """Return the linear envelope of the nonlinear action-to-Ward map."""

    output: dict[str, Vector] = {}
    for temporal_order in (0, 1):
        for emitter in (0, 1):
            row = arity.arity_two_row(
                52,
                (0, 0),
                {(0, 0): extension_q1(temporal_order=temporal_order)},
                _emitter_action_q2(emitter),
                arity.parities() + (0, 1),
            )
            specialized = arity.specialize_bilinear_rows({52: row})[52]
            output[f"z_{temporal_order}{emitter}"] = flatten(specialized)
    return output


def _fraction(value: Fraction) -> list[int]:
    return [value.numerator, value.denominator]


def _scalar(value: Scalar) -> list[list[int]]:
    return [_fraction(value[0]), _fraction(value[1])]


def _generator(value: Generator) -> list[Any]:
    kind, name, vertical, spacetime = value
    return [kind, name, list(vertical), list(spacetime)]


def _coordinate(value: Coordinate) -> dict[str, Any]:
    key, monomial = value
    left, left_word, right, right_word = key
    return {
        "ward_key": [
            left,
            list(left_word),
            right,
            list(right_word),
        ],
        "coefficient_monomial": [_generator(factor) for factor in monomial],
    }


def _vector_entries(
    vector: Vector, coordinate_index: dict[Coordinate, int]
) -> list[list[Any]]:
    return [
        [coordinate_index[coordinate], _scalar(coefficient)]
        for coordinate, coefficient in sorted(
            vector.items(), key=lambda item: coordinate_index[item[0]]
        )
    ]


def _monomial(*factors: Generator) -> Monomial:
    return tuple(sorted(factors))


def _rank_rational(matrix: list[list[int]]) -> int:
    work = [[Fraction(entry) for entry in row] for row in matrix]
    pivot_row = 0
    for column in range(len(work[0])):
        pivot = next(
            (row for row in range(pivot_row, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        divisor = work[pivot_row][column]
        work[pivot_row] = [entry / divisor for entry in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                left - factor * right
                for left, right in zip(work[row], work[pivot_row], strict=True)
            ]
        pivot_row += 1
    return pivot_row


def build_payload() -> tuple[dict[str, Any], dict[str, Any]]:
    sources = source_vectors()
    columns = action_columns()
    all_vectors = [sources[name] for name in SOURCE_ORDER] + [
        columns[name] for name in ACTION_COLUMN_ORDER
    ]
    coordinates = sorted(set().union(*(set(vector) for vector in all_vectors)))
    coordinate_index = {
        coordinate: index for index, coordinate in enumerate(coordinates)
    }
    pivots, _basis = _echelon([columns[name] for name in ACTION_COLUMN_ORDER])
    pivot_indices = [coordinate_index[pivot] for pivot in pivots]
    quotient_indices = [
        index for index in range(len(coordinates)) if index not in pivot_indices
    ]
    image_support = set().union(
        *(set(columns[name]) for name in ACTION_COLUMN_ORDER)
    )
    zero_image_indices = [
        coordinate_index[coordinate]
        for coordinate in coordinates
        if coordinate not in image_support
    ]
    total_source: Vector = {}
    for name in SOURCE_ORDER:
        total_source = _vector_add(total_source, sources[name])
    normalized_residual = _vector_add(
        _vector_add(
            total_source,
            columns["z_10"],
            (Fraction(-1), Fraction(0)),
        ),
        columns["z_11"],
        (Fraction(-1), Fraction(0)),
    )
    payload = {
        "schema": "closed-universe-berger-common-action-obstruction-module-payload-v1",
        "result_id": "BERGER_COMMON_ACTION_OBSTRUCTION_MODULE_PAYLOAD",
        "coefficient_field": "Q(sqrt(10)) with formal coefficient monomials as a free basis",
        "orbit_definition": {
            "background": "same pinned Berger clock background",
            "output_row": 52,
            "output_row_id": "tau_star",
            "bidegree": [0, 0],
            "q1_source": "emitter",
            "q2_sources": list(SOURCE_ORDER),
            "old_input_suborbit": (
                "all switch-specialized ordered A rows 55--58 crossed with "
                "K rows 84--95, in both input orders, with every PBW key and "
                "formal coefficient monomial retained"
            ),
            "completeness_rule": (
                "filter the complete recomputed source-pair rows by old A--K "
                "row membership only; no key, jet order, or coefficient is "
                "selected by its value"
            ),
        },
        "coordinate_basis": [_coordinate(coordinate) for coordinate in coordinates],
        "vectors": {
            **{
                name: _vector_entries(sources[name], coordinate_index)
                for name in SOURCE_ORDER
            },
            **{
                name: _vector_entries(columns[name], coordinate_index)
                for name in ACTION_COLUMN_ORDER
            },
            "source_total": _vector_entries(total_source, coordinate_index),
            "normalized_110_residual": _vector_entries(
                normalized_residual, coordinate_index
            ),
        },
        "canonical_linear_reduction": {
            "column_order": list(ACTION_COLUMN_ORDER),
            "pivot_coordinate_indices": pivot_indices,
            "cokernel_representative_coordinate_indices": quotient_indices,
            "coordinate_functionals_annihilating_the_entire_image": (
                zero_image_indices
            ),
        },
    }
    audit = {
        "sources": sources,
        "columns": columns,
        "coordinates": coordinates,
        "coordinate_index": coordinate_index,
        "pivots": pivots,
        "zero_image_indices": zero_image_indices,
        "total_source": total_source,
        "normalized_residual": normalized_residual,
    }
    return payload, audit


def build_certificate(
    payload: dict[str, Any], audit: dict[str, Any]
) -> dict[str, Any]:
    values = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    sources: dict[str, Vector] = audit["sources"]
    columns: dict[str, Vector] = audit["columns"]
    coordinates: list[Coordinate] = audit["coordinates"]
    coordinate_index: dict[Coordinate, int] = audit["coordinate_index"]
    image_columns = [columns[name] for name in ACTION_COLUMN_ORDER]
    image_rank = exact_rank(image_columns)
    codomain_dimension = len(coordinates)
    source_counts = {name: len(sources[name]) for name in SOURCE_ORDER}
    column_counts = {name: len(columns[name]) for name in ACTION_COLUMN_ORDER}
    if source_counts != {"emitter_Diff_BV": 228, "base_maxwell_typed": 120}:
        raise AssertionError(f"source orbit drifted: {source_counts}")
    if column_counts != {"z_00": 30, "z_01": 30, "z_10": 90, "z_11": 90}:
        raise AssertionError(f"action image drifted: {column_counts}")
    if (codomain_dimension, image_rank, len(audit["zero_image_indices"])) != (
        444,
        4,
        204,
    ):
        raise AssertionError("obstruction-module dimensions drifted")

    g0_h0 = _monomial(
        replay.generator("parameter", "g0"),
        replay.generator("profile", "h0"),
    )
    g1_h1 = _monomial(
        replay.generator("parameter", "g1"),
        replay.generator("profile", "h1"),
    )
    prior_coordinate = (PRIOR_WITNESS_KEY, g0_h0)
    second_prior_coordinate = (SECOND_EMITTER_PRIOR_WITNESS_KEY, g1_h1)
    typed_coordinate = (SECOND_WITNESS_KEY, g0_h0)
    emitter_outside = min(set(sources["emitter_Diff_BV"]) - set().union(
        *(set(column) for column in image_columns)
    ))
    for coordinate in (prior_coordinate, second_prior_coordinate, typed_coordinate):
        if coordinate not in coordinate_index:
            raise AssertionError(f"missing decisive coordinate: {coordinate}")
    if (
        sources["emitter_Diff_BV"][prior_coordinate] != ONE
        or columns["z_10"][prior_coordinate] != ONE
        or sources["emitter_Diff_BV"][second_prior_coordinate] != ONE
        or columns["z_11"][second_prior_coordinate] != ONE
    ):
        raise AssertionError("prior-witness action projection drifted")
    if sources["base_maxwell_typed"][typed_coordinate] != (
        Fraction(-2),
        Fraction(0),
    ):
        raise AssertionError("typed-Maxwell obstruction projection drifted")
    if any(typed_coordinate in column for column in image_columns):
        raise AssertionError("typed-Maxwell obstruction entered the action image")

    source_augmented_ranks = {
        name: exact_rank(image_columns + [sources[name]]) for name in SOURCE_ORDER
    }
    total_augmented_rank = exact_rank(image_columns + [audit["total_source"]])
    if source_augmented_ranks != {
        "emitter_Diff_BV": 5,
        "base_maxwell_typed": 5,
    } or total_augmented_rank != 5:
        raise AssertionError("source-pair cokernel classification drifted")

    incidence = [[1, 0, -1], [1, -1, 0], [0, 1, -1]]
    cycle = [1, -1, -1]
    valuation = [1, 0, 0]
    if _rank_rational(incidence) != 2:
        raise AssertionError("normalization incidence rank drifted")
    if [
        sum(cycle[row] * incidence[row][column] for row in range(3))
        for column in range(3)
    ] != [0, 0, 0]:
        raise AssertionError("cycle functional ceased to annihilate redefinitions")
    cycle_projection = sum(
        left * right for left, right in zip(cycle, valuation, strict=True)
    )
    if cycle_projection != 1:
        raise AssertionError("H=2 valuation projection drifted")

    payload_ref = {
        "path": str(PAYLOAD.relative_to(ROOT)),
        "result_id": payload["result_id"],
        "sha256": hashlib.sha256(
            (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
        ).hexdigest(),
        "canonical_sha256": canonical_sha256(payload),
    }
    return {
        "schema": "closed-universe-berger-common-action-obstruction-module-v1",
        "result_id": "BERGER_COMMON_ACTION_OBSTRUCTION_MODULE",
        "setting_id": values["component_contract"]["setting_id"],
        "claim_status": "CERTIFIED_SCOPED_COMMON_ACTION_OBSTRUCTION_MODULE",
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
        "payload_ref": payload_ref,
        "normalization_cokernel": {
            "coefficient_domain": (
                "prime-valuation lattice tensored with Q; displayed prime p=2"
            ),
            "edge_order": ["Maxwell_tau", "Maxwell_emitter", "emitter_tau"],
            "field_scale_order": ["Maxwell", "emitter", "tau"],
            "field_redefinition_incidence": incidence,
            "rank": 2,
            "cokernel_dimension": 1,
            "primitive_cycle_functional": cycle,
            "frozen_edge_ratios": [2, 1, 1],
            "frozen_v2_vector": valuation,
            "cycle_projection": cycle_projection,
            "recovered_holonomy": "H=2",
            "invariance": (
                "every rational field rescaling adds an incidence-column "
                "valuation vector, annihilated by (1,-1,-1)"
            ),
        },
        "action_to_ward_map": {
            "domain_parameters": {
                "unary": ["u_0=mu", "u_1=lambda"],
                "hessian": ["beta_0", "beta_1"],
                "pairing": "p!=0",
                "field_redefinition": (
                    "chi -> r chi, chi_plus -> r^-1 chi_plus; "
                    "u_s -> r u_s, beta_b -> r^-1 beta_b"
                ),
            },
            "invariant_product_coordinates": (
                "z_sb=u_s*beta_b/p, s,b in {0,1}"
            ),
            "nonlinear_action_locus": {
                "matrix": [["z_00", "z_01"], ["z_10", "z_11"]],
                "equation": "z_00*z_11-z_01*z_10=0",
                "description": "rank-at-most-one Segre cone",
                "normalized_110_point": [[0, 0], [-1, -1]],
                "normalized_point_satisfies_equation": True,
            },
            "linear_envelope": {
                "column_order": list(ACTION_COLUMN_ORDER),
                "codomain_dimension": codomain_dimension,
                "image_rank": image_rank,
                "cokernel_dimension": codomain_dimension - image_rank,
                "canonical_pivot_count": len(audit["pivots"]),
                "canonical_quotient_representative_count": (
                    codomain_dimension - image_rank
                ),
                "zero_image_coordinate_functional_count": len(
                    audit["zero_image_indices"]
                ),
            },
            "field_redefinition_quotient": (
                "the four z_sb are invariant under the admissible pair "
                "rescaling, so both the Segre equation and the image/cokernel "
                "are quotient-defined"
            ),
        },
        "complete_declared_source_pair_orbit": {
            "scope": payload["orbit_definition"],
            "source_coordinate_counts": source_counts,
            "action_column_coordinate_counts": column_counts,
            "codomain_basis_sha256": canonical_sha256(
                payload["coordinate_basis"]
            ),
            "source_pair_cokernel_classification": {
                "emitter_Diff_BV": {
                    "augmented_rank": source_augmented_ranks["emitter_Diff_BV"],
                    "status": "NONZERO_COKERNEL_CLASS",
                    "coordinate_projection": coordinate_index[emitter_outside],
                    "coefficient": _scalar(
                        sources["emitter_Diff_BV"][emitter_outside]
                    ),
                },
                "base_maxwell_typed": {
                    "augmented_rank": source_augmented_ranks[
                        "base_maxwell_typed"
                    ],
                    "status": "NONZERO_COKERNEL_CLASS",
                    "coordinate_projection": coordinate_index[typed_coordinate],
                    "coefficient": _scalar(
                        sources["base_maxwell_typed"][typed_coordinate]
                    ),
                },
                "source_total": {
                    "augmented_rank": total_augmented_rank,
                    "status": "NONZERO_COKERNEL_CLASS",
                },
            },
            "prior_projection_recovery": [
                {
                    "coordinate": coordinate_index[prior_coordinate],
                    "source_coefficient": _scalar(ONE),
                    "image_column": "z_10",
                    "image_coefficient": _scalar(ONE),
                    "normalized_parameter": -1,
                    "residual": _scalar(ZERO),
                },
                {
                    "coordinate": coordinate_index[second_prior_coordinate],
                    "source_coefficient": _scalar(ONE),
                    "image_column": "z_11",
                    "image_coefficient": _scalar(ONE),
                    "normalized_parameter": -1,
                    "residual": _scalar(ZERO),
                },
            ],
            "typed_maxwell_projection_recovery": {
                "coordinate": coordinate_index[typed_coordinate],
                "ward_key": _coordinate(typed_coordinate),
                "source_coefficient": _scalar(
                    sources["base_maxwell_typed"][typed_coordinate]
                ),
                "all_action_columns_zero": True,
                "normalized_110_residual_coefficient": _scalar(
                    audit["normalized_residual"][typed_coordinate]
                ),
                "display": "-2 g0 h0",
            },
        },
        "minimal_lower_bound_theorem": {
            "theorem": (
                "Any common-action extension of the frozen component embedding "
                "that repairs the displayed orbit must contain at least one "
                "nondegenerate complementary degree-(0,1) pair and must have "
                "an auxiliary old-field Hessian with nonzero A_0--K_12 "
                "component projection. Increasing only the outer scalar unary "
                "PBW jet order of the metric-natural <K,dA> Hessian cannot "
                "supply that projection at any finite order, because outer "
                "derivatives alter words and coefficients but not old row "
                "labels. Therefore a new A--K tensor/representation channel "
                "(for example a declared clock/frame or parity-odd insertion) "
                "or a different carrier mechanism is necessary."
            ),
            "carrier_pair_lower_bound": 1,
            "required_degrees": [0, 1],
            "required_hessian_projection": "A_0--K_12 nonzero",
            "outer_scalar_jet_order_alone": "INSUFFICIENT_AT_EVERY_FINITE_ORDER",
            "representation_content": (
                "must leave the declared metric-natural <K,dA> Hessian "
                "component support or use a different carrier mechanism"
            ),
            "additional_pair_count_beyond_one": "OPEN",
            "sufficiency_of_clock_frame_or_parity_odd_insertion": "OPEN",
        },
        "proof_obligation_dag": [
            {"id": "P1_NORMALIZATION_COKERNEL", "status": "CERTIFIED"},
            {"id": "P2_COMPLETE_DECLARED_ORBIT", "status": "CERTIFIED"},
            {"id": "P3_ACTION_MAP_MODULO_REDEFINITION", "status": "CERTIFIED"},
            {"id": "P4_EXACT_IMAGE_AND_COKERNEL", "status": "CERTIFIED"},
            {"id": "P5_WITNESS_PROJECTIONS", "status": "CERTIFIED"},
            {"id": "P6_MINIMAL_NECESSARY_LOWER_BOUND", "status": "CERTIFIED"},
            {
                "id": "P7_SMALLEST_SUFFICIENT_EXTENSION",
                "status": "OPEN_NOT_REQUIRED_AFTER_LOWER_BOUND",
            },
        ],
        "mutations": {
            "replace_typed_factor_two_by_one": {
                "v2_vector": [0, 0, 0],
                "cycle_projection": 0,
                "detected": True,
                "scientific_status": "MUTATION_ONLY_NOT_A_REPAIR",
            },
            "drop_typed_maxwell_source": {
                "typed_projection_after_drop": _scalar(ZERO),
                "detected": True,
            },
            "inject_forbidden_A0_K12_hessian_coordinate": {
                "typed_projection_enters_linear_envelope": True,
                "detected": True,
                "scientific_status": (
                    "SUPPORT_MUTATION_ONLY; no cyclic action or original Ward "
                    "substitution is claimed"
                ),
            },
            "break_rank_one_product_relation": {
                "z_matrix": [[1, 0], [0, 1]],
                "determinant": 1,
                "rejected_by_nonlinear_action_locus": True,
            },
        },
        "activation_disposition": {
            "obstruction_module_reusable": True,
            "smallest_sufficient_extension_found": False,
            "new_common_action_candidate_exists": False,
            "complete_arity_two_identity": False,
            "q3_authorized": False,
            "K_Berger_equivariance_authorized": False,
            "observer_morphism_stability_authorized": False,
            "detector_response_on_second_order_cone_authorized": False,
            "physical_branch_bridge_activated": False,
            "quantum_promotion_authorized": False,
        },
        "next_gate": (
            "DECLARE_A_COMPLETE_ACTION_BASIS_WITH_NONZERO_A0_K12_HESSIAN_"
            "PROJECTION_THEN_RECOMPUTE_THIS_MAP_AND_SUBSTITUTE_THE_ORIGINAL_WARD_ROW"
        ),
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE result replaces two serial "
            "ansatz checks by a reusable obstruction module on one explicitly "
            "declared same-background source-pair orbit. The orbit contains "
            "every switch-specialized tau_star coefficient with emitter q1, "
            "either emitter_Diff_BV or typed-Maxwell q2, and old A rows 55--58 "
            "crossed with massive-two-form K rows 84--95 in either order. "
            "Formal coefficient monomials are independent and coefficients lie "
            "in Q(sqrt(10)). The action-to-Ward map is computed for the complete "
            "bounded 110-row action class inherited from its certified no-go. "
            "Modulo the admissible pair rescaling it factors through four "
            "invariant products z_sb constrained by the rank-one Segre equation. "
            "Its four-column linear envelope has exact rank four in a "
            "444-dimensional codomain and exact cokernel dimension 440. Both "
            "declared source-pair vectors and their sum define nonzero cokernel "
            "classes. Coordinate projections recover cancellation of the two "
            "old +g_b h_b witnesses and the surviving typed-Maxwell coefficient "
            "-2 g0 h0. Independently, the prime-valuation incidence cokernel of "
            "the normalization triangle is one-dimensional and its 2-adic "
            "cycle projection recovers H=2. The lower-bound theorem applies to "
            "extensions that preserve the frozen component embedding and try "
            "to enlarge only the outer scalar unary jet of the metric-natural "
            "<K,dA> Hessian: such derivatives never change A/K row labels, so "
            "a nonzero A_0--K_12 Hessian projection is necessary and scalar "
            "outer jet order alone is insufficient at every finite order. At "
            "least one degree-(0,1) conjugate pair is also necessary; whether "
            "one broader pair suffices, whether two pairs are required, and "
            "which clock/frame or parity-odd representation is smallest remain "
            "OPEN. No claim is made against arbitrary higher actions or "
            "carriers. No new action candidate is fitted or promoted, and no "
            "q3, K_Berger, observer-morphism, detector, tangent-cone, causal, "
            "branch, particle, positivity, Conflux, or quantum conclusion is "
            "authorized. No compact-product mode is identified with a Berger row."
        ),
        "provenance": {
            "science_forge_work_item": (
                "sf:program/work/observer-common-action-obstruction-module"
            ),
            "input_commit": "2077af36",
            "source_manifest": [
                {
                    "path": str(path.relative_to(ROOT)),
                    "sha256": sha256(path),
                }
                for path in SOURCE_FILES
            ],
        },
    }


def report(value: dict[str, Any]) -> str:
    linear = value["action_to_ward_map"]["linear_envelope"]
    return f"""# Berger common-action obstruction module

## Result

The two previous failures are now projections of reusable exact cokernels.
For the normalization triangle, the field-rescaling incidence map has rank
two and one-dimensional cokernel.  Its primitive cycle functional is
`(1,-1,-1)`; applied to the 2-adic edge-valuation vector `(1,0,0)` it gives
one, recovering the invariant holonomy `H=2`.

For the declared `tau_star` old-`A`--`K` orbit, every coefficient from emitter
`q1` crossed with either `emitter_Diff_BV` or `base_maxwell_typed` `q2` was
recomputed.  The complete bounded conjugate-pair action descends modulo pair
rescaling to

```text
z_sb = u_s beta_b / p,
z_00 z_11 - z_01 z_10 = 0.
```

Its four-column linear envelope has exact rank
`{linear['image_rank']}` in a `{linear['codomain_dimension']}`-dimensional
`Q(sqrt(10))` coefficient space, hence cokernel dimension
`{linear['cokernel_dimension']}`.  Both complete source-pair vectors raise
the rank to five and therefore define nonzero cokernel classes.

The normalized point `[[0,0],[-1,-1]]` cancels the two earlier
`+g_b h_b` projections.  It cannot alter

```text
tau_star <- (e1 A_0, e2 K0_12): -2 g0 h0,
```

because all four action-image columns vanish on that coordinate.

## Lower bound

Any repair preserving the frozen component embedding needs at least one
nondegenerate degree-`(0,1)` conjugate pair and an auxiliary action Hessian
with nonzero `A_0--K_12` projection.  Raising only the outer scalar PBW jet
order of `<K,dA>` cannot work at any finite order: it changes words and
coefficients, not the old component labels.  A new tensor/representation
channel or another carrier mechanism is necessary, but its sufficiency and
the number of pairs beyond one remain open.

No new action candidate, q3, detector, cone, causal, branch, Conflux, or
quantum claim is promoted.

CLOSE-OUT: DONE — the scoped action-to-Ward map, exact cokernels, witness projections, and a necessary minimal lower-bound theorem are certified
EVIDENCE: closed_universe_observers/certificates/BERGER_COMMON_ACTION_OBSTRUCTION_MODULE.json
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
    rendered_payload = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    value = build_certificate(payload, audit)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
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
        raise SystemExit("stale Berger common-action obstruction module")
    print("BERGER_COMMON_ACTION_OBSTRUCTION_MODULE generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
