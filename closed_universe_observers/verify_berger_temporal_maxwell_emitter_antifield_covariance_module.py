#!/usr/bin/env python3
"""Independently replay the bounded temporal Maxwell antifield obstruction."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers.generate_berger_108_row_emitter_physical_q2_pbw import (
    Action,
    action_add,
    differential_slots,
    form_bilinear_base,
    parameter,
    product,
    profile,
    rational,
    scale,
    tensor_add_symmetric,
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
    invariant_action_basis,
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
CERTIFICATE = (
    PACKAGE
    / "certificates/BERGER_TEMPORAL_MAXWELL_EMITTER_ANTIFIELD_COVARIANCE_MODULE.json"
)
PAYLOAD = (
    PACKAGE
    / "certificates/BERGER_TEMPORAL_MAXWELL_EMITTER_ANTIFIELD_COVARIANCE_MODULE_PAYLOAD.json"
)
SCHEMA = (
    PACKAGE
    / "schema/berger-temporal-maxwell-emitter-antifield-covariance-module-v1.schema.json"
)
PAYLOAD_SCHEMA = (
    PACKAGE
    / "schema/berger-temporal-maxwell-emitter-antifield-covariance-module-payload-v1.schema.json"
)
ORDER_THREE = (
    PACKAGE
    / "certificates/BERGER_ORDER_THREE_COMMON_ACTION_PROMOTION_GATE_PAYLOAD.json"
)


def canonical_sha256(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def add_tensor(target, tensor) -> None:
    for (output, left, left_word, right, right_word), coefficient in tensor.items():
        arity.add_bilinear_term(
            target[(0, 0)].setdefault(output, {}),
            (left, left_word, right, right_word),
            coefficient,
        )


def dual(row: int) -> tuple[int, int]:
    pairs = {
        3: (52, 1),
        52: (3, -1),
    }
    if row in pairs:
        return pairs[row]
    if 55 <= row <= 58:
        return row + 4, -1
    if 59 <= row <= 62:
        return row - 4, 1
    if 84 <= row <= 95:
        return row + 12, 1
    if 96 <= row <= 107:
        return row - 12, -1
    raise AssertionError(f"unsupported row {row}")


def hessian(action: Action) -> dict:
    output = {}
    for factors, coefficient in action.items():
        for varied_position, (varied_row, varied_word) in enumerate(factors):
            remaining = list(factors)
            remaining.pop(varied_position)
            output_row, pairing_sign = dual(varied_row)
            if not varied_word:
                tensor_add_symmetric(
                    output,
                    output_row,
                    remaining[0],
                    remaining[1],
                    scale(coefficient, rational(pairing_sign)),
                )
                continue
            expansion = arity.apply_output_word(
                tuple(reversed(varied_word)),
                coefficient,
                remaining[0][1],
                remaining[1][1],
            )
            sign = pairing_sign * (-1) ** len(varied_word)
            for (left_word, right_word), expanded in expansion.items():
                tensor_add_symmetric(
                    output,
                    output_row,
                    (remaining[0][0], left_word),
                    (remaining[1][0], right_word),
                    scale(expanded, rational(sign)),
                )
    return output


def profile_action(emitter: int, components: range) -> Action:
    action = {}
    coefficient = product(
        parameter(f"g{emitter}"), profile(f"h{emitter}", (1,))
    )
    differentiated_a = differential_slots(1, 55)
    for component in components:
        metric = form_bilinear_base(2, component, component)
        for a_factor, a_coefficient in differentiated_a[component]:
            action_add(
                action,
                ((CHI, ()), (84 + 6 * emitter + component, ()), a_factor),
                scale(
                    coefficient,
                    (
                        metric * a_coefficient[0],
                        metric * a_coefficient[1],
                    ),
                ),
            )
    return action


def strip_emitter_switch(coefficient, emitter: int):
    output = {}
    for monomial, scalar in coefficient.items():
        monomial = tuple(
            factor
            for factor in monomial
            if not (
                factor[0] == "parameter"
                and factor[1] == f"g{emitter}"
                or factor[0] == "profile"
                and factor[1] == f"h{emitter}"
            )
        )
        output = arity.replay.add(output, {monomial: scalar})
    return output


def transform(action: Action, emitter: int, sector: str) -> Action:
    transformed = {}
    for factors, coefficient in action.items():
        new_factors = []
        for row, word in factors:
            if row == CHI:
                row = 3
            elif sector == "A_plus_tau_K" and 55 <= row <= 58:
                row += 4
            elif (
                sector == "K_plus_tau_A"
                and 84 + 6 * emitter <= row < 90 + 6 * emitter
            ):
                row += 12
            new_factors.append((row, word))
        if sector == "K_plus_tau_A":
            coefficient = strip_emitter_switch(coefficient, emitter)
        action_add(transformed, tuple(new_factors), coefficient)
    return transformed


def lower_action(emitter: int, terms, sector: str) -> Action:
    action = {}
    switched = product(
        parameter(f"g{emitter}"), profile(f"h{emitter}", ())
    )
    for krow, arow, word, scalar in terms:
        if sector == "A_plus_tau_K":
            factors = ((3, ()), (krow, ()), (arow + 4, word))
            coefficient = scale(switched, scalar)
        else:
            factors = ((3, ()), (krow + 12, ()), (arow, word))
            coefficient = scale({(): (Fraction(1), Fraction(0))}, scalar)
        action_add(action, factors, coefficient)
    return action


def module(emitter: int):
    for order in (0, 1, 2):
        basis, _ = invariant_action_basis(emitter, order)
        for sector in ("A_plus_tau_K", "K_plus_tau_A"):
            for name, terms in basis:
                yield (
                    f"{sector}.lower.{name}",
                    sector,
                    f"order_{order}",
                    lower_action(emitter, terms, sector),
                )
    inherited = json.loads(ORDER_THREE.read_text())["modules"]
    for sector in ("A_plus_tau_K", "K_plus_tau_A"):
        for name, value in inherited.items():
            if value["emitter"] == emitter:
                yield (
                    f"{sector}.{name}",
                    sector,
                    "order_3_IBP_closed",
                    transform(parse_action(value["action_entries"]), emitter, sector),
                )


def defect(q1, indexed_q1, q2, emitter: int):
    rows = {}
    for output in (52, 59):
        row = arity.arity_two_row(
            output,
            (0, 0),
            q1,
            q2,
            arity.parities() + (0, 1),
            indexed_q1,
        )
        if row:
            rows[output] = row
    specialized = arity.specialize_bilinear_rows(rows)
    return {
        ((output, *key), monomial): coefficient
        for output, row in specialized.items()
        for key, polynomial in row.items()
        for monomial, coefficient in polynomial.items()
        if any(
            factor[0] == "parameter" and factor[1] == f"g{emitter}"
            for factor in monomial
        )
    }


def action_column(q1, indexed_q1, action, emitter: int):
    q2 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
    tensor = hessian(action)
    add_tensor(q2, tensor)
    return defect(q1, indexed_q1, q2, emitter), tensor


def reduce_vector(vector, pivots, basis):
    residual = dict(vector)
    for pivot, existing in zip(pivots, basis, strict=True):
        if pivot in residual:
            residual = _vector_add(
                residual,
                existing,
                _scalar_scale(residual[pivot], Fraction(-1)),
            )
    return residual


def coordinate_json(coordinate, coefficient):
    (output, left, left_word, right, right_word), monomial = coordinate
    scalar = lambda value: [value.numerator, value.denominator]
    return {
        "output": output,
        "left_input": [left, list(left_word)],
        "right_input": [right, list(right_word)],
        "coefficient_monomial": [
            [kind, name, list(vertical), list(spacetime)]
            for kind, name, vertical, spacetime in monomial
        ],
        "coefficient": [scalar(coefficient[0]), scalar(coefficient[1])],
    }


def manifest(vector):
    entries = [
        coordinate_json(coordinate, coefficient)
        for coordinate, coefficient in sorted(vector.items())
    ]
    return {
        "coordinate_count": len(entries),
        "canonical_sha256": canonical_sha256(entries),
    }


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    for document, schema_path in (
        (value, SCHEMA),
        (payload, PAYLOAD_SCHEMA),
    ):
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(document)
    assert hashlib.sha256(PAYLOAD.read_bytes()).hexdigest() == value[
        "payload_ref"
    ]["sha256"]
    for reference in value["dependency_refs"].values():
        path = ROOT / reference["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference["sha256"]

    q1 = arity.completed_q1()
    q1[(0, 0)].update(extension_q1(temporal_order=0))
    indexed_q1 = {
        degree: arity.q1_rows(operator) for degree, operator in q1.items()
    }
    base_q2 = arity.load_q2()
    add_tensor(base_q2, generalized_action_to_q2(repair_action()))
    add_tensor(base_q2, scalar_diff_q2())
    inherited = json.loads(ORDER_THREE.read_text())["modules"]

    for emitter in (0, 1):
        old_columns = []
        for record in inherited.values():
            if record["emitter"] != emitter:
                continue
            q2 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
            add_tensor(
                q2,
                generalized_action_to_q2(
                    parse_action(record["action_entries"])
                ),
            )
            old_columns.append(defect(q1, indexed_q1, q2, emitter))
        for components in (range(3), range(3, 6)):
            q2 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
            add_tensor(
                q2,
                generalized_action_to_q2(
                    profile_action(emitter, components)
                ),
            )
            old_columns.append(defect(q1, indexed_q1, q2, emitter))

        source = defect(q1, indexed_q1, base_q2, emitter)
        old_pivots, old_basis = _echelon(old_columns)
        source_quotient = reduce_vector(source, old_pivots, old_basis)
        assert len(old_columns) == len(old_pivots) == 934
        assert len(source_quotient) == 42

        replayed_columns = []
        replayed_records = []
        sector_columns = {"A_plus_tau_K": [], "K_plus_tau_A": []}
        for name, sector, tier, action in module(emitter):
            column, tensor = action_column(q1, indexed_q1, action, emitter)
            quotient = reduce_vector(column, old_pivots, old_basis)
            replayed_columns.append(quotient)
            sector_columns[sector].append(quotient)
            replayed_records.append(
                {
                    "id": name,
                    "sector": sector,
                    "tier": tier,
                    "action_sha256": canonical_sha256(_action_entries(action)),
                    "q2_key_count": len(tensor),
                    "projection_column_manifest": manifest(column),
                    "old_image_quotient_manifest": manifest(quotient),
                }
            )

        certified_audit = payload["emitter_audits"][f"emitter_{emitter}"]
        certified_records = certified_audit["complete_antifield_module"][
            "records"
        ]
        assert len(replayed_records) == len(certified_records) == 2048
        for replayed, certified in zip(
            replayed_records, certified_records, strict=True
        ):
            for key in replayed:
                assert replayed[key] == certified[key]

        pivots, basis = _echelon(replayed_columns)
        final_source = reduce_vector(source_quotient, pivots, basis)
        projection = certified_audit["complete_projection"]
        assert 934 + len(pivots) == projection["full_action_image_rank"]
        assert (
            934 + len(_echelon(replayed_columns + [source_quotient])[0])
            == projection["source_augmented_rank"]
        )
        assert manifest(final_source) == projection["final_quotient_manifest"]
        first = min(final_source.items())
        assert coordinate_json(*first) == projection["first_quotient_witness"]
        assert first[0][0] == (
            59,
            3,
            (),
            84 + 6 * emitter,
            (0, 1),
        )
        assert first[1] == (Fraction(-3), Fraction(0))
        for omitted, retained in (
            ("A_plus_tau_K", "K_plus_tau_A"),
            ("K_plus_tau_A", "A_plus_tau_K"),
        ):
            mutation = certified_audit["mutations"][f"omit_{omitted}"]
            retained_rank = len(_echelon(sector_columns[retained])[0])
            assert retained_rank == mutation["quotient_action_rank"]
            assert retained_rank < len(pivots)

    assert value["arity_two_gate"]["status"] == "OBSTRUCTED"
    assert all(
        status == "NO_CERTIFIED_MAP"
        for status in value["downstream_disposition"].values()
    )
    print(
        "BERGER_TEMPORAL_MAXWELL_EMITTER_ANTIFIELD_COVARIANCE_MODULE "
        "independent verification: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
