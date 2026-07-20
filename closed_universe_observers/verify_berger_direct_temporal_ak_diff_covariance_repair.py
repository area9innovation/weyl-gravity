#!/usr/bin/env python3
"""Independently replay the direct temporal A--K covariance obstruction."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.generate_berger_108_row_emitter_physical_q2_pbw import (
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
)
from closed_universe_observers.generate_berger_higher_jet_invariant_action_module_classification import (
    generalized_action_to_q2,
)
from closed_universe_observers.generate_berger_order_three_common_action_promotion_gate import (
    parse_action,
)
from closed_universe_observers.generate_berger_quartic_completion_moduli_observer_invariance import (
    repair_action,
)


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_DIRECT_TEMPORAL_AK_DIFF_COVARIANCE_REPAIR.json"
PAYLOAD = P / "certificates/BERGER_DIRECT_TEMPORAL_AK_DIFF_COVARIANCE_REPAIR_PAYLOAD.json"
SCHEMA = P / "schema/berger-direct-temporal-ak-diff-covariance-repair-v1.schema.json"
PAYLOAD_SCHEMA = P / "schema/berger-direct-temporal-ak-diff-covariance-repair-payload-v1.schema.json"
ORDER_THREE = P / "certificates/BERGER_ORDER_THREE_COMMON_ACTION_PROMOTION_GATE_PAYLOAD.json"


def add_tensor(target, tensor):
    for (output, left, left_word, right, right_word), coefficient in tensor.items():
        arity.add_bilinear_term(
            target[(0, 0)].setdefault(output, {}),
            (left, left_word, right, right_word),
            coefficient,
        )


def profile_action(emitter, components):
    action = {}
    coefficient = product(
        parameter(f"g{emitter}"), profile(f"h{emitter}", (1,))
    )
    d_a = differential_slots(1, 55)
    for component in components:
        metric = form_bilinear_base(2, component, component)
        for a_factor, a_coefficient in d_a[component]:
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


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    for path, schema_path in (
        (CERTIFICATE, SCHEMA),
        (PAYLOAD, PAYLOAD_SCHEMA),
    ):
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(json.loads(path.read_text()))
    assert hashlib.sha256(PAYLOAD.read_bytes()).hexdigest() == value[
        "payload_ref"
    ]["sha256"]
    for reference in value["dependency_refs"].values():
        path = ROOT / reference["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference["sha256"]

    q1 = arity.completed_q1()
    q1[(0, 0)].update(extension_q1(temporal_order=0))
    indexed = {degree: arity.q1_rows(operator) for degree, operator in q1.items()}
    parity = arity.parities() + (0, 1)

    def defect(q2, emitter):
        rows = {}
        for output in (52, 59):
            row = arity.arity_two_row(
                output, (0, 0), q1, q2, parity, indexed
            )
            if row:
                rows[output] = row
        rows = arity.specialize_bilinear_rows(rows)
        return {
            ((output, *key), monomial): coefficient
            for output, row in rows.items()
            for key, polynomial in row.items()
            for monomial, coefficient in polynomial.items()
            if any(
                factor[0] == "parameter"
                and factor[1] == f"g{emitter}"
                for factor in monomial
            )
        }

    base = arity.load_q2()
    add_tensor(base, generalized_action_to_q2(repair_action()))
    add_tensor(base, scalar_diff_q2())
    modules = json.loads(ORDER_THREE.read_text())["modules"]

    for emitter in (0, 1):
        columns = []
        for module in modules.values():
            if module["emitter"] != emitter:
                continue
            q2 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
            add_tensor(
                q2,
                generalized_action_to_q2(
                    parse_action(module["action_entries"])
                ),
            )
            columns.append(defect(q2, emitter))
        for components in (range(3), range(3, 6)):
            q2 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
            add_tensor(
                q2,
                generalized_action_to_q2(
                    profile_action(emitter, components)
                ),
            )
            columns.append(defect(q2, emitter))
        source = defect(base, emitter)
        assert len(columns) == 934
        assert len(_echelon(columns)[0]) == 934
        assert len(_echelon(columns + [source])[0]) == 935
        witness = payload["emitter_audits"][f"emitter_{emitter}"][
            "complete_covariance_projection"
        ]["first_quotient_witness"]
        assert witness["output"] == 59
        assert witness["left_input"] == [3, []]
        assert witness["right_input"] == [84 + 6 * emitter, [0, 1]]
        assert witness["coefficient"] == [[-3, 1], [0, 1]]

    assert value["arity_three_and_quartic_gate"]["status"].startswith(
        "NOT_REACHED"
    )
    print(
        "BERGER_DIRECT_TEMPORAL_AK_DIFF_COVARIANCE_REPAIR independent verification: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
