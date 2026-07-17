from __future__ import annotations

from copy import deepcopy
import json

from jsonschema import Draft202012Validator, ValidationError

from closed_universe_observers.generate_berger_84_row_unary_pairing_green_gate import (
    CERTIFICATE,
    SCHEMA,
    build,
    memory_transport_green,
    memory_maxwell_template,
    two_channel_inverse_defect_counts,
    unary_defect_counts,
    unary_path_audit,
)
from closed_universe_observers.verify_berger_84_row_unary_pairing_green_gate import (
    _check_inverse,
    _semantic_boundary,
    verify,
)


def test_two_channel_universal_inverse_is_exact() -> None:
    template = memory_maxwell_template()
    assert template["left_inverse_defect_count"] == 0
    assert template["right_inverse_defect_count"] == 0
    assert template["maximum_kappa_degree"] == 2
    assert len(template["cross_detector_terms"]) == 2


def test_independent_specialization_requires_cross_terms() -> None:
    assert _check_inverse()
    assert not _check_inverse(delete_cross=True)
    assert sum(two_channel_inverse_defect_counts(delete_cross_01=True)) > 0


def test_new_unary_paths_are_nilpotent_and_cyclic() -> None:
    audit = unary_path_audit()
    assert audit["nilpotency_defect_count"] == 0
    assert audit["cyclicity_defect_count"] == 0
    assert len(audit["new_length_two_paths"]) == 4
    assert len(audit["new_cyclicity_pairs"]) == 4
    assert unary_defect_counts(maxwell_compatible=False)[0] == 4
    assert unary_defect_counts(cotangent_sign=-1)[1] == 4


def test_chain_homotopy_is_finite_and_two_sided() -> None:
    construction = build()["base_memory_72_row_subcomplex"]["chain_homotopy_construction"]
    assert construction["advanced_defect_count"] == 0
    assert construction["retarded_defect_count"] == 0
    assert "two V_kappa insertions" in construction["termination"]


def test_memory_transport_has_both_clock_line_inverses() -> None:
    transport = memory_transport_green()
    assert transport["formal_adjoint"] == "T*=-T"
    assert transport["identity_defect_count"] == 0
    assert len(transport["identities"]) == 4


def test_partial_promotion_is_fail_closed() -> None:
    value = build()
    _semantic_boundary(value)
    assert value["flags"]["BASE_MEMORY_72_ROW_CAUSAL_SUBCOMPLEX_CERTIFIED"]
    assert not value["flags"]["84_ROW_Q1_CERTIFIED"]
    assert value["next_gate"] == "EXPORT_COUPLED_ROD_GRAVITY_BV_UNARY_BLOCKS_AND_CAUSAL_WITNESS"
    mutant = deepcopy(value)
    mutant["flags"]["84_ROW_Q1_CERTIFIED"] = True
    try:
        _semantic_boundary(mutant)
    except ValueError:
        pass
    else:
        raise AssertionError("full-q1 overclaim mutation was accepted")


def test_strict_schema_and_persisted_certificate() -> None:
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert json.loads(CERTIFICATE.read_text()) == value
    mutant = deepcopy(value)
    mutant["unexpected"] = True
    try:
        Draft202012Validator(schema).validate(mutant)
    except ValidationError:
        pass
    else:
        raise AssertionError("strict schema accepted an unexpected field")


def test_independent_verifier() -> None:
    assert verify() == build()
