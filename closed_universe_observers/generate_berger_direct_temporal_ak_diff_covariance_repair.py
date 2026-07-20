#!/usr/bin/env python3
"""Test the complete minimal temporal A--K scalar-density action module."""

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
    _multiindex_from_word,
    serialize,
)
from closed_universe_observers.generate_berger_108_row_emitter_physical_q2_pbw import (
    Action,
    action_add,
    differential_slots,
    form_bilinear_base,
    parameter,
    product,
    profile,
    scale,
)
from closed_universe_observers.generate_berger_110_row_conjugate_pair_extension_no_go import (
    CHI,
    extension_q1,
)
from closed_universe_observers.generate_berger_auxiliary_diff_bv_scalar_orbit_repair import (
    scalar_diff_q2,
)
from closed_universe_observers.generate_berger_common_action_obstruction_module import (
    _echelon,
    _scalar_scale,
    _vector_add,
)
from closed_universe_observers.generate_berger_higher_jet_invariant_action_module_classification import (
    generalized_action_to_q2,
)
from closed_universe_observers.generate_berger_minimal_invariant_scalar_hessian_channel_no_go import (
    _action_entries,
)
from closed_universe_observers.generate_berger_order_three_common_action_promotion_gate import (
    parse_action,
)
from closed_universe_observers.generate_berger_quartic_completion_moduli_observer_invariance import (
    repair_action,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_DIRECT_TEMPORAL_AK_DIFF_COVARIANCE_REPAIR.json"
PAYLOAD = PACKAGE / "certificates/BERGER_DIRECT_TEMPORAL_AK_DIFF_COVARIANCE_REPAIR_PAYLOAD.json"
SCHEMA = PACKAGE / "schema/berger-direct-temporal-ak-diff-covariance-repair-v1.schema.json"
PAYLOAD_SCHEMA = PACKAGE / "schema/berger-direct-temporal-ak-diff-covariance-repair-payload-v1.schema.json"
REPORT = PACKAGE / "reports/berger-direct-temporal-ak-diff-covariance-repair.md"
ORDER_THREE_PAYLOAD = (
    PACKAGE / "certificates/BERGER_ORDER_THREE_COMMON_ACTION_PROMOTION_GATE_PAYLOAD.json"
)
DEPENDENCIES = {
    "predecessor": PACKAGE
    / "certificates/BERGER_AUXILIARY_DIFF_BV_SCALAR_ORBIT_REPAIR.json",
    "predecessor_payload": PACKAGE
    / "certificates/BERGER_AUXILIARY_DIFF_BV_SCALAR_ORBIT_REPAIR_PAYLOAD.json",
    "order_three": PACKAGE
    / "certificates/BERGER_ORDER_THREE_COMMON_ACTION_PROMOTION_GATE.json",
    "order_three_payload": ORDER_THREE_PAYLOAD,
    "complete_q1": PACKAGE
    / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
    "complete_q2": PACKAGE / "certificates/BERGER_108_ROW_COMPLETE_Q2_PBW.json",
    "complete_q2_payload": PACKAGE
    / "certificates/BERGER_108_ROW_COMPLETE_Q2_PBW_PAYLOAD.json",
    "emitter_diff_q2": PACKAGE
    / "certificates/BERGER_108_ROW_EMITTER_DIFF_BV_Q2_PBW.json",
    "component_contract": PACKAGE
    / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_direct_temporal_ak_diff_covariance_repair.py",
    PACKAGE / "tests/test_berger_direct_temporal_ak_diff_covariance_repair.py",
    SCHEMA,
    PAYLOAD_SCHEMA,
]

Scalar = tuple[Fraction, Fraction]
Coordinate = tuple[tuple, tuple]
Vector = dict[Coordinate, Scalar]
PROJECTION_OUTPUTS = (52, 59)
ONE: Scalar = (Fraction(1), Fraction(0))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def add_tensor(
    target: arity.GradedBilinearRows,
    tensor: dict,
    factor: Scalar = ONE,
) -> None:
    for (output, left, left_word, right, right_word), coefficient in tensor.items():
        arity.add_bilinear_term(
            target[(0, 0)].setdefault(output, {}),
            (left, left_word, right, right_word),
            replay.scale(coefficient, factor),
        )


def profile_action(emitter: int, sector: str) -> Action:
    """Return the two missing clock-normal first-profile-jet scalar lines."""

    if sector not in {"electric", "magnetic"}:
        raise ValueError("profile sector must be electric or magnetic")
    action: Action = {}
    coefficient = product(
        parameter(f"g{emitter}"), profile(f"h{emitter}", (1,))
    )
    k_offset = 84 + 6 * emitter
    d_a = differential_slots(1, 55)
    components = range(3) if sector == "electric" else range(3, 6)
    for component in components:
        metric = form_bilinear_base(2, component, component)
        for a_factor, a_coefficient in d_a[component]:
            action_add(
                action,
                ((CHI, ()), (k_offset + component, ()), a_factor),
                scale(
                    coefficient,
                    (
                        metric * a_coefficient[0],
                        metric * a_coefficient[1],
                    ),
                ),
            )
    expected = {"electric": 6, "magnetic": 9}[sector]
    if len(action) != expected:
        raise AssertionError(f"{sector} profile action support drifted")
    return action


def extended_q1() -> tuple[replay.GradedOperator, dict]:
    q1 = arity.completed_q1()
    q1[(0, 0)].update(extension_q1(temporal_order=0))
    indexed = {degree: arity.q1_rows(operator) for degree, operator in q1.items()}
    return q1, indexed


def base_q2() -> arity.GradedBilinearRows:
    q2 = arity.load_q2()
    add_tensor(q2, generalized_action_to_q2(repair_action()))
    add_tensor(q2, scalar_diff_q2())
    return q2


def projection_defect(
    q1: replay.GradedOperator,
    indexed_q1: dict,
    q2: arity.GradedBilinearRows,
    emitter: int,
) -> Vector:
    rows = {
        output: row
        for output in PROJECTION_OUTPUTS
        if (
            row := arity.arity_two_row(
                output,
                (0, 0),
                q1,
                q2,
                arity.parities() + (0, 1),
                indexed_q1,
            )
        )
    }
    specialized = arity.specialize_bilinear_rows(rows)
    parameter_name = f"g{emitter}"
    return {
        ((output, *key), monomial): coefficient
        for output, row in specialized.items()
        for key, polynomial in row.items()
        for monomial, coefficient in polynomial.items()
        if any(
            factor[0] == "parameter" and factor[1] == parameter_name
            for factor in monomial
        )
    }


def action_column(
    q1: replay.GradedOperator,
    indexed_q1: dict,
    action: Action,
    emitter: int,
) -> Vector:
    q2 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
    add_tensor(q2, generalized_action_to_q2(action))
    return projection_defect(q1, indexed_q1, q2, emitter)


def action_columns(
    q1: replay.GradedOperator,
    indexed_q1: dict,
    emitter: int,
) -> tuple[list[str], list[Vector], list[Action]]:
    payload = json.loads(ORDER_THREE_PAYLOAD.read_text())
    names: list[str] = []
    columns: list[Vector] = []
    actions: list[Action] = []
    for name, module in payload["modules"].items():
        if module["emitter"] != emitter:
            continue
        action = parse_action(module["action_entries"])
        names.append(name)
        actions.append(action)
        columns.append(action_column(q1, indexed_q1, action, emitter))
    for sector in ("electric", "magnetic"):
        action = profile_action(emitter, sector)
        names.append(f"profile_{sector}.emitter_{emitter}")
        actions.append(action)
        columns.append(action_column(q1, indexed_q1, action, emitter))
    if len(columns) != 934:
        raise AssertionError("complete temporal action-module dimension drifted")
    return names, columns, actions


def restrict_direct(vector: Vector, emitter: int) -> Vector:
    k_rows = range(84 + 6 * emitter, 90 + 6 * emitter)
    return {
        coordinate: coefficient
        for coordinate, coefficient in vector.items()
        if coordinate[0][0] == 52
        and (
            (
                55 <= coordinate[0][1] <= 58
                and coordinate[0][3] in k_rows
            )
            or (
                coordinate[0][1] in k_rows
                and 55 <= coordinate[0][3] <= 58
            )
        )
    }


def reduce_modulo(columns: list[Vector], source: Vector) -> tuple[int, int, Vector]:
    pivots, basis = _echelon(columns)
    augmented_rank = len(_echelon(columns + [source])[0])
    residual = dict(source)
    for pivot, existing in zip(pivots, basis, strict=True):
        if pivot in residual:
            residual = _vector_add(
                residual,
                existing,
                _scalar_scale(residual[pivot], Fraction(-1)),
            )
    return len(pivots), augmented_rank, residual


def scalar_json(value: Scalar) -> list[list[int]]:
    return [
        [value[0].numerator, value[0].denominator],
        [value[1].numerator, value[1].denominator],
    ]


def coordinate_json(coordinate: Coordinate, coefficient: Scalar) -> dict[str, Any]:
    (output, left, left_word, right, right_word), monomial = coordinate
    return {
        "output": output,
        "left_input": [left, list(left_word)],
        "right_input": [right, list(right_word)],
        "coefficient_monomial": [
            [kind, name, list(vertical), list(spacetime)]
            for kind, name, vertical, spacetime in monomial
        ],
        "coefficient": scalar_json(coefficient),
    }


def vector_manifest(vector: Vector) -> dict[str, Any]:
    entries = [
        coordinate_json(coordinate, coefficient)
        for coordinate, coefficient in sorted(vector.items())
    ]
    return {
        "coordinate_count": len(entries),
        "canonical_sha256": canonical_sha256(entries),
    }


def quartic_route_ledger(q1: replay.GradedOperator) -> list[dict[str, Any]]:
    rows = json.loads(DEPENDENCIES["component_contract"].read_text())[
        "carrier_contract"
    ]["rows"]
    row_ids = [row["row_id"] for row in rows]
    routes = []
    for (output, source, word), coefficient in sorted(q1[(0, 0)].items()):
        if output != 49 or not 27 <= source <= 36:
            continue
        routes.append(
            {
                "q3_output": source,
                "q3_output_row_id": row_ids[source],
                "q1_output": 49,
                "q1_output_row_id": "c_spatial_star_1",
                "q1_pbw_multiindex": list(_multiindex_from_word(word)),
                "q1_coefficient": serialize(coefficient),
                "candidate_quartic_action_support": (
                    f"{row_ids[source - 22]} * chi * A * K"
                ),
                "status": "NO_CERTIFIED_MAP",
            }
        )
    if len(routes) != 5:
        raise AssertionError("physical metric q1 preimage route count drifted")
    return routes


def build_payload() -> dict[str, Any]:
    q1, indexed_q1 = extended_q1()
    base = base_q2()
    profile_entries = {
        f"emitter_{emitter}_{sector}": _action_entries(
            profile_action(emitter, sector)
        )
        for emitter in (0, 1)
        for sector in ("electric", "magnetic")
    }
    audits = {}
    for emitter in (0, 1):
        source = projection_defect(q1, indexed_q1, base, emitter)
        names, columns, _actions = action_columns(q1, indexed_q1, emitter)
        direct_columns = [restrict_direct(column, emitter) for column in columns]
        direct_source = restrict_direct(source, emitter)
        direct_rank, direct_augmented, direct_residual = reduce_modulo(
            direct_columns, direct_source
        )
        full_rank, full_augmented, full_residual = reduce_modulo(columns, source)
        if direct_residual or direct_augmented != direct_rank:
            raise AssertionError("direct temporal projection was not repaired")
        if full_augmented != full_rank + 1 or not full_residual:
            raise AssertionError("full covariance projection obstruction drifted")
        first_coordinate, first_coefficient = min(full_residual.items())
        expected_key = (59, 3, (), 84 + 6 * emitter, (0, 1))
        if first_coordinate[0] != expected_key or first_coefficient != (
            Fraction(-3),
            Fraction(0),
        ):
            raise AssertionError("first full covariance quotient witness drifted")

        without_electric = columns[:-2] + [columns[-1]]
        without_magnetic = columns[:-1]
        electric_mutation = reduce_modulo(
            [restrict_direct(column, emitter) for column in without_electric],
            direct_source,
        )
        magnetic_mutation = reduce_modulo(
            [restrict_direct(column, emitter) for column in without_magnetic],
            direct_source,
        )

        diff_q2 = arity.load_q2(sources={"emitter_Diff_BV"})
        diff_column = projection_defect(q1, indexed_q1, diff_q2, emitter)
        free_diff_rank = len(_echelon(columns + [diff_column])[0])
        free_diff_augmented = len(
            _echelon(columns + [diff_column, source])[0]
        )
        if (free_diff_rank, free_diff_augmented) != (
            full_rank + 1,
            full_rank + 2,
        ):
            raise AssertionError("free Diff-orbit mutation stopped detecting")

        target_key = (
            (52, 55, (0, 1), 84 + 6 * emitter, ()),
            (
                ("parameter", f"g{emitter}", (), (0, 0, 0, 0)),
                ("profile", f"h{emitter}", (), (0, 0, 0, 0)),
            ),
        )
        target_columns = sum(target_key in column for column in direct_columns)
        if direct_source.get(target_key) != ONE or not target_columns:
            raise AssertionError("direct temporal Hessian target drifted")

        audits[f"emitter_{emitter}"] = {
            "action_column_order": names,
            "ambient_action_module": {
                "order_three_IBP_closed_U1_columns": 932,
                "clock_profile_scalar_density_columns": 2,
                "total_columns": 934,
                "contains_symmetry_constrained_ansatz_as_subspace": True,
                "reason": (
                    "the imported order-three module retains every differentiated "
                    "chi/K/A placement and both reflection parities; the two "
                    "clock-normal electric/magnetic h-prime lines close the only "
                    "missing coefficient grade"
                ),
            },
            "column_manifest": {
                "column_count": len(columns),
                "nonempty_column_count": sum(bool(column) for column in columns),
                "canonical_sha256": canonical_sha256(
                    [vector_manifest(column) for column in columns]
                ),
            },
            "direct_temporal_AK_projection": {
                "source_manifest": vector_manifest(direct_source),
                "action_image_rank": direct_rank,
                "source_augmented_rank": direct_augmented,
                "admissible": True,
                "target": coordinate_json(target_key, direct_source[target_key]),
                "target_reaching_column_count": target_columns,
            },
            "complete_covariance_projection": {
                "outputs": [52, 59],
                "source_manifest": vector_manifest(source),
                "action_image_rank": full_rank,
                "source_augmented_rank": full_augmented,
                "quotient_manifest": vector_manifest(full_residual),
                "first_quotient_witness": coordinate_json(
                    first_coordinate, first_coefficient
                ),
                "admissible": False,
            },
            "mutations": {
                "remove_electric_profile_line": {
                    "direct_image_rank": electric_mutation[0],
                    "direct_augmented_rank": electric_mutation[1],
                    "detected": electric_mutation[0] != electric_mutation[1],
                },
                "remove_magnetic_profile_line": {
                    "direct_image_rank": magnetic_mutation[0],
                    "direct_augmented_rank": magnetic_mutation[1],
                    "detected": magnetic_mutation[0] != magnetic_mutation[1],
                },
                "free_emitter_Diff_BV_normalization": {
                    "image_rank": free_diff_rank,
                    "source_augmented_rank": free_diff_augmented,
                    "detected": free_diff_augmented == free_diff_rank + 1,
                    "scientific_status": (
                        "MUTATION_ONLY: the inherited Diff representation is fixed"
                    ),
                },
            },
        }
    return {
        "schema": "closed-universe-berger-direct-temporal-ak-diff-covariance-repair-payload-v1",
        "result_id": "BERGER_DIRECT_TEMPORAL_AK_DIFF_COVARIANCE_REPAIR_PAYLOAD",
        "coefficient_field": "Q(sqrt(10)) differential switch-jet algebra",
        "profile_scalar_density_action_entries": profile_entries,
        "emitter_audits": audits,
        "quartic_descendant_route_ledger": quartic_route_ledger(q1),
        "imported_arity_three_witness": {
            "output": 49,
            "output_row_id": "c_spatial_star_1",
            "inputs": [
                [55, [0, 0, 2], "A_0"],
                [CHI, [], "chi"],
                [87, [], "K0_12"],
            ],
            "coefficient": [[-4, 1], [0, 1]],
            "status": "NOT_REPLAYED_AFTER_EMPTY_ARITY_TWO_LOCUS",
        },
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    dependencies = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    rendered_payload = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    first = payload["emitter_audits"]["emitter_0"][
        "complete_covariance_projection"
    ]["first_quotient_witness"]
    return {
        "schema": "closed-universe-berger-direct-temporal-ak-diff-covariance-repair-v1",
        "result_id": "BERGER_DIRECT_TEMPORAL_AK_DIFF_COVARIANCE_REPAIR",
        "setting_id": dependencies["predecessor"]["setting_id"],
        "claim_status": "OBSTRUCTED_COMPLETE_TEMPORAL_SCALAR_DENSITY_MODULE_FAILS_FULL_ARITY_TWO_COVARIANCE",
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": value.get("result_id", path.stem),
                "sha256": sha256(path),
            }
            for (name, path), value in zip(
                DEPENDENCIES.items(), dependencies.values(), strict=True
            )
        },
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": hashlib.sha256(rendered_payload.encode()).hexdigest(),
        },
        "proof_first_structure": {
            "mathematical_target": (
                "the smallest same-background local action enlargement whose "
                "Hessian reaches the direct temporal A--K witness and whose "
                "Diff covariance can seed the required quartic metric descendant"
            ),
            "candidate_theorem": (
                "the complete bounded scalar-density action module has a "
                "nonempty q1/q2 master locus before quartic completion"
            ),
            "falsifier": (
                "the exact source raises the complete action-image rank on the "
                "joint tau-star/A-plus-zero covariance projection"
            ),
        },
        "complete_action_ansatz": {
            "bounds": {
                "carrier": "the repaired 110-row Berger carrier",
                "field_arity": "cubic at the arity-two gate",
                "total_derivative_order": "three in the exact g_b h_b grade",
                "profile_completion": (
                    "both electric and magnetic clock-normal g_b h_b-prime "
                    "scalar-density lines"
                ),
                "integration_by_parts": (
                    "all differentiated chi, K and A placements retained before "
                    "the imported IBP normal form"
                ),
                "parity": "both reflection parities",
                "symmetry": (
                    "the Diff x Weyl x Maxwell x Berger-U(1) ansatz is a "
                    "subspace of the tested 934-column ambient module"
                ),
            },
            "ambient_superset_argument": (
                "Failure in the 934-dimensional ambient action image is stronger "
                "than failure in its symmetry-constrained scalar-density subspace; "
                "no selected coefficient subfamily is called complete."
            ),
            "per_emitter_dimension": 934,
            "two_emitter_dimension": 1868,
            "q1_change": "NONE",
            "q3_status": (
                "NO_CERTIFIED_MAP: no q1-closed cubic coefficient point exists "
                "from which a common-action quartic Taylor descendant can be derived"
            ),
        },
        "nilpotency_and_cyclicity": {
            "q1_nilpotency": "CERTIFIED_BY_UNCHANGED_IMPORTED_COMPLETE_Q1",
            "q2_odd_cyclicity": (
                "CERTIFIED_COLUMNWISE: every tested q2 column is the Euler "
                "Hessian of one serialized cubic action"
            ),
            "Maxwell_invariance": (
                "the admissible Maxwell-invariant family is contained in the "
                "larger tested ambient module"
            ),
            "Weyl_and_Berger_U1": (
                "the neutral clock-normal scalar-density family is contained in "
                "the exact imported U1 kernel; both reflection sectors are retained"
            ),
        },
        "arity_two_gate": {
            "status": "OBSTRUCTED",
            "direct_temporal_projection": (
                "CERTIFIED_REPAIRABLE_INSIDE_THE_COMPLETE_AMBIENT_MODULE"
            ),
            "full_covariance_projection": "EMPTY_ADMISSIBLE_LOCUS",
            "per_emitter_audits": payload["emitter_audits"],
            "decisive_witness": first,
            "theorem": (
                "For each emitter, 934 action columns span the complete direct "
                "temporal A--K source projection, but the source raises their "
                "rank from 934 to 935 on outputs tau_star and A_plus_0. Hence "
                "every action in the declared ambient module retains a nonzero "
                "arity-two covariance defect."
            ),
        },
        "arity_three_and_quartic_gate": {
            "status": "NOT_REACHED_AFTER_EMPTY_ARITY_TWO_LOCUS",
            "candidate_metric_routes": payload["quartic_descendant_route_ledger"],
            "imported_diagnostic": payload["imported_arity_three_witness"],
            "reason": (
                "q3 cannot enter the arity-two identity, and a quartic Taylor "
                "orbit cannot be promoted from a cubic action that fails q1 closure"
            ),
        },
        "first_missing_action_representation": {
            "object": (
                "a new temporal Maxwell/emitter antifield covariance module, "
                "beginning with A-plus/tau/K and cyclic K-plus/tau/A descendants"
            ),
            "selected_support": (
                "q2 preimages whose q1 image reaches "
                "A_plus_0 <- (tau,e0 e1 K0_01)"
            ),
            "why_existing_Diff_orbit_is_insufficient": (
                "even freeing the inherited emitter Diff-BV normalization adds "
                "one image rank and the source adds another"
            ),
        },
        "K_Berger_and_observer_disposition": {
            "K_Berger_compatibility": (
                "OBSTRUCTED before the nonlinear observer-morphism gate; "
                "background U1 invariance is not a K_Berger theorem"
            ),
            "gauge_reduction": "OBSTRUCTED_AT_ARITY_TWO",
            "detector_response": "NO_CERTIFIED_MAP",
            "response_rank": "NO_CERTIFIED_MAP",
            "redshift_memory_recoil_tangent_cone": "NO_CERTIFIED_MAP",
            "physical_branch_bridge": "INACTIVE",
            "quantum_claim": False,
        },
        "mutations": {
            "representation_removal": (
                "removing either clock-profile scalar line raises the direct "
                "projection rank when its source is appended"
            ),
            "coefficient_mutation": (
                "freeing the fixed emitter Diff-BV normalization still leaves "
                "an independent quotient class"
            ),
            "source_isolation": (
                "the decisive quotient is in the Maxwell-cotangent temporal "
                "covariance row, not the already repairable tau-star A--K row"
            ),
        },
        "proof_obligation_dag": [
            {"id": "P1_IMPORT_PINNED_PREDECESSOR", "status": "CERTIFIED"},
            {"id": "P2_COMPLETE_AMBIENT_ACTION_MODULE", "status": "CERTIFIED"},
            {"id": "P3_ACTION_DERIVED_Q2_AND_CYCLICITY", "status": "CERTIFIED"},
            {"id": "P4_DIRECT_TEMPORAL_HESSIAN_IMAGE", "status": "CERTIFIED"},
            {"id": "P5_FULL_ARITY_TWO_COVARIANCE", "status": "OBSTRUCTED"},
            {"id": "P6_QUARTIC_Q3_MASTER_IDENTITY", "status": "NO_CERTIFIED_MAP"},
            {"id": "P7_K_BERGER_OBSERVER_RESPONSE", "status": "NO_CERTIFIED_MAP"},
        ],
        "assumption_ledger": [
            "The frozen 108-row action, repaired auxiliary pair and exact relational switch specialization are imported unchanged.",
            "The tested 934-column family is an ambient superset of the bounded symmetry-constrained scalar-density ansatz.",
            "No compact-product mode is identified with a Berger carrier row.",
        ],
        "missing_object_ledger": [
            "temporal Maxwell/emitter antifield covariance action module",
            "q1-closed common cubic action",
            "common-action quartic Diff-covariance Taylor orbit",
            "full arity-three and K_Berger observer-morphism replay",
            "detector, redshift, memory, recoil and tangent-cone restriction",
        ],
        "next_gate": (
            "ADJOIN_TEMPORAL_MAXWELL_EMITTER_ANTIFIELD_COVARIANCE_MODULE_"
            "AND_REPLAY_ARITY_TWO_BEFORE_ANY_Q3_OR_OBSERVER_PROPAGATION"
        ),
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE obstruction imports the "
            "auxiliary scalar-orbit repair from commit fbc422cfa by content "
            "hash. Per emitter it tests all 932 imported IBP-closed order-three "
            "U1 action columns together with the two missing electric/magnetic "
            "clock-profile scalar-density lines. This 934-column ambient module "
            "contains the bounded Diff/Weyl/Maxwell/U1 scalar-density ansatz and "
            "therefore gives it more, not less, cancellation freedom. The direct "
            "tau-star A--K projection is in the action image. On the joint "
            "tau-star/A-plus-zero covariance projection, however, the source "
            "raises the exact rank from 934 to 935. The first quotient "
            "coefficient is A_plus_0 <- (tau,e0 e1 K0_01) = -3 g0 h0. "
            "Freeing the inherited emitter Diff-BV normalization does not remove "
            "the quotient. Thus the current carrier lacks a temporal "
            "Maxwell/emitter antifield covariance representation; no q1-closed "
            "cubic action and hence no common-action quartic q3 descendant exists. "
            "The imported -4 g0 h0 arity-three witness is retained only as a "
            "diagnostic. No K_Berger, detector, redshift, memory, recoil, "
            "tangent-cone, branch, particle, positivity, phenomenology, "
            "scattering or quantum claim is promoted."
        ),
        "provenance": {
            "science_forge_work_item": (
                "sf:program/work/observer-direct-temporal-ak-hessian-diff-covariance-repair"
            ),
            "input_commit": "fbc422cfa",
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
    gate = value["arity_two_gate"]
    witness = gate["decisive_witness"]
    return f"""# Direct temporal A--K and Diff-covariance repair

The complete bounded test gives the candidate repair more freedom than the
symmetry-constrained family: all 932 imported order-three action columns per
emitter, both reflection parities and differentiated chi/K/A placements, plus
the electric and magnetic clock-profile scalar-density lines.  Every q2
column is an exact Hessian of one serialized action.

The direct temporal A--K projection is repairable.  Its action image and
source-augmented ranks are both 934 for each emitter, so the displayed
`tau_star <- (e0 e1 A_0,K0_01)` coefficient is not itself a no-go.

The full covariance projection fails.  On the joint `tau_star` and
`A_plus_0` rows the action-image rank is 934 and the source-augmented rank is
935.  The first exact quotient coefficient is

```text
A_plus_0 <- (tau, e0 e1 K0_01) = -3 g0 h0.
```

The quotient has `{gate['per_emitter_audits']['emitter_0']['complete_covariance_projection']['quotient_manifest']['coordinate_count']}`
coordinates on the two-row falsifying projection.  Even treating the fixed
emitter Diff--BV normalization as a free mutation adds one image rank while
the source adds another.  The missing representation is therefore a temporal
Maxwell/emitter antifield covariance module beginning with A-plus/tau/K and
its cyclic K-plus/tau/A descendants.

Because the arity-two admissible locus is empty, no common-action quartic
Taylor descendant or q3 can be promoted.  The five physical metric q1 routes
to `c_spatial_star_1` are recorded fail-closed, and the inherited
`-4 g0 h0` arity-three coefficient remains only a diagnostic.  No
K_Berger, detector, redshift, memory, recoil, tangent-cone, branch or quantum
claim is made.

CLOSE-OUT: OBSTRUCTED — the direct temporal Hessian is in the action image, but the complete covariance projection retains an exact Maxwell-cotangent quotient class
EVIDENCE: closed_universe_observers/certificates/BERGER_DIRECT_TEMPORAL_AK_DIFF_COVARIANCE_REPAIR.json
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    value = build_certificate(payload)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    report_text = report(value)
    for document, schema_path in (
        (payload, PAYLOAD_SCHEMA),
        (value, SCHEMA),
    ):
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(document)
    if args.emit:
        PAYLOAD.write_text(payload_text)
        CERTIFICATE.write_text(rendered)
        REPORT.write_text(report_text)
    if args.check and (
        not PAYLOAD.exists()
        or PAYLOAD.read_text() != payload_text
        or not CERTIFICATE.exists()
        or CERTIFICATE.read_text() != rendered
        or not REPORT.exists()
        or REPORT.read_text() != report_text
    ):
        raise SystemExit("stale direct temporal A--K covariance artifact")
    print("BERGER_DIRECT_TEMPORAL_AK_DIFF_COVARIANCE_REPAIR generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
