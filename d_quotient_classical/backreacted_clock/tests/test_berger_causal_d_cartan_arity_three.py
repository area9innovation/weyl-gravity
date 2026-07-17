from __future__ import annotations

import json

import jsonschema

from d_quotient_classical.backreacted_clock import berger_causal_d_cartan_arity_three as theorem


def test_complete_arity_three_causal_cartan() -> None:
    payload = theorem.build()
    theorem.verify(payload)
    assert payload["flags"]["BERGER_ARITY_THREE_D_CARTAN_FULL_4D"] is True
    assert payload["flags"]["BERGER_CAUSAL_D_CARTAN_THROUGH_ARITY_THREE"] is True
    assert payload["flags"]["BERGER_HADAMARD_DATA"] is False
    assert payload["flags"]["QUANTUM_CLAIM"] is False
    assert payload["cyclic_completion"]["pairing_and_sign_audit"]["C4_group_law_defects"] == 0
    assert payload["cyclic_completion"]["pairing_and_sign_audit"]["admissible_degree_zero_row_quartets"] == 978736


def test_strict_schema_and_persisted_outputs() -> None:
    payload = theorem.build()
    schema = json.loads(theorem.SCHEMA_PATH.read_text())
    manifest_schema = json.loads(theorem.MANIFEST_SCHEMA_PATH.read_text())
    receipt_schema = json.loads(theorem.RECEIPT_SCHEMA_PATH.read_text())
    for current in (schema, manifest_schema, receipt_schema):
        jsonschema.Draft202012Validator.check_schema(current)
    jsonschema.Draft202012Validator(schema).validate(payload)
    jsonschema.Draft202012Validator(manifest_schema).validate(json.loads(theorem.MANIFEST_PATH.read_text()))
    jsonschema.Draft202012Validator(receipt_schema).validate(json.loads(theorem.RECEIPT_PATH.read_text()))
    assert json.loads(theorem.CERTIFICATE_PATH.read_text()) == payload
    assert theorem.REPORT_PATH.read_text() == theorem._report()
    assert json.loads(theorem.MANIFEST_PATH.read_text()) == theorem._manifest()


def test_mutation_guards() -> None:
    payload = theorem.build()
    payload["support_scope"]["separately_retarded_or_advanced_cyclic_primitive_claimed"] = True
    try:
        theorem.verify(payload)
    except AssertionError:
        pass
    else:
        raise AssertionError("support-overstatement mutation was accepted")
